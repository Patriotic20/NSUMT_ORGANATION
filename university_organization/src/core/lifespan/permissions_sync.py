from fastapi.routing import APIRoute
from fastapi import FastAPI

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from core.models.permission import Permission
from core.models.user import User
from core.models.role import Role
from core.models.role_permission_association import RolePermission
from core.models.user_role_association import UserRole
from core.config import settings
from auth.service.auth_service import AuthService
from auth.schemas.auth import UserCredentials

def http_to_action(method: str) -> str:
    mapping = {
        "GET": "read",
        "POST": "create",
        "PUT": "update",
        "PATCH": "update",
        "DELETE": "delete",
    }
    
    return mapping.get(method.upper(), "other")


def generate_permissions(app: FastAPI):
    perms = set()
    for route in app.routes:
        if isinstance(route, APIRoute):
            for method in route.methods:
                action = http_to_action(method)
                
                parts = [p for p in route.path.split("/") if p]
                resource = parts[0] if parts else "general"
                perms.add(f"{action}:{resource}")
    return perms


async def sync_permissions(app: FastAPI, session:AsyncSession):
    
    existing = {p.name for p in (await session.execute(select(Permission))).scalars().all()}
    
    generated = generate_permissions(app)
    
    new_perm = [Permission(name = p) for p in generated if p not in existing]
    
    if new_perm:
        session.add_all(new_perm)
        await session.commit()
        
    await seed_roles(session)
        
    
async def seed_roles(session: AsyncSession):
    default_roles = ["admin"]


    existing_roles = {
        r.name: r for r in (await session.execute(select(Role))).scalars().all()
    }

    
    new_roles = [
        Role(name=role) for role in default_roles if role not in existing_roles
    ]
    if new_roles:
        session.add_all(new_roles)
        await session.commit()
        
        existing_roles = {
            r.name: r for r in (await session.execute(select(Role))).scalars().all()
        }

    
    all_perms = (await session.execute(select(Permission))).scalars().all()

    
    admin_role = existing_roles["admin"]

    existing_rp = {
        (rp.role_id, rp.permission_id)
        for rp in (await session.execute(select(RolePermission))).scalars().all()
    }

    new_role_permissions = [
        RolePermission(role_id=admin_role.id, permission_id=perm.id)
        for perm in all_perms
        if (admin_role.id, perm.id) not in existing_rp
    ]

    if new_role_permissions:
        session.add_all(new_role_permissions)
        await session.commit()
        
        
    existing_admin = await session.execute(
        select(User).where(User.username == settings.admin.username)
    )
    existing_admin = existing_admin.scalars().first()
    
    userCredentials = UserCredentials(
        username=settings.admin.username,
        password=settings.admin.password
    )
    

    if not existing_admin:
        admin_user : User = await AuthService(session=session).register(credentials=userCredentials)
    
        
        user_role = UserRole(
            user_id=admin_user.id,
            role_id=admin_role.id
        )
        session.add(user_role)
        await session.commit()
