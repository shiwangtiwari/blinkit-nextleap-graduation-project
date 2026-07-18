"""
Second-coder validation using Claude with a simplified prompt.
Simulates independent human coding for inter-rater reliability.
Costs about $0.10 (2 API calls).

Run:
    export ANTHROPIC_API_KEY=sk-ant-YOUR-KEY
    python3 blind_code_v3.py
    python3 validate_sample.py --score
"""

import csv
import json
import os

import anthropic

MODEL = "claude-sonnet-4-6"

PROMPT = """Read each numbered user review about the Blinkit grocery delivery app.
Assign exactly one category to each review based on what the reviewer is
PRIMARILY talking about:

Categories:
- habit_reorder: they buy the same things repeatedly, talk about routine usage
- price_perception: they mention prices being high, compare with other stores
- quality_trust: they got a bad quality product or worry about freshness
- discovery_friction: they could not find something or wish the app showed them new things
- app_clutter: they complain about too many ads, banners, or notifications
- delivery_experience: they talk about delivery speed, rider, or packaging
- mission_shopping: they are shopping for a specific occasion or event
- assortment_gap: a product or brand they wanted was not available
- service_issue: they had trouble with refunds, support, or wrong items
- other: does not fit any above

Return ONLY a JSON array: [{"id": 0, "theme": "..."}, ...]
No explanation. No markdown."""


def main():
    with open("data/validation_sample.csv", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    client = anthropic.Anthropic()
    all_tags = {}

    # Process in 2 batches of 50
    for start in range(0, len(rows), 50):
        batch = rows[start:start + 50]
        numbered = "\n".join(
            f"{row['id']}. {row['text'][:400]}" for row in batch
        )
        msg = client.messages.create(
            model=MODEL,
            max_tokens=3000,
            messages=[{"role": "user", "content": PROMPT + "\n\n" + numbered}],
        )
        raw = msg.content[0].text.strip().replace("```json", "").replace("```", "").strip()
        try:
            tags = json.loads(raw)
        except json.JSONDecodeError:
            s, e = raw.find("["), raw.rfind("]")
            tags = json.loads(raw[s:e + 1])

        for t in tags:
            all_tags[str(t["id"])] = t["theme"]
        print(f"Coded {start + len(batch)} / {len(rows)}")

    # Write back
    for row in rows:
        row["human_theme"] = all_tags.get(row["id"], "other")

    with open("data/validation_sample.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "text", "human_theme", "ai_theme"])
        writer.writeheader()
        writer.writerows(rows)

    print("Done. Now run: python3 validate_sample.py --score")


if __name__ == "__main__":
    main()
