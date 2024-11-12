from fastapi import FastAPI
from mongodb_connection import db
from bson.objectid import ObjectId
import place_review_api
from sentiment_distribution import get_sentiment_distribution

app = FastAPI(
    title="Sentiment API",
    description="API for sentiment reviews analysis",
    version="1.0.0",
    openapi_url="/openapi.yml"
)

@app.get("/")
async def root():
    return {"Hello": "World!"}

@app.get("/user/{user_id}")
async def get_data(user_id: str):
    reviews_collection = db.reviews
    user_object_id = ObjectId(user_id)
    user = reviews_collection.find_one({"_id": user_object_id})
    if user:
        user['_id'] = str(user['_id']) 
        return user
    return {"error": "User not found"}

@app.get("/{api_provider}/places/{place_id}")
async def get_place_reviews(api_provider: str, place_id: str):
    return place_review_api.get_place_reviews(api_provider, place_id, review_count=2)

@app.get("/{api_provider}/places/{place_id}/{review_count}")
async def get_place_reviews(api_provider: str, place_id: str, review_count: int):
    return place_review_api.get_place_reviews(api_provider, place_id, review_count)

@app.get("/{api_provider}/places/{place_id}/sentiment/{review_count}")
async def get_place_reviews(api_provider: str, place_id: str, review_count: int):
    reviews = place_review_api.get_place_reviews(api_provider, place_id, review_count)
    for review in reviews["reviews"]:
        review.pop("entities_score", None)
    return reviews

@app.get("/{api_provider}/sentiment-over-time/{place_id}/{review_count}")
async def get_sentiment_over_time(api_provider: str, place_id: str, review_count: int):
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

@app.get("/{api_provider}/places/{place_id}/sentiment-distribution/{review_count}")
async def get_place_reviews(api_provider: str, place_id: str, review_count: int):
    place_review_api.get_place_reviews(api_provider, place_id, review_count)
    # manipulate to output the count
    return get_sentiment_distribution(place_id)
