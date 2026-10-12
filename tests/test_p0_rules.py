"""Static rule-presence checks only; no model inference or legal/semantic validator."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ('regulation-review', 'large-scale-reform', 'amendment-drafting')
# Fragments intentionally track the documented contract. They cannot prove model obedience.
CONTRACTS = {
    '01': ('fully read the new Skill', 'stop at obtaining/pasting/uploading',
           'do not bypass the START-HERE read gate'),
    '02': ('source path', 'version/commit/ref', 'actually read in this turn',
           '**UNVERIFIED**', 'explicitly request the source', 'do not invent a commit'),
    '05': ('exact incomplete fragment', 'one necessary clarification question',
           'clause ending in 「由」', 'Never silently supply'),
    '08': ('possible substantive change', '「該會議」', '「其出席之會議」',
           'obtain user confirmation'),
}
REFORM_CONTRACTS = {
    '03': ('Only **CONFIRMED** policy within its recorded scope',
           'ASSISTANT_PROPOSAL', 'clearly labeled, separate working candidates'),
    '04': ('「比較傾向 C」', 'DIRECTION', '「加上去」', '「照這個」',
           'specific option, scope, and policy consequences', 'ask what was agreed'),
    '06': ('A later-added instrument or source is not automatically covered',
           'new scope still needing confirmation', 'ask again',
           'Do not confuse proposal text with effective current law'),
    '07': ('`D-001`', '`I-001`', '`SRC-001`', 'independent of article numbers',
           'old-to-new provision mapping', 'version on both sides',
           'Never fabricate sources', 'supersession links'),
}


def missing_fragments(text, fragments):
    """Report absent literal clauses; never classify an actual agent answer."""
    return [fragment for fragment in fragments if fragment not in text]


class P0StaticTests(unittest.TestCase):
    def test_common_rules_present_in_each_skill(self):
        for skill in SKILLS:
            text = (ROOT / 'skills' / skill / 'SKILL.md').read_text()
            for case, fragments in CONTRACTS.items():
                with self.subTest(skill=skill, case=case):
                    self.assertEqual(missing_fragments(text, fragments), [])

    def test_reform_decision_and_source_rules_present(self):
        text = (ROOT / 'skills/large-scale-reform/SKILL.md').read_text()
        for case, fragments in REFORM_CONTRACTS.items():
            with self.subTest(case=case):
                self.assertEqual(missing_fragments(text, fragments), [])

    def test_missing_rule_mutations_rejected(self):
        # Negative controls remove each required clause, not simulate a model response.
        text = (ROOT / 'skills/large-scale-reform/SKILL.md').read_text()
        for case, fragments in {**CONTRACTS, **REFORM_CONTRACTS}.items():
            for fragment in fragments:
                with self.subTest(case=case, fragment=fragment):
                    mutated = text.replace(fragment, '')
                    self.assertIn(fragment, missing_fragments(mutated, fragments))

    def test_drafting_preserves_status_scope_and_mapping_contract(self):
        text = (ROOT / 'skills/amendment-drafting/SKILL.md').read_text()
        fragments = ('CONFIRMED', 'DIRECTION', 'OPEN', 'DEFERRED', 'SUPERSEDED',
                     'ASSISTANT_PROPOSAL', 'Only **CONFIRMED** policy within its recorded scope',
                     'clearly labeled, separate working candidates', 'decision/source IDs',
                     'old-to-new provision mappings', 'new matters requiring confirmation',
                     'policy consequences', 'current-text column and quotations remaining faithful')
        self.assertEqual(missing_fragments(text, fragments), [])

    def test_eight_documented_cases_have_positive_negative_and_limits(self):
        text = (ROOT / 'docs/regression/v0.1.4-p0-cases.md').read_text()
        cases = text.split('\n## P0-CASE-')[1:]
        self.assertEqual(len(cases), 8)
        for number, case in enumerate(cases, 1):
            with self.subTest(case=number):
                self.assertTrue(case.startswith(f'{number:02d}：'))
                for field in ('輸入情境：', '期待行為：', '禁止行為：', '正例：', '否定例：',
                              '驗證類型：DOCUMENTED_SCENARIO / STATIC_RULE_PRESENCE',
                              '真人模型 NOT TESTED'):
                    self.assertIn(field, case)
        self.assertIn('REAL-MODEL BEHAVIOR: NOT TESTED / UNVERIFIED', text)


if __name__ == '__main__':
    unittest.main()
