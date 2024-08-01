from typing import List
from sqlalchemy.orm import Session
from app.config import Email, Whatsapp
from app.notifications.constants import TextToSend
from app.database import CRUD
from app.tournaments.models import Tournaments, FootballGames
from app.tournaments.constants import STATUS_TOURNAMENT
from app.notifications.constants import Otp
from app.users.models import AppUsers, PlaysUsers
from email.message import EmailMessage
import smtplib
import requests

class Notificaciones_:
    @staticmethod
    def send_email(msg: str, addressee: str, asunto: str) -> None:
        remitente = Email.REMITENTE
        destinatario = addressee
        mensaje = msg
        email = EmailMessage()
        email["From"] = remitente
        email["To"] = destinatario
        email["Subject"] = asunto
        # email.set_content(mensaje, subtype="html")
        email.set_content(mensaje)
        smtp = smtplib.SMTP_SSL("smtp.gmail.com")
        smtp.login(remitente, Email.PASSWORD)
        smtp.sendmail(remitente, destinatario, email.as_string())
        smtp.quit()

    @staticmethod
    def send_whatsapp(phone: str, message: str) -> None:
        body = {"message":message,"phone":'51'+phone}
        response = requests.post(Whatsapp.URL_SEND, json = body)

    @staticmethod
    def send_whatsapp_otp(phone: str, otp: int, count_max: bool) -> None:
        text = TextToSend.otp(otp) + f". Si realizas un intento mas , tu cuenta se bloqueara por {Otp.MINUTES} min" if count_max else TextToSend.otp(otp)
        Notificaciones_.send_whatsapp(phone, text)

    @staticmethod
    def send_whatsapp_eliminated(db: Session, tournament_id: int, appuser_id: int, key:str) -> None:
        tournament = db.query(Tournaments).filter(Tournaments.id == tournament_id).first()
        appuser = db.query(AppUsers).filter(AppUsers.id == appuser_id).first()
        text = TextToSend.eliminated(tournament, appuser.name, fase=STATUS_TOURNAMENT[key])
        Notificaciones_.send_whatsapp(appuser.phone, text)
     
    @staticmethod
    def send_whatsapp_stage_passed(db: Session, tournament_cod: str, list_appuser_id: list[int], key:str) -> None:
        tournament = db.query(Tournaments).filter(Tournaments.codigo == tournament_cod).first()
        for appuser_id in list_appuser_id:
            if appuser_id:
                appuser = db.query(AppUsers).filter(AppUsers.id == appuser_id).first()        
                text = TextToSend.stage_passed(tournament, appuser.name, fase=STATUS_TOURNAMENT[key])
                Notificaciones_.send_whatsapp(appuser.phone, text)
    
    @staticmethod
    def send_whatsapp_user_not_play_games(db: Session, tournament_cod: str, list_appuser_id: list[int], stage:str) -> None:
        tournament = db.query(Tournaments).filter(Tournaments.codigo == tournament_cod).first()
        for appuser_id in list_appuser_id:
            if appuser_id[0]:
                appuser = db.query(AppUsers).filter(AppUsers.id == appuser_id[0]).first()        
                text = TextToSend.user_not_play_games(tournament, appuser.name, stage)
                Notificaciones_.send_whatsapp(appuser.phone, text)

    @staticmethod
    def send_whatsapp_user_winner(db: Session, tournament_cod: str, appuser_id: int) -> None:
        tournament = db.query(Tournaments).filter(Tournaments.codigo == tournament_cod).first()
        appuser = db.query(AppUsers).filter(AppUsers.id == appuser_id).first()
        text = TextToSend.user_winner(tournament, appuser.name)
        Notificaciones_.send_whatsapp(appuser.phone, text)

    @staticmethod
    def send_whatsapp_user_point_equal(db: Session, football_games_id: int, appuser_id1: int, appuser_id2: int, list_date_1, list_date_2, stage: str) -> None:
        tournament_id = db.query(FootballGames.tournament_id).filter(FootballGames.id == football_games_id).first()[0]
        tournament = db.query(Tournaments).filter(Tournaments.id == tournament_id).first()
        appuser1 = db.query(AppUsers).filter(AppUsers.id == appuser_id1).first()
        appuser2 = db.query(AppUsers).filter(AppUsers.id == appuser_id2).first()
        text = TextToSend.user_equal_poitns(tournament, appuser1.name, appuser2.name, list_date_1, list_date_2, stage)
        Notificaciones_.send_whatsapp(appuser1.phone, text)
    
    @staticmethod
    def send_whatsapp_user_has_not_played(db: Session, footballgame: FootballGames, appuser_id: int) -> None:
        play_user = db.query(PlaysUsers).filter(PlaysUsers.football_games_id == footballgame.id, PlaysUsers.appuser_id == appuser_id).first()
        if not play_user:
            appuser = db.query(AppUsers).filter(AppUsers.id == appuser_id).first()
            text = TextToSend.user_has_not_played(footballgame, appuser.name)
            Notificaciones_.send_whatsapp(appuser.phone, text)

class NotificacionesAdmin_:
    @staticmethod
    def send_whatsapp_incomplete_tournament(db: Session, tournament_id: int, numb_footballgame: int) -> None:
        tournament = db.query(Tournaments).filter(Tournaments.id == tournament_id).first()
        text = f"*Administrador* el torneo *{tournament.name}* creado recientemente tiene *{numb_footballgame}* footballgames incompletos, se le pondra data dummy."
        Notificaciones_.send_whatsapp("936224658", text)

    @staticmethod
    def send_whatsapp_adding_match(numb_match: int, start_date:str, end_date:str) -> None:
        text = f"*Administrador* se han agregado {numb_match} match nuevos correspondietes a las fechas *{start_date}* al *{end_date}*"
        Notificaciones_.send_whatsapp("936224658", text)

    @staticmethod
    def send_whatsapp_update_match(update_results: List[dict]) -> None:
        text = "Se actualizo el registro de los match:\n"
        for result in update_results:
            codigo = result["codigo"]
            home_team = result["home_team"]
            away_team = result["away_team"]
            home_score = result["home_score"]
            away_score = result["away_score"]
            hour = result["hour"]
            status = result["status"]
            text = text + f"- *{codigo}* -> {home_team} vs {away_team} -> {home_score} - {away_score} -> {hour} -> {status}\n"
        Notificaciones_.send_whatsapp("936224658", text)