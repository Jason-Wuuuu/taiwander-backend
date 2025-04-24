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
        # Optional: remove _id if not needed
        # del transformed["_id"]

    # Transform fields with name casing issues

    # 1. Simple field name mappings (PascalCase to camelCase)
    pascal_to_camel = {
        "Telephones": "telephones",
        "Images": "images",
        "Organizations": "organizations",
        "ServiceTimeInfo": "serviceTimeInfo",
        "TrafficInfo": "trafficInfo",
        "ParkingInfo": "parkingInfo",
        "Facilities": "facilities",
        "ServiceStatus": "serviceStatus",
        "FeeInfo": "feeInfo",
        "PaymentMethods": "paymentMethods",
        "LocatedCities": "locatedCities",
        "WebsiteURL": "websiteUrl",
        "ReservationURLs": "reservationUrls",
        "MapURLs": "mapUrls",
        "SameAsURLs": "sameAsUrls",
        "SocialMediaURLs": "socialMediaUrls",
        "VisitDuration": "visitDuration",
        "AssetsClass": "assetsClass",
        "SubAttractions": "subAttractions",
        "PartOfAttraction": "partOfAttraction",
        "Remarks": "remarks",
        "UpdateTime": "updateTime"
    }

    # Apply field name mappings
    for pascal_key, camel_key in pascal_to_camel.items():
        if pascal_key in transformed:
            transformed[camel_key] = transformed.pop(pascal_key)

    # 2. Transform nested objects in arrays

    # Handle telephones
    if "telephones" in transformed:
        transformed["telephones"] = [{"tel": t["Tel"]}
                                     for t in transformed["telephones"] if "Tel" in t]

    # Handle images
    if "images" in transformed:
        transformed_images = []
        for img in transformed["images"]:
            transformed_img = {
                "name": img.get("Name", ""),
                "description": img.get("Description"),
                "url": img.get("URL"),
                "width": img.get("Width"),
                "height": img.get("Height"),
                "keywords": img.get("Keywords", [])
            }
            transformed_images.append(transformed_img)
        transformed["images"] = transformed_images

    # Handle social media URLs
    if "socialMediaUrls" in transformed:
        transformed_social = []
        for sm in transformed["socialMediaUrls"]:
            transformed_sm = {
                "name": sm.get("Name", ""),
                "description": sm.get("Description"),
                "url": sm.get("URL"),
                "keywords": sm.get("Keywords", []),
                "tags": sm.get("Tags", [])
            }
            transformed_social.append(transformed_sm)
        transformed["socialMediaUrls"] = transformed_social

    # Handle postal address
    if "postalAddress" in transformed:
        postal_address = transformed["postalAddress"]
        if postal_address and "streetAddress" in postal_address and postal_address["streetAddress"] is None:
            postal_address["streetAddress"] = ""

    # Handle service times
    if "serviceTimes" in transformed:
        transformed_times = []
        for time in transformed["serviceTimes"]:
            transformed_time = {
                "name": time.get("Name", ""),
                "description": time.get("Description"),
                "days": time.get("ServiceDays", []),
                "startTime": time.get("StartTime", "00:00:00"),
                "endTime": time.get("EndTime", "00:00:00"),
                "effectiveDate": time.get("EffectiveDate"),
                "expireDate": time.get("ExpireDate")
            }
            transformed_times.append(transformed_time)
        transformed["serviceTimes"] = transformed_times

    # Handle fees
    if "fees" in transformed:
        transformed_fees = []
        for fee in transformed["fees"]:
            transformed_fee = {
                "name": fee.get("Name", ""),
                "price": fee.get("Price", 0),
                "description": fee.get("Description"),
                "url": fee.get("URL")
            }
            transformed_fees.append(transformed_fee)
        transformed["fees"] = transformed_fees

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
