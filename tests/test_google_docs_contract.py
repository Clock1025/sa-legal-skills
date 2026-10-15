"""Static prompt/ZIP contract only; no Google Docs API or model execution."""
from pathlib import Path
import tempfile
import unittest
from zipfile import ZipFile
import subprocess
import shutil

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ('amendment-drafting', 'regulation-review', 'large-scale-reform')


def workflow(text):
    return text.split('## Google Docs / DOCX workflow\n', 1)[1].split('## Skill Feedback Package', 1)[0]


class GoogleDocsContractTests(unittest.TestCase):
    def test_same_self_contained_safety_contract_in_all_three_skills(self):
        blocks = [workflow((ROOT / 'skills' / skill / 'SKILL.md').read_text()) for skill in SKILLS]
        self.assertEqual(blocks, [blocks[0]] * 3)
        # Deliberate contract assertions, not a simulation of integration success.
        for requirement in (
            'read gates, legal-source fidelity, policy confirmation',
            'document-specific edit permission', 'Do not infer support from a model name',
            'editing the supplied existing Google Docs in place',
            'do not regenerate or replace the whole document by default',
            'write that unit promptly', 'Existing explicit confirmation suffices',
            'Immediately before each write, reread', 'writeControl.requiredRevisionId',
            'targetRevisionId', 'reread alone closes the read/write race',
            'If no equivalent conditional write is exposed, stop automatic writes',
            'Never force overwrite', 'After each write, read the actual document again',
            'read before any retry', 'DOCX is a snapshot',
            'GOOGLE DOCS LIVE OPERATIONS: NOT TESTED',
        ):
            with self.subTest(requirement=requirement):
                self.assertIn(requirement, blocks[0])

    def test_five_file_zip_carries_the_contract_without_docs(self):
        # Work on a minimal copy so this test cannot overwrite a user's ZIP.
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in ('START-HERE.md', 'LICENSE', 'scripts/package-release.sh',
                         *(f'skills/{s}/SKILL.md' for s in SKILLS)):
                target = root / name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / name, target)
            subprocess.run(['bash', 'scripts/package-release.sh'], cwd=root, check=True, capture_output=True)
            with ZipFile(root / 'sa-legal-skills.zip') as archive:
                self.assertEqual(len(archive.namelist()), 5)
                for skill in SKILLS:
                    self.assertEqual(workflow(archive.read(f'skills/{skill}/SKILL.md').decode()),
                                     workflow((ROOT / f'skills/{skill}/SKILL.md').read_text()))
                self.assertIn('Google Docs', archive.read('START-HERE.md').decode())


if __name__ == '__main__':
    unittest.main()
