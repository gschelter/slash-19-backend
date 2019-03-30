import lxml.html
from bs4 import BeautifulSoup
from readability import Document


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
