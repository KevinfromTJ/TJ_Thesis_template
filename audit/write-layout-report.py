from pathlib import Path
import json, hashlib
import pymupdf
A=Path(__file__).resolve().parent
j=json.loads((A/'word-layout.json').read_text())
lines=['# official_ref_2510 原始 Word 分节页面设置核对','', '完成日期：2026-11-11。仅写入 audit；未修改 template 或原始 .doc。未使用 sudo、付费软件或在线文档转换服务。','', '## 原始值汇总','', '以下来自原始 OLE 二进制，而非文档正文中的写作要求或 LibreOffice 转换结果。单位 mm（括号内为原始 twips）；1 inch = 1440 twips。页眉/页脚距离分别从纸张顶边/底边计算，不是正文与页眉/页脚之间的空隙。','', '| 文件与节 | 上 | 下 | 左 | 右 | 页眉 | 页脚 |','|---|---:|---:|---:|---:|---:|---:|']
for doc in j['documents']:
 groups={}
 for sec in doc['sections']:
  vals=tuple(sec['layout'][k]['twips'] for k in ('top','bottom','left','right','header','footer'));groups.setdefault(vals,[]).append(sec['index'])
 for vals,ids in groups.items():
  title='指南' if '指南' in doc['source'] else '示例'; label=str(ids[0]) if len(ids)==1 else f'{ids[0]}–{ids[-1]}'
  lines.append('| '+title+' 第'+label+'节 | '+' | '.join(f'{v*25.4/1440:.3f} ({v})' for v in vals)+' |')
lines+=['','两份文件所有节纸张均为 11906 × 16838 twips，约 210.009 × 297.004 mm（A4），装订线均为 0。所有目标几何参数均有显式 SPRM，不需要猜测默认值。','', '## 每节定位','', 'CP 是主文档文本字符位置，不是页码。摘要含域代码时保留其部分文字；表格、文本框可能影响阅读顺序。']
for doc in j['documents']:
 lines+=['',f"### {Path(doc['source']).name}",'',f"SHA-256：`{doc['sha256']}`。原生节数：{doc['section_count']}。",'', '| 节 | CP 范围（左闭右开） | 起始文本 | SEPX 字节偏移 |','|---|---|---|---|']
 for sec in doc['sections']:
  lines.append(f"| {sec['index']} | [{sec['cp_start']}, {sec['cp_end_exclusive']}) | {sec['text_start'][:55].replace('|','/')} | {sec['sepx_offset']} |")
lines+=['','## 转换产物与差异','', 'LibreOffice 7.3.7 已成功生成两份 DOCX 和两份直接从 DOC 导出的 PDF；另生成两份 DOCX 再导出 PDF，便于往返核对。产物没有手工改写页边距或修补节数。','', '| 文件 | 原生节数 | 转换 DOCX 节数 | DOC→PDF 页数 | DOCX→PDF 页数 |','|---|---:|---:|---:|---:|']
for doc in j['documents']:
 lines.append(f"| {Path(doc['source']).stem} | {doc['section_count']} | {doc['libreoffice_docx']['section_count']} | {doc['libreoffice_pdf']['page_count']} | {doc['docx_roundtrip_pdf']['page_count']} |")
 p=A.parent/doc['libreoffice_pdf']['path'];q=A.parent/doc['docx_roundtrip_pdf']['path']; d=pymupdf.open(p);e=pymupdf.open(q)
 changed=[]
 for idx in range(min(len(d),len(e))):
  if d[idx].get_pixmap().samples!=e[idx].get_pixmap().samples: changed.append(idx+1)
 doc['pdf_roundtrip_visual_check']={'renderer':'PyMuPDF, default matrix (72 dpi), RGB','changed_physical_pages':changed,'equal_page_count':len(d)==len(e),'caveat':'Checks two LibreOffice outputs, not Microsoft Word fidelity.'}
