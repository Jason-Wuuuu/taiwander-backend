from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, Path
from motor.motor_asyncio import AsyncIOMotorDatabase

from ...database.mongodb import MongoDB
from ...database.repositories.attractions import AttractionsRepository
from ...schemas.attractions import (
    AttractionListResponse,
    AttractionFilter,
    PaginationParams,
    AttractionSearchParams,
    AttractionResponse
)
from ...models.attractions import Attraction

router = APIRouter(
    prefix="/attractions",
    tags=["attractions"]
)


async def get_attractions_repo() -> AttractionsRepository:
    """Dependency to get attractions repository."""
    return AttractionsRepository(MongoDB.db)


def transform_attraction_document(attraction: Dict[str, Any]) -> Dict[str, Any]:
    """Transform MongoDB attraction document to match Pydantic model."""
    if not attraction:
        return attraction

    # Create a copy to avoid modifying the original
    transformed = dict(attraction)

    # Set id field from _id for API responses
    if "_id" in transformed:
        transformed["id"] = transformed["_id"]

    return transformed


@router.get("/", response_model=AttractionListResponse)
async def get_attractions(
    pagination: PaginationParams = Depends(),
    repo: AttractionsRepository = Depends(get_attractions_repo)
):
    """Get all attractions with pagination."""
    skip = (pagination.page - 1) * pagination.limit

    attractions = await repo.find_many(
        query={},
        skip=skip,
        limit=pagination.limit,
        # sort=[("name", 1)]
    )

    # Transform attractions to match Pydantic model
    transformed_attractions = [
        transform_attraction_document(a) for a in attractions]

    total = await repo.count({})

    return {
        "total": total,
        "page": pagination.page,
        "limit": pagination.limit,
        "data": transformed_attractions
    }


@router.get("/search", response_model=AttractionListResponse)
async def search_attractions(
    search_params: AttractionSearchParams = Depends(),
    repo: AttractionsRepository = Depends(get_attractions_repo)
):
    """Search attractions by query."""
    skip = (search_params.page - 1) * search_params.limit

    attractions = await repo.search(
        query=search_params.q,
        skip=skip,
        limit=search_params.limit
    )

    # Transform attractions to match Pydantic model
    transformed_attractions = [
        transform_attraction_document(a) for a in attractions]

    total = await repo.count_search_results(search_params.q)

    return {
        "total": total,
        "page": search_params.page,
        "limit": search_params.limit,
        "data": transformed_attractions
    }


@router.get("/filter", response_model=AttractionListResponse)
async def filter_attractions(
    classes: Optional[List[int]] = Query(
        None, description="Attraction classes"),
    free: Optional[bool] = Query(None, description="Free admission"),
    region: Optional[str] = Query(None, description="Region/city name"),
    pagination: PaginationParams = Depends(),
    repo: AttractionsRepository = Depends(get_attractions_repo)
):
    """Get attractions with filters."""
    skip = (pagination.page - 1) * pagination.limit

    attractions = await repo.find_with_filters(
        classes=classes,
        free=free,
        region=region,
        skip=skip,
        limit=pagination.limit
    )

    # Transform attractions to match Pydantic model
    transformed_attractions = [
        transform_attraction_document(a) for a in attractions]

    total = await repo.count_with_filters(
        classes=classes,
        free=free,
        region=region
    )

    return {
        "total": total,
        "page": pagination.page,
        "limit": pagination.limit,
        "data": transformed_attractions
    }


@router.get("/nearby", response_model=AttractionListResponse)
async def nearby_attractions(
    lon: float = Query(..., description="Longitude of the center point"),
    lat: float = Query(..., description="Latitude of the center point"),
    radius: float = Query(
        5.0, description="Radius in kilometers (default: 5)"),
    pagination: PaginationParams = Depends(),
    repo: AttractionsRepository = Depends(get_attractions_repo)
):
    """Get attractions near a specific location within a radius.

    Args:
        lon: Longitude of the center point
        lat: Latitude of the center point  
        radius: Radius in kilometers (default: 5)

    Returns:
        List of attractions within the specified radius
    """
    skip = (pagination.page - 1) * pagination.limit

    attractions = await repo.find_nearby(
        lon=lon,
        lat=lat,
        radius_km=radius,
        skip=skip,
        limit=pagination.limit
    )

    # Transform attractions to match Pydantic model
    transformed_attractions = [
        transform_attraction_document(a) for a in attractions]

    total = await repo.count_nearby(
        lon=lon,
        lat=lat,
        radius_km=radius
    )

    return {
        "total": total,
        "page": pagination.page,
        "limit": pagination.limit,
        "data": transformed_attractions
    }


@router.get("/class/{class_id}", response_model=AttractionListResponse)
async def get_attractions_by_class(
    class_id: int = Path(..., description="Attraction class ID"),
    pagination: PaginationParams = Depends(),
    repo: AttractionsRepository = Depends(get_attractions_repo)
):
    """Get attractions by class ID."""
    skip = (pagination.page - 1) * pagination.limit

    attractions = await repo.find_by_classes(
        class_ids=[class_id],
        skip=skip,
        limit=pagination.limit
    )

    # Transform attractions to match Pydantic model
    transformed_attractions = [
        transform_attraction_document(a) for a in attractions]

    total = await repo.count_by_classes([class_id])

    return {
        "total": total,
        "page": pagination.page,
        "limit": pagination.limit,
        "data": transformed_attractions
    }


@router.get("/{attraction_id}", response_model=AttractionResponse)
async def get_attraction_by_id(
    attraction_id: str = Path(..., description="Attraction ID"),
    repo: AttractionsRepository = Depends(get_attractions_repo)
):
    """Get attraction by ID."""
    attraction = await repo.find_by_attraction_id(attraction_id)

    if not attraction:
        raise HTTPException(status_code=404, detail="Attraction not found")

    # Transform attraction to match Pydantic model
    transformed_attraction = transform_attraction_document(attraction)

    return {"data": transformed_attraction}
