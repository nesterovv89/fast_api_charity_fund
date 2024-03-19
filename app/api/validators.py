from fastapi import HTTPException, status
from pydantic import PositiveInt
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.charity_project import charity_project_crud
from app.models import CharityProject


async def check_name_duplicate(
    project_name: str, session: AsyncSession
) -> None:
    project_id = await charity_project_crud.get_project_id_by_name(
        project_name, session
    )
    if project_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Проект с таким именем уже существует',
        )


async def check_charity_project_exists(
    project_id: int, session: AsyncSession
) -> CharityProject:
    charity_project = await charity_project_crud.get(project_id, session)
    if charity_project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='Проект не найден'
        )
    return charity_project


async def check_project_was_closed(
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