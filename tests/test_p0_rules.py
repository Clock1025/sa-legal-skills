"""Static rule-presence checks only; no model inference or legal/semantic validator."""
from pathlib import Path
import copy
import json
import re
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


def check_example_structure(record):
    """Check demonstration fields/links only, not truth or legal/model semantics."""
    def require(condition, message):
        if not condition:
            raise ValueError(message)
    require(record['example_type'] == 'FICTIONAL_DEMONSTRATION', 'fictional label missing')
    issue = record['issue']
    require(re.fullmatch(r'I-[0-9]{3}', issue['id']) and issue['status'] == 'OPEN', 'issue identity/status')
    sources = {source['id']: source for source in record['sources']}
    require(len(sources) == len(record['sources']), 'duplicate source ID')
    for sid, source in sources.items():
        require(re.fullmatch(r'SRC-[0-9]{3}', sid), 'source ID')
        if source['type'] == 'legal_text_not_provided':
            require(source['version'] == source['location'] == 'UNVERIFIED' and source['text'] is None,
                    'unprovided legal source falsely verified')
    ids = [decision['id'] for decision in record['decisions']]
    require(len(ids) == len(set(ids)) and ids == issue['decision_ids'], 'decision IDs inconsistent')
    require(any(d['status'] == 'CONFIRMED' for d in record['decisions']), 'confirmed atomic example missing')
    for decision in record['decisions']:
        require(re.fullmatch(r'D-[0-9]{3}', decision['id']), 'decision ID')
        require(decision['issue_id'] == issue['id'], 'issue link')
        scope = decision['scope']
        require(all(scope.get(key) for key in ('instrument', 'offices', 'limits')), 'scope missing')
        require(decision['source_ids'] and all(sid in sources for sid in decision['source_ids']), 'source link')
        basis = decision['confirmation_basis']
        if decision['status'] == 'CONFIRMED':
            require(basis is not None, 'confirmation basis missing')
            require(basis['source_id'] in decision['source_ids'], 'confirmation source link')
            source = sources[basis['source_id']]
            require(source['type'] == 'fictional_user_statement' and source['version'] == 'example-1',
                    'confirmation must link fictional input')
            require(basis['location'] == source['location'] and basis['quote'] in source['text'],
                    'confirmation quote/location mismatch')
        else:
            require(decision['status'] in ('DIRECTION', 'OPEN') and basis is None, 'unconfirmed basis')


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

    def test_case04_multi_option_assent_and_case05_truncated_clause_rules(self):
        """Static guardrails; behavioral correctness still needs real-model testing."""
        text = (ROOT / 'skills/large-scale-reform/SKILL.md').read_text()
        case04 = ('In a multi-option discussion', 'a bare 「加上去」',
                  'added for discussion', 'formally adopted as policy',
                  'Keep statuses unchanged', 'one short, specific clarification',
                  'Only promote the precisely identified decision')
        case05 = ('the entire input is 「委員之任免由」',
                  'do not complete the sentence', 'infer an appointing body',
                  'Keep the affected policy unresolved')
        for case, clauses in (('04', case04), ('05', case05)):
            with self.subTest(case=case):
                self.assertEqual(missing_fragments(text, clauses), [])

    def test_drafting_preserves_status_scope_and_mapping_contract(self):
        text = (ROOT / 'skills/amendment-drafting/SKILL.md').read_text()
        fragments = ('CONFIRMED', 'DIRECTION', 'OPEN', 'DEFERRED', 'SUPERSEDED',
                     'ASSISTANT_PROPOSAL', 'Only **CONFIRMED** policy within its recorded scope',
                     'clearly labeled, separate working candidates', 'decision/source IDs',
                     'old-to-new provision mappings', 'new matters requiring confirmation',
                     'policy consequences', 'current-text column and quotations remaining faithful')
        self.assertEqual(missing_fragments(text, fragments), [])

    def test_example_record_structure_and_traceable_fictional_input(self):
        text = (ROOT / 'skills/large-scale-reform/SKILL.md').read_text()
        records = [json.loads(raw) for raw in re.findall(r'```json\n(.*?)\n```', text, re.S)]
        self.assertEqual(len(records), 2)
        all_ids = []
        for record in records:
            check_example_structure(record)
            all_ids.extend([record['issue']['id'], *record['issue']['decision_ids'],
                            *(source['id'] for source in record['sources'])])
        self.assertEqual(len(all_ids), len(set(all_ids)))

    def test_example_missing_scope_basis_or_wrong_link_rejected(self):
        text = (ROOT / 'skills/large-scale-reform/SKILL.md').read_text()
        record = json.loads(re.findall(r'```json\n(.*?)\n```', text, re.S)[0])
        for defect in ('scope', 'basis', 'quote', 'duplicate', 'legal_version'):
            with self.subTest(defect=defect):
                bad = copy.deepcopy(record)
                if defect == 'scope':
                    bad['decisions'][0]['scope']['limits'] = ''
                elif defect == 'basis':
                    bad['decisions'][0]['confirmation_basis'] = None
                elif defect == 'quote':
                    bad['decisions'][0]['confirmation_basis']['quote'] = 'not in the fictional source'
                elif defect == 'duplicate':
                    bad['decisions'][1]['id'] = bad['decisions'][0]['id']
                else:
                    bad['sources'][1]['version'] = 'pretend-verified'
                with self.assertRaises(ValueError):
                    check_example_structure(bad)

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
