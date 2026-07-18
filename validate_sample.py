"""
Step 4: Validate AI tags against human blind coding.

Usage:
  python validate_sample.py --make     # creates the 100 item sample
  python validate_sample.py --score    # scores agreement after you fill human_theme
"""

import argparse
import csv
import random


def make_sample():
    with open("data/tagged_reviews.csv", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    random.seed(42)
    sample = random.sample(rows, min(100, len(rows)))
    with open("data/validation_sample.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "text", "human_theme", "ai_theme"])
        for i, r in enumerate(sample):
            writer.writerow([i, r["text"], "", r["theme"]])
    print("Wrote data/validation_sample.csv")
    print("Fill the human_theme column without looking at ai_theme, then run --score")


def score_sample():
    with open("data/validation_sample.csv", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    coded = [r for r in rows if r["human_theme"].strip()]
    if not coded:
        print("No human_theme values found yet")
        return
    agree = sum(
        1 for r in coded
        if r["human_theme"].strip().lower() == r["ai_theme"].strip().lower()
    )
    print(f"Coded: {len(coded)} items")
    print(f"Agreement: {agree}/{len(coded)} = {agree / len(coded):.0%}")

    per_theme = {}
    for r in coded:
        t = r["ai_theme"]
        hit = r["human_theme"].strip().lower() == t.strip().lower()
        n, k = per_theme.get(t, (0, 0))
        per_theme[t] = (n + 1, k + (1 if hit else 0))
    print("\nPer theme:")
    for t, (n, k) in sorted(per_theme.items(), key=lambda kv: -kv[1][0]):
        print(f"  {t:<22} {n:>3}  {k / n:.0%}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--make", action="store_true")
    parser.add_argument("--score", action="store_true")
    args = parser.parse_args()
    if args.make:
        make_sample()
    elif args.score:
        score_sample()
    else:
        parser.print_help()
