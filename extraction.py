import itertools

import requests
import json
from rake_nltk import Rake
from readability import Document
import lxml.html
from bs4 import BeautifulSoup

API_KEY = "ada358ce40ea4d53a3188656f4b0e5ec"


def extract_text(html):
    doc = Document(html)
    html_string = doc.summary(True)

    text = lxml.html.document_fromstring(html_string).text_content()

    return str(text)


def extract_metadata(html):
    soup = BeautifulSoup(html, "lxml")
    tags = ['title', 'description', 'keywords']

    data = {
        tag: soup.find("meta", attrs={'name': lambda x: x and x.lower() == tag}).attrs['content'] for tag in tags
    }
    data['keywords'] = data['keywords'].split(',')

    return data


def get_website_data(link: str):
    response = requests.get(link)

    html = response.text

    data = extract_metadata(html)
    data['text'] = extract_text(html)

    return data


def extract_phrases(text: str):
    r = Rake(min_length=1, max_length=2)  # Uses stopwords for english from NLTK, and all puntuation characters.
    r.extract_keywords_from_text(text)

    phrases = r.get_ranked_phrases()
    return phrases


def get_data(term):
    res = requests.get(
        "https://listen-api.listennotes.com/api/v2/search?q={}&sort_by_date=0&type=episode&offset=0&language=English&ocid=&ncid=&safe_mode=0".format(
            term),
        headers={
            "X-ListenAPI-Key": API_KEY})

    return json.loads(res.text)['results']


def get_genres():
    res = requests.get(
        "https://listen-api.listennotes.com/api/v2/genres", headers={"X-ListenAPI-Key": API_KEY})

    return json.loads(res.text)['genres']


def get_podcasts_for_phrases(phrases):
    podcasts = []

    i = min(3, len(phrases))
    while i > 0 and not (i == 1 and len(podcasts) > 0):
        current_phrases = phrases[:i]
        for permutation in list(itertools.permutations(current_phrases)):
            matching_podcasts = get_data(' '.join(permutation))

            podcasts += matching_podcasts
        i -= 1

    return podcasts


def combined(website_url: str):
    data = get_website_data(website_url)
    website_text = data['text']
    website_phrases = extract_phrases(website_text)
    print(website_phrases)

    podcasts = get_podcasts_for_phrases(website_phrases)

    for podcast in podcasts:
        print(podcast['title_original'])


if __name__ == "__main__":
    combined('https://www.dell.com/de-de')
    # for genre in get_genres():
    #  print(genre)
