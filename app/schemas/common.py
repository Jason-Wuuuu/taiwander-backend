from typing import Generic, List, Optional, TypeVar, Any, Dict
from pydantic import BaseModel, Field
from pydantic.generics import GenericModel

T = TypeVar('T')

class ErrorResponse(BaseModel):
    """Error response model."""
    error: str = Field(..., description="Error type")
    detail: str = Field(..., description="Error details")

class StatusResponse(BaseModel):
    """Status response model."""
    status: str = Field(..., description="Operation status")
    message: Optional[str] = Field(None, description="Status message")

class PaginatedResponse(GenericModel, Generic[T]):
    """Generic paginated response model."""
    total: int = Field(..., description="Total number of items")
    page: int = Field(1, description="Current page number")
    limit: int = Field(..., description="Items per page")
    data: List[T] = Field(..., description="List of items") 