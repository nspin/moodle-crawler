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

for r in st.get_all_rows():
    if r.internal_location is not None:
        if r.internal_location != normalize_path(r.internal_location):
            st.put_row(Row(
                normalized_path=r.normalized_path,
                internal_location=normalize_path(r.internal_location),
                ))

