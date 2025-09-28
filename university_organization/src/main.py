from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn


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


origins = [
    "http://organization.nsumt.uz",
    "https://organization.nsumt.uz"
    
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
        reload=True
        )
