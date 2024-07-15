from pydantic import BaseModel
from typing import Optional

class NotificationsEmail(BaseModel):
    email: str
    asunto: str
    mensaje: str
