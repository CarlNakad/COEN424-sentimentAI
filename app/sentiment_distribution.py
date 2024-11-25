from mongodb_connection import db

def get_sentiment_distribution(place_id):
    sentiment_distribution = []

    pipeline_positive = [
        {"$set": {
            "_id": {
                "$concat": ["$place_id", "_", "positive"]
            }}},
        {"$match" : {
            "place_id": str(place_id),
            "sentiment_score": {
                "$gt": 0.25,
                "$lte": 1.00
            }}},
        { "$group": {
            "_id": "$_id",
            "positive_count": { "$sum": 1 },

        }},
        {"$addFields": {
            "sentiment": "positive"}
        }
    ]

    positive_results = list(db['review'].aggregate(pipeline_positive))
    sentiment_distribution.append(positive_results)

    pipeline_negative = [
        {"$set": {
            "_id": {
                "$concat": ["$place_id", "_", "negative"]
            }}},
        {"$match" : {
            "place_id": str(place_id),
            "sentiment_score": {
                "$gte": -1.00,
                "$lt": -0.25
            }}},
        { "$group": {
            "_id": "$_id",
            "negative_count": { "$sum": 1 },
        }},
        {"$addFields": {
            "sentiment": "negative"}}
    ]

    negative_results = list(db['review'].aggregate(pipeline_negative))
    sentiment_distribution.append(negative_results)

    pipeline_neutral = [
        {"$set": {
            "_id": {
                "$concat": ["$place_id", "_", "neutral"]
            }}},
        {"$match": {
            "place_id": str(place_id),
            "sentiment_score": {
                "$gte": -0.25,
                "$lte": 0.25
            }}},
        {"$group": {
            "_id": "$_id",
            "neutral_count": {"$sum": 1},
        }},
        {"$addFields": {
            "sentiment": "neutral"}}
    ]

    neutral_results = list(db['review'].aggregate(pipeline_neutral))
    sentiment_distribution.append(neutral_results)

    return sentiment_distribution

