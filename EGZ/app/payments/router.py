from fastapi import APIRouter, Depends, status, Request
from typing import Dict, List
from sqlalchemy.orm import Session
from app.users.models import AppUsers
from app.payments import exception
from app.payments.schemas import InputPayments
from app.payments.models import CommissionAgent, EventCoupon, Payments
from app.payments.service import CommissionAgent_, Payments_, EventCoupon_
from app.database import get_db
from app.security import get_user_current

router = APIRouter(prefix="/payments", tags=["payments"])

@router.post("/commission-agent", status_code=status.HTTP_201_CREATED)
def commission_agent_create(
    db: Session = Depends(get_db),
    user: AppUsers = Depends(get_user_current)
    ) -> Dict[str, object]:
        """
        **Descripcion** : El servicio de creacion de comisionista.
        \n**Excepcion** : 
            \n- El servicio requiere api-key.
        """
        commission_agent = db.query(CommissionAgent).filter(CommissionAgent.appuser_id == user.id).first()
        if commission_agent:
            raise exception.user_already_commission_agent
        new_commission_agent = CommissionAgent_.create(db, user)
        return {"status": "done", "commission_agent_id": new_commission_agent.id}

@router.get("/coupon/{codigo}", status_code=status.HTTP_200_OK)
def discount_get(
    codigo: str,
    db: Session = Depends(get_db),
    __: AppUsers = Depends(get_user_current)
    ) -> Dict[str, object]:
        """
        **Descripcion** : El servicio permite acceder a un cupon para la inscripcion de un torneo.
        \n**Excepcion** : 
            \n- El servicio requiere autorizacion via token
            \n- El servicio tiene excepcion si el token es invalido o expiro
        """
        commission_agent = db.query(CommissionAgent).filter(CommissionAgent.codigo == codigo).first()
        if not commission_agent:
            raise exception.invalid_coupon
        if not CommissionAgent_.valid_coupon(commission_agent):
            raise exception.coupon_expired
        return {"status":"done", "coupon":{"percent": commission_agent.percent, "id": commission_agent.id}}

# @router.post("/hola", status_code=status.HTTP_201_CREATED)
# def payments(
#     payments_in: schemas.Payments,
#     db: Session = Depends(get_db),
#     user: AppUsers = Depends(get_user_current)
#     ) -> Dict[str, object]:
#         """
#         **Descripcion** : El servicio para realizar un pago.
#         \n**Excepcion** : 
#             \n- El servicio requiere api-key.
#         """
#         commission_agent = db.query(CommissionAgent).filter(CommissionAgent.id == payments_in.commission_agent_id).first()
#         if not commission_agent:
#             raise exception.not_existent_commission_agent
#         tournament = db.query(Tournaments).filter(Tournaments.id == payments_in.tournaments_id).first()
#         if not tournament:
#             raise exception.tournament_does_not_exist
#         new_payment = Payments_.create(db, user.id, payments_in)
#         EventCoupon_.create(db, user.id, payments_in.tournaments_id, payments_in.commission_agent_id)
#         return {"status": "done", "payment_id": new_payment.id}

@router.post("/", status_code=status.HTTP_201_CREATED)
def payments(
    input_payments: InputPayments,
    db: Session = Depends(get_db),
    user: AppUsers = Depends(get_user_current)
    ) -> Dict[str, object]:
    """
        **Descripcion** : El servicio para realizar un pago.
        \n**Excepcion** : 
            \n- El servicio requiere autenticacion.
            \n- 
    """
    resp_toke = Payments_.toke_generation_mercado_pago(input_payments.phone, input_payments.approval_code)
    if resp_toke.status_code != 200:
        raise exception.token_generation_fails
    token = resp_toke.json()["id"]

    resp_payment = Payments_.payment_mercado_pago(db, user.email, input_payments.tournament_id, input_payments.discount, token)
    if resp_payment.json()["status"] !=  "approved":
        raise exception.rejected_payment
    new_payment = Payments_.create(
        db,
        user.id,
        input_payments,
        id_mercado_pago = resp_payment.json()["id"],
        total_paid_amount = resp_payment.json()["transaction_details"]["total_paid_amount"],
        net_received_amount = resp_payment.json()["transaction_details"]["net_received_amount"]
    )

    return {"data":new_payment}