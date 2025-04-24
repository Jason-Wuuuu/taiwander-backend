from typing import Dict, List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from .base import BaseRepository
import math


class AttractionsRepository(BaseRepository):
    """Repository for attractions data."""

    def __init__(self, database: AsyncIOMotorDatabase):
        super().__init__(database.attractions)

    async def find_by_attraction_id(self, attraction_id: str) -> Optional[Dict]:
        """Find attraction by its official attraction ID."""
        return await self.find_by_id(attraction_id)

    async def find_by_classes(self, class_ids: List[int], skip: int = 0, limit: int = 20) -> List[Dict]:
        """Find attractions by class IDs."""
        return await self.find_many(
            {"attractionClasses": {"$in": class_ids}},
            skip=skip,
            limit=limit,
            # sort=[("name", 1)]
        )

    async def count_by_classes(self, class_ids: List[int]) -> int:
        """Count attractions by class IDs."""
        return await self.count({"attractionClasses": {"$in": class_ids}})

    async def find_by_region(self, region: str, skip: int = 0, limit: int = 20) -> List[Dict]:
        """Find attractions by region."""
        return await self.find_many(
            {"postalAddress.city": {"$regex": region, "$options": "i"}},
            skip=skip,
            limit=limit,
            # sort=[("name", 1)]
        )

    async def count_by_region(self, region: str) -> int:
        """Count attractions by region."""
        return await self.count({"postalAddress.city": {"$regex": region, "$options": "i"}})

    async def find_free_attractions(self, skip: int = 0, limit: int = 20) -> List[Dict]:
        """Find attractions with free admission."""
        return await self.find_many(
            {"isAccessibleForFree": True},
            skip=skip,
            limit=limit,
            # sort=[("name", 1)]
        )

    async def count_free_attractions(self) -> int:
        """Count attractions with free admission."""
        return await self.count({"isAccessibleForFree": True})

    async def search(self, query: str, skip: int = 0, limit: int = 20) -> List[Dict]:
        """Search attractions by name and description."""
        return await self.find_many(
            {"$text": {"$search": query}},
            skip=skip,
            limit=limit,
            sort=[("score", {"$meta": "textScore"})]
        )

    async def count_search_results(self, query: str) -> int:
        """Count search results."""
        return await self.count({"$text": {"$search": query}})

    async def find_with_filters(
        self,
        classes: Optional[List[int]] = None,
        free: Optional[bool] = None,
        region: Optional[str] = None,
        skip: int = 0,
        limit: int = 20
    ) -> List[Dict]:
        """Find attractions with multiple filters."""
        query = {}

        if classes:
            query["attractionClasses"] = {"$in": classes}

        if free is not None:
            # Handle both boolean and integer representations
            if free:
                query["isAccessibleForFree"] = {"$in": [True, 1]}
            else:
                query["isAccessibleForFree"] = {"$in": [False, 0]}

        if region:
            query["postalAddress.city"] = {
                "$regex": region, "$options": "i"}

        return await self.find_many(
            query,
            skip=skip,
            limit=limit,
            sort=[("attractionName", 1)]
        )

    async def count_with_filters(
        self,
        classes: Optional[List[int]] = None,
        free: Optional[bool] = None,
        region: Optional[str] = None
    ) -> int:
        """Count attractions with multiple filters."""
        query = {}

        if classes:
            query["attractionClasses"] = {"$in": classes}

        if free is not None:
            # Handle both boolean and integer representations
            if free:
                query["isAccessibleForFree"] = {"$in": [True, 1]}
            else:
                query["isAccessibleForFree"] = {"$in": [False, 0]}

        if region:
            query["postalAddress.city"] = {
                "$regex": region, "$options": "i"}

        return await self.count(query)

    async def find_nearby(self, lon: float, lat: float, radius_km: float, skip: int = 0, limit: int = 20) -> List[Dict]:
        """Find attractions near a specific location within a radius in kilometers.

        Args:
            lon: Longitude of the center point
            lat: Latitude of the center point
            radius_km: Radius in kilometers
            skip: Number of items to skip (pagination)
            limit: Maximum number of items to return

        Returns:
            List of attractions within the specified radius
        """
        # Convert kilometers to meters for MongoDB
        radius_meters = radius_km * 1000

        # Use MongoDB's $nearSphere operator with $maxDistance
        query = {
            "location": {
                "$nearSphere": {
                    "$geometry": {
                        "type": "Point",
                        # GeoJSON uses [longitude, latitude] order
                        "coordinates": [lon, lat]
                    },
                    "$maxDistance": radius_meters
                }
            }
        }

        # MongoDB will automatically sort by distance
        attractions = await self.find_many(
            query,
            skip=skip,
            limit=limit
        )

        # Add distance field to results
        for attraction in attractions:
            if "positionLat" in attraction and "positionLon" in attraction:
                attraction_lat = attraction["positionLat"]
                attraction_lon = attraction["positionLon"]

                # Calculate distance using Haversine formula
                R = 6371  # Earth's radius in km
                dLat = math.radians(attraction_lat - lat)
                dLon = math.radians(attraction_lon - lon)
                a = (math.sin(dLat/2) * math.sin(dLat/2) +
                     math.cos(math.radians(lat)) * math.cos(math.radians(attraction_lat)) *
                     math.sin(dLon/2) * math.sin(dLon/2))
                c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
                distance = R * c

                attraction["distance_km"] = distance

        return attractions

    async def count_nearby(self, lon: float, lat: float, radius_km: float) -> int:
        """Count attractions near a specific location within a radius in kilometers."""
        # Convert km to radians (Earth's radius is approximately 6371 km)
        radius_radians = radius_km / 6371

        # Use $geoWithin with $centerSphere for counting
        # $centerSphere takes [lng, lat] and radius in radians
        query = {
            "location": {
                "$geoWithin": {
                    "$centerSphere": [[lon, lat], radius_radians]
                }
            }
        }

        return await self.count(query)

    async def replace_all(self, attractions: List[Dict]) -> bool:
        """Replace all attractions data with new data."""
        try:
            # Drop existing collection and recreate
            await self.drop_collection()

            # Insert new data if any
            if attractions:
                await self.insert_many(attractions)

            # Text search index for the search() method
            await self.create_index([("attractionName", "text"), ("description", "text")])

            # Index for filtering by class
            await self.create_index([("attractionClasses", 1)])

            # Geospatial index for nearby queries
            await self.create_index([("location", "2dsphere")])

            # Index for filtering by region
            await self.create_index([("postalAddress.city", 1)])

            # Index for filtering free attractions
            await self.create_index([("isAccessibleForFree", 1)])

            return True
        except Exception as e:
            return False
