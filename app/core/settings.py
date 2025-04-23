from pydantic import BaseModel
from typing import Optional
import os

class Settings(BaseModel):
    # Application settings
    APP_NAME: str = "Taiwander Backend"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False
    
    # MongoDB settings
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "taiwander"
    
    # Data sync settings
    DATA_SYNC_INTERVAL_HOURS: int = 24
    DATA_ZIP_PATH: str = "data/attractions.zip"
    DATA_LOG_PATH: str = "data/sync.log"
    
    @classmethod
    def from_env(cls):
        """Create settings from environment variables."""
        env_settings = {}
        
        # Application settings
        if os.getenv("APP_NAME"):
            env_settings["APP_NAME"] = os.getenv("APP_NAME")
        if os.getenv("APP_VERSION"):
            env_settings["APP_VERSION"] = os.getenv("APP_VERSION")
        if os.getenv("DEBUG"):
            env_settings["DEBUG"] = os.getenv("DEBUG").lower() in ("true", "1", "t", "yes")
        
        # MongoDB settings
        if os.getenv("MONGODB_URL"):
            env_settings["MONGODB_URL"] = os.getenv("MONGODB_URL")
        if os.getenv("MONGODB_DB_NAME"):
            env_settings["MONGODB_DB_NAME"] = os.getenv("MONGODB_DB_NAME")
        
        # Data sync settings
        if os.getenv("DATA_SYNC_INTERVAL_HOURS"):
            env_settings["DATA_SYNC_INTERVAL_HOURS"] = int(os.getenv("DATA_SYNC_INTERVAL_HOURS"))
        if os.getenv("DATA_ZIP_PATH"):
            env_settings["DATA_ZIP_PATH"] = os.getenv("DATA_ZIP_PATH")
        if os.getenv("DATA_LOG_PATH"):
            env_settings["DATA_LOG_PATH"] = os.getenv("DATA_LOG_PATH")
        
        return cls(**env_settings)

# Create settings instance from environment variables or use defaults
settings = Settings.from_env() 