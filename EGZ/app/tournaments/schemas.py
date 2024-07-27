from pydantic import BaseModel
from typing import Optional
from app.tournaments.constants import ETAPAS

class Tourmaments(BaseModel):
    name: str
    codigo: str
    logo: str
    start_date: str
    max_number_of_players: str
    game_mode: str
    tournament_rules: str
    is_active: bool = False
    type_tournament: str = "TIPO D"
    stage: str = ETAPAS["EE"]
    quota: int = 20
    reward: int = 200


class GroupStage(BaseModel):
    tournament_cod: str
    appuser_id: Optional[int]
    group: str
    position: int

class ConfrontationsGroupStage(BaseModel):
    group_stage_1_id: int
    group_stage_2_id: int
    football_games_cod: str
    tournaments_id: int
    points_1: Optional[int] = None
    points_2: Optional[int] = None

class ConfrontationsKeyStage(BaseModel):
    appuser_1_id: Optional[int] = None
    appuser_2_id: Optional[int] = None
    football_games_cod: str
    tournaments_id: int
    points_1: Optional[int] = None
    points_2: Optional[int] = None

class FootballGames(BaseModel):
    codigo: str
    tournament_id: int
    tournament_stage: str
    date: str
    hour: Optional[str]
    type_footballgames: str
    home_team: Optional[str]
    away_team: Optional[str]
    home_score: Optional[int]
    away_score: Optional[int]

class UpdateFootballGames(BaseModel):
    hour: Optional[str]
    home_team: Optional[str]
    away_team: Optional[str]
    home_score: Optional[int]
    away_score: Optional[int]

class UpdateTourmaments(BaseModel):
    name: Optional[str]
    logo: Optional[str]
    tournament_rules: Optional[str]