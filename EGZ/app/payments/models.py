from app.database import Base
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float
from sqlalchemy.schema import ForeignKey
from sqlalchemy.orm import relationship

class CommissionAgent(Base):
    __tablename__ = "payments_commission_agent"
    id = Column(Integer, primary_key=True, autoincrement=True)
    appuser_id = Column(Integer, unique=True)
    start_date = Column(String)
    end_date = Column(String)
    codigo = Column(String, unique=True)
    percent = Column(Integer)

    event_coupon = relationship("EventCoupon", back_populates="commission_agent")

class EventCoupon(Base):
    __tablename__ = "payments_event_coupon"
    id = Column(Integer, primary_key=True, autoincrement=True)
    appuser_id = Column(Integer)
    day = Column(String)
    hour = Column(String)
    commission_agent_id = Column(Integer, ForeignKey("payments_commission_agent.id"))
    tournaments_id = Column(Integer)

    commission_agent = relationship("CommissionAgent", back_populates="event_coupon")

class Payments(Base):
    __tablename__ = "payments_payments"
    id = Column(Integer, primary_key=True, autoincrement=True)
    appuser_id = Column(Integer)
    commission_agent_id = Column(Integer)
    tournaments_id = Column(Integer)
    day = Column(String)
    hour = Column(String)
    pay_phone = Column(String)
    id_mercado_pago = Column(String)
    total_paid_amount = Column(Float)
    net_received_amount = Column(Float)