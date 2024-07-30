import random
from typing import List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.exception import validate_credentials, expired_token
from app.database import CRUD
from app.competitions.models import Matchs, Competitions, Teams, MatchsFootballGames
from app.competitions import schemas
from app.competitions.constants import DataDummyTeam
from app.tournaments.models import FootballGames
from app.notifications.service import NotificacionesAdmin_



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
        objects_list = [compe_3, compe_4, compe_5, compe_6, compe_7, compe_8, compe_9, compe_11, compe_12]
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
                    CRUD.update(db, footballgames_by_day[i])
                    cont = cont + 1
                    match_footballgame = MatchsFootballGames( id_match=matchs_random[i].id , id_footballgames=footballgames_by_day[i].id )
                    CRUD.insert(db, match_footballgame)
                    footballgames_id_match.append(footballgames_by_day[i].id)
        
        teams = db.query(Teams.name).all()
        matchs = db.query(Matchs.hour).all()
        footballgames_id_data_dummy = set(footballgames_id) - set(footballgames_id_match)
        for id in footballgames_id_data_dummy:
            footballgame = db.query(FootballGames).filter(FootballGames.id == id).first()
            footballgame.hour = random.choice(matchs)[0]
            footballgame.home_team = random.choice(teams)[0]
            footballgame.away_team = random.choice(teams)[0]
            CRUD.update(db, footballgame)

        NotificacionesAdmin_.send_whatsapp_incomplete_tournament(db, tournament_id, len(footballgames)-cont)


