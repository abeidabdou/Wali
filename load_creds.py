import os
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from dotenv import load_dotenv

load_dotenv()

SCOPES = ['https://www.googleapis.com/auth/generative-language.retriever']

def load_creds():
    creds = None

    client_secret_content = os.getenv('CLIENT_SECRET_JSON')
    if client_secret_content:
        client_secret_data = json.loads(client_secret_content)
    else:
        raise ValueError("CLIENT_SECRET_JSON environment variable is not set")

    token_content = os.getenv('TOKEN_JSON')
    if token_content:
        creds = Credentials.from_authorized_user_info(json.loads(token_content), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_config(client_secret_data, SCOPES)
            creds = flow.run_local_server(port=0)

        os.environ['TOKEN_JSON'] = creds.to_json()

    return creds
