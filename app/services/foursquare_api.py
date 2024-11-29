import requests


# Foursquare API endpoint to get place details
def get_foursquare_place(fsq_id):
    url = "https://api.foursquare.com/v3/places/{}?fields=name%2Clocation%2Crating".format(fsq_id)

    headers = {"accept": "application/json",
               "authorization": "fsq3dJKtqnpO17WAiCnBSaEK4kUwB5CJo55ajWEWX4OhKAM="}

    response = requests.get(url, headers=headers)
    data = response.json()

    place = {
        "place_id": fsq_id,
        "name": data.get("name"),
        "address": data.get("location").get("address"),
        "rating": data.get("rating")
    }

    return place

# Foursquare API endpoint to get place reviews
def get_foursquare_place_reviews(fsq_id, review_count):
    num_pages = (review_count // 50) + (1 if review_count % 50 != 0 else 0)
    reviews = []
    for page in range(num_pages):
        limit = 50 if page < num_pages - 1 or review_count % 50 == 0 else review_count % 50

        url = f"https://api.foursquare.com/v3/places/{fsq_id}/tips?limit={limit}&offset={page * 50}"

        headers = {"accept": "application/json",
                    "authorization": "fsq3dJKtqnpO17WAiCnBSaEK4kUwB5CJo55ajWEWX4OhKAM="}

        response = requests.get(url, headers=headers)
        data = response.json()

        reviews.extend([
            {
                "review_id": review.get("id"),
                "text": review.get("text"),
                "created_at": review.get("created_at"),
            }
            for review in data
        ])

    return reviews