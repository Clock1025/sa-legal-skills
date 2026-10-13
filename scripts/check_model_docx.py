#!/usr/bin/env python3
"""比對提供的DOCX與核對基準，產生離線風險報告；不證明模型／法律或人工視覺驗收。"""
import argparse
from difflib import SequenceMatcher
import hashlib
import importlib.util
import json
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from zipfile import BadZipFile, ZipFile

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('reference', ROOT / 'tests/docx_reference.py')
reference = importlib.util.module_from_spec(spec); spec.loader.exec_module(reference)
W, NS, HEADERS, masks = reference.W, reference.NS, reference.HEADERS, reference.masks
MAX_BYTES = 64 * 1024 * 1024


def require(ok, message):
    if not ok: raise ValueError(message)


def digest(content):
    return {'sha256': hashlib.sha256(content).hexdigest(), 'byte_size': len(content)}


def parse_xml(content):
    require(len(content) <= 16 * 1024 * 1024, 'XML 超過安全大小上限')
    require(b'<!DOCTYPE' not in content.upper() and b'<!ENTITY' not in content.upper(), '不接受DTD／ENTITY')
    root = ET.fromstring(content)
    strict = 'http://purl.oclc.org/ooxml/wordprocessingml/main'
    for node in root.iter():
        node.tag = node.tag.replace('{'+strict+'}', '{'+W+'}')
        node.attrib = {k.replace('{'+strict+'}', '{'+W+'}'):v for k,v in node.attrib.items()}
    return root


def package(content):
    import io
    with ZipFile(io.BytesIO(content)) as z:
        infos = z.infolist()
        require(len(infos) <= 5000 and sum(i.file_size for i in infos) <= MAX_BYTES, 'DOCX解壓大小或成員數超過上限')
        names = [i.filename for i in infos]
        require(len(names) == len(set(names)), 'ZIP含重複成員')
        for name in names:
            path = PurePosixPath(name.rstrip('/'))
            require(not path.is_absolute() and '..' not in path.parts and '\\' not in name and ':' not in name, 'ZIP含不安全路徑')
        require(z.testzip() is None, 'ZIP CRC錯誤')
        require('word/document.xml' in names and '[Content_Types].xml' in names, '缺DOCX必要成員')
        types = parse_xml(z.read('[Content_Types].xml'))
        document = parse_xml(z.read('word/document.xml'))
        styles = parse_xml(z.read('word/styles.xml')) if 'word/styles.xml' in names else None
        settings = parse_xml(z.read('word/settings.xml')) if 'word/settings.xml' in names else None
        blocked = any('vbaproject' in n.lower() or n.lower().startswith('word/embeddings/') for n in names)
        blocked = blocked or any('macroenabled' in n.get('ContentType','').lower() or 'vbaproject' in n.get('ContentType','').lower() for n in types)
        for name in names:
            if name.endswith('.rels'):
                rels = parse_xml(z.read(name))
                blocked = blocked or any(r.get('TargetMode') == 'External' or r.get('Type','').lower().endswith('/vbaproject') for r in rels)
        blocked = blocked or document.find('.//w:altChunk', NS) is not None
    return document, styles, settings, blocked


def validate_source(source):
    require(isinstance(source,dict) and isinstance(source.get('source'),dict), 'source必須是JSON物件，含來源欄位')
    require(source.get('schema_version') == '1.0', '不支援source schema')
    require(all(isinstance(source.get('source', {}).get(k),str) and source['source'][k] for k in ('name','version','location')), '需來源名稱／版本／位置；未知明記UNVERIFIED')
    require(isinstance(source.get('rows'), list) and source['rows'], '需逐列原文及確認修正文')
    ids = set()
    for row in source['rows']:
        require(isinstance(row,dict), '每列須為JSON物件')
        require(isinstance(row.get('id'), str) and row['id'] and row['id'] not in ids, '列ID缺漏或重複')
        ids.add(row['id'])
        require(all(isinstance(row.get(k),str) and row[k] for k in ('source_anchor','confirmation_basis')), '需列來源anchor及確認依據；未知明記UNVERIFIED')
        for key in ('current','amended'):
            require(isinstance(row.get(key), list) and row[key] and all(isinstance(p,str) and p for p in row[key]), 'current/amended需完整段落字串陣列')
        require(row.get('reason') is None or (isinstance(row['reason'],list) and row['reason'] and all(isinstance(p,str) and p for p in row['reason'])), 'reason需段落陣列或null（未核對）')


