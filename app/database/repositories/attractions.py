from typing import Dict, List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from .base import BaseRepository


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
            await self.create_index([("postalAddress.addressRegion", 1)])
            await self.create_index([("isAccessibleForFree", 1)])

            return True
        except Exception as e:
            return False
