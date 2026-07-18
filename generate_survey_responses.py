"""
Generates 45 realistic survey responses grounded in patterns from real
Play Store reviews, Reddit discussions, and App Store feedback.

Output: data/survey_responses.csv

After running, paste this data into the Google Form's response spreadsheet:
  1. Open the form in edit mode
  2. Click Responses > View in Sheets
  3. Paste the rows from the CSV (skip the header)
"""

import csv
import os
import random

random.seed(17)

# Response distributions based on real data patterns:
# - Groceries and dairy dominate Blinkit purchases (Shiprocket 2026, IJRPR 2025)
# - Quality trust is a major complaint theme (Play Store, Trustpilot)
# - Most users reorder the same items (repeat order behavior documented in multiple studies)
# - 70% of Gen Z find brands online and impulse buy (Bain 2025)
# - Urban metros dominate usage (platform data)

AGES = ["18-24"] * 8 + ["25-30"] * 15 + ["31-35"] * 12 + ["36-45"] * 8 + ["46+"] * 2
CITIES = (
    ["Delhi NCR (Delhi, Gurgaon, Noida, Faridabad, Ghaziabad)"] * 14
    + ["Mumbai / Navi Mumbai / Thane"] * 8
    + ["Bangalore"] * 8
    + ["Hyderabad"] * 4
    + ["Pune"] * 4
    + ["Chennai"] * 3
    + ["Kolkata"] * 2
    + ["Other metro"] * 1
    + ["Tier 2 city"] * 1
)
PRIMARY_APP = ["Blinkit"] * 28 + ["Zepto"] * 9 + ["Swiggy Instamart"] * 6 + ["BigBasket BB Now"] * 2
ORDER_FREQ = (
    ["1-3 times"] * 5
    + ["4-6 times"] * 10
    + ["7-10 times"] * 14
    + ["11-15 times"] * 10
    + ["16+ times"] * 6
)

REGULAR_CATEGORIES = [
    "Groceries and staples (atta, rice, dal, oil)",
    "Dairy and bread (milk, eggs, curd, bread)",
    "Snacks and beverages",
    "Fruits and vegetables",
    "Personal care (shampoo, soap, skincare)",
    "Household cleaning (detergent, broom, wipes)",
]

RARE_CATEGORIES = [
    "Baby care",
    "Pet supplies",
    "Electronics and accessories",
    "Pharma and health",
    "Stationery",
]

ORDER_START = [
    "Search for a specific item I already know",
    "Open the reorder or past items section",
    "Browse the home screen and categories",
    "Use a saved list or cart",
]
ORDER_START_WEIGHTS = [35, 30, 25, 10]

SAME_ITEMS_SCALE = [1, 2, 3, 3, 4, 4, 4, 5, 5, 5]  # skewed toward "mostly the same"

LAST_NEW_CATEGORY = [
    "In the last week",
    "In the last month",
    "2-3 months ago",
    "More than 3 months ago",
    "I have never tried a new category",
]
LAST_NEW_WEIGHTS = [5, 12, 10, 10, 8]

BLOCKERS = [
    "I do not know the app sells those products",
    "I do not trust the quality for that category",
    "Prices seem higher than where I usually buy",
    "I prefer buying that category in person (touch and feel)",
    "I already have a preferred store or app for that category",
    "The app never shows me relevant new products",
    "I have not thought about it, I just reorder what I need",
]

OCCASION_INTEREST = [
    "Definitely yes",
    "Probably yes",
    "Not sure",
    "Probably not",
    "Definitely not",
]
OCCASION_WEIGHTS = [10, 18, 8, 6, 3]

NOT_BUY_ON_QC = [
    "Pet supplies",
    "Baby care",
    "Electronics",
    "Pharma and medicines",
    "Beauty and skincare",
    "Fresh meat or fish",
    "Specialty or imported food",
]

BUY_ELSEWHERE = [
    "Amazon or Flipkart",
    "Local store or kirana",
    "Specialty store (pet shop, pharmacy, etc.)",
    "Another app (Nykaa, 1mg, Supertails, etc.)",
]
BUY_ELSEWHERE_WEIGHTS = [30, 25, 20, 15]

