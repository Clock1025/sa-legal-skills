"""Source gate tests using local Git fixtures; no GitHub writes or release tags."""
import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('prepare_alpha', ROOT / 'scripts/prepare_alpha.py')
alpha = importlib.util.module_from_spec(spec)
spec.loader.exec_module(alpha)


class AlphaSourceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.git('init', '-b', 'integrated')
        self.git('config', 'user.name', 'Fixture')
        self.git('config', 'user.email', 'fixture@example.invalid')
        self.git('commit', '--allow-empty', '-m', 'integrated')
        self.commit = self.git('rev-parse', 'HEAD')
        self.git('update-ref', alpha.INTEGRATION_REF, self.commit)

    def git(self, *args):
        return subprocess.check_output(['git', '-C', str(self.root), *args], text=True,
                                       stderr=subprocess.DEVNULL).strip()

    def test_integrated_exact_commit_accepted_without_v01_develop(self):
        alpha.validate_source(self.root, self.commit)

    def test_feature_only_commit_rejected(self):
        self.git('commit', '--allow-empty', '-m', 'feature only')
        with self.assertRaisesRegex(ValueError, 'not integrated'):
            alpha.validate_source(self.root, self.git('rev-parse', 'HEAD'))

    def test_wrong_checkout_or_abbreviated_sha_rejected(self):
        with self.assertRaisesRegex(ValueError, '40-character'):
            alpha.validate_source(self.root, self.commit[:7])
        self.git('commit', '--allow-empty', '-m', 'later')
        with self.assertRaisesRegex(ValueError, 'HEAD does not match'):
            alpha.validate_source(self.root, self.commit)

    def test_missing_integration_ref_rejected(self):
        self.git('update-ref', '-d', alpha.INTEGRATION_REF)
        with self.assertRaises(subprocess.CalledProcessError):
            alpha.validate_source(self.root, self.commit)

    def test_workflow_only_publishes_explicit_alpha_tag_as_non_latest(self):
        workflow = (ROOT / '.github/workflows/alpha-v02.yml').read_text()
        self.assertIn('branches: [develop-0.2]', workflow)
        self.assertIn("tags: ['v0.2.0-alpha.2']", workflow)
        self.assertIn("if: github.event_name == 'push'", workflow)
        self.assertIn("github.ref == 'refs/tags/v0.2.0-alpha.2'", workflow)
        self.assertIn('--draft --prerelease --latest=false', workflow)
        self.assertIn('--draft=false --prerelease --latest=false', workflow)
        self.assertNotIn('--method POST', workflow)  # Workflow never creates tags.
        self.assertNotIn('--clobber', workflow)

    def test_modified_source_rejected(self):
        (self.root / 'unreviewed.txt').write_text('unreviewed')
        with self.assertRaisesRegex(ValueError, 'changes'):
            alpha.validate_source(self.root, self.commit)


if __name__ == '__main__':
    unittest.main()
