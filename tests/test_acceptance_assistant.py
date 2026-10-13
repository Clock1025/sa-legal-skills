"""離線合成資料測試；不是真人模型呼叫、平台匯出或行為驗收。"""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('acceptance_assistant', ROOT / 'scripts/acceptance_assistant.py')
assistant = importlib.util.module_from_spec(spec)
sys.path.insert(0, str(ROOT / 'scripts'))
try:
    spec.loader.exec_module(assistant)
finally:
    sys.path.pop(0)


class AssistantTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.repo = Path(self.tmp.name) / 'repo'; self.repo.mkdir()
        shutil.copytree(ROOT / 'docs', self.repo / 'docs')
        shutil.copytree(ROOT / 'skills', self.repo / 'skills')
        shutil.copytree(ROOT / 'tests/fixtures/docx', self.repo / 'tests/fixtures/docx')
        shutil.copy(ROOT / 'START-HERE.md', self.repo)
        def git(*args):
            return subprocess.check_output(['git', *args], cwd=self.repo, stderr=subprocess.DEVNULL).decode().strip()
        git('init', '-q'); git('add', '.')
        git('-c', 'user.name=Offline fixture', '-c', 'user.email=fixture@example.invalid', 'commit', '-qm', '合成資料的本機 Git fixture')
        self.sha = git('rev-parse', 'HEAD')
        self.txt = Path(self.tmp.name) / 'synthetic.txt'
        self.txt.write_bytes(b'\xef\xbb\xbfUser: SYNTHETIC INPUT\r\nChatGPT: SYNTHETIC OUTPUT, NOT A LIVE MODEL\r\n')

    def imported(self, **kwargs):
        values = dict(repo=self.repo, commit=self.sha, run_id='synthetic-only', case_id='P0-CASE-05',
                      transcript=self.txt, origin='SYNTHETIC')
        values.update(kwargs)
        return assistant.import_txt(**values)

    def test_prepare_separates_inputs_rubric_and_pins_candidate_bytes(self):
        original = (self.repo / 'skills/regulation-review/SKILL.md').read_bytes()
        (self.repo / 'skills/regulation-review/SKILL.md').write_text('DIRTY WORKTREE: never use this as candidate')
        result = assistant.prepare(self.repo, self.sha, 'cards', ['P0-CASE-01', 'P0-CASE-03'])
        self.assertEqual((result / 'P0-CASE-01/model/skills/regulation-review.md').read_bytes(), original)
        self.assertFalse((result / 'P0-CASE-01/model/skills/amendment-drafting.md').exists())
        review = (result / 'P0-CASE-03/reviewer/操作與判準.md').read_text()
        self.assertIn('ASSISTANT_PROPOSAL', review)
        for path in (result / 'P0-CASE-03/model').glob('turn-*.txt'):
            self.assertNotIn('ASSISTANT_PROPOSAL', path.read_text())
            self.assertNotIn('禁止行為', path.read_text())
        index = json.loads((result / 'index.json').read_text())
        for entry in index['files']:
            self.assertEqual(entry['sha256'], hashlib.sha256((result / entry['path']).read_bytes()).hexdigest())
        self.assertEqual(index['status'], 'NOT TESTED')

    def test_prepare_all_matrix_cases_and_expand_docx_inputs_only(self):
        result = assistant.prepare(self.repo, self.sha, 'all-cards')
        dirs = [p for p in result.iterdir() if p.is_dir() and p.name != 'reviewer']
        self.assertEqual(len(dirs), 21)
        self.assertEqual(len(list((result / 'C-DOCX/model').glob('C*.json'))), 6)
        long = json.loads((result / 'C-DOCX/model/C02.json').read_text())
        old = long['rows'][0]['old']
        self.assertEqual(old[1]['text'].count('虛構長文測試'), 80)
        self.assertIn('七日前', old[0]['text'])
        self.assertEqual(list(result.rglob('*.docx')), [])

    def test_docx_fixture_id_cannot_escape_output_directory(self):
        fixture = self.repo / 'tests/fixtures/docx/cases.json'
        data = json.loads(fixture.read_text())
        data['cases'][0]['id'] = '../../escape'
        assistant.write_json(fixture, data)
        subprocess.run(['git', 'add', '.'], cwd=self.repo, check=True)
        subprocess.run(['git', '-c', 'user.name=Offline fixture', '-c', 'user.email=fixture@example.invalid',
                        'commit', '-qm', 'synthetic invalid path fixture'], cwd=self.repo, check=True)
        sha = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=self.repo, text=True).strip()
        with self.assertRaises(ValueError): assistant.prepare(self.repo, sha, 'bad-docx', ['C-DOCX'])
        self.assertFalse((self.repo / 'test-output/acceptance/assistant/plans/bad-docx').exists())
        self.assertFalse((self.repo / 'test-output/acceptance/assistant/plans/escape.json').exists())

    def test_prepare_rejects_duplicate_selection_unknown_case_and_existing_bundle(self):
        with self.assertRaises(ValueError): assistant.prepare(self.repo, self.sha, 'bad', ['A-UNREAD', 'A-UNREAD'])
        with self.assertRaises(ValueError): assistant.prepare(self.repo, self.sha, 'bad', ['UNKNOWN'])
        result = assistant.prepare(self.repo, self.sha, 'once', ['A-SELECT-01'])
        original = (result / 'index.json').read_bytes()
        with self.assertRaises(FileExistsError): assistant.prepare(self.repo, self.sha, 'once', ['A-SELECT-01'])
        self.assertEqual((result / 'index.json').read_bytes(), original)

    def test_txt_bytes_bom_crlf_hash_index_and_no_turn_reconstruction(self):
        result = self.imported()
        self.assertEqual((result / 'transcript.txt').read_bytes(), self.txt.read_bytes())
        data = json.loads((result / 'record.json').read_text())
        self.assertEqual(data['artifacts'][0]['sha256'], hashlib.sha256(self.txt.read_bytes()).hexdigest())
        self.assertEqual(data['status'], 'NOT TESTED')
        self.assertFalse(data['execution']['actual_model_call'])
        self.assertEqual(data['inputs'], [])
        self.assertNotIn('turns', data)
        self.assertIn('待核對', data['outputs'][0]['anchor'])
        assistant.check(data, result)
        self.assertIn(data['artifacts'][0]['sha256'], (result / 'sources-index.md').read_text())
        self.assertNotIn('SYNTHETIC OUTPUT', (result / 'summary.md').read_text())

    def test_missing_platform_model_inputs_do_not_block_storage_or_fake_pass(self):
        result = self.imported()
        data = json.loads((result / 'record.json').read_text())
        self.assertEqual(data['platform']['product'], 'UNKNOWN')
        self.assertEqual(data['model']['version'], 'UNVERIFIED')
        self.assertTrue(data['missing_evidence'])
        self.assertIn('不自動否定', (result / 'summary.md').read_text())
        self.assertEqual(data['quality']['visual_qa'], 'NOT TESTED')

    def test_operator_call_declaration_stays_pending_and_needs_no_internal_logs(self):
        # Simulated declarations test compatibility ONLY, not actual platform/model evidence.
        inp = Path(self.tmp.name) / 'input.txt'; inp.write_text('SYNTHETIC UNIT INPUT')
        result = self.imported(origin='PLATFORM_EXPORT', observed_call=True, inputs=inp,
                               platform='ChatGPT', surface='Chat', model='synthetic UI label')
        data = json.loads((result / 'record.json').read_text())
        self.assertEqual(data['status'], 'NOT TESTED')
        self.assertEqual(data['execution']['call_evidence']['artifact_id'], 'transcript')
        # Independent caller verdict with anchors can be integrity-checked using visible TXT.
        data['status'] = 'FAIL'
        data['adjudication'].update(verifier='synthetic unit verifier, not real adjudication',
                                    basis='synthetic assertion fixture', evidence_anchors=[data['outputs'][0]])
        assistant.check(data, result)
        self.assertEqual(data['skill_sources'], [])  # Missing FULL receipt is not an automatic behavior failure.

    def test_synthetic_cannot_claim_real_call(self):
        with self.assertRaises(ValueError): self.imported(observed_call=True)
        self.assertFalse((self.repo / 'test-output').exists())

    def test_duplicate_digest_across_run_ids_and_preserve_existing_failure(self):
        result = self.imported(origin='PLATFORM_EXPORT', observed_call=True)
        inp = result / 'inputs.txt'; inp.write_text('SYNTHETIC INPUT')
        data = json.loads((result / 'record.json').read_text())
        data['artifacts'].append(assistant.artifact('input', 'inputs.txt', 'input', 'USER_INPUT', inp.read_bytes()))
        data['inputs'] = [dict(artifact_id='input', anchor='synthetic line 1')]
        data['status'] = 'FAIL'
        data['adjudication'].update(verifier='synthetic verifier', evidence_anchors=[data['outputs'][0]])
        assistant.write_json(result / 'record.json', data)
        old = (result / 'record.json').read_bytes()
        with self.assertRaisesRegex(ValueError, '相同 TXT'): self.imported(run_id='retry-id')
        self.assertEqual((result / 'record.json').read_bytes(), old)
        self.assertFalse((result.parent / 'retry-id').exists())
        self.assertFalse((result.parent / '.import.lock').exists())

    def test_same_run_id_different_text_never_overwrites(self):
        result = self.imported(); original = (result / 'record.json').read_bytes()
        self.txt.write_text('DIFFERENT SYNTHETIC EXPORT')
        with self.assertRaises(FileExistsError): self.imported()
        self.assertEqual((result / 'record.json').read_bytes(), original)

    def test_unsafe_names_and_output_symlink_rejected(self):
        for name in ('../escape', '/tmp/escape', 'a/b', '', 'a\\b'):
            with self.subTest(name=name), self.assertRaises(ValueError): self.imported(run_id=name)
        outside = Path(self.tmp.name) / 'outside'; outside.mkdir()
        (self.repo / 'test-output').symlink_to(outside, target_is_directory=True)
        with self.assertRaises(ValueError): self.imported()
        self.assertEqual(list(outside.iterdir()), [])

    def test_nested_run_symlink_input_symlink_and_lock_rejected(self):
        base = assistant.store(self.repo); (base / 'runs').symlink_to(Path(self.tmp.name), target_is_directory=True)
        with self.assertRaises(ValueError): self.imported()
        (base / 'runs').unlink()
        link = Path(self.tmp.name) / 'link.txt'; link.symlink_to(self.txt)
        with self.assertRaises(ValueError): self.imported(transcript=link)
        runs = base / 'runs'; runs.mkdir(); (runs / '.import.lock').write_text('existing lock')
        with self.assertRaises(FileExistsError): self.imported()
        self.assertTrue((runs / '.import.lock').exists())

    def test_bad_utf8_empty_nul_missing_and_bad_candidate_leave_no_run(self):
        for content in (b'\xff', b' \r\n', b'hello\x00world'):
            self.txt.write_bytes(content)
            with self.subTest(content=content), self.assertRaises(ValueError): self.imported()
        self.txt.unlink()
        with self.assertRaises(ValueError): self.imported()
        with self.assertRaises(ValueError): self.imported(commit='develop')
        with self.assertRaises(ValueError): self.imported(case_id='UNKNOWN')
        self.assertFalse((self.repo / 'test-output').exists())

    def test_skill_bytes_are_verified_without_claiming_actual_read(self):
        name = 'regulation-review'; filename = self.repo / f'skills/{name}/SKILL.md'
        result = self.imported(skills=[(name, filename)])
        data = json.loads((result / 'record.json').read_text()); source = data['skill_sources'][0]
        self.assertEqual(source['commit'], self.sha)
        self.assertEqual(source['read_status'], 'UNVERIFIED')
        filename.write_text('SYNTHETIC CHANGED SKILL')
        self.txt.write_text('DIFFERENT SYNTHETIC TXT')
        result = self.imported(run_id='second', skills=[(name, filename)])
        self.assertEqual(json.loads((result / 'record.json').read_text())['skill_sources'][0]['commit'], 'UNVERIFIED')

    def test_summary_reports_tamper_without_rewriting_verdict(self):
        result = self.imported(); original = (result / 'record.json').read_bytes()
        (result / 'transcript.txt').write_text('TAMPERED SYNTHETIC TXT')
        report = assistant.summary([result / 'record.json'])
        self.assertIn('hash mismatch', report)
        self.assertIn('未核對；不重寫原判定', report)
        self.assertEqual((result / 'record.json').read_bytes(), original)
        self.txt.write_text('new synthetic transcript')
        with self.assertRaisesRegex(ValueError, 'hash mismatch'): self.imported(run_id='other')

    def test_summary_escapes_metadata_and_never_prints_raw_dialogue(self):
        result = self.imported(model='[fake](https://example.invalid) | <script>\nrow')
        report = (result / 'summary.md').read_text()
        self.assertIn('\\[fake\\]', report)
        self.assertIn('\\|', report)
        self.assertIn('\\<script\\>', report)
        self.assertNotIn('SYNTHETIC INPUT', report)
        self.assertIn('人工', report)

    def test_summary_reads_existing_schema_without_moving_or_duplicating_record(self):
        result = self.imported(); original = (result / 'record.json').read_bytes()
        standalone = Path(self.tmp.name) / 'legacy-run'
        shutil.copytree(result, standalone)
        report = assistant.summary([standalone / 'record.json'])
        self.assertIn('synthetic-only', report)
        self.assertEqual((standalone / 'record.json').read_bytes(), original)
        with self.assertRaises(ValueError): assistant.summary([standalone / 'record.json', standalone / 'record.json'])

    def test_cli_invalid_skill_argument_and_empty_summary(self):
        cmd = [sys.executable, str(ROOT / 'scripts/acceptance_assistant.py'), 'import-txt',
               '--commit', self.sha, '--run-id', 'x', '--case', 'P0-CASE-05', '--transcript', str(self.txt), '--skill', 'missing-equals']
        result = subprocess.run(cmd, capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('NAME=FILE', result.stderr)
        self.assertIn('不給風險等級', assistant.summary([]))


if __name__ == '__main__':
    unittest.main()
