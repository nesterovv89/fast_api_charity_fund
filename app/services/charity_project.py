from datetime import datetime
from typing import Union

from sqlalchemy import select
from fastapi import HTTPException, status
from pydantic import PositiveInt
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.charity_project import CharityProjectCreate
from app.models.charity_project import CharityProject
from app.models.donation import Donation
from app.crud.charity_project import charity_project_crud
from app.schemas.charity_project import CharityProjectUpdate, CharityProjectDB


class CharityFundService:

    def __init__(self):
        pass

    async def create_project(self, charity_project: CharityProjectCreate, session):
        await self.check_name_duplicate(charity_project.name, session)
        new_project = await charity_project_crud.create(charity_project, session)
        new_project = await self.donation_process(new_project, session)
        return new_project

    async def delete_charity_project(self, project_id: int, session):
        charity_project = await charity_project_crud.get(project_id, session)
        await self.check_project_was_invested(project_id, session)
        charity_project = await charity_project_crud.remove(
            charity_project, session
        )
        return charity_project

    async def update_charity_project(
            self, charity_project: CharityProjectDB,
            obj_in: CharityProjectUpdate, session: AsyncSession
    ):
        await self.check_name_duplicate(obj_in.name, session)
        await self.check_project_was_closed(charity_project.id, session)
        await self.check_correct_full_amount_for_update(charity_project.id, session, obj_in.full_amount)

        updated_charity_project = await charity_project_crud.update(
            charity_project, obj_in, session
        )
        return updated_charity_project

    def mark_project_as_fully_invested_and_close(self, db_obj):
        db_obj.fully_invested = True
        db_obj.close_date = datetime.now()

    async def donation_process(
        self, obj_in: Union[CharityProject, Donation], session: AsyncSession
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
                self.mark_project_as_fully_invested_and_close(obj_in)

                db_obj.invested_amount += obj_in.full_amount

                if db_obj.invested_amount == db_obj.full_amount:
                    self.mark_project_as_fully_invested_and_close(db_obj)

            session.add(db_obj)

        session.add(obj_in)
        await session.commit()
        await session.refresh(obj_in)
        return obj_in

    async def check_name_duplicate(
        self, project_name: str, session: AsyncSession
    ) -> None:
        project_id = await charity_project_crud.get_project_id_by_name(
            project_name, session
        )
        if project_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Проект с таким именем уже существует',
            )

    async def check_project_was_closed(
        self,
        project_id: int,
        session: AsyncSession
    ):
        project_close_date = await (
            charity_project_crud.get_charity_project_close_date(
                project_id, session
            )
        )
        if project_close_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Проект уже закрыт'
            )

    async def check_project_was_invested(
        self,
        project_id: int,
        session: AsyncSession
    ):
        invested_project = await (
            charity_project_crud.get_charity_project_invested_amount(
                project_id, session
            )
        )
        if invested_project:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Проект, в который проинвестировали, нельзя удалить')

    async def check_correct_full_amount_for_update(
        self,
        project_id: int,
        session: AsyncSession,
        full_amount_to_update: PositiveInt,
    ):
        db_project_invested_amount = await (
            charity_project_crud.get_charity_project_invested_amount(
                project_id, session
            )
        )
        if db_project_invested_amount and db_project_invested_amount > full_amount_to_update:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail='Нельзя установить сумму меньше прежней',
            )
