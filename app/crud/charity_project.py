from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.charity_project import CharityProject


class CRUDCharityProject(CRUDBase):
    async def get_project_id_by_name(
        self,
        project_name: str,
        session: AsyncSession,
    ) -> Optional[int]:
        db_project_id = await session.execute(
            select(CharityProject.id).where(
                CharityProject.name == project_name
            )
        )

        db_project_id = db_project_id.scalars().first()
        return db_project_id

    async def get_charity_project_close_date(
        self,
        project_id: int,
        session: AsyncSession
    ):
        project_close_date = await session.execute(
            select(CharityProject.close_date).where(
                CharityProject.id == project_id
            )
        )
        return project_close_date.scalars().first()

    async def get_charity_project_invested_amount(
        self,
        project_id: int,
        session: AsyncSession
    ):
        project_invested_amount = await session.execute(
            select(CharityProject.invested_amount).where(
                CharityProject.id == project_id
            )
        )
        return project_invested_amount.scalars().first()


charity_project_crud = CRUDCharityProject(CharityProject)
