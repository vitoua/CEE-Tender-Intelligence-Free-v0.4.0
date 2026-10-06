from collections import defaultdict
from app.status import is_closed
def winner_rows(tenders,countries=None,date_from=None,date_to=None,categories=None):
    countries=set(countries or []); categories=set(categories or []); groups=defaultdict(lambda:{'wins':0,'total':0.0,'largest':0.0,'countries':set(),'buyers':set(),'months':defaultdict(int)})
    for x in tenders:
        d=x.award_date or x.published_at or x.deadline
        if not is_closed(x) or not x.winner:continue
        if countries and x.country not in countries:continue
        if categories and x.category not in categories:continue
        if date_from and (not d or d.date()<date_from):continue
        if date_to and (not d or d.date()>date_to):continue
        v=x.winner_value if x.winner_value is not None else (x.value or 0); g=groups[x.winner];g['wins']+=1;g['total']+=v;g['largest']=max(g['largest'],v);g['countries'].add(x.country);g['buyers'].add(x.buyer)
        if d:g['months'][d.strftime('%Y-%m')]+=1
    total=sum(g['total'] for g in groups.values())
    out=[]
    for name,g in groups.items():out.append({'winner':name,**g,'avg':g['total']/g['wins'],'share':(g['total']/total*100 if total else 0)})
    return sorted(out,key=lambda r:(r['wins'],r['total']),reverse=True)
