from app.schemas.charity_project import CharityProjectCreate
from app.crud.charity_project import charity_project_crud
from app.api.validators import check_name_duplicate, check_charity_project_by_id, check_project_was_invested
from app.services.donations import donation_process


async def service_create_project(charity_project: CharityProjectCreate, session):
    await check_name_duplicate(charity_project.name, session)
    new_project = await charity_project_crud.create(charity_project, session)
    new_project = await donation_process(new_project, session)
    return new_project


async def service_delete_charity_project(project_id: int, session):
    charity_project = await check_charity_project_by_id(project_id, session)
    await check_project_was_invested(project_id, session)
    charity_project = await charity_project_crud.remove(
        charity_project, session
    )
    return charity_project