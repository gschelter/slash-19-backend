import itertools
from collections import Counter
import requests
import json
from rake_nltk import Rake as Rake_nltk
from rake import Rake
from readability import Document
import lxml.html
from bs4 import BeautifulSoup
import tldextract

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

    data = {}
    for tag in tags:
        ele = soup.find("meta", attrs={'name': lambda x: x and x.lower() == tag})
        data[tag] = ele.attrs['content'] if ele is not None else None

    if data['keywords']:
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
    r = Rake('SmartStoplist.txt', min_char_length=3, max_words_length=1, min_keyword_frequency=4)
    return r.run(text)


def count_words(text: str):
    c = Counter(text.split())

    return c.most_common(20)


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


def get_podcasts_for_phrases(phrases):
    results = []

    i = min(2, len(phrases))
    while i > 0 and not (i == 1 and len(results) > 0):
        current_phrases = phrases[:i]
        for permutation in list(itertools.permutations(current_phrases)):
            matching_podcasts = search_listennotes(' '.join(permutation))

            results += matching_podcasts
        i -= 1

    # remove duplicate podcasts
    podcast_ids = list(set([result['podcast_id'] for result in results]))

    podcasts = [get_podcast_details(podcast_id) for podcast_id in podcast_ids]

    return podcasts


def combined(website_url: str):
    data = get_website_data(website_url)

    query = data['keywords'] if data['keywords'] else [tuple[0] for tuple in data['phrases']]
    if data['title']:
        query += data['title'].split(' ')
    query.append(tldextract.extract(website_url).domain)

    podcasts = get_podcasts_for_phrases(query)

    print('Counted words: {}'.format(data['counter']))
    print('Phrases: {}'.format(data['phrases']))
    print('Keywords: {}'.format(data['keywords']))
    print('Title: {}'.format(data['title']))
    print('Description: {}'.format(data['description']))
    print('Query: {}'.format(query))

    print('== Podcasts ==')
    for podcast in podcasts:
        print(podcast['title'])


if __name__ == "__main__":
    combined('https://www.redhat.com/de')
    # for genre in get_genres():
    #  print(genre)
