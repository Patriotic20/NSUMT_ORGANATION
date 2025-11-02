from sqlalchemy.ext.asyncio import AsyncSession
from .schemas import GroupTeacherCreate
from .schemas import GroupTeacherUpdate

from fastapi import HTTPException, status

from sqlalchemy import func
from sqlalchemy import select
from sqlalchemy.orm import selectinload


from core.utils.service import BasicService
from core.models.group import Group
from core.models.group_teacher import GroupTeacher
from core.schemas.get_all import GetAll

class GroupTeacherService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.service = BasicService(session=self.session)
    
    async def create(self, create_data: GroupTeacherCreate):
        return await self.service.create(
            model = GroupTeacher, 
            create_data = create_data, 
            filters = [
                GroupTeacher.group_id == create_data.group_id,
                GroupTeacher.teacher_id == create_data.teacher_id,
                ])
    
    async def get_by_id(self, id: int):
        stmt = (
            select(GroupTeacher)
            .where(GroupTeacher.id == id)
            .options(
                selectinload(GroupTeacher.group),
                selectinload(GroupTeacher.teacher)
            )
        )

        result = await self.session.execute(stmt)
        group_teacher = result.scalar_one_or_none()

        if not group_teacher:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No association found between group and teacher.",
            )

        return group_teacher
    
    
    async def get_by_teacher_id(self, teacher_id: int):
        stmt = (
            select(GroupTeacher)
            .where(GroupTeacher.teacher_id == teacher_id)
            .options(
                selectinload(GroupTeacher.group)  
            )
        )
        
        result = await self.session.execute(stmt)
        group_teachers = result.scalars().all()
        
        
        if not group_teachers:
            raise HTTPException(
                status_code=404, 
                detail="No groups found for this teacher"
                )

        # Extract groups from the association records
        groups = [gt.group for gt in group_teachers if gt.group is not None]
        return groups

        
        
    
    # async def update(self, id: int, update_data: GroupTeacherUpdate):
    #     return await self.service.update(
    #         model=GroupTeacher,
    #         filters=[GroupTeacher.id == id],
    #         unique_filters = [
    #             GroupTeacher.group_id == update_data.group_id,
    #             GroupTeacher.teacher_id == update_data.teacher_id
    #             ],
    #         update_data = update_data
    #     )
            
    # async def delete(self, id: int):
    #     return await self.service.delete(
    #         model = GroupTeacher,
    #         filters = [
    #             GroupTeacher.id == id 
    #         ]
    #     )
