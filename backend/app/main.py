from fastapi import FastAPI
from app.core.config import settings

app = FastAPI()


@app.get("/")
async def root():
    
    data = {
        "database_url": settings.DATABASE_URL,
        "secret_key": settings.SECRET_KEY,
        "edit_mode": settings.DEBUG
    }
        
    return data





