import json
from bson import json_util
from foursquare_api import get_foursquare_place, get_foursquare_place_reviews
from google_nlp import analyze_sentiment
from mongodb_connection import db

def have_reviews_changed(place_id, new_reviews_id):
    existing_review_id = db['review'].find({"place_id": place_id}, {'review_id': 1})
    existing_list = [str(review['review_id']) for review in existing_review_id]
    for review_id in new_reviews_id:
        if review_id not in existing_list:
            print("does if to check if changed")
            return True

def return_values(place_id):
    return {
        "place": json.loads(json_util.dumps(db['place'].find({"place_id": place_id}, {"_id": 0}))),
        "reviews": json.loads(json_util.dumps(db['review'].find({"place_id": place_id,
                                                                 "entities_score.place_id": place_id},
                                                                {"_id": 0, "entities_score._id": 0}))),
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

    db['review'].insert_many(reviews)
    db['place_reviews'].insert_one({"place": place, "reviews": reviews})


def get_place_reviews(api_provider: str, place_id: str, review_count: int):
    place = get_foursquare_place(place_id)
    place_reviews = get_foursquare_place_reviews(place_id, review_count)

    search = db['place'].find_one({"place_id": place_id})
    if search:
        # here, additional check to see if reviews have changed
        # check list of reviewIDs if same in db as incoming
        print("went in first if")
        new_reviews = []
        for review in place_reviews:
            new_reviews.append(review.get("review_id"))
        if have_reviews_changed(place_id, new_reviews) is False:
            print(have_reviews_changed(place_id, new_reviews))
            return return_values(place_id)
            # do sentiment analysis
    else:
        print("went in first else")
        place.update({"api_provider": api_provider})
        db['place'].insert_one(place)

    sentiment_analysis(place_id, place, place_reviews)
    return return_values(place_id)
