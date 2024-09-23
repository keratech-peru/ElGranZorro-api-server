import requests
import pytz
from typing import List
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from app.database import CRUD
from app.users.models import AppUsers
from app.tournaments.models import Tournaments
from app.payments.models import CommissionAgent, EventCoupon, Payments
from app.payments.constants import Coupon, URL_GENERATE_TOKEN, URL_PAYMENT
from app.payments import schemas
from app.config import YOUR_ACCESS_TOKEN, YOUR_PUBLIC_KEY
import uuid

class CommissionAgent_(CRUD):
    @staticmethod
    def create(db: Session, appuser: AppUsers) -> CommissionAgent:
        start_date = datetime.now(pytz.timezone("America/Lima"))
        end_date = start_date + timedelta(days=Coupon.DURATION)
        new_commission_agent = CommissionAgent(
            appuser_id=appuser.id,
            start_date=start_date.strftime('%d/%m/%Y'),
            end_date=end_date.strftime('%d/%m/%Y'),
            codigo=appuser.dni[:4] + appuser.name[:2].upper(),
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
        date_now, hour_now = datetime.strftime(datetime.now(pytz.timezone("America/Lima")),'%d/%m/%y %H:%M:%S').split(" ")
        new_event_coupon = EventCoupon(
            appuser_id=appuser_id,
            day=date_now,
            hour=hour_now,
            commission_agent_id=commission_agent_id,
            tournaments_id=tournament_id,
        )
        CRUD.insert(db, new_event_coupon)

class Payments_(CRUD):
    @staticmethod
    def create(
            db: Session,
            user_id:int,
            input_payment: schemas.InputPayments,
            id_mercado_pago: int,
            total_paid_amount:float,
            net_received_amount:float
        ) -> Payments:
        date_now, hour_now = datetime.strftime(datetime.now(pytz.timezone("America/Lima")),'%d/%m/%y %H:%M:%S').split(" ")
        new_payment = Payments(
            appuser_id=user_id,
            commission_agent_id=input_payment.commission_agent_id,
            tournaments_id=input_payment.tournament_id,
            day=date_now,
            hour=hour_now,
            pay_phone=input_payment.phone,
            id_mercado_pago=id_mercado_pago,
            total_paid_amount=total_paid_amount,
            net_received_amount=net_received_amount,
            status="RECIBIDO" 
        )
        CRUD.insert(db, new_payment)
        return new_payment

    @staticmethod
    def toke_generation_mercado_pago(phone, approval_code):
        query_params = {'public_key': YOUR_PUBLIC_KEY}
        body = { "phoneNumber": phone ,"otp": approval_code }
        resp_token = requests.post(URL_GENERATE_TOKEN, json=body, params=query_params)
        return resp_token
    
    @staticmethod
    def payment_mercado_pago(db : Session, email: str, tournament_id: int, discount: float, token:str):
        tournament = db.query(Tournaments).filter(Tournaments.id == tournament_id).first()
        amount = round((tournament.quota)*(1 - discount),1)
        headers = {
            'Authorization': f'Bearer {YOUR_ACCESS_TOKEN}',
            "Content-Type": "application/json",
            "x-idempotency-key": str(uuid.uuid4())
        }
        body = {
            "token": token,
            "transaction_amount": amount,
            "description": f"tournament_id: {tournament.id} , tournament_name: {tournament.name}",
            "installments": 1,
            "payment_method_id": "yape",
            "payer": {
                "email": email
            }
        }
        resp_payment = {}
        if amount > 2:
            resp_payment = requests.post(URL_PAYMENT, headers=headers, json=body)
        return resp_payment, amount