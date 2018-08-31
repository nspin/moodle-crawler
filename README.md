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

A command line interface is provided in `myydle.cli`.
`myydle.sh` is a shell script for convenience that calls that module.

You can either provide your username and password, or an appropriate session cookie.
If your account has 2FA enabled, you will need to use the cookie route.
The cookie argument is the value of the `MoodleSession` cookie.
It should be a string of letters.
You can get a cookie by logging in in your browser, and copying it using the developer tools in your browser.
Ask me if you need help.

```
./myydle.sh [-h] [-c COOKIE] [-u USERNAME] [-p PASSWORD]
              [--crawl-dir CRAWL_DIR] [--archive-dir ARCHIVE_DIR]

optional arguments:
  -h, --help            show this help message and exit
  -c COOKIE, --cookie COOKIE
                        "MoodleSession" cookie
  -u USERNAME, --username USERNAME
  -p PASSWORD, --password PASSWORD
  --crawl-dir CRAWL_DIR
  --archive-dir ARCHIVE_DIR
```

## Dependencies

Tested with Python 3.6.4 and Python 3.4.4

Requires `requests` and `beautifulsoup4`
