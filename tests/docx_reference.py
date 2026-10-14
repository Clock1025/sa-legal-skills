"""Small stdlib OOXML reference fixtures, NOT a production DOCX/legal drafting engine."""
from difflib import SequenceMatcher
import json
from pathlib import Path
import xml.etree.ElementTree as ET
from zipfile import ZIP_DEFLATED, ZipFile

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
NS = {'w': W}
ET.register_namespace('w', W)
HEADERS = ('修正條文', '現行條文', '說明')
WIDTHS = ('3600','3600','2886')
INDENTS = {'article': {'left':'240', 'hanging':'240'}, 'paragraph': {'left':'240', 'firstLine':'240'},
           'item': {'left':'480', 'hanging':'240'}, 'subitem': {'left':'720', 'hanging':'240'}, 'reason': {'left':'0'}}
FIXTURE = Path(__file__).parent / 'fixtures/docx/cases.json'


def node(parent, name, attrs=None, text=None):
    element = ET.SubElement(parent, '{'+W+'}'+name, {'{'+W+'}'+k:v for k,v in (attrs or {}).items()})
    element.text = text
    return element


def load_cases():
    return json.loads(FIXTURE.read_text())


def expand_row(row):
    old, new = [], []
    for p in row['paragraphs']:
        for dest, days in ((old, '七'), (new, '五')):
            seed = p['text'].replace('{days}', days)
            if p['level'] in ('item', 'subitem'):
                prefix = seed.index('、')+1 if p['level']=='item' else seed.index('）')+1
                text = seed + seed[prefix:] * (p['repeat']-1)
            else:
                text = seed * p['repeat']
            if p['level'] == 'article':
                text = row['article'] + '\u3000' + text
            dest.append({'level':p['level'], 'text':text})
    if 'added_paragraph' in row:
        p = row['added_paragraph']
        new.append({'level':p['level'], 'text':p['text'] * p['repeat']})
    return new, old, [{'level':'reason', 'text':row['reason'] * row.get('reason_repeat',1)}]


def masks(new, old):
    # Explicit fixture contract: changed characters only, never whitespace.
    ntext, otext = '\n'.join(p['text'] for p in new), '\n'.join(p['text'] for p in old)
    nmask, omask = [False]*len(ntext), [False]*len(otext)
    for tag, a, b, c, d in SequenceMatcher(None, ntext, otext, autojunk=False).get_opcodes():
        if tag != 'equal':
            nmask[a:b] = [not ch.isspace() for ch in ntext[a:b]]
            omask[c:d] = [not ch.isspace() for ch in otext[c:d]]
    return nmask, omask


def paragraph(cell, entry, mask, font):
    p = node(cell, 'p')
    props = node(p, 'pPr')
    node(props, 'spacing', {'before':'0','after':'0','line':'240','lineRule':'auto'})
    node(props, 'ind', INDENTS[entry['level']])
    node(props, 'jc', {'val':'left'})
    for flag in ('keepNext', 'keepLines', 'pageBreakBefore'):
        node(props, flag, {'val':'0'})
    text = entry['text']
    start = 0
    while start < len(text):
        end = start+1
        while end < len(text) and mask[end] == mask[start]:
            end += 1
        run = node(p, 'r')
        rpr = node(run, 'rPr')
        node(rpr, 'rFonts', {'ascii':font,'hAnsi':font,'eastAsia':font,'cs':font})
        node(rpr, 'sz', {'val':'24'})
        node(rpr, 'szCs', {'val':'24'})
        node(rpr, 'u', {'val':'single' if mask[start] else 'none'})
        t = node(run, 't', text=text[start:end])
        t.set('{http://www.w3.org/XML/1998/namespace}space','preserve')
        start = end
    return p


def make_document(case, font):
    doc = ET.Element('{'+W+'}document')
    body = node(doc,'body')
    title = case['id']+' 虛構 DOCX 回歸測試（非現行法規）'
    paragraph(body, {'level':'reason','text':title}, [False]*len(title),font)
    table = node(body,'tbl')
    pr = node(table,'tblPr')
    node(pr,'tblW',{'w':'10086','type':'dxa'})
    node(pr,'tblLayout',{'type':'fixed'})
    borders = node(pr,'tblBorders')
    for side in ('top','left','bottom','right','insideH','insideV'):
        node(borders,side,{'val':'single','sz':'4','color':'000000'})
    grid = node(table,'tblGrid')
    widths = WIDTHS
    for width in widths:
        node(grid,'gridCol',{'w':width})
    header = node(table,'tr')
    hpr = node(header,'trPr')
    node(hpr,'tblHeader',{'val':'1'})
    node(hpr,'cantSplit',{'val':'1'})
    for title,width in zip(HEADERS,widths):
        cell = node(header,'tc')
        node(node(cell,'tcPr'),'tcW',{'w':width,'type':'dxa'})
        paragraph(cell,{'level':'reason','text':title},[False]*len(title),font)
    for row in case['rows']:
        tr = node(table,'tr')
        node(node(tr,'trPr'),'cantSplit',{'val':'0'})
        columns = expand_row(row)
        nmask,omask = masks(columns[0],columns[1])
        for entries,width,mask in zip(columns,widths,(nmask,omask,[False]*len(columns[2][0]['text']))):
            cell = node(tr,'tc')
            cpr = node(cell,'tcPr')
            node(cpr,'tcW',{'w':width,'type':'dxa'})
            node(cpr,'vAlign',{'val':'top'})
            offset = 0
            for entry in entries:
                paragraph(cell,entry,mask[offset:offset+len(entry['text'])],font)
                offset += len(entry['text'])+1
    section = node(body,'sectPr')
    node(section,'pgSz',{'w':'11906','h':'16838'})
    node(section,'pgMar',{'top':'850','right':'910','bottom':'850','left':'910','header':'400','footer':'400','gutter':'0'})
    return doc


