# SentimentAI

SentimentAI performs customer sentiment analysis for businesses. Our application uses Google NLP to:
- Analyze sentiment from customer reviews;
- Extract and score essential components of a review
- Provide an overview of the of customer sentiment in time
- Provide sentiment distribution (???)

## Getting reviews

Our application can fetch reviews from the Foursquare API for you if you have the business' place ID on Foursquare.
You can also upload the reviews yourself via our POST endpoints.

## Run the app

    docker-compose up
    
# REST API

The REST API to SentimentAI is described below.

## Get analyzed reviews from a place

### Request

`GET /places/<place_id>?api_provider=<provider>`

    curl -H "Accept: application/json" http://localhost:8080/places/<place_id>?api_provider=<provider>

### Response


## Upload a Place

### Data model for Place

    place_id: Optional[str] = None
    name: str
    address: str
    rating: Optional[float] = None
    api_provider: Optional[str] = None

### Request

`POST /places/upload-place`

    curl -X POST -H "Content-Type: application/json" -d @place.json http://localhost:8080/places/upload-place

### Response

A dictionary of the place uploaded that contains the generated place_id. This place_id must be used to upload reviews and query other endpoints.

## Upload a Review

### Data model for Review

    place_id: Optional[str] = None
    review_id: Optional[str] = None
    text: str
    created_at: Optional[str] = None
    language: Optional[str] = None

### Request

`POST /places/upload-place`

    curl -X POST -H "Content-Type: application/json" -d @review.json http://localhost:8080/places/<place_id>/upload-review

### Response

The complete list of reviews for the given place, including the recently updated review.
