import logging

from mongodb_connection import db
from bson.objectid import ObjectId
import place_review_api
from entity_api import get_entity_score, get_all_entities_score
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
import auth
from datetime import timedelta
from auth import ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token, hash_password, verify_token, verify_password

app = FastAPI(
    title="Sentiment API",
    description="API for sentiment reviews analysis",
    version="1.0.0",
    openapi_url="/openapi.yml"
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class User(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str


#tobe deleted
fake_users_db = {
    "BASH": {
        "username": "bash",
        "full_name": "bashar",
        "email": "bash@example.com",
        "hashed_password": "fakehashedpassword",
        "disabled": False,
    }
}



@app.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(user: User):
    users_collection = db["users"]
    # Check if user already exists
    if users_collection.find_one({"username": user.username}):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    # hashbrown pass and store user in db
    hashed_password = hash_password(user.password)
    new_user = {
        "username": user.username,
        "hashed_password": hashed_password
    }
    users_collection.insert_one(new_user)
    return {"message": "User registered successfully"}

def authenticate_user(username: str, password: str):
    users_collection = db["users"]
    user = users_collection.find_one({"username": username})
    if not user or not verify_password(password, user["hashed_password"]):
        logging.error(f"Authentication failed for user {username}")
        return False
    return user



# def fake_hash_password(password: str):
#     return "fakehashed" + password

# def authenticate_user(fake_db, username: str, password: str):
#     user = fake_db.get(username)
#     if not user:
#         logging.error(f"User {username} not found")
#         return False
#     if not fake_hash_password(password) == user["hashed_password"]:
#         logging.error(f"Password for user {username} does not match")
#         return False
#     return user

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}



async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token_data = verify_token(token, credentials_exception)
    user = db["users"].find_one({"username": token_data.username})
    if user is None:
        raise credentials_exception
    return user



#may need to add route of user after tokenization
@app.get("/users/me")
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

@app.get("/")
async def root():
    return {"Hello": "World!"}


@app.get("/user/{user_id}")
async def get_data(user_id: str, current_user: User = Depends(get_current_user)):
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
async def entity_score(name: str, review_count: int, place_id: str, current_user: str = Depends(get_current_user)):
    return get_entity_score(name, review_count, place_id)

@app.get("/entities/{review_count}")
async def entities_score(review_count: int, place_id: str):
    return get_all_entities_score(review_count, place_id)

