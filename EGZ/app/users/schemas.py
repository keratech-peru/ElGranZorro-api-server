from pydantic import BaseModel
from typing import Optional
from app.users.constants import USER_STATUS_IN_TOURNAMENT

class AppUsers(BaseModel):
    name: str
    lastname: str
    birthdate: Optional[str] = None
    phone: str
    email: str
    dni: str
    imagen: Optional[str] = None
    team_name: Optional[str] = None
    level: int = 1

class UpdateAppUser(BaseModel):
    name: Optional[str] = None
    lastname: Optional[str] = None
    team_name: Optional[str] = None

class PasswordUpdateValidation(BaseModel):
    email: str
    what_team_are_you_fan: str
    from_what_age_are_you_fan: str

class PasswordUpdate(BaseModel):
    email: str
    what_team_are_you_fan: str
    from_what_age_are_you_fan: str
    password: str

class EnrollmentUsers(BaseModel):
    appuser_id: int
    tournaments_id: int
    state: str = USER_STATUS_IN_TOURNAMENT["EE"]

class PlaysUsers(BaseModel):
    appuser_id: Optional[int] = None
    football_games_id: int
    score_local: int
    score_visit: int

class EventLogUser(BaseModel):
    appuser_id: int
    servicio: str

class OtpUsers(BaseModel):
    appuser_id: int
    otp: Optional[str] = None
    is_verification: Optional[bool] = False
    is_user_respond: Optional[bool] = False

class CommissionAgent(BaseModel):
    appuser_id: Optional[int] = None
    start_date: str
    end_date: str
    codigo: Optional[str] = None
    percent: int