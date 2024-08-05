import random
import requests
import pytz
from typing import List
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from app.database import CRUD
from app.competitions.models import Matchs, Competitions, Teams, MatchsFootballGames
from app.tournaments.models import FootballGames
from app.tournaments.constants import Origin
from app.notifications.service import NotificacionesAdmin_
from app.config import API_FOOTBALL_DATA, KEY_FOOTBALL_DATA
from app.competitions.utils import format_date

class Competitions_(CRUD):
    @staticmethod
    def create(db: Session):
        compe_1 = Competitions(
            id_competition=2000,
            name="FIFA World Cup",
            code="WC",
            type="CUP",
            emblem="https://crests.football-data.org/qatar.png"
        )
        compe_2 = Competitions(
            id_competition=2001,
            name="UEFA Champions League",
            code="CL",
            type="CUP",
            emblem="https://crests.football-data.org/CL.png"
        )
        compe_3 = Competitions(
            id_competition=2002,
            name="Bundesliga",
            code="BL1",
            type="LEAGUE",
            emblem="https://crests.football-data.org/BL1.png"
        )
        compe_4 = Competitions(
            id_competition=2003,
            name="Eredivisie",
            code="DED",
            type="LEAGUE",
            emblem="https://crests.football-data.org/ED.png"
        )
        compe_5 = Competitions(
            id_competition=2013,
            name="Campeonato Brasileiro Série A",
            code="BSA",
            type="LEAGUE",
            emblem="https://crests.football-data.org/bsa.png"
        )
        compe_6 = Competitions(
            id_competition=2014,
            name="Primera Division",
            code="PD",
            type="LEAGUE",
            emblem="https://crests.football-data.org/PD.png"
        )
        compe_7 = Competitions(
            id_competition=2015,
            name="Ligue 1",
            code="FL1",
            type="LEAGUE",
            emblem="https://crests.football-data.org/FL1.png"
        )
        compe_8 = Competitions(
            id_competition=2016,
            name="Championship",
            code="ELC",
            type="LEAGUE",
            emblem="https://crests.football-data.org/ELC.png"
        )
        compe_9 = Competitions(
            id_competition=2017,
            name="Primeira Liga",
            code="PPL",
            type="LEAGUE",
            emblem="https://crests.football-data.org/PPL.png"
        )
        compe_10 = Competitions(
            id_competition=2018,
            name="European Championship",
            code="EC",
            type="CUP",
            emblem="https://crests.football-data.org/ec.png"
        )
        compe_11 = Competitions(
            id_competition=2019,
            name="Serie A",
            code="SA",
            type="LEAGUE",
            emblem="https://crests.football-data.org/SA.png"
        )
        compe_12 = Competitions(
            id_competition=2021,
            name="Premier League",
            code="PL",
            type="LEAGUE",
            emblem="https://crests.football-data.org/PL.png"
        )
        compe_13 = Competitions(
            id_competition=2101,
            name="Primera División",
            code="PPD",
            type="LEAGUE",
            emblem="https://upload.wikimedia.org/wikipedia/commons/6/62/Liga_de_F%C3%BAtbol_Profesional_-_Liga_1_%28Per%C3%BA%29.jpg"
        )
        compe_14 = Competitions(
            id_competition=2048,
            name="Primera División",
            code="CPD",
            type="LEAGUE",
            emblem="https://crests.football-data.org/cpd.png"
        )
        compe_15 = Competitions(
            id_competition=2024,
            name="Liga Profesional",
            code="ASL",
            type="LEAGUE",
            emblem="https://crests.football-data.org/LPDF.svg"
        )
        objects_list = [compe_3, compe_4, compe_5, compe_6, compe_7, compe_8, compe_9, compe_11, compe_12, compe_13, compe_14, compe_15]
        CRUD.bulk_insert(db, objects_list)
    
    @staticmethod
    def assignment(tournament_id: int, db: Session):
        footballgames = db.query(FootballGames).filter(FootballGames.tournament_id == tournament_id).all()
        days = set([footballgame.date for footballgame in footballgames])
        cont = 0 
        footballgames_id =  [footballgame.id for footballgame in footballgames]
        footballgames_id_match = []
        for day in days:
            footballgames_by_day = db.query(FootballGames).filter(FootballGames.tournament_id == tournament_id, FootballGames.date == day).all()
            matchs = db.query(Matchs).filter(Matchs.date == day).all()    
            if len(matchs) > 0:
                len_loop = len(footballgames_by_day) if len(matchs) > len(footballgames_by_day) else len(matchs)
                matchs_random = random.sample( matchs, len_loop)
                for i in range(len_loop):
                    footballgames_by_day[i].hour = matchs_random[i].hour
                    footballgames_by_day[i].home_team = db.query(Teams.name).filter(Teams.id_team == matchs_random[i].id_team_home).first()[0]
                    footballgames_by_day[i].away_team = db.query(Teams.name).filter(Teams.id_team == matchs_random[i].id_team_away).first()[0]
                    footballgames_by_day[i].origin = Origin.API
                    CRUD.update(db, footballgames_by_day[i])
                    cont = cont + 1
                    match_footballgame = MatchsFootballGames( id_match=matchs_random[i].id , id_footballgames=footballgames_by_day[i].id )
                    CRUD.insert(db, match_footballgame)
                    footballgames_id_match.append(footballgames_by_day[i].id)
        
        # teams = db.query(Teams.name).all()
        # matchs = db.query(Matchs.hour).all()
        # footballgames_id_data_dummy = set(footballgames_id) - set(footballgames_id_match)
        # for id in footballgames_id_data_dummy:
        #     footballgame = db.query(FootballGames).filter(FootballGames.id == id).first()
        #     footballgame.hour = random.choice(matchs)[0]
        #     footballgame.home_team = random.choice(teams)[0]
        #     footballgame.away_team = random.choice(teams)[0]
        #     CRUD.update(db, footballgame)
        NotificacionesAdmin_.send_whatsapp_incomplete_tournament(db, tournament_id, len(footballgames)-cont)

    @staticmethod
    def add_teams(competitions: List[Competitions], db: Session):
        objects_list = []
        for competition in competitions:
            uri = API_FOOTBALL_DATA + f'competitions/{competition[2]}/teams'
            headers = { 'X-Auth-Token':  KEY_FOOTBALL_DATA}
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

    @staticmethod
    def add_match(competitions: List[Competitions], db: Session):
        objects_list = []
        datetime_now = datetime.now(pytz.timezone("America/Lima"))
        datetime_last_moth = datetime_now + timedelta(days=30)
        day_now = str(datetime_now).split(" ")[0]
        day_last_moth = str(datetime_last_moth).split(" ")[0]
        for competition in competitions:
            uri = API_FOOTBALL_DATA + f'competitions/{competition[2]}/matches/?dateFrom={day_now}&dateTo={day_last_moth}'
            headers = { 'X-Auth-Token': KEY_FOOTBALL_DATA }
            response = requests.get(uri, headers=headers).json()
            for match in response["matches"]:
                list_datetime = str(datetime.strptime(match["utcDate"], '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc) - timedelta(hours=5)).split(" ")
                matchh = db.query(Matchs).filter(Matchs.id_match == match["id"]).first()
                if matchh:
                    pass
                else:
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

        NotificacionesAdmin_.send_whatsapp_adding_match(numb_match = len(objects_list), start_date = day_now, end_date = day_last_moth)