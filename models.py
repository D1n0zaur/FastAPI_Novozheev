from pydantic import BaseModel
from typing import Optional

class Movie(BaseModel):
    name: str
    id: int
    cost: int
    director: str
    oscar: Optional[bool] = False
    description: Optional[str] = None
    photo: Optional[str] = None