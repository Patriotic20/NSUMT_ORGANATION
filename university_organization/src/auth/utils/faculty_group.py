from sqlalchemy.ext.asyncio import AsyncSession
from core.utils.normalize_type_name import normalize_type_name
from core.utils.service import BasicService
from core.models.faculty import Faculty
from core.models.group import Group
from faculty.schemas import FacultyCreate
from group.schemas import GroupCreate
from sqlalchemy import select


async def faculty_create_check(session: AsyncSession, faculty_name: str) -> Faculty:
    crud = BasicService(session=session)

    faculty_name = normalize_type_name(value=faculty_name)
    faculty_create = FacultyCreate(name=faculty_name)
    
    stmt = select(Faculty).where(Faculty.name == faculty_create.name)
    result = await session.execute(stmt)
    existing_data = result.scalars().first()
    
    if not existing_data:
        new_faculty = Faculty(name=faculty_create.name)
        session.add(new_faculty)
        await session.commit()
        await session.refresh(new_faculty)
        return new_faculty
    
    return existing_data


async def group_create_check(session: AsyncSession, group_name: str, faculty_name: str) -> Group:

    faculty_data: Faculty = await faculty_create_check(session=session, faculty_name=faculty_name)

    crud = BasicService(session=session)

    group_name = normalize_type_name(value=group_name)
    group_create = GroupCreate(
        faculty_id=faculty_data.id,
        name=group_name
    )
    
    stmt = select(Group).where(Group.name == group_create.name)
    result = await session.execute(stmt)
    existing_data = result.scalars().first()
    
    if not existing_data:
        new_group = Group(name = group_create.name, faculty_id = group_create.faculty_id)
        session.add(new_group)
        await session.commit()
        await session.refresh(new_group)
        return new_group
    
    return existing_data
