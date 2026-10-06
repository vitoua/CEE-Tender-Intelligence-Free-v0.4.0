import re
LABELS={'uk':{'active':'Активний','complete':'Завершений','completed':'Завершений','awarded':'Присуджено','buyer':'Замовник'},'pl':{'active':'Aktywny','complete':'Zakonczony','completed':'Zakonczony','awarded':'Udzielono','buyer':'Zamawiajacy'},'en':{'active':'Active','complete':'Completed','completed':'Completed','awarded':'Awarded','buyer':'Buyer'}}
def clean(v): return re.sub(r'\s+',' ',str(v or '')).strip()
def localize_status(v,lang): return LABELS.get(lang,LABELS['uk']).get((v or '').lower(),clean(v))
def localized_tender(t,lang):
    # Source text is preserved. Known status labels are localized; multilingual TED fields are selected in the connector.
    return {'title':clean(t.title),'buyer':clean(t.buyer),'description':clean(t.description),'status':localize_status(t.status,lang),'items':[clean(i.description) for i in t.items]}
