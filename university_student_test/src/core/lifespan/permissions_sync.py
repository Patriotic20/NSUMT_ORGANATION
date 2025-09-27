from fastapi.routing import APIRoute
from fastapi import FastAPI

from core.config import settings
from core.config import LOG_DEFAULT_FORMAT

import httpx
import logging

logging.basicConfig(
    level=logging.INFO,
    format=LOG_DEFAULT_FORMAT
)

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

        try:
            resp = await client.post(
                settings.organization_urls.permissions,
                json=generated,
                timeout=10.0,  
                headers={"Accept": "application/json"},
            )
        except httpx.RequestError as e:
            logging.error(f"❌ Failed to reach permissions service: {e}")
            return None, None

        try:
            data = resp.json()
        except ValueError:
            logging.error(
                f"❌ Invalid JSON from permissions service "
                f"(status {resp.status_code}): {resp.text}"
            )
            data = None

        return resp.status_code, data
