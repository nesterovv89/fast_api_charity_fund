from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Extra, Field, PositiveInt

from app.schemas.base import CharityProjectBase
from app.core import constants as c


class CharityProjectCreate(BaseModel):
    name: str = Field(..., min_length=c.MIN_STR_LENGTH, max_length=c.MAX_STR_LENGTH)
    description: str = Field(..., min_length=c.MIN_STR_LENGTH)
    full_amount: PositiveInt


class CharityProjectUpdate(CharityProjectCreate):
    name: str = Field(None, min_length=c.MIN_STR_LENGTH, max_length=c.MAX_STR_LENGTH)
    description: str = Field(None, min_length=c.MIN_STR_LENGTH)
    full_amount: PositiveInt = Field(None)

    class Config:
        extra = Extra.forbid


class CharityProjectDB(CharityProjectBase):
    id: int
    name: str
    description: str
    invested_amount: int
    fully_invested: bool
    create_date: datetime
    close_date: Optional[datetime]

    class Config:
        orm_mode = True
