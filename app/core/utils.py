from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.charity_project import charity_project_crud
from app.models import CharityProject


async def get_project_or_404(
    project_id: int, session: AsyncSession, model: CharityProject
) -> CharityProject:
    charity_project = await charity_project_crud.get(project_id, session)
    if charity_project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='Проект не найден'
        )
    charity_project.model = model
    return charity_project
