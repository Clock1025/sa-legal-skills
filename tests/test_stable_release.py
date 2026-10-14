"""Offline release safety tests. No GitHub publication or model calls."""
import copy
import importlib.util
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


stable = load('stable', ROOT / 'scripts/publish_stable.py')
validator = load('validator', ROOT / 'scripts/validate.py')


class FakeGitHub:
    def __init__(self, package):
        self.package = package
        self.calls = []
        self.tag = None
        self.release = None
        self.upload_error = False
        self.bad_download = False
        self.existing_release = False
        self.existing_tag = False
        self.denied = False
        self.downloads = 0
        self.protected = {'type': 'tag', 'sha': 'original'}

    def request(self, method, path, data=None, absent_ok=False):
        self.calls.append((method, path, data))
        if self.denied:
            raise ValueError('GitHub GET: HTTP 403')
        if path == f'git/ref/tags/{stable.TAG}':
            if self.existing_tag:
                return {'object': {'sha': 'other'}}
            return None if self.tag is None else {'object': self.tag}
        if path.startswith('releases?'):
            return [{'tag_name': stable.TAG}] if self.existing_release else []
        if path.startswith('git/ref/tags/'):
            return {'object': copy.deepcopy(self.protected)}
        if path == 'git/refs':
            self.tag = {'type': 'commit', 'sha': data['sha']}
            return {'object': self.tag}
        if path == 'releases':
            self.release = dict(data, id=42, assets=[], html_url='https://github.com/example/release')
            return copy.deepcopy(self.release)
        if path == 'releases/42':
            if method == 'PATCH':
                self.release.update(data)
            return copy.deepcopy(self.release)
        if path == 'releases/latest':
            return {'id': 42}
        raise AssertionError((method, path))

    def upload(self):
        if self.upload_error:
            raise subprocess.CalledProcessError(1, ['gh', 'release', 'upload'])
        self.release['assets'] = [{'name': name, 'state': 'uploaded',
            'size': (self.package / name).stat().st_size} for name in stable.ASSETS]

    def download(self, directory):
        self.downloads += 1
        for name in stable.ASSETS:
            shutil.copyfile(self.package / name, Path(directory) / name)
        if self.bad_download:
            (Path(directory) / stable.ASSETS[0]).write_bytes(b'corrupt')


class StableReleaseTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.source = Path(self.temp.name) / 'candidate'
        self.source.mkdir()
        for name in (*validator.MEMBERS, 'README.md', 'scripts/package-release.sh', 'scripts/validate.py'):
            target = self.source / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, target)
        self.package = Path(self.temp.name) / 'package'
        self.mock = patch.object(stable, 'validation', return_value=validator)
        self.mock.start()
        self.addCleanup(self.mock.stop)
        stable.prepare(self.source, self.package)
        self.api = FakeGitHub(self.package)

    def publish(self):
        stable.publish(self.api, self.source, self.package, '繁體中文說明')

    def test_success_checks_draft_download_before_publication_and_downloads_again(self):
        with patch('builtins.print'):
            self.publish()
        self.assertFalse(self.api.release['draft'])
        self.assertFalse(self.api.release['prerelease'])
        self.assertEqual(self.api.release['make_latest'], 'true')
        self.assertEqual(self.api.tag['sha'], stable.COMMIT)
        self.assertEqual(self.api.downloads, 2)
        create = next(data for method, path, data in self.api.calls if method == 'POST' and path == 'releases')
        self.assertTrue(create['draft'])
        self.assertEqual(create['make_latest'], 'false')

    def test_existing_tag_stops_before_any_write(self):
        self.api.existing_tag = True
        with self.assertRaisesRegex(ValueError, 'Tag already exists'):
            self.publish()
        self.assertFalse(any(method != 'GET' for method, _, _ in self.api.calls))

    def test_existing_draft_stops_before_any_write(self):
        self.api.existing_release = True
        with self.assertRaisesRegex(ValueError, 'Release or draft already exists'):
            self.publish()
        self.assertIsNone(self.api.tag)

    def test_permission_failure_is_not_treated_as_absence(self):
        self.api.denied = True
        with self.assertRaisesRegex(ValueError, 'HTTP 403'):
            self.publish()
        self.assertIsNone(self.api.tag)

    def test_upload_failure_leaves_unpublished_draft_without_delete(self):
        self.api.upload_error = True
        with self.assertRaises(subprocess.CalledProcessError):
            self.publish()
        self.assertTrue(self.api.release['draft'])
        self.assertFalse(any(method in ('PATCH', 'DELETE') for method, _, _ in self.api.calls))

    def test_corrupt_download_blocks_publication(self):
        self.api.bad_download = True
        with self.assertRaisesRegex(ValueError, 'SHA-256 mismatch'):
            self.publish()
        self.assertTrue(self.api.release['draft'])

    def test_wrong_checksum_blocks_network_and_tag_creation(self):
        (self.package / stable.ASSETS[1]).write_text('invalid')
        with self.assertRaisesRegex(ValueError, 'checksum file mismatch'):
            self.publish()
        self.assertEqual(self.api.calls, [])

    def test_extra_or_missing_artifact_blocks_network(self):
        (self.package / 'extra.txt').write_text('extra')
        with self.assertRaisesRegex(ValueError, 'artifact files'):
            self.publish()
        (self.package / 'extra.txt').unlink()
        (self.package / stable.ASSETS[0]).unlink()
        with self.assertRaisesRegex(ValueError, 'artifact files'):
            self.publish()
        self.assertEqual(self.api.calls, [])

    def test_validation_rejects_new_workflow_commit(self):
        self.mock.stop()
        with patch.object(stable.subprocess, 'check_output', return_value='different-head\n'):
            with self.assertRaisesRegex(ValueError, 'fixed accepted Commit'):
                stable.validation(self.source)

    def test_validation_rejects_modified_candidate_source(self):
        self.mock.stop()
        original = stable.subprocess.check_output
        def git_result(args, **kwargs):
            if args[1] == 'rev-parse':
                return stable.COMMIT + '\n'
            return original(args, cwd=ROOT)
        (self.source / 'START-HERE.md').write_text('modified')
        with patch.object(stable.subprocess, 'check_output', side_effect=git_result):
            with self.assertRaisesRegex(ValueError, 'candidate source changed'):
                stable.validation(self.source)

    def test_api_only_404_can_mean_absent(self):
        api = stable.GitHub.__new__(stable.GitHub)
        api.token = 'dummy-test-token'
        for status in (403, 404, 500):
            error = stable.urllib.error.HTTPError('https://api.github.com/', status, 'test', {}, None)
            with self.subTest(status=status), patch.object(stable.urllib.request, 'urlopen', side_effect=error):
                if status == 404:
                    self.assertIsNone(api.request('GET', 'git/ref/tags/v0.1.4', absent_ok=True))
                else:
                    with self.assertRaisesRegex(ValueError, f'HTTP {status}'):
                        api.request('GET', 'git/ref/tags/v0.1.4', absent_ok=True)

    def test_workflow_is_manual_and_separates_read_and_write_permissions_static(self):
        text = (ROOT / '.github/workflows/stable-release.yml').read_text()
        self.assertIn('  workflow_dispatch:', text)
        self.assertNotIn('  push:', text)
        self.assertNotIn('  pull_request:', text)
        validate, publish = text.split('  publish:\n')
        self.assertNotIn('contents: write', validate)
        self.assertIn('contents: write', publish)
        self.assertIn('needs: validate', publish)
        self.assertEqual(text.count('ref: ' + stable.COMMIT), 2)
        self.assertIn("github.ref == 'refs/heads/main'", text)


if __name__ == '__main__':
    unittest.main()
