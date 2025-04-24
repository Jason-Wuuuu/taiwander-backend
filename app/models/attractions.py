from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class Position(BaseModel):
    """Geographical position model."""
    lat: float
    lon: float


class PostalAddress(BaseModel):
    """Postal address model."""
    addressRegion: str = Field(..., description="Region/city name")
    addressLocality: str = Field(..., description="Locality/town name")
    streetAddress: str = Field(..., description="Street address")
    zipCode: str = Field(..., description="Postal/ZIP code")


class Telephone(BaseModel):
    """Telephone model."""
    tel: str = Field(..., description="Telephone number")


class Image(BaseModel):
    """Image model."""
    name: str = Field(..., description="Image name")
    description: Optional[str] = Field(None, description="Image description")
    url: str = Field(..., description="Image URL")
    width: Optional[int] = Field(None, description="Image width")
    height: Optional[int] = Field(None, description="Image height")
    keywords: List[str] = Field(
        default_factory=list, description="Image keywords")


class ServiceTime(BaseModel):
    """Service time model."""
    name: str = Field(..., description="Service time name")
    description: Optional[str] = Field(
        None, description="Service time description")
    days: List[str] = Field(default_factory=list,
                            description="Days of the week")
    startTime: str = Field(..., description="Start time")
    endTime: str = Field(..., description="End time")
    effectiveDate: Optional[str] = Field(
        None, description="Date when this service time becomes effective")
    expireDate: Optional[str] = Field(
        None, description="Expiration date of this service time")


class Fee(BaseModel):
    """Fee model."""
    name: str = Field(..., description="Fee name")
    price: float = Field(..., description="Fee amount")
    description: Optional[str] = Field(None, description="Fee description")
    url: Optional[str] = Field(None, description="URL for fee information")


class SocialMedia(BaseModel):
    """Social media model."""
    name: str = Field(..., description="Social media name")
    description: Optional[str] = Field(
        None, description="Social media description")
    url: str = Field(..., description="Social media URL")
    keywords: List[str] = Field(default_factory=list, description="Keywords")
    tags: List[str] = Field(default_factory=list, description="Tags")


class Attraction(BaseModel):
    """Attraction model."""
    id: str = Field(..., description="Unique identifier")
    name: str = Field(..., description="Attraction name")
    alternateNames: List[str] = Field(
        default_factory=list, description="Alternative names")
    description: str = Field(..., description="Detailed description")
    position: Position = Field(..., description="Geographic position")
    classes: List[int] = Field(
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
    isPublicAccess: bool = Field(
        True, description="Public accessibility indicator")
    isAccessibleForFree: bool = Field(
        False, description="Free admission indicator")
    fees: List[Fee] = Field(default_factory=list, description="Admission fees")
    website: Optional[str] = Field(None, description="Official website URL")
    socialMediaURLs: List[SocialMedia] = Field(
        default_factory=list, description="Social media URLs")
    updatedAt: str = Field(..., description="Last update timestamp")


class AttractionResponse(BaseModel):
    """Single attraction response model."""
    attraction: Attraction


class AttractionsListResponse(BaseModel):
    """Paginated attractions list response model."""
    total: int = Field(..., description="Total number of attractions")
    page: int = Field(1, description="Current page number")
    limit: int = Field(20, description="Number of items per page")
    data: List[Attraction] = Field(..., description="List of attractions")
