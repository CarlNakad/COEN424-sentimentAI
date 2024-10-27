from foursquare_api import get_foursquare_place, get_foursquare_place_reviews
from google_nlp import analyze_sentiment

def get_place_reviews(api_provider: str, place_id: str, review_count: int):
    place = get_foursquare_place(place_id)
    place_reviews = get_foursquare_place_reviews(place_id, review_count)

    # Find place from MongoDB if it exists, 
    # return the existing sentiments 
    # otherwise analyze the sentiment and save it to MongoDB
    
    reviews = []
    for review in place_reviews:
        json_response = analyze_sentiment(review.get("text"))
    
        reviews.append({
            "review_id": review.get("review_id"),
            "text": review.get("text"),
            "created_at": review.get("created_at"),
            "sentiment_score": json_response.get("sentiment_score"),
            "entities_score": json_response.get("entities_score"),
            "language": json_response.get("language")
        })

    return {
        "place": place,
        "reviews": reviews,
        "api_provider": api_provider,
    }
