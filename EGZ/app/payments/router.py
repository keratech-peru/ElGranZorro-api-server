from fastapi import APIRouter, Depends, status, Request
from typing import Dict
from sqlalchemy.orm import Session
from app.users.models import AppUsers
from app.payments import exception
from app.payments.schemas import InputPayments
from app.payments.models import CommissionAgent, Payments
from app.payments.service import CommissionAgent_, Payments_
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

@router.get("/commission-agent", status_code=status.HTTP_200_OK)
def commission_agent(
    db: Session = Depends(get_db),
    user: AppUsers = Depends(get_user_current)
    ) -> Dict[str, object]:
        """
        **Descripcion** : El servicio que muestra la informacion del dashboard de Commision Agent.
        \n**Excepcion** : 
            \n- El servicio requiere autorizacion via token
            \n- El servicio tiene excepcion si el token es invalido o expiro
            \n- El servicio tiene excepcion si el usuario no es un agente commission-agent
        """
        commission_agent = db.query(CommissionAgent).filter(CommissionAgent.appuser_id == user.id).first()
        if commission_agent:
            exception.user_is_not_commission_agent
        commission_table, is_active_botton = Payments_.list_all_for_commission_agent(db , commission_agent.id)
        return {
            "status":"done",
            "data": {
                "commission_agent" : commission_agent,
                "commission_table" : commission_table,
                "is_active_botton" : is_active_botton
                }
            }

@router.get("/coupon/{codigo}", status_code=status.HTTP_200_OK)
def discount_get(
    codigo: str,
    db: Session = Depends(get_db),
    user: AppUsers = Depends(get_user_current)
    ) -> Dict[str, object]:
        """
        **Descripcion** : El servicio permite acceder a un cupon para la inscripcion de un torneo.
        \n**Excepcion** : 
            \n- El servicio requiere autorizacion via token
            \n- El servicio tiene excepcion si el token es invalido o expiro
            \n- El servicio tiene excepcion cuando el cupon no existe
            \n- El servicio tiene excepcion cuando el cupon caduco
            \n- El servicio tiene excepcion cuando el dueño del cupon quiere usar su propio cupon
        """
        commission_agent = db.query(CommissionAgent).filter(CommissionAgent.codigo == codigo).first()
        if not commission_agent:
            raise exception.not_exist_coupon
        if not CommissionAgent_.coupon_valid(commission_agent):
            raise exception.coupon_expired
        if user.id == commission_agent.appuser_id:
            raise exception.coupon_not_allowed_user
        return {
            "status":"done",
            "detail":{
                "message":f"Cupón valido, descuento del {commission_agent.percent}%",
                "coupon":{"percent": commission_agent.percent, "id": commission_agent.id}
                }
            }

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
            \n- El servicio tiene excepcion si el token es invalido o expiro
            \n- El servicio tiene excepcion cuando la generacion del token falla
            \n- El servicio tiene excepcion cuando el pago es rechazado
            \n- El servicio tiene excepcion cuando el dueño del cupon quiere usar su propio cupon 
    """
    commission_agent = db.query(CommissionAgent).filter(CommissionAgent.id == input_payments.commission_agent_id).first()
    if user.id == commission_agent.appuser_id:
        raise exception.coupon_not_allowed_user

    payment = db.query(Payments).filter(Payments.appuser_id == user.id , Payments.tournaments_id == input_payments.tournament_id).first()
    if payment:
        raise exception.payment_already_registered

    resp_toke = Payments_.toke_generation_mercado_pago(input_payments.phone, input_payments.approval_code)
    if resp_toke.status_code != 200:
        raise exception.token_generation_fails
    token = resp_toke.json()["id"]

    resp_payment, amount = Payments_.payment_mercado_pago(db, user.email, input_payments.tournament_id, commission_agent.percent/100, token)
    if amount > 2:
        if resp_payment.json()["status"] !=  "approved":
            raise exception.rejected_payment

    new_payment = Payments_.create(
        db,
        user.id,
        input_payments,
        id_mercado_pago = resp_payment.json()["id"] if amount > 2 else "",
        total_paid_amount = resp_payment.json()["transaction_details"]["total_paid_amount"] if amount > 2 else 0,
        net_received_amount = resp_payment.json()["transaction_details"]["net_received_amount"] if amount > 2 else 0
    )
    return {"data":new_payment}