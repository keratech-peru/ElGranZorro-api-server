from fastapi import APIRouter, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import Dict
from sqlalchemy.orm import Session
from app.users.service import AppUsers_
from app.users import schemas
from app.database import get_db
from app.security import valid_header
from app.constants import ApiKey
import csv
import json
import pandas
import shutil

FILEDIR = "app/admin/archivos/"

router = APIRouter(prefix="/admin", tags=["admin"])
templates = Jinja2Templates(directory="app/admin/templates")

@router.get("/file-upload", response_class=HTMLResponse)
def get_basic_form(request: Request):
    return templates.TemplateResponse("form.html", {"request": request})

@router.post('/file-upload', response_class=HTMLResponse)
async def post_basic_form(request: Request, username: str = Form(...), password: str = Form(...), file: UploadFile = File(...)):     
    contents = await file.read()
    with open(f"{FILEDIR}{file.filename}", "wb") as f:
        f.write(contents)
    return templates.TemplateResponse("form.html", {"request": request})
