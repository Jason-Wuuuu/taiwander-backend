from fastapi import FastAPI
import logging
from .database.mongodb import MongoDB
from .core.exceptions import register_exception_handlers
from .core.settings import settings
from contextlib import asynccontextmanager
import os
import datetime
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Define lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage database connections during application lifespan."""
    # Connect to the database on startup
    await MongoDB.connect_to_database()
    
    # Check if data needs to be synchronized
    await check_data_sync()
    
    yield
    # Close database connection on shutdown
    await MongoDB.close_database_connection()

async def check_data_sync():
    """Check if data files exist and if data has been synced to MongoDB."""
    data_dir = Path("data")
    today = datetime.datetime.now().date()
    needs_sync = False
    
    # Step 1: Check if data directory and required files exist
    required_files = ["AttractionList.json", "AttractionServiceTimeList.json", "AttractionFeeList.json"]
    
    if not data_dir.exists() or not data_dir.is_dir():
        logger.info("Data directory not found. Will trigger data sync.")
        needs_sync = True
    else:
        # Check for specific required data files
        missing_files = [f for f in required_files if not (data_dir / f).exists()]
        
        if missing_files:
            logger.info(f"Missing required data files: {', '.join(missing_files)}. Will trigger data sync.")
            needs_sync = True
        else:
            # Check the most recent file's modification date
            data_files = [data_dir / f for f in required_files if (data_dir / f).exists()]
            if data_files:
                most_recent = max(data_files, key=lambda p: p.stat().st_mtime)
                last_mod_date = datetime.datetime.fromtimestamp(most_recent.stat().st_mtime).date()
                
                if last_mod_date < today:
                    logger.info(f"Data files last updated on {last_mod_date}. Will trigger data sync.")
                    needs_sync = True
                else:
                    logger.info(f"Data files are up to date (last updated: {last_mod_date}).")
    
    # Step 2: Check if data is in MongoDB
    if not needs_sync:
        try:
            # Check if we have attractions in the database
            collection = MongoDB.db.attractions
            attraction_count = await collection.count_documents({})
            
            if attraction_count == 0:
                logger.info("No attractions found in database. Will trigger data sync.")
                needs_sync = True
            else:
                logger.info(f"Database contains {attraction_count} attractions.")
        except Exception as e:
            logger.error(f"Error checking database: {str(e)}")
            # If we can't check the database, assume we need to sync
            needs_sync = True
    
    if needs_sync:
        try:
            # Import here to avoid circular imports
            from .services.data.attractions import AttractionDataService
            
            logger.info("Starting automatic data synchronization...")
            attraction_service = AttractionDataService(MongoDB.db)
            result = await attraction_service.process_attraction_data()
            
            if result:
                logger.info("Successfully synchronized attraction data.")
            else:
                logger.error("Failed to synchronize attraction data.")
        except Exception as e:
            logger.error(f"Error during automatic data sync: {str(e)}")

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    lifespan=lifespan
)

# Register exception handlers
register_exception_handlers(app)

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint to verify the API is running."""
    return {"status": "ok", "message": f"Welcome to {settings.APP_NAME} v{settings.APP_VERSION}"}

# Include routers for different API versions
from .api.v1 import attractions_router
app.include_router(attractions_router, prefix="/api") 