from app.database import Base
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float
from sqlalchemy.schema import ForeignKey
from sqlalchemy.orm import relationship

class AppUsers(Base):
    __tablename__= "users_appusers"
    id=Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, default=datetime.utcnow(), onupdate=datetime.now())
    updated_at = Column(DateTime, default=datetime.utcnow(), onupdate=datetime.now())
    name = Column(String)
    lastname = Column(String)
    birthdate = Column(String)
    phone = Column(String, unique=True)
    email = Column(String, unique=True)
    dni = Column(String)
    imagen = Column(String)
    username = Column(String)
    team_name = Column(String)
    team_logo = Column(String)

    enrollment_user = relationship("EnrollmentUsers", back_populates="appuser")
    plays_users = relationship("PlaysUsers", back_populates="appuser")
    event_log_users = relationship("EventLogUser", back_populates="appuser")
    otp_users = relationship("OtpUsers", back_populates="appuser")
    event_otp_users = relationship("EventOtpUsers", back_populates="appuser")
    commission_agent_users = relationship("CommissionAgent", back_populates="appuser")

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
    created_at = Column(DateTime, default=datetime.utcnow(), onupdate=datetime.now())
    updated_at = Column(DateTime, default=datetime.utcnow(), onupdate=datetime.now())
    appuser_id = Column(Integer, ForeignKey("users_appusers.id"))
    football_games_id = Column(Integer)
    score_local = Column(Integer)
    score_visit = Column(Integer)

    appuser = relationship("AppUsers", back_populates="plays_users")

class EventLogUser(Base):
    __tablename__= "users_event_log_users"
    id=Column(Integer, primary_key=True, autoincrement=True )
    due_date = Column(DateTime, default=lambda: datetime.utcnow())
    appuser_id = Column(Integer, ForeignKey("users_appusers.id"))
    servicio = Column(String)
    status = Column(Integer)

    appuser = relationship("AppUsers", back_populates="event_log_users")

class OtpUsers(Base):
    __tablename__= "users_otp_users"
    id=Column(Integer, primary_key=True, autoincrement=True )
    appuser_id = Column(Integer, ForeignKey("users_appusers.id"), unique = True)
    otp = Column(String)
    is_verification = Column(Boolean)
    is_user_respond = Column(Boolean)

    appuser = relationship("AppUsers", back_populates="otp_users")

class EventOtpUsers(Base):
    __tablename__ = "users_event_otp_users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    appuser_id = Column(Integer, ForeignKey("users_appusers.id"))
    due_date = Column(DateTime, default=lambda: datetime.utcnow())

    appuser = relationship("AppUsers", back_populates="event_otp_users")

class CommissionAgent(Base):
    __tablename__ = "users_commission_agent"
    id = Column(Integer, primary_key=True, autoincrement=True)
    appuser_id = Column(Integer, ForeignKey("users_appusers.id"), unique=True)
    start_date = Column(String)
    end_date = Column(String)
    codigo = Column(String, unique=True)
    percent = Column(Integer)

    appuser = relationship("AppUsers", back_populates="commission_agent_users")