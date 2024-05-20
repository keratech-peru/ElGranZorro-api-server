from app.database import CRUD
from app.users.service import AppUsers_
from app.users.models import PlaysUsers, EnrollmentUsers, AppUsers
from app.tournaments.models import Tournaments, FootballGames, GroupStage, ConfrontationsGroupStage, ConfrontationsKeyStage
from app.tournaments import schemas
from app.tournaments.constants import GROUPS
from app.tournaments.utils import is_past, hide_data_because_is_past_is_appuser
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
    
    def update(tourmament_id:int , update_tournament_in: schemas.UpdateTourmaments, db: Session):
        tourmament = db.query(Tournaments).filter(Tournaments.id == tourmament_id).first()
        if tourmament:
            tourmament.name = update_tournament_in.name
            tourmament.logo = update_tournament_in.logo
            tourmament.tournament_rules = update_tournament_in.tournament_rules
            CRUD.update(db, tourmament)

    def list_all(db: Session) -> List[Tournaments]:
        return db.query(Tournaments).all()

    def list_all_is_enrollend_user(db: Session, appuser_id: int) -> List[Tournaments]:
        tournaments_ = []
        tournaments = db.query(Tournaments).order_by(Tournaments.id).all()
        for tournament in tournaments:
            tournament_ = tournament.__dict__
            tournament_["is_enrolled_user"] = True if  db.query(EnrollmentUsers).filter(
                EnrollmentUsers.tournaments_id == tournament.id,
                EnrollmentUsers.appuser_id == appuser_id
                ).first() else False
            tournaments_.append(tournament_)
        return tournaments_

    def list_search_codigo(db: Session, codigo: str) -> List[Tournaments]:
        tournaments_ = []
        tournaments = db.query(Tournaments).all()
        for tournament in tournaments:
            tournament_ = tournament.__dict__
            tournament_["is_last"] = is_past(tournament.start_date)
            tournament_["number_enrollment"] = db.query(EnrollmentUsers).filter(EnrollmentUsers.tournaments_id == tournament.id).count()
            if codigo in tournament_["codigo"]:
                tournaments_.append(tournament_)
        return tournaments_
    
    def get_data_group_table(db: Session, tournament_id: int , user_id: int):
        tournament_cod = db.query(Tournaments.codigo).filter(Tournaments.id == tournament_id).first()
        group_user = db.query(GroupStage.group).filter(GroupStage.tournament_cod == tournament_cod[0], GroupStage.appuser_id == user_id).first()
        group_stage_table = []
        groups_stage = db.query(GroupStage).filter(GroupStage.group == group_user[0], GroupStage.tournament_cod == tournament_cod[0]).order_by(GroupStage.position).all()
        group_stage_point = Confrontations_.get_group_stage_point(db, tournament_cod[0],  group_user[0])
        group_stage_ids_list = [group.id for group in groups_stage]
        for group_stage in groups_stage:
            group_stage_ = group_stage.__dict__
            group_stage_["team"] = db.query(AppUsers.team_name, AppUsers.team_logo).filter(AppUsers.id == group_stage_['appuser_id']).first()
            group_stage_["points"] = group_stage_point[group_stage.id]
            group_stage_table.append(group_stage_)
        return group_stage_table, group_stage_ids_list

    def get_data_group_stage_plays(db: Session, footballgame: FootballGames, group_stage_ids_list, footballgame_dict, user_id: int):
        confrontations_group_stage = db.query(ConfrontationsGroupStage).filter(
            ConfrontationsGroupStage.football_games_cod == footballgame.codigo,
            or_(ConfrontationsGroupStage.group_stage_1_id.in_(group_stage_ids_list) , ConfrontationsGroupStage.group_stage_2_id.in_(group_stage_ids_list))).all()
        plays_ = []
        for confrontation in confrontations_group_stage:
            appuser_id_local  = db.query(GroupStage.appuser_id).filter(GroupStage.id == confrontation.group_stage_1_id).first()[0]
            appuser_id_visit  = db.query(GroupStage.appuser_id).filter(GroupStage.id == confrontation.group_stage_2_id).first()[0]
            plays_local = db.query(PlaysUsers.score_local, PlaysUsers.score_visit).filter(PlaysUsers.appuser_id == appuser_id_local, PlaysUsers.football_games_id == footballgame.id).first()
            plays_visit = db.query(PlaysUsers.score_local, PlaysUsers.score_visit).filter(PlaysUsers.appuser_id == appuser_id_visit, PlaysUsers.football_games_id == footballgame.id).first()
            appuser_local  = db.query(AppUsers).filter(AppUsers.id == appuser_id_local).first()
            appuser_visit  = db.query(AppUsers).filter(AppUsers.id == appuser_id_visit).first()  
            plays_.append({ "id_local":appuser_id_local,
                            "team_local_name":None if appuser_local is None else appuser_local.team_name,
                            "team_local_logo":None if appuser_local is None else appuser_local.team_logo,
                            "plays_local": hide_data_because_is_past_is_appuser(footballgame_dict["is_past"], user_id == appuser_id_local, plays_local),
                            "points_local":hide_data_because_is_past_is_appuser(footballgame_dict["is_past"], user_id == appuser_id_local, confrontation.points_1),
                            "id_visit":appuser_id_visit,
                            "team_visit_name":None if appuser_visit is None else appuser_visit.team_name,
                            "team_visit_logo":None if appuser_visit is None else appuser_visit.team_logo,
                            "plays_visit":hide_data_because_is_past_is_appuser(footballgame_dict["is_past"], user_id == appuser_id_visit, plays_visit),
                            "points_visit":hide_data_because_is_past_is_appuser(footballgame_dict["is_past"], user_id == appuser_id_visit, confrontation.points_2),
                            "is_user_play": user_id in [appuser_id_local, appuser_id_visit],
                            "is_appuser_local": user_id == appuser_id_local
                        })
        footballgame_dict["plays"] = plays_
        return footballgame_dict

    def get_data_group_key_plays(db: Session, footballgame: FootballGames, footballgame_dict, user_id: int):
        confrontations_key_stage = db.query(ConfrontationsKeyStage).filter(ConfrontationsKeyStage.football_games_cod == footballgame.codigo).order_by(ConfrontationsKeyStage.id).all()
        plays_ = []
        cont = 0
        for confrontation in confrontations_key_stage:
            plays_local = db.query(PlaysUsers.score_local, PlaysUsers.score_visit).filter(PlaysUsers.appuser_id == confrontation.appuser_1_id, PlaysUsers.football_games_id == footballgame.id).first()
            plays_visit = db.query(PlaysUsers.score_local, PlaysUsers.score_visit).filter(PlaysUsers.appuser_id == confrontation.appuser_2_id, PlaysUsers.football_games_id == footballgame.id).first()
            appuser_local  = db.query(AppUsers).filter(AppUsers.id == confrontation.appuser_1_id).first()
            appuser_visit  = db.query(AppUsers).filter(AppUsers.id == confrontation.appuser_2_id).first()
            cont = cont + 1
            plays_.append({ "id_local":confrontation.appuser_1_id,
                            "team_local_name":appuser_local.team_name if appuser_local else None,
                            "team_local_logo":appuser_local.team_logo if appuser_local else None,
                            "plays_local":hide_data_because_is_past_is_appuser(footballgame_dict["is_past"], user_id == confrontation.appuser_1_id, plays_local),
                            "points_local":hide_data_because_is_past_is_appuser(footballgame_dict["is_past"], user_id == confrontation.appuser_1_id, confrontation.points_1),
                            "id_visit":confrontation.appuser_2_id,
                            "team_visit_name":appuser_visit.team_name if appuser_visit else None,
                            "team_visit_logo":appuser_visit.team_logo if appuser_visit else None,
                            "plays_visit":hide_data_because_is_past_is_appuser(footballgame_dict["is_past"], user_id == confrontation.appuser_2_id, plays_visit),
                            "points_visit":hide_data_because_is_past_is_appuser(footballgame_dict["is_past"], user_id == confrontation.appuser_2_id, confrontation.points_2),
                            "is_user_play": user_id in [confrontation.appuser_1_id, confrontation.appuser_2_id],
                            "is_appuser_local": user_id == confrontation.appuser_1_id,
                            "key_side": "A" if len(confrontations_key_stage)/2 >= cont else "B"
                            })
        footballgame_dict["plays"] = plays_
        return footballgame_dict

    def get_footballgames(db: Session, tournament: Tournaments, user_id: int):
        football_stage_group = {'Fecha 1': [], 'Fecha 2': [], 'Fecha 3': []}
        football_stage_keys = {'OCTAVOS':[], 'CUARTOS':[], 'SEMI-FINAL':[], 'FINAL':[]}
        footballgames = db.query(FootballGames).filter(FootballGames.tournament_id == tournament.id).order_by(FootballGames.id).all()
        group_stage_table, group_stage_ids_list = Tournaments_.get_data_group_table(db, tournament.id, user_id)
        tournament_stage = []
        for footballgame in footballgames:
            footballgame_dict = footballgame.__dict__
            footballgame_dict["is_past"] = is_past(footballgame.date, footballgame.hour)
            if footballgame_dict["is_past"]:
                tournament_stage.append(footballgame.tournament_stage)
            if "GRUPOS" in footballgame.tournament_stage:
                footballgame_dict = Tournaments_.get_data_group_stage_plays(db, footballgame, group_stage_ids_list, footballgame_dict, user_id)
                football_stage_group[footballgame.tournament_stage[:7]].append(footballgame_dict)
            else:
                footballgame_dict = Tournaments_.get_data_group_key_plays(db, footballgame, footballgame_dict, user_id)
                football_stage_keys[footballgame.tournament_stage].append(footballgame_dict)
        tournament_ = tournament.__dict__
        tournament_["tournament_stage"] = tournament_stage[-1] if len(tournament_stage) > 0 else "AUN NO EMPIEZA"
        return tournament_, group_stage_table, football_stage_group, football_stage_keys

    def start(db: Session, tournament_cod: str):
        enrollment_users = db.query(EnrollmentUsers).filter(EnrollmentUsers.tournaments_id == int(tournament_cod[-3:])).all()
        for enrollment_user in enrollment_users:
            enrollment_user.state = "EN PROCESO"
            CRUD.update(db, enrollment_user)

