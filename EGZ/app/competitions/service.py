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
from app.competitions.utils import format_date, preferred_random_values, get_cod_competitions_most_used

class Match_(CRUD):
    @staticmethod
    def get_list_match_cod_competitions_most_used(day: str, cod_competitions_most_used: List[str], len_footballgames_by_day: int, db: Session):
        matchs = db.query(Matchs).filter(Matchs.date == day, Matchs.cod_competitions.in_(cod_competitions_most_used)).all()
        if len(matchs) == 0:
            matchs = db.query(Matchs).filter(Matchs.date == day).all()
        elif len(matchs) < 3 and len(matchs) > 0:
            match_ = db.query(Matchs).filter(Matchs.date == day, Matchs.cod_competitions.notin_(cod_competitions_most_used)).all()
            matchs = matchs + match_[:3-len(matchs)]
        
        matchs_random = []
        len_loop = 0
        if len(matchs) > 0:
            len_loop = len_footballgames_by_day if len(matchs) > len_footballgames_by_day else len(matchs)
            matchs_random = preferred_random_values( matchs, len_loop)
        return matchs_random, len_loop

    @staticmethod    
    def update_footbalgame_and_match_footballgame(len_loop: int, cont: int, db: Session, matchs: List[Matchs], footballgames_by_day: List[FootballGames]):
        for i in range(len_loop):
            footballgames_by_day[i].hour = matchs[i].hour
            footballgames_by_day[i].home_team = db.query(Teams.name).filter(Teams.id_team == matchs[i].id_team_home).first()[0]
            footballgames_by_day[i].away_team = db.query(Teams.name).filter(Teams.id_team == matchs[i].id_team_away).first()[0]
            footballgames_by_day[i].origin = Origin.API
            CRUD.update(db, footballgames_by_day[i])
            cont = cont + 1
            match_footballgame = MatchsFootballGames( id_match=matchs[i].id , id_footballgames=footballgames_by_day[i].id )
            CRUD.insert(db, match_footballgame)
        return cont

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
    def assignment_api(tournament_id: int, db: Session):
        footballgames = db.query(FootballGames).filter(FootballGames.tournament_id == tournament_id).all()
        days = set([footballgame.date for footballgame in footballgames])
        cont = 0
        cod_competitions_most_used = get_cod_competitions_most_used(days, db)
        for day in days:
            footballgames_by_day = db.query(FootballGames).filter(FootballGames.tournament_id == tournament_id, FootballGames.date == day).all()
            matchs, len_loop = Match_.get_list_match_cod_competitions_most_used(day, cod_competitions_most_used, len(footballgames_by_day), db)
            cont = Match_.update_footbalgame_and_match_footballgame(len_loop, cont, db, matchs, footballgames_by_day)
        return cont

    @staticmethod
    def assignment_random(tournament_id: int, db: Session):
        footballgames = db.query(FootballGames).filter(FootballGames.tournament_id == tournament_id, FootballGames.origin == Origin.HANDBOOK).all()
        teams = db.query(Teams.name).all()
        matchs = db.query(Matchs.hour).all()
        for footballgame in footballgames:
            footballgame.hour = random.choice(matchs)[0]
            footballgame.home_team = random.choice(teams)[0]
            footballgame.away_team = random.choice(teams)[0]
            CRUD.update(db, footballgame)
        return len(footballgames)

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
        objects_list_update = []
        datetime_now = datetime.now(pytz.timezone("America/Lima"))
        datetime_last_moth = datetime_now + timedelta(days=10)
        day_now = str(datetime_now).split(" ")[0]
        day_last_moth = str(datetime_last_moth).split(" ")[0]
        for competition in competitions:
            uri = API_FOOTBALL_DATA + f'competitions/{competition[2]}/matches/?dateFrom={day_now}&dateTo={day_last_moth}'
            headers = { 'X-Auth-Token': KEY_FOOTBALL_DATA }
            response = requests.get(uri, headers=headers).json()
            for match in response["matches"]:
                list_datetime = str(datetime.strptime(match["utcDate"], '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc) - timedelta(hours=5)).split(" ")
                matchh = db.query(Matchs).filter(Matchs.id_match == match["id"]).first()
                date_api = format_date(list_datetime[0])
                hour_api = list_datetime[1][:8]
                if matchh:
                    objects_list_update = Competitions_.update_match(matchh, date_api, hour_api, objects_list_update, db)
                else:
                    match_ = Matchs(
                        id_match=match["id"],
                        cod_competitions=match["competition"]["code"],
                        date=date_api,
                        hour=hour_api,
                        id_team_home=match["homeTeam"]["id"],
                        id_team_away=match["awayTeam"]["id"],
                        score_home=None,
                        score_away=None,
                        status=match["status"]
                    )
                    objects_list.append(match_)
        CRUD.bulk_insert(db, objects_list)

        NotificacionesAdmin_.send_whatsapp_update_match(objects_list_update ,numb_match = len(objects_list_update), start_date = day_now, end_date = day_last_moth)
        NotificacionesAdmin_.send_whatsapp_adding_match(numb_match = len(objects_list), start_date = day_now, end_date = day_last_moth)

    @staticmethod
    def checkout_match(footballgames: List[FootballGames], db: Session):
        text = ""
        text_timed = ""
        for footballgame in footballgames:
            match_id = db.query(MatchsFootballGames.id_match).filter(MatchsFootballGames.id_footballgames == footballgame.id).first()[0]
            match = db.query(Matchs).filter(Matchs.id == match_id).first()
            uri = API_FOOTBALL_DATA + f'matches/{match.id_match}'
            headers = { 'X-Auth-Token': KEY_FOOTBALL_DATA }
            response = requests.get(uri, headers=headers).json()
            list_datetime = str(datetime.strptime(response["utcDate"], '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc) - timedelta(hours=5)).split(" ")
            home_team = footballgame.home_team
            away_team = footballgame.away_team
            if footballgame.date == format_date(list_datetime[0]) and (footballgame.hour != list_datetime[1][:8]):
                footballgame_hour_temp = footballgame.hour
                footballgame.hour = list_datetime[1][:8]
                match.hour = list_datetime[1][:8]
                text = text + f"*{home_team} - {away_team}*\nFootballGames : {footballgame.date} {footballgame_hour_temp}\nApi_new : {format_date(list_datetime[0])} {list_datetime[1][:8]}\n\n"
            elif footballgame.date != format_date(list_datetime[0]):
                footballgame_hour_temp = footballgame.hour
                footballgame_date_temp = footballgame.date
                footballgame.hour = None
                footballgame.date = None
                footballgame.away_team = None
                footballgame.home_team = None
                match.date = format_date(list_datetime[0])
                match.hour = list_datetime[1][:8]
                text_timed = text_timed + f"*{home_team} - {away_team}*\nCodigo: *{footballgame.codigo}*\nFootballGames : {footballgame_date_temp} {footballgame_hour_temp}\nApi_new : {format_date(list_datetime[0])} {list_datetime[1][:8]}\n\n"
            CRUD.update(db, footballgame)
            CRUD.update(db, match)
        if len(footballgames) > 0:
            NotificacionesAdmin_.send_whatsapp_checkout_match_timed(text_timed)
            NotificacionesAdmin_.send_whatsapp_checkout_match(text)

    @staticmethod
    def update_match(match: Matchs, date_api: str, hour_api: str, objects_list_update: list, db: Session):
        dict_temp = None
        if match.date == date_api and match.hour != hour_api:
            hour_temp = match.hour
            match.hour = hour_api
            CRUD.update(db ,match)   
            match_footballgame = db.query(MatchsFootballGames).filter(MatchsFootballGames.id_match == match.id).first()
            if match_footballgame:
                footballgame = db.query(FootballGames).filter(FootballGames.id == match_footballgame.id_footballgames).first()
                dict_temp = {
                    "codigo_match":match.id,
                    "codigo_footballgame":footballgame.codigo,
                    "status":"API-MATCH , RANDOM-FOOTBALLGAME",
                    "home_team":{"old":footballgame.home_team,"new":footballgame.home_team},
                    "away_team":{"old":footballgame.away_team,"new":footballgame.away_team},
                    "day":{"old":footballgame.date,"new":footballgame.date},
                    "hour":{"old":footballgame.hour,"new":hour_api}
                }
                footballgame.hour = hour_api
                CRUD.update(db ,footballgame)
            else:
                home_team = db.query(Teams.name).filter(Teams.id_team == match.id_team_home).first()[0]
                away_team = db.query(Teams.name).filter(Teams.id_team == match.id_team_away).first()[0]
                dict_temp = {
                    "codigo_match":match.id,
                    "codigo_footballgame":None,
                    "status":"API-MATCH",
                    "home_team":{"old":home_team,"new":home_team},
                    "away_team":{"old":away_team,"new":away_team},
                    "day":{"old":match.date,"new":match.date},
                    "hour":{"old":hour_temp,"new":hour_api}
                }
        elif match.date != date_api and match.hour != hour_api:
            hour_temp = match.hour
            date_temp = match.date
            match.hour = hour_api
            match.date = date_api
            CRUD.update(db ,match)  
            match_footballgame = db.query(MatchsFootballGames).filter(MatchsFootballGames.id_match == match.id).first()
            if match_footballgame:
                footballgame = db.query(FootballGames).filter(FootballGames.id == match_footballgame.id_footballgames).first()
                home_team_temp = footballgame.home_team
                away_team_temp = footballgame.away_team
                hour_temp = footballgame.hour

                teams = db.query(Teams.name).all()
                matchs = db.query(Matchs.hour).all()
                footballgame.hour = random.choice(matchs)[0]
                footballgame.home_team = random.choice(teams)[0]
                footballgame.away_team = random.choice(teams)[0]
                footballgame.origin = Origin.HANDBOOK
                dict_temp = {
                    "codigo_match":match.id,
                    "codigo_footballgame":footballgame.codigo,
                    "status":"API-MATCH , RANDOM-FOOTBALLGAME",
                    "home_team":{"old":home_team_temp,"new":footballgame.home_team},
                    "away_team":{"old":away_team_temp,"new":footballgame.away_team},
                    "day":{"old":date_temp,"new":footballgame.date},
                    "hour":{"old":hour_temp,"new":footballgame.hour}
                }
                CRUD.update(db, footballgame)
            else:
                home_team = db.query(Teams.name).filter(Teams.id_team == match.id_team_home).first()[0]
                away_team = db.query(Teams.name).filter(Teams.id_team == match.id_team_away).first()[0]
                dict_temp = {
                    "codigo_match":match.id,
                    "codigo_footballgame":None,
                    "status":"API-MATCH",
                    "home_team":{"old":home_team,"new":home_team},
                    "away_team":{"old":away_team,"new":away_team},
                    "day":{"old":date_temp,"new":date_api},
                    "hour":{"old":hour_temp,"new":hour_api}
                }

        if dict_temp is not None:
            objects_list_update.append(dict_temp)

        return objects_list_update

