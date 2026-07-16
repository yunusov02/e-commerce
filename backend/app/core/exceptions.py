from fastapi import status
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi import FastAPI

class NotFoundError(HTTPException):
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class ConflictError(HTTPException):
    def __init__(self, detail: str = "Resource already exists"):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)
        


def validation_exception_handler(
    request: Request, 
    exc: RequestValidationError
) -> JSONResponse:
    
    errors = [
        {"field": err["loc"][-1], "message": err["msg"]}
        for err in exc.errors()
    ]

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content={"detail": exc.errors()},
    )
    
    
    
    
    

def register_exception_handlers(app: FastAPI):
    
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    
    
    