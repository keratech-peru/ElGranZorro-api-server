from fastapi import Depends
from app.config import SQLALCHEMY_DATABASE_URI
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from sqlalchemy.orm import Session
from app.database import get_db, SessionLocal
from app.tournaments.models import Tournaments, FootballGames
from app.tournaments.service import Tournaments_, FootballGames_
from datetime import datetime
import pytz
import random

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
    for footballgame in footballgames:
        dif = datetime.strptime(hour_now, time_format) - datetime.strptime(footballgame.hour, time_format)
        if dif.days == 0 and dif.total_seconds() >= 5400 and (footballgame.home_score is None) and (footballgame.away_score is None):
            footballgame.home_score = random.randint(0, 3)
            footballgame.away_score = random.randint(0, 3)
            db.commit()
            db.refresh(footballgame)

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