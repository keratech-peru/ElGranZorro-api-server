import requests
import pytz
from typing import List
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from app.database import CRUD
from app.users.models import AppUsers
from app.tournaments.models import Tournaments
from app.payments.models import CommissionAgent, Payments, PaymentsCommissionAgent
from app.payments.constants import Coupon, StatusPayments, StatusPaymentsCommissionAgent
from app.payments import schemas
from app.config import MercadoPago
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
    def coupon_valid(commission_agent: CommissionAgent) -> bool:
        now_date = datetime.now(pytz.timezone("America/Lima"))
        end_date = datetime.strptime(f'{commission_agent.end_date}', '%d/%m/%Y').replace(tzinfo=timezone.utc)
        dif = end_date - now_date
        return int(dif.days) >= 0

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
            status = StatusPayments.FREE if id_mercado_pago == "" else StatusPayments.RECEIVED
        )
        if input_payment.commission_agent_id:
            payment_commission_agent = PaymentsCommissionAgent(
                payment_id = new_payment.id,
                status = StatusPaymentsCommissionAgent.WAITING
            )
            CRUD.insert(db, payment_commission_agent)
        CRUD.insert(db, new_payment)
        return new_payment

    @staticmethod
    def toke_generation_mercado_pago(phone, approval_code):
        query_params = {'public_key': MercadoPago.PUBLIC_KEY}
        body = { "phoneNumber": phone ,"otp": approval_code }
        resp_token = requests.post(MercadoPago.URL_GENERATE_TOKEN, json=body, params=query_params)
        return resp_token
    
    @staticmethod
    def payment_mercado_pago(db : Session, email: str, tournament_id: int, discount: float, token:str):
        tournament = db.query(Tournaments).filter(Tournaments.id == tournament_id).first()
        amount = round((tournament.quota)*(1 - discount),1)
        headers = {
            'Authorization': f'Bearer {MercadoPago.ACCESS_TOKEN}',
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
            resp_payment = requests.post(MercadoPago.URL_PAYMENT, headers=headers, json=body)
        return resp_payment, amount

    @staticmethod
    def pending_refund(db : Session ,tournament_id : int , user):
        payment = db.query(Payments).filter(Payments.appuser_id == user.id, Payments.tournaments_id == tournament_id).first()
        payment.status = StatusPayments.WAITING_FOR_REFOUND
        CRUD.update(db, payment)
        payments_commission_agent = db.query(PaymentsCommissionAgent).filter(PaymentsCommissionAgent.payment_id == payment.id).first()
        if payments_commission_agent:
            payments_commission_agent.status = StatusPaymentsCommissionAgent.REFUND
            CRUD.update(db, payments_commission_agent)
    
    @staticmethod
    def list_search_codigo(db: Session):
        payments_ = []
        payments = db.query(Payments).order_by(Payments.id.desc()).all()
        for payment in payments:
            appuser = db.query(AppUsers).filter(AppUsers.id == payment.appuser_id).first()
            commission_agent = db.query(CommissionAgent).filter(CommissionAgent.id == payment.commission_agent_id).first()
            tournament = db.query(Tournaments).filter(Tournaments.id == payment.tournaments_id).first()
            payment_ = payment.__dict__
            payment_["appuser"] = appuser.name + " " + appuser.lastname
            payment_["commission_agent"] = commission_agent.codigo
            payment_["tournament"] = tournament.codigo
            payment_["day_hour"] = payment.day + " " + payment.hour
            payments_.append(payment_)
        return payments_
    
    @staticmethod
    def list_all_for_commission_agent(db: Session, commission_agent_id: int):
        payments = db.query(Payments).filter(Payments.commission_agent_id == commission_agent_id).all()
        payments_commission_agent = []
        payments_enabled = False
        for payment in payments:
            payment_commission_agent_ = {}
            payment_commission_agent = db.query(PaymentsCommissionAgent).filter(PaymentsCommissionAgent.payment_id == payment.id).first()
            tournament = db.query(Tournaments).filter(Tournaments.id == payment.tournaments_id).first()
            payment_commission_agent_["id_mercado_pago"] = payment.id_mercado_pago
            payment_commission_agent_["tournament"] = tournament.name
            payment_commission_agent_["appuser_id"] = payment.appuser_id
            payment_commission_agent_["day_hour"] = payment.day + " " + payment.hour
            payment_commission_agent_["status"] = payment_commission_agent.status
            payments_enabled = payments_enabled or (payment_commission_agent_["status"] == StatusPaymentsCommissionAgent.APPROVED)
            payments_commission_agent.append(payment_commission_agent_)
        return payments_commission_agent, payments_enabled