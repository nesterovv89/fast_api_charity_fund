from datetime import datetime
from typing import Optional

from pydantic import BaseModel, PositiveInt

from app.schemas.base import CharityProjectBase


class DonationCreate(BaseModel):
    comment: Optional[str]
    full_amount: PositiveInt


class DonationDB(DonationCreate):
    id: int
    comment: Optional[str]
    create_date: datetime

    class Config:
        orm_mode = True


class AllDonations(DonationDB, CharityProjectBase):
    user_id: int