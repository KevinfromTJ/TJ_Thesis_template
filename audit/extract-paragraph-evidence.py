from pathlib import Path
import olefile,struct,json,re,zipfile
from lxml import etree
from docx import Document
import pymupdf
A=Path(__file__).resolve().parent; base=A.parent
u16=lambda b,o:struct.unpack_from('<H',b,o)[0]
u32=lambda b,o:struct.unpack_from('<I',b,o)[0]
def sprms(g):
 out=[];j=0
 while j+2<=len(g):
  op=u16(g,j);j+=2
  if op==0 and all(x==0 for x in g[j:]):break
  n=[1,1,2,4,2,2,None,3][op>>13]
  if n is None:
   if op==0xd608: n=u16(g,j)-1;j+=2
   else:n=g[j];j+=1
  if j+n>len(g):out.append({'error':'operand overrun','opcode':hex(op)});break
  raw=g[j:j+n];j+=n;r={'opcode':hex(op),'operand_hex':raw.hex()}
  if op==0x6412:
   a,b=struct.unpack('<hh',raw);r.update(name='sprmPDyaLine',dyaLine=a,fMultLinespace=b,multiple=a/240 if b else None,points=a/20 if not b else None)
  if op in (0xa413,0xa414):r.update(name={0xa413:'sprmPDyaBefore',0xa414:'sprmPDyaAfter'}[op],points=int.from_bytes(raw,'little')/20)
  if op==0x4a43:r.update(name='sprmCHps',points=int.from_bytes(raw,'little')/2)
  out.append(r)
 return out
p=next((base/'official_ref_2510').glob('*示例.doc'));o=olefile.OleFileIO(p);w=o.openstream('WordDocument').read();t=o.openstream('1Table').read();pos=32;pos+=2+2*u16(w,pos);pos+=2+4*u16(w,pos);count=u16(w,pos);pos+=2;pairs=[struct.unpack_from('<II',w,pos+8*i) for i in range(count)]
fc,sz=pairs[33];clx=t[fc:fc+sz];pos=0
while clx[pos]==1:pos+=3+u16(clx,pos+1)
assert clx[pos]==2
sz=u32(clx,pos+1);plc=clx[pos+5:pos+5+sz];n=(sz-4)//12;pieces=[]
for i in range(n):
 a,b=u32(plc,4*i),u32(plc,4*i+4);off=u32(plc,4*(n+1)+8*i+2);comp=bool(off&0x40000000);off&=0x3fffffff
 if comp:off//=2
 text=w[off:off+(b-a)*(1 if comp else 2)].decode('cp1252' if comp else 'utf-16le',errors='replace')
 pieces.append({'cp_start':a,'cp_end':b,'fc_start':off,'step':1 if comp else 2,'text':text,'prm':u16(plc,4*(n+1)+8*i+6)})
