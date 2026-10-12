"""Executable packaging and release-gate tests, independent of historical fixtures."""
import hashlib
import importlib.util
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('validation', ROOT / 'scripts/validate.py')
validation = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validation)


class PackageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='sa-package-test-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for name in (*validation.MEMBERS, 'README.md', 'scripts/package-release.sh'):
            target = self.root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / name, target)
        self.archive = self.root / 'sa-legal-skills.zip'

    def package(self):
        subprocess.run(['bash', 'scripts/package-release.sh'], cwd=self.root,
                       check=True, capture_output=True)

    def cli(self, *args):
        return subprocess.run([sys.executable, str(ROOT / 'scripts/validate.py'),
                               '--root', str(self.root), *args], capture_output=True, text=True)

    def test_fresh_checkout_package_and_independent_hash(self):
        result = self.cli()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('PASS:', result.stdout)
        first = hashlib.sha256(self.archive.read_bytes()).hexdigest()
        self.archive.unlink()
        self.package()
        self.assertEqual(first, hashlib.sha256(self.archive.read_bytes()).hexdigest())
        validation.validate_zip(self.root, self.archive)

    def test_missing_skill_exits_nonzero(self):
        (self.root / validation.MEMBERS[-1]).unlink()
        result = self.cli()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('missing required file:', result.stderr)
        packaged = subprocess.run(['bash', 'scripts/package-release.sh'], cwd=self.root,
                                  capture_output=True, text=True)
        self.assertNotEqual(packaged.returncode, 0)
        self.assertFalse(self.archive.exists())

    def test_wrong_skill_name(self):
        p = self.root / validation.MEMBERS[-1]
        p.write_text(p.read_text().replace('name: amendment-drafting', 'name: wrong'))
        result = self.cli()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Skill name mismatch', result.stderr)

    def test_entry_reference_missing(self):
        p = self.root / 'START-HERE.md'
        p.write_text(p.read_text().replace('regulation-review', 'wrong-review'))
        self.assertNotEqual(self.cli().returncode, 0)

    def write_zip(self, names, changed=None):
        with ZipFile(self.archive, 'w') as z:
            for name in names:
                z.writestr(name, b'wrong content' if name == changed else
                           (self.root / name).read_bytes() if name in validation.MEMBERS else b'extra')

    def test_content_mismatch(self):
        self.write_zip(validation.MEMBERS, changed='START-HERE.md')
        with self.assertRaisesRegex(ValueError, 'content mismatch'):
            validation.validate_zip(self.root, self.archive)

    def test_extra_missing_and_unsafe_member(self):
        for names in (validation.MEMBERS[:-1], (*validation.MEMBERS, 'extra.md'),
                      (*validation.MEMBERS, '../escape.md')):
            with self.subTest(names=names):
                self.write_zip(names)
                with self.assertRaisesRegex(ValueError, 'members mismatch'):
                    validation.validate_zip(self.root, self.archive)
        self.assertFalse((self.root.parent / 'escape.md').exists())

    def test_invalid_zip(self):
        self.archive.write_bytes(b'not a ZIP')
        from zipfile import BadZipFile
        with self.assertRaises(BadZipFile):
            validation.validate_zip(self.root, self.archive)

    def test_faulty_packager_fails_cli(self):
        (self.root / 'scripts/package-release.sh').write_text(
            "#!/bin/bash\npython3 - <<'PY'\nfrom zipfile import ZipFile\n"
            "with ZipFile('sa-legal-skills.zip', 'w') as z: z.writestr('wrong', 'wrong')\nPY\n")
        result = self.cli()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('ZIP members mismatch', result.stderr)

    def test_non_deterministic_packager_fails(self):
        p = self.root / 'scripts/package-release.sh'
        p.write_text(p.read_text().replace('date_time=(1980, 1, 1, 0, 0, 0)',
            'date_time=(1980, 1, 1, 0, 0, 2 * int((root / "counter").read_text()))')
            .replace('output = root / "sa-legal-skills.zip"',
            'counter = root / "counter"\n'
            'counter.write_text(str(int(counter.read_text()) + 1) if counter.exists() else "1")\n'
            'output = root / "sa-legal-skills.zip"'))
        result = self.cli()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('SHA-256 values differ', result.stderr)

    def test_illegal_tags_fail_cli_before_build(self):
        for tag in ('v0.1.3', 'v0.1.4-rc.1', 'v0.1.4-beta.1-extra',
                    'v01.1.4-beta.1', 'v0.01.4-beta.1', 'v0.1.04-beta.1',
                    'v0.1.4-beta.01', 'v0.1.4-beta.x', 'main', 'v0.1.4-beta.1\n'):
            with self.subTest(tag=tag):
                result = self.cli('--beta-tag', tag)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn('illegal Beta tag', result.stderr)
                self.assertFalse(self.archive.exists())


