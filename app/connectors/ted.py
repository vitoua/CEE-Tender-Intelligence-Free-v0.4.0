from datetime import datetime
import httpx
from app.models import Tender,Item
URL='https://api.ted.europa.eu/v3/notices/search';FIELDS=['publication-number','notice-title','buyer-name','buyer-country','total-value','total-value-cur','publication-date','deadline','classification-cpv','description-proc','description-lot','winner-name','contract-value','contract-value-cur','contract-conclusion-date']
def first(v,lang='eng'):
 if isinstance(v,dict):
  for k in (lang,'eng','pol','ukr','deu','fra'):
   if k in v:return first(v[k],lang)
  return first(next(iter(v.values()),''),lang)
 if isinstance(v,list):return first(v[0],lang) if v else ''
 return str(v or '')
def dt(v):
 try:return datetime.fromisoformat(first(v)[:10])
 except:return None
def num(v):
 try:return float(first(v))
 except:return None
async def fetch(limit=200):
 queries=['FT~"SSD" OR FT~"NVMe" OR FT~"DDR4" OR FT~"DDR5" OR FT~"memory card" OR FT~"flash drive"','classification-cpv IN (30233100 30233130 30234100 30236100 30237200)'];notices=[];err=''
 async with httpx.AsyncClient(timeout=45,follow_redirects=True,headers={'User-Agent':'CEE-Tender-Intelligence/0.4','Accept':'application/json'}) as c:
  for query in queries:
   r=await c.post(URL,json={'query':query,'fields':FIELDS,'page':1,'limit':min(limit,200),'scope':'ALL','checkQuerySyntax':False,'paginationMode':'PAGE_NUMBER','onlyLatestVersions':True})
   if r.status_code==200:notices=r.json().get('notices') or [];break
   err=f'HTTP {r.status_code}: {r.text[:700]}'
  else:raise RuntimeError('TED API: '+err)
 out=[]
 for x in notices:
  n=first(x.get('publication-number')) or first(x.get('notice-identifier'));cpvs=x.get('classification-cpv') or [];des=first(x.get('description-proc')) or first(x.get('description-lot'));w=first(x.get('winner-name'));status='awarded' if w else 'active'
  items=[Item(des or first(x.get('notice-title')),cpv=first(cpv)) for cpv in (cpvs if isinstance(cpvs,list) else [cpvs])] or [Item(des or first(x.get('notice-title')))]
  out.append(Tender('ted:'+n,'ted',first(x.get('buyer-country'))[:3] or 'EU',first(x.get('notice-title')) or n,first(x.get('buyer-name')),des,num(x.get('total-value')),first(x.get('total-value-cur')),dt(x.get('deadline')),dt(x.get('publication-date')),status,f'https://ted.europa.eu/en/notice/-/detail/{n}',items=items,winner=w,winner_value=num(x.get('contract-value')),award_date=dt(x.get('contract-conclusion-date'))))
 return out
