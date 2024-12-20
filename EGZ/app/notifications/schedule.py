from fastapi import Depends
from sqlalchemy.orm import Session
from app.config import ADMINISTRATOR_NUMBER
from app.database import SessionLocal
from app.tournaments.models import FootballGames, ConfrontationsGroupStage, ConfrontationsKeyStage,GroupStage
from app.tournaments.service import FootballGames_
from app.competitions.models import MatchsFootballGames
from app.notifications.service import Notificaciones_, NotificacionesAdmin_
from datetime import datetime
import pytz

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
        Notifica al administrador que footballgames se actualizaron desde el API o Random.
        '''
        time_format = "%H:%M:%S"
        update_result = []
        result_home = None
        result_away = None
        date_now, hour_now = datetime.strftime(datetime.now(pytz.timezone("America/Lima")),'%d/%m/%y %H:%M:%S').split(" ")
        footballgames = db.query(FootballGames).filter(FootballGames.date == date_now).all()
        for footballgame in footballgames:
            dif = datetime.strptime(hour_now, time_format) - datetime.strptime(footballgame.hour, time_format)
            if dif.total_seconds() > 6000 and (footballgame.home_score is None) and (footballgame.away_score is None):
                match_footballgame = db.query(MatchsFootballGames).filter(MatchsFootballGames.id_footballgames ==footballgame.id).first()
                if match_footballgame:
                    update_result, result_home, result_away = FootballGames_.update_footballgames_from_api(footballgame, match_footballgame, update_result, db)
                #else:
                #    update_result, result_home, result_away = FootballGames_.update_footballgames_from_random(footballgame, update_result, db)
                # Activa los flujos para pasar de etapas en el torneo.
                    FootballGames_.update_stage(footballgame, result_home, result_away, db)
        NotificacionesAdmin_.send_whatsapp_update_footballgames(update_result)

    def incomplete_footballgames(db: Session):
        '''
        Notifica al administrador los footballgames que faltan actualizar su marcador.
        '''
        time_format = "%H:%M:%S"
        date_now, hour_now = datetime.strftime(datetime.now(pytz.timezone("America/Lima")),'%d/%m/%y %H:%M:%S').split(" ")
        footballgames = db.query(FootballGames).filter( FootballGames.date == date_now,
                                                        FootballGames.away_score.is_(None),
                                                        FootballGames.home_score.is_(None)).all()
        NotificacionesAdmin_.send_whatsapp_incomplete_footballgames(footballgames, hour_now, time_format)

# Configura el cron job para que se ejecute cada minuto
class CronJob:
    def not_complete_footballgames():
        db = SessionLocal()
        try:
            JobNotificationsUsers.not_complete_footballgames(db)
        except:
            Notificaciones_.send_whatsapp(ADMINISTRATOR_NUMBER, "*ADMINISTRADOR* : Hay error en not_complete_footballgames.")
        finally:
            db.close()

    def update_footballgames():
        db = SessionLocal()
        try:
            JobNotificationsAdmin.update_footballgames(db)
        except:
            Notificaciones_.send_whatsapp(ADMINISTRATOR_NUMBER, "*ADMINISTRADOR* : Hay error en update_footballgames.")
        finally:
            db.close()

    def incomplete_footballgames():
        db = SessionLocal()
        try:
            JobNotificationsAdmin.incomplete_footballgames(db)
        except:
            Notificaciones_.send_whatsapp(ADMINISTRATOR_NUMBER, "*ADMINISTRADOR* : Hay error en incomplete_footballgames.")
        finally:
            db.close()
