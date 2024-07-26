import random
from typing import List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.exception import validate_credentials, expired_token
from app.database import CRUD
from app.users.models import AppUsers, EnrollmentUsers, PlaysUsers, EventLogUser, OtpUsers, EventOtpUsers
from app.users import exception, schemas 
from app.users.utils import get_hash, generate_otp_numeric
from app.tournaments.models import Tournaments, GroupStage
from app.tournaments.constants import ETAPAS
from app.notifications.service import Notificaciones_
from app.notifications.constants import TextToSend, Otp

class AppUsers_(CRUD):
    @staticmethod
    def create(db: Session, user_in: schemas.AppUsers) -> AppUsers:
        user_in.team_name = user_in.name + " FC"
        new_user = AppUsers(**user_in.dict())
        CRUD.insert(db, new_user)
        return new_user
    
    def list_search_email(db: Session, email: str) -> List[AppUsers]:
        return db.query(AppUsers).filter(AppUsers.email.like(f"%{email}%")).all()
    
    def get(db: Session, email: str, phone: str):
        return db.query(AppUsers).filter(AppUsers.email == email, AppUsers.phone == phone).first()

    def update(db: Session, user_old: AppUsers, user_new: schemas.UpdateAppUser):
        user_new_ = user_new.__dict__
        user_old.name = user_new_["name"] if user_new_["name"] else user_old.name
        user_old.lastname = user_new_["lastname"] if user_new_["lastname"] else user_old.lastname
        user_old.birthdate = user_new_["birthdate"] if user_new_["birthdate"] else user_old.birthdate
        user_old.email = user_new_["email"] if user_new_["email"] else user_old.email
        user_old.dni = user_new_["dni"] if user_new_["dni"] else user_old.dni
        user_old.imagen = user_new_["imagen"] if user_new_["imagen"] else user_old.imagen
        user_old.username = user_new_["username"] if user_new_["username"] else user_old.username
        user_old.team_name = user_new_["team_name"] if user_new_["team_name"] else user_old.team_name
        user_old.team_logo = user_new_["team_logo"] if user_new_["team_logo"] else user_old.team_logo

        if user_new_["phone"]:
            user_old.phone = user_new_["phone"]
            new_otp, __ = OtpUsers_.resend(db, user_old.id)
            Notificaciones_.send_whatsapp_otp(user_new_["phone"] ,new_otp, count_max=False)
        CRUD.insert(db, user_old)

        return user_old.id

    def authenticate(db: Session, email, phone):
        user = AppUsers_.get(db, email, phone)
        if not user:
            raise validate_credentials
        return user

    def enrollment(db: Session, user: AppUsers, tournaments: Tournaments):
        new_user_enrollment = EnrollmentUsers(
            appuser_id=user.id,
            tournaments_id=tournaments.id,
            state=ETAPAS["EE"]
        )
        group = random.choice( db.query(GroupStage).filter(GroupStage.tournament_cod == tournaments.codigo ,GroupStage.appuser_id == None).all() )
        group.appuser_id = user.id
        CRUD.update(db, group)
        CRUD.insert(db, new_user_enrollment)
        return new_user_enrollment

    def decline(db: Session, user: AppUsers, tournament_cod: str, enrollment: EnrollmentUsers):
        db.query(EnrollmentUsers).filter(EnrollmentUsers.id==enrollment.id).delete()
        group_stage = db.query(GroupStage).filter(GroupStage.tournament_cod == tournament_cod, GroupStage.appuser_id == user.id).first()
        group_stage.appuser_id = None
        CRUD.update(db, group_stage) 

    def plays_footballgames(db: Session, user: AppUsers, play_users: schemas.PlaysUsers):
        playusers = db.query(PlaysUsers).filter(PlaysUsers.appuser_id==user.id, PlaysUsers.football_games_id == play_users.football_games_id).first()
        if playusers:
            playusers.updated_at = datetime.now()
            playusers.score_local=play_users.score_local
            playusers.score_visit=play_users.score_visit
            CRUD.update(db, playusers)
        else:
            new_user_play_footballgame = PlaysUsers(
                appuser_id=user.id,
                football_games_id=play_users.football_games_id,
                score_local=play_users.score_local,
                score_visit=play_users.score_visit
            )
            CRUD.insert(db, new_user_play_footballgame)

    def play_users_points(db: Session, footballgame_id: int, footballgame_type: str, home_score: str, away_score: str):
        plays_users = db.query(PlaysUsers).filter(PlaysUsers.football_games_id == footballgame_id).all()
        appuser_id_point_plays = {}
        for play in plays_users:
            if footballgame_type == 'SCORE':
                point = 3 if play.score_local == int(home_score) and play.score_visit == int(away_score)  else 0
            if  footballgame_type == 'RESULT':
                point = 1 if (play.score_local >= play.score_visit) == (int(home_score) >= int(away_score)) else 0
            appuser_id_point_plays[play.appuser_id] = point
        return appuser_id_point_plays
    
    def eliminated_group_stage(db: Session, cod_tournament: str):
        eliminateds = db.query(GroupStage.appuser_id, GroupStage.group, GroupStage.position).filter(GroupStage.tournament_cod == cod_tournament, GroupStage.position != 1, GroupStage.position != 2).order_by(GroupStage.id).all()
        for eliminated in eliminateds:
            if eliminated[0]:
                enrollment_users = db.query(EnrollmentUsers).filter(EnrollmentUsers.appuser_id == eliminated[0], EnrollmentUsers.tournaments_id == int(cod_tournament[-3:])).first()
                enrollment_users.state = "ELIMINADO - GRUPOS"
                CRUD.update(db,enrollment_users)
                db.commit()
                Notificaciones_.send_whatsapp_eliminated(db, enrollment_users.tournaments_id, enrollment_users.appuser_id, key = "GP")

    def eliminated_key_stage(db: Session, key: str, list_appuser_id: List[int], tournament_id: int):
        enrollments_en_proceso = db.query(EnrollmentUsers).filter(EnrollmentUsers.tournaments_id == tournament_id,EnrollmentUsers.state == "EN PROCESO").all()
        for enrollment in enrollments_en_proceso:
            if enrollment.appuser_id not in  list_appuser_id:
                enrollment.state = f"ELIMINADO - {ETAPAS[key]}"
                CRUD.update(db, enrollment)
                db.commit()
                Notificaciones_.send_whatsapp_eliminated(db, enrollment.tournaments_id, enrollment.appuser_id, key = key)

    def password_update_validation(db: Session, recovery_in: schemas.PasswordUpdateValidation, user: AppUsers):
        val_1 = user.email.lower() == recovery_in.email.lower()
        val_2 = user.what_team_are_you_fan.lower() == recovery_in.what_team_are_you_fan.lower()
        val_3 = user.from_what_age_are_you_fan.lower() == recovery_in.from_what_age_are_you_fan.lower()
        if not (val_1 and val_2 and val_3):
            new_event_log = EventLogUser(due_date = datetime.utcnow(), appuser_id = user.id, servicio = "password_update_validation", status = 400)
            CRUD.insert(db, new_event_log)
            raise exception.user_failed_validate_password_update
        new_event_log = EventLogUser(due_date = datetime.utcnow(), appuser_id = user.id, servicio = "password_update_validation", status = 200)
        CRUD.insert(db, new_event_log)