def underline_value(props):
    if props is None: return 'INHERIT'
    u = props.find('w:u', NS)
    return u.get('{'+W+'}val', 'single') if u is not None else 'INHERIT'


class Underline:
    """Resolve doc defaults, paragraph/character styles, and direct overrides; unknown remains unknown."""
    def __init__(self, styles):
        self.styles = {} if styles is None else {s.get('{'+W+'}styleId'):s for s in styles.findall('w:style',NS)}
        self.default = 'none' if styles is None else underline_value(styles.find('w:docDefaults/w:rPrDefault/w:rPr',NS))
        if self.default == 'INHERIT': self.default = 'none'
        self.paragraph_default = next((id for id,s in self.styles.items() if s.get('{'+W+'}type')=='paragraph' and s.get('{'+W+'}default')=='1'), None)

    def style(self, id, trail=()):
        if not id: return 'INHERIT'
        if id in trail or id not in self.styles: return None
        node = self.styles[id]
        value = underline_value(node.find('w:rPr',NS))
        if value != 'INHERIT': return value
        parent = node.find('w:basedOn',NS)
        return self.style(parent.get('{'+W+'}val'), trail+(id,)) if parent is not None else 'INHERIT'

    def run(self, p, r, table_style):
        value = self.default
        for id in (table_style, self.paragraph_default):
            v = self.style(id)
            if v != 'INHERIT': value = v
            ts = self.styles.get(id) if id == table_style else None
            if ts is not None and ts.find('.//w:tblStylePr//w:u',NS) is not None:
                value = None  # Unknown conditional table state; higher styles/direct values can override.
        sid = p.find('w:pPr/w:pStyle',NS)
        if sid is not None:
            v = self.style(sid.get('{'+W+'}val'))
            if v != 'INHERIT': value = v
        rs = r.find('w:rPr/w:rStyle',NS)
        if rs is not None:
            v = self.style(rs.get('{'+W+'}val'))
            if v != 'INHERIT': value = v
        direct = underline_value(r.find('w:rPr',NS))
        if direct != 'INHERIT': value = direct
        return value


def cell_data(cell, underline, table_style):
    paragraphs, flags = [], []
    for p in cell.findall('w:p',NS):
        text, mask = '', []
        for run in p.iter('{'+W+'}r'):
            style = underline.run(p, run, table_style)
            value = ''
            for n in run.iter():
                if n.tag == '{'+W+'}t': value += n.text or ''
                elif n.tag == '{'+W+'}tab': value += '\t'
                elif n.tag in ('{'+W+'}br','{'+W+'}cr'): value += '\n'
            text += value
            mask.extend([None if style is None else (style != 'none' and (style != 'words' or not ch.isspace())) for ch in value])
        paragraphs.append(text); flags.extend(mask+[False])
    return paragraphs, flags[:-1]


def changed_masks(new, old):
    n, o = '\n'.join(new), '\n'.join(old)
    if old == ['（本條新增）']: return [not c.isspace() for c in n], [False]*len(o)
    if new == ['（刪除）']: return [False]*len(n), [not c.isspace() for c in o]
    return masks([{'text':p} for p in new], [{'text':p} for p in old])


def text_changes(new, old):
    n, o = '\n'.join(new), '\n'.join(old)
    return [dict(old=o[a:b], new=n[c:d]) for tag,a,b,c,d in SequenceMatcher(None,o,n,autojunk=False).get_opcodes() if tag!='equal']


