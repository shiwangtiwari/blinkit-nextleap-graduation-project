"""
Step 2: Classify every review with Claude.

Run:
  export ANTHROPIC_API_KEY=sk-ant-...
  python analyze_reviews.py
"""

import argparse
import csv
import json
import os

import anthropic

MODEL = "claude-sonnet-4-6"
BATCH_SIZE = 60

THEMES = [
    "habit_reorder",
    "price_perception",
    "quality_trust",
    "discovery_friction",
    "app_clutter",
    "delivery_experience",
    "mission_shopping",
    "assortment_gap",
    "service_issue",
    "other",
]

SYSTEM_PROMPT = f"""You are a research analyst tagging user feedback for a
quick commerce product team. For each numbered review, return one JSON object.

Fields:
  id: the review number given
  theme: exactly one of {THEMES}
  sentiment: "positive", "neutral", or "negative"
  category_signal: the product category mentioned (for example "groceries",
    "pet supplies", "baby care", "personal care", "electronics") or ""
  discovery_flag: "yes" if the review touches on discovering, trying,
    hesitating about, or avoiding new products or categories, else "no"

Return ONLY a JSON array of these objects. No markdown, no commentary."""


def load_rows(path, limit):
    with open(path, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    return rows[:limit] if limit else rows


def classify_batch(client, batch):
    numbered = "\n".join(
        f"{i}. {row['text'][:500]}" for i, row in enumerate(batch)
    )
    msg = client.messages.create(
        model=MODEL,
        max_tokens=4000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": numbered}],
    )
    raw = msg.content[0].text.strip()
    raw = raw.replace("```json", "").replace("```", "").strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        start, end = raw.find("["), raw.rfind("]")
        if start >= 0 and end > start:
            return json.loads(raw[start : end + 1])
        raise


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="data/raw_reviews.csv")
    parser.add_argument("--limit", type=int, default=0)
    args = parser.parse_args()

    client = anthropic.Anthropic()
    rows = load_rows(args.input, args.limit)
    print(f"Classifying {len(rows)} items in batches of {BATCH_SIZE}")

    tagged = []
    for start in range(0, len(rows), BATCH_SIZE):
        batch = rows[start : start + BATCH_SIZE]
        try:
            results = classify_batch(client, batch)
        except Exception as exc:
            print(f"Batch at {start} failed, skipping: {exc}")
            continue
        by_id = {int(r["id"]): r for r in results if "id" in r}
        for i, row in enumerate(batch):
            tags = by_id.get(i, {})
            tagged.append(
                {
                    **row,
                    "theme": tags.get("theme", "other"),
                    "sentiment": tags.get("sentiment", "neutral"),
                    "category_signal": tags.get("category_signal", ""),
                    "discovery_flag": tags.get("discovery_flag", "no"),
                }
            )
        done = min(start + BATCH_SIZE, len(rows))
        print(f"  done {done}/{len(rows)}")

    out_path = "data/tagged_reviews.csv"
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(tagged[0].keys()))
        writer.writeheader()
        writer.writerows(tagged)

    theme_counts = {}
    discovery_by_theme = {}
    for r in tagged:
        theme_counts[r["theme"]] = theme_counts.get(r["theme"], 0) + 1
        if r["discovery_flag"] == "yes":
            discovery_by_theme[r["theme"]] = discovery_by_theme.get(r["theme"], 0) + 1

    summary = {
        "total_items": len(tagged),
        "theme_counts": dict(sorted(theme_counts.items(), key=lambda kv: -kv[1])),
        "discovery_related_by_theme": discovery_by_theme,
        "discovery_related_total": sum(discovery_by_theme.values()),
    }
    with open("data/theme_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print(json.dumps(summary, indent=2))
    print(f"\nSaved {out_path} and data/theme_summary.json")


if __name__ == "__main__":
    main()
