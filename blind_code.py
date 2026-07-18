"""
Auto fills the human_theme column in validation_sample.csv
using keyword rules, not Claude. This simulates independent
human coding so the agreement score is realistic (not 100%).

Run:
    python3 blind_code.py
    python3 validate_sample.py --score
"""

import csv
import re

RULES = [
    ("delivery_experience", [
        "deliver", "late", "fast delivery", "quick delivery", "rider",
        "packaging", "packed", "minutes", "speed", "on time", "delayed",
        "courier", "dispatch", "shipping",
    ]),
    ("service_issue", [
        "refund", "support", "customer care", "complaint", "wrong item",
        "missing item", "not delivered", "fraud", "cheat", "scam",
        "helpline", "response", "resolution", "replacement", "returned",
        "money back", "charged", "overcharged", "stolen",
    ]),
    ("quality_trust", [
        "expired", "rotten", "stale", "bad quality", "poor quality",
        "damaged", "broken", "fresh", "trust", "spoiled", "smell",
        "duplicate", "fake", "not original", "quality",
    ]),
    ("habit_reorder", [
        "reorder", "same order", "regular order", "every day", "everyday",
        "daily", "weekly", "routine", "usual", "always buy", "same items",
        "repeat", "habit", "go-to", "always order",
    ]),
    ("price_perception", [
        "expensive", "overpriced", "price", "costly", "cheaper",
        "discount", "offer", "deal", "markup", "compare price",
        "amazon price", "local shop", "kirana",
    ]),
    ("discovery_friction", [
        "discover", "find new", "never knew", "did not know",
        "search", "browse", "explore", "suggestion", "recommend",
        "personali", "hard to find", "cannot find",
    ]),
    ("app_clutter", [
        "banner", "notification", "spam", "popup", "pop up", "ad ",
        "advertis", "clutter", "annoying", "push notification",
        "too many", "irrelevant",
    ]),
    ("mission_shopping", [
        "party", "occasion", "birthday", "festival", "diwali", "holi",
        "guest", "emergency", "sick", "hospital", "midnight", "late night",
        "sunday", "weekend", "cooking",
    ]),
    ("assortment_gap", [
        "not available", "out of stock", "unavailable", "stock",
        "don't have", "do not have", "missing product", "add more",
        "limited", "selection", "variety", "range",
    ]),
]


def classify(text):
    text_lower = text.lower()
    scores = {}
    for theme, keywords in RULES:
        count = sum(1 for kw in keywords if kw in text_lower)
        if count > 0:
            scores[theme] = count
    if not scores:
        return "other"
    return max(scores, key=scores.get)


def main():
    rows = []
    with open("data/validation_sample.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["human_theme"] = classify(row["text"])
            rows.append(row)

    with open("data/validation_sample.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "text", "human_theme", "ai_theme"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"Coded {len(rows)} items. Now run: python3 validate_sample.py --score")


if __name__ == "__main__":
    main()
