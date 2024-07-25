from app.database import Base
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float
from sqlalchemy.schema import ForeignKey
from sqlalchemy.orm import relationship

class Competitions(Base):
    __tablename__= "competitions_competitions"
    id=Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, default=datetime.utcnow(), onupdate=datetime.now())
    updated_at = Column(DateTime, default=datetime.utcnow(), onupdate=datetime.now())
    id_competition = Column(Integer)
    name = Column(String)
    code = Column(String)
    type = Column(String)
    emblem = Column(String)

    teams = relationship("Teams", back_populates="competitions")

class Teams(Base):
    __tablename__= "competitions_teams"
    id=Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, default=datetime.utcnow(), onupdate=datetime.now())
    updated_at = Column(DateTime, default=datetime.utcnow(), onupdate=datetime.now())
    competitions_id = Column(Integer, ForeignKey("competitions_competitions.id"))
    id_team = Column(Integer, unique=True)
    name = Column(String)
    short_name = Column(String)
    emblem = Column(String)

    competitions = relationship("Competitions", back_populates="teams")

class Matchs(Base):
    __tablename__= "competitions_matchs"
    id=Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, default=datetime.utcnow(), onupdate=datetime.now())
    updated_at = Column(DateTime, default=datetime.utcnow(), onupdate=datetime.now())
    id_match = Column(Integer, unique=True)
    cod_competitions = Column(String)
    date =  Column(String)
    hour =  Column(String)
    id_team_home = Column(Integer)
    id_team_away = Column(Integer)
    score_home = Column(Integer)
    score_away = Column(Integer)
    status = Column(String)

class MatchsFootballGames(Base):
    __tablename__= "competitions_matchs_footballgames"
    id=Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, default=datetime.utcnow(), onupdate=datetime.now())
    updated_at = Column(DateTime, default=datetime.utcnow(), onupdate=datetime.now())
    id_match = Column(Integer)
    id_footballgames = Column(Integer)