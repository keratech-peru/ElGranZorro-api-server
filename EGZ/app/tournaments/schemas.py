from pydantic import BaseModel, validator
from typing import Optional
from app.tournaments.constants import STATUS_TOURNAMENT, LEVELS, Origin, Players

class Tourmaments(BaseModel):
    name: str
    codigo: str = "T32000"
    logo: str
    start_date: str
    max_number_of_players: str = Players.MAXIMO
    game_mode: str = Players.GAME_MODE
    tournament_rules: str
    is_active: bool = False
    stage: str = STATUS_TOURNAMENT["EE"]
    level: str = "1"
    quota: Optional[int]
    reward: Optional[int] 

    @validator('quota', always=True)
    def set_quota(cls, v, values):
        level = values.get('level')
        return LEVELS[level]["quota"]

    @validator('reward', always=True)
    def set_reward(cls, v, values):
        level = values.get('level')
        return LEVELS[level]["reward"]

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
    origin: str = Origin.HANDBOOK

class UpdateFootballGames(BaseModel):
    hour: Optional[str]
    home_team: Optional[str]
    away_team: Optional[str]
    home_score: Optional[int]
    away_score: Optional[int]

class UpdateTourmaments(BaseModel):
    name: Optional[str]
    logo: Optional[str]
    is_active: Optional[bool]
    tournament_rules: Optional[str]