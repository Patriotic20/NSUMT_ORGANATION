from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from sqlalchemy import select

from .security import hash_password
from auth.schemas.auth import UserRoleCreate

from core.utils.service import BasicService
from core.models import User, UserRole
from core.models.role import Role

from auth.schemas.auth import UserCredentials


async def student_register(session: AsyncSession, credentials: UserCredentials): 
    try:
        crud = BasicService(session=session)

    
        stmt = select(Role).where(Role.name == "student")
        result = await session.execute(stmt)
        user_role = result.scalar_one_or_none()

        if not user_role:
            user_role = Role(name="student")
            session.add(user_role)
            await session.flush()  
            
            
        
        
        stmt = select(User).where(User.username == credentials.username)
        result = await session.execute(stmt)
        existing_user = result.scalar_one_or_none()

        hashed_password = hash_password(credentials.password)

        if existing_user:
            # Update password if user already exists
            user_data: User = await crud.update(
                model=User,
                filters=[User.id == existing_user.id],
                update_data={"password": hashed_password},
            )
        else:
            # Create a new user
            user_data: User = await crud.create(
                model=User,
                create_data={
                    "username": credentials.username,
                    "password": hashed_password,
                },
            )

     
        await crud.create(
            model=UserRole,
            create_data=UserRoleCreate(role_id=user_role.id, user_id=user_data.id),
        )

        await session.commit()
        return user_data  

    except Exception:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error registering user",
        )
