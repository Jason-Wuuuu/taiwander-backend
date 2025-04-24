# Taiwander Backend

## Overview

Taiwander Backend is a FastAPI-powered service that provides seamless access to Taiwan's tourism attractions. The service:

- Automatically syncs data daily from Taiwan's official tourism data
- Processes and stores attraction information in MongoDB
- Provides RESTful endpoints with comprehensive filtering options
- Supports full-text search for attraction names and descriptions
- Offers geospatial queries for finding nearby attractions
- Delivers fast performance through modern async Python architecture

## Technologies

- **FastAPI**: Web framework for building APIs
- **MongoDB**: Database for storing attraction data

## Requirements

- Python 3.7+
- MongoDB

## Dependencies

- FastAPI: Web framework for building APIs
- Motor: Async MongoDB driver
- PyMongo: MongoDB driver
- Requests: HTTP library for fetching data

All dependencies can be installed from the requirements.txt file.

## Setup

### Virtual Environment

```bash
# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Environment Variables

Create a `.env` file in the root directory with the following variables:

```env
# Application settings
APP_NAME="Taiwander Backend"
APP_VERSION="0.1.0"
DEBUG=true

# MongoDB settings
MONGODB_URL="mongodb://localhost:27017"
MONGODB_DB_NAME="taiwander"

