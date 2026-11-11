#!/usr/bin/env python3
"""Check TeX dimensions AND rendered PDF evidence. Run from template/.
Requires PyMuPDF. Test references are synthetic and not thesis bibliography.
"""
import argparse
import json
import re
from pathlib import Path
import pymupdf

root = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('--output-dir', default='output', help='Relative to template/, or absolute')
args = parser.parse_args()
out = root / args.output_dir
values = {}
for line in (out/'tests/layout.layout').read_text().splitlines():
    key, value = line.split('=')
    values[key] = float(value.removesuffix('pt'))
pt_to_mm = 25.4 / 72.27
expected_mm = {'paperwidth':210, 'paperheight':297, 'left':31.7,
               'evenleft':31.7, 'textwidth':146.6, 'textheight':246.2,
               'top':25.4, 'headtop':20, 'footerboxbottomfrombottom':15}
for key, expected in expected_mm.items():
    assert abs(values[key]*pt_to_mm-expected)<0.005, (key, values[key]*pt_to_mm)
assert abs(values['bodyleading']*72/72.27-20)<0.005

pdf = pymupdf.open(out/'tests/layout.pdf')
def lines(page):
    return [line for block in page.get_text('dict')['blocks'] if 'lines' in block
            for line in block['lines']]
def text(line):
    return ''.join(span['text'] for span in line['spans'])
def baseline(line):
    return line['spans'][0]['origin'][1]
def header(page):
    return ''.join(text(l) for l in lines(page) if 50<baseline(l)<70).replace(' ','')
def body(page):
    return [l for l in lines(page) if 75<baseline(l)<770]
def check_leading(ls, expected):
    ys = sorted({round(baseline(l),3) for l in ls})
    assert len(ys)>=3, ys
    deltas = [round(b-a,3) for a,b in zip(ys,ys[1:])]
    assert all(abs(d-expected)<0.03 for d in deltas), (expected,deltas)
    return deltas

headers = [header(p) for p in pdf]
for name, count in [('摘要',2),('Abstract',2),('目录',2),('参考文献',3),('致谢',2),
                    ('个人简历、在读期间发表的学术成果',2)]:
    assert headers.count(name)==count, (name,headers)
footers = []
for page in pdf:
    footer = [l for l in lines(page) if baseline(l)>780]
    assert len(footer)==1, footer
    footers.append(text(footer[0]))
    assert all('SimSun' in s['font'] for s in footer[0]['spans']), footer
    # CJK punctuation is compressed: its full-em font bbox can extend beyond
    # the ink. Check the raster instead of treating that bbox as ink overflow.
    pix = page.get_pixmap(matrix=pymupdf.Matrix(2,2), colorspace=pymupdf.csGRAY, alpha=False)
    data = pix.samples
    xleft = int((31.7-0.2)*72/25.4*2)
    xright = int((210-31.7+0.2)*72/25.4*2)+1
    for row in range(pix.height):
        assert min(data[row*pix.stride:row*pix.stride+xleft],default=255)>120
        assert min(data[row*pix.stride+xright:(row+1)*pix.stride],default=255)>120
assert footers[:6]==['I','II','III','IV','V','VI'],footers
assert footers[6:]==list(map(str,range(1,len(pdf)-5))),footers

body_deltas = check_leading([l for l in body(pdf[7]) if baseline(l)<250],20)
toc = body(pdf[4])
toc = [l for l in toc if l['spans'][0]['size']<13]
toc_deltas = check_leading(toc,18)
# Locate the continuation page by its header: title spacing can move pagination.
refs = body(pdf[headers.index('参考文献')+1])
reference_deltas = check_leading(refs,16)
left = 31.7*72/25.4
sec = next(l for l in toc if text(l).startswith('1.1 '))
subsec = next(l for l in toc if text(l).startswith('1.2.1 '))
assert abs(sec['bbox'][0]-left-24)<0.05
assert abs(subsec['bbox'][0]-left-48)<0.05
# A newer TeX distribution may split a reference at a page boundary.
# Identify continuation lines by content, not by their position on the page.
reference_continuations = [l for l in refs if not text(l).startswith('[')]
assert reference_continuations
assert all(abs(l['bbox'][0]-left-21)<0.05 for l in reference_continuations)
all_text = '\n'.join(p.get_text() for p in pdf)
assert '(A1)' in all_text
assert '图A1' in all_text.replace(' ','').replace('\n','')
assert '表A1' in all_text.replace(' ','').replace('\n','')
assert 'SMITH J, DOE J.' in all_text
assert '//' in all_text

anon = pymupdf.open(out/'thesis_anonymous.pdf')
formal = pymupdf.open(out/'thesis.pdf')
formal_text = '\n'.join(p.get_text() for p in formal)
anon_text = '\n'.join(p.get_text() for p in anon)
for marker in ['作者姓名','学院全称','导师姓名及职称','Author Name','Supervisor Name and Title']:
    assert marker in formal_text, marker
    assert marker not in anon_text, marker
assert not anon.metadata.get('author')
assert '同济大学学位论文原创性声明' not in anon_text
assert '个人简历、在读期间发表的学术成果' not in anon_text
# Only the two reverse sides of the single-sided covers may be empty.
assert [i+1 for i,p in enumerate(formal) if not p.get_text().strip()]==[2,4]
for name in ['thesis','thesis_anonymous','spine','tests/layout']:
    log = (out/f'{name}.log').read_text()
    assert not re.search(r'Overfull|Undefined control sequence|Missing character:|undefined references|undefined citations|headheight is too small|footskip is too small',log),name
report = {'status':'PASS','geometry_mm':{k:round(values[k]*pt_to_mm,6) for k in expected_mm},
          'footer_baseline_from_bottom_mm':round(values['footerbaselinefrombottom']*pt_to_mm,6),
          'leading_bp':{'body':20,'toc':18,'references':16},
          'toc_indent_bp':[24,48], 'reference_hanging_indent_bp':21,
          'regression_pages':len(pdf),'headers':headers,'footers':footers,
          'formal_pages':len(formal),'anonymous_pages':len(anon),
          'sample_anonymity':'PASS (only the included sample, not arbitrary user content)'}
(out/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False,indent=2))
