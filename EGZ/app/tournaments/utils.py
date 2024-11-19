from app.tournaments.models import Tournaments
from app.tournaments.constants import Players
from app.database import get_db
from fastapi import Depends
from sqlalchemy.orm import Session
from datetime import datetime, timezone, timedelta
import pytz


def code_generator_tournaments(db: Session = Depends(get_db)):
    filtro = db.query(Tournaments.id).order_by(Tournaments.id.desc()).first()[0] if db.query(Tournaments).all() else 0
    if filtro < 10:
        id = "00" + str(filtro)
    elif filtro >= 10 and filtro < 100:
        id = "0"+str(filtro)
    else:
        id = str(filtro)
    return "T" + Players.MAXIMO + id, filtro

def is_past(start_date: str, hour: str=None):
    datetime_now = datetime.now(pytz.timezone("America/Lima"))
    if hour:
        dif = datetime_now - datetime.strptime(f'{start_date} {hour}', '%d/%m/%y %H:%M:%S').replace(tzinfo=timezone.utc) - timedelta(hours=5)
    else:
        dif = datetime_now - datetime.strptime(f'{start_date}', '%d/%m/%y').replace(tzinfo=timezone.utc) - timedelta(hours=5)
    return int(dif.days) >= 0

def is_over(start_date: str):
    datetime_now = datetime.now(pytz.timezone("America/Lima"))
    dif = datetime_now - datetime.strptime(f'{start_date}', '%d/%m/%y').replace(tzinfo=timezone.utc) - timedelta(hours=5)
    return int(dif.days) > 300

def hide_data_because_is_past_is_appuser(is_past:True, is_appuser:True, data):
    if not is_appuser:
        if not is_past:
            return None
    return data
