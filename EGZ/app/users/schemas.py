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
    imagen: Optional[str] = None
    username: Optional[str] = None
    team_name: Optional[str] = None
    team_logo: Optional[str] = None

class UpdateAppUser(BaseModel):
    name: Optional[str] = None
    lastname: Optional[str] = None
    birthdate: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    imagen: Optional[str] = None
    username: Optional[str] = None
    team_name: Optional[str] = None
    team_logo: Optional[str] = None


class AppUsersLogin(BaseModel):
    email: str
    password: str
