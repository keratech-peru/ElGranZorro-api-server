from fastapi import APIRouter, Request, Form, Query, Depends, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_302_FOUND
from typing import Optional, List
from sqlalchemy.orm import Session
from app.competitions.service import Competitions_
from app.tournaments.schemas import Tourmaments as SchemasTournaments, FootballGames as SchemasFootballGames, UpdateFootballGames as SchemasUpdateFootballGames, UpdateTourmaments as SchemasUpdateTourmaments
from app.tournaments.models import Tournaments as ModelsTournaments, FootballGames as ModelsFootballGames, GroupStage as ModelsGroupStage, ConfrontationsGroupStage as ModelsConfrontationsGroupStage
from app.tournaments.service import Tournaments_, FootballGames_, Confrontations_
from app.tournaments.utils import code_generator_tournaments
from app.tournaments.constants import Players
from app.users.models import PlaysUsers as ModelsPlaysUsers
from app.users.service import AppUsers_
from app.notifications.service import NotificacionesAdmin_
from app.database import get_db, CRUD
from app.security import valid_access_token, create_token
from app.admin import exception, utils
from app.admin.constants import RESOURCES, ErrorAdmin
from app.config import USERNAME, PASSWORD, TOKEN_SCONDS_EXP
import os

FILEDIR = os.getcwd() + "/app/admin/archivos/"

router = APIRouter(prefix="/admin", tags=["admin"])
templates = Jinja2Templates(directory="app/admin/templates")


@router.post("/login", response_class=HTMLResponse)
def get_login(request: Request, username: str = Form(...), password: str = Form(...)):
    if not (username == USERNAME and password == PASSWORD):
        return templates.TemplateResponse("login.html",status_code=HTTP_401_UNAUTHORIZED, context = {"request": request, "error":ErrorAdmin.LOGIN})
    token = create_token({"username":username})
    return RedirectResponse("/admin/tournaments/list/1", status_code=HTTP_302_FOUND, headers={"set-cookie" : f"access_token={token}; Max-Age={TOKEN_SCONDS_EXP}"})  

@router.post("/tournaments", response_class=HTMLResponse)
async def create_tournaments(request: Request,
            name: str = Form(...),
            logo: str = Form(...),
            start_date: str = Form(...),
            tournament_rules: str = Form(...),
            level: str = Form(...),
            db: Session = Depends(get_db)):       
    obj = SchemasTournaments(               
        name=name,
        logo=logo,
        start_date=start_date,
        tournament_rules=tournament_rules ,
        level=level                                                                                    
    )
    id, codigo = Tournaments_.create(obj, db)
    
    FootballGames_.create_groups_stage(id, codigo, start_date, db)
    FootballGames_.create_keys_stage(id, codigo, start_date, "OC", db)
    FootballGames_.create_keys_stage(id, codigo, start_date, "CU", db)
    FootballGames_.create_keys_stage(id, codigo, start_date, "SF", db)
    FootballGames_.create_keys_stage(id, codigo, start_date, "FI", db)

    numb_fooballgames_api = Competitions_.assignment_api(id, db)
    # Eliminar cuando se pase a produccion.
    numb_fooballgames_random = Competitions_.assignment_random(id, db)

    NotificacionesAdmin_.send_whatsapp_create_tournament(name, numb_fooballgames_api, numb_fooballgames_random)
    return templates.TemplateResponse("create_tournaments.html", {"request": request ,"resources":RESOURCES})

