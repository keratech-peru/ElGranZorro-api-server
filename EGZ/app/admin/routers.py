from fastapi import APIRouter, Request, Form, UploadFile, File, Depends, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from typing import Optional
from sqlalchemy.orm import Session
from app.tournaments.schemas import Tourmaments as SchemasTournaments, FootballGames as SchemasFootballGames, UpdateFootballGames as SchemasUpdateFootballGames
from app.tournaments.models import Tournaments as ModelsTournaments, FootballGames as ModelsFootballGames, GroupStage as ModelsGroupStage, ConfrontationsGroupStage as ModelsConfrontationsGroupStage
from app.tournaments.service import Tournaments_, FootballGames_, Confrontations_
from app.tournaments.utils import code_generator_tournaments
from app.tournaments.constants import Players
from app.users.models import PlaysUsers as ModelsPlaysUsers
from app.users.service import AppUsers_
from app.database import get_db, CRUD
from app.security import valid_access_token, create_token
from app.admin import exception
from app.admin.constants import RESOURCES
from app.config import USERNAME, PASSWORD, TOKEN_SCONDS_EXP
import os

FILEDIR = os.getcwd() + "/app/admin/archivos/"

router = APIRouter(prefix="/admin", tags=["admin"])
templates = Jinja2Templates(directory="app/admin/templates")


@router.post("/login", response_class=HTMLResponse)
def get_login(request: Request, username: str = Form(...), password: str = Form(...)):
    if not (username == USERNAME and password == PASSWORD):
        return templates.TemplateResponse("login.html", {"request": request, "error":True})
    token = create_token({"username":username})
    return RedirectResponse("/admin/tournaments/list", status_code=302, headers={"set-cookie" : f"access_token={token}; Max-Age={TOKEN_SCONDS_EXP}"})  

@router.post("/tournaments", response_class=HTMLResponse)
async def create_tournaments(request: Request,
            name: str = Form(...),
            logo: str = Form(...),
            start_date: str = Form(...),
            tournament_rules: str = Form(...),
            db: Session = Depends(get_db)):
    codigo, id = code_generator_tournaments(db)       
    obj = SchemasTournaments(               
        name=name,
        codigo=codigo,
        logo=logo,
        start_date=start_date,
        max_number_of_players=Players.MAXIMO,
        game_mode=Players.GAME_MODE,
        tournament_rules=tournament_rules                                                                                      
    )    
    CRUD.insert(db, ModelsTournaments(**obj.dict()))

    FootballGames_.create_groups_stage(id, codigo, start_date, db)
    FootballGames_.create_eighths_stage(id, codigo, start_date, db)
    FootballGames_.create_quarter_stage(id, codigo, start_date, db)
    FootballGames_.create_semifinal_stage(id, codigo, start_date, db)
    FootballGames_.create_final_stage(id, codigo, start_date, db)

    return templates.TemplateResponse("create_tournaments.html", {"request": request ,"resources":RESOURCES})

@router.post("/footballgames", response_class=HTMLResponse)
async def create_footballgames(request: Request,
            codigo: str = Form(...),
            tournament_id: int = Form(...),
            tournament_stage: str = Form(...),
            date: str = Form(...),
            type_footballgames: str = Form(...),
            home_team: str = Form(...),
            away_team: str = Form(...),
            home_score: str = Form(...),
            away_score: str = Form(...),
            db: Session = Depends(get_db)):
    obj = SchemasFootballGames(               
        codigo=codigo,
        tournament_id=tournament_id,
        tournament_stage=tournament_stage,
        date=date,
        type_footballgames=type_footballgames,
        home_team=home_team,
        away_team=away_team,
        home_score=home_score,
        away_score=away_score                                                                                     
    )    
    CRUD.insert(db, ModelsFootballGames(**obj.dict()))
    contex =  {"request": request ,"resources":RESOURCES}
    return templates.TemplateResponse("create_footballgames.html",contex)

@router.post("/footballgames/{footballgame_id}", response_class=HTMLResponse)
async def update_footballgames(request: Request,
            footballgame_id: str,
            home_team: str = Form(...),
            away_team: str = Form(...),
            home_score: str = Form(None),
            away_score: str = Form(None),
            db: Session = Depends(get_db)):
    update_footballgame_in = SchemasUpdateFootballGames(
        home_team=home_team,
        away_team=away_team,
        home_score=home_score,
        away_score=away_score
    )
    FootballGames_.update(int(footballgame_id), update_footballgame_in, db)
    if home_score != None and away_score != None:
        footballgame = db.query(ModelsFootballGames).filter(ModelsFootballGames.id == footballgame_id).first()
        if "GP" in footballgame.codigo:
            FootballGames_.update_group_stage(footballgame, home_score, away_score, db)
        else:
            FootballGames_.update_key_stage(footballgame, home_score, away_score, db)
    list_all = FootballGames_.list_all(db)
    contex =  {"request": request ,"resources":RESOURCES,"tablas":list_all}
    return templates.TemplateResponse("table_footballgames.html",contex)


#------------------------------------------------------------------------------------------------

@router.get("/login", response_class=HTMLResponse)
def view_login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.get("/{table_name}/list", response_class=HTMLResponse)
def view_table(request: Request ,table_name: str, access_token: Optional[str] = Cookie(None), db: Session = Depends(get_db)):
    valid_access_token(access_token)
    list_all = []
    if table_name in 'tournaments':
        list_all = Tournaments_.list_all(db)
    elif table_name in 'footballgames':
        list_all = FootballGames_.list_all(db)
    elif table_name in 'appusers':
        list_all = AppUsers_.list_all(db)
    else:
        raise exception.table_does_not_exist
    contex = {"request": request,"resources":RESOURCES, "title": "Hi", "table_name":table_name , "tablas":list_all}
    return templates.TemplateResponse(f"table_{table_name}.html",contex)

@router.get("/{table_name}/create", response_class=HTMLResponse)
def view_create_record_in_table(request: Request, table_name: str, access_token: Optional[str] = Cookie(None)):
    valid_access_token(access_token)
    contex = {"request": request,"resources":RESOURCES}
    return templates.TemplateResponse(f"create_{table_name}.html", contex)

@router.get("/footballgames/update/{pk}", response_class=HTMLResponse)
def view_update_record_in_table(request: Request, pk: str, access_token: Optional[str] = Cookie(None), db: Session = Depends(get_db)):
    valid_access_token(access_token)
    footballgame = db.query(ModelsFootballGames).filter(ModelsFootballGames.id == pk).first()
    contex = {"request": request,"resources":RESOURCES, "pk": pk ,"footballgame":footballgame}
    return templates.TemplateResponse(f"update_footballgames.html", contex)