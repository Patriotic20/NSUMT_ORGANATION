from fastapi.routing import APIRoute
from fastapi import FastAPI

from core.config import settings

import httpx


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
                
    return [{"name": p} for p in perms] 


async def sync_permissions(app: FastAPI):
    async with httpx.AsyncClient() as client:

        login_resp = await client.post(
            "http://127.0.0.1:8000/auth/login",
            params={
                "username": settings.admin.username, 
                "password": settings.admin.password,
                },  
        )
        login_data = login_resp.json()
        token = login_data.get("access_token")

        # 2. Generate permissions
        generated = generate_permissions(app)

        resp = await client.post(
            "http://127.0.0.1:8000/permissions/sync",
            json=generated,
            headers={"Authorization": f"Bearer {token}"},
        )

        return resp.status_code, resp.json()
