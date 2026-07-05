from sqlalchemy.orm import Session

def get_db_session():
    """
    Get database session for interacting with the database
    """

    from db.engine import engine

    session = Session(bind=engine)

    try:
        yield session
    finally:
        session.close()

    



