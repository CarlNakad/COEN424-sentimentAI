from fastapi import FastAPI
# from mongodb_connection import mongodb_client, db
# from bson.objectid import ObjectId
import os

app = FastAPI()

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
async def get_place_reviews(api_provider: str, place_id: int):
    return {"api_provider": api_provider, "place_id": place_id}

@app.get("/{api_provider}/places/{place_id}/{review_count}")
async def get_place_reviews(api_provider: str, place_id: int, review_count: int):
    return {"api_provider": api_provider, "place_id": place_id, "review_count": review_count}


@app.get("/entity/{entity_name}/{review_count}")
async def get_entity_reviews(entity_name: str, review_count: int):
    return {"entity_name": entity_name, "review_count": review_count}

@app.get("/entities/{review_count}")
async def get_entities_reviews(review_count: int):
    return {"review_count": review_count}
