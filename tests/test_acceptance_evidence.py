"""Synthetic offline integrity tests and static plan checks; NO real model calls."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
TEMPLATE=ROOT/'docs/acceptance/run-template.json'
spec=importlib.util.spec_from_file_location('evidence',ROOT/'scripts/check_acceptance_evidence.py')
evidence=importlib.util.module_from_spec(spec)
spec.loader.exec_module(evidence)


class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        self.record=json.loads(TEMPLATE.read_text())
        self.record['run_id']='synthetic-test-only'

    def artifact(self,id,path,kind,origin,text='SYNTHETIC TEST DATA, NOT A REAL MODEL OUTPUT\n'):
        (self.root/path).write_text(text)
        content=(self.root/path).read_bytes()
        entry={'id':id,'path':path,'kind':kind,'origin':origin,
               'sha256':hashlib.sha256(content).hexdigest(),'byte_size':len(content)}
        self.record['artifacts'].append(entry)
        return {'artifact_id':id,'anchor':'synthetic line 1'}

    def declared_run(self):
        # Pretend declarations ONLY to test structure. Never publish as live run/evidence.
        inp=self.artifact('input','input.txt','input','USER_INPUT')
        out=self.artifact('output','output.txt','raw_output','MODEL_OUTPUT')
        call=self.artifact('call','call.txt','call_evidence','SELF_REPORTED')
        self.record.update(inputs=[inp],outputs=[out],status='PASS')
        self.record['execution']={'kind':'HUMAN_MODEL_RUN','actual_model_call':True,'call_evidence':call}
        self.record['isolation'].update(fresh_conversation=True,evidence='synthetic declared setup')
        self.record['adjudication']={'verifier':'synthetic fixture, not actual verifier','basis':'testing declarations only',
                                    'evidence_anchors':[out],'limitations':['NOT REAL MODEL TEST']}

    def test_empty_not_tested_template_is_not_promoted(self):
        checked=evidence.check(self.record,self.root)
        self.assertEqual(checked['status'],'NOT TESTED')
        self.assertEqual(checked['execution']['actual_model_call'],False)

    def test_required_fields_and_bad_ids_rejected(self):
        for field in evidence.REQUIRED:
            bad=copy.deepcopy(self.record)
            del bad[field]
            with self.subTest(field=field),self.assertRaises(ValueError):
                evidence.check(bad,self.root)
        self.record['candidate_commit']='main'
        with self.assertRaises(ValueError):
            evidence.check(self.record,self.root)

    def test_synthetic_or_static_cannot_be_model_pass(self):
        for kind in ('PLANNED','SYNTHETIC','STATIC'):
            self.record['execution']['kind']=kind
            self.record['status']='PASS'
            with self.subTest(kind=kind),self.assertRaisesRegex(ValueError,'no actual model call'):
                evidence.check(self.record,self.root)

    def test_declared_run_integrity_does_not_certify_truth(self):
        self.declared_run()
        checked=evidence.check(self.record,self.root)
        self.assertEqual(checked['status'],'PASS') # Caller verdict unchanged; no semantic/real-world claim.
        self.assertIn('NOT REAL MODEL TEST',checked['adjudication']['limitations'])

    def test_expected_reference_and_missing_raw_output_cannot_be_tested(self):
        self.declared_run()
        self.record['artifacts'][1]['origin']='EXPECTED_REFERENCE'
        with self.assertRaisesRegex(ValueError,'raw output'):
            evidence.check(self.record,self.root)
        self.record['artifacts'][1]['origin']='MODEL_OUTPUT'
        self.record['outputs']=[]
        with self.assertRaises(ValueError):
            evidence.check(self.record,self.root)

    def test_actual_call_verifier_and_anchor_requirements(self):
        for defect in ('call','verifier','anchor','isolated'):
            self.record=json.loads(TEMPLATE.read_text()); self.record['run_id']='synthetic'
            self.declared_run()
            if defect=='call': self.record['execution']['call_evidence']=None
            elif defect=='verifier': self.record['adjudication']['verifier']=None
            elif defect=='anchor': self.record['outputs'][0]['artifact_id']='missing'
            else: self.record['isolation']['fresh_conversation']=False
            with self.subTest(defect=defect),self.assertRaises(ValueError):
                evidence.check(self.record,self.root)

    def test_file_missing_tamper_size_and_symlink_escape(self):
        self.artifact('a','a.txt','other','SYNTHETIC')
        (self.root/'a.txt').write_text('altered')
        with self.assertRaisesRegex(ValueError,'hash mismatch'):
            evidence.check(self.record,self.root,index_bytes=True)
        (self.root/'a.txt').unlink()
        with self.assertRaises(ValueError):
            evidence.check(self.record,self.root)
        outside=self.root.parent/(self.root.name+'-outside.txt')
        outside.write_text('outside synthetic data')
        self.addCleanup(outside.unlink)
        (self.root/'a.txt').symlink_to(outside)
        with self.assertRaises(ValueError):
            evidence.check(self.record,self.root)

    def test_byte_index_is_computed_and_cli_never_grades_or_overwrites(self):
        self.artifact('a','a.txt','other','SYNTHETIC')
        entry=self.record['artifacts'][0]
        entry['sha256']=entry['byte_size']=None
        path=self.root/'record.json'; path.write_text(json.dumps(self.record))
        original=path.read_bytes()
        command=[sys.executable,str(ROOT/'scripts/check_acceptance_evidence.py'),str(path),'--index-bytes']
        result=subprocess.run(command,text=True,capture_output=True)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertIn('INTEGRITY CHECK ONLY',result.stdout)
        indexed=json.loads((self.root/'record.indexed.json').read_text())
        self.assertEqual(indexed['status'],'NOT TESTED')
        self.assertEqual(indexed['artifacts'][0]['sha256'],hashlib.sha256((self.root/'a.txt').read_bytes()).hexdigest())
        self.assertEqual(path.read_bytes(),original)
        again=subprocess.run(command,text=True,capture_output=True)
        self.assertNotEqual(again.returncode,0)

    def test_size_bad_path_and_planned_quality_claims_rejected(self):
        self.artifact('a','a.txt','other','SYNTHETIC')
        entry=self.record['artifacts'][0]
        entry['byte_size']+=1
        with self.assertRaisesRegex(ValueError,'size mismatch'):
            evidence.check(self.record,self.root)
        entry['byte_size']-=1
        for name in ('../outside.txt','/tmp/outside.txt','a/../a.txt'):
            bad=copy.deepcopy(self.record); bad['artifacts'][0]['path']=name
            with self.subTest(name=name),self.assertRaises(ValueError):
                evidence.check(bad,self.root)
        self.record['quality']['source_fidelity']='PASS'
        with self.assertRaises(ValueError):
            evidence.check(self.record,self.root)

    def test_skill_full_read_requires_recorded_evidence(self):
        self.artifact('skill','skill.txt','skill','SYNTHETIC')
        self.record['skill_sources']=[{'name':'regulation-review','path':'skills/regulation-review/SKILL.md',
                                     'commit':'UNVERIFIED','read_status':'FULL','artifact_id':'skill','evidence_anchor':None}]
        with self.assertRaises(ValueError):
            evidence.check(self.record,self.root)
        self.record['skill_sources'][0]['read_status']='UNVERIFIED'
        self.assertEqual(evidence.check(self.record,self.root)['skill_sources'][0]['commit'],'UNVERIFIED')

    def test_visual_claim_without_reviewed_pages_or_pdf_rejected(self):
        self.declared_run()
        self.record['quality']['visual_qa']='PASS'
        with self.assertRaises(ValueError):
            evidence.check(self.record,self.root)
        self.record['quality']['pages_reviewed']=[1]
        self.record['quality']['visual_evidence']=self.record['outputs'][0]
        with self.assertRaisesRegex(ValueError,'PDF/page image'):
            evidence.check(self.record,self.root)


class AcceptancePlanStaticTests(unittest.TestCase):
    def test_matrix_reuses_eight_cases_and_all_cells_not_tested(self):
        matrix=json.loads((ROOT/'docs/acceptance/model-matrix.json').read_text())
        ids=[case['id'] for case in matrix['cases']]
        self.assertEqual(len(ids),len(set(ids)))
        self.assertEqual(len(ids),21)
        self.assertEqual(len(matrix['platforms']),4)
        self.assertEqual(matrix['evidence_level'],'SPECIFICATION_ONLY')
        self.assertTrue(all(case['status']=='NOT TESTED' for case in matrix['cases']))
        for i in range(1,9):
            case=next(c for c in matrix['cases'] if c['id']==f'P0-CASE-{i:02d}')
            self.assertEqual(case['source'],'docs/regression/v0.1.4-p0-cases.md')
        for case in matrix['cases']:
            self.assertTrue((ROOT/case['source']).is_file())
            for key in ('steps','expected','forbidden'):
                self.assertTrue(case[key])

    def test_docs_distinguish_test_levels_and_human_release_decision(self):
        plan=(ROOT/'docs/acceptance/model-regression.md').read_text()
        checklist=(ROOT/'docs/acceptance/beta-checklist.md').read_text()
        guide=(ROOT/'docs/acceptance/record-guide.md').read_text()
        for text,clauses in ((plan,('0/84','NOT TESTED','reference生成的DOCX','實際對話export')),
                             (checklist,('建議','使用者決定','不新增發布機制','VISUAL QA: NOT TESTED')),
                             (guide,('INTEGRITY CHECK ONLY','手寫expected不是outputs','不解析對話語義'))):
            for clause in clauses:
                self.assertIn(clause,text)


if __name__=='__main__':
    unittest.main()
