from requests import Session

from myydle.auth import do_auth
from myydle.filter import keep
from myydle.normalize import get_normalized_path, normalize_path
from myydle.scrape import scrape_html, scrape_css
from myydle.storage import Row
from myydle.uniq import UniQ

URL_PREFIX = 'https://moodle.carleton.edu'

def is_redirect(status_code):
    return status_code in (301, 302, 303, 307, 308)

def ensure_not_logged_out(resp):
    assert not is_redirect(resp.status_code) or resp.headers['Location'] != 'https://moodle.carleton.edu/login/index.php'

def crawl(st, cookie_key, cookie_value):

    sess = Session()
    do_auth(sess, cookie_key, cookie_value)

    q = UniQ()
    q.en('/')

    while not q.is_empty():

        path = q.de()
        assert path == normalize_path(path)

        row = st.get_row_by_path(path)
        if row is None:
            r = sess.get(URL_PREFIX + path, allow_redirects=False)
            ensure_not_logged_out(r)

            if is_redirect(r.status_code):
                location = r.headers['Location']
                internal_location = get_normalized_path(location)
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
