from fastapi import HTTPException
from foursquare_api import get_foursquare_place_reviews
from google_nlp import analyze_sentiment
from mongodb_connection import db

# Function to perform sentiment analysis on new reviews and store results in MongoDB
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
        
        # Insert entity scores for each entity in the review
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
    
    # Store the analyzed reviews in MongoDB
    db['review'].insert_many(analyzed_reviews)
    return analyzed_reviews

# Function to retrieve and analyze reviews if they don't exist or if there are new reviews
def retrieve_and_analyze_reviews(place_id, review_count):
    db_reviews = list(db['review'].find({"place_id": place_id}).sort("created_at", -1).limit(review_count))
    
    # Fetch new reviews from Foursquare if there are fewer than the required count in MongoDB
    if len(db_reviews) < review_count:
        reviews = get_foursquare_place_reviews(place_id, review_count)
        new_reviews = [r for r in reviews if r not in db_reviews]
        
        # Analyze new reviews
        analyzed_reviews = perform_sentiment_analysis(place_id, new_reviews)
        db_reviews.extend(analyzed_reviews)

    return db_reviews[:review_count]

# Function to get sentiment analysis for a specific entity
def get_entity_score(name, review_count, place_id):
    retrieve_and_analyze_reviews(place_id, review_count)  # Fetch and analyze reviews if necessary

    pipeline = [
        {"$match": {"name": name, "place_id": place_id}},  # Match the entity name and place
        {"$sort": {"created_at": -1}},                      # Sort by the most recent reviews
        {"$limit": review_count},                           # Limit to the specified review count
        {
            "$group": {                                     # Aggregate to calculate average sentiment and count
                "_id": "$name",
                "average_sentiment": {"$avg": "$sentiment"},
                "total_mentions": {"$sum": 1},
            }
        }
    ]
    result = list(db['entity_score'].aggregate(pipeline))
    if not result:
        raise HTTPException(status_code=404, detail="Entity not found or no data available")

    return result[0]

# Function to get sentiment analysis for all entities
def get_all_entities_score(review_count, place_id):
    retrieve_and_analyze_reviews(place_id, review_count)  # Fetch and analyze reviews if necessary

    pipeline = [
        {"$match": {"place_id": place_id}},  # Match the place
        {"$sort": {"created_at": -1}},       # Sort by most recent
        {"$limit": review_count},            # Limit to specified review count
        {
            "$group": {                      # Group and aggregate for each entity
                "_id": "$name",
                "average_sentiment": {"$avg": "$sentiment"},
                "total_mentions": {"$sum": 1},
            }
        }
    ]
    result = list(db['entity_score'].aggregate(pipeline))
    return result
