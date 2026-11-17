# 同济大学研究生学位论文模板：核对与修订版

**当前版本（2026-11-17）：学术学位，中文封面→英文封面→书脊，无空白页；章标题使用紧凑的“第1章”。** [最新PDF](template/output/texlive2026/thesis.pdf)。以下2026-11-11留档作为历史记录保留。

**2026-11-11 更正：不再使用 LibreOffice 转换结果校准。当前以你提供的 Adobe/Word PDF 为视觉基准；此前封面、声明页和标题位置已重新修订。**

推荐使用 **`template/`**，它以 huang-shuai-dev 分支为底稿，按研究生院 2025 年 10 月指南修订。两个上游完整仓库保存在 `upstream/`，你提供的原始资料保留在 `official_ref_2510/`。

- [修订模板与用法](template/README.md)
- [正式版示例 PDF](template/output/texlive2026/thesis.pdf)
- [隐名版示例 PDF](template/output/texlive2026/thesis_anonymous.pdf)
- [Adobe/Word重新核对报告](audit/adobe-review/REVIEW.md)
- [早期选型记录（视觉结论已更正）](audit/COMPARISON.md)
- [原始 Word 分节参数](audit/word-layout-report.md)
- [自动核验结果](template/output/texlive2026/verification.json)

在本目录运行：

```bash
./template/build-2026.sh all
```

