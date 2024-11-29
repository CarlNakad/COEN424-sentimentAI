from foursquare_api import get_foursquare_place_reviews
from google_nlp import analyze_sentiment
from mongodb_connection import db
from place_review_api import get_place_reviews

# Function tht performs sentiment analysis on new reviews and store results in MongoDB
def perform_sentiment_analysis(place_id, reviews):
    analyzed_reviews = []
    for review in reviews:
        analysis = analyze_sentiment(review['text'])
        analyzed_review = {
            "place_id": place_id,
            "review_id": review['review_id'],
            "text": review['text'],
            "created_at": review['created_at'],
            "sentiment_score": analysis["sentiment_score"],
            "entities_score": analysis["entities_score"],
            "language": analysis["language"]
        }
        
        for entity in analysis["entities_score"]:
            entity_data = {
                "name": entity["name"],
                "sentiment": entity["sentiment"],
                "confidence": entity["confidence"],
                "place_id": place_id,
                "review_id": review['review_id']
            }
            db["entity_score"].insert_one(entity_data)
        
        analyzed_reviews.append(analyzed_review)
    
    db['review'].insert_many(analyzed_reviews)
    return analyzed_reviews

# Function to retrieve and analyze reviews if they don't exist or if there are new reviewzz
def retrieve_and_analyze_reviews(place_id, review_count):
    db_reviews = list(db['review'].find({"place_id": place_id}).sort("created_at", -1).limit(review_count))
    
    if len(db_reviews) < review_count:
        reviews = get_foursquare_place_reviews(place_id, review_count)
        new_reviews = [r for r in reviews if r not in db_reviews] 
        
        analyzed_reviews = perform_sentiment_analysis(place_id, new_reviews)
        db_reviews.extend(analyzed_reviews)

    return db_reviews[:review_count]

def get_entity_score(api_provider: str, place_id: str, review_count: int, entity_name: str):
    # Use get_place_reviews to retrieve and analyze reviews
    place_reviews = get_place_reviews(api_provider, place_id, review_count)
    
    # Initialize variables to calculate overall analysis
    total_score = 0
    total_confidence = 0
    entity_count = 0

    # Iterate through reviews to find the specified entity and calculate scores
    for review in place_reviews["reviews"]:
        for entity in review.get("entities_score", []):
            if entity.get("name") == entity_name:
                total_score += entity.get("sentiment_score", 0)
                total_confidence += entity.get("confidence_score", 0)
                entity_count += 1

    # Calculate average scores
    if entity_count > 0:
        average_score = total_score / entity_count
        average_confidence = total_confidence / entity_count
    else:
        average_score = 0
        average_confidence = 0

    return {
        "entity_name": entity_name,
        "average_sentiment_score": average_score,
        "average_confidence_score": average_confidence,
        "entity_count": entity_count
    }

def get_all_entities_score(api_provider: str, place_id: str, review_count: int):
    # Use get_place_reviews to retrieve and analyze reviews
    place_reviews = get_place_reviews(api_provider, place_id, review_count)
    entities_scores = []
    for review in place_reviews["reviews"]:
        entities_scores.extend(review.get("entities_score", []))
    return entities_scores