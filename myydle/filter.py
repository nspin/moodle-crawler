import re

# using re.fullmatch
white_list = [

    '/',
    '/my/',

    '/pluginfile\.php/.+', # bold

    '/course/index\.php',
    '/course/view\.php\?id=[0-9]+(&section(id)?=[0-9]+)?',

    '/mod/assign/view\.php\?(forceview=1&)?id=[0-9]+',
    '/mod/attendance/view\.php\?(forceview=1&)?id=[0-9]+',
    '/mod/choice/view\.php\?(forceview=1&)?id=[0-9]+',
    '/mod/feedback/print\.php\?id=[0-9]+',
    '/mod/feedback/view\.php\?(forceview=1&)?id=[0-9]+',
    '/mod/folder/view\.php\?(forceview=1&)?id=[0-9]+',
    '/mod/forum/discuss\.php\?d=[0-9]+(&parent=[0-9]+)?',
    '/mod/forum/post\.php\?reply=[0-9]+',
    '/mod/forum/view\.php\?(forceview=1&)?f=[0-9]+',
    '/mod/forum/view\.php\?(forceview=1&)?id=[0-9]+',
    '/mod/lesson/view\.php\?(forceview=1&)?id=[0-9]+',
    '/mod/lti/launch\.php\?(forceview=1&)?id=[0-9]+',
    '/mod/lti/view\.php\?(forceview=1&)?id=[0-9]+',
    '/mod/page/view\.php\?(forceview=1&)?id=[0-9]+',
    '/mod/questionnaire/view\.php\?(forceview=1&)?id=[0-9]+',
    '/mod/quiz/review\.php\?attempt=[0-9]+&cmid=[0-9]+(&showall=0)?(&page=[0-9]+)?',
    '/mod/quiz/view\.php\?(forceview=1&)?id=[0-9]+',
    '/mod/resource/view\.php\?(forceview=1&)?id=[0-9]+',
    '/mod/scheduler/view\.php\?(forceview=1&)?id=[0-9]+',
    '/mod/scorm/view\.php\?(forceview=1&)?id=[0-9]+',
    '/mod/url/view\.php\?(forceview=1&)?id=[0-9]+',

    '/blocks/completionstatus/details\.php\?course=[0-9]+',
    '/blocks/iclicker/registration.php',

    '/\?redirect=0',

    '/brokenfile.php',

    ]

# using re.search
# some excludes taken from https://github.com/central-queensland-uni/moodle-tool_crawler/blob/master/settings.php
black_list = [

    '[?&]action=', # too aggressive?
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

    '/my/\?myoverviewtab=courses',

    '/course/index\.php\?categoryid=[0-9]+',
    '/course/recent\.php\?id=[0-9]+',

    '/mod/attendance/view\.php\?curdate=[0-9]+&id=[0-9]+',
    '/mod/attendance/view\.php\?id=[0-9]+&mode=[0-9]+',
    '/mod/attendance/view\.php\?id=[0-9]+&view=[0-9]+',
    '/mod/forum/search\.php\?id=[0-9]+',
    '/mod/questionnaire/complete\.php\?id=[0-9]+',

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
    print('[unhandled path]', path)
    return False