校级来源：[研究生院《同济大学研究生学位论文写作指南》](https://gs.tongji.edu.cn/info/1063/1754.htm)，页面日期 2025-10-31。本次核对日期 2026-11-11。学院/学位分委员会另行规定的格式需按实际专业补充；本目录没有擅自套用交通学院等其他学院的专用封面。

补充：已找到本机独立安装的 **TeX Live 2026**，推荐运行 `./template/build-2026.sh all`。新版直接编译结果及学校示例集中在 [PDF对照入口](compare/README.md)，其中含物理页序号对应表。

## 手动留档：模板来源与修改记录

记录日期：**2026-11-11**。本节手动维护；以后修改模板时，应同步写明修改原因、文件、验证结果，再提交 Git。

### 来源与版本

- **实际代码底稿**：[huang-shuai-dev/TongjiThesis_Proto](https://github.com/huang-shuai-dev/TongjiThesis_Proto)，固定提交 `9362cdd8a4d8e5a73c0ce3f7df7bf6ace597c20e`。`template/` 是在它上面修改的，并非从零重写。
- **交叉核对来源**：[windforestfiremountain/TongjiThesisForCS](https://github.com/windforestfiremountain/TongjiThesisForCS)，固定提交 `bd4f2553826081f4dfcc44e61a04881efd6d549e`。用于检查代码差异及仓库自带的 `样例论文.pdf`，没有整体合并该分支。
- **格式依据**：`official_ref_2510/` 的2025年10月校级指南、原始Word示例及用户提供的Adobe/Word导出PDF。明确文字要求优先；有冲突的示例外观不直接照搬。LibreOffice导出不再作为校准依据。
- 机器可读来源记录：[UPSTREAM.lock.json](UPSTREAM.lock.json)。继承的字体、图片及上游作者信息保留，不把它们算作本次原创内容。

### 已做的修改

| 范围 | 修改内容 | 主要文件 |
|---|---|---|
| 页面与页眉页脚 | A4，上下25.4mm、左右31.7mm、装订线0；修正页眉盒高度与间距的计算，明确页脚盒底距底15mm；修复多页章节页眉和页码衔接 | `template/tongjithesis.cls` |
| 字号、行距、标题 | 正文12/20bp、目录12/18bp、文献及简历10.5/16bp；统一标题与编号字号；章标题及章后一级标题按Adobe实际基线修正CTeX行盒和段距映射 | `template/tongjithesis.cls`、`template/ctex-fontset-tongji.def` |
| 封面 | 专业/学术封面分别定位；信息行31.2bp，日期固定在页底；可选导师和联合单位字段为空时不显示；使用学校PDF中的标志图像 | `template/tongjithesis.cls`、`template/data/cover.tex`、`template/figures/tongji-official-logo.jpeg` |
| 声明 | 恢复学校声明内容，按Adobe布局使用约25.4/27.24bp行距及固定签名区域；超长声明文本报错防止叠印 | `template/data/statements.tex` |
| 目录、图表、文献、附录 | 目录缩进2/4字符；调整图表标题；文献16bp、21bp悬挂缩进、恢复必要URL/DOI和析出分隔符；附录图表公式采用A1形式 | `template/tongjithesis.cls`、`template/ref/`、`template/data/appendix.tex` |
| 文档内容与隐名 | 将个人论文示例改为通用占位内容；调整文末顺序为文献、附录、致谢、简历、声明；提供隐名字段及相应内容开关；独立书脊入口 | `template/thesis*.tex`、`template/data/`、`template/spine.tex` |
| 构建 | 固定XeLaTeX配套Biber，编译失败返回失败；增加本机TeX Live 2026入口和独立输出目录 | `template/.latexmkrc`、`template/build.sh`、`template/build-2026.sh` |
| 核验与证据 | 增加多页回归、封面变体、Adobe同内容摘录；保存PDF基线测量、原生DOC分节分析和并排对照 | `template/tests/`、`template/scripts/verify_layout.py`、`audit/`、`compare/` |

相对完整上游快照，本地写作目录也未携带上游GitHub发布工作流及个人VS Code配置；这些删除同样可在Git差异中看到。字体文件沿用上游，未改写。

### 纠错记录与验证边界

此前错误地用LibreOffice转换外观校准，导致封面信息区过密、日期上移、声明页压紧；已撤回相关结论并在Adobe复核中修正。旧稿仅作为历史证据保留于 `audit/adobe-review/before/`，不作为当前模板。

本轮已有验证：XeLaTeX2026编译正式版15页、隐名版12页、书脊1页；19页扩展回归通过版心、行距、缩进、页眉页码、匿名样例与日志检查。同内容摘录的章标题、章后一级标题和首行正文基线与Adobe差小于0.05bp。详细证据见 [本轮报告](audit/adobe-review/REVIEW.md) 和 [核验JSON](template/output/texlive2026/verification.json)。

仍有边界：Word和XeLaTeX的标点压缩、断行不同；二三级标题、多行标题及复杂图表周围留白尚未逐页校准。目录缩进、副标题字号等存在学校示例与文字要求不一致之处，处理理由已在报告中列出。**当前是可复核的第三方修订模板，不是宣称完全一致或校方认证的最终版。**

### Git 留档方式

最外层 `Thesis_template/` 原来没有Git仓库。本次按用户要求**事后补录**，没有伪造之前各轮操作的提交历史：

| 提交／标签 | 内容 |
|---|---|
| `899500f` / `upstream-baseline-9362cdd` | 将上游固定提交的全部受控文件原样放到Git树的 `template/` 下，作为未修改基线；不覆盖当前工作文件 |
| `adobe-revision-20261111` | 当前修订模板、原始依据、选定检查证据、直接编译PDF快照和本README留档；与基线比较可查看全部最终改动 |

这次仅提交到本地Git，没有推送到GitHub。源码、原始官方资料、当前PDF快照和选定审查证据纳入版本控制；构建中间文件、转换缓存、预览图片及两个独立上游克隆不纳入外层仓库。PDF快照已显式纳入Git，其后重新编译仍可通过 `git diff` 发现更新。

```bash
# 查看本项目补录的两次提交（不展开取回的上游对象）
git log --oneline main
# 查看相对未修改底稿的最终代码修改
git diff upstream-baseline-9362cdd adobe-revision-20261111 -- template/
# 查看本轮修订归档
git show --stat adobe-revision-20261111
# 后续修改后手动更新本节，再提交
git status --short
```

`upstream/` 是本地独立克隆，被外层Git忽略。若迁移到新机器后需要重建原始对照来源，可按 `UPSTREAM.lock.json` 克隆两个仓库并分别检出固定提交；`compare/06_上游CS仓库自带样例.pdf` 链接及对照生成脚本依赖该来源。当前编译PDF已归档，重新生成则需要在新机器安装成套XeLaTeX/Biber，并通过 `TONGJI_TEX_BIN` 指定其bin目录。


### 2026-11-17：学术学位、连续页序及章号间距修订

按用户新增要求修改，不改动2026-11-11基线标签：

1. `thesis.tex` 与 `spine.tex` 改为 `degreetype=academic`。中文封面仅显示学术学位类型，英文采用相应学术学位配置。
2. 移除封面背面与摘要前的强制奇数页补白；中文封面、英文封面、书脊固定为物理第1/2/3页，第4页起摘要。没有封面说明页。书脊按学校Adobe第8页所示内容结构排版，使用实际题目/作者和同济大学字样，仿宋四号、16bp行距、上下约50mm，不复制示例说明箭头及批注。主论文与独立 `spine.pdf` 共用 `\makespine`。
3. 章正标题仍为黑体三号16bp；仅在章号范围关闭中西文自动间距，使“第1章”连续。章号与章名间保留一个汉字间距，不影响正文中西文间距。
4. 页眉线保留：直接读取PDF矢量数据，Adobe参考为0.72bp高的实心矩形，当前XeLaTeX为约0.3985bp描边。因此60%缩放时出现浅色像素边缘不能证明物理线更粗，未为了某个缩放比例盲目改宽度；抗锯齿观感仍取决于阅读器。

验证：XeLaTeX2026配套编译正式版14页、隐名版11页、独立书脊1页；19页回归通过。新增检查确认两版本均无空白页、前三页内容与顺序正确，以及章号字符间没有额外空隙。常规版心、20/18/16bp行距及页眉页码检查仍通过。本轮未改变学校边距要求。

当前PDF见上方入口；[本轮学校示例与修订版对照](compare/07_学术版_学校与修订版对照.pdf)。`compare/03`–`05` 保留2026-11-11的历史对照，不是本轮PDF；本轮对照页明确标示来源和物理页码。Git提交信息为 `fix: use academic covers and include spine without blank pages`。


### 2026-11-17：第二轮细节修订

按用户复核意见进一步修改，覆盖上一轮相应设置：

- 页眉分隔线从0.4pt改为 **0.72bp**，与Adobe/Word PDF实测线条厚度一致；页眉位置与版心边距仍用既有设置。
- 主论文第3页与独立书脊恢复窄长矩形边框，按参考第8页约33bp宽、658bp高的位置绘制，框线0.75bp。框内文字仍为仿宋四号14bp、加粗、16bp行距、段前段后0；不含示例批注。
- “第x章”内的中西文间距改为每侧 **2bp**，介于第一版约8bp的自动间距和上一轮0间距之间；章号数字与汉字均为黑体三号16bp。章节名称前仍空一汉字。
- 显示公式编号及 `\eqref` 正文引用统一中文全角括号，如“（2.1）”“（A1）”，编号本身保持原样。
- 图题置下，宋体五号10.5bp、居中、单倍行距、段前6bp/段后12bp；表题置上，同字体字号及行距、段前6bp/段后6bp；图表序号与名称间距均为一个字号宽度10.5bp。修正原有序号局部字体命令残留的1.5倍行距。浮动体距正文的间距与标题段距是分别控制的参数。

本轮重新编译正式版14页、隐名版11页、书脊1页，并通过19页布局回归；核对PDF中的线宽、书脊框、公式括号、章号间距与图表标题。当前 [正式PDF](template/output/texlive2026/thesis.pdf) 和 [学校对照07](compare/07_学术版_学校与修订版对照.pdf) 已更新。Git提交信息：`fix: refine header rule spine chapter spacing and captions`。
