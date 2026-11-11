"""Read Word 97+ FIB/PlcfSed/SEPX directly, compare LO DOCX and PDFs.
Only targeted section properties are interpreted; all SPRMs retained for audit.
"""
from pathlib import Path
import struct, json, hashlib, re, zipfile
from lxml import etree
import olefile, pymupdf as fitz
BASE=Path(__file__).resolve().parent.parent
AUDIT=BASE/'audit'
def u16(b,o): return struct.unpack_from('<H',b,o)[0]
def u32(b,o): return struct.unpack_from('<I',b,o)[0]
PROPS={0xB01F:('width','sprmSXaPage'),0xB020:('height','sprmSYaPage'),0xB021:('left','sprmSDxaLeft'),0xB022:('right','sprmSDxaRight'),0x9023:('top','sprmSDyaTop'),0x9024:('bottom','sprmSDyaBottom'),0xB025:('gutter','sprmSDzaGutter'),0xB017:('header','sprmSDyaHdrTop'),0xB018:('footer','sprmSDyaHdrBottom')}
OTHER={0x3009:('break_type',2),0x300A:('different_first_page',0),0x301D:('orientation',0),0x500B:('columns_minus_one',0),0x3011:('page_number_restart',0),0x300E:('page_number_format',0)}
NS={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
def text_pieces(w,t,pairs):
 fc,sz=pairs[33]; clx=t[fc:fc+sz]; pos=0
 while clx[pos]==1: pos+=3+u16(clx,pos+1)
 assert clx[pos]==2
 size=u32(clx,pos+1); plc=clx[pos+5:pos+5+size]; n=(size-4)//12
 out=[]
 for i in range(n):
  a,b=u32(plc,i*4),u32(plc,(i+1)*4); raw=u32(plc,4*(n+1)+8*i+2); compressed=bool(raw&0x40000000); off=raw&0x3fffffff
  if compressed: out.append(w[off//2:off//2+b-a].decode('cp1252',errors='replace'))
  else: out.append(w[off:off+2*(b-a)].decode('utf-16le',errors='replace'))
 return ''.join(out)
def extract(path):
 o=olefile.OleFileIO(path); w=o.openstream('WordDocument').read(); assert u16(w,0)==0xa5ec
 flags=u16(w,10); assert not flags&0x100,'Encrypted document unsupported'
 table='1Table' if flags&0x200 else '0Table'; t=o.openstream(table).read()
 pos=32; pos+=2+2*u16(w,pos); pos+=2+4*u16(w,pos); count=u16(w,pos); pos+=2
 pairs=[struct.unpack_from('<II',w,pos+8*i) for i in range(count)]
 fc,sz=pairs[6]; assert (sz-4)%16==0; n=(sz-4)//16
 cps=[u32(t,fc+4*i) for i in range(n+1)]; assert cps==sorted(cps)
 txt=text_pieces(w,t,pairs)
 result={'source':str(path.relative_to(BASE)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'fib_version':u16(w,2),'table_stream':table,'plcf_sed_offset':fc,'plcf_sed_bytes':sz,'main_story_ccpText':u32(w,76),'section_count':n,'sections':[]}
 for i in range(n):
  off=u32(t,fc+4*(n+1)+12*i+2); size=0 if off==0xffffffff else u16(w,off); grp=b'' if size==0 else w[off+2:off+2+size]; assert len(grp)==size
  sec={'index':i+1,'cp_start':cps[i],'cp_end_exclusive':min(cps[i+1],u32(w,76)), 'plcf_cp_end_raw':cps[i+1],'text_start':re.sub(r'[\x00-\x1f]+',' ',txt[cps[i]:min(cps[i+1],u32(w,76))]).strip()[:110],'sepx_offset':off,'sepx_bytes':size,'sepx_hex':grp.hex(),'layout':{},'other':{},'sprms':[]}; j=0
  while j<len(grp):
   start=j; op=u16(grp,j);j+=2; spra=op>>13; sizeop=[1,1,2,4,2,2,None,3][spra]
   if sizeop is None: sizeop=grp[j]; j+=1
   operand=grp[j:j+sizeop]; assert len(operand)==sizeop;j+=sizeop
   item={'opcode':f'0x{op:04X}','operand_hex':operand.hex(),'word_document_offset':off+2+start}
   if op in PROPS:
    key,name=PROPS[op]; value=int.from_bytes(operand,'little',signed=op in (0x9023,0x9024)); item['name']=name
    sec['layout'][key]={'twips':value,'mm':round(value*25.4/1440,6),'source':'explicit SEPX','sprm':name,'word_document_offset':item['word_document_offset']}
   elif op in OTHER: sec['other'][OTHER[op][0]]={'value':int.from_bytes(operand,'little'),'source':'explicit SEPX'}
   sec['sprms'].append(item)
  for key,_ in PROPS.values():
   if key not in sec['layout']: sec['layout'][key]={'twips':None,'mm':None,'source':'not stored; implementation/locale default not inferred'}
  for key,default in OTHER.values(): sec['other'].setdefault(key,{'value':default,'source':'MS-DOC default'})
  result['sections'].append(sec)
 o.close(); return result

def converted(path,raw):
 with zipfile.ZipFile(path) as z:
  root=etree.fromstring(z.read('word/document.xml')); settings=etree.fromstring(z.read('word/settings.xml'))
  fonts=etree.fromstring(z.read('word/fontTable.xml'))
  sections=[]
  for i,s in enumerate(root.findall('.//w:sectPr',NS)):
   layout={}
   for tag in ('pgSz','pgMar'):
    el=s.find('w:'+tag,NS)
    if el is not None:
     for k,v in el.attrib.items():
      key=etree.QName(k).localname; key={'w':'width','h':'height'}.get(key,key)
      if key in [x[0] for x in PROPS.values()]: layout[key]=int(v)
   orig=raw['sections'][i]['layout'] if i<len(raw['sections']) else {}
   delta={key:val-orig[key]['twips'] for key,val in layout.items() if key in orig and orig[key]['twips'] is not None and val!=orig[key]['twips']}
   sections.append({'index':i+1,'layout_twips':layout,'comparison_status': 'same-index only; not section identity alignment' if len(root.findall('.//w:sectPr',NS)) != raw['section_count'] else 'same-index comparison', 'differences_from_same_index_native_twips':delta,'xml':etree.tostring(s,encoding='unicode')})
  return {'path':str(path.relative_to(BASE)),'section_count':len(sections),'index_comparison_caveat':'Comparison by section order; matching counts alone do not prove identical pagination.','sections':sections,'requested_fonts':[x.get('{'+NS['w']+'}name') for x in fonts],'even_and_odd_headers':settings.find('w:evenAndOddHeaders',NS) is not None,'mirror_margins':settings.find('w:mirrorMargins',NS) is not None}
def pdf_info(path):
 d=fitz.open(path)
 return {'path':str(path.relative_to(BASE)),'page_count':len(d),'page_sizes_pt':sorted(set((round(p.rect.width,3),round(p.rect.height,3)) for p in d)),'pages':[{'number':i+1,'text_start':re.sub(r'\s+',' ',p.get_text()).strip()[:100]} for i,p in enumerate(d)],'fonts':sorted(set(f[3] for p in d for f in p.get_fonts()))}
results=[]
for p in sorted((BASE/'official_ref_2510').glob('*.doc')):
 r=extract(p); q=AUDIT/'converted'/p.with_suffix('.docx').name
 if q.exists(): r['libreoffice_docx']=converted(q,r)
 for key,folder in [('libreoffice_pdf','converted'),('docx_roundtrip_pdf','converted/docx-roundtrip')]:
  q=AUDIT/folder/p.with_suffix('.pdf').name
  if q.exists(): r[key]=pdf_info(q)
 results.append(r)
output={'method':'Native OLE WordDocument + selected Table stream; FIB -> PlcfSed -> SED -> SEPX -> SPRMs. Converted files are separate evidence.','units':'1 inch = 1440 twips; mm = twips * 25.4 / 1440','references':['https://learn.microsoft.com/en-us/openspecs/office_file_formats/ms-doc/46c3ec54-53ff-4c0a-b0d6-07ad15d2546e','https://learn.microsoft.com/en-us/openspecs/office_file_formats/ms-doc/6777a859-d537-486b-96c7-fb0c959a5bf9'],'limitations':['Not a Microsoft Word rendering. Native CP positions are not physical page numbers.','No full DOP/header/footer text or tracked section-revision semantics interpretation. Raw section SPRMs retained.','Unstored locale-dependent geometry is left unknown, not guessed. All requested geometry in these two files is explicitly stored.','Negative top/bottom margins, if any, need MS-DOC fixed-margin interpretation.','PDF pagination depends on installed fonts and LibreOffice import/layout.'], 'documents':results}
(AUDIT/'word-layout.json').write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n')
for r in results:
 print(r['source'],r['section_count'])
 for s in r['sections']: print(s['index'],s['text_start'][:35],{k:v['twips'] for k,v in s['layout'].items()})
 if 'libreoffice_docx' in r: print('DOCX',r['libreoffice_docx']['section_count'],[s['differences_from_same_index_native_twips'] for s in r['libreoffice_docx']['sections']])
 for key in ('libreoffice_pdf','docx_roundtrip_pdf'):
  if key in r: print(key,r[key]['page_count'])
