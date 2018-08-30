import re
import html
import urllib.parse
from bs4 import BeautifulSoup
from requests import PreparedRequest

from myydle.filter import keep
from myydle.normalize import normalize_path, get_normalized_path

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
        for url in urls:
            if url is not None and len(url) > 0:
                path = get_normalized_path(url)
                if path is not None:
                    yield path
    ret = set()
    for path in paths(yes()):
        ret.add(path)
    for path in paths(maybe()):
        if keep(path):
            ret.add(path)
    return ret

import_re = re.compile(r'@import url\(([^\)]*)\)')

def scrape_css(path, css):
    paths = set()
    for m in import_re.finditer(css):
        imp = m.groups(1)
        if re.compile('(https?:)?//').match(imp) is None:
            paths.add(normalize_path(urllib.parse.urljoin(path, imp)))
    return paths
