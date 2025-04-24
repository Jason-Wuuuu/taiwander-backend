from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field


class Position(BaseModel):
    """Geographical position model."""
    lat: float
    lon: float


class PostalAddress(BaseModel):
    """Postal address model."""
    city: Optional[str] = Field(None, description="Region/city name")
    cityCode: Optional[str] = Field(None, description="City code")
    town: Optional[str] = Field(None, description="Locality/town name")
    townCode: Optional[str] = Field(None, description="Town code")
    zipCode: Optional[str] = Field(None, description="Postal/ZIP code")
    streetAddress: Optional[str] = Field(None, description="Street address")


class Telephone(BaseModel):
    """Telephone model."""
    tel: Optional[str] = Field(None, description="Telephone number")


class Image(BaseModel):
    """Image model."""
    name: Optional[str] = Field(None, description="Image name")
    description: Optional[str] = Field(None, description="Image description")
    url: Optional[str] = Field(None, description="Image URL")
    width: Optional[int] = Field(None, description="Image width")
    height: Optional[int] = Field(None, description="Image height")
    keywords: List[str] = Field(
        default_factory=list, description="Image keywords")


class ServiceTime(BaseModel):
    """Service time model."""
    name: Optional[str] = Field(None, description="Service time name")
    description: Optional[str] = Field(
        None, description="Service time description")
    serviceDays: List[str] = Field(default_factory=list,
                                   description="Days of the week")
    startTime: Optional[str] = Field(None, description="Start time")
    endTime: Optional[str] = Field(None, description="End time")
    effectiveDate: Optional[str] = Field(
        None, description="Date when this service time becomes effective")
    expireDate: Optional[str] = Field(
        None, description="Expiration date of this service time")


class Fee(BaseModel):
    """Fee model."""
    name: Optional[str] = Field(None, description="Fee name")
    price: Optional[float] = Field(None, description="Fee amount")
    description: Optional[str] = Field(None, description="Fee description")
    url: Optional[str] = Field(None, description="URL for fee information")


class SocialMedia(BaseModel):
    """Social media model."""
    name: Optional[str] = Field(None, description="Social media name")
    description: Optional[str] = Field(
        None, description="Social media description")
    url: Optional[str] = Field(None, description="Social media URL")
    keywords: List[str] = Field(default_factory=list, description="Keywords")
    tags: List[str] = Field(default_factory=list, description="Tags")


class LocatedCity(BaseModel):
    """Located city model."""
    name: Optional[str] = Field(None, description="City name")
    city: Optional[str] = Field(None, description="City")
    cityCode: Optional[str] = Field(None, description="City code")
    town: Optional[str] = Field(None, description="Town")
    townCode: Optional[str] = Field(None, description="Town code")
    classId: Optional[int] = Field(None, alias="class", description="Class ID")


class Attraction(BaseModel):
    """Attraction model."""
    id: str = Field(..., description="Unique identifier")
    attractionName: str = Field(..., description="Attraction name")
    alternateNames: List[str] = Field(
        default_factory=list, description="Alternative names")
    description: Optional[str] = Field(
        None, description="Detailed description")
    positionLat: Optional[float] = Field(None, description="Latitude")
    positionLon: Optional[float] = Field(None, description="Longitude")
    location: Optional[Dict[str, Any]] = Field(None,
                                               description="Geographic position in GeoJSON format")
    attractionClasses: List[int] = Field(
        default_factory=list, description="Attraction classification codes")
    postalAddress: Optional[PostalAddress] = Field(
        None, description="Postal address")
    telephones: List[Telephone] = Field(
        default_factory=list, description="Contact telephone numbers")
    images: List[Image] = Field(
        default_factory=list, description="Associated images")
    serviceTimes: List[ServiceTime] = Field(
        default_factory=list, description="Service/opening times")
    trafficInfo: Optional[str] = Field(
        None, description="Transportation information")
    parkingInfo: Optional[str] = Field(None, description="Parking information")
    facilities: List[str] = Field(
        default_factory=list, description="Facility information")
    serviceStatus: Optional[int] = Field(None, description="Service status")
    isPublicAccess: bool = Field(
        True, description="Public accessibility indicator")
    isAccessibleForFree: bool = Field(
        False, description="Free admission indicator")
    feeInfo: Optional[str] = Field(None, description="Fee information")
    fees: List[Fee] = Field(
        default_factory=list, description="Admission fees")
    paymentMethods: List[str] = Field(
        default_factory=list, description="Payment methods")
    locatedCities: List[LocatedCity] = Field(
        default_factory=list, description="Located cities")
    websiteUrl: Optional[str] = Field(None, description="Official website URL")
    reservationUrls: List[str] = Field(
        default_factory=list, description="Reservation URLs")
    mapUrls: List[str] = Field(
        default_factory=list, description="Map URLs")
    sameAsUrls: List[str] = Field(
        default_factory=list, description="Same as URLs")
    socialMediaUrls: List[SocialMedia] = Field(
        default_factory=list, description="Social media URLs")
    visitDuration: Optional[int] = Field(None, description="Visit duration")
    assetsClass: Optional[int] = Field(None, description="Assets class")
    subAttractions: List[str] = Field(
        default_factory=list, description="Sub attractions")
    partOfAttraction: Optional[str] = Field(
        None, description="Part of attraction")
    remarks: Optional[str] = Field(None, description="Remarks")
    updateTime: str = Field(..., description="Last update timestamp")


class AttractionResponse(BaseModel):
    """Single attraction response model."""
    attraction: Attraction


class AttractionsListResponse(BaseModel):
    """Paginated attractions list response model."""
    total: int = Field(..., description="Total number of attractions")
    page: int = Field(1, description="Current page number")
    limit: int = Field(20, description="Number of items per page")
    data: List[Attraction] = Field(..., description="List of attractions")
