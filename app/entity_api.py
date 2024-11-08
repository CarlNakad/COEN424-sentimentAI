from fastapi import HTTPException
from foursquare_api import get_foursquare_place_reviews
from google_nlp import analyze_sentiment
from mongodb_connection import db

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


def get_entity_score(name, review_count, place_id):
    retrieve_and_analyze_reviews(place_id, review_count)  

    pipeline = [
        {"$match": {"name": name, "place_id": place_id}},  
        {"$sort": {"created_at": -1}},                      
        {"$limit": review_count},                           
        {
            "$group": {                                     
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

# get sentiment analysis for all entities
def get_all_entities_score(review_count, place_id):
    retrieve_and_analyze_reviews(place_id, review_count)  

    pipeline = [
        {"$match": {"place_id": place_id}},  
        {"$sort": {"created_at": -1}},       
        {"$limit": review_count},            
        {
            "$group": {                      
                "_id": "$name",
                "average_sentiment": {"$avg": "$sentiment"},
                "total_mentions": {"$sum": 1},
            }
        }
    ]
    result = list(db['entity_score'].aggregate(pipeline))
    return result
