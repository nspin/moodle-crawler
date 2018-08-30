from myydle.storage import Storage
from myydle.normalize import normalize_path

st = Storage('db.sqlite', 'blobs')

for r in st.get_all_rows():
    if r.normalized_path != normalize_path(r.normalized_path):
        print(r.normalized_path)
        print(normalize_path(r.normalized_path))
        break
