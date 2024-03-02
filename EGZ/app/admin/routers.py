from fastapi import APIRouter, Request, Form, UploadFile, File, Depends, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from typing import Dict, Optional
from sqlalchemy.orm import Session
from app.tournaments.schemas import Tourmaments as SchemasTournaments
from app.tournaments.models import Tournaments as ModelsTournaments
from app.tournaments.service import Tournaments_, FootballGames_
from app.database import get_db, CRUD
from app.security import valid_header
from app.constants import ApiKey
from app.admin import exception
from app.admin.constants import RESOURCES
from app.config import USERNAME, PASSWORD
import pandas as pd
import os
from jose import jwt, JWTError
from datetime import datetime, timedelta


FILEDIR = os.getcwd() + "/app/admin/archivos/"

router = APIRouter(prefix="/admin", tags=["admin"])
templates = Jinja2Templates(directory="app/admin/templates")


SECRETE_KEY = "a2468f571c35be1540412ac8053e97ed164569cb33350b7848d0342d9a2ee7c0"
TOKEN_SCONDS_EXP = 10

def create_token(data: list):
    data_token = data.copy()
    data_token["exp"] = datetime.utcnow() + timedelta(seconds=TOKEN_SCONDS_EXP)
    token_jwt = jwt.encode(data_token, key=SECRETE_KEY, algorithm="HS256")
    return token_jwt

@router.get("/login", response_class=HTMLResponse)
def get_login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login", response_class=HTMLResponse)
def get_login(request: Request, username: str = Form(...), password: str = Form(...)):
    if not (username == USERNAME and password == PASSWORD):
        return templates.TemplateResponse("login.html", {"request": request, "error":True})
    token = create_token({"username":username})
    return RedirectResponse("/admin/table/tournaments", status_code=302, headers={"set-cookie" : f"access_token={token}; Max-Age={TOKEN_SCONDS_EXP}"})  

@router.post('/file-upload', response_class=HTMLResponse)
async def post_basic_form(request: Request, username: str = Form(...), password: str = Form(...), file: UploadFile = File(...), db: Session = Depends(get_db)):     
    contents = await file.read()

    if not (username == USERNAME and password == PASSWORD):
        raise exception.unauthorized

    if file.filename.split(".")[-1] != "xsls":
        raise exception.file_not_allowed
 
    with open(f"{FILEDIR}{file.filename}", "wb") as f:
        f.write(contents)
    excel_data_df = pd.read_excel(f"{FILEDIR}{file.filename}")

    for __, row in excel_data_df.iterrows():              
        obj = SchemasTournaments(               
            name=row["name"],
            codigo=row["codigo"],
            logo=row["logo"],
            start_date=row["start_date"].strftime('%Y-%m-%d %X'),
            max_number_of_players=row["max_number_of_players"],
            game_mode=row["game_mode"],
            tournament_rules=row["tournament_rules"]                                                                                      
        )        
        CRUD.insert(db, ModelsTournaments(**obj.dict()))

    os.remove(f"{FILEDIR}{file.filename}")
    tourmaments = Tournaments_.list_all(db)
    return templates.TemplateResponse("bootstrap_table.html",{"request": request, "title":'Bootstrap Table', "tourmaments":tourmaments})


@router.get("/table/{table_name}", response_class=HTMLResponse)
def get_basic_table(request: Request ,table_name: str, access_token: Optional[str] = Cookie(None), db: Session = Depends(get_db)):
    if access_token is None:
        return RedirectResponse("/admin/login", status_code=302)
    try:
        data_user = jwt.decode(access_token, key=SECRETE_KEY, algorithms=["HS256"])
        if data_user["username"] != USERNAME:
            return RedirectResponse("/admin/login", status_code=302)
    except JWTError:
        return RedirectResponse("/admin/login", status_code=302)
    list_all = []
    if table_name in 'tournaments':
        list_all = Tournaments_.list_all(db)
    elif table_name in 'footballgames':
        list_all = FootballGames_.list_all(db)
    else:
        raise exception.table_does_not_exist
    return templates.TemplateResponse(f"table_{table_name}.html",{"request": request,"resources":RESOURCES, "title": "Hi", "table_name":table_name , "tablas":list_all})