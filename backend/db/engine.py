from sqlalchemy import create_engine

from sqlalchemy.ext.asyncio import create_async_engine

DATABASE_URL = "sqlite+aiosqlite:///./test.db"  # Replace with your database URL

# engine = create_engine(
#     DATABASE_URL, 
#     echo=True
# )


engine = create_async_engine(
    DATABASE_URL,
    # echo=True
    echo=False
)




