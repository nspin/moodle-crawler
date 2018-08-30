import os
import os.path
import re
import string
import shutil
import mimetypes
import urllib.parse
from bs4 import BeautifulSoup

from myydle.storage import Storage
from myydle.normalize import get_normalized_path_with_fragment

def sanitize_path(path):
    ALLOWED = string.ascii_letters + string.digits + '-._'
    return 'X' + ''.join(
        (c if c in ALLOWED else '-') for c in path
        )

def guess_extension(content_type):
    mty = content_type.split(';', 1)[0]
    overrides = {
        'text/html': '.html',
        }
    if mty in overrides:
        return overrides[mty]
    ext = mimetypes.guess_extension(mty)
    if ext is not None:
        return ext
    # these aren't inluded in the mimtypes module
    extras = {
        'application/x-javascript': '.js',
        'audio/mp3': '.mp3',
        'audio/wav': '.wav',
        'text/rtf': '.rtf',
        }
    return extras[mty]

def resolve_path(st, path):
    while True:
        row = st.get_row_by_path(path)
        if row is None:
            return None
        if row.external_location is not None:
            return row.external_location
        if row.content_type is not None:
            return sanitize_path(path) + guess_extension(row.content_type)
        if row.failure_status_code is not None:
            return 'HTTP_{}_{}'.format(row.failure_status_code, sanitize_path(path))
        path = row.internal_location

def resolve_url(st, url):
    path, fragment = get_normalized_path_with_fragment(url)
    if path is None:
        return url
    resolved = resolve_path(st, path)
    if resolved is None:
        return url
    return resolved + fragment

def patch_soup(st, soup):
    for tag in soup.find_all('script'):
        tag.extract()
    for tag in soup.find_all('link'):
        if 'href' in tag.attrs:
            tag.attrs['href'] = resolve_url(st, tag.attrs['href'])
    for tag in soup.find_all('img'):
        if 'src' in tag.attrs:
            tag.attrs['src'] = resolve_url(st, tag.attrs['src'])
    for tag in soup.find_all('a'):
        if 'href' in tag.attrs:
            tag.attrs['href'] = resolve_url(st, tag.attrs['href'])

def patch_html(st, doc):
    soup = BeautifulSoup(doc, 'html.parser')
    patch_soup(st, soup)
    return str(soup)

import_re = re.compile(r'@import url\((?P<imp>[^\)]*)\)')

def patch_css(st, path, css):
    def repl(m):
        imp = m.group('imp')
        if re.compile('(https?:)?//').match(imp) is None:
            new = resolve_path(st, urllib.parse.urljoin(path, imp))
        else:
            new = imp
        return '@import url({})'.format(new)
    return import_re.sub(repl, css)

def archive(st, out_dir):

    os.makedirs(out_dir, exist_ok=True)

    for row in st.get_all_rows():
        if row.content_type is not None:
            fname = sanitize_path(row.normalized_path) + guess_extension(row.content_type)
            fpath = os.path.join(out_dir, fname)
            if row.content_type.startswith('text/html'):
                with open(fpath, 'w') as f:
                    f.write(patch_html(st,
                        st.get_blob(row.content_hash, binary=False)
                        ))
            elif row.content_type.startswith('text/css'):
                with open(fpath, 'w') as f:
                    f.write(patch_css(st, row.normalized_path,
                        st.get_blob(row.content_hash, binary=False)
                        ))
            else:
                shutil.copy(st.blob_path(row.content_hash), fpath)
