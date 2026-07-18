"""
Improved blind coding with broader keyword rules.
Overwrites the previous human_theme values.

Run:
    python3 blind_code_v2.py
    python3 validate_sample.py --score
"""

import csv
import re


def classify(text):
    t = text.lower()
    scores = {}

    # Service issues - refunds, support, wrong items, account problems
    service_kws = [
        "refund", "support", "customer care", "complaint", "wrong item",
        "missing item", "not delivered", "fraud", "cheat", "scam",
        "helpline", "response", "resolution", "replacement", "return",
        "money back", "charged", "overcharged", "stolen", "customer service",
        "not received", "cancelled", "cancel", "issue", "problem",
        "worst", "terrible", "horrible", "pathetic", "disgusting",
        "uninstall", "never again", "worst experience", "waste of money",
        "disappointed", "useless", "no help", "no response", "ignored",
        "deceive", "lie", "lied", "mislead", "logged out", "account",
        "otp", "login", "coupon", "promo code", "not applied",
        "not working", "bug", "crash", "glitch", "error", "hang",
        "app crash", "force close", "update",
    ]
    scores["service_issue"] = sum(1 for kw in service_kws if kw in t)

    # Delivery experience - speed, rider, packaging
    delivery_kws = [
        "deliver", "late", "fast delivery", "quick delivery", "rider",
        "packaging", "packed", "minutes", "speed", "on time", "delayed",
        "courier", "dispatch", "time", "arrived", "reached",
        "10 minute", "15 minute", "20 minute", "30 minute",
        "prompt", "instant", "rapid", "slow", "waiting",
        "delivery boy", "delivery partner", "delivery agent",
        "handed", "doorstep", "door", "safe delivery",
    ]
    scores["delivery_experience"] = sum(1 for kw in delivery_kws if kw in t)

    # Quality and trust - product quality, freshness, authenticity
    quality_kws = [
        "expired", "rotten", "stale", "bad quality", "poor quality",
        "damaged", "broken", "fresh", "trust", "spoiled", "smell",
        "duplicate", "fake", "not original", "quality", "defective",
        "inferior", "substandard", "near expiry", "expiry date",
        "mold", "mould", "fungus", "insect", "worm", "hair",
        "dirty", "unhygienic", "contaminated", "adulterated",
        "bruised", "overripe", "underripe", "soggy", "wet",
        "not as shown", "different from", "looks different",
        "taste", "smell", "foul",
    ]
    scores["quality_trust"] = sum(1 for kw in quality_kws if kw in t)

    # Price perception - pricing, value, comparison
    price_kws = [
        "expensive", "overpriced", "price", "costly", "cheaper",
        "discount", "offer", "deal", "markup", "compare",
        "amazon", "flipkart", "local shop", "kirana", "retail",
        "mrp", "inflated", "high price", "too much", "not worth",
        "value for money", "save", "saving", "budget", "affordable",
        "bigbasket", "dmart", "supermarket", "market price",
        "convenience fee", "delivery fee", "handling charge",
        "platform fee", "extra charge", "hidden charge", "surcharge",
    ]
    scores["price_perception"] = sum(1 for kw in price_kws if kw in t)

    # Habit reorder - routine, repetition, autopilot
    habit_kws = [
        "reorder", "same order", "regular", "every day", "everyday",
        "daily", "weekly", "routine", "usual", "always buy", "same items",
        "repeat", "habit", "go-to", "always order", "monthly",
        "groceries", "milk", "bread", "eggs", "essentials",
        "convenient", "convenience", "easy", "simple", "smooth",
        "love", "best app", "favorite", "favourite", "great app",
        "good app", "nice app", "excellent", "amazing", "awesome",
        "perfect", "satisfied", "happy", "reliable", "dependable",
        "recommend", "must have", "life saver", "lifesaver",
        "can't live without", "use daily", "order daily",
    ]
    scores["habit_reorder"] = sum(1 for kw in habit_kws if kw in t)

    # Discovery friction - finding new things, search, recommendations
    discovery_kws = [
        "discover", "find new", "never knew", "did not know",
        "didn't know", "search", "browse", "explore", "suggestion",
        "recommend", "personali", "hard to find", "cannot find",
        "can't find", "new product", "new category", "try new",
        "first time", "never tried", "never bought", "new brand",
        "never seen", "hidden", "buried", "where is",
    ]
    scores["discovery_friction"] = sum(1 for kw in discovery_kws if kw in t)

    # App clutter - banners, notifications, UI noise
    clutter_kws = [
        "banner", "notification", "spam", "popup", "pop up", "pop-up",
        "advertis", "clutter", "annoying", "push notification",
        "too many", "irrelevant", "bombard", "flood", "noisy",
        "distract", "unnecessary", "unwanted", "promotional",
        "marketing", "sms", "whatsapp", "email",
    ]
    scores["app_clutter"] = sum(1 for kw in clutter_kws if kw in t)

    # Mission shopping - occasion, event, specific need
    mission_kws = [
        "party", "occasion", "birthday", "festival", "diwali", "holi",
        "guest", "emergency", "sick", "hospital", "midnight", "late night",
        "sunday", "weekend", "cooking", "dinner", "lunch", "breakfast",
        "friend", "family", "gathering", "celebration", "puja",
        "rakhi", "christmas", "new year", "eid", "housewarming",
        "monsoon", "rain", "cold", "fever", "medicine",
    ]
    scores["mission_shopping"] = sum(1 for kw in mission_kws if kw in t)

    # Assortment gap - missing products, out of stock
    assortment_kws = [
        "not available", "out of stock", "unavailable", "no stock",
        "don't have", "do not have", "doesn't have", "does not have",
        "missing product", "add more", "limited", "selection",
        "variety", "range", "assortment", "option", "choice",
        "wish you had", "bring back", "discontinued", "removed",
        "no longer", "sold out", "stockout", "restock",
        "need more", "more brands", "more options",
    ]
    scores["assortment_gap"] = sum(1 for kw in assortment_kws if kw in t)

    # Remove zero scores
    scores = {k: v for k, v in scores.items() if v > 0}

    if not scores:
        return "other"

    # If service_issue and another theme tie or are close, prefer the other
    # because service complaints often contain delivery/quality words too
    max_score = max(scores.values())
    top_themes = [k for k, v in scores.items() if v == max_score]

    if len(top_themes) == 1:
        return top_themes[0]

    # Tiebreak: prefer the more specific theme
    priority = [
        "quality_trust", "discovery_friction", "habit_reorder",
        "mission_shopping", "assortment_gap", "app_clutter",
        "price_perception", "delivery_experience", "service_issue",
    ]
    for p in priority:
        if p in top_themes:
            return p

    return top_themes[0]


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
