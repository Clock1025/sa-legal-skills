"""合成／reference DOCX測試，不是模型輸出或視覺驗收。"""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET
from zipfile import ZIP_DEFLATED, ZipFile

from docx_reference import NS, W, expand_row, load_cases, write_docx

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('model_docx',ROOT/'scripts/check_model_docx.py')
quality=importlib.util.module_from_spec(spec);spec.loader.exec_module(quality)


class ModelDocxTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        self.fixture=load_cases();self.case=self.fixture['cases'][0]
        self.docx=write_docx(self.case,self.root/'reference-only.docx')
        self.source=self.make_source(self.case)
        self.json=self.root/'source.json';self.json.write_text(json.dumps(self.source,ensure_ascii=False),encoding='utf-8')

    def make_source(self,case):
        rows=[]
        for row in case['rows']:
            new,old,reason=expand_row(row)
            rows.append(dict(id=row['id'],amended=[p['text'] for p in new],current=[p['text'] for p in old],reason=[p['text'] for p in reason],
                             source_anchor='fictional fixture '+row['id'],confirmation_basis='fictional scenario input, NOT actual user decision'))
        return dict(schema_version='1.0',source=dict(name='虛構資料，非有效法律',version='docx-fixture-1',location='local synthetic fixture'),rows=rows)

    def mutate(self,change,styles=None,extra=None):
        with ZipFile(self.docx) as z: files={n:z.read(n) for n in z.namelist()}
        root=ET.fromstring(files['word/document.xml']);change(root)
        files['word/document.xml']=ET.tostring(root)
        if styles:files['word/styles.xml']=styles.encode()
        if extra:files.update(extra)
        with ZipFile(self.docx,'w',ZIP_DEFLATED) as z:
            for name,raw in files.items():z.writestr(name,raw)
        return self.docx.read_bytes()

    def cell(self,root,col=0):return root.findall('w:body/w:tbl/w:tr',NS)[1].findall('w:tc',NS)[col]

    def inspect(self,content=None):return quality.inspect(content or self.docx.read_bytes(),self.source,'REFERENCE')

    def test_all_six_reference_files_checked_but_never_model_or_visual_pass(self):
        for case in self.fixture['cases']:
            path=write_docx(case,self.root/(case['id']+'.docx'))
            report=quality.inspect(path.read_bytes(),self.make_source(case),'REFERENCE')
            with self.subTest(case=case['id']):
                self.assertTrue(report['content_equality'].startswith('PASS'))
                self.assertTrue(report['underline'].startswith('PASS'))
                self.assertEqual(report['model_origin'],'UNVERIFIED（需人工核對生成鏈）')
                self.assertEqual(report['visual_qa'],'NOT TESTED')
                self.assertEqual(report['findings'],[])
        # Independent short text assertions, not only shared fixture helper agreement.
        self.assertEqual(self.source['rows'][0]['current'],['第一條　應於會議七日前公告。'])
        self.assertEqual(self.source['rows'][0]['amended'],['第一條　應於會議五日前公告。'])

    def test_lost_changed_duplicated_and_swapped_text_are_high_content_findings(self):
        for defect in ('lost','changed','duplicated','swapped'):
            write_docx(self.case,self.docx)
            def mutation(root):
                cell=self.cell(root,1)
                if defect=='lost':cell.find('.//w:t',NS).text=''
                elif defect=='changed':
                    t=next(t for t in cell.findall('.//w:t',NS) if '七' in (t.text or ''));t.text='九'
                elif defect=='duplicated':cell.append(copy.deepcopy(cell.find('w:p',NS)))
                else:
                    row=root.findall('w:body/w:tbl/w:tr',NS)[1];cells=row.findall('w:tc',NS)
                    row.remove(cells[0]);row.insert(2,cells[0])
            report=self.inspect(self.mutate(mutation))
            with self.subTest(defect=defect):
                self.assertEqual(report['content_equality'],'FAIL')
                self.assertTrue(any(f['severity']=='HIGH' and f['code']=='TEXT_OR_PARAGRAPH_DIFFERENCE' for f in report['findings']))

    def test_missing_and_duplicate_rows_do_not_produce_unobserved_underline_pass(self):
        for duplicate in (False,True):
            write_docx(self.case,self.docx)
            def mutation(root):
                table=root.find('w:body/w:tbl',NS);row=table.findall('w:tr',NS)[1]
                if duplicate:table.append(copy.deepcopy(row))
                else:table.remove(row)
            report=self.inspect(self.mutate(mutation))
            self.assertEqual(report['content_equality'],'FAIL')
            self.assertEqual(report['underline'],'UNVERIFIED')

    def test_extra_day_underline_is_low_format_defect_not_legal_content_error(self):
        def mutation(root):
            p=self.cell(root,1).find('w:p',NS)
            run=next(r for r in p.findall('w:r',NS) if '日前' in ''.join(t.text or '' for t in r.findall('w:t',NS)))
            original=run.find('w:t',NS).text
            rest=copy.deepcopy(run);rest.find('w:t',NS).text=original[1:]
            run.find('w:t',NS).text=original[:1];run.find('w:rPr/w:u',NS).set('{'+W+'}val','single')
            p.insert(list(p).index(run)+1,rest)
        report=self.inspect(self.mutate(mutation))
        self.assertTrue(report['content_equality'].startswith('PASS'))
        self.assertEqual(report['underline'],'FAIL')
        self.assertEqual({f['severity'] for f in report['findings']},{'LOW'})
        self.assertEqual(report['observations'][0]['observed_text_changes'],[{'old':'七','new':'五'}])

    def test_missing_changed_underline_is_medium_format_defect(self):
        def mutation(root):
            for r in self.cell(root).findall('.//w:r',NS):r.find('w:rPr/w:u',NS).set('{'+W+'}val','none')
        report=self.inspect(self.mutate(mutation))
        self.assertTrue(report['content_equality'].startswith('PASS'))
        self.assertEqual(report['underline'],'FAIL')
        self.assertEqual({f['severity'] for f in report['findings']},{'MEDIUM'})

    def test_inherited_character_style_overrides_table_unknown_and_direct_none_is_resolved(self):
        styles=f'<w:styles xmlns:w="{W}"><w:style w:type="table" w:styleId="TableU"><w:tblStylePr w:type="firstRow"><w:rPr><w:u w:val="single"/></w:rPr></w:tblStylePr></w:style><w:style w:type="character" w:styleId="Base"><w:rPr><w:u w:val="single"/></w:rPr></w:style><w:style w:type="character" w:styleId="Child"><w:basedOn w:val="Base"/></w:style></w:styles>'
        def mutation(root):
            ET.SubElement(root.find('w:body/w:tbl/w:tblPr',NS),'{'+W+'}tblStyle',{'{'+W+'}val':'TableU'})
            for r in self.cell(root).findall('.//w:r',NS):
                props=r.find('w:rPr',NS);t=''.join(t.text or '' for t in r.findall('w:t',NS))
                ET.SubElement(props,'{'+W+'}rStyle',{'{'+W+'}val':'Child'})
                if t=='五':props.remove(props.find('w:u',NS))
        report=self.inspect(self.mutate(mutation,styles=styles))
        self.assertTrue(report['underline'].startswith('PASS'))

    def test_missing_or_cyclic_style_does_not_falsely_mean_no_underline(self):
        styles=f'<w:styles xmlns:w="{W}"><w:style w:styleId="A"><w:basedOn w:val="B"/></w:style><w:style w:styleId="B"><w:basedOn w:val="A"/></w:style></w:styles>'
        def mutation(root):
            r=next(r for r in self.cell(root).findall('.//w:r',NS) if ''.join(t.text or '' for t in r.findall('w:t',NS))=='五')
            props=r.find('w:rPr',NS);props.remove(props.find('w:u',NS));ET.SubElement(props,'{'+W+'}rStyle',{'{'+W+'}val':'A'})
        report=self.inspect(self.mutate(mutation,styles=styles))
        self.assertEqual(report['underline'],'UNVERIFIED')
        self.assertTrue(any(f['code']=='UNDERLINE_UNVERIFIED' for f in report['findings']))

    def test_header_order_uses_labels_not_wrong_column_assumptions(self):
        def mutation(root):
            for row in root.findall('w:body/w:tbl/w:tr',NS):
                cells=row.findall('w:tc',NS);row.remove(cells[0]);row.insert(list(row).index(cells[1])+1,cells[0])
        report=self.inspect(self.mutate(mutation))
        self.assertTrue(report['content_equality'].startswith('PASS'))
        self.assertEqual(report['findings'][0]['code'],'HEADER_ORDER')
        self.assertEqual(report['findings'][0]['severity'],'MEDIUM')

    def test_multiple_tables_need_selection_and_report_is_scoped(self):
        def mutation(root):root.find('w:body',NS).append(copy.deepcopy(root.find('w:body/w:tbl',NS)))
        raw=self.mutate(mutation)
        with self.assertRaises(ValueError):self.inspect(raw)
        self.assertEqual(quality.inspect(raw,self.source,'REFERENCE',2)['table_index'],2)

    def test_non_native_picture_or_complex_mapping_does_not_claim_editable_complete(self):
        def no_table(root):root.find('w:body',NS).remove(root.find('w:body/w:tbl',NS))
        report=self.inspect(self.mutate(no_table));self.assertEqual(report['native_table'],'FAIL')
        write_docx(self.case,self.docx)
        def nested(root):ET.SubElement(self.cell(root),'{'+W+'}tbl')
        report=self.inspect(self.mutate(nested));self.assertEqual(report['content_equality'],'PARTIAL')
        write_docx(self.case,self.docx)
        def drawn(root):ET.SubElement(self.cell(root).find('w:p/w:r',NS),'{'+W+'}drawing')
        report=self.inspect(self.mutate(drawn));self.assertEqual(report['native_table'],'PARTIAL')

    def test_extra_empty_paragraph_is_low_not_deleted_text(self):
        def mutation(root):ET.SubElement(self.cell(root),'{'+W+'}p')
        report=self.inspect(self.mutate(mutation))
        self.assertTrue(report['content_equality'].startswith('PASS'))
        self.assertEqual(report['findings'][0]['severity'],'LOW')

    def test_unverified_approval_and_missing_reason_retain_limitations(self):
        self.source['rows'][0].update(confirmation_basis='UNVERIFIED',reason=None)
        report=self.inspect()
        self.assertTrue(any('確認依據UNVERIFIED' in l for l in report['limitations']))
        self.assertTrue(any('說明欄' in l for l in report['limitations']))

    def test_new_and_deleted_markers_are_not_underlined_legal_text(self):
        new,old=quality.changed_masks(['第一條　新增規定。'],['（本條新增）'])
        self.assertFalse(new[3]);self.assertFalse(any(old))
        new,old=quality.changed_masks(['（刪除）'],['第一條　舊規定。'])
        self.assertFalse(any(new));self.assertFalse(old[3]);self.assertTrue(old[-1])

    def test_zip_traversal_duplicate_and_doctype_rejected_without_extraction(self):
        for name in ('../escape.txt','/absolute','word\\bad.xml'):
            write_docx(self.case,self.docx)
            self.mutate(lambda r:None,extra={name:b'bad'})
            with self.assertRaises(ValueError):self.inspect()
        write_docx(self.case,self.docx)
        with ZipFile(self.docx,'a') as z:
            import warnings
            with warnings.catch_warnings():
                warnings.simplefilter('ignore');z.writestr('word/document.xml',b'<bad/>')
        with self.assertRaises(ValueError):self.inspect()
        with self.assertRaises(ValueError):quality.parse_xml(b'<!DOCTYPE x [<!ENTITY y "x">]><x>&y;</x>')
        self.assertFalse((self.root/'escape.txt').exists())

    def test_external_relationships_and_embedded_payload_block_renderer(self):
        raw=self.mutate(lambda r:None,extra={'word/_rels/document.xml.rels':b'<Relationships><Relationship TargetMode="External" Target="https://example.invalid"/></Relationships>'})
        self.assertTrue(self.inspect(raw)['renderer_blocked'])
        with patch.object(quality.shutil,'which') as which:
            self.assertEqual(quality.preview(self.docx,self.root/'preview',True)['status'],'NOT TESTED')
            which.assert_not_called()

    def test_write_report_preserves_bytes_and_declared_model_origin_is_not_proof(self):
        original=self.docx.read_bytes()
        evidence=self.root/'evidence.txt';evidence.write_text('SYNTHETIC TEST evidence; not a real platform export')
        result=quality.write_report(self.docx,self.json,'synthetic-only','SYNTHETIC',generation_evidence=evidence,repo=self.root)
        report=json.loads((result/'report.json').read_text())
        self.assertEqual((result/'input.docx').read_bytes(),original)
        self.assertEqual(report['docx'],quality.digest(original))
        self.assertEqual(report['visual_qa'],'NOT TESTED')
        self.assertEqual((result/'generation-evidence.bin').read_bytes(),evidence.read_bytes())
        with self.assertRaises(FileExistsError):quality.write_report(self.docx,self.json,'synthetic-only',repo=self.root)
        report=self.inspect();self.assertIn('UNVERIFIED',quality.markdown(report))

    def test_unsafe_output_and_invalid_source_fail_before_any_report(self):
        for id in ('../bad','/tmp/bad','a/b'):
            with self.assertRaises(ValueError):quality.write_report(self.docx,self.json,id,repo=self.root)
        self.source['rows'][0]['current']=[]
        with self.assertRaises(ValueError):self.inspect()
        target=self.root/'test-output';target.symlink_to(self.root,target_is_directory=True)
        with self.assertRaises(ValueError):quality.write_report(self.docx,self.json,'safe',repo=self.root)
        target.unlink()
        link=self.root/'linked.docx';link.symlink_to(self.docx)
        with self.assertRaises(ValueError):quality.write_report(link,self.json,'safe',repo=self.root)

    def test_renderer_unavailable_and_failure_never_visual_pass(self):
        with patch.object(quality.shutil,'which',return_value=None):
            self.assertEqual(quality.preview(self.docx,self.root/'preview',False)['status'],'NOT TESTED')
        with patch.object(quality.shutil,'which',return_value='/synthetic/soffice'),patch.object(quality.subprocess,'run',side_effect=OSError('synthetic unavailable')):
            self.assertEqual(quality.preview(self.docx,self.root/'preview2',False)['status'],'NOT TESTED')

    def test_renderer_pipeline_uses_shared_preview_without_claiming_visual_qa(self):
        # Only mocked synthetic renderer/PDF interfaces, never a real page inspection.
        from types import SimpleNamespace
        from unittest.mock import MagicMock
        fitz=MagicMock();pdf=MagicMock();page=MagicMock()
        fitz.open.return_value.__enter__.return_value=pdf
        pdf.__iter__.return_value=iter([page]);pdf.__len__.return_value=1
        page.get_fonts.return_value=[(0,0,0,'SYNTHETIC FONT')]
        page.get_pixmap.return_value.save.side_effect=lambda p:Path(p).write_bytes(b'SYNTHETIC MOCK PNG')
        def render(args,**kwargs):
            if '--version' not in args:
                out=Path(args[args.index('--outdir')+1]);(out/(self.docx.stem+'.pdf')).write_bytes(b'SYNTHETIC MOCK PDF')
            return SimpleNamespace(stdout='SYNTHETIC RENDERER',stderr='',returncode=0)
        with patch.object(quality.shutil,'which',return_value='/synthetic/soffice'),patch.object(quality.subprocess,'run',side_effect=render),patch.dict(sys.modules,{'fitz':fitz}):
            report=quality.preview(self.docx,self.root/'mock-preview',False)
        self.assertTrue(report['status'].startswith('PASS'))
        self.assertEqual(report['pdf_pages'],1)
        self.assertEqual(report['preview_pages'],['page-001.png'])
        self.assertEqual(report['visual_qa'],'NOT TESTED')
        self.assertEqual(report['pages_reviewed'],[])

    def test_cli_bad_zip_returns_error_without_traceback(self):
        bad=self.root/'bad.docx';bad.write_bytes(b'not a docx')
        result=subprocess.run([sys.executable,str(ROOT/'scripts/check_model_docx.py'),'--docx',str(bad),'--source',str(self.json),'--run-id','bad'],capture_output=True,text=True)
        self.assertNotEqual(result.returncode,0);self.assertNotIn('Traceback',result.stderr)


if __name__=='__main__':unittest.main()
