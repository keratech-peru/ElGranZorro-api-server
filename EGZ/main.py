from fastapi import FastAPI, Request, Form, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from mangum import Mangum
from typing import Dict
from app.database import Base, engine
from app.users.routers import router as users
from app.admin.routers import router as admin
from app.tournaments.routers import router as tournaments
from app.notifications.router import router as notifications
from app.competitions.routers import router as competitions
from app.competitions.schedule import cron_job_adding_match
from app.notifications.schedule import cron_job_notifications
from app.tournaments.schedule import cron_job_start_tournament, cron_job_update_footballgames, cron_job_incomplete_footballgames
from apscheduler.schedulers.background import BackgroundScheduler
import pytz

# Creacion de la BD
Base.metadata.create_all(bind=engine)

app = FastAPI()
app.mount("/static", StaticFiles(directory="app/admin/static"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users)
app.include_router(admin)
app.include_router(tournaments)
app.include_router(notifications)
app.include_router(competitions)

# Inicia el scheduler

@app.get("/")
def root() -> Dict[str, object]:
    return {"message": "Bienvenido al backend EGZ"}

handler = Mangum(app)

@app.on_event('startup')
def init_data():
    scheduler = BackgroundScheduler(timezone=pytz.timezone("America/Lima"))
    scheduler.add_job(cron_job_notifications, 'cron', minute=2)
    scheduler.add_job(cron_job_start_tournament, 'cron', hour=0, minute=5)
    scheduler.add_job(cron_job_update_footballgames, 'cron', minute=0)
    scheduler.add_job(cron_job_adding_match, 'cron', day_of_week='thu', hour=11, minute=0)
    scheduler.add_job(cron_job_incomplete_footballgames, 'cron', hour=23, minute=50)
    scheduler.start()