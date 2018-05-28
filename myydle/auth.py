import re
import html

action_re = re.compile(r'<form action="([^"]*)" method="post">')
relay_state_re = re.compile('<input type="hidden" name="RelayState" value="([^"]*)"/>')
saml_response_re = re.compile('<input type="hidden" name="SAMLResponse" value="([^"]*)"/>')

def do_auth(session, username, password):

    session.get('https://moodle.carleton.edu'
        ).raise_for_status()

    session.get('https://moodle.carleton.edu/auth/shibboleth/index.php'
        ).raise_for_status()

    session.post('https://login.carleton.edu/idp/profile/SAML2/Redirect/SSO?execution=e1s1', data = {
        'shib_idp_ls_exception.shib_idp_session_ss': '',
        'shib_idp_ls_success.shib_idp_session_ss': 'false',
        'shib_idp_ls_value.shib_idp_session_ss': '',
        'shib_idp_ls_exception.shib_idp_persistent_ss': '',
        'shib_idp_ls_success.shib_idp_persistent_ss': 'false',
        'shib_idp_ls_value.shib_idp_persistent_ss': '',
        'shib_idp_ls_supported': '',
        '_eventId_proceed': '',
        }).raise_for_status()

    resp = session.post('https://login.carleton.edu/idp/profile/SAML2/Redirect/SSO?execution=e1s2', data={
        'j_username': username,
        'j_password': password,
        '_eventId_proceed': '',
        })
    resp.raise_for_status()

    session.post(html.unescape(action_re.search(resp.text)[1]), data={
        'RelayState': html.unescape(relay_state_re.search(resp.text)[1]),
        'SAMLResponse': html.unescape(saml_response_re.search(resp.text)[1]),
        }).raise_for_status()
