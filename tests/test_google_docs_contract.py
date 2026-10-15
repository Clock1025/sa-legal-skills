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
            'only when the user explicitly chooses it',
            'never switch to DOCX automatically',
            'stop the affected operations and preserve the current document state',
            'failure reason, verified completed changes, unfinished work',
            'Do not create a substitute Google Docs or DOCX',
            'A Google Docs failure does not authorize a change of document mode',
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

        for removed_rule in ('continue with the existing DOCX workflow',
                             'offer DOCX or a patch',
                             'the fallback when safe Google Docs editing is unavailable'):
            for skill in SKILLS:
                with self.subTest(skill=skill, removed_rule=removed_rule):
                    self.assertNotIn(removed_rule, (ROOT / f'skills/{skill}/SKILL.md').read_text())

    def test_template_minimum_contract_is_available_without_guides(self):
        # Core equality is checked above; these are static requirements, not API calls.
        block = workflow((ROOT / 'skills/amendment-drafting/SKILL.md').read_text())
        for requirement in (
            'never hardcode private template IDs, URLs or contents',
            'If the template is missing, ask for it', 'keep the template read-only',
            'destination differs from the template before any write',
            'Resume the verified working copy', 'extend native rows beyond',
            'read → conditionally write using the fresh revision → read back',
            'first-page title 「學生議會關係文書」 24 pt', 'proposal fields 14 pt',
            '20 pt with a native page break', 'table header/body 12 pt',
            '139.5 pt each', '`DFKai-SB`', 'A4 portrait',
            'changed text only, never unchanged text or structural whitespace',
            'reported template acceptance does not verify a new copy',
        ):
            with self.subTest(requirement=requirement):
                self.assertIn(requirement, block)

    def test_template_drafting_requires_precise_styles_and_safe_resume(self):
        text = (ROOT / 'skills/amendment-drafting/SKILL.md').read_text()
        section = text.split('## Google Docs template proposal production', 1)[1].split('## Drafting deliverables', 1)[0]
        for requirement in (
            'one instrument per formal proposal', 'Do not invent the proposer',
            'one logical data row', 'more than two provisions',
            '「（本條新增）」', '「（刪除）」', 'U+3000',
            '「七」→「五」', 'not also underline 「日前」',
            'UTF-16 code units', 'checkpoint only after readback',
            'do not duplicate rows or create another copy',
            'requiredRevisionId', 'targetRevisionId',
            'no placeholder/sample residue', 'actual copy',
            'GOOGLE DOCS LIVE OPERATIONS: NOT TESTED', 'VISUAL QA: NOT TESTED',
        ):
            with self.subTest(requirement=requirement):
                self.assertIn(requirement, section)
        # Public prompts and guides must not embed a runtime private template link/ID.
        import re
        paths = [ROOT / f'skills/{skill}/SKILL.md' for skill in SKILLS]
        paths += [ROOT / 'docs/google-docs-workflow.md',
                  ROOT / 'docs/acceptance/google-docs-template.md']
        for path in paths:
            self.assertIsNone(re.search(r'https?://(?:docs|drive)\.google\.com/[^\s)]+', path.read_text()), path)

    def test_ci_targets_integration_branches_without_feature_hardcoding(self):
        # No YAML dependency: check the two existing event branch filters.
        ci = (ROOT / '.github/workflows/ci.yml').read_text()
        self.assertEqual(ci.count('branches: [main, develop, develop-0.2]'), 2)
        self.assertNotIn('feature/', ci)

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
                    self.assertEqual(archive.read(f'skills/{skill}/SKILL.md'),
                                     (ROOT / f'skills/{skill}/SKILL.md').read_bytes())
                self.assertIn('Google Docs', archive.read('START-HERE.md').decode())


if __name__ == '__main__':
    unittest.main()
