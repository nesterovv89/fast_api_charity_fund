from datetime import datetime, timedelta
from typing import Optional

from pydantic import BaseModel, Field, PositiveInt

from app.core import constants as c

FROM_TIME = (
    datetime.now() + timedelta(minutes=10)
).isoformat(timespec='minutes')

TO_TIME = (
    datetime.now() + timedelta(hours=1)
).isoformat(timespec='minutes')


class CharityProjectBase(BaseModel):
    full_amount: PositiveInt
    invested_amount: int = Field(default=c.DEFAULT_AMOUNT)
    fully_invested: bool = Field(default=False)
    create_date: datetime = Field(..., example=FROM_TIME)
    close_date: Optional[datetime] = Field(..., example=TO_TIME)