def fc_text(a,b):
 out=[]
 for p in pieces:
  x=max(a,p['fc_start']);y=min(b,p['fc_start']+len(p['text'])*p['step'])
  if x<y:out.append((p['cp_start']+(x-p['fc_start'])//p['step'],p['text'][(x-p['fc_start'])//p['step']:(y-p['fc_start'])//p['step']],p['prm']))
 return sorted(out)
native=[]
for kind,idx in [('PAPX',13),('CHPX',12)]:
 fc,sz=pairs[idx];bt=t[fc:fc+sz];n=(sz-4)//8
 for i in range(n):
  pg=u32(bt,4*(n+1)+i*4)*512;f=w[pg:pg+512];nr=f[511]
  for k in range(nr):
   a,b=u32(f,k*4),u32(f,k*4+4);texts=fc_text(a,b)
   if not texts:continue
   text=''.join(x[1] for x in texts);cp=texts[0][0]
   if cp>=u32(w,76):continue
   if not (5964<=cp<u32(w,76) or (kind=='PAPX' and any(x in text for x in ['第1章','第3章','第7章','摘要','参考文献','致谢']))):continue
   off=f[4*(nr+1)+(13*k if kind=='PAPX' else k)]*2
   if not off:continue
   if kind=='PAPX':
    cb=f[off]
    if cb: raw=f[off+1:off+1+2*cb-1]
    else:raw=f[off+2:off+2+2*f[off+1]]
    istd=u16(raw,0);g=raw[2:]
   else:istd=None;g=f[off+1:off+1+f[off]]
   native.append({'kind':kind,'cp_start':cp,'text':text[:300],'fc_range':[a,b],'fkp_offset':pg,'property_offset':pg+off,'style_index':istd,'piece_prms':sorted(set(x[2] for x in texts)),'sprms':sprms(g),'raw_hex':g.hex()})
# DOCX: apply docDefaults -> paragraph style ancestry -> direct properties.
docpath=next((A/'converted').glob('*示例.docx'));doc=Document(docpath);ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'};W='{'+ns['w']+'}'
with zipfile.ZipFile(docpath) as z: styles=etree.fromstring(z.read('word/styles.xml'))
def props(el):
 return {} if el is None else {etree.QName(ch).localname:{etree.QName(k).localname:v for k,v in ch.attrib.items()} for ch in el}
def merge(d,p):
 for k,v in p.items():d.setdefault(k,{}).update(v)
 return d
paras=[]
for i,p in enumerate(doc.paragraphs):
 if not (218<=i<=242 or i in [114,135,152,167,174,185]):continue
 chain=[];sty=p.style or doc.styles['Normal']
 while sty is not None:chain.append(sty);sty=sty.base_style
 pp=props(styles.find('w:docDefaults/w:pPrDefault/w:pPr',ns));rp=props(styles.find('w:docDefaults/w:rPrDefault/w:rPr',ns))
 for sty in reversed(chain):merge(pp,props(sty.element.find(W+'pPr')));merge(rp,props(sty.element.find(W+'rPr')))
 merge(pp,props(p._p.find(W+'pPr')))
 runs=[]
 for run in p.runs:
  rr={k:dict(v) for k,v in rp.items()};merge(rr,props(run._r.find(W+'rPr')))
  if run.text:runs.append({'text':run.text,'properties':rr,'size_pt':int(rr['sz']['val'])/2 if 'sz'in rr else None})
 paras.append({'paragraph_index_0based':i,'text':p.text,'style':p.style.style_id if p.style else 'Normal (fallback)','effective_pPr':pp,'direct_pPr_xml':etree.tostring(p._p.find(W+'pPr'),encoding='unicode') if p._p.find(W+'pPr') is not None else None,'runs':runs})
pdf=pymupdf.open(next((A/'converted').glob('*示例.pdf')));foot=[];decl=[]
for i,page in enumerate(pdf):
 spans=[s for b in page.get_text('dict')['blocks'] if 'lines'in b for l in b['lines'] for s in l['spans']]
 foot.extend({'physical_page':i+1,'text':s['text'],'size_pt':s['size'],'baseline_from_bottom_mm':(page.rect.height-s['origin'][1])*25.4/72,'bbox_bottom_from_bottom_mm':(page.rect.height-s['bbox'][3])*25.4/72} for s in spans if s['origin'][1]>page.rect.height-55 and re.fullmatch('[0-9IVX]+',s['text']))
 if i>=22:decl.append({'physical_page':i+1,'spans':spans})
result={'native_direct_formatting':native,'native_limitations':'Direct FKP SPRMs only; no binary STSH inheritance or nonzero piece PRM expansion. Missing values are not defaults. Full CHPX inheritance not resolved.','docx_paragraphs':paras,'docx_limitations':'LibreOffice conversion evidence. Resolved docDefaults and paragraph styles plus direct properties; character styles/toggles not fully resolved. Paragraph mark rPr does not determine all run sizes.','pdf_footer_measurements':foot,'pdf_declaration_pages':decl}
(A/'paragraph-evidence.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
for r in native:
 if r['kind']=='PAPX':print('NATIVE',r['cp_start'],repr(r['text'][:40]),[x for x in r['sprms'] if 'name'in x], 'PRM',r['piece_prms'])
for p in paras:print('DOCX',p['paragraph_index_0based'],repr(p['text'][:40]),p['effective_pPr'].get('spacing'),sorted(set(r['size_pt'] for r in p['runs'] if r['size_pt'])))
