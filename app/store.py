from datetime import datetime
from app.matching import match
class Store:
 def __init__(self): self.tenders={}; self.runs=[]
 def ingest(self,source,rows):
  relevant=0
  for t in rows:
   t.category,t.score,hits=match(' '.join([t.title,t.description]+[i.description for i in t.items]))
   for i in t.items:i.matched_terms=hits
   self.tenders[t.id]=t; relevant+=int(t.score>=25)
  self.runs.insert(0,{'source':source,'status':'ok','fetched':len(rows),'relevant':relevant,'at':datetime.utcnow(),'error':''});self.runs=self.runs[:8];return len(rows),relevant
 def error(self,source,e):self.runs.insert(0,{'source':source,'status':'error','fetched':0,'relevant':0,'at':datetime.utcnow(),'error':f'{type(e).__name__}: {e}'})
 def countries(self):return sorted({x.country for x in self.tenders.values() if x.country})
store=Store()
