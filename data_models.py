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
    place_id: str
    name: str
    address: Address
    rating: float
    api_provider: str

class EntityScore(BaseModel):
    name: str
    sentiment: float
    confidence: float
    review_id: str
    place_id: str
 
class Review(BaseModel):
    place_id: Optional[str] = None
    review_id: str
    text: str
    created_at: str
    sentiment_score: float
    entities_score: List[EntityScore]

class PlaceReviews(BaseModel):
    place: Place
    reviews: List[Review]