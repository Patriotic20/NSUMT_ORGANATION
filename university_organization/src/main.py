from fastapi import FastAPI
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

from router import router as api_router
from core.config import settings
from core.lifespan.lifespan import lifespan





app = FastAPI(
    lifespan=lifespan,
    title="NSMUT Organization",
    version="0.0.1",
    description="NSMUT Organization — bu universitet ichidagi tashkiliy tuzilmani boshqarishga mo‘ljallangan zamonaviy dasturiy ta'minotdir. Ushbu loyiha orqali universitetning quyidagi asosiy bo'limlarini boshqarish va ularga oid ma'lumotlarni avtomatlashtirilgan tarzda yuritish imkoniyati yaratiladi:",
)

app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://test.api.nsumt.uz"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    uvicorn.run(                    
        "main:app", 
        # host=settings.server.host, 
        port=settings.server.port, 
        reload=True
        )
