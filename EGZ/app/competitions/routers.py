from fastapi import APIRouter, Depends, status, Request
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from typing import Dict, List
from sqlalchemy.orm import Session
from app.users.service import AppUsers_, OtpUsers_, EventOtpUsers_
from app.users import schemas
from app.users.models import AppUsers, EnrollmentUsers, PlaysUsers, EventLogUser
from app.tournaments import models, utils, exception as exception_tournaments
from app.users import exception
from app.database import get_db, CRUD
from app.security import create_token, valid_header, get_user_current
from app.config import ApiKey, TOKEN_SCONDS_EXP
from datetime import datetime, timedelta
from app.competitions.models import Competitions, Teams
from app.competitions.service import Competitions_
import requests
import pytz

router = APIRouter(prefix="/competitions", tags=["competitions"])

@router.get("/teams", status_code=status.HTTP_200_OK)
def teams(
    db: Session = Depends(get_db)
    ) -> Dict[str, object]:

        competitions = db.query(Competitions.id, Competitions.id_competition, Competitions.code).all()
        objects_list = []
        for competition in competitions:
            uri = f'https://api.football-data.org/v4/competitions/{competition[2]}/teams'
            headers = { 'X-Auth-Token': '17e9ddf85c184860a6c2a004ed4d0e3d' }
            response = requests.get(uri, headers=headers).json()

            for team in response["teams"]:
                team_ = Teams(
                    competitions_id=competition[0],
                    id_team=team["id"],
                    name=team["name"],
                    short_name=team["shortName"],
                    emblem=team["crest"]
                )
                objects_list.append(team_)
        CRUD.bulk_insert(db, objects_list)
        return {"status":"done"}

@router.get("/competition", status_code=status.HTTP_200_OK)
def teams(
    db: Session = Depends(get_db)
    ) -> Dict[str, object]:
        competitions = db.query(Competitions.id, Competitions.id_competition, Competitions.code).all()
        objects_list = []

        datetime_now = datetime.now(pytz.timezone("America/Lima"))
        print(datetime_now)
        for competition in competitions:
            uri = f'https://api.football-data.org/v4/competitions/{competition[2]}/matches?dateTo=2024-08-31&dateFrom=2024-07-24'
            headers = { 'X-Auth-Token': '17e9ddf85c184860a6c2a004ed4d0e3d' }
            response = requests.get(uri, headers=headers).json()
            for match in response["matches"]:
                print( match["homeTeam"]["name"], " - ", match["awayTeam"]["name"] , " --> " , match["utcDate"])



        return {"status":"done"}