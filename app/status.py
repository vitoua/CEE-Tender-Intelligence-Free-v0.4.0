from datetime import datetime
ACTIVE={'active','active.tendering','active.auction','active.pre-qualification','active.qualification','clarification','submission','published','planned'}
CLOSED={'complete','completed','closed','awarded','cancelled','canceled','unsuccessful'}
def is_active(t, now=None):
    now=now or datetime.utcnow(); s=(t.status or '').lower().strip()
    if s in CLOSED:return False
    if t.deadline and t.deadline < now:return False
    return s in ACTIVE or s.startswith('active')
def is_closed(t): return not is_active(t)
