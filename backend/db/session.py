from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession



async def get_db_session():
    """
    Get database session for interacting with the database
    """

    from db.engine import engine

    async with AsyncSession(engine) as session:
        yield session

    # with Session(engine) as session:
    #     yield session

