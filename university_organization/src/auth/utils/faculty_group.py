from sqlalchemy.ext.asyncio import AsyncSession
from core.utils.normalize_type_name import normalize_type_name
from core.utils.service import BasicService
from core.models.faculty import Faculty
from core.models.group import Group
from faculty.schemas import FacultyCreate
from group.schemas import GroupCreate


async def faculty_create_check(session: AsyncSession, faculty_name: str) -> Faculty:
    crud = BasicService(session=session)

    faculty_name = normalize_type_name(value=faculty_name)
    faculty_create = FacultyCreate(name=faculty_name)

    faculty_data = await crud.create(
        model=Faculty,
        create_data=faculty_create,
        filters=[Faculty.name == faculty_name]
    )

    return faculty_data


async def group_create_check(session: AsyncSession, group_name: str, faculty_name: str) -> Group:

    faculty_data: Faculty = await faculty_create_check(session=session, faculty_name=faculty_name)

    crud = BasicService(session=session)

    group_name = normalize_type_name(value=group_name)
    group_create = GroupCreate(
        faculty_id=faculty_data.id,
        name=group_name
    )


    group_data = await crud.create(
        model=Group,
        create_data=group_create,
        filters=[Group.name == group_name, Group.faculty_id == faculty_data.id]
    )

    return group_data
