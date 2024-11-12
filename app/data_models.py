from typing import Optional, List 
from pydantic import BaseModel 

class Address(BaseModel):
    civic_number: str
    street: str
    city: Optional[str] = None
    postal_code: Optional[str] = None
    province: Optional[str] = None
    country: Optional[str] = None

class Place(BaseModel):
    place_id: Optional[str] = None
    name: str
    address: Address
    rating: Optional[float] = None
    api_provider: Optional[str] = None

class EntityScore(BaseModel):
    name: str
    sentiment: float
    confidence: float
    review_id: str
    place_id: str
 
class Review(BaseModel):
    place_id: str
    review_id: Optional[str] = None
    text: str
    created_at: Optional[str] = None
    sentiment_score: Optional[float] = None
    entities_score: Optional[List[EntityScore]] = None

class PlaceReviews(BaseModel):
    place: Place
    reviews: List[Review]