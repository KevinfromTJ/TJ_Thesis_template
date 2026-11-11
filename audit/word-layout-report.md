# official_ref_2510 原始 Word 分节页面设置核对

完成日期：2026-11-11。仅写入 audit；未修改 template 或原始 .doc。未使用 sudo、付费软件或在线文档转换服务。

## 原始值汇总

以下来自原始 OLE 二进制，而非文档正文中的写作要求或 LibreOffice 转换结果。单位 mm（括号内为原始 twips）；1 inch = 1440 twips。页眉/页脚距离分别从纸张顶边/底边计算，不是正文与页眉/页脚之间的空隙。

| 文件与节 | 上 | 下 | 左 | 右 | 页眉 | 页脚 |
|---|---:|---:|---:|---:|---:|---:|
| 指南 第1–3节 | 25.012 (1418) | 23.001 (1304) | 26.000 (1474) | 24.007 (1361) | 15.011 (851) | 14.993 (850) |
| 示例 第1–2节 | 25.400 (1440) | 25.400 (1440) | 31.697 (1797) | 31.697 (1797) | 20.002 (1134) | 20.002 (1134) |
| 示例 第3–14节 | 25.400 (1440) | 25.400 (1440) | 31.697 (1797) | 31.697 (1797) | 20.002 (1134) | 14.993 (850) |

两份文件所有节纸张均为 11906 × 16838 twips，约 210.009 × 297.004 mm（A4），装订线均为 0。所有目标几何参数均有显式 SPRM，不需要猜测默认值。

## 每节定位

CP 是主文档文本字符位置，不是页码。摘要含域代码时保留其部分文字；表格、文本框可能影响阅读顺序。

### 同济大学研究生学位论文写作参考指南.doc

SHA-256：`54d02d03dde964b62d6ac29ea5b33376800fdd75916613d5a1b227a1cdd20e32`。原生节数：3。

| 节 | CP 范围（左闭右开） | 起始文本 | SEPX 字节偏移 |
|---|---|---|---|
| 1 | [0, 1846) | 同济大学研究生学位论文写作参考指南 （研究生院，2025年10月） 前言  学位论文是研究生科研成果的集中体现 | 51712 |
| 2 | [1846, 2548) | 2.12 学位论文原创性声明 本部分内容可直接下载，提交时作者须亲笔签名。 同济大学学位论文原创性声明 本人郑 | 51785 |
| 3 | [2548, 5530) | 第3章 书写要求 3.1 文字、标点符号和数字 汉字的使用应严格执行国家的有关规定，除特殊需要外，不得使用已废 | 51845 |

### 同济大学研究生学位论文写作参考示例.doc

SHA-256：`87031a8e16c3694ae4c8ea98453ef9470d7c11be24631aa4d4dd9d7320032f1e`。原生节数：14。

| 节 | CP 范围（左闭右开） | 起始文本 | SEPX 字节偏移 |
|---|---|---|---|
| 1 | [0, 928) | 硕/博士学位论文  （学术学位）    专业型硕士博士（打印时删除） 硕/博士学位论文  （专业学位）   同 | 71168 |
| 2 | [928, 939) |  | 71240 |
| 3 | [939, 1533) | 摘要 在实际工程结构的服役过程中，由于非线性与随机性的耦合作用，工程结构特别是混凝土结构的非线性反应具有不可精 | 71312 |
| 4 | [1533, 2314) | ABSTRACT In practical engineering, the structures usual | 71384 |
| 5 | [2314, 3895) | 目录  TOC \o "1-3" \h \z \u   HYPERLINK \l "_Toc93734158" | 71443 |
| 6 | [3895, 4483) | 第1章 引言 1.1 概述 随着现代科学技术的发展和人们生活质量的提高，对于工程结构的性能提出了越来越高的要求 | 71502 |
| 7 | [4483, 4597) | 趋于成熟。早期在物理学研究中使用的随机模拟方法于20世纪70年代初期引入随机结构分析以来，已经成为检验各种随机 | 71575 |
| 8 | [4597, 4968) | 第3章 结构非线性损伤构形状态的随机演化分析  …… 3.2 结构非线性构形状态转移过程及其演化方程  ……  | 71635 |
| 9 | [4968, 5156) | 第7章 结论与展望 7.1 结论 本文的研究工作初步探讨了随机结构反应的概率密度演化问题，对于具有不同类型本构 | 71695 |
| 10 | [5156, 5404) | 参考文献 [1] 陈**，车**，陈**. 具有***的工程结构动力优化设计[J]. 计算力学学报，2021， | 71755 |
| 11 | [5404, 5425) | 附录A ×××××     …… | 71815 |
| 12 | [5425, 5732) | 致谢 逾尺的札记和研究纪录凝聚成这么薄薄的一本，高兴和欣慰之余，不禁感慨系之。记得鲁迅在一篇文章里写道：“人类 | 71875 |
| 13 | [5732, 5964) | 个人简历、在读期间发表的学术成果 个人简历： XX，男/女，X年X月生。 X年X月毕业于XX大学 XX专业 获 | 71935 |
| 14 | [5964, 6729) | 同济大学学位论文原创性声明 本人郑重声明：所呈交的学位论文《XXXXXXXXXXXXXXXXXXXXXXXXX | 71998 |

## 转换产物与差异

LibreOffice 7.3.7 已成功生成两份 DOCX 和两份直接从 DOC 导出的 PDF；另生成两份 DOCX 再导出 PDF，便于往返核对。产物没有手工改写页边距或修补节数。

