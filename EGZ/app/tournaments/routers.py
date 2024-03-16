from fastapi import APIRouter, Depends, status
from fastapi.encoders import jsonable_encoder
from typing import Dict
from sqlalchemy.orm import Session
from app.users.models import AppUsers
from app.tournaments.service import Tournaments_
from app.database import get_db
from app.security import get_user_current
from app.config import ApiKey, TOKEN_SCONDS_EXP



router = APIRouter(prefix="/tournaments", tags=["tournaments"])

@router.get("/", status_code=status.HTTP_201_CREATED)
def tournaments_get(
    db: Session = Depends(get_db),
    __: AppUsers = Depends(get_user_current)
    ) -> Dict[str, object]:
    tournaments = Tournaments_.list_all(db)
    return {"status": "done", "data": tournaments}