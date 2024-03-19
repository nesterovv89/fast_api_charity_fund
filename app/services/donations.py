from datetime import datetime
from typing import Union

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.charity_project import CharityProject
from app.models.donation import Donation


def value_setting(db_obj):
    db_obj.fully_invested = True
    db_obj.close_date = datetime.now()


async def donation_process(
    obj_in: Union[CharityProject, Donation], session: AsyncSession
):
    db_obj = CharityProject if isinstance(obj_in, Donation) else Donation

    db_objs = await session.execute(
        select(db_obj)
        .where(db_obj.fully_invested == 0)
        .order_by(db_obj.create_date.desc(), db_obj.id.desc())
    )
    db_objs = db_objs.scalars().all()

    while db_objs and obj_in.full_amount > obj_in.invested_amount:
        db_obj = db_objs.pop()

        remainder = db_obj.full_amount - db_obj.invested_amount

        if obj_in.full_amount > remainder:
            obj_in.invested_amount += remainder
        else:
            obj_in.invested_amount = obj_in.full_amount
            value_setting(obj_in)

            db_obj.invested_amount += obj_in.full_amount

            if db_obj.invested_amount == db_obj.full_amount:
                value_setting(db_obj)

        session.add(db_obj)

    session.add(obj_in)
    await session.commit()
    await session.refresh(obj_in)
    return obj_in