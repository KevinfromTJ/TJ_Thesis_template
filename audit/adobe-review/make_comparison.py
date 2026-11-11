"""Rebuild inspection PDFs from unmodified source pages, at original physical size."""
from pathlib import Path
import json, hashlib
import pymupdf as f
root=Path(__file__).resolve().parents[2]
out=root/'compare'
sources={
 'adobe':root/'official_ref_2510/同济大学研究生学位论文写作参考示例_adobe转.pdf',
 'upstream':root/'upstream/TongjiThesisForCS/样例论文.pdf',
 'before':root/'audit/adobe-review/before/thesis.pdf',
 'after':root/'template/output/texlive2026/thesis.pdf',
 'proof':root/'template/output/texlive2026/proof/adobe-proof.pdf'}
docs={k:f.open(p) for k,p in sources.items()}
manifest={k:{'path':str(p.relative_to(root)), 'sha256':hashlib.sha256(p.read_bytes()).hexdigest(), 'pages':len(docs[k]),'metadata':docs[k].metadata} for k,p in sources.items()}
(root/'audit/adobe-review/sources.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
def paired(filename,columns,rows):
 result=f.open()
 for label,nums in rows:
  page=result.new_page(width=595.276*len(columns),height=841.89+28)
  for j,(col,num) in enumerate(zip(columns,nums)):
   page.insert_text((595.276*j+18,17),f'{label} | {col.upper()} p.{num}',fontsize=10)
   page.show_pdf_page(f.Rect(595.276*j,28,595.276*(j+1),869.89),docs[col],num-1)
 result.save(out/filename,garbage=4,deflate=True)
paired('03_Adobe与XeLaTeX_同内容摘录对照.pdf',['adobe','proof'],[
 ('Chinese professional cover',[2,1]),('English cover',[5,3]),
 ('Abstract - first paragraph only',[9,5]),('Chapter - first paragraph only',[12,7]),
 ('Declaration - same placeholder title',[20,8])])
paired('04_Adobe与修订前后_页面布局对照.pdf',['adobe','before','after'],[
 ('Chinese professional cover',[2,1,1]),('English cover',[5,3,3]),
 ('Abstract - different text',[9,5,5]),('Chapter - different text',[12,8,8]),
 ('Declaration - different title',[20,15,15])])
paired('05_Adobe与上游样例及修订版.pdf',['adobe','upstream','after'],[
 ('Abstract - different text',[9,3,5]),('Chapter - different text',[12,15,8]),
 ('Declaration - different title and wording',[20,29,15])])
def textlines(page):
 return [( ''.join(s['text'] for s in l['spans']),l['spans'][0]['origin'][1])
         for b in page.get_text('dict')['blocks'] for l in b.get('lines',[])]
# Compare external reference baselines with a same-content XeLaTeX fixture.
checks=[('chapter title',11,6,lambda t:'第1' in t,100,140),
 ('section title',11,6,lambda t:t.startswith('1.1'),140,190),
 ('chapter first text',11,6,lambda t:t.startswith('随着现代'),150,230),
 ('abstract title',8,4,lambda t:t=='摘要',100,140),
 ('abstract first text',8,4,lambda t:t.startswith('在实际工程'),140,180),
 ('declaration title',19,7,lambda t:'原创性声明' in t,70,110),
 ('declaration first text',19,7,lambda t:t.startswith('本人郑重'),115,145),
 ('authorization title',19,7,lambda t:'版权使用授权书' in t,380,420),
 ('authorization first text',19,7,lambda t:t.startswith('本人完全'),420,460)]
measurements=[]
for label,a,b,pred,lo,hi in checks:
 vals=[next(y for t,y in textlines(docs[k][i]) if lo<y<hi and pred(t.strip())) for k,i in [('adobe',a),('proof',b)]]
 measurements.append({'item':label,'adobe_bp':round(vals[0],3),'xelatex_bp':round(vals[1],3),'delta_bp':round(vals[1]-vals[0],3)})
 assert abs(vals[1]-vals[0])<0.1,(label,vals)
(root/'audit/adobe-review/measurements.json').write_text(json.dumps(measurements,indent=2))
print(json.dumps(measurements,indent=2))
for k,num in [('after',0),('after',2),('after',14),('proof',6)]:
 docs[k][num].get_pixmap(matrix=f.Matrix(1.2,1.2)).save(root/f'audit/adobe-review/{k}-{num+1:02}.png')
