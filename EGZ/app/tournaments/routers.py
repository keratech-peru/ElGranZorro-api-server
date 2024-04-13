from fastapi import APIRouter, Depends, status
from fastapi.encoders import jsonable_encoder
from typing import Dict
from sqlalchemy.orm import Session
from app.users.models import AppUsers, EnrollmentUsers, PlaysUsers
from app.users import exception as exception_users
from app.tournaments.models import Tournaments, FootballGames
from app.tournaments.service import Tournaments_
from app.tournaments import exception
from app.database import get_db
from app.security import get_user_current
from app.config import ApiKey, TOKEN_SCONDS_EXP




router = APIRouter(prefix="/tournaments", tags=["tournaments"])

@router.get("/", status_code=status.HTTP_200_OK)
def tournaments_get(
    db: Session = Depends(get_db),
    user: AppUsers = Depends(get_user_current)
    ) -> Dict[str, object]:
        """
        **Descripcion** : El servicio brinda la informacion de todos los torneos disponibles,
        se envia un booleano para saber si el usuario esta inscrito al torneo o no.
        \n**Excepcion** : 
            \n- El servicio requiere autorizacion via token
            \n- El servicio tiene excepcion si el token es invalido o expiro
        """
        ### Se debe considerar solo retornar los torneos activos
        tournaments = Tournaments_.list_all(db, user.id)
        return {"status": "done", "data": tournaments}

@router.get("/user", status_code=status.HTTP_200_OK)
def tournaments_user(
    db: Session = Depends(get_db),
    user: AppUsers = Depends(get_user_current)
    ) -> Dict[str, object]:
        """
        **Descripcion** : El servicio brinda la informacion de todos los torneo en el cual el usuario esta inscrito.
        \n**Excepcion** : 
            \n- El servicio requiere autorizacion via token
            \n- El servicio tiene excepcion si el token es invalido o expiro
        """
        enrollment_tournaments = db.query(EnrollmentUsers.tournaments_id).filter(EnrollmentUsers.appuser_id == user.id).all()
        list_tournaments_id = [tournament[0] for tournament in enrollment_tournaments]
        tournaments = db.query(Tournaments).filter(Tournaments.id.in_(list_tournaments_id)).all()
        return {"status": "done", "tournaments": tournaments}

@router.get("/{tournament_id}", status_code=status.HTTP_200_OK)
def tournament_user(
    tournament_id: str,
    db: Session = Depends(get_db),
    user: AppUsers = Depends(get_user_current)
    ) -> Dict[str, object]:
        """
        **Descripcion** : El servicio muestra la informacion de un torneo especifico - torneo - jugadas del dia - jugadas pasadas
        \n**Excepcion** : 
            \n- El servicio requiere autorizacion via token
            \n- El servicio tiene excepcion si el token es invalido o expiro
            \n- El servicio tiene excepcion si el torneo no existe
            \n- El servicio tiene excepcion si el usuario no esta inscrito en el torneo
        """
        tournament = db.query(Tournaments).filter(Tournaments.id == tournament_id).first() 
        if not tournament:
            raise exception.tournament_not_exist
        enrollment = db.query(EnrollmentUsers).filter(EnrollmentUsers.tournaments_id == tournament_id, EnrollmentUsers.appuser_id == user.id).first()
        if not enrollment:
            raise exception_users.user_not_enrolled_in_tournament
        football_of_the_day, football_past = Tournaments_.get_footballgames(db, tournament_id, user.id)
        return {"status": "done", "tournament":tournament ,"football_of_the_day":football_of_the_day, "football_past":football_past }