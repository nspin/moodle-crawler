import os
import sys
from argparse import ArgumentParser
from requests import Session

from myydle.auth import do_auth
from myydle.crawl import crawl
from myydle.archive import archive
from myydle.storage import Storage

INDEX = '''
<!DOCTYPE html>
<html>    
  <head>      
    <title>redirecting...</title>      
    <meta http-equiv="refresh" content="0;URL='files/X-my-.html'" />    
  </head>    
  <body>
    <p>start here: <a href="files/X-my-.html">files/X-my-.html</a></p>
  </body>  
</html>    
'''

def main():
    parser = ArgumentParser()
    parser.add_argument('-c', '--cookie', help='"MoodleSession" cookie')
    parser.add_argument('-u', '--username')
    parser.add_argument('-p', '--password')
    parser.add_argument('--crawl-dir', default='crawl')
    parser.add_argument('--archive-dir', default='archive')
    args = parser.parse_args()

    st = Storage(
        os.path.join(args.crawl_dir, 'db.sqlite'),
        os.path.join(args.crawl_dir, 'blobs'),
        )

    os.makedirs(args.archive_dir, exist_ok=True)

    sess = Session()

    if args.cookie is not None:
        sess.cookies['MoodleSession'] = args.cookie
    else:
        if args.username is None or args.password is None:
            sys.exit('must supply cookie or both username and password')
        print('authenticating')
        do_auth(sess, args.username, args.password)

    print('crawling')
    crawl(st, sess)

    print('archiving')
    archive(st, os.path.join(args.archive_dir, 'files'))

    with open(os.path.join(args.archive_dir, 'index.html'), 'w') as f:
        f.write(INDEX)

    print('archive complete')
    print('{} contains the raw moodle archive. you can remove it, or keep it just in case.'.format(args.crawl_dir))
    print('{} contains a browsable version of your moodle archive. start at {}/index.html.'.format(args.archive_dir, args.archive_dir))

if __name__ == '__main__':
    main()