class AncestryTests(unittest.TestCase):
    # Synthetic tags exist only inside disposable local Git fixtures, never in the project.
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='sa-git-test-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.git('init', '-b', 'develop')
        self.git('config', 'user.name', 'Test')
        self.git('config', 'user.email', 'test@example.invalid')
        self.git('commit', '--allow-empty', '-m', 'base')
        self.base = self.git('rev-parse', 'HEAD')
        self.git('update-ref', 'refs/remotes/origin/develop', self.base)

    def git(self, *args):
        return subprocess.check_output(['git', *args], cwd=self.root,
                                       stderr=subprocess.STDOUT, text=True).strip()

    def test_lightweight_and_annotated_develop_tags(self):
        self.git('tag', 'v0.1.4-beta.1')
        self.git('tag', '-a', 'v0.1.4-beta.2', '-m', 'synthetic test')
        for tag in ('v0.1.4-beta.1', 'v0.1.4-beta.2'):
            validation.validate_beta(self.root, tag)

    def test_older_develop_commit_accepted(self):
        self.git('tag', 'v0.1.4-beta.1')
        self.git('commit', '--allow-empty', '-m', 'new develop')
        self.git('update-ref', 'refs/remotes/origin/develop', self.git('rev-parse', 'HEAD'))
        self.git('checkout', '--detach', self.base)
        validation.validate_beta(self.root, 'v0.1.4-beta.1')

    def test_unmerged_branch_rejected(self):
        self.git('switch', '-c', 'unmerged')
        self.git('commit', '--allow-empty', '-m', 'unmerged')
        self.git('tag', 'v0.1.4-beta.1')
        with self.assertRaisesRegex(ValueError, 'not in develop history'):
            validation.validate_beta(self.root, 'v0.1.4-beta.1')

    def test_wrong_checkout_rejected(self):
        self.git('tag', 'v0.1.4-beta.1')
        self.git('commit', '--allow-empty', '-m', 'later develop')
        with self.assertRaisesRegex(ValueError, 'HEAD is not'):
            validation.validate_beta(self.root, 'v0.1.4-beta.1')

    def test_integrated_develop_commit_without_main_accepted(self):
        # New integrated development does not need a stable-main merge.
        self.git('update-ref', 'refs/remotes/origin/main', self.base)
        self.git('commit', '--allow-empty', '-m', 'integrated develop')
        self.git('update-ref', 'refs/remotes/origin/develop', self.git('rev-parse', 'HEAD'))
        self.git('tag', 'v0.1.4-beta.1')
        validation.validate_beta(self.root, 'v0.1.4-beta.1')

    def test_main_only_commit_rejected(self):
        self.git('switch', '-c', 'main-only')
        self.git('commit', '--allow-empty', '-m', 'not integrated into develop')
        self.git('update-ref', 'refs/remotes/origin/main', self.git('rev-parse', 'HEAD'))
        self.git('tag', 'v0.1.4-beta.1')
        with self.assertRaisesRegex(ValueError, 'not in develop history'):
            validation.validate_beta(self.root, 'v0.1.4-beta.1')

    def test_missing_develop_ref_fails_cli(self):
        self.git('tag', 'v0.1.4-beta.1')
        self.git('update-ref', '-d', 'refs/remotes/origin/develop')
        result = subprocess.run([sys.executable, str(ROOT / 'scripts/validate.py'),
                                 '--root', str(self.root), '--beta-tag', 'v0.1.4-beta.1'],
                                text=True, capture_output=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('develop history ref missing or invalid', result.stderr)

    def test_shallow_history_rejected(self):
        self.git('tag', 'v0.1.4-beta.1')
        (self.root / '.git/shallow').write_text(self.base + '\n')
        with self.assertRaisesRegex(ValueError, 'shallow checkout rejected'):
            validation.validate_beta(self.root, 'v0.1.4-beta.1')

    def test_missing_tag_rejected(self):
        with self.assertRaises(subprocess.CalledProcessError):
            validation.validate_beta(self.root, 'v0.1.4-beta.1')


if __name__ == '__main__':
    unittest.main()
