from fastapi import Depends
from app.config import SQLALCHEMY_DATABASE_URI
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from sqlalchemy.orm import Session
from app.database import get_db, SessionLocal
from app.tournaments.models import Tournaments, FootballGames, ConfrontationsGroupStage, ConfrontationsKeyStage,GroupStage
from app.users.models import PlaysUsers
from app.notifications.service import Notificaciones_
from datetime import datetime
import pytz

# # Agrega aquí tus tareas programadas
def my_job(db: Session):
    #print("Ejecutando tarea programada... #####")
    date_now, hour_now = datetime.strftime(datetime.now(pytz.timezone("America/Lima")),'%d/%m/%y %H:%M:%S').split(" ")
    hour_now_ = datetime.strptime(hour_now, '%H:%M:%S')
    footballgames = db.query(FootballGames).filter(FootballGames.date == date_now).all()
    for footballgame in footballgames:
        if footballgame.hour:
            hour_footballgames = datetime.strptime(footballgame.hour, '%H:%M:%S')
            dif = hour_footballgames - hour_now_
            #print(footballgame.codigo, dif.days, dif.total_seconds())
            if dif.days == 0 and dif.total_seconds() < 3600:
                if "GP" in footballgame.codigo:
                    group_stage = db.query(ConfrontationsGroupStage.group_stage_1_id, ConfrontationsGroupStage.group_stage_2_id).filter(ConfrontationsGroupStage.football_games_cod == footballgame.codigo).all()
                    for group in group_stage:
                        appusers_id_group_1 = db.query(GroupStage.appuser_id).filter(GroupStage.id == group[0], GroupStage.appuser_id.isnot(None)).first()
                        appusers_id_group_2 = db.query(GroupStage.appuser_id).filter(GroupStage.id == group[1], GroupStage.appuser_id.isnot(None)).first()
                        if appusers_id_group_1:
                            print(footballgame, appusers_id_group_1[0])
                            Notificaciones_.send_whatsapp_user_has_not_played(db, footballgame, appusers_id_group_1[0])
                        if appusers_id_group_2:
                            print(footballgame, appusers_id_group_2[0])
                            Notificaciones_.send_whatsapp_user_has_not_played(db, footballgame, appusers_id_group_2[0])
                else:
                    appusers_id_key = db.query(ConfrontationsKeyStage.appuser_1_id, ConfrontationsKeyStage.appuser_2_id).filter(ConfrontationsKeyStage.football_games_cod == footballgame.codigo).all()
                    for appuser_id in appusers_id_key:
                        if appuser_id[0]:
                            Notificaciones_.send_whatsapp_user_has_not_played(db, footballgame, appuser_id[0])
                        if appuser_id[1]:
                            Notificaciones_.send_whatsapp_user_has_not_played(db, footballgame, appuser_id[1])

# Configura el cron job para que se ejecute cada minuto
def cron_job():
    db = SessionLocal()
    try:
        my_job(db)
    finally:
        db.close()