class OtpUsers_(CRUD):
    @staticmethod
    def create(db: Session, appuser_id: int) -> OtpUsers:
        otp = generate_otp_numeric()
        otp_user = OtpUsers(appuser_id = appuser_id, otp = get_hash(otp))
        CRUD.insert(db, otp_user)
        return otp_user, otp
    
    def resend(db: Session, appuser_id: int) -> OtpUsers:
        appuser = db.query(AppUsers).filter(AppUsers.id == appuser_id).first()
        otp_users = db.query(OtpUsers).filter(OtpUsers.appuser_id == appuser_id).first()
        new_otp = generate_otp_numeric()
        otp_users.otp = get_hash(new_otp)
        CRUD.update(db, otp_users)
        return new_otp, appuser.phone
    
    def validate(db: Session, appuser_id: int, otp: str) -> bool:
        otp_users = db.query(OtpUsers).filter(OtpUsers.appuser_id == appuser_id).first()
        otp_ = otp_users.otp
        bool_otp = get_hash(otp) == otp_
        otp_users.is_verification = bool_otp
        CRUD.update(db, otp_users)
        return bool_otp

class EventOtpUsers_(CRUD):
    @staticmethod
    def create(db: Session, appuser_id: int) -> EventOtpUsers:
        event_otp_user = EventOtpUsers(appuser_id = appuser_id)
        CRUD.insert(db, event_otp_user)

    @staticmethod
    def get_by_appuser_id(db: Session, appuser_id: int) -> EventOtpUsers:
        event_otp_user_list = db.query(EventOtpUsers).filter(EventOtpUsers.appuser_id == appuser_id).all()
        return event_otp_user_list

    @staticmethod
    def validate_count(db: Session, appuser_id: int) -> int:
        current_time = datetime.utcnow()
        ten_weeks_ago = current_time - timedelta(minutes=Otp.MINUTES)
        return db.query(EventOtpUsers).filter(EventOtpUsers.appuser_id == appuser_id, EventOtpUsers.due_date > ten_weeks_ago).count()
  
    @staticmethod
    def user_should_be_blocked(db: Session, user: AppUsers):
        validate_count = EventOtpUsers_.validate_count(db, user.id)
        if validate_count < Otp.COUNT:
            new_otp, __ = OtpUsers_.resend(db, user.id)
            EventOtpUsers_.create(db, user.id)
            Notificaciones_.send_whatsapp_otp(user.phone, new_otp, count_max=False)
        elif validate_count == Otp.COUNT:
            new_otp, __ = OtpUsers_.resend(db, user.id)
            EventOtpUsers_.create(db, user.id)
            Notificaciones_.send_whatsapp_otp(user.phone, new_otp, count_max=True)
        else:
            raise exception.user_temporarily_blocked