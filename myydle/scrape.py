import re
import html
from urllib.parse import urlparse, urlunparse, urljoin
from bs4 import BeautifulSoup
from requests import PreparedRequest

from myydle.filter import keep
from myydle.normalize import normalize_url, normalize_path

URL_PREFIX = 'https://moodle.carleton.edu'

def scrape_html(doc):
    soup = BeautifulSoup(doc, 'html.parser')
    def yes():
        for tag in soup.find_all('link'):
            yield tag.get('href')
        for tag in soup.find_all('script'):
            yield tag.get('src')
        for tag in soup.find_all('img'):
            yield tag.get('src')
    def maybe():
        for tag in soup.find_all('a'):
            yield tag.get('href')
    # need to html unescape? depends on bs4 api
    def paths(urls):
        for _url in urls:
            if _url is not None and len(_url) > 0:
                url = normalize_url(_url)
                if url.startswith(URL_PREFIX):
                    path = url[len(URL_PREFIX):]
                    yield path
    ret = set()
    for path in paths(yes()):
        ret.add(path)
    for path in paths(maybe()):
        if keep(path):
            ret.add(path)
    return ret

import_re = re.compile(r'@import url\(([^\)]*)\)')

def scrape_css(path, doc):
    paths = set()
    for m in import_re.finditer(doc):
        imp = m[1]
        if not imp.startswith('http') and not imp.startswith('//'):
            paths.add(normalize_path(urljoin(path, imp)))
    return paths
