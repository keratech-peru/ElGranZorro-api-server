from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.security import oauth2_scheme
from app.exception import validate_credentials, expired_token
from app.database import CRUD, get_db
from app.users.models import AppUsers, EnrollmentUsers, PlaysUsers
from app.tournaments.models import Tournaments, GroupStage
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
    
    def list_all(db: Session) -> List[AppUsers]:
        return db.query(AppUsers).all()
    
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
        CRUD.insert(db, new_user_enrollment)
        ### Revisar por que new_user_enrollment retorna vacio.
        group = random.choice( db.query(GroupStage).filter(GroupStage.tournament_cod == tournaments.codigo ,GroupStage.appuser_id == None).all() )
        group.appuser_id = user.id
        CRUD.update(db, group)
        return new_user_enrollment

    def plays_footballgames(db: Session, user: AppUsers, play_users: schemas.PlaysUsers):
        new_user_play_footballgame = PlaysUsers(
            appuser_id=user.id,
            football_games_id=play_users.football_games_id,
            score_local=play_users.score_local,
            score_visit=play_users.score_visit
        )
        CRUD.insert(db, new_user_play_footballgame)
        return new_user_play_footballgame
