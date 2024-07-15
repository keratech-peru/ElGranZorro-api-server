from app.database import Base
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float
from sqlalchemy.schema import ForeignKey
from sqlalchemy.orm import relationship


class NumberVerification(Base):
    __tablename__= "notification_number_verification"
    id=Column(Integer, primary_key=True, autoincrement=True )
    appuser_id = Column(Integer)
    phone = Column(String)
    otp = str
    is_verification = Column(Boolean)
    is_user_respond = Column(Boolean)