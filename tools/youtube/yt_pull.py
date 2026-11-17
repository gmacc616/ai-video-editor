"""Pull channel + per-video analytics into data/youtube/<YYYY-MM-DD>/.

Usage: py tools\\youtube\\yt_pull.py [--retention-videos 50]

Every optional query is attempted and, if the API rejects it, logged to
errors.json instead of guessed - nothing here is estimated or invented.
"""
import argparse
import csv
import json
import re
from datetime import date
from pathlib import Path

from googleapiclient.errors import HttpError

from yt_common import services

ROOT = Path(__file__).resolve().parents[2]

VIDEO_METRICS = (
    "views,estimatedMinutesWatched,averageViewDuration,averageViewPercentage,"
    "subscribersGained,subscribersLost,likes,comments,shares"
)


def iso_duration_seconds(d: str) -> int:
    m = re.fullmatch(r"P(?:(\d+)D)?T?(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", d or "")
    if not m:
        return 0
    days, h, mi, s = (int(x or 0) for x in m.groups())
    return days * 86400 + h * 3600 + mi * 60 + s


def rows_to_dicts(resp):
    cols = [c["name"] for c in resp.get("columnHeaders", [])]
    return [dict(zip(cols, r)) for r in resp.get("rows", []) or []]


def write_csv(path: Path, rows: list[dict]):
    if not rows:
        return
    keys = list(dict.fromkeys(k for r in rows for k in r))
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        w.writerows(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--retention-videos", type=int, default=50,
                    help="retention curves for the N most recent videos")
    args = ap.parse_args()

    yt, yta = services()
    out = ROOT / "data" / "youtube" / str(date.today())
    out.mkdir(parents=True, exist_ok=True)
    errors = []

    def query(name, **kw):
        try:
            return yta.reports().query(ids="channel==MINE", **kw).execute()
        except HttpError as e:
            errors.append({"query": name, "params": kw, "error": str(e)})
            return None

    # Channel
    ch = yt.channels().list(part="snippet,statistics,contentDetails", mine=True).execute()["items"][0]
    (out / "channel.json").write_text(json.dumps(ch, indent=2), encoding="utf-8")
    start = ch["snippet"]["publishedAt"][:10]
    end = str(date.today())
    uploads = ch["contentDetails"]["relatedPlaylists"]["uploads"]

    # All uploads + metadata
    ids, token = [], None
    while True:
        r = yt.playlistItems().list(part="contentDetails", playlistId=uploads,
                                    maxResults=50, pageToken=token).execute()
        ids += [i["contentDetails"]["videoId"] for i in r["items"]]
        token = r.get("nextPageToken")
        if not token:
            break
    videos = {}
    for i in range(0, len(ids), 50):
        r = yt.videos().list(part="snippet,contentDetails,statistics",
                             id=",".join(ids[i:i + 50])).execute()
        for v in r["items"]:
            videos[v["id"]] = {
                "video_id": v["id"],
                "title": v["snippet"]["title"],
                "published_at": v["snippet"]["publishedAt"],
                "duration_s": iso_duration_seconds(v["contentDetails"]["duration"]),
                "tags": "|".join(v["snippet"].get("tags", [])),
                "lifetime_views": v["statistics"].get("viewCount"),
                "lifetime_likes": v["statistics"].get("likeCount"),
                "lifetime_comments": v["statistics"].get("commentCount"),
            }

    # Per-video analytics (lifetime)
    r = query("per_video", startDate=start, endDate=end, metrics=VIDEO_METRICS,
              dimensions="video", sort="-views", maxResults=200)
    for row in rows_to_dicts(r or {}):
        videos.setdefault(row["video"], {"video_id": row["video"]}).update(
            {k: v for k, v in row.items() if k != "video"})

    # Content type per video (Shorts vs long-form), if the API supports it for this channel
    r = query("content_type", startDate=start, endDate=end, metrics="views",
              dimensions="video,creatorContentType", sort="-views", maxResults=200)
    for row in rows_to_dicts(r or {}):
        if row["video"] in videos:
            videos[row["video"]]["content_type"] = row["creatorContentType"]

    write_csv(out / "videos.csv", sorted(videos.values(),
                                        key=lambda v: v.get("published_at", ""), reverse=True))

    # Channel-level breakdowns
    for name, dims, metrics, extra in [
        ("daily", "day", "views,estimatedMinutesWatched,subscribersGained,subscribersLost", {}),
        ("traffic_sources", "insightTrafficSourceType", "views,estimatedMinutesWatched", {}),
        ("content_type", "creatorContentType", "views,estimatedMinutesWatched,averageViewDuration", {}),
        ("subscribed_status", "subscribedStatus", "views,estimatedMinutesWatched,averageViewDuration", {}),
        ("country", "country", "views,estimatedMinutesWatched", {"sort": "-views", "maxResults": 25}),
        ("age_gender", "ageGroup,gender", "viewerPercentage", {}),
        ("device", "deviceType", "views,estimatedMinutesWatched", {}),
    ]:
        r = query(name, startDate=start, endDate=end, dimensions=dims, metrics=metrics, **extra)
        if r:
            write_csv(out / f"{name}.csv", rows_to_dicts(r))

    # Per-video traffic sources and retention curves for the most recent videos
    recent = sorted(videos.values(), key=lambda v: v.get("published_at", ""), reverse=True)
    recent = recent[: args.retention_videos]
    traffic, retention = [], []
    for v in recent:
        vid = v["video_id"]
        r = query(f"traffic:{vid}", startDate=start, endDate=end, metrics="views,estimatedMinutesWatched",
                  dimensions="insightTrafficSourceType", filters=f"video=={vid}")
        traffic += [{"video_id": vid, **row} for row in rows_to_dicts(r or {})]
        r = query(f"retention:{vid}", startDate=start, endDate=end,
                  metrics="audienceWatchRatio,relativeRetentionPerformance",
                  dimensions="elapsedVideoTimeRatio", filters=f"video=={vid}")
        retention += [{"video_id": vid, **row} for row in rows_to_dicts(r or {})]
    write_csv(out / "video_traffic_sources.csv", traffic)
    write_csv(out / "video_retention.csv", retention)

    (out / "errors.json").write_text(json.dumps(errors, indent=2), encoding="utf-8")
    print(f"Saved to {out}")
    print(f"Videos: {len(videos)}  retention curves: {len({r['video_id'] for r in retention})}  "
          f"failed queries: {len(errors)}")
    print("Not pulled: thumbnail impressions / CTR (not in the Analytics API query endpoint; "
          "needs a YouTube Reporting API bulk-report job or a Studio CSV export).")


if __name__ == "__main__":
    main()
