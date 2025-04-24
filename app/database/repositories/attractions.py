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
            {"classes": {"$in": class_ids}},
            skip=skip,
            limit=limit,
            # sort=[("name", 1)]
        )

    async def count_by_classes(self, class_ids: List[int]) -> int:
        """Count attractions by class IDs."""
        return await self.count({"classes": {"$in": class_ids}})

    async def find_by_region(self, region: str, skip: int = 0, limit: int = 20) -> List[Dict]:
        """Find attractions by region."""
        return await self.find_many(
            {"postalAddress.addressRegion": {"$regex": region, "$options": "i"}},
            skip=skip,
            limit=limit,
            # sort=[("name", 1)]
        )

    async def count_by_region(self, region: str) -> int:
        """Count attractions by region."""
        return await self.count({"postalAddress.addressRegion": {"$regex": region, "$options": "i"}})

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
            query["classes"] = {"$in": classes}

        if free is not None:
            query["isAccessibleForFree"] = free

        if region:
            query["postalAddress.addressRegion"] = {
                "$regex": region, "$options": "i"}

        return await self.find_many(
            query,
            skip=skip,
            limit=limit,
            sort=[("name", 1)]
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
            query["classes"] = {"$in": classes}

        if free is not None:
            query["isAccessibleForFree"] = free

        if region:
            query["postalAddress.addressRegion"] = {
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
        # MongoDB uses the WGS84 coordinate reference system
        # Convert km to radians (Earth's radius is approximately 6371 km)
        radius_radians = radius_km / 6371

        # Instead of using $geoWithin, let's use a simpler approach with direct coordinate comparison
        # We'll calculate a bounding box around the search point for initial filtering
        lat_delta = radius_km / 111.12  # 1 degree latitude is approximately 111.12 km
        # 1 degree longitude varies with latitude; it's about 111.12 * cos(lat) km
        lon_delta = radius_km / (111.12 * abs(math.cos(math.radians(lat))))

        min_lat = lat - lat_delta
        max_lat = lat + lat_delta
        min_lon = lon - lon_delta
        max_lon = lon + lon_delta

        # Get results within the bounding box
        query = {
            "$and": [
                {"position.lat": {"$gte": min_lat, "$lte": max_lat}},
                {"position.lon": {"$gte": min_lon, "$lte": max_lon}}
            ]
        }

        attractions = await self.find_many(
            query,
            skip=skip,
            limit=limit,
            # Sort by closest first - would require an aggregation pipeline
            # For now, use name as default sort
            sort=[("name", 1)]
        )

        # Further filter by actual distance for more accurate results
        result = []
        for attraction in attractions:
            if "position" in attraction and attraction["position"]:
                # Calculate the actual distance
                attraction_lat = attraction["position"]["lat"]
                attraction_lon = attraction["position"]["lon"]

                # Use Haversine formula to calculate distance
                R = 6371  # Earth's radius in km
                dLat = math.radians(attraction_lat - lat)
                dLon = math.radians(attraction_lon - lon)
                a = (math.sin(dLat/2) * math.sin(dLat/2) +
                     math.cos(math.radians(lat)) * math.cos(math.radians(attraction_lat)) *
                     math.sin(dLon/2) * math.sin(dLon/2))
                c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
                distance = R * c

                if distance <= radius_km:
                    result.append(attraction)

                    # Add distance for reference (optional)
                    attraction["distance_km"] = distance

        # Apply pagination after filtering
        start = skip
        end = min(start + limit, len(result))
        return result[start:end]

    async def count_nearby(self, lon: float, lat: float, radius_km: float) -> int:
        """Count attractions near a specific location within a radius in kilometers."""
        # Reuse the same logic to find nearby attractions but just return the count
        # Use a large limit to get all
        attractions = await self.find_nearby(lon, lat, radius_km, skip=0, limit=1000000)
        return len(attractions)

    async def replace_all(self, attractions: List[Dict]) -> bool:
        """Replace all attractions data with new data."""
        try:
            # Drop existing collection and recreate
            await self.drop_collection()

            # Insert new data if any
            if attractions:
                await self.insert_many(attractions)

            # Recreate the text index for search functionality
            await self.create_index([("name", "text"), ("description", "text")])

            # Recreate other indexes for better query performance
            await self.create_index([("classes", 1)])
            await self.create_index([("position.lat", 1), ("position.lon", 1)])
            # Remove the 2dsphere index that's causing the error
            # await self.create_index([("position", "2dsphere")])
            await self.create_index([("postalAddress.addressRegion", 1)])
            await self.create_index([("isAccessibleForFree", 1)])

            return True
        except Exception as e:
            return False
