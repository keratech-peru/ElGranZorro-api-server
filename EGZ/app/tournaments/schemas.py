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

class FootballGames(BaseModel):
    codigo: str
    tournament_id: int
    home_team: str
    away_team: str
    home_score: int
    away_score: int
