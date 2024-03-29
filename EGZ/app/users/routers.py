from fastapi import APIRouter, Depends, status, Request
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from typing import Dict
from sqlalchemy.orm import Session
from app.users.service import AppUsers_
from app.users import schemas
from app.users.models import AppUsers, EnrollmentUsers, PlaysUsers
from app.tournaments import models, exception as exception_tournaments
from app.users import exception
from app.database import get_db
from app.security import create_token, valid_header, get_user_current
from app.config import ApiKey, TOKEN_SCONDS_EXP



router = APIRouter(prefix="/users", tags=["users"])

@router.post("/", status_code=status.HTTP_201_CREATED)
def user_create(
    request: Request,
    user_in: schemas.AppUsers,
    db: Session = Depends(get_db),
    ) -> Dict[str, object]:
        """
        **Descripcion** : El servicio crea un usuario.
        \n**Excepcion** : 
            \n- El servicio requiere api-key.
            \n- El servicio tiene excepcion si el email ya pertenece a otro usuario.
        """
        valid_header(request, ApiKey.USERS)
        user = db.query(AppUsers).filter(AppUsers.email == user_in.email).first()
        if user:
            raise exception.email_already_used
        new_user = AppUsers_.create(db, user_in)
        return {"status": "done", "user_id": new_user.id}

@router.get("/")
def user_get(
    user: AppUsers = Depends(get_user_current)
    ) -> Dict[str, object]:
        """
        **Descripcion** : El servicio muestra la informacion del usuario logiado.
        \n**Excepcion** : 
            \n- El servicio requiere autorizacion via token
            \n- El servicio tiene excepcion si el token es invalido o expiro
        """
        return user

@router.put("/")
def user_put(
    user_new: schemas.UpdateAppUser,
    db: Session = Depends(get_db),
    user: AppUsers = Depends(get_user_current)
    ) -> Dict[str, object]:
        """
        **Descripcion** : El servicio permite actualizar la informacion del usuario logiado. En el body los campos son opcionales es decir solo se envia los campos a actualizar, los campos **password, what_team_are_you_fan, from_what_age_are_you_fan** no se puede actualizar mediante este flujo.
        \n**Excepcion** : 
            \n- El servicio requiere autorizacion via token
            \n- El servicio tiene excepcion si el token es invalido o expiro
        """
        user_id = AppUsers_.update(db ,user, user_new)
        return {"status": "done", "user_id": user_id}

@router.post("/login", status_code=status.HTTP_201_CREATED)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
    ) -> Dict[str, object]:
        user = AppUsers_.authenticate(db , form_data.username, form_data.password)
        access_token_jwt = create_token({"email":user.email})
        return { "access_token": access_token_jwt, "token_type": "bearder", "expires_in": TOKEN_SCONDS_EXP }

@router.post("/enrollment/{tournaments_id}", status_code=status.HTTP_201_CREATED)
def user_enrollment(
    tournaments_id: str,
    db: Session = Depends(get_db),
    user: AppUsers = Depends(get_user_current)
    ) -> Dict[str, object]:
        """
        **Descripcion** : El servicio que inscribe al usuario a un torneo especifico.
        \n**Excepcion** : 
            \n- El servicio requiere autorizacion via token
            \n- El servicio tiene excepcion si el token es invalido o expiro
            \n- El servicio tiene excepcion cuando se ingresa un tournaments_id inexistente
            \n- El servicio tiene excepcion si el usuario quiere inscribirse en un torneo al cual ya esta inscrito.
            \n- El servicio tiene excepcion si el usuario quiere inscribirse a un torneo que ya tiene las plazas llenas.
        """
        tournament = db.query(models.Tournaments).filter(models.Tournaments.id == tournaments_id).first() 
        if not tournament:
            raise exception_tournaments.tournament_not_exist
        enrollment = db.query(EnrollmentUsers).filter(EnrollmentUsers.tournaments_id == tournaments_id, EnrollmentUsers.appuser_id == user.id).first()
        list_enrollment = db.query(EnrollmentUsers).filter(EnrollmentUsers.tournaments_id == tournaments_id).all()
        enrollment_tournament_max = int(tournament.max_number_of_players)
        if enrollment:
            raise exception.user_already_registered_tournament
        if enrollment_tournament_max <= len(list_enrollment):
            raise exception_tournaments.full_tournament
        new_user_enrollment = AppUsers_.enrollment(db, user, tournament)
        return {"status": "done", "new_user_enrollment": new_user_enrollment}

@router.post("/plays/{footballgames_id}", status_code=status.HTTP_201_CREATED)
def user_plays_footballgames(
    play_user_in: schemas.PlaysUsers,
    db: Session = Depends(get_db),
    user: AppUsers = Depends(get_user_current)
    ) -> Dict[str, object]:
        """
        **Descripcion** : El servicio permite que el usuario inscriba su jugada de una partida especifica.
        \n**Excepcion** : 
            \n- El servicio requiere autorizacion via token
            \n- El servicio tiene excepcion si el token es invalido o expiro
            \n- El servicio tiene excepcion si el footballgame_id no existe
            \n- El servicio tiene excepcion si el usuario quiere escribir su jugada a un footballgame de un torneo al cual no esta inscrito.
        """
        footballgame = db.query(models.FootballGames).filter(models.FootballGames.id == play_user_in.football_games_id).first() 
        if not footballgame:
            raise exception_tournaments.footballgames_not_exist
        enrollment = db.query(EnrollmentUsers).filter(EnrollmentUsers.tournaments_id == footballgame.tournament_id, EnrollmentUsers.appuser_id == user.id).first()
        if not enrollment:
            raise exception.user_not_registered_in_footballgame
        new_play_footballgame = AppUsers_.plays_footballgames(db, user, play_user_in)
        return {"status": "done", "play_footballgame_id": new_play_footballgame.id}