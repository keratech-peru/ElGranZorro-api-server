from pydantic import BaseModel
from typing import Optional

class Competitions(BaseModel):
    id_competition: int
    name: str
    code: str
    type: str
    emblem: str
