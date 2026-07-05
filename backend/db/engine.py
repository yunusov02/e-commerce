from sqlalchemy import create_engine



DATABASE_URL = "sqlite:///./test.db"  # Replace with your database URL

engine = create_engine(
    DATABASE_URL, 
    echo=True
)

