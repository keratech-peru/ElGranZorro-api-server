import random
import pytz
from typing import List
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from app.database import CRUD
from app.users.models import AppUsers
from app.payments.models import CommissionAgent, EventCoupon, Payments
from app.payments.constants import Coupon
from app.payments import schemas

class CommissionAgent_(CRUD):
    @staticmethod
    def create(db: Session, appuser: AppUsers) -> CommissionAgent:
        start_date = datetime.now(pytz.timezone("America/Lima"))
        end_date = start_date + timedelta(days=Coupon.DURATION)
        new_commission_agent = CommissionAgent(
            appuser_id=appuser.id,
            start_date=start_date.strftime('%d/%m/%Y'),
            end_date=end_date.strftime('%d/%m/%Y'),
            codigo=appuser.dni[:4],
            percent=Coupon.PERCENT
        )
        CRUD.insert(db, new_commission_agent)
        return new_commission_agent
    
    @staticmethod
    def valid_coupon(commission_agent: CommissionAgent) -> bool:
        now_date = datetime.now(pytz.timezone("America/Lima"))
        end_date = datetime.strptime(f'{commission_agent.end_date}', '%d/%m/%Y').replace(tzinfo=timezone.utc)
        dif = end_date - now_date
        return int(dif.days) >= 0

class EventCoupon_(CRUD):
    @staticmethod
    def create(db: Session, appuser_id: int, tournament_id: int, commission_agent_id: int) -> EventCoupon:
        new_event_coupon = EventCoupon(
            appuser_id=appuser_id,
            commission_agent_id=commission_agent_id.id,
            tournaments_id=tournament_id,
        )
        CRUD.insert(db, new_event_coupon)

class Payments_(CRUD):
    @staticmethod
    def create(db: Session, user_id:int, payment_in: schemas.Payments) -> Payments:
        date_now, hour_now = datetime.strftime(datetime.now(pytz.timezone("America/Lima")),'%d/%m/%y %H:%M:%S').split(" ")
        new_payment = Payments(
            appuser_id=user_id,
            commission_agent_id=payment_in.commission_agent_id,
            tournaments_id=payment_in.tournaments_id,
            day=date_now,
            hour=hour_now,
            amount_pay=payment_in.amount_pay,
            payment_accepted=True
        )
        CRUD.insert(db, new_payment)
        return new_payment