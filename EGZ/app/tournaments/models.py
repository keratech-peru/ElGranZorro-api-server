from app.database import Base
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float
from sqlalchemy.schema import ForeignKey
from sqlalchemy.orm import relationship

class Tournaments(Base):
    __tablename__= "tournaments_tournaments"
    id=Column(Integer, primary_key=True, autoincrement=True )
    created_at = Column(DateTime, default=datetime.utcnow(), onupdate=datetime.now())
    updated_at = Column(DateTime, default=datetime.utcnow(), onupdate=datetime.now())
    name = Column(String)
    codigo = Column(String, unique=True)
    logo = Column(String)
    start_date = Column(String)
    max_number_of_players = Column(String)
    game_mode = Column(String)
    tournament_rules = Column(String)

    football_game = relationship("FootballGames", back_populates="tournament")

class GroupStage(Base):
    __tablename__= "tournaments_group_stage"
    id=Column(Integer, primary_key=True, autoincrement=True )
    tournament_cod = Column(String)
    appuser_id = Column(Integer)
    group = Column(String)
    position = Column(Integer)

class ConfrontationsGroupStage(Base):
    __tablename__= "tournaments_confrontations_group_stage"
    id=Column(Integer, primary_key=True, autoincrement=True )
    group_stage_1_id = Column(Integer)
    group_stage_2_id = Column(Integer)
    football_games_cod = Column(String)
    tournaments_id = Column(String)
    points_1 = Column(Integer)
    points_2 = Column(Integer)

class ConfrontationsKeyStage(Base):
    __tablename__= "tournaments_confrontations_key_stage"
    id=Column(Integer, primary_key=True, autoincrement=True )
    appuser_1_id = Column(Integer)
    appuser_2_id = Column(Integer)
    football_games_cod = Column(String)
    tournaments_id = Column(String)
    points_1 = Column(Integer)
    points_2 = Column(Integer)

class FootballGames(Base):
    __tablename__= "tournaments_football_games"
    id=Column(Integer, primary_key=True, autoincrement=True )
    codigo = Column(String, unique=True)
    tournament_id = Column(Integer, ForeignKey("tournaments_tournaments.id"))
    tournament_stage = Column(String)
    date = Column(String)
    hour = Column(String)
    type_footballgames = Column(String)
    home_team = Column(String)
    away_team = Column(String)
    home_score = Column(String)
    away_score = Column(String)

    tournament = relationship("Tournaments", back_populates="football_game")
