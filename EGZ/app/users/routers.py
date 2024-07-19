from fastapi import APIRouter, Depends, status, Request
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from typing import Dict, List
from sqlalchemy.orm import Session
from app.users.service import AppUsers_, OtpUsers_, EventOtpUsers_
from app.users import schemas
from app.users.models import AppUsers, EnrollmentUsers, PlaysUsers, EventLogUser
from app.tournaments import models, utils, exception as exception_tournaments
from app.users import exception
from app.database import get_db
from app.security import create_token, valid_header, get_user_current
from app.config import ApiKey, TOKEN_SCONDS_EXP
from datetime import datetime, timedelta
from app.notifications.service import Notificaciones_
from app.notifications.constants import TextToSend


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
        user_email = db.query(AppUsers).filter(AppUsers.email == user_in.email).first()
        user_phone = db.query(AppUsers).filter(AppUsers.phone == user_in.phone).first()
        if user_email:
           raise exception.email_already_used
        if user_phone:
           raise exception.phone_already_used
        new_user = AppUsers_.create(db, user_in)
        __, otp = OtpUsers_.create(db, new_user.id)
        Notificaciones_.send_whatsapp(user_in.phone , TextToSend.otp(otp))
        return {"status": "done", "user_id": new_user.id}

@router.get("/", status_code=status.HTTP_200_OK)
def user_get(
    user: AppUsers = Depends(get_user_current)
    ) -> Dict[str, object]:
        """
        **Descripcion** : El servicio muestra la informacion del usuario logiado.
        \n**Excepcion** : 
            \n- El servicio requiere autorizacion via token
            \n- El servicio tiene excepcion si el token es invalido o expiro
        """
        return {"status":"done", "data":user}

@router.patch("/", status_code=status.HTTP_200_OK)
def user_patch(
    user_new: schemas.UpdateAppUser,
    db: Session = Depends(get_db),
    user: AppUsers = Depends(get_user_current)
    ) -> Dict[str, object]:
        """
        **Descripcion** : El servicio permite actualizar la informacion del usuario logiado. En el body los campos son opcionales es decir solo se envia los campos a actualizar, los campos **password, what_team_are_you_fan, from_what_age_are_you_fan** no se puede actualizar mediante este flujo.
        \n**Excepcion** : 
            \n- El servicio requiere autorizacion via token
            \n- El servicio tiene excepcion si el token es invalido o expiro
            \n- El servicio tiene una excepcion cuando el correo a actualizar ya esta siendo utilizado
        """
        if user_new.email and db.query(AppUsers).filter(AppUsers.email==user_new.email).first():
            raise exception.email_cannot_updated
        if user_new.phone and db.query(AppUsers).filter(AppUsers.phone==user_new.phone).first():
            raise exception.phone_cannot_updated
        user_id = AppUsers_.update(db ,user, user_new)
        return {"status": "done", "user_id": user_id}

@router.post("/login", status_code=status.HTTP_201_CREATED)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
    ) -> Dict[str, object]:
        user = AppUsers_.authenticate(db , form_data.username, form_data.password)
        access_token_jwt = create_token({"email":user.email})
        EventOtpUsers_.user_should_be_blocked(db, user)
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
        Notificaciones_.send_whatsapp(user.phone , TextToSend.enrollment(tournament, user.name))
        return {"status": "done", "new_user_enrollment": new_user_enrollment}

@router.delete("/declining/{tournaments_id}", status_code=status.HTTP_200_OK)
def user_declining(
    tournaments_id: str,
    db: Session = Depends(get_db),
    user: AppUsers = Depends(get_user_current)
    ) -> Dict[str, object]:
        """
        **Descripcion** : El servicio que retira al usuario a un torneo especifico.
        \n**Excepcion** : 
            \n- El servicio requiere autorizacion via token
            \n- El servicio tiene excepcion si el token es invalido o expiro
            \n- El servicio tiene excepcion cuando se ingresa un tournaments_id inexistente
            \n- El servicio tiene excepcion si el usuario quiere retirarse en un torneo al cual no esta inscrito.
            \n- El servicio tiene excepcion si el usuario quiere retirarse de un torneo que ya empezo.
        """
        tournament = db.query(models.Tournaments).filter(models.Tournaments.id == tournaments_id).first() 
        if not tournament:
            raise exception_tournaments.tournament_not_exist
        enrollment = db.query(EnrollmentUsers).filter(EnrollmentUsers.tournaments_id == tournaments_id, EnrollmentUsers.appuser_id == user.id).first()
        if not enrollment:
            raise exception.user_already_not_registered
        if utils.is_past(tournament.start_date):
            raise exception.user_cannot_withdraw_tournament_already_started
        AppUsers_.decline(db, user, tournament.codigo, enrollment)
        Notificaciones_.send_whatsapp(user.phone , TextToSend.declining(tournament, user.name))
        return {"status": "done"}

