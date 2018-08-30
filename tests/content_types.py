from myydle.storage import Storage
import mimetypes

st = Storage('db.sqlite', 'blobs')

s = set()

for r in st.get_all_rows():
    if r.content_type is not None:
        s.add(r.content_type.split(';', 1)[0])

for x in sorted(s):
    print(x, mimetypes.guess_extension(x))
