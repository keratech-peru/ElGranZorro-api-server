from app.database import CRUD
from app.users.models import PlaysUsers
from app.tournaments.models import Tournaments, FootballGames, GroupStage, ConfrontationsGroupStage, ConfrontationsKeyStage
from app.tournaments import schemas
from app.tournaments.constants import GROUPS
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List 
from datetime import datetime, timezone, timedelta
import pytz
from fastapi.encoders import jsonable_encoder
class Tournaments_(CRUD):
    @staticmethod
    def create(tourmament_in: schemas.Tourmaments, db: Session) -> Tournaments:
        new_tourmament = Tournaments(**tourmament_in.dict())
        CRUD.insert(db, new_tourmament)
        return new_tourmament
    
    def list_all(db: Session) -> List[Tournaments]:
        return db.query(Tournaments).all()
    
    def get_footballgames(db: Session, tournament_id: int, user_id: int):
        footballgames = db.query(FootballGames).filter(FootballGames.tournament_id == tournament_id).all()
        datetime_now = datetime.now(pytz.timezone("America/Lima"))
        football_of_the_day = []
        football_past = []
        for footballgame in footballgames:
            dif = datetime_now - datetime.strptime(footballgame.date, '%d/%m/%y').replace(tzinfo=timezone.utc)
            footballgame_dict = footballgame.__dict__
            play_user = db.query(PlaysUsers).filter(PlaysUsers.id == footballgame.id,PlaysUsers.appuser_id == user_id).first()
            if int(dif.days) == 0:
                del footballgame_dict["home_score"]
                del footballgame_dict["away_score"]
                footballgame_dict["score_local_user"] = play_user["score_local"] if play_user else None
                footballgame_dict["score_visit_user"] = play_user["score_local"] if play_user else None
                football_of_the_day.append(footballgame_dict)
            if int(dif.days) > 0:
                footballgame_dict["score_local_user"] = play_user["score_local"] if play_user else None
                footballgame_dict["score_visit_user"] = play_user["score_local"] if play_user else None
                football_past.append(footballgame_dict)
        return football_of_the_day, football_past

