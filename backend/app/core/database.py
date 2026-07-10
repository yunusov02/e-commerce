from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from fastapi import Depends
from typing import Annotated
from app.core.config import settings

engine = create_async_engine(settings.DATABASE_URL, echo=True)

Sessionlocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def get_db():
    async with Sessionlocal() as session:
        yield session        
        

SessionDependency = Annotated[AsyncSession, Depends(get_db)]



