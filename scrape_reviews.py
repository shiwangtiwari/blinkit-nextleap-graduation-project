"""
Step 1: Gather raw user feedback for Blinkit.

Sources:
  1. Google Play Store reviews (google-play-scraper, no auth needed)
  2. Apple App Store reviews (public iTunes RSS feed)
  3. Reddit threads (public JSON search, best effort)

Run:
  pip install -r requirements.txt
  python scrape_reviews.py --play-count 4000

Output: data/raw_reviews.csv
"""

import argparse
import csv
import json
import os
import time

import requests
from google_play_scraper import Sort, reviews

PLAY_APP_ID = "com.grofers.customerapp"
IOS_APP_ID = "960335206"
DATA_DIR = "data"

REDDIT_QUERIES = [
    "blinkit",
    "blinkit category",
    "blinkit vs zepto",
    "quick commerce habits india",
    "blinkit quality trust",
    "blinkit new products",
]


def scrape_play_store(target_count):
    rows = []
    token = None
    while len(rows) < target_count:
        batch, token = reviews(
            PLAY_APP_ID,
            lang="en",
            country="in",
            sort=Sort.NEWEST,
            count=200,
            continuation_token=token,
        )
        for r in batch:
            rows.append(
                {
                    "source": "play_store",
                    "date": r["at"].strftime("%Y-%m-%d"),
                    "rating": r["score"],
                    "text": (r["content"] or "").replace("\n", " ").strip(),
                }
            )
        print(f"Play Store: {len(rows)} reviews collected")
        if token is None:
            break
        time.sleep(1)
    return rows


def scrape_app_store(pages=10):
    rows = []
    for page in range(1, pages + 1):
        url = (
            f"https://itunes.apple.com/in/rss/customerreviews/"
            f"page={page}/id={IOS_APP_ID}/sortby=mostrecent/json"
        )
        try:
            resp = requests.get(url, timeout=20)
            resp.raise_for_status()
            entries = resp.json().get("feed", {}).get("entry", [])
        except Exception as exc:
            print(f"App Store page {page} failed: {exc}")
            break
        for e in entries:
            if "im:rating" not in e:
                continue
            rows.append(
                {
                    "source": "app_store",
                    "date": "",
                    "rating": int(e["im:rating"]["label"]),
                    "text": (
                        e.get("title", {}).get("label", "")
                        + ". "
                        + e.get("content", {}).get("label", "")
                    ).replace("\n", " ").strip(),
                }
            )
        print(f"App Store: {len(rows)} reviews collected")
        time.sleep(1)
    return rows


def scrape_reddit():
    rows = []
    headers = {"User-Agent": "blinkit-discovery-engine/1.0"}
    for query in REDDIT_QUERIES:
        url = (
            "https://www.reddit.com/search.json"
            f"?q={requests.utils.quote(query)}&sort=relevance&limit=25&t=year"
        )
        try:
            resp = requests.get(url, headers=headers, timeout=20)
            resp.raise_for_status()
            posts = resp.json().get("data", {}).get("children", [])
        except Exception as exc:
            print(f"Reddit query '{query}' failed: {exc}")
            continue
        for p in posts:
            d = p.get("data", {})
            text = (d.get("title", "") + ". " + d.get("selftext", "")).strip()
            if len(text) < 30:
                continue
            rows.append(
                {
                    "source": "reddit",
                    "date": "",
                    "rating": "",
                    "text": text.replace("\n", " ")[:2000],
                }
            )
        time.sleep(2)
    print(f"Reddit: {len(rows)} posts collected")
    return rows


def load_manual():
    """Load manually collected posts from data/manual_posts.txt (one per line)."""
    path = os.path.join(DATA_DIR, "manual_posts.txt")
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        lines = [ln.strip() for ln in f if len(ln.strip()) > 30]
    return [
        {"source": "manual", "date": "", "rating": "", "text": ln}
        for ln in lines
    ]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--play-count", type=int, default=4000)
    parser.add_argument("--ios-pages", type=int, default=10)
    parser.add_argument("--skip-reddit", action="store_true")
    args = parser.parse_args()

    os.makedirs(DATA_DIR, exist_ok=True)
    all_rows = []
    all_rows += scrape_play_store(args.play_count)
    all_rows += scrape_app_store(args.ios_pages)
    if not args.skip_reddit:
        all_rows += scrape_reddit()
    all_rows += load_manual()

    seen = set()
    clean = []
    for r in all_rows:
        key = r["text"][:120].lower()
        if len(r["text"]) < 15 or key in seen:
            continue
        seen.add(key)
        clean.append(r)

    out_path = os.path.join(DATA_DIR, "raw_reviews.csv")
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["source", "date", "rating", "text"])
        writer.writeheader()
        writer.writerows(clean)

    print(f"\nSaved {len(clean)} unique items to {out_path}")
    summary = {}
    for r in clean:
        summary[r["source"]] = summary.get(r["source"], 0) + 1
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
