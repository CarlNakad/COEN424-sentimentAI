from fastapi import FastAPI
from mongodb_connection import db
from bson.objectid import ObjectId
import place_review_api
from entity_api import get_entity_score, get_all_entities_score


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



@app.get("/entity/{name}/{review_count}")
async def entity_score(name: str, review_count: int, place_id: str):
    return get_entity_score(name, review_count, place_id)

@app.get("/entities/{review_count}")
async def entities_score(review_count: int, place_id: str):
    return get_all_entities_score(review_count, place_id)

