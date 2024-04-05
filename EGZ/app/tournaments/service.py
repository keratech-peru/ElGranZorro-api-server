from app.database import CRUD
from app.users.service import AppUsers_
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
            # print("footballgame_dict : ",footballgame_dict)
            # print("play_user : ",play_user,"\n")
            # if int(dif.days) == 0:
            #     del footballgame_dict["home_score"]
            #     del footballgame_dict["away_score"]
            #     footballgame_dict["score_local_user"] = play_user["score_local"] if play_user else None
            #     footballgame_dict["score_visit_user"] = play_user["score_local"] if play_user else None
            #     football_of_the_day.append(footballgame_dict)
            # if int(dif.days) > 0:
            #     footballgame_dict["score_local_user"] = play_user["score_local"] if play_user else None
            #     footballgame_dict["score_visit_user"] = play_user["score_local"] if play_user else None
            #     football_past.append(footballgame_dict)
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

    def update_group_stage(footballgame: FootballGames, home_score: int,  away_score: int, db: Session):
        tournament_cod = footballgame.codigo[:-3]
        appuser_id_point_plays = AppUsers_.play_users_points(db, footballgame.id, footballgame.type_footballgames, home_score, away_score)
        Confrontations_.allocation_points_group_stage(db, appuser_id_point_plays,footballgame.codigo)
        Confrontations_.orden_update_group_stage(db, tournament_cod)
        if "GP9" in footballgame.codigo:
            Confrontations_.registration_teams_eighths(db, tournament_cod)
    
    def update_key_stage(footballgame: FootballGames, home_score: int,  away_score: int, db: Session):
        tournament_cod = footballgame.codigo[:-3]
        appuser_id_point_plays = AppUsers_.play_users_points(db, footballgame.id, footballgame.type_footballgames, home_score, away_score)
        if "OC" in footballgame.codigo:
            Confrontations_.allocation_points_key_stage(db, appuser_id_point_plays,footballgame.codigo)
            if "OC3" in footballgame.codigo:
                Confrontations_.registration_teams_quarter(db, tournament_cod)
        elif "CU" in footballgame.codigo:
            print("Aqui se debe hacer el codigo para que se registre los puntos de los partidos de CU")
            Confrontations_.allocation_points_key_stage(db, appuser_id_point_plays,footballgame.codigo)
            if "CU3" in footballgame.codigo:
                Confrontations_.registration_teams_semifinal(db, tournament_cod)
        elif "SF" in footballgame.codigo:
            print("Aqui se debe hacer el codigo para que se registre los puntos de los partidos de SF")
            Confrontations_.allocation_points_key_stage(db, appuser_id_point_plays,footballgame.codigo)
            if "SF3" in footballgame.codigo: 
                Confrontations_.registration_teams_final(db, tournament_cod)
        else:
            print("decidir que hacer con el ganador ...")
            Confrontations_.allocation_points_key_stage(db, appuser_id_point_plays,footballgame.codigo)
            

    
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

    def allocation_points_key_stage(db: Session, appuser_id_point_plays, footballgame_cod: str):
        appuser_id_plays = list(appuser_id_point_plays.keys())
        confrontations_key_stage = db.query(ConfrontationsKeyStage).filter(
            or_(ConfrontationsKeyStage.appuser_1_id.in_(appuser_id_plays) , ConfrontationsKeyStage.appuser_2_id.in_(appuser_id_plays)),
            ConfrontationsKeyStage.football_games_cod == footballgame_cod
            ).order_by(ConfrontationsKeyStage.id).all()
        for confront in confrontations_key_stage:
            if confront.appuser_1_id in appuser_id_plays:
                confront.points_1 = appuser_id_point_plays[confront.appuser_1_id]
                CRUD.update(db, confront)
            if confront.appuser_2_id in appuser_id_plays:
                confront.points_2 = appuser_id_point_plays[confront.appuser_2_id]
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
                        point = point + (confront.points_1 if confront.points_1 else 0) 
                    if confront.group_stage_2_id == group.id:
                        point = point + (confront.points_2 if confront.points_2 else 0)
                group_stage_point[group.id] = point
            group_stage_id_and_points_orden = sorted(group_stage_point.items(), key=lambda x: x[1], reverse=True)
            for i in range(1,len(group_stage_id_and_points_orden)+1):
                groups_stage =  db.query(GroupStage).filter(GroupStage.id == group_stage_id_and_points_orden[i-1][0]).first()
                groups_stage.position = i
                CRUD.update(db, groups_stage)
    
    def registration_teams_eighths(db, cod_tournament: str):
        tournaments_id = str(int(cod_tournament[-3:]))
        first_place = {groups_stage.group:groups_stage.appuser_id for groups_stage in db.query(GroupStage).filter(GroupStage.tournament_cod == cod_tournament, GroupStage.position == 1).order_by(GroupStage.id).all()}
        second_place = {groups_stage.group:groups_stage.appuser_id for groups_stage in db.query(GroupStage).filter(GroupStage.tournament_cod == cod_tournament, GroupStage.position == 2).order_by(GroupStage.id).all()}
        key_stage_oc = db.query(ConfrontationsKeyStage).filter(ConfrontationsKeyStage.tournaments_id == tournaments_id, ConfrontationsKeyStage.football_games_cod.contains("OC")).order_by(ConfrontationsKeyStage.id).all()
        cont = 0
        for i in range(1,9,2):
            for j in range(1,7):
                if j >= 4:
                    key_stage_oc[cont].appuser_1_id = first_place[GROUPS[i]]
                    key_stage_oc[cont].appuser_2_id = second_place[GROUPS[i-1]]
                else:
                    key_stage_oc[cont].appuser_1_id = first_place[GROUPS[i-1]]
                    key_stage_oc[cont].appuser_2_id = second_place[GROUPS[i]]
                CRUD.update(db, key_stage_oc[cont])
                cont = cont + 1

    def registration_teams_quarter(db, cod_tournament: str):
        tournaments_id = str(int(cod_tournament[-3:]))
        eighths = db.query(ConfrontationsKeyStage).filter(ConfrontationsKeyStage.tournaments_id == tournaments_id, ConfrontationsKeyStage.football_games_cod.contains("OC")).order_by(ConfrontationsKeyStage.id).all()
        quarter = db.query(ConfrontationsKeyStage).filter(ConfrontationsKeyStage.tournaments_id == tournaments_id, ConfrontationsKeyStage.football_games_cod.contains("CU")).order_by(ConfrontationsKeyStage.id).all()
        for i in range(4):
            key_stage_oc_group = eighths[6*i:6*(i+1)]
            points_grupo_a = {key_stage_oc.id:[key_stage_oc.points_1 if key_stage_oc.points_1 is not None else 0,key_stage_oc.points_2 if key_stage_oc.points_2 is not None else 0] for key_stage_oc in key_stage_oc_group[:3]}
            points_grupo_b = {key_stage_oc.id:[key_stage_oc.points_1 if key_stage_oc.points_1 is not None else 0,key_stage_oc.points_2 if key_stage_oc.points_2 is not None else 0] for key_stage_oc in key_stage_oc_group[3:]}
            points_local_a = 0
            poitns_visit_a = 0
            for points_grupo in list(points_grupo_a.values()):
                points_local_a = points_local_a + points_grupo[0]
                poitns_visit_a = poitns_visit_a + points_grupo[1]
            points_local_b = 0
            poitns_visit_b = 0
            for points_grupo in list(points_grupo_b.values()):
                points_local_b = points_local_b + points_grupo[0]
                poitns_visit_b = poitns_visit_b + points_grupo[1]
            if points_local_a >= poitns_visit_a:
                appuser_1_id = key_stage_oc_group[0].appuser_1_id
            else:
                appuser_1_id = key_stage_oc_group[0].appuser_2_id
            if points_local_b >= poitns_visit_b:
                appuser_2_id = key_stage_oc_group[5].appuser_1_id
            else:
                appuser_2_id = key_stage_oc_group[5].appuser_2_id
            
            key_stage_cu_group = quarter[3*i:3*(i+1)]
            for cu in key_stage_cu_group:
                cu.appuser_1_id = appuser_1_id
                cu.appuser_2_id = appuser_2_id
                CRUD.update(db, cu)

    def registration_teams_semifinal(db, cod_tournament: str):
        tournaments_id = str(int(cod_tournament[-3:]))
        quarter = db.query(ConfrontationsKeyStage).filter(ConfrontationsKeyStage.tournaments_id == tournaments_id, ConfrontationsKeyStage.football_games_cod.contains("CU")).order_by(ConfrontationsKeyStage.id).all()
        semifinal = db.query(ConfrontationsKeyStage).filter(ConfrontationsKeyStage.tournaments_id == tournaments_id, ConfrontationsKeyStage.football_games_cod.contains("SF")).order_by(ConfrontationsKeyStage.id).all()
        for i in range(2):
            key_stage_oc_group = quarter[6*i:6*(i+1)]
            points_grupo_a = {key_stage_oc.id:[key_stage_oc.points_1 if key_stage_oc.points_1 is not None else 0,key_stage_oc.points_2 if key_stage_oc.points_2 is not None else 0] for key_stage_oc in key_stage_oc_group[:3]}
            points_grupo_b = {key_stage_oc.id:[key_stage_oc.points_1 if key_stage_oc.points_1 is not None else 0,key_stage_oc.points_2 if key_stage_oc.points_2 is not None else 0] for key_stage_oc in key_stage_oc_group[3:]}
            points_local_a = 0
            poitns_visit_a = 0
            for points_grupo in list(points_grupo_a.values()):
                points_local_a = points_local_a + points_grupo[0]
                poitns_visit_a = poitns_visit_a + points_grupo[1]
            points_local_b = 0
            poitns_visit_b = 0
            for points_grupo in list(points_grupo_b.values()):
                points_local_b = points_local_b + points_grupo[0]
                poitns_visit_b = poitns_visit_b + points_grupo[1]
            if points_local_a >= poitns_visit_a:
                appuser_1_id = key_stage_oc_group[0].appuser_1_id
            else:
                appuser_1_id = key_stage_oc_group[0].appuser_2_id
            if points_local_b >= poitns_visit_b:
                appuser_2_id = key_stage_oc_group[5].appuser_1_id
            else:
                appuser_2_id = key_stage_oc_group[5].appuser_2_id
            
            key_stage_sf_group = semifinal[3*i:3*(i+1)]
            for sf in key_stage_sf_group:
                sf.appuser_1_id = appuser_1_id
                sf.appuser_2_id = appuser_2_id
                CRUD.update(db, sf)

    def registration_teams_final(db, cod_tournament: str):
        tournaments_id = str(int(cod_tournament[-3:]))
        semifinal = db.query(ConfrontationsKeyStage).filter(ConfrontationsKeyStage.tournaments_id == tournaments_id, ConfrontationsKeyStage.football_games_cod.contains("SF")).order_by(ConfrontationsKeyStage.id).all()
        final = db.query(ConfrontationsKeyStage).filter(ConfrontationsKeyStage.tournaments_id == tournaments_id, ConfrontationsKeyStage.football_games_cod.contains("FI")).order_by(ConfrontationsKeyStage.id).all()
        key_stage_sf_group = semifinal[0:6]
        points_local_1 = [key_stage_oc.points_1 if key_stage_oc.points_1 != None else 0 for key_stage_oc in key_stage_sf_group[:3]]
        points_visit_1 = [key_stage_oc.points_1 if key_stage_oc.points_1 != None else 0 for key_stage_oc in key_stage_sf_group[:3]]
        points_local_2 = [key_stage_oc.points_1 if key_stage_oc.points_1 != None else 0 for key_stage_oc in key_stage_sf_group[3:]]
        points_visit_2 = [key_stage_oc.points_1 if key_stage_oc.points_1 != None else 0 for key_stage_oc in key_stage_sf_group[3:]]
        if sum(points_local_1) >= sum(points_visit_1):
            appuser_1_id = key_stage_sf_group[0].appuser_1_id
        else:
            appuser_1_id = key_stage_sf_group[5].appuser_1_id
        if sum(points_local_2) >= sum(points_visit_2):
            appuser_2_id = key_stage_sf_group[0].appuser_2_id
        else:
            appuser_2_id = key_stage_sf_group[5].appuser_2_id

        for fi in final:
            fi.appuser_1_id = appuser_1_id
            fi.appuser_2_id = appuser_2_id
            CRUD.update(db, fi)
