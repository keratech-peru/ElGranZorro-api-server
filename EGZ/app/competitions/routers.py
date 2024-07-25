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
from datetime import datetime, timedelta, timezone
from app.competitions.models import Competitions, Teams, Matchs
from app.competitions.utils import format_date
from app.competitions.service import Competitions_
import requests
import pytz

router = APIRouter(prefix="/competitions", tags=["competitions"])

@router.get("/teams", status_code=status.HTTP_200_OK)
def teams(
    db: Session = Depends(get_db)
    ) -> Dict[str, object]:
        #Competitions_.create(db)
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
        datetime_last_moth = datetime_now + timedelta(days=30)
        day_now = str(datetime_now).split(" ")[0]
        day_last_moth = str(datetime_last_moth).split(" ")[0]
        for competition in competitions:
            uri = f'https://api.football-data.org/v4/competitions/{competition[2]}/matches/?dateFrom={day_now}&dateTo={day_last_moth}'
            headers = { 'X-Auth-Token': '17e9ddf85c184860a6c2a004ed4d0e3d' }
            response = requests.get(uri, headers=headers).json()
            for match in response["matches"]:
                list_datetime = str(datetime.strptime(match["utcDate"], '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc) - timedelta(hours=5)).split(" ")
                match_ = Matchs(
                    id_match=match["id"],
                    cod_competitions=match["competition"]["code"],
                    date=format_date(list_datetime[0]),
                    hour=list_datetime[1][:8],
                    id_team_home=match["homeTeam"]["id"],
                    id_team_away=match["awayTeam"]["id"],
                    score_home=None,
                    score_away=None,
                    status=match["status"]
                )
                objects_list.append(match_)
        CRUD.bulk_insert(db, objects_list)
        return {"status":"done"}