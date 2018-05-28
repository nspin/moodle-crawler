import re

# using re.fullmatch
white_list = [
    # '[^?]*/view\.php.*',
    # '/pluginfile\.php.*',
    # '[^?]*\.css/?\??.*',
    # '[^?]*\.js/?\??.*',
    # '[^?]*?.*css=?.*',
    # '[^?]*?.*js=?.*',
    '.*',
    ]

# using re.search
# some excludes taken from https://github.com/central-queensland-uni/moodle-tool_crawler/blob/master/settings.php
black_list = [
    # '[?&]action=',
    '[?&]sesskey=',
    '[?&]time=',
    '[?&]lang=',
    '[?&]useridlistid=',

    'login',

    'grading',
    '/admin',
    '/blog',
    '/badges',
    '/blocks/quickmail',
    '/calendar',
    '/enrol',
    '/help/',
    '/login',
    '/message',
    '/report',
    '/rss',
    '/user',
    '/tag/',

    ]

_white_list = [ re.compile(r) for r in white_list ]
_black_list = [ re.compile(r) for r in black_list ]

# given a normalized path, do we care about it?
def keep(path):
    for r in _black_list:
        if r.search(path) is not None:
            return False
    for r in _white_list:
        if r.fullmatch(path) is not None:
            return True
    return False
