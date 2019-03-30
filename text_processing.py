from collections import Counter
from rake_nltk import Rake as Rake_nltk
from rake import Rake

PHRASES_MIN_LENGTH = 1
PHRASES_MAX_LENGTH = 4
PHRASES_MIN_CHAR_LENGTH = 3
PHRASES_MAX_WORDS_LENGTH = 1
PHRASES_MIN_KEYWORD_FREQUENCY = 3


def extract_phrases_nltk(text: str):
    r = Rake_nltk(min_length=PHRASES_MIN_LENGTH, max_length=PHRASES_MAX_LENGTH)
    r.extract_keywords_from_text(text)

    phrases = r.get_ranked_phrases()
    return phrases


# https://www.airpair.com/nlp/keyword-extraction-tutorial
def extract_phrases(text):
    r = Rake('SmartStoplist.txt', min_char_length=PHRASES_MIN_CHAR_LENGTH, max_words_length=PHRASES_MAX_WORDS_LENGTH,
             min_keyword_frequency=PHRASES_MIN_KEYWORD_FREQUENCY)
    return r.run(text)


def count_words(text: str, n=20):
    c = Counter(text.split())

    return c.most_common(n)