def write_docx(case, path, font='Noto Serif CJK TC'):
    path = Path(path)
    path.parent.mkdir(parents=True,exist_ok=True)
    doc = make_document(case,font)
    contents = {
      '[Content_Types].xml': b'''<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/></Types>''',
      '_rels/.rels': b'''<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>''',
      'word/document.xml':ET.tostring(doc,encoding='utf-8',xml_declaration=True),
    }
    with ZipFile(path,'w',ZIP_DEFLATED) as z:
        for name,content in contents.items():
            z.writestr(name,content)
    check_docx(case,path,font)
    return path


def check_docx(case,path,font='Noto Serif CJK TC'):
    """Direct-format reference contract only; not universal OOXML/style/visual validation."""
    def require(ok,message):
        if not ok:
            raise ValueError(message)
    with ZipFile(path) as z:
        require(z.testzip() is None,'ZIP integrity')
        root = ET.fromstring(z.read('word/document.xml'))
    table = root.find('w:body/w:tbl',NS)
    require(table is not None,'native table missing')
    require(table.find('w:tblPr/w:tblLayout',NS).get('{'+W+'}type')=='fixed','fixed layout missing')
    borders = table.findall('w:tblPr/w:tblBorders/*',NS)
    require(len(borders)==6 and all(e.get('{'+W+'}color')=='000000' for e in borders),'border color')
    require(tuple(e.get('{'+W+'}w') for e in table.findall('w:tblGrid/w:gridCol',NS))==WIDTHS,'column grid mismatch')
    rows = table.findall('w:tr',NS)
    require(len(rows)==len(case['rows'])+1,'missing/duplicate row')
    flag = rows[0].find('w:trPr/w:tblHeader',NS)
    require(flag is not None and flag.get('{'+W+'}val')=='1','repeat header missing')
    def text(p):
        return ''.join(p.itertext()) # OOXML fixture has only text in w:t; no indentation text nodes.
    require(tuple(text(c) for c in rows[0].findall('w:tc',NS))==HEADERS,'header column order')
    for tr,row in zip(rows[1:],case['rows']):
        split = tr.find('w:trPr/w:cantSplit',NS)
        require(split is not None and split.get('{'+W+'}val')=='0','body row must allow split')
        require(tr.find('w:trPr/w:trHeight',NS) is None,'fixed row height forbidden')
        cells = tr.findall('w:tc',NS)
        require(len(cells)==3,'three-column association broken')
        expected = expand_row(row)
        nm,om = masks(expected[0],expected[1])
        for cell,entries,mask,width in zip(cells,expected,(nm,om,[False]*len(expected[2][0]['text'])),WIDTHS):
            require(cell.find('w:tcPr/w:tcW',NS).get('{'+W+'}w')==width,'cell width mismatch')
            require(cell.find('w:tcPr/w:vAlign',NS).get('{'+W+'}val')=='top','cell alignment')
            paragraphs = cell.findall('w:p',NS)
            require(len(paragraphs)==len(entries),'paragraph structure lost')
            offset = 0
            for p,entry in zip(paragraphs,entries):
                require(text(p)==entry['text'],'source/column text changed, truncated or duplicated')
                props = p.find('w:pPr',NS)
                spacing = props.find('w:spacing',NS)
                require(all(spacing.get('{'+W+'}'+k)==v for k,v in {'before':'0','after':'0','line':'240','lineRule':'auto'}.items()),'paragraph spacing')
                ind = props.find('w:ind',NS)
                require(ind.attrib=={'{'+W+'}'+k:v for k,v in INDENTS[entry['level']].items()},'indentation conflict')
                for name in ('keepNext','keepLines','pageBreakBefore'):
                    require(props.find('w:'+name,NS).get('{'+W+'}val')=='0','forced paragraph pagination')
                actual = []
                for run in p.findall('w:r',NS):
                    value = ''.join(t.text or '' for t in run.findall('w:t',NS))
                    rpr = run.find('w:rPr',NS)
                    require(rpr.find('w:rFonts',NS).get('{'+W+'}eastAsia')==font,'East Asian font missing')
                    u = rpr.find('w:u',NS).get('{'+W+'}val')=='single'
                    require(not u or not any(ch.isspace() for ch in value),'whitespace underlined')
                    actual.extend([u]*len(value))
                require(actual==mask[offset:offset+len(entry['text'])],'unchanged/diff underline mismatch')
                offset += len(entry['text'])+1
    return {'generation':'PASS','ooxml_direct_contract':'PASS','source_fidelity':'PASS',
            'visual_qa':'NOT TESTED','font_rendering':'NOT TESTED'}


if __name__=='__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir',type=Path,required=True)
    args = parser.parse_args()
    fixture = load_cases()
    for case in fixture['cases']:
        path = write_docx(case,args.output_dir/(case['id']+'.docx'),fixture['font'])
        print(path)
