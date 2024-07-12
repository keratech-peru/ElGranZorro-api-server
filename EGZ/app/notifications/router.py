from fastapi import APIRouter, Depends, status, Request
from typing import Dict
from sqlalchemy.orm import Session
from app.notifications.schemas import NotificationsEmail
from app.notifications.service import Notificaciones_
from app.database import get_db
from app.security import valid_header
from app.config import ApiKey




router = APIRouter(prefix="/notifications", tags=["notifications"])

@router.post("/email", status_code=status.HTTP_201_CREATED)
def user_create(
    request: Request,
    notification_in: NotificationsEmail,
    db: Session = Depends(get_db),
    ) -> Dict[str, object]:
        """
        **Descripcion** : El servicio crea un usuario.
        \n**Excepcion** : 
            \n- El servicio requiere api-key.
            \n- El servicio tiene excepcion si el email ya pertenece a otro usuario.
        """
        valid_header(request, ApiKey.USERS)
        Notificaciones_.send_email(notification_in.mensaje, notification_in.email, "SOPORTE-EGZ : " + notification_in.asunto)
        return {"status": "done"}