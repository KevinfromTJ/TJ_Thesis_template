# 使用说明

这是以 `huang-shuai-dev/TongjiThesis_Proto@9362cdd` 为底稿的本地修订版。已经对照 2025 年 10 月校级指南、原始 Word 示例分节数据和上游 issues 核对。本次视觉更正依据在 [Adobe/Word核对报告](../audit/adobe-review/REVIEW.md)，早期选型记录见 [旧报告（部分已更正）](../audit/COMPARISON.md)。上游作者和历史说明保存在 [UPSTREAM_README.md](UPSTREAM_README.md)；它描述的是修改前的版本，使用方法以本文件为准。

## 开始写作

1. 在 `thesis.tex` 第一行选择学位：`degree=master` / `doctor`；学位类型：`degreetype=academic` / `profession`。当前示例按用户要求采用学术型硕士。`spine.tex` 也应采用同样的学位设置。
2. 修改 `data/cover.tex` 的中英文题目、作者、学号、学院、学科和导师。`cmajorfirst` 等中英文字段分别填写；英文学位名称 `edegree` 必须按实际授予学位显式配置，类文件的工科默认值不适合所有专业。
3. 替换 `data/chap01.tex` 至 `chap03.tex`，按需增加章节并在主文件中加入 `\tongjiinputfile{...}`。正文和引用均为排版占位示例。
4. 修改 `ref/refs.bib`，用 `\cite{key}` 引用。采用 Biber，不是 BibTeX；PDF 中默认只列实际引用的文献。电子文献保留 URL，作者缩写和析出分隔符由国标样式处理。
5. 修改附录、致谢、简历。`cassosupervisor={}` 等空值会移除可选封面行；有副导师/行业导师时才填写。基金内容也默认为空。
6. 最终签署声明页，可打印模板末页后签名；若需使用学院提供的原版表单，替换为该表单签署扫描件。扫描件自身的尺寸、页码必须人工核对。

当前按用户要求输出连续电子版：中文学术封面、英文封面、书脊依次占第1/2/3页，第4页起为摘要。不插入空白背面，不包含封面说明页。默认仍用 `twoside` 管理奇偶页样式，纸张左右边距同为31.7mm、装订线0。打印时A4、100%实际尺寸；本版没有为单面封面自动补空白页。

## 编译

需要 XeLaTeX、latexmk、Biber 和完整常用 TeX 宏包；本轮采用 TeX Live 2026 / Biber 2.22，推荐 `./build-2026.sh all`；下列 `build.sh` 仅使用当前PATH，旧发行版未重新执行本轮校准验证。字体从 `fonts/` 直接读取。

```bash
./build.sh             # output/thesis.pdf
./build.sh anonymous   # output/thesis_anonymous.pdf
./build.sh all         # 上述两种
./build.sh spine       # output/spine.pdf：独立书脊排版页
./build.sh watch       # 持续编译
./build.sh clean       # 清理辅助文件，保留 PDF
```

统一使用 `.latexmkrc`。Biber 或 XeLaTeX 出错时构建返回失败，不以旧 PDF 是否存在判断成功。PDF 的生成时间应与这次成功编译一致。

书脊采用仿宋四号、16 bp 行距、上下约 50 mm。主论文第3页和独立输出共用同一书脊排版命令；独立输出便于印制单位按论文厚度处理。长题目、英文题目和特殊符号需要检查竖排效果。

隐名入口会留空被 `\blindreviewfield{...}` 包裹的封面字段，并跳过致谢、简历和声明。正文中的姓名、自引、项目号、图片标识、附录等仍由作者按送审要求处理；自动核验只证明本仓库样例的已知字段已隐藏。

## 布局与可选项

- A4；上/下 25.4 mm，左/右 31.7 mm；版心 146.6 × 246.2 mm。
- 页眉盒顶距纸顶 20 mm。`headheight=5mm`，`headsep=0.4mm`；不要改回上游的 5.4 mm。
- 页脚盒底距纸底 15 mm。页码使用宋体 10.5 bp，显式盒深 2.1 bp；`footskip=10.4mm-2.1bp`。文字基线距底约 15.741 mm。
- 正文 12 bp / 20 bp 行距；目录 12 bp / 18 bp；参考文献、符号说明、简历 10.5 bp / 16 bp。
- 指南要求章标题16bp、段前24bp、段后18bp；节标题15/14/12bp、段后6bp。章标题和一级标题的CTeX行盒/skip已按Adobe基线校准，不能把源代码的skip值直接当作Word段落面板的段距。二、三级标题尚未完成同内容视觉校准。
- 封面信息区31.2bp行距，日期固定；声明采用25.4/27.24bp行距及固定签名位置。它们来自Adobe/Word实际排版，不再按字号数值推断Word单倍/多倍行距。
- `newstyle=true` 和 `bibtype=numeric` 是校级配置；旧式页眉及作者年份制仅为兼容保留，不作为本次校级合规配置。
- 符号表、图表索引默认注释，按论文实际需要启用。符号很多时应加入符号说明。
- 同等学力与涉密论文未覆盖本次正式/隐名成品验证，需按对应官方封面单独核对。不要把普通学硕/专硕示例直接用于其他封面类型。

## 复测

```bash
./build.sh all
./build.sh spine
latexmk -outdir=output/tests tests/layout.tex
python scripts/verify_layout.py
latexmk -outdir=output/tests tests/cover-variants.tex
```

Python 核验需 `pymupdf`。`tests/layout.tex` 含刻意扩展的摘要、目录、参考文献、致谢、简历，并使用虚构的测试文献；这些不会进入主论文。脚本检查真实 PDF 的行距、缩进、字号/字体、页眉页码、引用和附录编号，并通过栅格检查左右边界；结果写入 `output/verification.json`。

继承的字体文件归原权利人所有；保留上游字体说明。此修订是可复核的第三方排版实现，不是学校官方发布的 LaTeX 模板。Word 的字体行盒、页顶段距抑制、浮动文本框与 TeX 不完全相同，声明页和封面的逐像素一致性未作保证。

## 本机新版 TeX Live（2026-11-11 补充）

已找到并使用独立安装的 TeX Live 2026：`/data1_temp/chenjuntao/texlive/2026/bin/x86_64-linux`。本机推荐 `./build-2026.sh all`，输出 `output/texlive2026/`，不会与旧版辅助文件混用。

XeLaTeX 是实际编译引擎，TeX Live 是包含该引擎和宏包的发行版，latexmk 只是构建调度器；`latexmk` 不意味着使用 pdfLaTeX。新版日志确认 `preloaded format=xelatex`，参考文献使用同一发行版的 Biber 2.22。

[用于人工对照的两份 PDF 与页序号表](../compare/README.md)。旧 `build.sh` 使用当前 PATH，未修改系统默认环境。


2026-11-17细节更新：页眉线0.72bp；第3页书脊保留0.75bp矩形框，框内仿宋四号加粗、16bp行距；章号内部每侧留2bp小间隔，数字同为黑体三号。公式编号和 `\eqref` 使用中文全角括号。图题在下（段前6bp/后12bp），表题在上（段前后6bp），两者宋体五号、居中、单倍行距，序号与名称间距10.5bp。
