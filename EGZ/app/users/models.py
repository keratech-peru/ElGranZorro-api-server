from app.database import Base
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float
from sqlalchemy.schema import ForeignKey
from sqlalchemy.orm import relationship

class AppUsers(Base):
    __tablename__= "users_appusers"
    id=Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, default=datetime.now(), onupdate=datetime.now())
    updated_at = Column(DateTime, default=datetime.now(), onupdate=datetime.now())
    name = Column(String)
    lastname = Column(String)
    birthdate = Column(String)
    phone = Column(String)
    email = Column(String, unique=True)
    password = Column(String)
    what_team_are_you_fan = Column(String)
    from_what_age_are_you_fan = Column(String)
    imagen = Column(String)
    username = Column(String)
    team_name = Column(String)
    team_logo = Column(String)

    enrollment_user = relationship("EnrollmentUsers", back_populates="appuser")
    plays_users = relationship("PlaysUsers", back_populates="appuser")

class EnrollmentUsers(Base):
    __tablename__= "users_enrollment_users"
    id=Column(Integer, primary_key=True, autoincrement=True )
    appuser_id = Column(Integer, ForeignKey("users_appusers.id"))
    tournaments_id = Column(Integer)
    state = Column(String)

    appuser = relationship("AppUsers", back_populates="enrollment_user")

class PlaysUsers(Base):
    __tablename__= "users_plays_users"
    id=Column(Integer, primary_key=True, autoincrement=True )
    created_at = Column(DateTime, default=datetime.now(), onupdate=datetime.now())
    updated_at = Column(DateTime, default=datetime.now(), onupdate=datetime.now())
    appuser_id = Column(Integer, ForeignKey("users_appusers.id"))
    football_games_id = Column(Integer)
    score_local = Column(Integer)
    score_visit = Column(Integer)

    appuser = relationship("AppUsers", back_populates="plays_users")

