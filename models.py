from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta

class Movie(BaseModel):
    name: str
    id: int
    cost: float  # Изменено с int на float
    director: str
    oscar: Optional[bool] = False
    description: Optional[str] = None
    photo: Optional[str] = None

class UserLogin(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    message: str
    username: str
    session_created: datetime
    session_expires: datetime

class UserProfileResponse(BaseModel):
    username: str
    login_time: datetime
    session_start: datetime
    last_activity: datetime
    session_duration: timedelta
    time_until_expiry: timedelta
    movies_count: int

class UserDataResponse(BaseModel):
    user: dict
    time_info: dict
    movies: dict
    message: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    expires_at: Optional[datetime] = None