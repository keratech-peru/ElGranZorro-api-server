from pydantic import BaseModel
from typing import Optional

class Payments(BaseModel):
    commission_agent_id: Optional[int] = None
    tournaments_id: int
    amount_pay: int