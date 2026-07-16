from fastapi import FastAPI
from app.core.config import settings

from app.core.routers import init_routers
from app.core.logging import setup_logging
from app.core.middleware import LoggingMiddleware
from app.core.exceptions import register_exception_handlers

# Set Up logging
setup_logging()

app = FastAPI()

# Register exception handlers
register_exception_handlers(app)

# Initialize routers
init_routers(app)

# Add logging middleware
app.add_middleware(LoggingMiddleware)


@app.get("/")
async def root():
    
    data = {
        "secret_key": settings.SECRET_KEY,
        "edit_mode": settings.DEBUG
    }
        
    return data





