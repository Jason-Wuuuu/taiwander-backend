# Taiwander Backend

## Overview

A FastAPI backend service that:

1. Downloads attraction data daily from Taiwan's tourism API
2. Parses and stores data in MongoDB
3. Provides RESTful endpoints to query attractions with filters
4. Includes full-text search functionality for attraction names and descriptions

## Technologies

- **FastAPI**: Web framework for building APIs
- **MongoDB**: Database for storing attraction data
- **Python 3.x**: Programming language

## Requirements

- Python 3.7+
- MongoDB

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

### Running the Application

```bash
# Start the server
fastapi dev
```

### API Documentation

Once the server is running, API documentation is available at:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Features

- Daily data updates from Taiwan tourism open data
- Filterable attraction endpoints
- Full-text search capabilities

## Attraction Data

The application uses attraction data from Taiwan's official tourism API, which includes:

### Data Structure

The attraction data consists of three main components:

1. **AttractionList.json**: Core attraction information including:

   - Basic details (name, ID, description)
   - Geographic coordinates
   - Address and contact information
   - Classification
   - Images
   - Facilities information
   - Access information

2. **AttractionServiceTimeList.json**: Operating hours for attractions including:

   - Opening/closing times for weekdays and weekends
   - Seasonal variations in operating hours
   - Special hours for holidays

3. **AttractionFeeList.json**: Admission fee information including:
   - Regular admission prices
   - Free attractions
   - Special pricing information

### Data Schema

#### AttractionList Fields

| Field                 | Type             | Description                          |
| --------------------- | ---------------- | ------------------------------------ |
| `AttractionID`        | string           | Unique identifier for the attraction |
| `AttractionName`      | string           | Name of the attraction               |
| `AlternateNames`      | array of strings | Alternative names for the attraction |
| `Description`         | string           | Detailed description                 |
| `PositionLat`         | number           | Latitude coordinate                  |
| `PositionLon`         | number           | Longitude coordinate                 |
| `AttractionClasses`   | array of numbers | Categories/classifications           |
| `PostalAddress`       | object           | Physical address                     |
| `Telephones`          | array of objects | Contact numbers                      |
| `Images`              | array of objects | Associated images with URLs          |
| `Organizations`       | array of objects | Managing organizations               |
| `ServiceTimeInfo`     | object           | Operating hours reference            |
| `TrafficInfo`         | string           | Transportation information           |
| `ParkingInfo`         | string           | Parking details                      |
| `Facilities`          | array of strings | Available amenities                  |
| `ServiceStatus`       | string           | Current service status               |
| `IsPublicAccess`      | boolean          | Public accessibility indicator       |
| `IsAccessibleForFree` | boolean          | Free admission indicator             |
| `FeeInfo`             | object           | Cost information reference           |
| `PaymentMethods`      | array of strings | Accepted payment methods             |
| `LocatedCities`       | array of objects | Location information                 |
| `WebsiteURL`          | string           | Official website                     |
| `MapURLs`             | array of strings | Maps and directions                  |
| `UpdateTime`          | string/datetime  | Last data update timestamp           |

#### AttractionServiceTimeList Fields

| Field            | Type             | Description                               |
| ---------------- | ---------------- | ----------------------------------------- |
| `AttractionID`   | string           | Unique identifier matching the attraction |
| `AttractionName` | string           | Name of the attraction                    |
| `ServiceTimes`   | array of objects | Array of operating schedules              |

Each `ServiceTimes` object contains:

| Field           | Type                | Description                                 |
| --------------- | ------------------- | ------------------------------------------- |
| `Name`          | string              | Schedule name (e.g., "Weekday Hours")       |
| `Description`   | string or null      | Additional schedule information             |
| `ServiceDays`   | array of strings    | Days applicable (e.g., "Monday", "Tuesday") |
| `StartTime`     | string/time         | Opening time in 24-hour format              |
| `EndTime`       | string/time         | Closing time in 24-hour format              |
| `EffectiveDate` | string/date or null | Start date of validity period               |
| `ExpireDate`    | string/date or null | End date of validity period                 |

#### AttractionFeeList Fields

| Field            | Type             | Description                               |
| ---------------- | ---------------- | ----------------------------------------- |
| `AttractionID`   | string           | Unique identifier matching the attraction |
| `AttractionName` | string           | Name of the attraction                    |
| `Fees`           | array of objects | Array of fee structures                   |
| `UpdateTime`     | string/datetime  | Last data update timestamp                |

Each `Fees` object contains:

| Field         | Type           | Description                 |
| ------------- | -------------- | --------------------------- |
| `Name`        | string         | Fee type/name               |
| `Price`       | number         | Cost amount                 |
| `Description` | string or null | Additional fee details      |
| `URL`         | string or null | Link to pricing information |

#### AttractionClasses Enum

The `AttractionClasses` field contains numeric codes representing different categories of attractions:

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

## API Endpoints

<!-- The following endpoints will be available once the backend is implemented: -->

### Attractions

#### Get All Attractions

```
GET /api/attractions?page=1&limit=20
```

Query Parameters:

- `page`: Page number (default: 1)
- `limit`: Number of items per page (default: 20)

Response:

```json
{
  "total": 3500,
  "page": 1,
  "limit": 20,
  "data": [
    {
      "id": "Attraction_345040000G_000001",
      "name": "太平山國家森林遊樂區",
      "description": "...",
      "position": {
        "lat": 24.5023,
        "lon": 121.5388
      },
      "classes": [16],
      "isAccessibleForFree": false,
      "website": "https://example.com/...",
      "updatedAt": "2023-11-30T00:00:00"
    }
    // ...more attractions
  ]
}
```

#### Get Attraction by ID

```
GET /api/attractions/{attraction_id}
```

Response:

```json
{
  "id": "Attraction_345040000G_000001",
  "name": "太平山國家森林遊樂區",
  "description": "...",
  "position": {
    "lat": 24.5023,
    "lon": 121.5388
  },
  "classes": [16],
  "alternateNames": ["Taipingshan National Forest Recreation Area"],
  "postalAddress": {
    "addressRegion": "宜蘭縣",
    "addressLocality": "大同鄉",
    "streetAddress": "泰雅路89號"
  },
  "images": [
    {
      "url": "https://example.com/image1.jpg",
      "description": "太平山景觀"
    }
  ],
  "serviceTimes": [
    {
      "name": "平日（星期一~星期五）",
      "startTime": "06:00:00",
      "endTime": "20:00:00",
      "days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    }
  ],
  "fees": [
    {
      "name": "全票",
      "price": 150
    }
  ],
  "isAccessibleForFree": false,
  "website": "https://example.com/...",
  "updatedAt": "2023-11-30T00:00:00"
}
```

#### Get Attractions by Class

```
GET /api/attractions/class/{class_id}?page=1&limit=20
```

Query Parameters:

- `page`: Page number (default: 1)
- `limit`: Number of items per page (default: 20)

Response: Same format as Get All Attractions

#### Search Attractions

```
GET /api/attractions/search?q=森林&page=1&limit=20
```

Query Parameters:

- `q`: Search query
- `page`: Page number (default: 1)
- `limit`: Number of items per page (default: 20)

Response: Same format as Get All Attractions

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

Response: Same format as Get All Attractions