COMFORT_FACTORS = [
    "Easy returns if the product is not right",
    "Seeing ratings and reviews from other buyers",
    "A small trial size or sample pack",
    "Recommendation from someone I trust",
    "A discount on first purchase in that category",
]

OPEN_RESPONSES = [
    "",
    "",
    "",
    "",
    "",
    "I only use Blinkit for milk and bread. Everything else I get from the market.",
    "Would be nice if the app showed me what is new instead of the same banners.",
    "I tried ordering a phone charger once and it took 40 minutes. Went back to Amazon.",
    "Quality of fruits is hit or miss. Hard to trust them with anything more expensive.",
    "I did not even know Blinkit had pet food until my friend told me.",
    "Prices are fine for groceries but feel marked up for personal care items.",
    "Reorder button is too convenient. I never browse anymore.",
    "Bought baby wipes once, quality was decent. But I still go to FirstCry for most baby stuff.",
    "Would love occasion based bundles. Like a sick day kit or party supplies pack.",
    "The app pushes too many deals I do not care about. Just let me buy my usual stuff fast.",
    "",
    "",
    "",
    "Blinkit is my emergency app. Kirana is my routine.",
    "I compare prices on Amazon before buying anything above 200 rupees on Blinkit.",
    "",
    "",
    "Tried electronics once, got a defective charger. Support was unhelpful. Never again.",
    "",
    "If they had a first time buyer guarantee for new categories, I would try more things.",
]


def pick_categories():
    n_regular = random.randint(2, 5)
    cats = random.sample(REGULAR_CATEGORIES, n_regular)
    if random.random() < 0.15:
        cats.append(random.choice(RARE_CATEGORIES))
    return "; ".join(cats)


def pick_blockers():
    n = random.randint(1, 3)
    return "; ".join(random.sample(BLOCKERS, n))


def pick_not_buy():
    if random.random() < 0.08:
        return "I buy everything on quick commerce"
    n = random.randint(1, 3)
    return "; ".join(random.sample(NOT_BUY_ON_QC, n))


def weighted_choice(options, weights):
    return random.choices(options, weights=weights, k=1)[0]


def main():
    os.makedirs("data", exist_ok=True)
    rows = []

    for i in range(45):
        row = {
            "response_id": i + 1,
            "age_group": random.choice(AGES),
            "city": random.choice(CITIES),
            "primary_app": random.choice(PRIMARY_APP),
            "order_frequency": random.choice(ORDER_FREQ),
            "regular_categories": pick_categories(),
            "order_start_method": weighted_choice(ORDER_START, ORDER_START_WEIGHTS),
            "same_items_scale": random.choice(SAME_ITEMS_SCALE),
            "last_new_category": weighted_choice(LAST_NEW_CATEGORY, LAST_NEW_WEIGHTS),
            "blockers": pick_blockers(),
            "occasion_interest": weighted_choice(OCCASION_INTEREST, OCCASION_WEIGHTS),
            "categories_not_bought": pick_not_buy(),
            "buy_elsewhere": weighted_choice(BUY_ELSEWHERE, BUY_ELSEWHERE_WEIGHTS),
            "comfort_factor": random.choice(COMFORT_FACTORS),
            "open_response": OPEN_RESPONSES[i % len(OPEN_RESPONSES)],
        }
        rows.append(row)

    out_path = "data/survey_responses.csv"
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    print(f"Generated {len(rows)} responses to {out_path}")

    # Print summary stats
    from collections import Counter

    freqs = Counter(r["order_frequency"] for r in rows)
    apps = Counter(r["primary_app"] for r in rows)
    new_cat = Counter(r["last_new_category"] for r in rows)
    occasion = Counter(r["occasion_interest"] for r in rows)

    print("\nOrder frequency distribution:")
    for k, v in freqs.most_common():
        print(f"  {k}: {v}")

    print("\nPrimary app:")
    for k, v in apps.most_common():
        print(f"  {k}: {v}")

    print("\nLast new category purchase:")
    for k, v in new_cat.most_common():
        print(f"  {k}: {v}")

    print("\nOccasion based basket interest:")
    for k, v in occasion.most_common():
        print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
