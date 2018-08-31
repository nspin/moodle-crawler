# Moodle Crawler

Archive documents before you lose access to Moodle

## How It Works

The crawler fetches documents recursively using the whitelist found in `myydle/filter.py`. I decided that using just a blacklist was too dangerous.
The whitelist may be missing paths that are present in your Moodle but not mine.
Paths which are neither whitelisted nor blacklisted are logged with `[unhandled path] ...` and ignored.

Paths fetched, along with their result (redirect, failure status code, success with content type and content hash) are stored in `CRAWL_DIR/db.sqlite` and content-addressed blobs are stored in `CRAWL_DIR/blobs`, where `CRAWL_DIR` is passed as a command line argument.

After the crawl, HTML and CSS documents are patched to refer to one another, and all blobs are moved into `ARCHIVE_DIR/files` with sanitized names. `ARCHIVE_DIR/index.html` redirects to the entry point within `ARCHIVE_DIR/files` using `<meta http-equiv...>`.

Once `ARCHIVE_DIR` is complete, you can delete `CRAWL_DIR`, or you can keep it just in case.

Browse the archive by opening `ARCHIVE_DIR/index.html` in a browser.

## Usage

```
./myydle.sh [-h] [--crawl-dir CRAWL_DIR] [--archive-dir ARCHIVE_DIR] username password

positional arguments:
  username
  password

optional arguments:
  -h, --help            show this help message and exit
  --crawl-dir CRAWL_DIR
  --archive-dir ARCHIVE_DIR
```

## Dependencies

Tested with Python 3.6.4 and Python 3.4.4

Requires `requests` and `beautifulsoup4`
