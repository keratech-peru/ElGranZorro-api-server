import pytz
from fastapi import Depends
from datetime import datetime, timedelta
from app.config import SQLALCHEMY_DATABASE_URI
from app.competitions.models import Competitions
from app.competitions.service import Competitions_
from app.tournaments.service import Tournaments_
from app.tournaments.models import Tournaments, FootballGames
from app.tournaments.constants import Origin
from sqlalchemy.orm import Session
from app.database import SessionLocal

class JobCompetitions:
    def adding_match(db: Session):
        '''
        Agrega matchs desde la API.
        '''
        competitions = db.query(Competitions.id, Competitions.id_competition, Competitions.code).all()
        Competitions_.add_match(competitions, db)

    def start_tournament(db: Session):
        '''
        Actualiza el estado de un torneo al empezar.
        '''
        date_now, __ = datetime.strftime(datetime.now(pytz.timezone("America/Lima")),'%d/%m/%y %H:%M:%S').split(" ")
        tournaments = db.query(Tournaments).filter(Tournaments.start_date == date_now).all()
        for tournament in tournaments:
            Tournaments_.start(db, tournament.id)

    def checking_changes_in_matches(db: Session):
        list_dates = []
        for i in range(0,3):
            now = datetime.now(pytz.timezone("America/Lima")) + timedelta(days=i)
            date_now, __ = datetime.strftime(now,'%d/%m/%y %H:%M:%S').split(" ")
            list_dates.append(date_now)
        footballgames = db.query(FootballGames).filter(FootballGames.date.in_(list_dates), FootballGames.origin == Origin.API).all()
        Competitions_.checkout_match(footballgames, db)

class CronJob:
    def adding_match():
        db = SessionLocal()
        try:
            JobCompetitions.adding_match(db)
        finally:
            db.close()

    def start_tournament():
        db = SessionLocal()
        try:
            JobCompetitions.start_tournament(db)
        finally:
            db.close()

    def checking_changes_in_matches():
        db = SessionLocal()
        try:
            JobCompetitions.checking_changes_in_matches(db)
        finally:
            db.close()