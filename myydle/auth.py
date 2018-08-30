def do_auth(session, cookie_key, cookie_value):
    session.cookies[cookie_key] = cookie_value
