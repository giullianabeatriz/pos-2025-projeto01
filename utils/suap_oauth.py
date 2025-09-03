from requests_oauthlib import OAuth2Session
from config import Config

def make_suap_session(token=None, state=None):
    return OAuth2Session(
        client_id=Config.SUAP_CLIENT_ID,
        redirect_uri=Config.SUAP_REDIRECT_URI,
        token=token,
        state=state,
        scope=["identificacao", "email"]
    )