class FootballGames_(CRUD):
    @staticmethod
    def create(football_game_in: schemas.FootballGames, db: Session) -> FootballGames:
        new_football_game = FootballGames(**football_game_in.dict())
        CRUD.insert(db, new_football_game)
        return new_football_game

    def update(footballgame_id:int , update_footballgame_in: schemas.UpdateFootballGames, db: Session) :
        footballgame = db.query(FootballGames).filter(FootballGames.id == footballgame_id).first()
        if footballgame:
            footballgame.home_team = update_footballgame_in.home_team
            footballgame.away_team = update_footballgame_in.away_team
            footballgame.home_score = update_footballgame_in.home_score
            footballgame.away_score = update_footballgame_in.away_score
            CRUD.update(db, footballgame)       

    def list_all(db: Session) -> List[FootballGames]:
        # db.query(FootballGames, Tournaments.codigo).join(Tournaments).all()
        data = jsonable_encoder(db.query(FootballGames).all())
        for i in range(len(data)):
            data[i]["tournament_codigo"] = db.query(Tournaments.codigo).filter(Tournaments.id == data[i]["tournament_id"]).first()[0]
        return data
    
    def create_groups_stage(id: int , codigo:str, start_date:str, db: Session):
        list_footballgames = []
        cont = 0
        for i in range(1,4):
            for j in range(1,4):
                cont = cont + 1
                date = datetime.strptime(start_date, '%d/%m/%y') + timedelta(days = i-1)
                obj_temp = schemas.FootballGames(
                    codigo=codigo+'GP'+str(cont),
                    tournament_id=id,
                    tournament_stage=f"Fecha {i} - GRUPOS",
                    date=datetime.strftime(date,'%d/%m/%y'),
                    type_footballgames= "RESULT" if i*j%2 == 0 else "SCORE",
                    home_team=None,
                    away_team=None,
                    home_score=None,
                    away_score=None                                                                                     
                )
                list_footballgames.append(FootballGames(**obj_temp.dict()))
        CRUD.bulk_insert(db, list_footballgames)
        
        list_groupstage = []
        for group in GROUPS:
            for i in range(1,5):
                obj_temp = schemas.GroupStage(tournament_cod=codigo, group=group, position=i)
                list_groupstage.append(GroupStage(**obj_temp.dict()))
        CRUD.bulk_insert(db, list_groupstage)

        Confrontations_.create_groups_stage(id, db, codigo)

    def create_eighths_stage(id: int , codigo:str, start_date:str, db: Session):
        list_footballgames = []
        cont = 0
        for i in range(1,4):
            cont = cont + 1
            date = datetime.strptime(start_date, '%d/%m/%y') + timedelta(days = 3)
            obj_temp = schemas.FootballGames(
                codigo=codigo+'OC'+str(cont),
                tournament_id=id,
                tournament_stage=f"OCTAVOS",
                date=datetime.strftime(date,'%d/%m/%y'),
                type_footballgames= "RESULT" if i%2 == 0 else "SCORE",
                home_team=None,
                away_team=None,
                home_score=None,
                away_score=None                                                                                     
            )
            list_footballgames.append(FootballGames(**obj_temp.dict()))
        CRUD.bulk_insert(db, list_footballgames)

        Confrontations_.create_eighths_stage(id, db, codigo)

    def create_quarter_stage(id: int , codigo:str, start_date:str, db: Session):
        list_footballgames = []
        cont = 0
        for i in range(1,4):
            cont = cont + 1
            date = datetime.strptime(start_date, '%d/%m/%y') + timedelta(days = 4)
            obj_temp = schemas.FootballGames(
                codigo=codigo+'CU'+str(cont),
                tournament_id=id,
                tournament_stage=f"CUARTOS",
                date=datetime.strftime(date,'%d/%m/%y'),
                type_footballgames= "RESULT" if i%2 == 0 else "SCORE",
                home_team=None,
                away_team=None,
                home_score=None,
                away_score=None                                                                                     
            )
            list_footballgames.append(FootballGames(**obj_temp.dict()))
        CRUD.bulk_insert(db, list_footballgames)

        Confrontations_.create_quarter_stage(id, db, codigo)

    def create_semifinal_stage(id: int , codigo:str, start_date:str, db: Session):
        list_footballgames = []
        cont = 0
        for i in range(1,4):
            cont = cont + 1
            date = datetime.strptime(start_date, '%d/%m/%y') + timedelta(days = 5)
            obj_temp = schemas.FootballGames(
                codigo=codigo+'SF'+str(cont),
                tournament_id=id,
                tournament_stage=f"SEMI-FINAL",
                date=datetime.strftime(date,'%d/%m/%y'),
                type_footballgames= "RESULT" if i%2 == 0 else "SCORE",
                home_team=None,
                away_team=None,
                home_score=None,
                away_score=None                                                                                     
            )
            list_footballgames.append(FootballGames(**obj_temp.dict()))
        CRUD.bulk_insert(db, list_footballgames)

        Confrontations_.create_semifinal_stage(id, db, codigo)

    def create_final_stage(id: int , codigo:str, start_date:str, db: Session):
        list_footballgames = []
        cont = 0
        for i in range(1,6):
            cont = cont + 1
            date = datetime.strptime(start_date, '%d/%m/%y') + timedelta(days = 6)
            obj_temp = schemas.FootballGames(
                codigo=codigo+'FI'+str(cont),
                tournament_id=id,
                tournament_stage=f"FINAL",
                date=datetime.strftime(date,'%d/%m/%y'),
                type_footballgames= "RESULT" if i%2 == 0 else "SCORE",
                home_team=None,
                away_team=None,
                home_score=None,
                away_score=None                                                                                     
            )
            list_footballgames.append(FootballGames(**obj_temp.dict()))
        CRUD.bulk_insert(db, list_footballgames)
        Confrontations_.create_final_stage(id, db, codigo)

