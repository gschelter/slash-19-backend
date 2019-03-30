import itertools
import requests
import tldextract
from html_extraction import extract_metadata, html2text, extract_main_text
from listennotes_api import search_listennotes, get_podcast_details, do_networking
from text_processing import count_words, extract_phrases

COMBINED_PHRASES = 3


def get_website_data(link: str):
    response = requests.get(link)

    html = response.text

    data = extract_metadata(html)
    data['text'] = html2text(html)
    data['main_text'] = extract_main_text(html)
    data['counter'] = count_words(data['text'])

    phrases_text = data['text']
    if data['title']:
        phrases_text += ' ' + data['title']
    data['phrases'] = extract_phrases(phrases_text)

    return data


def get_podcasts_for_phrases(phrases):
    results = []

    i = min(COMBINED_PHRASES, len(phrases))
    while i > 0 and not (i == 1 and len(results) > 0):
        current_phrases = phrases[:i]

        matching_podcasts = do_networking(lambda permutation: search_listennotes(' '.join(permutation)),
                                          list(itertools.permutations(current_phrases)))

        for x in matching_podcasts:
            results += x

        i -= 1

    # remove duplicate podcasts
    podcast_ids = list(set([result['podcast_id'] for result in results]))

    podcasts = do_networking(lambda podcast_id: get_podcast_details(podcast_id), podcast_ids)

    return podcasts


def find_podcast_by_website(website_url: str, output=False):
    data = get_website_data(website_url)

    query = []
    if data['keywords']:
        query += data['keywords']
    else:
        query += [tuple[0] for tuple in data['phrases']]

    if data['title']:
        query += data['title'].split(' ')
    query.append(tldextract.extract(website_url).domain)

    podcasts = get_podcasts_for_phrases(query)

    if output:
        print('Counted words: {}'.format(data['counter']))
        print('Phrases: {}'.format(data['phrases']))
        print('Keywords: {}'.format(data['keywords']))
        print('Title: {}'.format(data['title']))
        print('Description: {}'.format(data['description']))
        print('Query: {}'.format(query))

        print('== Podcasts ==')
        for podcast in podcasts:
            print(podcast['title'])

    return podcasts