class FootballGames_(CRUD):
    @staticmethod
    def create(football_game_in: schemas.FootballGames, db: Session) -> FootballGames:
        new_football_game = FootballGames(**football_game_in.dict())
        CRUD.insert(db, new_football_game)
        return new_football_game

    def update(footballgame_id:int , update_footballgame_in: schemas.UpdateFootballGames, db: Session) :
        footballgame = db.query(FootballGames).filter(FootballGames.id == footballgame_id).first()
        if footballgame:
            footballgame.hour = update_footballgame_in.hour
            footballgame.home_team = update_footballgame_in.home_team
            footballgame.away_team = update_footballgame_in.away_team
            footballgame.home_score = update_footballgame_in.home_score
            footballgame.away_score = update_footballgame_in.away_score
            CRUD.update(db, footballgame)       

    def list_search_codigo(db: Session, codigo: str) -> List[FootballGames]:
        footballgames_ = []
        footballgames = db.query(FootballGames).order_by(FootballGames.id.desc()).all()
        for footballgame in footballgames:
            footballgame_ = footballgame.__dict__
            footballgame_["tournament_codigo"] = db.query(Tournaments.codigo).filter(Tournaments.id == footballgame.tournament_id).first()[0]
            footballgame_["is_last"] = is_past(footballgame.date,footballgame.hour)
            footballgame_["home_team"] = str(footballgame.home_team)
            footballgame_["away_team"] = str(footballgame.away_team)
            footballgame_["home_score"] = str(footballgame.home_score)
            footballgame_["away_score"] = str(footballgame.away_score)
            if codigo in footballgame_["codigo"]:
                footballgames_.append(footballgame_)
        return footballgames_

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
                    hour=None,
                    type_footballgames= "RESULT" if cont%2 == 0 else "SCORE",
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
                hour=None,
                type_footballgames= "RESULT" if cont%2 == 0 else "SCORE",
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
                hour=None,
                type_footballgames= "RESULT" if cont%2 == 0 else "SCORE",
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
                hour=None,
                type_footballgames= "RESULT" if cont%2 == 0 else "SCORE",
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
                hour=None,
                type_footballgames= "RESULT" if cont%2 == 0 else "SCORE",
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
        if "GP1" in footballgame.codigo:
            Tournaments_.start(db, tournament_cod)
        if "GP9" in footballgame.codigo:
            Confrontations_.registration_teams_eighths(db, tournament_cod)
            AppUsers_.eliminated_group_stage(db, tournament_cod)
    
    def update_key_stage(footballgame: FootballGames, home_score: int,  away_score: int, db: Session):
        tournament_cod = footballgame.codigo[:-3]
        tournament_id = int(tournament_cod[-3:])
        appuser_id_point_plays = AppUsers_.play_users_points(db, footballgame.id, footballgame.type_footballgames, home_score, away_score)
        if "OC" in footballgame.codigo:
            Confrontations_.allocation_points_key_stage(db, appuser_id_point_plays,footballgame.codigo)
            if "OC3" in footballgame.codigo:
                list_appuser_id = Confrontations_.registration_teams_quarter(db, tournament_cod)
                AppUsers_.eliminated_key_stage(db, "OC", list_appuser_id, tournament_id)
        elif "CU" in footballgame.codigo:
            Confrontations_.allocation_points_key_stage(db, appuser_id_point_plays,footballgame.codigo)
            if "CU3" in footballgame.codigo:
                list_appuser_id = Confrontations_.registration_teams_semifinal(db, tournament_cod)
                AppUsers_.eliminated_key_stage(db, "CU", list_appuser_id, tournament_id)
        elif "SF" in footballgame.codigo:
            Confrontations_.allocation_points_key_stage(db, appuser_id_point_plays,footballgame.codigo)
            if "SF3" in footballgame.codigo: 
                list_appuser_id = Confrontations_.registration_teams_final(db, tournament_cod)
                AppUsers_.eliminated_key_stage(db, "SF", list_appuser_id, tournament_id)
        else:
            Confrontations_.allocation_points_key_stage(db, appuser_id_point_plays,footballgame.codigo)
            if "FI5" in footballgame.codigo:
                list_appuser_id = Confrontations_.first_place(db, tournament_cod)
                AppUsers_.eliminated_key_stage(db, "FI", list_appuser_id, tournament_id)
            

    
