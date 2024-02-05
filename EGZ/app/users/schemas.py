from pydantic import BaseModel
from typing import Optional

class AppUsers(BaseModel):
    name: str
    lastname: str
    birthdate: str
    phone: str
    email: str
    password: str
    what_team_are_you_fan: str
    from_what_age_are_you_fan: str