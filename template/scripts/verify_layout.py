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
assert '（A1）' in all_text
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
# User-requested continuous edition: Chinese / English / spine, without blanks.
for document in (formal, anon):
    assert all(p.get_text().strip() for p in document)
    assert '学术学位' in document[0].get_text()
    assert 'A thesis submitted to' in document[1].get_text()
    spine_text = ''.join(document[2].get_text().split())
    assert '同济大学' in spine_text and '学位论文中文题目' in spine_text
    assert '摘要' in document[3].get_text()

# Chapter label must have no extra CJK/Latin glue: 第(16bp) + 2bp, digit(8bp) + 2bp, 章.
chapter_page = next(p for p in formal if header(p).startswith('第1章'))
raw_lines = [l for b in chapter_page.get_text('rawdict')['blocks'] for l in b.get('lines',[])]
label = next(l for l in raw_lines if 110 < l['spans'][0]['origin'][1] < 125
             and l['spans'][0]['chars'][0]['c'] == '第')
chars = [c for s in label['spans'] for c in s['chars']]
assert ''.join(c['c'] for c in chars[:3]) == '第1章'
assert abs(chars[1]['origin'][0]-chars[0]['origin'][0]-18) < 0.03
assert abs(chars[2]['origin'][0]-chars[1]['origin'][0]-10) < 0.03
assert all('SimHei' in s['font'] and abs(s['size']-16)<0.01 for s in label['spans'])
assert '论文封面说明' not in formal_text
# User-reviewed visual details, checked against the rendered PDF.
rule = next(d for d in chapter_page.get_drawings() if 70<d['rect'].y0<73)
assert abs(rule['width']-0.72)<0.01
frame = formal[2].get_drawings()
assert len(frame)==4 and all(abs(d['width']-0.75)<0.01 for d in frame)
assert '（2.1）' in formal_text and '式（2.1）' in formal_text
spine_lines = lines(formal[2])
assert all('FangSong' in s['font'] and abs(s['size']-14)<0.01
           for l in spine_lines for s in l['spans'])
check_leading(spine_lines[:len('学位论文中文题目')],16)
# Section/subsection adjacency must retain Word-style paragraph separation.
found_adjacent = False
for page in pdf:
    ls = lines(page)
    sub = next((l for l in ls if text(l)=='二级目录缩进检查'
                and l['spans'][0]['size']>13),None)
    if sub is None:
        continue
    section = [l for l in ls if text(l).startswith('目录续页检查')
               and l['spans'][0]['size']>14 and baseline(l)<baseline(sub)]
    if section:
        assert abs(baseline(sub)-baseline(section[-1])-42.84)<0.05
        found_adjacent = True
        break
assert found_adjacent
# Leaders must reach the page digits, including entries with multi-digit pages.
for page in [p for p in pdf if header(p)=='目录']:
    for block in page.get_text('rawdict')['blocks']:
        for line in block.get('lines',[]):
            cs = [c for span in line['spans'] for c in span['chars']]
            dots = [i for i,c in enumerate(cs) if c['c']=='.']
            if not dots:
                continue
            lastdot = dots[-1]
            if len(dots)>10:
                xs = [cs[i]['origin'][0] for i in dots[-9:]]
                assert all(abs(b-a-5.28)<0.03 for a,b in zip(xs,xs[1:])), xs
            digits = [c for c in cs[lastdot+1:] if c['c'].isdigit()]
            if digits:
                assert digits[0]['bbox'][0]-cs[lastdot]['bbox'][2]<5
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
