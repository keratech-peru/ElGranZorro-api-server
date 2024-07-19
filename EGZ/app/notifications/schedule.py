from fastapi import Depends
from app.config import SQLALCHEMY_DATABASE_URI
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from sqlalchemy.orm import Session
from app.database import get_db

jobstore = {
    'default': SQLAlchemyJobStore(url=SQLALCHEMY_DATABASE_URI)
}

# Inicializa el scheduler
scheduler = BackgroundScheduler(jobstores=jobstore)

# Agrega aquí tus tareas programadas
def my_job(db: Session = Depends(get_db)):
    print("Ejecutando tarea programada...")

# Agrega un job
scheduler.add_job(my_job, 'interval', seconds=60)