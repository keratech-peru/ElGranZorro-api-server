from fastapi import APIRouter, Depends, status, Request
from typing import Dict
from sqlalchemy.orm import Session
from app.users.service import AppUsers_
from app.users import schemas
from app.database import get_db
from app.security import valid_header
from app.constants import ApiKey

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/create", status_code=status.HTTP_201_CREATED)
def create(
    request: Request,
    user_in: schemas.AppUsers,
    db: Session = Depends(get_db),
    ) -> Dict[str, object]:
        #valid_header(request, ApiKey.USERS)
        new_user = AppUsers_.create(user_in, db)
        return {"status": "done", "user_id": new_user.id}
