"""Build the 2026-11-17 academic-layout comparison at original physical size."""
from pathlib import Path
import pymupdf as f
root = Path(__file__).resolve().parents[1]
ref = f.open(root/'official_ref_2510/同济大学研究生学位论文写作参考示例_adobe转.pdf')
current = f.open(root/'template/output/texlive2026/thesis.pdf')
assert len(current)==14
pairs=[('Academic cover',1,1),('English cover',5,2),('Spine - reference annotations excluded',8,3),('Chapter heading - different body text',12,7)]
result=f.open()
for title,a,b in pairs:
    page=result.new_page(width=1190.552,height=869.89)
    for col,doc,num,name in [(0,ref,a,'ADOBE WORD'),(1,current,b,'XELATEX 2026-11-17')]:
        page.insert_text((595.276*col+15,17),f'{title} | {name} p.{num}',fontsize=9)
        page.show_pdf_page(f.Rect(595.276*col,28,595.276*(col+1),869.89),doc,num-1)
result.save(root/'compare/07_学术版_学校与修订版对照.pdf',deflate=True,garbage=4)
