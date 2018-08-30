import re
import unicodedata
import urllib.parse

def get_normalized_path(url):
    m = re.compile('(https?:)?//moodle.carleton.edu(?P<path>.*)').fullmatch(url)
    if m is not None:
        return normalize_path(m.group('path'))

def get_normalized_path_with_fragment(url):
    m = re.compile('(https?:)?//moodle.carleton.edu(?P<path>.*)').fullmatch(url)
    if m is None:
        return None, None
    else:
        return normalize_path_with_fragment(m.group('path'))

def normalize_path(path):
    return normalize_path_with_fragment(path)[0]

def normalize_path_with_fragment(path):
    query = fragment = ''
    if '#' in path:
        path, fragment = path.split('#', 1)
    if '?' in path:
        path, query = path.split('?', 1)

    path = urllib.parse.quote(
        unicodedata.normalize('NFC', urllib.parse.unquote(path)),
        # "~:/?#[]@!$&'()*+,;="
        '/'
        )

    if path == '':
        path = '/'

    output, part = [], None
    for part in path.split('/')[1:]:
        if part in ['', '.']:
            pass
        elif part == '..':
            if len(output) > 1:
                output.pop()
        else:
            output.append(part)
    if part in ['', '.', '..']:
        output.append('')
    path = '/' + '/'.join(output)

    if query:
        path += '?' + '&'.join(sorted(
            '='.join(
                urllib.parse.quote(
                    unicodedata.normalize('NFC', urllib.parse.unquote(t)),
                    # "~:/?#[]@!$'()*+,;="
                    ''
                    )
                for t in q.split('=', 1)
                )
            for q in query.split('&')
            ))

    return path, ('#' + fragment if fragment else '')