def inspect(content, source, origin='UNVERIFIED', table_index=None):
    validate_source(source)
    require(origin in ('MODEL_OUTPUT','REFERENCE','SYNTHETIC','UNVERIFIED'), '未知產物來源分類')
    document, styles, settings, blocked = package(content)
    result = dict(schema_version='1.0', supplied_origin=origin, model_origin='UNVERIFIED（需人工核對生成鏈）',
                  docx=digest(content), source=source['source'], native_table='NOT TESTED',
                  content_equality='NOT TESTED', underline='NOT TESTED', findings=[], observations=[],
                  rendering={'status':'NOT TESTED'}, visual_qa='NOT TESTED', pages_reviewed=[],
                  renderer_blocked=blocked,
                  limitations=['只比對提供的核對基準，不證明來源效力、確認真實性或法律正確性',
                               '只核對所選表格，文件其他提案／附件、版面、字型與所有OOXML特性未全面驗證'])
    def finding(code, severity, anchor, detail):
        result['findings'].append(dict(code=code, severity=severity, anchor=anchor, detail=detail))
    if any(row['confirmation_basis']=='UNVERIFIED' for row in source['rows']):
        result['limitations'].append('有修正確認依據UNVERIFIED；文字匹配不代表已獲授權')
    if document.find('.//w:ins',NS) is not None or document.find('.//w:del',NS) is not None or document.find('.//w:moveFrom',NS) is not None or document.find('.//w:moveTo',NS) is not None:
        finding('TRACKED_CHANGES','HIGH','word/document.xml','有未決追蹤修訂，需人工確定要比較的版本；未自動接受或拒絕')
    tables = document.findall('w:body/w:tbl',NS)
    underline = Underline(styles)
    candidates = []
    for index, table in enumerate(tables,1):
        for ri, row in enumerate(table.findall('w:tr',NS)):
            cells = row.findall('w:tc',NS)
            headers = [''.join(cell_data(c,underline,None)[0]).strip() for c in cells]
            if len(headers)==3 and set(headers)==set(HEADERS):
                candidates.append((index,table,ri,headers)); break
    if table_index is not None:
        require(table_index>0, 'table需正整數')
        candidates = [c for c in candidates if c[0]==table_index]
    if not candidates:
        result['native_table']='FAIL'
        finding('NO_COMPARISON_TABLE','HIGH','word/document.xml','未找到有三個可辨識欄名的原生比較表；圖片／未知欄名需人工檢查，不用OCR重建')
        result['content_equality']='NOT TESTED'; return result
    require(len(candidates)==1, '有多個比較表，請用--table指定文件中第幾張表，不自動混合不同法規')
    ti, table, header_row, headers = candidates[0]
    result['table_index']=ti; result['native_table']='PASS（原生文字結構，非Word編輯實測）'
    if headers != list(HEADERS): finding('HEADER_ORDER','MEDIUM',f'table {ti}','欄位順序與規範不同；依實際欄名比對內容，不直接當錯欄')
    protection = None if settings is None else settings.find('w:documentProtection',NS)
    if protection is not None and protection.get('{'+W+'}enforcement') not in (None,'0','false','off'):
        result['native_table']='PARTIAL'; finding('PROTECTED_DOCUMENT','MEDIUM','word/settings.xml','文件有編輯保護；不宣稱可直接編輯')
    ts = table.find('w:tblPr/w:tblStyle',NS); table_style = ts.get('{'+W+'}val') if ts is not None else None
    rows = []
    for ri, row in enumerate(table.findall('w:tr',NS)[header_row+1:],header_row+2):
        cells = row.findall('w:tc',NS)
        if [''.join(cell_data(c,underline,table_style)[0]).strip() for c in cells] == headers: continue
        rows.append((ri,cells))
    if len(rows)!=len(source['rows']): finding('ROW_COUNT','HIGH',f'table {ti}',f'基準{len(source["rows"])}列，實際{len(rows)}列；可能漏列／重複，需人工核對')
    for (ri,cells), expected in zip(rows,source['rows']):
        anchor=f'word/document.xml table {ti} row {ri} / {expected["id"]}'
        if len(cells)!=3 or any(c.find('.//w:vMerge',NS) is not None or (c.find('.//w:gridSpan',NS) is not None and c.find('.//w:gridSpan',NS).get('{'+W+'}val')!='1') or c.find('w:tbl',NS) is not None for c in cells):
            finding('COMPLEX_CELL_MAPPING','HIGH',anchor,'合併／巢狀／非三欄結構未自動映射；不猜補條文'); continue
        observed = [cell_data(cells[headers.index(h)],underline,table_style) for h in HEADERS]
        if any(c.find('.//w:drawing',NS) is not None or c.find('.//w:object',NS) is not None for c in cells):
            finding('NON_TEXT_CONTENT','HIGH',anchor,'含圖片／物件，原生文字不能證明圖中條文完整或可編輯')
            result['native_table']='PARTIAL'
        row_result=dict(id=expected['id'], anchor=anchor, paragraphs={key:data[0] for key,data in zip(('amended','current','reason'),observed)},
                        observed_text_changes=text_changes(observed[0][0],observed[1][0]))
        result['observations'].append(row_result)
        for column,key in enumerate(('amended','current','reason')):
            paragraphs=observed[column][0]; target=expected.get(key)
            if target is None:
                result['limitations'].append(expected['id']+'：說明欄無核對基準，未判定實質理由'); continue
            if paragraphs!=target:
                if [p for p in paragraphs if p] == target:
                    finding('EMPTY_PARAGRAPH','LOW',anchor+' '+key,'多餘空段落，非漏字；原文非空段落仍相同')
                else:
                    finding('TEXT_OR_PARAGRAPH_DIFFERENCE','HIGH',anchor+' '+key,
                            '與提供基準有文字或段落結構差異；可能漏字、重複、錯欄或未授權修改，不自動斷定法律效果')
        new_mask, old_mask = changed_masks(observed[0][0],observed[1][0])
        for column, expected_mask in enumerate((new_mask,old_mask)):
            actual_mask=observed[column][1]; label=('amended','current')[column]
            unknown=sum(v is None for v in actual_mask)
            if unknown: finding('UNDERLINE_UNVERIFIED','MEDIUM',anchor+' '+label,f'{unknown}字的樣式底線無法解析，不當未畫底線或PASS')
            extra=[i for i,(a,e) in enumerate(zip(actual_mask,expected_mask)) if a is True and not e]
            missing=[i for i,(a,e) in enumerate(zip(actual_mask,expected_mask)) if a is False and e]
            if extra: finding('EXTRA_UNDERLINE','LOW',anchor+' '+label,f'未變動／空白字元多畫底線：{len(extra)}字；前20位置（0-based）{extra[:20]}，不等同內容錯誤')
            if missing: finding('MISSING_UNDERLINE','MEDIUM',anchor+' '+label,f'實際變動字元缺底線：{len(missing)}字；前20位置{missing[:20]}，內容一致性另列')
    codes={f['code'] for f in result['findings']}
    content_codes={'ROW_COUNT','TEXT_OR_PARAGRAPH_DIFFERENCE'}
    result['content_equality']='FAIL' if codes&content_codes else ('PARTIAL' if codes&{'TRACKED_CHANGES','NON_TEXT_CONTENT','COMPLEX_CELL_MAPPING'} else 'PASS（限提供的段落基準）')
    result['underline']='FAIL' if codes&{'EXTRA_UNDERLINE','MISSING_UNDERLINE'} else ('UNVERIFIED' if codes&{'UNDERLINE_UNVERIFIED','ROW_COUNT','COMPLEX_CELL_MAPPING','TRACKED_CHANGES','NON_TEXT_CONTENT'} else 'PASS（限可解析格式及實際文字diff）')
    return result


