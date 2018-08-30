import os
import os.path
import hashlib
import sqlite3
import itertools
from binascii import hexlify

create_table = '''
    create table if not exists paths (
        normalized_path varchar primary key,
        internal_location varchar, /* normalized path */
        external_location varchar, /* url */
        failure_status_code integer,
        content_type varchar,
        content_hash char(64) /* hex-encoded out of lazyiness */
    )
    '''

class Row(object):

    def __init__(self, normalized_path,
            internal_location=None,
            external_location=None,
            failure_status_code=None,
            content_type=None,
            content_hash=None,
            ):
        self.normalized_path = normalized_path
        self.internal_location = internal_location
        self.external_location = external_location
        self.failure_status_code = failure_status_code
        self.content_type = content_type
        self.content_hash = content_hash

    def __iter__(self):
        for f in Row._fields:
            yield getattr(self, f)

    _fields = ('normalized_path', 'internal_location', 'external_location', 'failure_status_code', 'content_type', 'content_hash')

class Storage():

    def __init__(self, db, blob_dir):
        self.blob_dir = blob_dir
        os.makedirs(self.blob_dir, exist_ok=True)
        self.conn = sqlite3.connect(db)
        self.conn.execute(create_table)

    def close(self):
        self.conn.close()

    # assumes no loops
    def resolve_path(self, normalized_path):
        while True:
            row = self.get_row_by_path(normalized_path)
            if row is None or row.internal_location is None:
                return row
            normalized_path = row.internal_location

    # assumes no loops
    def unresolve_path(self, normalized_path):
        def go(p):
            for row in self.get_rows_by_internal_location(p):
                yield row.normalized_path
                yield from go(row.normalized_path)
        return frozenset(go(normalized_path))

    def put_row(self, row):
        q = 'insert or replace into paths ({}) values ({})'.format(','.join(Row._fields), ','.join('?' for _ in Row._fields))
        cur = self.conn.cursor()
        cur.execute(q, tuple(row))
        self.conn.commit()

    def get_row_by_path(self, normalized_path):
        cur = self.conn.cursor()
        it = cur.execute('select * from paths where normalized_path = ?', (normalized_path,))
        try:
            return Row(*next(it))
        except StopIteration:
            return None

    def get_rows_by_path_where(self, pred):
        for row in self.get_all_rows():
            if pred(row.normalized_path):
                yield row

    def get_all_rows(self):
        cur = self.conn.cursor()
        it = cur.execute('select * from paths')
        return itertools.starmap(Row, it)

    def blob_path(self, content_hash):
        return os.path.join(self.blob_dir, content_hash)

    def put_blob(self, blob):
        h = hashlib.new('sha256')
        h.update(blob)
        content_hash = hexlify(h.digest()).decode('ascii')
        path = self.blob_path(content_hash)
        if not os.path.isfile(path):
            with open(path, 'wb') as f:
                f.write(blob)
        return content_hash

    def get_blob(self, content_hash, binary=True):
        path = self.blob_path(content_hash)
        if os.path.isfile(path):
            mode = 'rb' if binary else 'r'
            with open(path, mode) as f:
                return f.read()
        else:
            return None
