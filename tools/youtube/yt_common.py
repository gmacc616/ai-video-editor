"""Shared YouTube OAuth helpers.

Secrets live outside OneDrive in %USERPROFILE%\\.yt-analytics\\:
  client_secret.json  - OAuth "Desktop app" client downloaded from Google Cloud
  token.json          - created by yt_auth.py after you sign in
"""
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SECRETS_DIR = Path.home() / ".yt-analytics"
CLIENT_SECRET = SECRETS_DIR / "client_secret.json"
TOKEN = SECRETS_DIR / "token.json"

# Read-only. No upload/manage scopes.
SCOPES = [
    "https://www.googleapis.com/auth/youtube.readonly",
    "https://www.googleapis.com/auth/yt-analytics.readonly",
]


def get_credentials(interactive: bool = False) -> Credentials:
    creds = None
    if TOKEN.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN), SCOPES)
    if creds and creds.valid:
        return creds
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        if not interactive:
            raise SystemExit("Not signed in. Run: py tools\\youtube\\yt_auth.py")
        if not CLIENT_SECRET.exists():
            raise SystemExit(f"Missing {CLIENT_SECRET} - download the OAuth Desktop client JSON there.")
        flow = InstalledAppFlow.from_client_secrets_file(str(CLIENT_SECRET), SCOPES)
        creds = flow.run_local_server(port=0, open_browser=True)
    TOKEN.write_text(creds.to_json(), encoding="utf-8")
    return creds


def services(interactive: bool = False):
    creds = get_credentials(interactive)
    return (
        build("youtube", "v3", credentials=creds, cache_discovery=False),
        build("youtubeAnalytics", "v2", credentials=creds, cache_discovery=False),
    )
