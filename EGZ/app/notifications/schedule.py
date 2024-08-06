from fastapi import Depends
from app.config import API_FOOTBALL_DATA, KEY_FOOTBALL_DATA
from sqlalchemy.orm import Session
from app.database import get_db, SessionLocal
from app.tournaments.models import FootballGames, ConfrontationsGroupStage, ConfrontationsKeyStage,GroupStage
from app.tournaments.service import FootballGames_
from app.tournaments.constants import Origin
from app.users.models import PlaysUsers
from app.competitions.models import Matchs, MatchsFootballGames
from app.notifications.service import Notificaciones_, NotificacionesAdmin_
from datetime import datetime
import pytz
import requests

class JobNotificationsUsers:
    def not_complete_footballgames(db: Session):
        '''
        Notifica a los usuarios que no completaron sus jugadas hasta 1 hora antes del inicio.
        '''
        date_now, hour_now = datetime.strftime(datetime.now(pytz.timezone("America/Lima")),'%d/%m/%y %H:%M:%S').split(" ")
        hour_now_ = datetime.strptime(hour_now, '%H:%M:%S')
        footballgames = db.query(FootballGames).filter(FootballGames.date == date_now).all()
        for footballgame in footballgames:
            if footballgame.hour:
                hour_footballgames = datetime.strptime(footballgame.hour, '%H:%M:%S')
                dif = hour_footballgames - hour_now_
                if dif.days == 0 and dif.total_seconds() < 3600:
                    if "GP" in footballgame.codigo:
                        group_stage = db.query(ConfrontationsGroupStage.group_stage_1_id, ConfrontationsGroupStage.group_stage_2_id).filter(ConfrontationsGroupStage.football_games_cod == footballgame.codigo).all()
                        for group in group_stage:
                            appusers_id_group_1 = db.query(GroupStage.appuser_id).filter(GroupStage.id == group[0], GroupStage.appuser_id.isnot(None)).first()
                            appusers_id_group_2 = db.query(GroupStage.appuser_id).filter(GroupStage.id == group[1], GroupStage.appuser_id.isnot(None)).first()
                            if appusers_id_group_1:
                                Notificaciones_.send_whatsapp_user_has_not_played(db, footballgame, appusers_id_group_1[0])
                            if appusers_id_group_2:
                                Notificaciones_.send_whatsapp_user_has_not_played(db, footballgame, appusers_id_group_2[0])
                    else:
                        appusers_id_key = db.query(ConfrontationsKeyStage.appuser_1_id, ConfrontationsKeyStage.appuser_2_id).filter(ConfrontationsKeyStage.football_games_cod == footballgame.codigo).all()
                        for appuser_id in appusers_id_key:
                            if appuser_id[0]:
                                Notificaciones_.send_whatsapp_user_has_not_played(db, footballgame, appuser_id[0])
                            if appuser_id[1]:
                                Notificaciones_.send_whatsapp_user_has_not_played(db, footballgame, appuser_id[1])

class JobNotificationsAdmin:
    def update_footballgames(db: Session):
        '''
        Notifica al administrador que footballgames se actualizaron desde la API.
        '''
        date_now, hour_now = datetime.strftime(datetime.now(pytz.timezone("America/Lima")),'%d/%m/%y %H:%M:%S').split(" ")
        footballgames = db.query(FootballGames).filter(FootballGames.date == date_now, FootballGames.origin == Origin.API).all()
        time_format = "%H:%M:%S"
        update_result = []
        result_home = None
        result_away = None
        for footballgame in footballgames:
            dif = datetime.strptime(hour_now, time_format) - datetime.strptime(footballgame.hour, time_format)
            if dif.total_seconds() > 6000 and (footballgame.home_score is None) and (footballgame.away_score is None):
                match_footballgame = db.query(MatchsFootballGames).filter(MatchsFootballGames.id_footballgames ==footballgame.id).first()
                if match_footballgame:
                    match = db.query(Matchs).filter(Matchs.id == match_footballgame.id_match).first()
                    uri = API_FOOTBALL_DATA + f'matches/{match.id_match}'
                    headers = { 'X-Auth-Token':  KEY_FOOTBALL_DATA}
                    response = requests.get(uri, headers=headers).json()
                    status = response["status"]
                    if status == "FINISHED":
                        result_home = response["score"]["fullTime"]["home"]
                        result_away = response["score"]["fullTime"]["away"]
                        match.score_home = result_home
                        match.score_away = result_away
                        match.status = status
                        db.commit()
                        db.refresh(match)
                        footballgame.home_score = result_home
                        footballgame.away_score = result_away
                        db.commit()
                        db.refresh(footballgame)
                        update_result.append({
                            "codigo":footballgame.codigo,
                            "home_team":footballgame.home_team,
                            "away_team":footballgame.away_team,
                            "home_score":result_home,
                            "away_score":result_away,
                            "hour":footballgame.hour,
                            "status":status
                        })
                        if (result_home != None) and (result_away != None):
                            if "GP" in footballgame.codigo:
                                FootballGames_.update_group_stage(footballgame, result_home, result_away, db)
                            else:
                                FootballGames_.update_key_stage(footballgame, result_home, result_away, db)
        if len(update_result) > 0:
            NotificacionesAdmin_.send_whatsapp_update_match(update_result)

    def incomplete_footballgames(db: Session):
        '''
        Notifica al administrador los footballgames que faltan actualizar su marcador.
        '''
        date_now, __ = datetime.strftime(datetime.now(pytz.timezone("America/Lima")),'%d/%m/%y %H:%M:%S').split(" ")
        footballgames = db.query(FootballGames).filter( FootballGames.date == date_now,
                                                        FootballGames.away_score.is_(None),
                                                        FootballGames.home_score.is_(None)).all()
        NotificacionesAdmin_.send_whatsapp_incomplete_footballgames(footballgames)

# Configura el cron job para que se ejecute cada minuto
class CronJob:
    def not_complete_footballgames():
        db = SessionLocal()
        try:
            JobNotificationsUsers.not_complete_footballgames(db)
        finally:
            db.close()

    def update_footballgames():
        db = SessionLocal()
        try:
            JobNotificationsAdmin.update_footballgames(db)
        finally:
            db.close()

    def incomplete_footballgames():
        db = SessionLocal()
        try:
            JobNotificationsAdmin.incomplete_footballgames(db)
        finally:
            db.close()
