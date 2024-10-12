from fastapi import FastAPI
from mongodb_connection import mongodb_client, db
from bson.objectid import ObjectId
import os

app = FastAPI()

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

if __name__ == "__main__":
    app.run(port=int(os.environ.get("PORT", 8080)),host='0.0.0.0',debug=True)