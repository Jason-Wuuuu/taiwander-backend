#!/usr/bin/env python3
import os
import sys
import asyncio
import logging
from datetime import datetime

# Add the parent directory to path so we can import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database.mongodb import MongoDB
from app.services.data.attractions import AttractionDataService
from app.core.settings import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(settings.DATA_LOG_PATH),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("data_sync")

async def sync_attraction_data():
    """Sync attraction data to MongoDB."""
    try:
        # Connect to database
        logger.info("Connecting to MongoDB...")
        await MongoDB.connect_to_database()
        
        # Process attraction data
        logger.info("Processing attraction data...")
        attraction_service = AttractionDataService(MongoDB.db)
        result = await attraction_service.process_attraction_data()
        
        if result:
            logger.info("Successfully synced attraction data to MongoDB")
        else:
            logger.error("Failed to sync attraction data to MongoDB")
            
        # Close database connection
        await MongoDB.close_database_connection()
        
        return result
    except Exception as e:
        logger.error(f"Error syncing attraction data: {str(e)}")
        return False

if __name__ == "__main__":
    logger.info("-" * 50)
    logger.info(f"Starting attraction data sync at {datetime.now().isoformat()}")
    
    # Run the sync process
    result = asyncio.run(sync_attraction_data())
    
    logger.info(f"Completed attraction data sync at {datetime.now().isoformat()}")
    logger.info(f"Sync status: {'Success' if result else 'Failed'}")
    logger.info("-" * 50)
    
    # Exit with appropriate status code
    sys.exit(0 if result else 1) 