def preview(docx, directory, blocked):
    if blocked: return dict(status='NOT TESTED', limitation='含外部連結／嵌入物件／altChunk，安全起見不啟動renderer；非法律內容判定')
    executable=shutil.which('soffice')
    if not executable: return dict(status='NOT TESTED', limitation='未安裝soffice')
    directory.mkdir()
    profile=directory/'profile'; profile.mkdir()
    (profile/'registrymodifications.xcu').write_text('<?xml version="1.0"?><oor:items xmlns:oor="http://openoffice.org/2001/registry"><item oor:path="/org.openoffice.Office.Common/Security/Scripting"><prop oor:name="MacroSecurityLevel" oor:op="fuse"><value>3</value></prop></item></oor:items>',encoding='utf-8')
    try:
        version=subprocess.run([executable,'--version'],capture_output=True,text=True,check=True,timeout=10).stdout.strip()
        done=subprocess.run([executable,'-env:UserInstallation='+profile.resolve().as_uri(),'--headless','--convert-to','pdf:writer_pdf_Export','--outdir',str(directory),str(docx.resolve())],capture_output=True,text=True,timeout=60)
        (directory/'renderer.log').write_text(done.stdout+'\n'+done.stderr,encoding='utf-8')
        pdf=directory/(docx.stem+'.pdf')
        require(done.returncode==0 and pdf.is_file(), 'renderer未產生PDF')
        spec=importlib.util.spec_from_file_location('pdf_preview',ROOT/'tests/docx_pdf_probe.py')
        module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
        return dict(status='PASS（僅產生PDF／預覽）',renderer=version,**module.preview_pdf(pdf,directory))
    except (OSError,ValueError,ImportError,subprocess.SubprocessError) as error:
        return dict(status='PARTIAL' if (directory/(docx.stem+'.pdf')).is_file() else 'NOT TESTED',limitation=str(error))


