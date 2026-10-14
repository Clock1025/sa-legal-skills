"""Executable stdlib OOXML reference tests, not Word/PDF or model behavior tests."""
import copy
from pathlib import Path
import tempfile
import unittest
import xml.etree.ElementTree as ET
from zipfile import ZIP_DEFLATED, ZipFile

from docx_reference import NS, W, check_docx, expand_row, load_cases, write_docx


class DocxQualityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.fixture = load_cases()
        self.short = self.fixture['cases'][0]

    def mutate(self, case, change):
        path = write_docx(case,self.root/'negative.docx')
        with ZipFile(path) as z:
            contents = {name:z.read(name) for name in z.namelist()}
        root = ET.fromstring(contents['word/document.xml'])
        change(root)
        contents['word/document.xml'] = ET.tostring(root,encoding='utf-8',xml_declaration=True)
        with ZipFile(path,'w',ZIP_DEFLATED) as z:
            for name,data in contents.items():
                z.writestr(name,data)
        return path

    def cell(self,root,col=0):
        return root.findall('w:body/w:tbl/w:tr',NS)[1].findall('w:tc',NS)[col]

    def test_six_real_docx_cases_round_trip_and_exact_sources(self):
        self.assertEqual(len(self.fixture['cases']),6)
        self.assertEqual(self.fixture['kind'],'FICTIONAL_REFERENCE_FIXTURES')
        for case in self.fixture['cases']:
            with self.subTest(case=case['id']):
                path = write_docx(case,self.root/(case['id']+'.docx'))
                with ZipFile(path) as z:
                    self.assertIsNone(z.testzip())
                    self.assertIn('[Content_Types].xml',z.namelist())
                    document = ET.fromstring(z.read('word/document.xml'))
                rows = document.findall('w:body/w:tbl/w:tr',NS)[1:]
                for tr,original in zip(rows,case['rows']):
                    for cell,expected in zip(tr.findall('w:tc',NS),expand_row(original)):
                        self.assertEqual([''.join(p.itertext()) for p in cell.findall('w:p',NS)],
                                         [p['text'] for p in expected])
                self.assertEqual(check_docx(case,path)['visual_qa'],'NOT TESTED')

    def test_short_diff_underlines_only_changed_five_and_seven(self):
        path=write_docx(self.short,self.root/'short.docx')
        with ZipFile(path) as z:
            root=ET.fromstring(z.read('word/document.xml'))
        for col,expected in ((0,'五'),(1,'七'),(2,'')):
            spans=[]
            for run in self.cell(root,col).findall('.//w:r',NS):
                if run.find('w:rPr/w:u',NS).get('{'+W+'}val')=='single':
                    spans.append(''.join(run.itertext()))
            self.assertEqual(''.join(spans),expected)

    def test_long_cases_have_pressure_and_asymmetric_case_preserves_old_text(self):
        for index in (1,2,4,5):
            case=self.fixture['cases'][index]
            length=max(sum(len(p['text']) for row in case['rows'] for p in expand_row(row)[col]) for col in range(3))
            self.assertGreater(length,1500)
        new,old,_=expand_row(self.fixture['cases'][4]['rows'][0])
        self.assertEqual(len(old),1)
        self.assertEqual(old[0]['text'],'第七條\u3000應於會議七日前公告。')
        self.assertGreater(len(new[1]['text']),1500)

    def test_multilevel_paragraphs_and_source_typo_preserved(self):
        hierarchy=expand_row(self.fixture['cases'][3]['rows'][0])[1]
        self.assertEqual([p['level'] for p in hierarchy],['article','paragraph','item','subitem','item'])
        self.assertEqual(hierarchy[2]['text'].count('一、'),1)
        self.assertEqual(hierarchy[3]['text'].count('（一）'),1)
        original=expand_row(self.fixture['cases'][2]['rows'][0])[1][0]['text']
        self.assertIn('应',original) # Intentional source glyph; no normalization of quoted/current text.

    def test_changed_truncated_duplicated_or_swapped_text_rejected(self):
        for defect in ('changed','truncated','duplicated','swap'):
            def change(root):
                cell=self.cell(root,1)
                t=cell.find('.//w:t',NS)
                if defect=='changed':
                    target=next(t for t in cell.findall('.//w:t',NS) if '七' in (t.text or ''))
                    target.text=target.text.replace('七','五')
                elif defect=='truncated': t.text=t.text[:-1]
                elif defect=='duplicated': cell.append(copy.deepcopy(cell.find('w:p',NS)))
                else:
                    row=root.findall('w:body/w:tbl/w:tr',NS)[1]
                    cells=row.findall('w:tc',NS)
                    row.remove(cells[0]); row.insert(2,cells[0])
            with self.subTest(defect=defect),self.assertRaises(ValueError):
                check_docx(self.short,self.mutate(self.short,change))

    def test_repeat_header_split_height_and_keep_chain_negative_controls(self):
        for defect in ('header','cantSplit','height','keepNext','keepLines','pageBreakBefore'):
            def change(root):
                table=root.find('w:body/w:tbl',NS)
                if defect=='header':
                    table.find('w:tr/w:trPr/w:tblHeader',NS).set('{'+W+'}val','0')
                elif defect=='cantSplit':
                    table.findall('w:tr',NS)[1].find('w:trPr/w:cantSplit',NS).set('{'+W+'}val','1')
                elif defect=='height':
                    ET.SubElement(table.findall('w:tr',NS)[1].find('w:trPr',NS),'{'+W+'}trHeight',{'{'+W+'}val':'200','{'+W+'}hRule':'exact'})
                else:
                    self.cell(root).find('w:p/w:pPr/w:'+defect,NS).set('{'+W+'}val','1')
            with self.subTest(defect=defect),self.assertRaises(ValueError):
                check_docx(self.short,self.mutate(self.short,change))

    def test_underlined_whitespace_unchanged_text_bad_indent_font_spacing_border_rejected(self):
        for defect in ('whitespace','unchanged','indent','font','spacing','border','grid','cellwidth','alignment'):
            def change(root):
                p=self.cell(root).find('w:p',NS)
                if defect in ('whitespace','unchanged'):
                    if defect=='whitespace':
                        p.find('w:r/w:rPr/w:u',NS).set('{'+W+'}val','single')
                    if defect=='unchanged':
                        for run in p.findall('w:r',NS):
                            if not any(ch.isspace() for ch in ''.join(run.itertext())):
                                run.find('w:rPr/w:u',NS).set('{'+W+'}val','single')
                elif defect=='indent': p.find('w:pPr/w:ind',NS).set('{'+W+'}firstLine','240')
                elif defect=='font': p.find('w:r/w:rPr/w:rFonts',NS).attrib.pop('{'+W+'}eastAsia')
                elif defect=='spacing': p.find('w:pPr/w:spacing',NS).set('{'+W+'}line','360')
                elif defect=='border': root.find('w:body/w:tbl/w:tblPr/w:tblBorders/w:top',NS).set('{'+W+'}color','808080')
                elif defect=='grid': root.find('w:body/w:tbl/w:tblGrid/w:gridCol',NS).set('{'+W+'}w','1000')
                elif defect=='cellwidth': self.cell(root).find('w:tcPr/w:tcW',NS).set('{'+W+'}w','1000')
                else: self.cell(root).find('w:tcPr/w:vAlign',NS).set('{'+W+'}val','center')
            with self.subTest(defect=defect),self.assertRaises(ValueError):
                check_docx(self.short,self.mutate(self.short,change))

    def test_skill_a4_portrait_default_and_exceptions_static_only(self):
        """Guard the written contract; this is not model or visual validation."""
        text=(Path(__file__).resolve().parents[1]/'skills/amendment-drafting/SKILL.md').read_text()
        for literal in ('正式法規文件及修正條文對照表預設採 **A4 直式（portrait）**',
                        '不得僅因條文過長、三欄內容長度差異或減少頁數而自行改為橫式',
                        '應依既有長表格分頁規則處理',
                        '使用者明確指定其他方向',
                        '已提供具權威性的正式文件範本另有要求',
                        '以使用者要求或該正式範本為準'):
            with self.subTest(clause=literal):
                self.assertIn(literal,text)

    def test_skill_pagination_and_validation_limit_clauses_static_only(self):
        text=(Path(__file__).resolve().parents[1]/'skills/amendment-drafting/SKILL.md').read_text()
        for literal in ('w:tblHeader','w:cantSplit','keepNext','keepLines','exact','VISUAL QA: NOT TESTED',
                        '長短差異造成的空白欄不代表內容遺失','不能拿靜態規則或 CI PASS 冒充版面驗證'):
            self.assertIn(literal,text)


if __name__=='__main__':
    unittest.main()