| 文件 | 原生节数 | 转换 DOCX 节数 | DOC→PDF 页数 | DOCX→PDF 页数 |
|---|---:|---:|---:|---:|
| 同济大学研究生学位论文写作参考指南 | 3 | 3 | 10 | 10 |
| 同济大学研究生学位论文写作参考示例 | 14 | 15 | 24 | 24 |

- 指南 3 节的 DOCX `header` 均变为 0；原生为 851 twips（15.011 mm）。DOCX 未写入页眉引用，这与未启用页眉的导出处理相符；不能据此说原生页眉距离为 0。其余目标几何值一致。
- 示例前两节的 DOCX `footer` 均变为 0；原生为 1134 twips（20.003 mm）。这两节 DOCX 未写入页脚引用。
- 示例原生 14 节，DOCX 含 15 个 `sectPr`，其中第 13 个标为 continuous；因此不能将全部转换节与原生节逐一按序等同。所有转换节的纸张与四边距均与原生一致，转换第 3–15 节页眉/页脚为 1134/850 twips。JSON 的同序差值只是机械对照，不代表已经完成文本边界对齐。
- 原文要求的宋体、黑体、仿宋等在导出 PDF 中出现 NotoSansCJKjp、WenQuanYiZenHei 等替代字体。字体和 LibreOffice 排版可能改变换行、页数、表格、公式、文本框与浮动对象位置。
- 已查看两份 PDF 首页，正文/封面能正常显示；未逐页人工核对，亦没有 Microsoft Word 原生导出基准。PDF 页数属于本机 LibreOffice 结果，不能称为原始 Word 页数。

- 同济大学研究生学位论文写作参考指南：两条转换路径在 72 dpi 渲染下像素不同的物理页为 [1, 2, 3, 4, 6, 7, 8, 9, 10]；相同页数不保证相同版面。
- 同济大学研究生学位论文写作参考示例：两条转换路径在 72 dpi 渲染下像素不同的物理页为 [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24]；相同页数不保证相同版面。

## LibreOffice 故障处理与复现

有两个依次出现的启动阻碍：

1. 最初 `LD_LIBRARY_PATH` 将 `usr/lib/x86_64-linux-gnu` 放前面，使 UNO 从该目录尝试读取不存在的 `unorc`；调整为 LibreOffice `program` 在前后，ConfigItem 的 SIGSEGV 不再出现，转为配置异常。依据见 `lo-startup.strace` 与 `lo-order.strace`。
2. 仅解包 .deb 不会执行 postinst。`etc/libreoffice/registry` 缺少 main.xcd、writer.xcd 等配置；包内 `share/.registry` 已有这些文件。依据 libreoffice-common postinst 的 ucf 复制动作，将其复制到 audit 内的 etc 注册目录后启动和转换成功。原先 fundamentalrc 的本地绝对路径修复保留。

动态扫描确实发现 writerperfect、XML 安全、数据库等可选组件缺库，但没有额外补装：本任务的 DOC 导入、DOCX 和 PDF 导出已成功。javaldx 警告仍在日志中，并未阻止这些转换。

在当前目录复现：

```bash
python audit/convert-official.py
python audit/extract-word-layout.py
python audit/write-layout-report.py
```

转换器使用 audit/lo-profile-working2 独立配置；环境中 program 库目录在前。本次修复前 fundamentalrc 备份为 fundamentalrc.before-fix；最终文件已还原到该备份内容（试验性的额外 res 层未保留）。转换命令、返回码和输出见 conversion-log.json。

## 解析依据与产物

解析链：OLE → WordDocument FIB → 指定的 1Table → PlcfSed → SED.fcSepx → SEPX → SPRM。读取结构长度、边界和每个操作数，不进行字节模式搜索。文本标签从 CLX piece table 提取。JSON 保存原文件 SHA-256、CP 范围、SEPX 偏移/原始十六进制、全部 section SPRM、twips/mm、转换 XML、PDF 字体和页信息。

解析器面向这两份未加密 Word 97+ 文件，不是通用 Word 渲染器；未完整解释 DOP、页眉正文及修订节属性，不能用它推导实际物理分页。

- [微软 MS-DOC Section Properties](https://learn.microsoft.com/en-us/openspecs/office_file_formats/ms-doc/46c3ec54-53ff-4c0a-b0d6-07ad15d2546e)
- [微软 MS-DOC 分节结构示例](https://learn.microsoft.com/en-us/openspecs/office_file_formats/ms-doc/6777a859-d537-486b-96c7-fb0c959a5bf9)
- [LibreOffice 配置加载源码](https://github.com/LibreOffice/core/blob/libreoffice-7-3/configmgr/source/components.cxx)
- [完整结构化结果](word-layout.json)
- [原生提取脚本](extract-word-layout.py)
- [转换脚本](convert-official.py)
- [转换命令日志](conversion-log.json)

- [converted/同济大学研究生学位论文写作参考指南.docx](converted/同济大学研究生学位论文写作参考指南.docx)
- [converted/同济大学研究生学位论文写作参考指南.pdf](converted/同济大学研究生学位论文写作参考指南.pdf)
- [converted/docx-roundtrip/同济大学研究生学位论文写作参考指南.pdf](converted/docx-roundtrip/同济大学研究生学位论文写作参考指南.pdf)
- [converted/同济大学研究生学位论文写作参考示例.docx](converted/同济大学研究生学位论文写作参考示例.docx)
- [converted/同济大学研究生学位论文写作参考示例.pdf](converted/同济大学研究生学位论文写作参考示例.pdf)
- [converted/docx-roundtrip/同济大学研究生学位论文写作参考示例.pdf](converted/docx-roundtrip/同济大学研究生学位论文写作参考示例.pdf)
