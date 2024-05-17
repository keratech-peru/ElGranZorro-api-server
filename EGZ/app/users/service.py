from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.security import oauth2_scheme
from app.exception import validate_credentials, expired_token
from app.database import CRUD, get_db
from app.users.models import AppUsers, EnrollmentUsers, PlaysUsers
from app.tournaments.models import Tournaments, GroupStage, ConfrontationsKeyStage
from app.users import schemas
from app.users.utils import get_hash
from sqlalchemy.orm import Session
from typing import List
from app.config import SECRETE_KEY
from jose import jwt, JWTError
import random

class AppUsers_(CRUD):
    @staticmethod
    def create(db: Session, user_in: schemas.AppUsers) -> AppUsers:
        user_in.password = get_hash(user_in.password)
        new_user = AppUsers(**user_in.dict())
        CRUD.insert(db, new_user)
        return new_user
    
    def list_search_email(db: Session, email: str) -> List[AppUsers]:
        return db.query(AppUsers).filter(AppUsers.email.like(f"%{email}%")).all()
    
    def get(db: Session, email: str):
        return db.query(AppUsers).filter(AppUsers.email == email).first()

    def update(db: Session, user_old: AppUsers, user_new: schemas.UpdateAppUser):
        user_new_ = user_new.__dict__
        user_old.name = user_new_["name"] if user_new_["name"] else user_old.name
        user_old.lastname = user_new_["lastname"] if user_new_["lastname"] else user_old.lastname
        user_old.birthdate = user_new_["birthdate"] if user_new_["birthdate"] else user_old.birthdate
        user_old.phone = user_new_["phone"] if user_new_["phone"] else user_old.phone
        #user.email = user_.get("email",user.email)
        #user.password = user_.get("name",user.password)
        #user.what_team_are_you_fan = user_.get("name",user.what_team_are_you_fan)
        #user.from_what_age_are_you_fan = user_.get("name",user.from_what_age_are_you_fan)
        user_old.imagen = user_new_["imagen"] if user_new_["imagen"] else user_old.imagen
        user_old.username = user_new_["username"] if user_new_["username"] else user_old.username
        user_old.team_name = user_new_["team_name"] if user_new_["team_name"] else user_old.team_name
        user_old.team_logo = user_new_["team_logo"] if user_new_["team_logo"] else user_old.team_logo
        CRUD.insert(db, user_old)

        return user_old.id

    def authenticate(db: Session, email, password):
        user = AppUsers_.get(db, email)
        if not user:
            raise validate_credentials
        if not get_hash(password) == user.password:
            raise validate_credentials
        return user

    def enrollment(db: Session, user: AppUsers, tournaments: Tournaments):
        new_user_enrollment = EnrollmentUsers(
            appuser_id=user.id,
            tournaments_id=tournaments.id,
            state="EN ESPERA"
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
                enrollment_users = db.query(EnrollmentUsers).filter(EnrollmentUsers.appuser_id == eliminated[0]).first()
                enrollment_users.state = "ELIMINADO - GP"
                CRUD.update(db,enrollment_users)

    def eliminated_key_stage(db: Session, key: str, list_appuser_id: List[int], tournament_id: int):
        enrollments_en_proceso = db.query(EnrollmentUsers).filter(EnrollmentUsers.tournaments_id == tournament_id,EnrollmentUsers.state == "EN PROCESO").all()
        for enrollment in enrollments_en_proceso:
            if enrollment.appuser_id not in  list_appuser_id:
                enrollment.state = f"ELIMINADO - {key}"
                CRUD.update(db, enrollment)
