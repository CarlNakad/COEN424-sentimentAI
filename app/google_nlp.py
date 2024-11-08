from google.cloud import language_v1
import os

def analyze_sentiment(text):
    client_options={"api_key": os.getenv("GOOGLE_CLOUD_NLP_API_KEY")}
    client = language_v1.LanguageServiceClient(
        client_options=client_options
    )

    document_type_in_plain_text = language_v1.Document.Type.PLAIN_TEXT
    document = {
        "content": text,
        "type_": document_type_in_plain_text,
    }

    encoding_type = language_v1.EncodingType.UTF8

    sentiment_response = client.analyze_sentiment(
        request={"document": document, "encoding_type": encoding_type}
    )

    entities_response = client.analyze_entity_sentiment(
        request={"document": document, "encoding_type": encoding_type}
    )

    sentiment_score = sentiment_response.document_sentiment.score
    language = sentiment_response.language

    entities_score = [
        {
            "name": entity.name,
            "sentiment": entity.sentiment.score,
            "confidence": entity.salience
        }
        for entity in entities_response.entities
    ]
    json_response = {
        "sentiment_score": sentiment_score,
        "entities_score": entities_score,
        "language": language
    }
    return json_response