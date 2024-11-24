import json
from bson import json_util
from foursquare_api import get_foursquare_place, get_foursquare_place_reviews
from google_nlp import analyze_sentiment
from mongodb_connection import db

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
        review_analyzed = {
            "place_id": place_id,
            "review_id": review.get("review_id"),
            "text": review.get("text"),
            "created_at": review.get("created_at"),
            "sentiment_score": json_response.get("sentiment_score"),
            "entities_score": json_response.get("entities_score"),
            "language": json_response.get("language")
        }
        entities_score = json_response.get("entities_score")
        for entity in entities_score:
            entity.update({"review_id": review.get("review_id")})
            entity.update({"place_id": place_id})
        db['entity_score'].insert_one({"entities_score": entities_score})

        # for the review table
        reviews.append(review_analyzed)
        # for the place_review table
        review.update({"reviews": review_analyzed})


    if reviews:
        db['review'].insert_many(reviews)
    db['place_reviews'].insert_one({"place": place, "reviews": reviews})


def get_place_reviews(api_provider: str, place_id: str, review_count: int):
    place = get_foursquare_place(place_id)
    place_reviews = get_foursquare_place_reviews(place_id, review_count)
    place_reviews = sorted(place_reviews, key=lambda x: x.get("created_at"), reverse=True)

    db_reviews = db['review'].find({"place_id": place_id})
    db_reviews = sorted(db_reviews, key=lambda x: x.get("created_at"), reverse=True)
    #print(db_reviews)
    if db_reviews:
        found_new_reviews = db_reviews[0].get("review_id") != place_reviews[0].get("review_id")
        print("found_new_reviews: ", found_new_reviews)
        print(db_reviews[0].get("review_id"))
        print( "SECONDDDDDDDDD", place_reviews[0].get("review_id"))
        if found_new_reviews or len(db_reviews) < review_count:
            sentiment_analysis(place_id, place, place_reviews[len(db_reviews):])
    else:
        place.update({"api_provider": api_provider})
        db['place'].insert_one(place)
        sentiment_analysis(place_id, place, place_reviews)

    return return_values(place_id, review_count)
