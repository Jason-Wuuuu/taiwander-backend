from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse

class DatabaseError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

async def database_exception_handler(request: Request, exc: DatabaseError):
    return JSONResponse(
        status_code=500,
        content={
            "error": "Database Error",
            "detail": exc.message
        }
    )

def register_exception_handlers(app):
    """Register all exception handlers to the FastAPI app"""
    app.add_exception_handler(DatabaseError, database_exception_handler) 