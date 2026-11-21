"""Compare official figure and local before/after gaps at original page size."""
from pathlib import Path
import subprocess
import pymupdf as f
root=Path(__file__).resolve().parents[1]
old=f.open(stream=subprocess.check_output(['git','show','a3a138f:template/output/texlive2026/thesis.pdf'],cwd=root),filetype='pdf')
new=f.open(root/'template/output/texlive2026/thesis.pdf')
ref=f.open(root/'official_ref_2510/同济大学研究生学位论文写作参考示例_adobe转.pdf')
out=f.open();p=out.new_page(width=595.276*3,height=869.89)
for col,(doc,num,label) in enumerate([(ref,13,'Adobe Word p.14 - different artwork'),(old,7,'Before - a3a138f p.8'),(new,7,'After - 2026-11-21 p.8')]):
    p.insert_text((595.276*col+12,17),label,fontsize=10)
    p.show_pdf_page(f.Rect(595.276*col,28,595.276*(col+1),869.89),doc,num)
out.save(root/'compare/08_图表与题注间距_修订前后对照.pdf',deflate=True,garbage=4)
