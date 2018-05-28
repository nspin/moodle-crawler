from requests import Session

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

q = UniQ()
q.en('/')
# q.en('/lib/requirejs.php/1522770736/core/first.js')
# q.en('/lib/requirejs.php/1522770736/core/event.js')
# q.en('/lib/javascript.php/1522770736/lib/requirejs/jquery-private.js')
# q.en('/lib/javascript.php/1522770736/lib/jquery/jquery-3.1.0.min.js')
while not q.is_empty():
    path = q.de()
    print(path)
    assert path == normalize_path(path)
    row = st.get_row_by_path(path)
    if row is None:
        while True:
            r = s.get(URL_PREFIX + path, allow_redirects=False)
            assert r.url == URL_PREFIX + path
            if not is_redirect(r.status_code) or r.headers['Location'] != 'https://moodle.carleton.edu/login/index.php':
                break
            s = Session()
            print('AUTH')
            do_auth(s, USERNAME, PASSWORD)
        if is_redirect(r.status_code):
            location = r.headers['Location']
            if 'login' in location:
                print('FUCK:', path, location)
            internal_location_path = internal_path(location)
            if internal_location_path is None:
                row = Row(path, external_location=location)
            else:
                row = Row(path, internal_location_path=internal_location_path)
        elif r.status_code != 200:
            row = Row(path, status_code=r.status_code)
            print('BAD:', path, r.status_code)
        else:
            content_type = r.headers['content-type']
            hash = st.put_blob(r.content)
            row = Row(path, content_type=content_type, hash=hash)
        st.put_row(row)
    if row.internal_location_path is not None:
        q.en(row.internal_location_path)
    elif row.content_type is not None:
        if row.content_type.startswith('text/html'):
            doc = st.get_blob(row.hash, binary=False)
            for p in scrape_html(doc):
                q.en(p)
        elif row.content_type.startswith('text/css'):
            doc = st.get_blob(row.hash, binary=False)
            for p in scrape_css(path, doc):
                q.en(p)