lines+=['', '- 指南 3 节的 DOCX `header` 均变为 0；原生为 851 twips（15.011 mm）。DOCX 未写入页眉引用，这与未启用页眉的导出处理相符；不能据此说原生页眉距离为 0。其余目标几何值一致。','- 示例前两节的 DOCX `footer` 均变为 0；原生为 1134 twips（20.003 mm）。这两节 DOCX 未写入页脚引用。','- 示例原生 14 节，DOCX 含 15 个 `sectPr`，其中第 13 个标为 continuous；因此不能将全部转换节与原生节逐一按序等同。所有转换节的纸张与四边距均与原生一致，转换第 3–15 节页眉/页脚为 1134/850 twips。JSON 的同序差值只是机械对照，不代表已经完成文本边界对齐。','- 原文要求的宋体、黑体、仿宋等在导出 PDF 中出现 NotoSansCJKjp、WenQuanYiZenHei 等替代字体。字体和 LibreOffice 排版可能改变换行、页数、表格、公式、文本框与浮动对象位置。','- 已查看两份 PDF 首页，正文/封面能正常显示；未逐页人工核对，亦没有 Microsoft Word 原生导出基准。PDF 页数属于本机 LibreOffice 结果，不能称为原始 Word 页数。','']
for doc in j['documents']:
 lines.append(f"- {Path(doc['source']).stem}：两条转换路径在 72 dpi 渲染下像素不同的物理页为 {doc['pdf_roundtrip_visual_check']['changed_physical_pages']}；相同页数不保证相同版面。")
lines+=['','## LibreOffice 故障处理与复现','', '有两个依次出现的启动阻碍：','', '1. 最初 `LD_LIBRARY_PATH` 将 `usr/lib/x86_64-linux-gnu` 放前面，使 UNO 从该目录尝试读取不存在的 `unorc`；调整为 LibreOffice `program` 在前后，ConfigItem 的 SIGSEGV 不再出现，转为配置异常。依据见 `lo-startup.strace` 与 `lo-order.strace`。','2. 仅解包 .deb 不会执行 postinst。`etc/libreoffice/registry` 缺少 main.xcd、writer.xcd 等配置；包内 `share/.registry` 已有这些文件。依据 libreoffice-common postinst 的 ucf 复制动作，将其复制到 audit 内的 etc 注册目录后启动和转换成功。原先 fundamentalrc 的本地绝对路径修复保留。','', '动态扫描确实发现 writerperfect、XML 安全、数据库等可选组件缺库，但没有额外补装：本任务的 DOC 导入、DOCX 和 PDF 导出已成功。javaldx 警告仍在日志中，并未阻止这些转换。','', '在当前目录复现：','', '```bash','python audit/convert-official.py','python audit/extract-word-layout.py','python audit/write-layout-report.py','```','', '转换器使用 audit/lo-profile-working2 独立配置；环境中 program 库目录在前。本次修复前 fundamentalrc 备份为 fundamentalrc.before-fix；最终文件已还原到该备份内容（试验性的额外 res 层未保留）。转换命令、返回码和输出见 conversion-log.json。','', '## 解析依据与产物','', '解析链：OLE → WordDocument FIB → 指定的 1Table → PlcfSed → SED.fcSepx → SEPX → SPRM。读取结构长度、边界和每个操作数，不进行字节模式搜索。文本标签从 CLX piece table 提取。JSON 保存原文件 SHA-256、CP 范围、SEPX 偏移/原始十六进制、全部 section SPRM、twips/mm、转换 XML、PDF 字体和页信息。','', '解析器面向这两份未加密 Word 97+ 文件，不是通用 Word 渲染器；未完整解释 DOP、页眉正文及修订节属性，不能用它推导实际物理分页。','', '- [微软 MS-DOC Section Properties](https://learn.microsoft.com/en-us/openspecs/office_file_formats/ms-doc/46c3ec54-53ff-4c0a-b0d6-07ad15d2546e)','- [微软 MS-DOC 分节结构示例](https://learn.microsoft.com/en-us/openspecs/office_file_formats/ms-doc/6777a859-d537-486b-96c7-fb0c959a5bf9)','- [LibreOffice 配置加载源码](https://github.com/LibreOffice/core/blob/libreoffice-7-3/configmgr/source/components.cxx)','- [完整结构化结果](word-layout.json)','- [原生提取脚本](extract-word-layout.py)','- [转换脚本](convert-official.py)','- [转换命令日志](conversion-log.json)','']
for doc in j['documents']:
 for key in ('libreoffice_docx','libreoffice_pdf','docx_roundtrip_pdf'):
  path=Path(doc[key]['path']).relative_to('audit');lines.append(f'- [{path}]({path})')
(A/'word-layout.json').write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n')
(A/'word-layout-report.md').write_text('\n'.join(lines)+'\n')
print('Report saved; pixel differences:',[(Path(d['source']).name,d['pdf_roundtrip_visual_check']['changed_physical_pages']) for d in j['documents']])