@router.post("/footballgames", response_class=HTMLResponse)
async def create_footballgames(request: Request,
            codigo: str = Form(...),
            tournament_id: int = Form(...),
            tournament_stage: str = Form(...),
            date: str = Form(...),
            hour: str = Form(...),
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
        hour=hour,
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
            hour: str = Form(...),
            home_team: str = Form(...),
            away_team: str = Form(...),
            home_score: str = Form(None),
            away_score: str = Form(None),
            db: Session = Depends(get_db)):
    update_footballgame_in = SchemasUpdateFootballGames(
        hour=hour,
        home_team=home_team,
        away_team=away_team,
        home_score=home_score,
        away_score=away_score
    )
    FootballGames_.update(int(footballgame_id), update_footballgame_in, db)
    footballgame = db.query(ModelsFootballGames).filter(ModelsFootballGames.id == footballgame_id).first()
    
    # Activa los flujos de cambios de estados en el torneo.
    FootballGames_.update_stage(footballgame, home_score, away_score, db)
    
    list_all = FootballGames_.list_search_codigo(db, "", "")
    contex =  utils.get_context_view_pagination(request, "footballgames", 1, list_all)
    return templates.TemplateResponse("table_footballgames.html",contex)

@router.post("/tournaments/{tournament_id}", response_class=HTMLResponse)
async def update_tournaments(request: Request,
            tournament_id: str,
            name: str = Form(...),
            logo: str = Form(...),
            activo: bool = Form(None),
            tournament_rules: str = Form(...),
            db: Session = Depends(get_db)):
    update_tournament_in = SchemasUpdateTourmaments(
        name=name,
        logo=logo,
        is_active=activo,
        tournament_rules=tournament_rules
    )
    Tournaments_.update(int(tournament_id), update_tournament_in, db)
    list_all = Tournaments_.list_search_codigo(db, "")
    contex =  utils.get_context_view_pagination(request, "tournaments", 1, list_all)
    return templates.TemplateResponse("table_tournaments.html",contex)


#------------------------------------------------------------------------------------------------

@router.get("/login", response_class=HTMLResponse)
def view_login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.get("/{table_name}/list/{page_number}", response_class=HTMLResponse)
def view_table(
        request: Request ,
        table_name: str,
        page_number :int,
        codigo: str = '',
        date: str = '',
        email: str = '',
        access_token: Optional[str] = Cookie(None),
        db: Session = Depends(get_db)):
    valid_access_token(access_token)
    list_all = []
    if table_name in 'tournaments':
        list_all = Tournaments_.list_search_codigo(db, codigo)
    elif table_name in 'footballgames':
        list_all = FootballGames_.list_search_codigo(db, codigo, date)
    elif table_name in 'appusers':
        list_all = AppUsers_.list_search_email(db, email)
    else:
        raise exception.table_does_not_exist
    contex = utils.get_context_view_pagination(request, table_name, page_number, list_all)
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

@router.get("/tournaments/update/{pk}", response_class=HTMLResponse)
def view_update_record_in_table(request: Request, pk: str, access_token: Optional[str] = Cookie(None), db: Session = Depends(get_db)):
    valid_access_token(access_token)
    tournament = db.query(ModelsTournaments).filter(ModelsTournaments.id == pk).first()
    contex = {"request": request,"resources":RESOURCES, "pk": pk ,"tournament":tournament}
    return templates.TemplateResponse(f"update_tournaments.html", contex)

@router.get("/tournaments/delete/{pk}", response_class=HTMLResponse)
def tournament_delete(request: Request, pk: str, access_token: Optional[str] = Cookie(None), db: Session = Depends(get_db)):
    valid_access_token(access_token)
    tournament = db.query(ModelsTournaments).filter(ModelsTournaments.id == pk).first()
    Tournaments_.delete(tournament, db)
    list_all = Tournaments_.list_search_codigo(db, "")
    contex =  utils.get_context_view_pagination(request, "tournaments", 1, list_all)
    return templates.TemplateResponse("table_tournaments.html",contex)

@router.get("/tournaments/enrollment/{pk}", response_class=HTMLResponse)
def tournament_enrollment(request: Request, pk: str, access_token: Optional[str] = Cookie(None), db: Session = Depends(get_db)):
    valid_access_token(access_token)
    Tournaments_.enrollment_all(db, pk)
    list_all = Tournaments_.list_search_codigo(db, "")
    contex =  utils.get_context_view_pagination(request, "tournaments", 1, list_all)
    return templates.TemplateResponse("table_tournaments.html",contex)