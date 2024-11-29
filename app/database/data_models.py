from typing import Optional, List 
from pydantic import BaseModel 
from typing import Union

class Place(BaseModel):
    place_id: Optional[str] = None
    name: str
    address: str
    rating: Optional[float] = None
    api_provider: Optional[str] = None

class EntityScore(BaseModel):
    name: str
    sentiment: float
    confidence: float
    review_id: str
    place_id: str
 
class Review(BaseModel):
    place_id: Optional[str] = None
    review_id: Optional[str] = None
    text: str
    created_at: Optional[str] = None
    sentiment_score: Optional[float] = None
    entities_score: Optional[List[EntityScore]] = None
    language: Optional[str] = None

class PlaceReviews(BaseModel):
    place: Place
    reviews: List[Review]

class User(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Union[str, None] = None