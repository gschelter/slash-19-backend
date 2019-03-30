from collections import Counter
from rake_nltk import Rake as Rake_nltk
from rake import Rake


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
