from app.database import Base
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float

class Tourmaments(Base):
    __tablename__= "tourmaments_tournament"
    id=Column(Integer, primary_key=True, autoincrement=True )
    created_at = Column(DateTime, default=datetime.now(), onupdate=datetime.now())
    updated_at = Column(DateTime, default=datetime.now(), onupdate=datetime.now())
    name = Column(String)
    codigo = Column(String)
    logo = Column(String)
    start_date = Column(String)
    max_number_of_players = Column(String)
    game_mode = Column(String)
    tournament_rules = Column(String)
