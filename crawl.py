from requests import Session

from myydle.filter import keep
from myydle.uniq import UniQ
from myydle.auth import do_auth
from myydle.storage import Storage, Row
from myydle.scrape import scrape_html, scrape_css
from myydle.normalize import normalize_url, normalize_path

from config import USERNAME, PASSWORD

URL_PREFIX = 'https://moodle.carleton.edu'

def is_redirect(status_code):
    return status_code in (301, 302, 303, 307, 308)

def internal_path(url):
    if url.startswith(URL_PREFIX):
        return url[len(URL_PREFIX):]

st = Storage('db.sqlite', 'blobs')
s = Session()
do_auth(s, USERNAME, PASSWORD)

q = UniQ()
q.en('/')

while not q.is_empty():

    path = q.de()
    # print(path)
    assert path == normalize_path(path)

    row = st.get_row_by_path(path)
    if row is None:
        r = s.get(URL_PREFIX + path, allow_redirects=False)
        assert r.url == URL_PREFIX + path
        assert not is_redirect(r.status_code) or r.headers['Location'] != 'https://moodle.carleton.edu/login/index.php'

        if is_redirect(r.status_code):
            location = r.headers['Location']
            assert 'login' not in location
            internal_location = internal_path(location)
            if internal_location is None:
                row = Row(path, external_location=location)
            else:
                row = Row(path, internal_location=normalize_path(internal_location))
        elif r.status_code != 200:
            row = Row(path, failure_status_code=r.status_code)
            print('[http {}]'.format(r.status_code), path)
        else:
            content_type = r.headers['content-type']
            content_hash = st.put_blob(r.content)
            row = Row(path, content_type=content_type, content_hash=content_hash)
        st.put_row(row)

    if row.internal_location is not None:
        q.en(row.internal_location)
    elif row.content_type is not None:
        if row.content_type.startswith('text/html'):
            doc = st.get_blob(row.content_hash, binary=False)
            for p in scrape_html(doc):
                q.en(p)
        elif row.content_type.startswith('text/css'):
            doc = st.get_blob(row.content_hash, binary=False)
            for p in scrape_css(path, doc):
                q.en(p)