# Data sync settings
DATA_SYNC_INTERVAL_HOURS=24
DATA_ZIP_PATH="data/attractions.zip"
DATA_LOG_PATH="data/sync.log"
```

### Running the Application

```bash
# Start the server
fastapi dev
```

### Data Synchronization

The application has two methods for syncing attraction data from Taiwan's tourism API:

1. **Automatic Check on Startup**: The server performs comprehensive checks:

   - Verifies the `/data` directory exists
   - Confirms all required data files are present (`AttractionList.json`, `AttractionServiceTimeList.json`, `AttractionFeeList.json`)
   - Checks if the data files were last updated today
   - Validates that attraction data exists in the MongoDB database

   If any of these checks fail, the application automatically triggers a data sync.

2. **Manual Sync**: You can also manually run the data sync script:

```bash
# Run data sync script
python scripts/data_sync.py
```

### API Documentation

Once the server is running, API documentation is available at:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Project Structure

```
taiwander-backend/
├── app/
│   ├── main.py                 # FastAPI application entry point
│   ├── api/
│   │   ├── v1/                 # API version 1 endpoints
│   │   │   ├── attractions.py  # Attraction routes
│   │   │   └── (future domains)# For restaurants, hotels, etc.
│   │   └── dependencies.py     # API dependencies (pagination, etc.)
│   ├── models/
│   │   ├── base.py             # Base models and mixins
│   │   └── attractions.py      # Attraction models
│   ├── schemas/                # Pydantic schemas for validation
│   │   ├── common.py           # Shared schemas (pagination, etc.)
│   │   └── attractions.py      # Attraction schemas
│   ├── database/
│   │   ├── mongodb.py          # MongoDB connection
│   │   └── repositories/       # Data access repositories
│   │       ├── base.py         # Base repository patterns
│   │       └── attractions.py  # Attraction data operations
│   ├── core/
│   │   ├── settings.py         # App settings from env variables
│   │   └── exceptions.py       # Custom exception handlers
│   └── services/
│       ├── data/
│       │   ├── fetcher.py      # Base data fetcher
│       │   └── attractions.py  # Attractions data sync
│       └── search.py           # Search functionality
├── scripts/
│   └── data_sync.py            # Scheduled data sync script
├── tests/                      # Test package
│   ├── test_api/               # API tests
│   └── test_services/          # Service tests
├── .env                        # Environment variables (gitignored)
└── requirements.txt            # Project dependencies
```

## Features

- Daily data updates from Taiwan tourism open data
- Filterable attraction endpoints
- Full-text search capabilities
- Geospatial queries for finding nearby attractions
- CORS support for frontend integration

## API Endpoints

The following endpoints are available:

### Attractions

#### Get All Attractions

```
GET /api/attractions?page=1&limit=20
```

Query Parameters:

- `page`: Page number (default: 1)
- `limit`: Number of items per page (default: 20)

#### Get Attraction by ID

```
GET /api/attractions/{attraction_id}
```

#### Get Attractions by Class

```
GET /api/attractions/class/{class_id}?page=1&limit=20
```

Query Parameters:

- `page`: Page number (default: 1)
- `limit`: Number of items per page (default: 20)

#### Search Attractions

```
GET /api/attractions/search?q=森林&page=1&limit=20
```

Query Parameters:

- `q`: Search query
- `page`: Page number (default: 1)
- `limit`: Number of items per page (default: 20)

### Filters

#### Get Attractions with Filters

```
GET /api/attractions/filter?classes=16,7&free=true&region=宜蘭縣&page=1&limit=20
```

Query Parameters:

- `classes`: Comma-separated list of class IDs
- `free`: Boolean indicating free admission
- `region`: Region/city name
- `page`: Page number (default: 1)
- `limit`: Number of items per page (default: 20)

#### Get Nearby Attractions

```
GET /api/attractions/nearby?lon=121.5388&lat=24.5023&radius=5&page=1&limit=20
```

Query Parameters:

- `lon`: Longitude of the center point
- `lat`: Latitude of the center point
- `radius`: Radius in kilometers (default: 5)
- `page`: Page number (default: 1)
- `limit`: Number of items per page (default: 20)

## Attraction Data

The application uses attraction data from Taiwan's official tourism data:

### Data Structure

The application retrieves data from three source files:

1. **AttractionList.json**: Core attraction information
2. **AttractionServiceTimeList.json**: Operating hours information
3. **AttractionFeeList.json**: Admission fee information

These are processed and merged into a single comprehensive data structure in our MongoDB database.

### Data Schema

Our consolidated attraction schema includes:

| Field                 | Type             | Description                          |
| --------------------- | ---------------- | ------------------------------------ |
| `id`                  | string           | Unique identifier for the attraction |
| `attractionName`      | string           | Name of the attraction               |
| `alternateNames`      | array of strings | Alternative names for the attraction |
| `description`         | string           | Detailed description                 |
| `positionLat`         | float            | Latitude coordinate                  |
| `positionLon`         | float            | Longitude coordinate                 |
| `location`            | object           | Geographic coordinates in GeoJSON    |
| `attractionClasses`   | array of numbers | Categories/classifications           |
| `postalAddress`       | object           | Physical address                     |
| `telephones`          | array of objects | Contact numbers                      |
| `images`              | array of objects | Associated images with URLs          |
| `serviceTimes`        | array of objects | Operating hours                      |
| `trafficInfo`         | string           | Transportation information           |
| `parkingInfo`         | string           | Parking details                      |
| `facilities`          | array of strings | Available amenities                  |
| `serviceStatus`       | number           | Current service status               |
| `isPublicAccess`      | boolean          | Public accessibility indicator       |
| `isAccessibleForFree` | boolean          | Free admission indicator             |
| `fees`                | array of objects | Admission costs                      |
| `paymentMethods`      | array of strings | Accepted payment methods             |
| `locatedCities`       | array of objects | Location information                 |
| `websiteUrl`          | string           | Official website                     |
| `mapUrls`             | array of strings | Maps and directions                  |
| `updateTime`          | string/datetime  | Last data update timestamp           |

Each `serviceTimes` object contains:

| Field           | Type                | Description                                 |
| --------------- | ------------------- | ------------------------------------------- |
| `name`          | string              | Schedule name (e.g., "Weekday Hours")       |
| `description`   | string or null      | Additional schedule information             |
| `serviceDays`   | array of strings    | Days applicable (e.g., "Monday", "Tuesday") |
| `startTime`     | string/time         | Opening time in 24-hour format              |
| `endTime`       | string/time         | Closing time in 24-hour format              |
| `effectiveDate` | string/date or null | Start date of validity period               |
| `expireDate`    | string/date or null | End date of validity period                 |

Each `fees` object contains:

| Field         | Type           | Description                 |
| ------------- | -------------- | --------------------------- |
| `name`        | string         | Fee type/name               |
| `price`       | number         | Cost amount                 |
| `description` | string or null | Additional fee details      |
| `url`         | string or null | Link to pricing information |

#### AttractionClasses Enum

The `attractionClasses` field contains numeric codes representing different categories of attractions:

| Code | Chinese Name   | English Name            | Description                                                               |
| ---- | -------------- | ----------------------- | ------------------------------------------------------------------------- |
| 1    | 文化類         | Cultural                | Cultural venues and activities                                            |
| 2    | 生態類         | Ecological              | Ecological/natural attractions                                            |
| 3    | 文化資產類     | Cultural Heritage       | Cultural heritage sites, historical buildings, ruins, cultural landscapes |
| 4    | 宗教廟宇類     | Religious Sites         | Religious temples, shrines, churches                                      |
| 5    | 藝術類         | Art                     | Art venues and exhibitions                                                |
| 6    | 商圈商店類     | Shopping Areas          | Shopping districts, old streets, markets                                  |
| 7    | 國家公園類     | National Parks          | National parks (Kenting, Yushan, etc.)                                    |
| 8    | 國家風景區類   | National Scenic Areas   | National scenic areas (Sun Moon Lake, Penghu, etc.)                       |
| 9    | 休閒農業類     | Leisure Agriculture     | Leisure agriculture, farming experiences                                  |
| 10   | 溫泉類         | Hot Springs             | Hot springs                                                               |
| 11   | 自然風景類     | Natural Landscapes      | Natural landscapes and scenery                                            |
| 12   | 遊憩類         | Recreation              | Recreational areas                                                        |
| 13   | 體育健身類     | Sports & Fitness        | Sports and fitness venues (walking trails, bicycle paths, stadiums)       |
| 14   | 觀光工廠類     | Tourism Factories       | Tourism factories with educational/cultural value                         |
| 15   | 都會公園類     | Urban Parks             | Urban parks                                                               |
| 16   | 森林遊樂區類   | Forest Recreation Areas | Forest recreation areas                                                   |
| 17   | 平地森林園區類 | Flatland Forest Parks   | Flatland forest parks                                                     |
| 18   | 國家自然公園類 | National Nature Parks   | National nature parks                                                     |
| 19   | 公園綠地類     | Parks & Green Spaces    | Parks and green spaces                                                    |
| 20   | 觀光遊樂業類   | Tourism & Amusement     | Tourism and amusement businesses                                          |
| 21   | 原住民文化類   | Indigenous Culture      | Indigenous cultural sites                                                 |
| 22   | 客家文化類     | Hakka Culture           | Hakka cultural sites                                                      |
| 23   | 交通場站類     | Transportation Hubs     | Transportation hubs (airports, stations)                                  |
| 24   | 水域環境類     | Water Environments      | Water environments (seas, wetlands, lakes, rivers)                        |
| 25   | 藝文場館類     | Arts & Cultural Venues  | Arts and cultural venues (museums, galleries, libraries)                  |
| 26   | 生態場館類     | Ecological Venues       | Ecological venues (zoos, aquariums, nature education centers)             |
| 27   | 娛樂場館類     | Entertainment Venues    | Entertainment venues (cinemas, game centers)                              |
| 254  | 其他           | Others                  | Others                                                                    |

### Data Source

This data is sourced from Taiwan's official tourism data platform (政府資料開放平台):

- URL: [景點 - 觀光資訊資料庫](https://data.gov.tw/dataset/7777)
- Update frequency: Daily
- Language: Traditional Chinese (Zh_tw)
- Data Standard: [觀光資料標準 V2.0.pdf](https://media.taiwan.net.tw/Upload/觀光資料標準V2.0.pdf)
