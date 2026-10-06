from datetime import datetime,timedelta
from app.models import Tender
from app.status import is_active
from app.analytics import winner_rows
def test_active_by_deadline(): assert is_active(Tender('1','x','PL','x',deadline=datetime.utcnow()+timedelta(days=1),status='active'))
def test_closed_winner_analytics():
 t=Tender('1','x','PL','SSD',value=100,status='completed',category='SSD',winner='ABC',winner_value=90,award_date=datetime(2026,1,1))
 r=winner_rows([t],['PL'],None,None,['SSD']);assert r[0]['wins']==1 and r[0]['total']==90
