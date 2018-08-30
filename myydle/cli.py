import os
from argparse import ArgumentParser

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
    parser.add_argument('cookie_key')
    parser.add_argument('cookie_value')
    parser.add_argument('--crawl-dir', default='crawl')
    parser.add_argument('--archive-dir', default='archive')
    args = parser.parse_args()

    st = Storage(
        os.path.join(args.crawl_dir, 'db.sqlite'),
        os.path.join(args.crawl_dir, 'blobs'),
        )

    os.makedirs(args.archive_dir, exist_ok=True)

    print('crawling')
    crawl(st, args.cookie_key, args.cookie_value)

    print('archiving')
    archive(st, os.path.join(args.archive_dir, 'files'))

    with open(os.path.join(args.archive_dir, 'index.html'), 'w') as f:
        f.write(INDEX)

    print('archive complete')
    print('{} contains the raw moodle archive. you can remove it, or keep it just in case.'.format(args.crawl_dir))
    print('{} contains a browsable version of your moodle archive. start at {}/index.html.'.format(args.archive_dir, args.archive_dir))

if __name__ == '__main__':
    main()
