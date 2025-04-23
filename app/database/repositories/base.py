from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection
from ...core.exceptions import DatabaseError

T = TypeVar('T')

class BaseRepository(Generic[T]):
    """Base repository with common database operations."""
    
    def __init__(self, collection: AsyncIOMotorCollection):
        self.collection = collection
    
    async def find_one(self, query: Dict) -> Optional[Dict]:
        """Find a single document by query."""
        return await self.collection.find_one(query)
    
    async def find_by_id(self, id: str) -> Optional[Dict]:
        """Find a document by its ID."""
        return await self.collection.find_one({"_id": id})
    
    async def find_many(
        self, 
        query: Dict = None, 
        skip: int = 0, 
        limit: int = 100,
        sort: List = None
    ) -> List[Dict]:
        """Find multiple documents by query with pagination."""
        if query is None:
            query = {}
            
        cursor = self.collection.find(query).skip(skip).limit(limit)
        
        if sort:
            cursor = cursor.sort(sort)
            
        return await cursor.to_list(length=limit)
    
    async def count(self, query: Dict = None) -> int:
        """Count documents matching a query."""
        if query is None:
            query = {}
        return await self.collection.count_documents(query)
    
    async def insert_one(self, document: Dict) -> str:
        """Insert a single document."""
        try:
            result = await self.collection.insert_one(document)
            return str(result.inserted_id)
        except Exception as e:
            raise DatabaseError(f"Failed to insert document: {str(e)}")
    
    async def insert_many(self, documents: List[Dict]) -> List[str]:
        """Insert multiple documents."""
        try:
            result = await self.collection.insert_many(documents)
            return [str(id) for id in result.inserted_ids]
        except Exception as e:
            raise DatabaseError(f"Failed to insert documents: {str(e)}")
    
    async def update_one(self, query: Dict, update: Dict) -> bool:
        """Update a single document."""
        try:
            result = await self.collection.update_one(query, {"$set": update})
            return result.modified_count > 0
        except Exception as e:
            raise DatabaseError(f"Failed to update document: {str(e)}")
    
    async def update_many(self, query: Dict, update: Dict) -> int:
        """Update multiple documents."""
        try:
            result = await self.collection.update_many(query, {"$set": update})
            return result.modified_count
        except Exception as e:
            raise DatabaseError(f"Failed to update documents: {str(e)}")
    
    async def delete_one(self, query: Dict) -> bool:
        """Delete a single document."""
        try:
            result = await self.collection.delete_one(query)
            return result.deleted_count > 0
        except Exception as e:
            raise DatabaseError(f"Failed to delete document: {str(e)}")
    
    async def delete_many(self, query: Dict) -> int:
        """Delete multiple documents."""
        try:
            result = await self.collection.delete_many(query)
            return result.deleted_count
        except Exception as e:
            raise DatabaseError(f"Failed to delete documents: {str(e)}")
    
    async def aggregate(self, pipeline: List[Dict]) -> List[Dict]:
        """Execute an aggregation pipeline."""
        try:
            return await self.collection.aggregate(pipeline).to_list(length=None)
        except Exception as e:
            raise DatabaseError(f"Failed to execute aggregation: {str(e)}")
    
    async def create_index(self, keys, **kwargs):
        """Create an index."""
        try:
            return await self.collection.create_index(keys, **kwargs)
        except Exception as e:
            raise DatabaseError(f"Failed to create index: {str(e)}")
    
    async def drop_collection(self):
        """Drop the collection."""
        try:
            return await self.collection.drop()
        except Exception as e:
            raise DatabaseError(f"Failed to drop collection: {str(e)}")
    
    async def bulk_write(self, operations):
        """Execute bulk write operations."""
        try:
            return await self.collection.bulk_write(operations)
        except Exception as e:
            raise DatabaseError(f"Failed to execute bulk write: {str(e)}") 