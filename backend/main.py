from fastapi import FastAPI

from core.routers import include_routers

app = FastAPI()


include_routers(app)

@app.get("/")
async def root():
    return {"message": "Hello World"}





