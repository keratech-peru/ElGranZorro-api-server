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
from app.notifications.schedule import cron_job
from apscheduler.schedulers.background import BackgroundScheduler

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

# Inicia el scheduler

@app.get("/")
def root() -> Dict[str, object]:
    return {"message": "Bienvenido al backend EGZ"}

handler = Mangum(app)

@app.on_event('startup')
def init_data():
    scheduler = BackgroundScheduler()
    scheduler.add_job(cron_job, 'cron', minute='10')
    scheduler.start()