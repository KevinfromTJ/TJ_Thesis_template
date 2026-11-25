"""Side-by-side original-size pages for the 2026-11-25 spacing revision."""
from pathlib import Path
import subprocess
import pymupdf as f
root=Path(__file__).resolve().parents[1]
old=f.open(stream=subprocess.check_output(['git','show','dc3828a:template/output/texlive2026/thesis.pdf'],cwd=root),filetype='pdf')
new=f.open(root/'template/output/texlive2026/thesis.pdf')
out=f.open()
for idx,label in [(5,'TOC leaders'),(6,'Subsection spacing')]:
    p=out.new_page(width=1190.552,height=869.89)
    for col,doc,title in [(0,old,'Before dc3828a'),(1,new,'After 2026-11-25')]:
        p.insert_text((595.276*col+15,17),f'{title} | {label} p.{idx+1}',fontsize=10)
        p.show_pdf_page(f.Rect(595.276*col,28,595.276*(col+1),869.89),doc,idx)
out.save(root/'compare/09_二级节标题与目录引导点_修订前后.pdf',garbage=4,deflate=True)
