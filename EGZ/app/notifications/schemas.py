from pydantic import BaseModel
from typing import Optional

class NotificationsEmail(BaseModel):
    email: str
    asunto: str
    mensaje: str

class NumberVerification(BaseModel):
    appuser_id: int
    phone: str
    otp: str
    is_verification: bool
    is_user_respond: bool = False