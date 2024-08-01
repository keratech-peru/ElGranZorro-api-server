import pytz
import random
import requests
from fastapi import Depends
from app.config import API_FOOTBALL_DATA, KEY_FOOTBALL_DATA
from sqlalchemy.orm import Session
from app.database import get_db, SessionLocal
from app.tournaments.models import Tournaments, FootballGames
from app.tournaments.service import Tournaments_, FootballGames_
from app.competitions.models import Matchs, MatchsFootballGames
from app.notifications.service import NotificacionesAdmin_
from datetime import datetime


# # Agrega aquí tus tareas programadas
def start_tournament(db: Session):
    date_now, __ = datetime.strftime(datetime.now(pytz.timezone("America/Lima")),'%d/%m/%y %H:%M:%S').split(" ")
    tournaments = db.query(Tournaments).filter(Tournaments.start_date == date_now).all()
    for tournament in tournaments:
        Tournaments_.start(db, tournament.id)

def update_footballgames(db: Session):
    date_now, hour_now = datetime.strftime(datetime.now(pytz.timezone("America/Lima")),'%d/%m/%y %H:%M:%S').split(" ")
    footballgames = db.query(FootballGames).filter(FootballGames.date == date_now).all()
    time_format = "%H:%M:%S"
    update_result = []
    for footballgame in footballgames:
        dif = datetime.strptime(hour_now, time_format) - datetime.strptime(footballgame.hour, time_format)
        if dif.days < 0 and (footballgame.home_score is None) and (footballgame.away_score is None):
            match_footballgame = db.query(MatchsFootballGames).filter(MatchsFootballGames.id_footballgames ==footballgame.id).first()
            if match_footballgame:
                match = db.query(Matchs).filter(Matchs.id == match_footballgame.id_match).first()
                uri = API_FOOTBALL_DATA + f'matches/{match.id_match}'
                headers = { 'X-Auth-Token':  KEY_FOOTBALL_DATA}
                response = requests.get(uri, headers=headers).json()
                result_home = response["score"]["fullTime"]["home"]
                result_away = response["score"]["fullTime"]["away"]
                status = response["status"]
            else:
                result_home = random.randint(0, 3)
                result_away = random.randint(0, 3)
                status = "RANDOM"
            update_result.append({
                "codigo":footballgame.codigo,
                "home_team":footballgame.home_team,
                "away_team":footballgame.away_team,
                "home_score":result_home,
                "away_score":result_away,
                "hour":footballgame.hour,
                "status":status
            })
            db.commit()
            db.refresh(footballgame)
    NotificacionesAdmin_.send_whatsapp_update_match(update_result)

# Configura el cron job para que se ejecute cada minuto
def cron_job_start_tournament():
    db = SessionLocal()
    try:
        start_tournament(db)
    finally:
        db.close()

def cron_job_update_footballgames():
    db = SessionLocal()
    try:
        update_footballgames(db)
    finally:
        db.close()