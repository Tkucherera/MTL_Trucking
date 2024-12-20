
import os
from pathlib import Path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow


BASE_DIR = Path(__file__).parent


class GoogleApisAuthenticate(object):
    def __init__(self):
        self.SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/documents']
        self.creds = self._authenticate()

    def _authenticate(self):
        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        # TODO There is potential of this Error google.auth.exceptions.RefreshError  - try to delete the token.json file and reauthentiate
        if os.path.exists(os.path.join(BASE_DIR, "token.json")):
            creds = Credentials.from_authorized_user_file(os.path.join(BASE_DIR, "token.json"), self.SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    os.path.join(BASE_DIR, "credentials.json"), self.SCOPES
                )
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(os.path.join(BASE_DIR, "token.json"), "w") as token:
                token.write(creds.to_json())
        if not creds:
            raise Exception('Failed to authenticate')
        return creds