class Confrontations_(CRUD):
    @staticmethod
    def create_groups_stage(tournament_id: int ,db: Session, tournament_cod: str):
        list_confrontations = []
        for group in GROUPS:
            group_stage = db.query(GroupStage).filter(GroupStage.group == group).all()
            confrontations_group_stage = [ 
                [group_stage[0].id, group_stage[1].id, tournament_cod+'GP'+'1'],
                [group_stage[0].id, group_stage[1].id, tournament_cod+'GP'+'2'],
                [group_stage[0].id, group_stage[1].id, tournament_cod+'GP'+'3'],
                [group_stage[2].id, group_stage[3].id, tournament_cod+'GP'+'1'],
                [group_stage[2].id, group_stage[3].id, tournament_cod+'GP'+'2'],
                [group_stage[2].id, group_stage[3].id, tournament_cod+'GP'+'3'],

                [group_stage[0].id, group_stage[2].id, tournament_cod+'GP'+'4'],
                [group_stage[0].id, group_stage[2].id, tournament_cod+'GP'+'5'],
                [group_stage[0].id, group_stage[2].id, tournament_cod+'GP'+'6'],
                [group_stage[1].id, group_stage[3].id, tournament_cod+'GP'+'4'],
                [group_stage[1].id, group_stage[3].id, tournament_cod+'GP'+'5'],
                [group_stage[1].id, group_stage[3].id, tournament_cod+'GP'+'6'],

                [group_stage[0].id, group_stage[3].id, tournament_cod+'GP'+'7'],
                [group_stage[0].id, group_stage[3].id, tournament_cod+'GP'+'8'],
                [group_stage[0].id, group_stage[3].id, tournament_cod+'GP'+'9'],
                [group_stage[1].id, group_stage[2].id, tournament_cod+'GP'+'7'],
                [group_stage[1].id, group_stage[2].id, tournament_cod+'GP'+'8'],
                [group_stage[1].id, group_stage[2].id, tournament_cod+'GP'+'9'],
            ]
            for confrontation in confrontations_group_stage:
                obj_temp = schemas.ConfrontationsGroupStage(
                    group_stage_1_id=confrontation[0],
                    group_stage_2_id=confrontation[1],
                    football_games_cod=confrontation[2],
                    tournaments_id=tournament_id
                )
                list_confrontations.append(ConfrontationsGroupStage(**obj_temp.dict()))
        CRUD.bulk_insert(db, list_confrontations)
    
    def create_eighths_stage(tournament_id: int, db: Session, cod_tournament: str):
        list_confrontations = []
        for _ in range(8):
            codigos = [ cod_tournament+'OC'+'1', cod_tournament+'OC'+'2', cod_tournament+'OC'+'3']
            for cod in codigos:
                obj_temp = schemas.ConfrontationsKeyStage(
                    football_games_cod=cod,
                    tournaments_id=tournament_id
                )
                list_confrontations.append(ConfrontationsKeyStage(**obj_temp.dict()))
        CRUD.bulk_insert(db, list_confrontations)
    
    def create_quarter_stage(tournament_id: int, db: Session, cod_tournament: str):
        list_confrontations = []
        for _ in range(4):
            codigos = [ cod_tournament+'CU'+'1', cod_tournament+'CU'+'2', cod_tournament+'CU'+'3']
            for cod in codigos:
                obj_temp = schemas.ConfrontationsKeyStage(
                    football_games_cod=cod,
                    tournaments_id=tournament_id
                )
                list_confrontations.append(ConfrontationsKeyStage(**obj_temp.dict()))
        CRUD.bulk_insert(db, list_confrontations)

    def create_semifinal_stage(tournament_id: int, db: Session, cod_tournament: str):
        list_confrontations = []
        for _ in range(2):
            codigos = [ cod_tournament+'SF'+'1', cod_tournament+'SF'+'2', cod_tournament+'SF'+'3']
            for cod in codigos:
                obj_temp = schemas.ConfrontationsKeyStage(
                    football_games_cod=cod,
                    tournaments_id=tournament_id
                )
                list_confrontations.append(ConfrontationsKeyStage(**obj_temp.dict()))
        CRUD.bulk_insert(db, list_confrontations)

    def create_final_stage(tournament_id: int, db: Session, cod_tournament: str):
        list_confrontations = []
        codigos = [ cod_tournament+'FI'+'1', cod_tournament+'FI'+'2', cod_tournament+'FI'+'3', cod_tournament+'FI'+'4', cod_tournament+'FI'+'5' ]
        for cod in codigos:
            obj_temp = schemas.ConfrontationsKeyStage(
                football_games_cod=cod,
                tournaments_id=tournament_id
            )
            list_confrontations.append(ConfrontationsKeyStage(**obj_temp.dict()))
        CRUD.bulk_insert(db, list_confrontations)

    def ids_point_play_and_not_play_group_stage(db: Session, footballgame_cod: str, appuser_id_plays: List[int], point_plays: List[int]):
        group_stage_ids =  db.query(GroupStage.id).filter(GroupStage.tournament_cod == footballgame_cod[:-3], GroupStage.appuser_id.in_(appuser_id_plays)).all()
        group_stage_ids_all =  db.query(GroupStage.id).filter(GroupStage.tournament_cod == footballgame_cod[:-3]).all()   
        ids_list = [ group_stage_id[0] for group_stage_id in  group_stage_ids ]
        ids_list_all = [ group_stage_id[0] for group_stage_id in  group_stage_ids_all ]
        ids_point_play = { ids_list[i]:point_plays[i] for i in range(len(group_stage_ids)) }
        ids_point_not_play = { ids:0 for ids in ids_list_all if ids not in ids_list }
        return ids_point_play , ids_point_not_play

    def allocation_points_group_stage(db: Session, appuser_id_point_plays, footballgame_cod: str):
        appuser_id_plays = list(appuser_id_point_plays.keys())
        point_plays = list(appuser_id_point_plays.values())
        ids_point_play , ids_point_not_play = Confrontations_.ids_point_play_and_not_play_group_stage(db,footballgame_cod,appuser_id_plays, point_plays)
        dict_ids_point = ids_point_play | ids_point_not_play
        group_stage_ids_list = list(dict_ids_point.keys())
        confrontations_group_stage = db.query(ConfrontationsGroupStage).filter(
            or_(ConfrontationsGroupStage.group_stage_1_id.in_(group_stage_ids_list) , ConfrontationsGroupStage.group_stage_2_id.in_(group_stage_ids_list)),
            ConfrontationsGroupStage.football_games_cod == footballgame_cod
            ).all()
        for confront in confrontations_group_stage:
            if confront.group_stage_1_id in group_stage_ids_list:
                confront.points_1 = dict_ids_point[confront.group_stage_1_id]
                CRUD.update(db, confront)
            if confront.group_stage_2_id in group_stage_ids_list:
                confront.points_2 = dict_ids_point[confront.group_stage_2_id]
                CRUD.update(db, confront)

    def orden_update_group_stage(db: Session, cod_tournament: str):
        for group_ in GROUPS:
            groups_stage =  db.query(GroupStage).filter(GroupStage.tournament_cod == cod_tournament, GroupStage.group == group_).all()
            group_stage_point = {}
            for group in groups_stage:
                confront_group_stage = db.query(ConfrontationsGroupStage).filter(
                    or_(ConfrontationsGroupStage.group_stage_1_id.in_([group.id]) ,
                    ConfrontationsGroupStage.group_stage_2_id.in_([group.id]))).all()
                point = 0
                for confront in confront_group_stage:
                    if confront.group_stage_1_id == group.id:
                        point = point + confront.points_1 if confront.points_1 else 0
                    if confront.group_stage_2_id == group.id:
                        point = point + confront.points_2 if confront.points_2 else 0
                group_stage_point[group.id] = point
            
            group_stage_id_and_points_orden = sorted(group_stage_point.items(), key=lambda x: x[1], reverse=True)
            for i in range(1,len(group_stage_id_and_points_orden)+1):
                groups_stage =  db.query(GroupStage).filter(GroupStage.id == group_stage_id_and_points_orden[i-1][0]).first()
                groups_stage.position = i
                CRUD.update(db, groups_stage)
    
    def registration_teams_eighths(db, cod_tournament: str):
        groups_stage_first_place =  db.query(GroupStage).filter(GroupStage.tournament_cod == cod_tournament, GroupStage.position == 1).all()
        groups_stage_first_place_dict = {groups_stage.group:groups_stage.appuser_id for groups_stage in groups_stage_first_place}
        groups_stage_second_place =  db.query(GroupStage).filter(GroupStage.tournament_cod == cod_tournament, GroupStage.position == 2).all()
        groups_stage_second_place_dict = {groups_stage.group:groups_stage.appuser_id for groups_stage in groups_stage_second_place}
        confrontations_key_stage = db.query(ConfrontationsKeyStage).filter(ConfrontationsKeyStage.tournaments_id == cod_tournament[-1], ConfrontationsKeyStage.football_games_cod.contains("OC")).all()
        
        cont = 0
        for i in range(1,5):
            for _ in range(1,7):
                confrontations_key_stage[cont].appuser_1_id = groups_stage_first_place_dict[GROUPS[i-1]]
                confrontations_key_stage[cont].appuser_2_id = groups_stage_second_place_dict[GROUPS[i]]
                if i == 4:
                    confrontations_key_stage[cont].appuser_1_id = groups_stage_first_place_dict[GROUPS[i]]
                    confrontations_key_stage[cont].appuser_2_id = groups_stage_second_place_dict[GROUPS[i-1]]
                CRUD.update(db, confrontations_key_stage[cont])
                cont = cont + 1
