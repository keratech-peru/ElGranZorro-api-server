from pydantic import BaseModel
from typing import Optional

class Tourmaments(BaseModel):
    name: str
    codigo: str
    logo: str
    start_date: str
    max_number_of_players: str
    game_mode: str
    tournament_rules: str

class GroupStage(BaseModel):
    tournament_cod: str
    appuser_id: Optional[int]
    group: str


class FootballGames(BaseModel):
    codigo: str
    tournament_id: int
    tournament_stage: str
    date: str
    type_footballgames: str
    home_team: Optional[str]
    away_team: Optional[str]
    home_score: Optional[int]
    away_score: Optional[int]

class UpdateFootballGames(BaseModel):
    home_team: Optional[str]
    away_team: Optional[str]
    home_score: Optional[int]
    away_score: Optional[int]