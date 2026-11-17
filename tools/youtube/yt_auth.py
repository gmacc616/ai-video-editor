"""One-time sign-in. Opens a browser for Google consent, saves token.json, verifies access."""
from datetime import date, timedelta

from yt_common import TOKEN, services


def main():
    yt, yta = services(interactive=True)
    ch = yt.channels().list(part="snippet,statistics", mine=True).execute()
    items = ch.get("items", [])
    if not items:
        raise SystemExit("Signed in, but this Google account has no YouTube channel (or picked the wrong brand account).")
    c = items[0]
    print(f"Channel: {c['snippet']['title']} ({c['id']})")
    print(f"Subscribers: {c['statistics'].get('subscriberCount', 'hidden')}  Videos: {c['statistics'].get('videoCount')}")

    end = date.today()
    r = yta.reports().query(
        ids="channel==MINE",
        startDate=str(end - timedelta(days=28)),
        endDate=str(end),
        metrics="views,estimatedMinutesWatched",
    ).execute()
    row = (r.get("rows") or [[0, 0]])[0]
    print(f"Analytics API OK - last 28 days: {row[0]} views, {row[1]} minutes watched")
    print(f"Token saved to {TOKEN}")


if __name__ == "__main__":
    main()
