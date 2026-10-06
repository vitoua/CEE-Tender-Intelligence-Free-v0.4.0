from io import BytesIO
from datetime import datetime,date
from urllib.parse import unquote
from fastapi import FastAPI,Form,HTTPException,Request
from fastapi.responses import HTMLResponse,RedirectResponse,StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from itsdangerous import URLSafeSerializer,BadSignature
from openpyxl import Workbook
from app.config import settings
from app.i18n import tr
from app.store import store
from app.status import is_active
from app.translation import localized_tender
from app.analytics import winner_rows
app=FastAPI(title='CEE Tender Intelligence Free',version='0.4.0');app.mount('/static',StaticFiles(directory='app/static'),name='static');tpl=Jinja2Templates(directory='app/templates');signer=URLSafeSerializer(settings.secret_key,'session')
def lang(r):return r.cookies.get('lang') or settings.app_language
def logged(r):
 try:return signer.loads(r.cookies.get('session',''))=='admin'
 except BadSignature:return False
def require(r):
 if not logged(r):raise HTTPException(401)
@app.get('/health')
def health():return {'status':'ok','version':'0.4.0','storage':'memory','tenders':len(store.tenders)}
@app.get('/lang/{code}')
def set_lang(code:str,request:Request):
 if code not in ('uk','pl','en'):code='uk'
 r=RedirectResponse(request.headers.get('referer') or '/',303);r.set_cookie('lang',code,samesite='lax');return r
@app.get('/login',response_class=HTMLResponse)
def login_page(request:Request):return tpl.TemplateResponse('login.html',{'request':request,'t':tr(lang(request))})
@app.post('/login')
def login(email:str=Form(),password:str=Form()):
 if email!=settings.admin_email or password!=settings.admin_password:return HTMLResponse('Invalid credentials',400)
 r=RedirectResponse('/',303);r.set_cookie('session',signer.dumps('admin'),httponly=True,secure=True,samesite='lax');return r
@app.get('/logout')
def logout():r=RedirectResponse('/login',303);r.delete_cookie('session');return r
@app.get('/',response_class=HTMLResponse)
def index(request:Request,country:str='',category:str='',min_score:int=0,q:str='',active_only:int=1):
 if not logged(request):return RedirectResponse('/login',303)
 rows=list(store.tenders.values())
 if active_only:rows=[x for x in rows if is_active(x)]
 if country:rows=[x for x in rows if x.country.lower()==country.lower()]
 if category:rows=[x for x in rows if x.category==category]
 if q:rows=[x for x in rows if q.lower() in ' '.join([x.title,x.buyer,x.description]+[i.description for i in x.items]).lower()]
 rows=[x for x in rows if x.score>=min_score];rows.sort(key=lambda x:x.deadline or datetime.max)
 return tpl.TemplateResponse('index.html',{'request':request,'rows':rows[:settings.cache_limit],'runs':store.runs,'countries':store.countries(),'country':country,'category':category,'min_score':min_score,'q':q,'active_only':active_only,'t':tr(lang(request))})
@app.get('/tenders/{tid:path}',response_class=HTMLResponse)
def detail(tid:str,request:Request):
 require(request);x=store.tenders.get(tid)
 if not x:raise HTTPException(404)
 return tpl.TemplateResponse('detail.html',{'request':request,'x':x,'view':localized_tender(x,lang(request)),'t':tr(lang(request))})
@app.get('/analytics',response_class=HTMLResponse)
def analytics(request:Request,countries:list[str]|None=None,categories:list[str]|None=None,date_from:str='',date_to:str=''):
 require(request);df=date.fromisoformat(date_from) if date_from else None;dt=date.fromisoformat(date_to) if date_to else None;rows=winner_rows(store.tenders.values(),countries,df,dt,categories)
 return tpl.TemplateResponse('analytics.html',{'request':request,'rows':rows,'countries':store.countries(),'selected_countries':countries or [],'selected_categories':categories or [],'date_from':date_from,'date_to':date_to,'t':tr(lang(request))})
@app.get('/suppliers/{name:path}',response_class=HTMLResponse)
def supplier(name:str,request:Request):
 require(request);name=unquote(name);rows=winner_rows(store.tenders.values());row=next((r for r in rows if r['winner']==name),None)
 if not row:raise HTTPException(404)
 return tpl.TemplateResponse('supplier.html',{'request':request,'name':name,'row':row,'t':tr(lang(request))})
@app.post('/refresh/{source}')
async def refresh(source:str,request:Request):
 require(request)
 try:
  if source=='prozorro':from app.connectors.prozorro import fetch
  elif source=='ted':from app.connectors.ted import fetch
  else:raise HTTPException(404)
  store.ingest(source,await fetch())
 except Exception as e:store.error(source,e)
 return RedirectResponse('/',303)
@app.get('/export.xlsx')
def export(request:Request):
 require(request);rows=list(store.tenders.values());wb=Workbook();ws=wb.active;ws.title='Tenders';ws.append(['ID','Source','Country','Title','Buyer','Value','Currency','Deadline','Category','Score','Status','Winner','Winner value','Award date','URL'])
 for x in rows:ws.append([x.id,x.source,x.country,x.title,x.buyer,x.value,x.currency,x.deadline,x.category,x.score,x.status,x.winner,x.winner_value,x.award_date,x.source_url])
 wa=wb.create_sheet('Winner analytics');wa.append(['Winner','Wins','Total value','Average','Largest','Market share %','Countries'])
 for r in winner_rows(rows):wa.append([r['winner'],r['wins'],r['total'],r['avg'],r['largest'],r['share'],', '.join(sorted(r['countries']))])
 b=BytesIO();wb.save(b);b.seek(0);return StreamingResponse(b,media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',headers={'Content-Disposition':'attachment; filename=tenders-v0.4.xlsx'})