def markdown(report):
    def escape(text): return re.sub(r'([\\`*_{}\[\]()#+.!|<>])',r'\\\1',str(text).replace('\n',' '))
    lines=['# DOCX 品質報告','',f'產物來源宣告：{report["supplied_origin"]}；模型來源：UNVERIFIED。',
           f'內容：{report["content_equality"]}；底線：{report["underline"]}；原生表格：{report["native_table"]}。',
           'VISUAL QA: NOT TESTED；此報告不證明法律正確性。','', '| 風險 | 項目／位置 | 發現 |','| --- | --- | --- |']
    for f in report['findings']: lines.append('| '+' | '.join(escape(v) for v in (f['severity'],f['code']+' / '+f['anchor'],f['detail']))+' |')
    lines+=['','需人工：核對生成鏈、原始來源／確認依據、差異法意、字型／段落有效格式及實際頁面；不要把格式FAIL升格為法律內容錯誤。','']
    lines+=['- '+escape(l) for l in report['limitations']]
    lines+=['',f'渲染：{escape(report["rendering"])}；PDF／PNG若存在僅供預覽，沒有人工看頁判定。']
    return '\n'.join(lines)+'\n'


def write_report(docx, source_path, run_id, origin='UNVERIFIED', table_index=None, render=False, generation_evidence=None, repo=ROOT):
    require(re.fullmatch(r'[A-Za-z0-9_-]+',run_id) is not None,'run-id不安全')
    for path in (Path(docx),Path(source_path)):
        require(path.is_file() and not path.is_symlink() and path.stat().st_size<=MAX_BYTES,'輸入必須是限大小實檔，不接受symlink')
    content=Path(docx).read_bytes(); raw=Path(source_path).read_bytes()
    source=json.loads(raw.decode('utf-8-sig'))
    report=inspect(content,source,origin,table_index)
    evidence=None
    if generation_evidence:
        p=Path(generation_evidence)
        require(p.is_file() and not p.is_symlink() and p.stat().st_size<=MAX_BYTES,'生成證據必須是實際限大小檔案')
        evidence=p.read_bytes()
    base=Path(repo).resolve()
    for name in ('test-output','model-docx-quality'):
        base=base/name; require(not base.is_symlink(),'輸出父路徑不能是symlink'); base.mkdir(exist_ok=True)
    folder=base/run_id; require(not folder.is_symlink(),'輸出不能是symlink'); folder.mkdir()
    try:
        (folder/'input.docx').write_bytes(content); (folder/'source.json').write_bytes(raw)
        report['source_manifest']=digest(raw)
        report['generation_evidence']=digest(evidence) if evidence is not None else None
        if evidence is not None: (folder/'generation-evidence.bin').write_bytes(evidence)
        if render: report['rendering']=preview(folder/'input.docx',folder/'preview',report['renderer_blocked'])
        (folder/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        (folder/'report.md').write_text(markdown(report),encoding='utf-8')
    except BaseException:
        shutil.rmtree(folder); raise
    return folder


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--docx',type=Path,required=True); parser.add_argument('--source',type=Path,required=True)
    parser.add_argument('--run-id',required=True); parser.add_argument('--table',type=int)
    parser.add_argument('--origin',choices=('MODEL_OUTPUT','REFERENCE','SYNTHETIC','UNVERIFIED'),default='UNVERIFIED')
    parser.add_argument('--generation-evidence',type=Path); parser.add_argument('--render',action='store_true')
    args=parser.parse_args()
    try:
        print(write_report(args.docx,args.source,args.run_id,args.origin,args.table,args.render,args.generation_evidence))
    except (ValueError,OSError,KeyError,TypeError,ET.ParseError,BadZipFile,RuntimeError) as error:
        print('FAIL: '+str(error),file=sys.stderr); return 1
    return 0  # Report findings are not an automatic release gate or model verdict.


if __name__=='__main__': sys.exit(main())
