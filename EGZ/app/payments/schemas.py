from pydantic import BaseModel
from typing import Optional

# class Payments(BaseModel):
#     commission_agent_id: Optional[int] = None
#     tournaments_id: int
#     amount_pay: int

class InputPayments(BaseModel):
    commission_agent_id: Optional[int] = None
    discount: Optional[float] = 0
    phone: str
    approval_code: str
    tournament_id: int

class Payments(BaseModel):
    appuser_id: int
    commission_agent_id: Optional[int] = None
    tournaments_id: int
    day: str
    hour: str
    pay_phone: str
    id_mercado_pago: str
    total_paid_amount: float
    net_received_amount: float