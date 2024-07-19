from sqlalchemy.orm import Session
from app.config import Email, Whatsapp
from app.notifications.constants import TextToSend
from app.database import CRUD
from app.tournaments.models import Tournaments, FootballGames
from app.tournaments.constants import ETAPAS
from app.users.models import AppUsers
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
        text = TextToSend.otp(otp) + ". Si realizas un intento mas , tu cuenta se bloqueara por 20 min" if count_max else ""
        Notificaciones_.send_whatsapp(phone, text)

    @staticmethod
    def send_whatsapp_eliminated(db: Session, tournament_id: int, appuser_id: int, key:str) -> None:
        tournament = db.query(Tournaments).filter(Tournaments.id == tournament_id).first()
        appuser = db.query(AppUsers).filter(AppUsers.id == appuser_id).first()
        text = TextToSend.eliminated(tournament, appuser.name, fase=ETAPAS[key])
        Notificaciones_.send_whatsapp(appuser.phone, text)
     
    @staticmethod
    def send_whatsapp_stage_passed(db: Session, tournament_cod: str, list_appuser_id: list[int], key:str) -> None:
        tournament = db.query(Tournaments).filter(Tournaments.codigo == tournament_cod).first()
        for appuser_id in list_appuser_id:
            if appuser_id:
                appuser = db.query(AppUsers).filter(AppUsers.id == appuser_id).first()        
                text = TextToSend.stage_passed(tournament, appuser.name, fase=ETAPAS[key])
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