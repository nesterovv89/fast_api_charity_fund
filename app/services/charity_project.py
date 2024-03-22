from datetime import datetime
from typing import Union

from sqlalchemy import select
from fastapi import HTTPException, status
from pydantic import PositiveInt
from accessify import protected
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.charity_project import CharityProjectCreate
from app.models.charity_project import CharityProject
from app.models.donation import Donation
from app.crud.charity_project import charity_project_crud
from app.schemas.charity_project import CharityProjectUpdate, CharityProjectDB


class CharityFundService:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_project(self, charity_project: CharityProjectCreate):
        await self.check_name_duplicate(charity_project.name)
        new_project = await charity_project_crud.create(charity_project, self.session)
        new_project = await self.donation_process(new_project)
        return new_project

    async def delete_charity_project(self, charity_project: CharityProject):
        await self.check_project_was_invested(charity_project)
        charity_project = await charity_project_crud.remove(
            charity_project, self.session
        )
        return charity_project

    async def update_charity_project(
            self, charity_project: CharityProjectDB,
            obj_in: CharityProjectUpdate
    ):
        await self.check_name_duplicate(obj_in.name)
        await self.check_project_was_closed(charity_project)
        await self.check_correct_full_amount_for_update(charity_project, obj_in.full_amount)

        updated_charity_project = await charity_project_crud.update(
            charity_project, obj_in, self.session
        )
        return updated_charity_project

    @protected
    def mark_project_as_fully_invested_and_close(self, db_obj):
        db_obj.fully_invested = True
        db_obj.close_date = datetime.now()

    async def donation_process(
        self, obj_in: Union[CharityProject, Donation]
    ):
        db_obj = CharityProject if isinstance(obj_in, Donation) else Donation

        db_objs = await self.session.execute(
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

            self.session.add(db_obj)

        self.session.add(obj_in)
        await self.session.commit()
        await self.session.refresh(obj_in)
        return obj_in

    async def check_name_duplicate(
        self, project_name: str
    ) -> None:
        project_id = await charity_project_crud.get_project_id_by_name(
            project_name, self.session
        )
        if project_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Проект с таким именем уже существует',
            )

    async def check_project_was_closed(
        self,
        charity_project: CharityProject
    ):
        if charity_project.close_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Проект уже закрыт'
            )

    async def check_project_was_invested(
        self,
        charity_project: CharityProject
    ):
        if charity_project.invested_amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Проект, в который проинвестировали, нельзя удалить')

    async def check_correct_full_amount_for_update(
        self,
        charity_project: CharityProject,
        full_amount_to_update: PositiveInt,
    ):
        if charity_project.invested_amount and charity_project.invested_amount > full_amount_to_update:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail='Нельзя установить сумму меньше прежней',
            )
