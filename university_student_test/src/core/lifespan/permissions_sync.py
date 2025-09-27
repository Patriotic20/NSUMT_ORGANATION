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

        generated = generate_permissions(app)

        resp = await client.post(
            settings.organization_urls.permissions,
            json=generated,
        )

        return resp.status_code, resp.json()
