# usage: python3 -I crm_sync.py <crm_products_dir> <page_in.html> <page_out.html>
import json,glob,sys,re,datetime
crm_dir,src,dst=sys.argv[1:4]
H='mvr01lyl1swcz'
P={}
for f in glob.glob(crm_dir+'/*.json'):
    x=json.load(open(f,encoding='utf-8')); d=x.get('data',x)
    if d.get('companyId')==H: P[f.split('/')[-1][:-5]]=d
s=open(src,encoding='utf-8').read()
m=re.findall(r'/\*CRM-MAP-START\*/\s*const CRM_MAP = (\{.*?\});\s*/\*CRM-MAP-END\*/',s,flags=re.S)
assert len(m)==1,'CRM_MAP block not found'
MAP=json.loads(m[0])
def plural(n):
    a,b=n%10,n%100
    return 'цвет' if a==1 and b!=11 else ('цвета' if 2<=a<=4 and not 12<=b<=14 else 'цветов')
out={};miss=[]
for pid,r in MAP.items():
    e={}
    if 'doc' in r:
        d=P.get(r['doc'])
        if not d or not (d.get('price') or 0)>0: miss.append(pid); continue
        e={'p':int(d['price']),'q':max(0,int(d.get('stock') or 0))}
        if r.get('d'): e['d']=r['d']
    else:
        v=[dict(d,_id=i) for i,d in P.items() if d.get('category')==r['cat'] and (d.get('price') or 0)>0]
        big=[d for d in v if d['price']>=500]
        g=big or v
        if not g: miss.append(pid); continue
        w=re.search(r'(\d+(?:[.,]\d+)?\s?(?:кг|г))\b',g[0].get('name') or '')
        cols=[]
        for d in sorted(g,key=lambda d:(-(d.get('stock') or 0),d['_id'])):
            if (d.get('stock') or 0)>0:
                c=re.search(r'\(([^()]*(?:\([^()]*\))?[^()]*)\)\s*$',d.get('name') or '')
                c=(c.group(1) if c else d.get('name') or '').strip()
                if c and c not in cols: cols.append(c)
        e={'p':int(min(d['price'] for d in g)),'q':int(sum(max(0,d.get('stock') or 0) for d in g)),'cl':', '.join(cols)}
        parts=[r.get('dd') or '']+([w.group(1)] if w else [])+([str(len(cols))+' '+plural(len(cols))] if cols else [])
        e['d']=' · '.join(x for x in parts if x)
        ser=r['cat'].split(' / ',1)[-1]; vv=[]
        for d in sorted(v,key=lambda d:(-(d['price']>=500),-(d.get('stock') or 0),d['_id'])):
            n=d.get('name') or ''
            ww=re.search(r'(\d+(?:[.,]\d+)?\s?(?:кг|г))\b',n)
            cc=re.search(r'\(([^()]*(?:\([^()]*\))?[^()]*)\)\s*$',n)
            en=n[len(ser):] if n.startswith(ser) else n
            if ww and ww.group(1) in en: en=en[:en.find(ww.group(1))]
            en=en.strip()
            vv.append([d['_id'],(cc.group(1).strip() if cc else en),en,int(d['price']),max(0,int(d.get('stock') or 0)),ww.group(1) if ww else ''])
        e['v']=vv
    if r.get('n'): e['n']=r['n']
    out[pid]=e
old=re.findall(r'/\*CRM-SYNC-START\*/\s*const CRM = (\{.*?\});\s*const CRM_AT',s,flags=re.S)
assert len(old)==1,'CRM block not found'
oldc=json.loads(old[0])
at=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=6))).strftime('%d.%m.%Y %H:%M')
block='/*CRM-SYNC-START*/\nconst CRM = '+json.dumps(out,ensure_ascii=False)+';\nconst CRM_AT = "'+at+'";\n/*CRM-SYNC-END*/'
s,k=re.subn(r'/\*CRM-SYNC-START\*/.*?/\*CRM-SYNC-END\*/',lambda _:block,s,flags=re.S); assert k==1
open(dst,'w',encoding='utf-8').write(s)
print('CHANGED' if out!=oldc else 'SAME')
for pid in sorted(set(out)|set(oldc)):
    a,b=oldc.get(pid),out.get(pid)
    if a!=b: print(pid,'|',(a or {}).get('p'),(a or {}).get('q'),'->',(b or {}).get('p'),(b or {}).get('q'))
print('MISSING',miss)
