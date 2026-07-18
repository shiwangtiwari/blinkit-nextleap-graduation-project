"""
Step 3: Synthesize tagged reviews into an insight report.

Run:
  export ANTHROPIC_API_KEY=sk-ant-...
  python synthesize.py
"""

import csv
import json
import random

import anthropic

MODEL = "claude-sonnet-4-6"
VERBATIMS_PER_THEME = 12

RESEARCH_QUESTIONS = """
1. Why do users repeatedly buy from the same categories?
2. What prevents users from exploring new categories?
3. How do users discover products today?
4. What role do habits play in shopping behavior?
5. What information do users need before trying a new category?
6. What frustrations emerge repeatedly?
7. Which user segments are more likely to experiment?
8. What unmet needs emerge consistently across discussions?
"""


def main():
    with open("data/tagged_reviews.csv", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    with open("data/theme_summary.json", encoding="utf-8") as f:
        summary = json.load(f)

    random.seed(7)
    samples = {}
    for theme in summary["theme_counts"]:
        pool = [r["text"][:300] for r in rows if r["theme"] == theme]
        samples[theme] = random.sample(pool, min(VERBATIMS_PER_THEME, len(pool)))

    prompt = f"""You are synthesizing quick commerce user research for Blinkit.

Aggregate tag counts across {summary['total_items']} reviews and posts:
{json.dumps(summary, indent=2)}

Sample verbatims per theme:
{json.dumps(samples, indent=2)}

Write a research report in plain markdown that answers each of these questions.
Ground every answer in the data above. Under every answer, cite 2 or 3 short
verbatims and the theme counts that support it. Flag low confidence answers
where the data is thin. Do not use em dashes anywhere. Use hyphens or commas
instead. Write like a human analyst, not like an AI.

End with a section titled "Segments showing experimentation signals" and a
section titled "Open questions for user interviews".

Questions:
{RESEARCH_QUESTIONS}
"""

    client = anthropic.Anthropic()
    msg = client.messages.create(
        model=MODEL,
        max_tokens=4000,
        messages=[{"role": "user", "content": prompt}],
    )
    report = msg.content[0].text
    with open("data/insight_report.md", "w", encoding="utf-8") as f:
        f.write(report)
    print("Saved data/insight_report.md")


if __name__ == "__main__":
    main()
