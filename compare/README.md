# PDF 对照入口（2026-11-21 更新）

- [08 图表与题注留白：学校／修订前／修订后](08_图表与题注间距_修订前后对照.pdf)（学校与本地图片内容不同；表格留白为试调值）

**02为当前学术版直接编译PDF；03–05为2026-11-11历史对照。**

- [07 当前学术版与学校参考对照（含第3页书脊）](07_学术版_学校与修订版对照.pdf)

当前物理页序：中文封面1、英文封面2、书脊3、中文摘要4、英文摘要5、目录6、第一章7、文献10、附录11、致谢12、简历13、声明14。无空白页。

以下页码表、同内容摘录及对照生成命令属于2026-11-11历史版本；复现旧对照应使用 `adobe-revision-20261111` 标签下的完整源码和PDF。

唯一学校视觉基准为用户通过 Adobe/PDFMaker 从 Word 导出的 PDF。LibreOffice 旧导出退出本入口，不再据其调整布局。

- [01 学校 Adobe/Word 原始 PDF](01_学校示例_Adobe_Word导出.pdf)
- [02 修订模板：XeLaTeX 2026 直接编译 PDF](02_LaTeX模板_XeLaTeX2026直接编译.pdf)
- [03 同内容摘录：学校在左、XeLaTeX 在右](03_Adobe与XeLaTeX_同内容摘录对照.pdf)
- [04 修改前后：学校／旧修订／新修订](04_Adobe与修订前后_页面布局对照.pdf)
- [05 上游样例：学校／CS仓库样例／新修订](05_Adobe与上游样例及修订版.pdf)
- [06 CS 仓库原始样例](06_上游CS仓库自带样例.pdf)
- [本次核对报告与已知差异](../audit/adobe-review/REVIEW.md)

02 是直接编译文件的链接，未拼接或移动内容。03–05 是检查用并排 PDF，各原页以原尺寸放置，页顶只增加英文来源标签；不要将检查用宽幅页面作为论文打印。03 的摘要、正文只摘录学校示例首段，不含批注及后续段落；声明使用相同 X 占位题目。封面按专硕配置，学位字样等仍取决于选项。未给普通正文添加手动断行。04、05 正文和题目不同，只用于布局对照，不用于判断分页是否一致。

| 页面 | 学校 Adobe 物理页 | 修订论文物理页 |
|---|---:|---:|
| 专业学位中文封面 | 2 | 1 |
| 英文封面 | 5 | 3 |
| 中文摘要 | 9 | 5 |
| 英文摘要 | 10 | 6 |
| 目录 | 11 | 7 |
| 第一章 | 12 | 8 |
| 参考文献 | 16 | 11 |
| 附录 | 17 | 12 |
| 致谢 | 18 | 13 |
| 简历 | 19 | 14 |
| 声明 | 20 | 15 |

```bash
./template/build-2026.sh all
./template/build-2026.sh test
python template/scripts/verify_layout.py --output-dir output/texlive2026
# 在 template/ 中重建同内容摘录：
PATH=/data1_temp/chenjuntao/texlive/2026/bin/x86_64-linux:$PATH latexmk -outdir=output/texlive2026/proof tests/adobe-proof.tex
# 回到项目根目录，重建检查用并排文件：
python audit/adobe-review/make_comparison.py
```

本机固定使用 `/data1_temp/chenjuntao/texlive/2026/bin/x86_64-linux` 中配套 XeLaTeX / latexmk / Biber。当前正式版15页、隐名版12页、书脊1页；扩展回归文档19页。自动检查通过不等于所有 Word 排版细节均已逐项认证，具体范围见核对报告。
