"""Upload a Short with the YouTube Data API v3.

Usage:
  py tools\\youtube\\yt_upload.py "<file.mp4>" --title "..." [--description "..." | --description-file d.txt]
      [--tags "boxabl,tiny home"] [--publish-at 2026-10-23T07:00:00+08:00] [--thumbnail t.jpg] [--dry-run]

- Uses the OAuth client in %USERPROFILE%\\.yt-analytics\\client_secret.json (same as the analytics tools),
  but its own token (token_upload.json) with the upload scope, so the read-only analytics sign-in is untouched.
- Always uploads as private. --publish-at schedules it (YouTube only honours this once the API project has
  passed its audit; until then the video stays private and is scheduled in Studio).
- Fixed per the user's standing upload settings: Made for kids = No, altered/synthetic content = No,
  category Entertainment, English. Paid promotion isn't settable via the API (stays No).
- --dry-run prints the request without signing in or uploading (the runnable self-check).
"""
import argparse
import csv
import json
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SECRETS_DIR = Path.home() / ".yt-analytics"
CLIENT_SECRET = SECRETS_DIR / "client_secret.json"
TOKEN = SECRETS_DIR / "token_upload.json"
SCOPES = ["https://www.googleapis.com/auth/youtube.upload", "https://www.googleapis.com/auth/youtube.readonly"]
LOG = ROOT / "data" / "youtube" / "uploads.csv"


def build_body(a):
    if not a.title.strip() or len(a.title) > 100 or any(c in a.title for c in "<>"):
        sys.exit("Title must be 1-100 characters with no < or >.")
    desc = Path(a.description_file).read_text(encoding="utf-8") if a.description_file else (a.description or "")
    if len(desc) > 5000 or any(c in desc for c in "<>"):
        sys.exit("Description must be <= 5000 characters with no < or >.")
    tags = [t.strip() for t in (a.tags or "").split(",") if t.strip()]
    if sum(len(t) + 2 for t in tags) > 500:
        sys.exit("Tags exceed YouTube's 500-character total.")
    status = {"privacyStatus": "private", "selfDeclaredMadeForKids": False, "containsSyntheticMedia": False}
    if a.publish_at:
        t = datetime.fromisoformat(a.publish_at)
        if t.tzinfo is None:
            sys.exit("--publish-at needs a time zone, e.g. 2026-10-23T07:00:00+08:00")
        status["publishAt"] = t.isoformat()
    return {"snippet": {"title": a.title, "description": desc, "tags": tags, "categoryId": "24",
                        "defaultLanguage": "en", "defaultAudioLanguage": "en"}, "status": status}


def youtube():
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    creds = Credentials.from_authorized_user_file(str(TOKEN), SCOPES) if TOKEN.exists() else None
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    elif not creds or not creds.valid:
        if not CLIENT_SECRET.exists():
            sys.exit(f"Missing {CLIENT_SECRET}: download the OAuth 'Desktop app' client JSON there first.")
        creds = InstalledAppFlow.from_client_secrets_file(str(CLIENT_SECRET), SCOPES).run_local_server(port=0, open_browser=True)
    TOKEN.write_text(creds.to_json(), encoding="utf-8")
    return build("youtube", "v3", credentials=creds, cache_discovery=False)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("file")
    p.add_argument("--title", required=True)
    p.add_argument("--description")
    p.add_argument("--description-file")
    p.add_argument("--tags")
    p.add_argument("--publish-at")
    p.add_argument("--thumbnail")
    p.add_argument("--dry-run", action="store_true")
    a = p.parse_args()
    f = Path(a.file)
    if not f.is_file() or f.suffix.lower() not in (".mp4", ".mov"):
        sys.exit(f"Not a video file: {f}")
    body = build_body(a)
    if a.dry_run:
        print(json.dumps({"file": str(f), "bytes": f.stat().st_size, **body}, indent=1, ensure_ascii=False))
        return

    from googleapiclient.http import MediaFileUpload
    yt = youtube()
    ch = yt.channels().list(part="snippet", mine=True).execute().get("items", [])
    if not ch:
        sys.exit("Signed in, but this account has no YouTube channel (wrong brand account?).")
    print(f"Channel: {ch[0]['snippet']['title']}")
    req = yt.videos().insert(part="snippet,status", body=body,
                             media_body=MediaFileUpload(str(f), chunksize=8 * 1024 * 1024, resumable=True))
    resp = None
    while resp is None:
        prog, resp = req.next_chunk()
        if prog:
            print(f"  uploading {int(prog.progress() * 100)}%")
    vid = resp["id"]
    print(f"Uploaded: https://youtube.com/shorts/{vid}  (status: {resp['status']['privacyStatus']})")
    print(f"Studio:   https://studio.youtube.com/video/{vid}/edit")
    if a.thumbnail:
        yt.thumbnails().set(videoId=vid, media_body=MediaFileUpload(a.thumbnail)).execute()
        print("Thumbnail set.")
    LOG.parent.mkdir(parents=True, exist_ok=True)
    new = not LOG.exists()
    with LOG.open("a", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        if new:
            w.writerow(["uploaded_at", "video_id", "title", "file", "publish_at", "privacy"])
        w.writerow([datetime.now().isoformat(timespec="seconds"), vid, a.title, f.name, a.publish_at or "", resp["status"]["privacyStatus"]])


if __name__ == "__main__":
    main()
