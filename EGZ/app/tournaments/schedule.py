from fastapi import Depends
from app.config import SQLALCHEMY_DATABASE_URI
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from sqlalchemy.orm import Session
from app.database import get_db, SessionLocal
from app.tournaments.models import Tournaments
from app.tournaments.service import Tournaments_
from datetime import datetime
import pytz

# # Agrega aquí tus tareas programadas
def my_job(db: Session):
    date_now, __ = datetime.strftime(datetime.now(pytz.timezone("America/Lima")),'%d/%m/%y %H:%M:%S').split(" ")
    tournaments = db.query(Tournaments).filter(Tournaments.start_date == date_now).all()
    for tournament in tournaments:
        Tournaments_.start(db, tournament.id)

# Configura el cron job para que se ejecute cada minuto
def cron_job_tournaments():
    db = SessionLocal()
    try:
        my_job(db)
    finally:
        db.close()