@router.put("/plays", status_code=status.HTTP_201_CREATED)
def user_plays_footballgames(
    play_user_list: List[schemas.PlaysUsers],
    db: Session = Depends(get_db),
    user: AppUsers = Depends(get_user_current)
    ) -> Dict[str, object]:
        """
        **Descripcion** : El servicio permite que el usuario inscriba sus tres jugadas de la fecha.
        \n**Excepcion** : 
            \n- El servicio requiere autorizacion via token
            \n- El servicio tiene excepcion si el token es invalido o expiro
            \n- El servicio tiene excepcion si el footballgame_id no existe
            \n- El servicio tiene excepcion si el usuario quiere escribir su jugada a un footballgame de un torneo al cual no esta inscrito.
        """
        for play_user_in in play_user_list:
            footballgame = db.query(models.FootballGames).filter(models.FootballGames.id == play_user_in.football_games_id).first() 
            if not footballgame:
                raise exception_tournaments.footballgames_not_exist
            enrollment = db.query(EnrollmentUsers).filter(EnrollmentUsers.tournaments_id == footballgame.tournament_id, EnrollmentUsers.appuser_id == user.id).first()
            if not enrollment:
                raise exception.user_not_registered_in_footballgame
            AppUsers_.plays_footballgames(db, user, play_user_in)
        return {"status": "done"}

@router.post("/validation/password", status_code=status.HTTP_200_OK)
def user_password_update_validation(
    password_update_validation_in: schemas.PasswordUpdateValidation,
    db: Session = Depends(get_db)
    ) -> Dict[str, object]:
        """
        **Descripcion** : El servicio que valida si el usuario puede cambiar su contraseña.
        \n**Excepcion** : 
            \n- El servicio requiere autorizacion via token
            \n- El servicio tiene excepcion si el token es invalido o expiro
            \n- El servicio tiene excepcion cuando es llamado mas de 3 veces en la ultima media hora
        """
        user = db.query(AppUsers).filter(AppUsers.email == password_update_validation_in.email.lower()).first()
        if not user:
            raise exception.email_unregistered
        current_time = datetime.utcnow()
        ten_weeks_ago = current_time - timedelta(minutes=10)
        number_events_log = db.query(EventLogUser).filter(
            EventLogUser.appuser_id == user.id,
            EventLogUser.due_date > ten_weeks_ago,
            EventLogUser.servicio == "password_update_validation",
            EventLogUser.status == 400
            ).count()
        if number_events_log > 3:
            raise exception.user_max_attemps_validate_password_update 
        AppUsers_.password_update_validation(db, password_update_validation_in, user)
        return {"status": "done"}

@router.post("/otp/resend", status_code=status.HTTP_201_CREATED)
def resend_otp(
    request: Request,
    otp_in: schemas.OtpUsers,
    db: Session = Depends(get_db),
    ) -> Dict[str, object]:
        """
        **Descripcion** : El servicio re-envio de otp.
        \n**Excepcion** : 
            \n- El servicio requiere api-key.
        """
        valid_header(request, ApiKey.USERS)
        _, _ = OtpUsers_.resend(db, otp_in.appuser_id)
        user = db.query(AppUsers).filter(AppUsers.id == otp_in.appuser_id).first()
        EventOtpUsers_.user_should_be_blocked(db, user)
        return {"status": "done", "user_id": otp_in.appuser_id}

@router.post("/otp/validation", status_code=status.HTTP_201_CREATED)
def validation_otp(
    request: Request,
    otp_in: schemas.OtpUsers,
    db: Session = Depends(get_db),
    ) -> Dict[str, object]:
        """
        **Descripcion** : El servicio validacion de otp.
        \n**Excepcion** : 
            \n- El servicio requiere api-key.
        """
        valid_header(request, ApiKey.USERS)
        valido = OtpUsers_.validate(db, otp_in.appuser_id, otp_in.otp)
        appuser = db.query(AppUsers).filter(AppUsers.id == otp_in.appuser_id).first()
        if valido:
            Notificaciones_.send_whatsapp(appuser.phone, TextToSend.login())
        else:
            raise exception.incorrect_otp
        return {"status": "done"}