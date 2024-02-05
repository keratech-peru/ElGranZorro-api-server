from app.database import Base
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float

class AppUsers(Base):
    __tablename__= "users_appusers"
    id=Column(Integer, primary_key=True, autoincrement=True )
    created_at = Column(DateTime, default=datetime.now(), onupdate=datetime.now())
    updated_at = Column(DateTime, default=datetime.now(), onupdate=datetime.now())
    name = Column(String)
    lastname = Column(String)
    birthdate = Column(String)
    phone = Column(String)
    email = Column(String)
    password = Column(String)
    what_team_are_you_fan = Column(String)
    from_what_age_are_you_fan = Column(String)
