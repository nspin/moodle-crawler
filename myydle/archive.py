import os
import os.path
import re
import string
import shutil
import itertools
import mimetypes
import urllib.parse
from bs4 import BeautifulSoup

from myydle.storage import Storage
from myydle.normalize import normalize_path, get_normalized_path_with_fragment

def guess_all_extensions(content_type):
    # for overriding order
    overrides = {
        'text/html': '.html',
        }
    # these aren't inluded in the mimtypes module
    extras = {
        'application/x-javascript': '.js',
        'audio/mp3': '.mp3',
        'audio/mp4': '.mp4', # moodle's fault
        'audio/wav': '.wav',
        'text/rtf': '.rtf',
        'application/vnd.openxmlformats-officedocument.presentationml.presentation': '.pptx',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document': '.docx',
        }
    mty = content_type.split(';', 1)[0]
    exts = []
    if mty in overrides:
        exts.append(overrides[mty])
    exts.extend(mimetypes.guess_all_extensions(mty))
    if mty in extras:
        exts.append(extras[mty])
    if not exts:
        raise Exception('could not guess extension of', content_type)
    return exts

FNAME_MAX = 64

def derive_fname(path, exts):
    last = urllib.parse.unquote(path.split('?')[0].split('/')[-1])
    suffix = exts[0]
    for ext in exts:
        if last.endswith(ext):
            last = last[:-len(ext)]
            suffix = ext
            break
    return sanitize((last or 'x')[:(FNAME_MAX - len(suffix))]) + suffix

def sanitize(s):
    ALLOWED = string.ascii_letters + string.digits + '-_'
    return ''.join(
        (c if c in ALLOWED else '-') for c in s
        )

class Resolver(object):

    def __init__(self, st):
        self.st = st
        self.assocs = {}

        fnames = set()
        for row in st.get_all_rows():
            if row.content_type is not None:
                base = derive_fname(row.normalized_path, guess_all_extensions(row.content_type))
                for i in itertools.count(0):
                    fname = 'x{:x}-{}'.format(i, base)
                    if fname not in fnames:
                        self.assocs[row.normalized_path] = fname
                        fnames.add(fname)
                        break

    def resolve_path(self, any_path):
        path = normalize_path(any_path)
        while True:
            row = self.st.get_row_by_path(path)
            if row is None:
                return None
            if row.external_location is not None:
                return row.external_location
            if row.content_type is not None:
                return self.assocs[row.normalized_path]
            if row.failure_status_code is not None:
                return 'HTTP_{}'.format(row.failure_status_code, sanitize(row.normalized_path))
            path = row.internal_location

    def resolve_url(self, url):
        path, fragment = get_normalized_path_with_fragment(url)
        if path is None:
            return url
        resolved = self.resolve_path(path)
        if resolved is None:
            return url
        return resolved + fragment

def patch_soup(resolver, soup):
    for tag in soup.find_all('script'):
        tag.extract()
    for tag in soup.find_all('noscript'):
        tag.replace_with_children()
    for tag in soup.find_all('link'):
        if 'href' in tag.attrs:
            tag.attrs['href'] = resolver.resolve_url(tag.attrs['href'])
    for tag in soup.find_all('img'):
        if 'src' in tag.attrs:
            tag.attrs['src'] = resolver.resolve_url(tag.attrs['src'])
    for tag in soup.find_all('a'):
        if 'href' in tag.attrs:
            tag.attrs['href'] = resolver.resolve_url(tag.attrs['href'])

def patch_html(resolver, doc):
    soup = BeautifulSoup(doc, 'html.parser')
    patch_soup(resolver, soup)
    return str(soup)

import_re = re.compile(r'@import url\((?P<imp>[^\)]*)\)')

def patch_css(resolver, path, css):
    def repl(m):
        imp = m.group('imp')
        if re.compile('(https?:)?//').match(imp) is None:
            new = resolver.resolve_path(urllib.parse.urljoin(path, imp))
        else:
            new = imp
        return '@import url({})'.format(new)
    return import_re.sub(repl, css)

def archive(st, out_dir):

    os.makedirs(out_dir, exist_ok=True)

    resolver = Resolver(st)

    for row in st.get_all_rows():
        if row.content_type is not None:
            fname = resolver.resolve_path(row.normalized_path)
            fpath = os.path.join(out_dir, fname)
            if row.content_type.startswith('text/html'):
                with open(fpath, 'w') as f:
                    f.write(patch_html(resolver,
                        st.get_blob(row.content_hash, binary=False)
                        ))
            elif row.content_type.startswith('text/css'):
                with open(fpath, 'w') as f:
                    f.write(patch_css(resolver, row.normalized_path,
                        st.get_blob(row.content_hash, binary=False)
                        ))
            else:
                shutil.copy(st.blob_path(row.content_hash), fpath)

    return resolver.resolve_path('/')
