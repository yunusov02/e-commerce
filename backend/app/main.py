from fastapi import FastAPI
from app.core.config import settings

from app.core.routers import init_routers


app = FastAPI()

init_routers(app)



@app.get("/")
async def root():
    
    data = {
        "database_url": settings.DATABASE_URL,
        "secret_key": settings.SECRET_KEY,
        "edit_mode": settings.DEBUG
    }
        
    return data





