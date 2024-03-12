from app.tournaments.models import Tournaments
from app.tournaments.constants import Players
from app.database import get_db
from fastapi import Depends
from sqlalchemy.orm import Session


def code_generator_tournaments(db: Session = Depends(get_db)):
    filtro = db.query(Tournaments.id).order_by(Tournaments.id.desc()).first()[0] if db.query(Tournaments).all() else 0
    id_next = filtro + 1
    if id_next < 10:
        id = "00" + str(id_next)
    elif id_next >= 10 and id_next < 100:
        id = "0"+str(id_next)
    else:
        id = str(id_next)
    return "T" + Players.MAXIMO + id, id_next

