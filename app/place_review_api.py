import json
from email.policy import default

from bson import json_util
from foursquare_api import get_foursquare_place, get_foursquare_place_reviews
from google_nlp import analyze_sentiment
from mongodb_connection import db

def return_values():
    return {
        "place": json.loads(json_util.dumps(db['place'].find({}, {"_id": 0}))),
        "reviews": json.loads(json_util.dumps(db['review'].find({}, {"_id": 0, "entities_score._id": 0 }))),
    }

def get_place_reviews(api_provider: str, place_id: str, review_count: int):
    place = get_foursquare_place(place_id)
    place_reviews = get_foursquare_place_reviews(place_id, review_count)
    reviews = []
    collections = db.list_collection_names()

    if 'place' in collections:
        search = db['place'].find_one({"place_id": place_id })
        if search:
            return return_values()
    else:
        place.update({"api_provider": api_provider})
        db['place'].insert_one(place)

    if 'place_reviews' not in collections or 'review' not in collections or 'entity_score' not in collections:

        for review in place_reviews:
            json_response = analyze_sentiment(review.get("text"))
            review_analyzed = {
                "review_id": review.get("review_id"),
                "text": review.get("text"),
                "created_at": review.get("created_at"),
                "sentiment_score": json_response.get("sentiment_score"),
                "entities_score": json_response.get("entities_score"),
                "language": json_response.get("language")
            }
            db['entity_score'].insert_many(json_response.get("entities_score"))

            # for the review table
            reviews.append(review_analyzed)
            # for the place_review table
            review.update({"reviews": review_analyzed})

        db['review'].insert_many(reviews)
        db['place_reviews'].insert_one({"place": place, "reviews": reviews})

    return return_values()
