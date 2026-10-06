from datetime import datetime
from urllib.parse import urljoin
import httpx
from app.models import Tender,Item
BASE='https://public-api.prozorro.gov.ua/api/2.5/tenders'
def dt(v):
 try:return datetime.fromisoformat(str(v).replace('Z','+00:00')).replace(tzinfo=None)
 except:return None
def winner(x):
 awards=[a for a in x.get('awards',[]) if a.get('status')=='active']
 if not awards:return '',None,None
 a=awards[0]; suppliers=a.get('suppliers') or []; name=(suppliers[0].get('name') if suppliers else '') or ''; value=(a.get('value') or {}).get('amount'); return name,value,dt(a.get('date'))
async def fetch(limit=300):
 out=[];seen=set();url=BASE;params={'limit':100,'descending':1}
 async with httpx.AsyncClient(timeout=40,follow_redirects=True,headers={'User-Agent':'CEE-Tender-Intelligence/0.4'}) as c:
  while url and len(seen)<limit:
   r=await c.get(url,params=params);r.raise_for_status();body=r.json();params=None
   for row in body.get('data',[]):
    rid=row.get('id')
    if not rid or rid in seen:continue
    seen.add(rid); rr=await c.get(f'{BASE}/{rid}');rr.raise_for_status();x=rr.json().get('data',{});v=x.get('value') or {};p=x.get('tenderPeriod') or {};e=x.get('procuringEntity') or {};tid=x.get('tenderID',rid);w,wv,wd=winner(x)
    items=[Item(i.get('description',''),i.get('quantity'),(i.get('unit') or {}).get('name'),(i.get('classification') or {}).get('id')) for i in x.get('items',[])]
    out.append(Tender('prozorro:'+tid,'prozorro','UKR',x.get('title') or x.get('title_en') or tid,e.get('name',''),x.get('description',''),v.get('amount'),v.get('currency'),dt(p.get('endDate')),dt(x.get('dateCreated')),x.get('status',''),f'https://prozorro.gov.ua/tender/{tid}',items=items,winner=w,winner_value=wv,award_date=wd))
    if len(seen)>=limit:break
   nxt=(body.get('next_page') or {}).get('uri');url=urljoin(BASE,nxt) if nxt else None
 return out
