# SentimentAI

SentimentAI performs customer sentiment analysis for businesses. Our application uses Google NLP to:
- Analyze sentiment from customer reviews;
- Extract and score essential components of a review
- Provide an overview of the of customer sentiment in time
- Provide sentiment distribution (???)

## Getting reviews

Our application can fetch reviews from the Foursquare API for you if you know its Foursquare place ID.
You can also upload the reviews yourself via our POST endpoints.

## Run the app

    docker-compose up
    
# REST API

The REST API to SentimentAI is described below.

## Get analyzed reviews

Fetches reviews for the place and API provider combination you give. Our application analyzes the new reviews and returns the complete list of analyzed reviews. If you omit to give an API provider, the application will look for the reviews you uploaded yourself.

### Request

`GET /places/<place_id>?api_provider=<provider>`

    curl -H "Accept: application/json" http://localhost:8080/places/<place_id>?api_provider=<provider>

### Response

A json representation of the place and a list of analyzed reviews (including entity score for each review). You can specify an API provider to get the reviews for a specific API provider, or omit it to get the reviews that you uploaded yourself.

## Get a specific number of analyzed reviews from a place

Fetches a specific number of reviews for the place and API provider combination you give. Our application analyzes the new reviews and returns the complete list of analyzed reviews. If you omit to give an API provider, the application will look for the reviews you uploaded yourself.

### Request

`GET /places/<place_id>/<review_count>?api_provider=<provider>`

    curl -H "Accept: application/json" http://localhost:8080/places/<place_id>/<review_count>?api_provider=<provider>

### Response

A json representation of the place and a list of analyzed reviews (including entity score for each review). The number of reviews will correspond to the number you specified in the path. If you provide a number higher than the number of available reviews, the available reviews will be returned. You can specify an API provider to get the reviews for a specific API provider, or omit it to get the reviews that you uploaded yourself.

## Get reviews sentiment

Returns the overall sentiment for each review.

### Request

`GET /places/<place_id>/sentiment/<review_count>?api_provider=<provider>`

    curl -H "Accept: application/json" http://localhost:8080/places/<place_id>/sentiment/<review_count>?api_provider=<provider>

### Response

A json representation of the place and a list of analyzed reviews (excluding entity score for each review). The number of reviews will correspond to the number you specified in the path. If you provide a number higher than the number of available reviews, the available reviews will be returned. You can specify an API provider to get the reviews for a specific API provider, or omit it to get the reviews that you uploaded yourself.

## Get sentiment over time

Returns the overall sentiment over time.

### Request

`GET /places/<place_id>/sentiment-over-time/<review_count>?api_provider=<provider>`

    curl -H "Accept: application/json" http://localhost:8080/places/<place_id>/sentiment-over-time/<review_count>?api_provider=<provider>

### Response

An array of dictionaries, where each dictionary contains: the creation time, overall sentiment and sentiment score for the associated review. The number of reviews will correspond to the number you specified in the path. If you provide a number higher than the number of available reviews, the available reviews will be returned. You can specify an API provider to get the reviews for a specific API provider, or omit it to get the reviews that you uploaded yourself.

## Get review sentiment distribution

Returns the sentiment distribution.

### Request

`GET /places/<place_id>/sentiment-distribution/<review_count>?api_provider=<provider>`

    curl -H "Accept: application/json" http://localhost:8080/places/<place_id>/sentiment-distribution/<review_count>?api_provider=<provider>

### Response

(???)

## Create a place

You need to create a place to be able to upload your own reviews. You must include:
- The name of the place
- The address

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

A json representation of the place that you uploaded. It contains the generated place_id for your place. This place_id must be used to upload reviews and query other endpoints.

## Upload a review

Upload your own reviews to have them analyzed. You must minimally provide the review (text).

### Data model for Review

    place_id: Optional[str] = None
    review_id: Optional[str] = None
    text: str
    created_at: Optional[str] = None
    language: Optional[str] = None

### Request

`POST /places/<place_id>/upload-review`

    curl -X POST -H "Content-Type: application/json" -d @review.json http://localhost:8080/places/<place_id>/upload-review

### Response

The complete list of reviews for the given place, including the recently updated review.
