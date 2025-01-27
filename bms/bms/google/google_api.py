from bms.web_manager import oauth
import os, requests

GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")
GOOGLE_DISCOVERY_URL = os.environ.get("GOOGLE_DISCOVERY_URL")


api_url = requests.get(GOOGLE_DISCOVERY_URL).json()

google = oauth.register(
    name='google',
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    authorize_url=api_url['authorization_endpoint'],
    authorize_params=None,
    access_token_url=api_url['token_endpoint'],
    access_token_params=None,
    refresh_token_url=None,
    refresh_token_params=None,
    base_url='https://www.googleapis.com/oauth2/v1/',
    client_kwargs={'scope': 'openid profile email'},
    jwks_uri=api_url['jwks_uri']
)