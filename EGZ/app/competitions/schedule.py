from fastapi import Depends
from app.config import SQLALCHEMY_DATABASE_URI
from app.competitions.models import Competitions
from app.competitions.service import Competitions_
from sqlalchemy.orm import Session
from app.database import SessionLocal

# # Agrega aquí tus tareas programadas
def adding_match(db: Session):
    competitions = db.query(Competitions.id, Competitions.id_competition, Competitions.code).all()
    Competitions_.add_match(competitions, db)

# Configura el cron job para que se ejecute cada minuto
def cron_job_adding_match():
    db = SessionLocal()
    try:
        adding_match(db)
    finally:
        db.close()