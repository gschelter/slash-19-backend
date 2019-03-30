import json
import requests

API_KEY = "ada358ce40ea4d53a3188656f4b0e5ec"


def search_listennotes(term):
    res = requests.get(
        "https://listen-api.listennotes.com/api/v2/search?q={}&sort_by_date=0&offset=0&language=English&only_in=title,description&safe_mode=1".format(
            term),
        headers={
            "X-ListenAPI-Key": API_KEY})

    return json.loads(res.text)['results']


def get_genres():
    res = requests.get(
        "https://listen-api.listennotes.com/api/v2/genres", headers={"X-ListenAPI-Key": API_KEY})

    return json.loads(res.text)['genres']


def get_podcast_details(podcast_id):
    res = requests.get("https://listen-api.listennotes.com/api/v2/podcasts/{}".format(podcast_id),
                       headers={"X-ListenAPI-Key": API_KEY})

    return json.loads(res.text)
