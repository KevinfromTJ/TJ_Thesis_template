# 将编译产物输出到指定文件夹，保持项目根目录整洁
# 使用方式：在项目根目录执行 latexmk thesis.tex（不要加 -norc）
$out_dir = '.output';

# XeLaTeX + Biber（与模板要求一致）
$pdf_mode = 5;
$latex = 'xelatex -synctex=1 -interaction=nonstopmode -file-line-error %O %S';
$biber = 'biber %O %S';
$clean_ext = 'synctex.gz synctex.gz(busy) run.xml tex.bak bbl bcf fdb_latexmk run toc out';

# 若希望输出到 build 文件夹，可改为：$out_dir = 'build';
