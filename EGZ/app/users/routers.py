from fastapi import APIRouter, Depends, status, Request
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from typing import Dict
from sqlalchemy.orm import Session
from app.users.service import AppUsers_
from app.users import schemas
from app.users.models import AppUsers
from app.database import get_db
from app.security import create_token, valid_header
from app.config import ApiKey



router = APIRouter(prefix="/users", tags=["users"])

@router.post("/", status_code=status.HTTP_201_CREATED)
def user_create(
    request: Request,
    user_in: schemas.AppUsers,
    db: Session = Depends(get_db),
    ) -> Dict[str, object]:
        valid_header(request, ApiKey.USERS)
        new_user = AppUsers_.create(user_in, db)
        return {"status": "done", "user_id": new_user.id}

@router.get("/")
def user_get(user: AppUsers = Depends(AppUsers_.get_user_current)):
    return user

@router.put("/")
def user_put(
    user_new: schemas.UpdateAppUser,
    db: Session = Depends(get_db),
    user: AppUsers = Depends(AppUsers_.get_user_current)
    ):
    user_id = AppUsers_.update(db ,user, user_new)

    return {"status": "done", "user_id": user_id}


@router.post("/login", status_code=status.HTTP_201_CREATED)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
    ) -> Dict[str, object]:
    user = AppUsers_.authenticate(db , form_data.username, form_data.password)
    access_token_jwt = create_token({"email":user.email})
    return {
        "access_token": access_token_jwt,
        "token_type": "bearder"
    }