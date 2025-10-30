from fastapi import FastAPI
from core.config import settings
from fastapi.staticfiles import StaticFiles
from pathlib import Path


from router import router as api_router
from core.lifespan.lifespan import lifespan
import uvicorn

app = FastAPI(
    lifespan=lifespan,
    version="0.0.1",
    title="NSMUT Test",
    description="NSMUT Test - Talabalar uchun onlayn test tizimi. Ushbu platforma orqali talabalar turli fanlardan test topshirib, o‘z bilimlarini sinab ko‘rishlari mumkin."
    )

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

app.include_router(api_router)


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.server.host,
        port=settings.server.port,
        reload=settings.server.is_reload
        )
