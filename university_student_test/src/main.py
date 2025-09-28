from fastapi import FastAPI
from core.config import settings
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from router import router as api_router
from core.lifespan.lifespan import lifespan
import uvicorn

app = FastAPI(
    lifespan=lifespan,
    version="0.0.1",
    title="NSMUT Test",
    description="NSMUT Test - Talabalar uchun onlayn test tizimi. Ushbu platforma orqali talabalar turli fanlardan test topshirib, o‘z bilimlarini sinab ko‘rishlari mumkin."
    )

app.mount("/uploads" , StaticFiles(directory="uploads") , name="uploads")

app.include_router(api_router)


origins = [
    "http://localhost:5174",
    "http://organization.nsumt.uz",
    "https://organization.nsumt.uz"
    "http://test.nsumt.uz"
    "https://test.nsumt.uz",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.server.host,
        port=settings.server.port,
        reload=settings.server.is_reload
        )
