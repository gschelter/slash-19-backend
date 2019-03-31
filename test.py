from podcasts import find_podcast_by_website

URL = 'https://trivago.de/'

if __name__ == '__main__':
    print(find_podcast_by_website(URL, True))
