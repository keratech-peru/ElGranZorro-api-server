from fastapi import APIRouter, Depends, status
from typing import Dict
from sqlalchemy.orm import Session
from app.database import get_db
from app.competitions.models import Competitions
from app.competitions.service import Competitions_

router = APIRouter(prefix="/competitions", tags=["competitions"])

@router.get("/teams", status_code=status.HTTP_200_OK)
def teams(
    db: Session = Depends(get_db)
    ) -> Dict[str, object]:
        #Competitions_.create(db)
        competitions = db.query(Competitions.id, Competitions.id_competition, Competitions.code).all()
        Competitions_.add_teams(competitions, db)
        return {"status":"done"}

@router.get("/competition", status_code=status.HTTP_200_OK)
def teams(
    db: Session = Depends(get_db)
    ) -> Dict[str, object]:
        competitions = db.query(Competitions.id, Competitions.id_competition, Competitions.code).all()
        Competitions_.add_match(competitions, db)
        return {"status":"done"}