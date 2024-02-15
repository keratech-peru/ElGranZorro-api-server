from fastapi import APIRouter, Request, Form, UploadFile, File, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import Dict
from sqlalchemy.orm import Session
from app.users.service import AppUsers_
from app.users import schemas
from app.tournaments.schemas import Tourmaments as SchemasTournaments
from app.tournaments.models import Tourmaments as ModelsTournaments
from app.database import get_db, CRUD
from app.security import valid_header
from app.constants import ApiKey
import pandas as pd
import os
import datetime as dt

FILEDIR = os.getcwd() + "/app/admin/archivos/"

router = APIRouter(prefix="/admin", tags=["admin"])
templates = Jinja2Templates(directory="app/admin/templates")

@router.get("/file-upload", response_class=HTMLResponse)
def get_basic_form(request: Request):
    return templates.TemplateResponse("form.html", {"request": request})

@router.post('/file-upload', response_class=HTMLResponse)
async def post_basic_form(request: Request, username: str = Form(...), password: str = Form(...), file: UploadFile = File(...), db: Session = Depends(get_db)):     
    contents = await file.read()
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

    return templates.TemplateResponse("form.html", {"request": request})
