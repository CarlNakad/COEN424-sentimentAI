import logging
from fastapi import HTTPException
from google.api_core.exceptions import GoogleAPIError
from google.cloud import language_v1
import os

# Function to analyze the sentiment of the text
def analyze_sentiment(text):
    client_options = {"api_key": os.getenv("GOOGLE_CLOUD_NLP_API_KEY")}
    client = language_v1.LanguageServiceClient(
        client_options=client_options
    )
    document = {
        "content": text,
        "type_": language_v1.Document.Type.PLAIN_TEXT
    }
    encoding_type = language_v1.EncodingType.UTF8

    language, sentiment_score = analyze_text_sentiment(client, document, encoding_type)
    entities_score = analyze_entity_sentiment(client, document, encoding_type)

    json_response = {
        "sentiment_score": sentiment_score,
        "entities_score": entities_score,
        "language": language
    }
    return json_response

# Function to analyze the sentiment of the entities in the text
def analyze_entity_sentiment(client, document, encoding_type):
    entities_score = []
    try:
        entities_response = client.analyze_entity_sentiment(
            request={"document": document, "encoding_type": encoding_type}
        )
        entities_score = [
            {
                "name": entity.name,
                "sentiment": entity.sentiment.score,
                "confidence": entity.salience
            }
            for entity in entities_response.entities
        ]
    except GoogleAPIError as e:
        logging.error("Entity sentiment analysis failed: %s", e)
    return entities_score

# Function to analyze the sentiment of the text
def analyze_text_sentiment(client, document, encoding_type):
    sentiment_score, language = None, None
    try:
        sentiment_response = client.analyze_sentiment(
            request={"document": document, "encoding_type": encoding_type}
        )
        sentiment_score = sentiment_response.document_sentiment.score
        language = sentiment_response.language
    except GoogleAPIError as e:
        logging.error("Sentiment analysis failed: %s", e)
        raise HTTPException(status_code=500, detail="Sentiment analysis failed")
    return language, sentiment_score