class Confrontations_(CRUD):
    @staticmethod
    def create_groups_stage(tournament_id: int ,db: Session, tournament_cod: str):
        list_confrontations = []
        for group in GROUPS:
            group_stage = db.query(GroupStage).filter(GroupStage.group == group, GroupStage.tournament_cod == tournament_cod).all()
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

    def ids_point_play_and_not_play_group_stage(db: Session, footballgame_cod: str, appuser_id_point_plays):
        group_stage_ids =  db.query(GroupStage.id,GroupStage.appuser_id).filter(GroupStage.tournament_cod == footballgame_cod[:-3], GroupStage.appuser_id.in_(list(appuser_id_point_plays.keys()))).all()
        group_stage_ids_all =  db.query(GroupStage.id).filter(GroupStage.tournament_cod == footballgame_cod[:-3]).all()   
        ids_list = [ group_stage_id[0] for group_stage_id in  group_stage_ids ]
        ids_list_all = [ group_stage_id[0] for group_stage_id in  group_stage_ids_all ]
        ids_point_play = { group_stage_id[0]:appuser_id_point_plays[group_stage_id[1]] for group_stage_id in  group_stage_ids }
        ids_point_not_play = { ids:0 for ids in ids_list_all if ids not in ids_list }
        return ids_point_play , ids_point_not_play

    def allocation_points_group_stage(db: Session, appuser_id_point_plays, footballgame_cod: str):
        ids_point_play , ids_point_not_play = Confrontations_.ids_point_play_and_not_play_group_stage(db,footballgame_cod, appuser_id_point_plays)
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

    def winner_points_equal(db:Session, key_stage: List[ConfrontationsKeyStage], group: str):
        key_stage_part = key_stage[:3] if group == 'A' else key_stage[3:]
        footballgames_cod_list = [key.football_games_cod for key in key_stage_part]
        footballgames_id_list = [db.query(FootballGames.id).filter(FootballGames.codigo == footballgames_cod).first()[0] for footballgames_cod in footballgames_cod_list]
        play_users_update_at_1 = db.query(PlaysUsers.updated_at).filter(PlaysUsers.appuser_id == key_stage_part[0].appuser_1_id,PlaysUsers.id.in_(footballgames_id_list)).order_by(PlaysUsers.id).all()
        play_users_update_at_2 = db.query(PlaysUsers.updated_at).filter(PlaysUsers.appuser_id == key_stage_part[0].appuser_2_id,PlaysUsers.id.in_(footballgames_id_list)).order_by(PlaysUsers.id).all()
        cont = 0
        for i in range(3):
            if (play_users_update_at_1[i][0] > play_users_update_at_2[i][0]):
                cont = cont + 1
        if cont > 2:
            appuser_id = key_stage_part[0].appuser_1_id
        else:
            appuser_id = key_stage_part[0].appuser_2_id

        return appuser_id

    def winner_confrontation_key_stage(db: Session, key_stage: List[ConfrontationsKeyStage], points_grupo_a, points_grupo_b):
        # Se hace conteo de puntos
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
        
        # Se define cual de los dos son los ganadores
        if points_local_a > poitns_visit_a:
            appuser_1_id = key_stage[0].appuser_1_id
        elif points_local_a == poitns_visit_a:
            appuser_1_id = Confrontations_.winner_points_equal(db, key_stage, group="A")
        else:
            appuser_1_id = key_stage[0].appuser_2_id

        if points_local_b > poitns_visit_b:
            appuser_2_id = key_stage[-1].appuser_1_id
        elif points_local_b == poitns_visit_b:
            appuser_2_id = Confrontations_.winner_points_equal(db, key_stage, group="B")
        else:
            appuser_2_id = key_stage[-1].appuser_2_id
        
        return appuser_1_id, appuser_2_id

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

    def get_group_stage_point(db: Session, cod_tournament: str, group: str):
        groups_stage =  db.query(GroupStage).filter(GroupStage.tournament_cod == cod_tournament, GroupStage.group == group).all()
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
        return group_stage_point
    
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
        list_appuser_id = []
        for i in range(4):
            key_stage_oc_group = eighths[6*i:6*(i+1)]
            points_grupo_a = {key_stage_oc.id:[key_stage_oc.points_1 if key_stage_oc.points_1 is not None else 0,key_stage_oc.points_2 if key_stage_oc.points_2 is not None else 0] for key_stage_oc in key_stage_oc_group[:3]}
            points_grupo_b = {key_stage_oc.id:[key_stage_oc.points_1 if key_stage_oc.points_1 is not None else 0,key_stage_oc.points_2 if key_stage_oc.points_2 is not None else 0] for key_stage_oc in key_stage_oc_group[3:]}
            appuser_1_id, appuser_2_id = Confrontations_.winner_confrontation_key_stage(db, key_stage_oc_group, points_grupo_a, points_grupo_b)
            key_stage_cu_group = quarter[3*i:3*(i+1)]
            if appuser_1_id:
                list_appuser_id.append(appuser_1_id)
            if appuser_2_id:
                list_appuser_id.append(appuser_2_id)
            for cu in key_stage_cu_group:
                cu.appuser_1_id = appuser_1_id
                cu.appuser_2_id = appuser_2_id
                CRUD.update(db, cu)
        return list_appuser_id

    def registration_teams_semifinal(db, cod_tournament: str):
        tournaments_id = str(int(cod_tournament[-3:]))
        quarter = db.query(ConfrontationsKeyStage).filter(ConfrontationsKeyStage.tournaments_id == tournaments_id, ConfrontationsKeyStage.football_games_cod.contains("CU")).order_by(ConfrontationsKeyStage.id).all()
        semifinal = db.query(ConfrontationsKeyStage).filter(ConfrontationsKeyStage.tournaments_id == tournaments_id, ConfrontationsKeyStage.football_games_cod.contains("SF")).order_by(ConfrontationsKeyStage.id).all()
        list_appuser_id = []
        for i in range(2):
            key_stage_cu_group = quarter[6*i:6*(i+1)]
            points_grupo_a = {key_stage_cu.id:[key_stage_cu.points_1 if key_stage_cu.points_1 is not None else 0,key_stage_cu.points_2 if key_stage_cu.points_2 is not None else 0] for key_stage_cu in key_stage_cu_group[:3]}
            points_grupo_b = {key_stage_cu.id:[key_stage_cu.points_1 if key_stage_cu.points_1 is not None else 0,key_stage_cu.points_2 if key_stage_cu.points_2 is not None else 0] for key_stage_cu in key_stage_cu_group[3:]}
            appuser_1_id, appuser_2_id = Confrontations_.winner_confrontation_key_stage(db, key_stage_cu_group, points_grupo_a, points_grupo_b)
            key_stage_sf_group = semifinal[3*i:3*(i+1)]
            if appuser_1_id:
                list_appuser_id.append(appuser_1_id)
            if appuser_2_id:
                list_appuser_id.append(appuser_2_id)
            for sf in key_stage_sf_group:
                sf.appuser_1_id = appuser_1_id
                sf.appuser_2_id = appuser_2_id
                CRUD.update(db, sf)
        return list_appuser_id

    def registration_teams_final(db, cod_tournament: str):
        tournaments_id = str(int(cod_tournament[-3:]))
        semifinal = db.query(ConfrontationsKeyStage).filter(ConfrontationsKeyStage.tournaments_id == tournaments_id, ConfrontationsKeyStage.football_games_cod.contains("SF")).order_by(ConfrontationsKeyStage.id).all()
        final = db.query(ConfrontationsKeyStage).filter(ConfrontationsKeyStage.tournaments_id == tournaments_id, ConfrontationsKeyStage.football_games_cod.contains("FI")).order_by(ConfrontationsKeyStage.id).all()
        list_appuser_id = []
        key_stage_sf_group = semifinal[0:6]
        points_grupo_a = {key_stage_sf.id:[key_stage_sf.points_1 if key_stage_sf.points_1 is not None else 0,key_stage_sf.points_2 if key_stage_sf.points_2 is not None else 0] for key_stage_sf in key_stage_sf_group[:3]}
        points_grupo_b = {key_stage_sf.id:[key_stage_sf.points_1 if key_stage_sf.points_1 is not None else 0,key_stage_sf.points_2 if key_stage_sf.points_2 is not None else 0] for key_stage_sf in key_stage_sf_group[3:]}
        appuser_1_id, appuser_2_id = Confrontations_.winner_confrontation_key_stage(db, key_stage_sf_group, points_grupo_a, points_grupo_b)
        if appuser_1_id:
            list_appuser_id.append(appuser_1_id)
        if appuser_2_id:
            list_appuser_id.append(appuser_2_id) 
        for fi in final:
            fi.appuser_1_id = appuser_1_id
            fi.appuser_2_id = appuser_2_id
            CRUD.update(db, fi)
        return list_appuser_id

    def first_place(db, cod_tournament: str):
        tournaments_id = int(cod_tournament[-3:])
        confrontations_final = db.query(ConfrontationsKeyStage).filter(ConfrontationsKeyStage.tournaments_id == str(tournaments_id), ConfrontationsKeyStage.football_games_cod.contains("FI")).order_by(ConfrontationsKeyStage.id).all()
        fooballgames_final = db.query(FootballGames).filter(FootballGames.tournament_id == tournaments_id, FootballGames.tournament_stage=='FINAL').order_by(FootballGames.id).all()
        
        # Calculo de puntos de todos los enfrentamientos.
        points_local = 0
        poitns_visit = 0
        for confrontation in confrontations_final:
            points_local = points_local + (confrontation.points_1 if confrontation.points_1 is not None else 0)
            poitns_visit = poitns_visit + (confrontation.points_2 if confrontation.points_2 is not None else 0)
        
        # Asignacion de appuser_id para el ganador
        if points_local > poitns_visit:
            appuser_id = confrontations_final[0].appuser_1_id
        elif points_local < poitns_visit:
            appuser_id = confrontations_final[0].appuser_2_id
        else:
            footballgames_id_list = [footballgames.id for footballgames in fooballgames_final]
            play_users_update_at_1 = db.query(PlaysUsers.updated_at).filter(PlaysUsers.appuser_id == confrontations_final[0].appuser_1_id, PlaysUsers.id.in_(footballgames_id_list)).order_by(PlaysUsers.id).all()
            play_users_update_at_2 = db.query(PlaysUsers.updated_at).filter(PlaysUsers.appuser_id == confrontations_final[0].appuser_2_id, PlaysUsers.id.in_(footballgames_id_list)).order_by(PlaysUsers.id).all()
            cont_1 = 0
            cont_2 = 0
            for i in range(len(footballgames_id_list)):
                if (play_users_update_at_1[i] == None) and (play_users_update_at_2[i] != None):
                    cont_2 = cont_2 + 1
                elif (play_users_update_at_1[i] != None) and (play_users_update_at_2[i] == None):
                    cont_1 = cont_1 + 1
                elif play_users_update_at_1[i][0] > play_users_update_at_2[i][0]:
                    cont_1 = cont_1 + 1
                elif play_users_update_at_1[i][0] < play_users_update_at_2[i][0]:
                    cont_2 = cont_2 + 1
                
            if cont_1 > cont_2:
                appuser_id = confrontations_final[0].appuser_1_id
            elif cont_1 < cont_2:
                appuser_id = confrontations_final[0].appuser_2_id
            else:
                print("Nos fuimos a la mrd ...")

        enrollment = db.query(EnrollmentUsers).filter(EnrollmentUsers.tournaments_id == tournaments_id,EnrollmentUsers.appuser_id == appuser_id).first()
        enrollment.state = "GANADOR"
        CRUD.update(db, enrollment)
        return [appuser_id]
