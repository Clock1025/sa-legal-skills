"""Offline executable fixtures + separately labeled static Skill checks; no model calls."""
import copy
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
import warnings
from unittest.mock import patch
from zipfile import ZipFile, ZIP_DEFLATED

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / 'tests/fixtures/feedback'
spec = importlib.util.spec_from_file_location('feedback', ROOT / 'scripts/feedback_package.py')
feedback = importlib.util.module_from_spec(spec)
spec.loader.exec_module(feedback)


class FeedbackTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.input = self.root / 'input'
        shutil.copytree(FIXTURE, self.input)
        self.output = self.root / 'output'
        self.data = json.loads((self.input / 'partial.json').read_text())

    def build(self, data=None, **kwargs):
        return feedback.build_package(data or self.data, self.input, self.output,
                                      naming_date='2026-10-12', **kwargs)

    def files(self, path):
        with ZipFile(path) as archive:
            self.assertIsNone(archive.testzip())
            return {name: archive.read(name) for name in archive.namelist()}

    def test_real_zip_members_source_bytes_and_hashes(self):
        path, manifest = self.build()
        self.assertTrue(path.is_file())
        files = self.files(path)
        self.assertEqual(set(files), {'manifest.json', *feedback.BASE_FILES, 'files/sample-output.txt'})
        self.assertEqual(files['files/sample-output.txt'], (self.input / 'sample-output.txt').read_bytes())
        for entry in manifest['files']:
            if entry['path'] != 'manifest.json':
                content = files[entry['path']]
                self.assertEqual(entry['sha256'], hashlib.sha256(content).hexdigest())
                self.assertEqual(entry['byte_size'], len(content))
        self.assertEqual(feedback.validate_zip_bytes(path.read_bytes()), manifest)
        with ZipFile(path) as archive:
            archive.extractall(self.root / 'extracted')
        self.assertEqual((self.root / 'extracted/files/sample-output.txt').read_bytes(),
                         (self.input / 'sample-output.txt').read_bytes())

    def test_same_conversation_id_multiple_reports_unique_suffix(self):
        first, m1 = self.build()
        second, m2 = self.build()
        self.assertEqual(m1['conversation_id'], m2['conversation_id'])
        self.assertNotEqual(first.name, second.name)
        self.assertNotEqual(m1['report_id'][-4:], m2['report_id'][-4:])

    def test_collision_rerolls_suffix(self):
        self.output.mkdir()
        (self.output / 'report_OX7m4q2x_260101_aaaa.txt').write_text('previous record')
        with patch.object(feedback.secrets, 'choice', side_effect=list('aaaabbbb')):
            path, _ = self.build()
        self.assertTrue(path.name.endswith('_bbbb.zip'))

    def test_new_conversation_id_collision_rerolls_and_can_be_reused(self):
        self.data['conversation_id'] = None
        self.output.mkdir()
        (self.output / 'report_OXaaaaaa_260101_zzzz.txt').write_text('other conversation')
        with patch.object(feedback.secrets, 'choice', side_effect=list('aaaaaabbbbbbcccc')):
            _, manifest = self.build()
        self.assertEqual(manifest['conversation_id'], 'OXbbbbbb')
        self.data['conversation_id'] = manifest['conversation_id']
        _, second = self.build()
        self.assertEqual(second['conversation_id'], 'OXbbbbbb')

    def test_illegal_conversation_ids_rejected(self):
        for cid in ('OC123', 'ZZ7m4q2x', 'OX7M4Q2X', '../../escape', 'OX7m4q2x\n'):
            with self.subTest(cid=cid):
                self.data['conversation_id'] = cid
                with self.assertRaises(ValueError):
                    self.build()

    def test_different_surface_segments_and_unknown_skill_stay_unverified(self):
        _, manifest = self.build()
        self.assertEqual([m['platform']['code'] for m in manifest['model_segments']], ['UU', 'OX'])
        self.assertEqual(manifest['skill_reads'][0]['version'], 'UNVERIFIED')
        self.assertEqual(manifest['skill_reads'][0]['read_status'], 'UNVERIFIED')
        self.assertEqual(manifest['model_segments'][0]['reasoning_effort'], 'UNKNOWN')

    def test_platform_cannot_be_guessed_from_model_or_unknown_code(self):
        for mutation in ('code', 'surface'):
            bad = copy.deepcopy(self.data)
            bad['platform'][mutation] = 'made-up'
            with self.assertRaises(ValueError):
                self.build(bad)

    def test_missing_coverage_cannot_be_complete(self):
        self.data['transcript']['transcript_completeness'] = 'COMPLETE'
        self.data['transcript']['coverage']['verification'] = 'CHECKED_USER_VISIBLE_SCOPE'
        with self.assertRaisesRegex(ValueError, 'known gaps'):
            self.build()

    def test_redaction_or_summary_requires_partial(self):
        for kind in ('REDACTED', 'SUMMARY'):
            for claimed in ('COMPLETE', 'UNVERIFIED'):
                with self.subTest(kind=kind, claimed=claimed):
                    bad = copy.deepcopy(self.data)
                    bad['transcript']['coverage']['missing'] = []
                    bad['transcript']['turns'][0]['representation'] = kind
                    bad['transcript']['transcript_completeness'] = claimed
                    if kind == 'REDACTED':
                        bad['redactions'] = [{'location':'T1', 'reason':'personal data omitted'}]
                    with self.assertRaises(ValueError):
                        self.build(bad)

    def test_partial_redaction_and_summary_disclosures(self):
        for representation in ('REDACTED', 'SUMMARY'):
            bad = copy.deepcopy(self.data)
            bad['transcript']['turns'][0]['representation'] = representation
            with self.assertRaises(ValueError):
                self.build(bad)
            if representation == 'REDACTED':
                bad['transcript']['turns'][0]['text'] = '[REDACTED]'
                bad['redactions'] = [{'location':'T1', 'reason':'user-authorized minimization'}]
            else:
                bad['transcript']['coverage']['summary_substitutions'] = ['T1 is a supplied summary, not reconstructed verbatim']
            _, manifest = self.build(bad)
            self.assertEqual(manifest['transcript']['transcript_completeness'], 'PARTIAL')

    def test_checked_complete_scope_and_unverified_scope_are_distinct(self):
        self.data['transcript']['coverage']['missing'] = []
        self.data['transcript']['transcript_completeness'] = 'UNVERIFIED'
        self.assertEqual(self.build()[1]['transcript']['transcript_completeness'], 'UNVERIFIED')
        self.data['transcript']['transcript_completeness'] = 'COMPLETE'
        with self.assertRaises(ValueError):
            self.build()
        self.data['transcript']['coverage']['verification'] = 'CHECKED_USER_VISIBLE_SCOPE'
        self.assertEqual(self.build()[1]['transcript']['transcript_completeness'], 'COMPLETE')

    def test_unknown_time_needs_explicit_naming_date_and_no_timestamp_is_invented(self):
        with self.assertRaisesRegex(ValueError, 'unknown time'):
            feedback.build_package(self.data, self.input, self.output)
        path, manifest = self.build()
        self.assertIsNone(manifest['generated_at'])
        self.assertEqual(manifest['naming_date']['source'], 'USER_PROVIDED_NAMING_DATE')
        self.assertIn('timestamp: UNKNOWN', self.files(path)['transcript.md'].decode())
        self.data['generated_at'] = '2026-10-12T20:00:00+08:00'
        _, supplied = self.build()
        self.assertEqual(supplied['generated_at'], self.data['generated_at'])
        self.data['generated_at'] = '2026-10-12T20:00:00'
        with self.assertRaises(ValueError):
            self.build()

    def test_verbatim_text_unicode_and_newlines_preserved(self):
        original = '第一行\n\n引號「中文」\t尾端  \n'
        self.data['transcript']['turns'][0]['text'] = original
        path, manifest = self.build()
        self.assertIn(original.encode(), self.files(path)['transcript.md'])
        self.assertEqual(manifest['transcript']['turns'][0]['text'], original)

    def test_hidden_roles_and_wrong_turn_order_rejected(self):
        for role in ('system', 'developer', 'tool', 'private_reasoning'):
            bad = copy.deepcopy(self.data)
            bad['transcript']['turns'][0]['role'] = role
            with self.assertRaises(ValueError):
                self.build(bad)
        self.data['transcript']['turns'].reverse()
        with self.assertRaises(ValueError):
            self.build()

    def test_nonexistent_attachment_and_output_rejected(self):
        for collection in ('attachments', 'outputs'):
            with self.subTest(collection=collection):
                bad = copy.deepcopy(self.data)
                entry = copy.deepcopy(bad['outputs'][0])
                entry['local_path'] = 'does-not-exist.pdf'
                bad[collection] = [entry]
                with self.assertRaisesRegex(ValueError, 'unavailable'):
                    self.build(bad)

    def test_unauthorized_unsafe_and_symlink_escape_rejected(self):
        for field, value in (('authorized', False), ('package_path', 'files/../escape'),
                             ('local_path', '../escape'), ('package_path', '/tmp/escape')):
            bad = copy.deepcopy(self.data)
            bad['outputs'][0][field] = value
            with self.assertRaises(ValueError):
                self.build(bad)
        outside = self.root / 'private.txt'
        outside.write_text('not allowed')
        (self.input / 'outside.txt').symlink_to(outside)
        self.data['outputs'][0]['local_path'] = 'outside.txt'
        with self.assertRaises(ValueError):
            self.build()

    def test_fabricated_hash_and_full_skill_read_without_evidence_rejected(self):
        self.data['outputs'][0]['sha256'] = 'fake'
        with self.assertRaises(ValueError):
            self.build()
        self.data['outputs'][0].pop('sha256')
        self.data['skill_reads'][0]['read_status'] = 'FULL'
        with self.assertRaises(ValueError):
            self.build()

    def test_empty_indexes_and_unavailable_records_remain(self):
        self.data['outputs'] = []
        path, manifest = self.build()
        files = self.files(path)
        self.assertIn('No files available', files['outputs/INDEX.md'].decode())
        self.assertIsNone(manifest['attachments'][0]['sha256'])
        self.assertIsNone(manifest['attachments'][0]['package_path'])
        self.assertNotIn('files/unavailable-example.pdf', files)

    def test_text_fallback_without_zip_capability(self):
        with patch.object(feedback, 'ZipFile', side_effect=OSError('ZIP unavailable')):
            path, manifest = self.build(text_only=True)
        self.assertEqual(path.suffix, '.txt')
        text = path.read_text()
        for name in ('manifest.json', *feedback.BASE_FILES):
            self.assertIn(f'===== {name} (', text)
        self.assertEqual(manifest['delivery'], 'TEXT_FALLBACK')
        self.assertEqual(manifest['outputs'][0]['availability'], 'EXCLUDED')
        self.assertIsNone(manifest['outputs'][0]['sha256'])
        self.assertIsNone(manifest['outputs'][0]['package_path'])
        self.assertNotIn('sandbox:', text)
        self.assertFalse(list(self.output.glob('*.zip')))

    def test_manifest_required_fields_and_tampered_contents_rejected(self):
        path, _ = self.build()
        files = self.files(path)
        manifest = json.loads(files['manifest.json'])
        for key in feedback.REQUIRED:
            bad = copy.deepcopy(manifest)
            del bad[key]
            with self.subTest(key=key), self.assertRaises(ValueError):
                feedback.validate_files({**files, 'manifest.json': feedback.json_bytes(bad)})
        with self.assertRaises(ValueError):
            feedback.validate_files({**files, 'transcript.md': b'changed'})
        with self.assertRaises(ValueError):
            feedback.validate_files({**files, 'files/sample-output.txt': b'changed'})

    def test_zip_extra_or_unsafe_members_rejected(self):
        path, _ = self.build()
        files = self.files(path)
        for extra in ('extra.md', '../unsafe.txt'):
            buffer = io.BytesIO()
            with ZipFile(buffer, 'w', ZIP_DEFLATED) as archive:
                for name, content in {**files, extra:b'extra'}.items():
                    archive.writestr(name, content)
            with self.assertRaises(ValueError):
                feedback.validate_zip_bytes(buffer.getvalue())

    def test_duplicate_zip_members_rejected(self):
        path, _ = self.build()
        files = self.files(path)
        buffer = io.BytesIO()
        with warnings.catch_warnings():
            warnings.simplefilter('ignore', UserWarning)
            with ZipFile(buffer, 'w', ZIP_DEFLATED) as archive:
                for name, content in files.items():
                    archive.writestr(name, content)
                archive.writestr('report.md', files['report.md'])
        with self.assertRaisesRegex(ValueError, 'duplicate ZIP'):
            feedback.validate_zip_bytes(buffer.getvalue())

    def test_manifest_date_id_and_uncovered_segment_rejected(self):
        path, _ = self.build()
        files = self.files(path)
        for key, value in (('report_id', 'report_OX7m4q2x_261013_aaaa'),
                           ('conversation_id', 'XX123456'), ('delivery', 'fake')):
            with self.subTest(key=key):
                manifest = json.loads(files['manifest.json'])
                manifest[key] = value
                with self.assertRaises(ValueError):
                    feedback.validate_files({**files, 'manifest.json':feedback.json_bytes(manifest)})
        self.data['model_segments'].pop()
        with self.assertRaisesRegex(ValueError, 'every supplied turn'):
            self.build()

    def test_cli_pack_validate_and_negative_exit(self):
        command = [sys.executable, str(ROOT / 'scripts/feedback_package.py')]
        result = subprocess.run([*command, 'pack', str(self.input / 'partial.json'), '--date',
                                 '2026-10-12', '--output-dir', str(self.output)], text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        archive = next(self.output.glob('*.zip'))
        result = subprocess.run([*command, 'validate', str(archive)], text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        archive.write_bytes(b'invalid archive')
        result = subprocess.run([*command, 'validate', str(archive)], text=True, capture_output=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('FAIL:', result.stderr)


class FeedbackStaticTests(unittest.TestCase):
    def test_three_skills_have_identical_trigger_and_release_zip_fallback_rules(self):
        blocks = []
        for skill in ('regulation-review', 'large-scale-reform', 'amendment-drafting'):
            text = (ROOT / 'skills' / skill / 'SKILL.md').read_text()
            block = text.split('## Skill Feedback Package\n', 1)[1].split('## Stage provenance', 1)[0]
            for fragment in ('請產生完整 Skill 回報包，包含可取得的完整對話紀錄。',
                             '../../docs/feedback-package.md', 'not a new legal-work stage',
                             'PARTIAL', 'UNVERIFIED', 'copyable text', 'no automatic external upload'):
                self.assertIn(fragment, block)
            blocks.append(block)
        self.assertEqual(blocks, [blocks[0]] * 3)

    def test_canonical_platform_codes_match_tool(self):
        doc = (ROOT / 'docs/feedback-package.md').read_text()
        for code, (product, surface) in feedback.PLATFORMS.items():
            self.assertIn(f'| {code} | {product} | {surface} |', doc)
        entry = (ROOT / 'START-HERE.md').read_text()
        self.assertEqual(entry.count('## 可複製提示詞'), 1)


if __name__ == '__main__':
    unittest.main()
