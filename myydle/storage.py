import os
import os.path
import hashlib
import sqlite3
import itertools
from binascii import hexlify
from collections import namedtuple
from urllib.parse import unquote

from myydle.normalize import normalize_path

# store hashes hex-encoded out of lazyiness
create_table = '''
    create table if not exists paths (
        path varchar primary key,
        internal_location_path varchar,
        external_location varchar,
        status_code integer,
        content_type varchar,
        hash char(64)
    )
    '''

class Row(object):

    def __init__(self, path,
            internal_location_path=None,
            external_location=None,
            status_code=None,
            content_type=None,
            hash=None,
            ):
        self.path = normalize_path(path)
        self.internal_location_path = internal_location_path
        self.external_location = external_location
        self.status_code = status_code
        self.content_type = content_type
        self.hash = hash

    def __iter__(self):
        yield self.path
        yield self.internal_location_path
        yield self.external_location
        yield self.status_code
        yield self.content_type
        yield self.hash

    _fields = ('path', 'internal_location_path', 'external_location', 'status_code', 'content_type', 'hash')

class Storage():

    def __init__(self, db, blob_dir):
        self.blob_dir = blob_dir
        os.makedirs(self.blob_dir, exist_ok=True)
        self.conn = sqlite3.connect(db)
        self.conn.execute(create_table)

    def close(self):
        self.conn.close()

    # assumes no loops
    def resolve_path(self, path):
        while True:
            row = self.get_row_by_path(normalize_path(path))
            if row is None or row.internal_location_path is None:
                return row
            path = row.internal_location_path

    # assumes no loops
    def unresolve_path(self, path):
        def go(p):
            for row in self.get_rows_by_internal_location_path(p):
                yield row.path
                yield from go(row.path)
        return frozenset(go(normalize_path(path)))

    def put_row(self, row):
        q = 'insert or replace into paths ({}) values ({})'.format(','.join(Row._fields), ','.join('?' for _ in Row._fields))
        cur = self.conn.cursor()
        cur.execute(q, tuple(row))
        self.conn.commit()

    def get_row_by_path(self, path):
        cur = self.conn.cursor()
        it = cur.execute('select * from paths where path = ?', (normalize_path(path),))
        try:
            return Row(*next(it))
        except StopIteration:
            return None

    def get_rows_by_path_pred(self, pred):
        for row in self.get_all_rows():
            if pred(row.path):
                yield row

    def get_all_rows(self):
        cur = self.conn.cursor()
        it = cur.execute('select * from paths')
        return itertools.starmap(Row, it)

    def blob_path(self, hash):
        return os.path.join(self.blob_dir, hash)

    def put_blob(self, blob):
        h = hashlib.new('sha256')
        h.update(blob)
        hash = hexlify(h.digest()).decode('ascii')
        path = self.blob_path(hash)
        if not os.path.isfile(path):
            with open(path, 'wb') as f:
                f.write(blob)
        return hash

    def get_blob(self, hash, binary=True):
        path = self.blob_path(hash)
        if os.path.isfile(path):
            mode = 'rb' if binary else 'r'
            with open(path, mode) as f:
                return f.read()
        else:
            return None
