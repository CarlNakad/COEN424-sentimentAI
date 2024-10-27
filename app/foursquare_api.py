import requests

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

def get_foursquare_place_reviews(fsq_id, review_count):
    url = "https://api.foursquare.com/v3/places/{}/tips?limit={}".format(fsq_id, review_count)

    headers = {"accept": "application/json",
                "authorization": "fsq3dJKtqnpO17WAiCnBSaEK4kUwB5CJo55ajWEWX4OhKAM="}

    response = requests.get(url, headers=headers)
    data = response.json()

    reviews = [
        {
            "review_id": review.get("id"),
            "text": review.get("text"),
            "created_at": review.get("created_at"),
        }
        for review in data
    ]

    return reviews



# get_foursquare_place_reviews("4b1290d5f964a520da8a23e3")
# get_foursquare_place("4b1290d5f964a520da8a23e3")