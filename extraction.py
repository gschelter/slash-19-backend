import itertools
from collections import Counter
import requests
import json
from rake_nltk import Rake as Rake_nltk
from rake import Rake
from readability import Document
import lxml.html
from bs4 import BeautifulSoup

API_KEY = "ada358ce40ea4d53a3188656f4b0e5ec"


def html2text(html):
    soup = BeautifulSoup(html, 'lxml')

    # kill all script and style elements
    for script in soup(["script", "style"]):
        script.decompose()  # rip it out

    # get text
    text = soup.get_text()

    # break into lines and remove leading and trailing space on each
    lines = (line.strip() for line in text.splitlines())
    # break multi-headlines into a line each
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    # drop blank lines
    text = '\n'.join(chunk for chunk in chunks if chunk)

    return text


def extract_main_text(html):
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
    data['text'] = html2text(html)
    data['main_text'] = extract_main_text(html)
    data['counter'] = count_words(data['text'])
    data['phrases'] = extract_phrases(data['text'])

    return data


def extract_phrases_nltk(text: str):
    r = Rake_nltk(min_length=1, max_length=4)  # Uses stopwords for english from NLTK, and all puntuation characters.
    r.extract_keywords_from_text(text)

    phrases = r.get_ranked_phrases()
    return phrases


# https://www.airpair.com/nlp/keyword-extraction-tutorial
def extract_phrases(text):
    r = Rake('SmartStoplist.txt', 4, 3, 4)
    return r.run(text)


def count_words(text: str):
    c = Counter(text.split())

    return c.most_common(20)


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

    print('Counted words: {}', data['counter'])
    print('Phrases: {}', data['phrases'])
    print('Keywords: {}', data['keywords'])
    print('Title: {}', data['title'])
    print('Description: {}', data['description'])

    podcasts = get_podcasts_for_phrases(data['phrases'])

    for podcast in podcasts:
        print(podcast['title_original'])


if __name__ == "__main__":
    combined('https://www.dell.com/de-de')
    # for genre in get_genres():
    #  print(genre)
