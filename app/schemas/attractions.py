from typing import List, Optional
from pydantic import BaseModel, Field

from ..models.attractions import Attraction


class AttractionFilter(BaseModel):
    """Filter parameters for attractions."""
    classes: Optional[List[int]] = Field(
        None, description="Attraction classes to filter by")
    free: Optional[bool] = Field(None, description="Filter by free admission")
    region: Optional[str] = Field(None, description="Filter by region/city")


class PaginationParams(BaseModel):
    """Pagination parameters."""
    page: int = Field(1, ge=1, description="Page number (1-indexed)")
    limit: int = Field(
        20, ge=1, le=100, description="Number of items per page")


class AttractionListResponse(BaseModel):
    """Paginated list of attractions."""
    total: int = Field(..., description="Total number of attractions")
    page: int = Field(..., description="Current page number")
    limit: int = Field(..., description="Number of items per page")
    data: List[Attraction] = Field(..., description="List of attractions")


class AttractionResponse(BaseModel):
    """Single attraction response."""
    data: Attraction = Field(..., description="Attraction details")


class AttractionSearchParams(PaginationParams):
    """Parameters for attraction search."""
    q: str = Field(..., min_length=1, description="Search query")


class AttractionClassListResponse(BaseModel):
    """List of attraction classes."""
    data: List[dict] = Field(..., description="List of attraction classes")
