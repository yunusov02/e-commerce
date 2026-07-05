from typing import Annotated
from fastapi import Depends
from sqlalchemy.orm import Session
from db.session import get_db_session




#  Session Dependency
SessionDependency = Annotated[Session, Depends(get_db_session)]

