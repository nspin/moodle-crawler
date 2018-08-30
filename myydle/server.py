import os.path
from urllib.parse import unquote
from flask import Flask, Response, g, request, redirect, send_file

from myydle.storage import Storage
from myydle.normalize import normalize_path

REMOTE_URL_PREFIX = 'https://moodle.carleton.edu'

app = Flask(__name__)

@app.route('/', defaults={'_': ''})
@app.route('/<path:_>')
def handle(_):
    st = get_st()
    row = st.get_row_by_path(just_path())
    print(just_path(), row)
    if row is None:
        return 'not found: "{}"'.format(just_path()), 404
    if row.internal_location is not None:
        return redirect(row.internal_location)
    elif row.external_location is not None:
        return redirect(row.external_location)
    elif row.content_hash is not None:
        mimetype = row.content_type.split(';', 1)[0]
        if mimetype in ('text/html', 'text/css', 'text/javascript'):
            content = st.get_blob(row.content_hash, binary=False).replace(REMOTE_URL_PREFIX, '')
            return Response(content, mimetype=mimetype)
        else:
            return send_file(st.blob_path(row.content_hash), mimetype=mimetype)
    elif row.failure_status_code is not None:
        return str(row), row.failure_status_code

def just_path():
    url = request.url.replace('%2F', '/') # hack: different quoting behavior between crawler and flask
    assert url.startswith(request.url_root)
    path = url[len(request.url_root) - 1:]
    return normalize_path(path)

def get_st():
    if not hasattr(g, 'st'):
        g.st = Storage(
            os.path.join(app.config['CRAWL_DIR'], 'db.sqlite'),
            os.path.join(app.config['CRAWL_DIR'], 'blobs'),
            )
    return g.st

@app.teardown_appcontext
def close_st(error):
    if hasattr(g, 'st'):
        g.st.close()

def main():
    parser = ArgumentParser()
    parser.add_argument('crawl_dir')
    args = parser.parse_args()

    app.config['CRAWL_DIR'] = args.crawl_dir

    app.run(
        host='127.0.0.1',
        port=13337,
        debug=True,
        )

if __name__ == '__main__':
    main()
