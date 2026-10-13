"""Optional local PDF text/font/page probe; rendered images still need visual inspection.
Requires PyMuPDF and Pillow already present locally. Not run by CI or called a visual PASS.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys


def probe(directory):
    from docx_reference import HEADERS, expand_row, load_cases
    import fitz
    from PIL import Image, ImageDraw
    fixture = load_cases()
    results = []
    for case in fixture['cases']:
        path = directory/(case['id']+'.pdf')
        docx_path = directory/(case['id']+'.docx')
        if path.stat().st_mtime_ns < docx_path.stat().st_mtime_ns:
            raise ValueError(f'{case["id"]}: stale PDF predates the generated DOCX; rerender before probing')
        pdf = fitz.open(path)
        expected = [''.join(p['text'] for row in case['rows'] for p in expand_row(row)[col]) for col in range(3)]
        observed = ['','','']
        headers_ok = True
        fonts = set()
        boxes_ok = True
        thumbs = []
        boundaries = (45.5,225.5,405.5,549.8)
        for page in pdf:
            header = page.search_for(HEADERS[0])
            headers_ok = headers_ok and len(header)==1 and all(
                any(abs(rect.y0-header[0].y0)<1 for rect in page.search_for(h)) for h in HEADERS)
            if not header:
                raise ValueError(f'{case["id"]}: missing repeated header on page {page.number+1}')
            for col in range(3):
                rect = fitz.Rect(boundaries[col],header[0].y1+.1,boundaries[col+1],page.rect.height-40)
                observed[col] += page.get_text('text',clip=rect)
            for font in page.get_fonts():
                fonts.add(font[3])
            for block in page.get_text('dict')['blocks']:
                for line in block.get('lines',[]):
                    for span in line['spans']:
                        r = fitz.Rect(span['bbox'])
                        boxes_ok = boxes_ok and r.x0>=40 and r.x1<=page.rect.width-40 and r.y0>=35 and r.y1<=page.rect.height-35
            pix = page.get_pixmap(matrix=fitz.Matrix(.6,.6))
            thumbs.append(Image.frombytes('RGB',(pix.width,pix.height),pix.samples))
        normalize = lambda text: re.sub(r'\s+','',text)
        columns_ok = [normalize(a)==normalize(b) for a,b in zip(observed,expected)]
        sheet = Image.new('RGB',(4*370,((len(thumbs)+3)//4)*535),'#dddddd')
        draw = ImageDraw.Draw(sheet)
        for i,thumb in enumerate(thumbs):
            x,y = (i%4)*370,(i//4)*535
            sheet.paste(thumb,(x,y+20))
            draw.text((x+10,y+3),f'{case["id"]} page {i+1}',fill='black')
        sheet.save(directory/(case['id']+'-contact.png'))
        results.append({'case':case['id'],'pdf_pages':len(pdf),'docx_sha256':hashlib.sha256(docx_path.read_bytes()).hexdigest(),
                        'pdf_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
                        'column_text_match_ignoring_whitespace':columns_ok,'repeat_header_all_pages':headers_ok,
                        'text_boxes_within_page_margins':boxes_ok,'embedded_fonts':sorted(fonts),
                        'visual_qa':'NOT TESTED BY THIS SCRIPT','renderer':'record actual soffice --version separately'})
        pdf.close()
    (directory/'pdf-probe.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(results,ensure_ascii=False,indent=2))
    if not all(all(r['column_text_match_ignoring_whitespace']) and r['repeat_header_all_pages'] and r['text_boxes_within_page_margins'] for r in results):
        raise ValueError('PDF probe failure; see pdf-probe.json, do not claim rendered source fidelity PASS')


def preview_pdf(path, directory, max_pages=100):
    """任意PDF的PNG頁面預覽；不使用fixture固定欄寬，不給visual PASS。"""
    import fitz
    with fitz.open(path) as pdf:
        fonts=set()
        pages=[]
        for i,page in enumerate(pdf):
            if i >= max_pages: break
            name=f'page-{i+1:03d}.png'
            target=Path(directory)/name
            if target.exists(): raise ValueError('拒絕覆寫既有預覽')
            page.get_pixmap(matrix=fitz.Matrix(1.25,1.25)).save(target)
            fonts.update(font[3] for font in page.get_fonts())
            pages.append(name)
        return {'pdf_sha256':hashlib.sha256(Path(path).read_bytes()).hexdigest(), 'pdf_pages':len(pdf),
                'preview_pages':pages,'embedded_fonts_observed':sorted(fonts),
                'preview_limit':max_pages,'visual_qa':'NOT TESTED','pages_reviewed':[]}


if __name__=='__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory',type=Path)
    args = parser.parse_args()
    try:
        probe(args.directory)
    except (ValueError,OSError,ImportError) as e:
        print(f'FAIL: {e}',file=sys.stderr)
        sys.exit(1)
