import json
from bson import json_util
from fastapi import HTTPException
from data_models import Place, Review

from foursquare_api import get_foursquare_place, get_foursquare_place_reviews
from google_nlp import analyze_sentiment
from mongodb_connection import db
import logging

api_providers = ["foursquare"]

def return_values(place_id, review_count):
    return {
        "place": json.loads(json_util.dumps(db['place'].find({"place_id": place_id}, {"_id": 0}))),
        "reviews": json.loads(json_util.dumps(db['review'].find({"place_id": place_id,
                                                                 "entities_score.place_id": place_id},
                                                                {"_id": 0, "entities_score._id": 0}).limit(review_count))),
    }

def sentiment_analysis(place_id, place, place_reviews):
    reviews = []
    for review in place_reviews:
        json_response = analyze_sentiment(review.get("text"))
        entities_score = json_response.get("entities_score")
        review_analyzed = {
            "place_id": place_id,
            "review_id": review.get("review_id"),
            "text": review.get("text"),
            "created_at": review.get("created_at"),
            "sentiment_score": json_response.get("sentiment_score"),
            "entities_score": entities_score,
            "language": json_response.get("language")
        }

        for entity in entities_score:
            entity.update({"review_id": review.get("review_id")})
            entity.update({"place_id": place_id})
        db['entity_score'].insert_one({"entities_score": entities_score})

        reviews.append(review_analyzed)
        review.update({"reviews": review_analyzed})

    if len(reviews) > 0:
        db['review'].insert_many(reviews)
        db['place_reviews'].insert_one({"place": place, "reviews": reviews})


def get_place_reviews(api_provider: str, place_id: str, review_count: int):
    if not api_provider or api_provider not in api_providers:
        raise HTTPException(status_code=400, detail="Invalid API provider")
    if review_count < 1:
        raise HTTPException(status_code=400, detail="Invalid review count")


    place = get_foursquare_place(place_id)

    place_reviews = get_foursquare_place_reviews(place_id, review_count)
    place_reviews = sorted(place_reviews, key=lambda x: x.get("created_at"), reverse=True)

    db_reviews = db['review'].find({"place_id": place_id})
    db_reviews = sorted(db_reviews, key=lambda x: x.get("created_at"), reverse=True)
    
    if db_reviews:
        found_new_reviews = db_reviews[0].get("review_id") != place_reviews[0].get("review_id")
        if found_new_reviews or len(db_reviews) < review_count:
            sentiment_analysis(place_id, place, place_reviews[len(db_reviews):])
    else:
        place.update({"api_provider": api_provider})
        db['place'].insert_one(place)
        sentiment_analysis(place_id, place, place_reviews)

    return return_values(place_id, review_count)

def insert_place(place: Place):
    db['place'].insert_one(place)
    result = db['place'].insert_one(place.model_dump)
    inserted_place = db['place'].find_one({"_id": result.inserted_id})
    return inserted_place

def get_place(place_id: str):
    return db['place'].find_one({"place_id:": place_id})

def sentiment_analysis(place_id, place, place_reviews):
    reviews = []
    for review in place_reviews:
        json_response = analyze_sentiment(review.get("text"))
        entities_score = json_response.get("entities_score")
        review_analyzed = {
            "place_id": place_id,
            "review_id": review.get("review_id"),
            "text": review.get("text"),
            "created_at": review.get("created_at"),
            "sentiment_score": json_response.get("sentiment_score"),
            "entities_score": entities_score,
            "language": json_response.get("language")
        }

        for entity in entities_score:
            entity.update({"review_id": review.get("review_id")})
            entity.update({"place_id": place_id})
        db['entity_score'].insert_one({"entities_score": entities_score})

        reviews.append(review_analyzed)
        review.update({"reviews": review_analyzed})

    if len(reviews) > 0:
        db['review'].insert_many(reviews)
        result = db['place_reviews'].insert_one({"place": place, "reviews": reviews})
        inserted_review = db['review'].find_one({"_id": result.inserted_id})
    return inserted_review

