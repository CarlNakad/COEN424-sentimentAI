from typing import List, Optional
from fastapi import FastAPI, HTTPException
from mongodb_connection import db
from bson.objectid import ObjectId
import place_review_api
import uuid
from datetime import datetime
from sentiment_distribution import get_sentiment_distribution
from data_models import Review, Place, PlaceReviews

app = FastAPI(
    title="Sentiment API",
    description="API for sentiment reviews analysis",
    version="1.0.0",
    openapi_url="/openapi.yml"
)

@app.get("/")
async def root():
    return {"Hello": "SentimentAI!"}

@app.get("/places/{place_id}")
async def get_place_reviews(place_id: str, api_provider: Optional[str] = None):
    return place_review_api.get_place_reviews(api_provider, place_id, review_count=2)

@app.get("/places/{place_id}/{review_count}")
async def get_place_reviews(place_id: str, review_count: int, api_provider: Optional[str] = None):
    return place_review_api.get_place_reviews(api_provider, place_id, review_count)

@app.get("/places/{place_id}/sentiment/{review_count}")
async def get_place_reviews(place_id: str, review_count: int, api_provider: Optional[str] = None):
    reviews = place_review_api.get_place_reviews(api_provider, place_id, review_count)
    for review in reviews["reviews"]:
        review.pop("entities_score", None)
    return reviews

@app.get("/places/{place_id}/sentiment-over-time/{review_count}")
async def get_sentiment_over_time(place_id: str, review_count: int, api_provider: Optional[str] = None):
    reviews = place_review_api.get_place_reviews(api_provider, place_id, review_count)
    reviews["reviews"] = sorted(reviews["reviews"], key=lambda x: x.get("created_at"))

    sentiment_over_time = []
    for review in reviews["reviews"]:
        sentiment_score = review.get("sentiment_score")

        if sentiment_score >= 0.3:
            sentiment = "positive"
        elif sentiment_score >= 0.1:
            sentiment = "neutral"
        elif sentiment_score > -0.1:
            sentiment = "mixed"
        elif sentiment_score >= -0.3:
            sentiment = "neutral"
        else:
            sentiment = "negative"

        sentiment_over_time.append({
            "created_at": review.get("created_at"),
            "sentiment": sentiment,
            "sentiment_score": review.get("sentiment_score")
        })

    print(len(sentiment_over_time), "reviews found")

    return sentiment_over_time

@app.get("/places/{place_id}/sentiment-distribution/{review_count}")
async def get_place_reviews(place_id: str, review_count: int, api_provider: Optional[str] = None):
    place_review_api.get_place_reviews(api_provider, place_id, review_count)
    # manipulate to output the count
    return get_sentiment_distribution(place_id)

@app.post("/places/upload-place", response_model=Place)
async def upload_places(place: Place):
    if not place.place_id:
        place.place_id = str(uuid.uuid4())
    if not place.api_provider:
        place.api_provider = None
    return place_review_api.insert_place(place)

@app.post("/places/{place_id}/upload-review", response_model=List[Review])
async def upload_reviews(place_id:str, review:Review):
    place = place_review_api.get_place(place_id)
    if not place:
        raise HTTPException(status_code=404, detail="Place not found")

    review.place_id = place_id
    review.review_id = str(uuid.uuid4())
    if not review.created_at:
        review.created_at = str(datetime.now().isoformat())
    
    place_review_api.sentiment_analysis(place_id, place, [review.model_dump()])
    return place_review_api.return_reviews(place_id, 0)