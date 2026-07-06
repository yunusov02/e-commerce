from fastapi import FastAPI

from core.routers import include_routers
from core.logging import configure_structlog


configure_structlog()
app = FastAPI()


include_routers(app)

@app.get("/")
async def root():
    return {"message": "Hello World"}





