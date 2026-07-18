"""
Blinkit Discovery Engine
Analyzes user feedback at scale to surface category discovery insights.
Built for the NextLeap PM Fellowship graduation project.
"""

import csv
import io
import json
import os

import pandas as pd
import streamlit as st

MODEL = "claude-sonnet-4-6"

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

THEME_LABELS = {
    "habit_reorder": "Habit reorder loop",
    "price_perception": "Price doubts on new items",
    "quality_trust": "Quality and trust gap",
    "discovery_friction": "Discovery friction in app",
    "app_clutter": "Banner and ad noise",
    "delivery_experience": "Delivery experience",
    "mission_shopping": "Mission based shopping",
    "assortment_gap": "Assortment gaps",
    "service_issue": "Service and support issues",
    "other": "Other",
}

THEME_DESCRIPTIONS = {
    "habit_reorder": "User talks about buying the same items on autopilot, reordering without thinking, or relying on search history and past orders.",
    "price_perception": "User mentions new or unfamiliar items feeling overpriced, compares prices with local stores or Amazon, or hesitates on price before trying something new.",
    "quality_trust": "User worries about freshness, quality, or authenticity of items in categories they have not tried on the platform. Includes damaged or expired product complaints that erode trust in new categories.",
    "discovery_friction": "User cannot find new products, never sees relevant suggestions, or says the app does not surface things they might want.",
    "app_clutter": "User complains about too many banners, pop ups, or promotional noise that they ignore or find annoying.",
    "delivery_experience": "User talks about delivery speed, packaging, rider behavior, or the delivery process itself.",
    "mission_shopping": "User describes shopping for a specific occasion, event, or need rather than browsing a category. Includes multi-app or multi-store shopping trips.",
    "assortment_gap": "User wanted a specific product, brand, or category that was not available on the platform.",
    "service_issue": "User reports problems with refunds, customer support, wrong items delivered, or account issues.",
    "other": "Does not fit any of the above themes clearly.",
}


st.set_page_config(
    page_title="Blinkit Discovery Engine",
    page_icon="🔍",
    layout="wide",
)

st.title("Blinkit Discovery Engine")
st.markdown(
    "An AI powered pipeline that ingests app reviews and community posts, "
    "classifies every item against a fixed 10 theme taxonomy using Claude, "
    "and surfaces the insights a growth team needs to drive category expansion."
)

tab_results, tab_live, tab_how, tab_themes = st.tabs(
    ["Analyzed dataset", "Try it live", "How it works", "Theme taxonomy"]
)

# --- Tab 1: Pre-analyzed results ---
with tab_results:
    data_path = "data/tagged_reviews.csv"
    if os.path.exists(data_path):
        df = pd.read_csv(data_path)
        total = len(df)
        disc = int((df["discovery_flag"] == "yes").sum()) if "discovery_flag" in df.columns else 0
        sources = df["source"].nunique() if "source" in df.columns else 0

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total items analyzed", f"{total:,}")
        c2.metric("Discovery related", f"{disc:,}")
        c3.metric("Discovery share", f"{(disc / total * 100):.0f}%" if total > 0 else "0%")
        c4.metric("Data sources", sources)

        st.divider()

        col_chart, col_insight = st.columns([3, 2])

        with col_chart:
            st.subheader("What users talk about")
            if "theme" in df.columns:
                counts = (
                    df["theme"]
                    .map(THEME_LABELS)
                    .value_counts()
                    .rename_axis("Theme")
                    .reset_index(name="Count")
                )
                st.bar_chart(counts.set_index("Theme"), horizontal=True)

        with col_insight:
            st.subheader("Discovery related by theme")
            if "discovery_flag" in df.columns and "theme" in df.columns:
                disc_df = df[df["discovery_flag"] == "yes"]
                disc_counts = (
                    disc_df["theme"]
                    .map(THEME_LABELS)
                    .value_counts()
                    .rename_axis("Theme")
                    .reset_index(name="Discovery items")
                )
                st.dataframe(disc_counts, use_container_width=True, hide_index=True)

        st.divider()
        st.subheader("Read the evidence")
        pick = st.selectbox("Filter by theme", options=["All"] + list(THEME_LABELS.values()), index=0)

        if pick == "All":
            sub = df.head(50)
        else:
            inv = {v: k for k, v in THEME_LABELS.items()}
            sub = df[df["theme"] == inv[pick]].head(30)

        for _, row in sub.iterrows():
            sentiment = row.get("sentiment", "")
            badge = ""
            if sentiment == "negative":
                badge = "🔴"
            elif sentiment == "positive":
                badge = "🟢"
            elif sentiment == "neutral":
                badge = "🟡"
            disc_badge = " [DISCOVERY]" if row.get("discovery_flag") == "yes" else ""
            st.markdown(f"{badge} {row['text'][:300]}{disc_badge}")

        # Insight report
        report_path = "data/insight_report.md"
        if os.path.exists(report_path):
            st.divider()
            with st.expander("Full synthesized insight report", expanded=False):
                with open(report_path, encoding="utf-8") as f:
                    st.markdown(f.read())
    else:
        st.info(
            "No pre-analyzed dataset found. Run the pipeline scripts "
            "(scrape_reviews.py, analyze_reviews.py, synthesize.py) "
            "and commit the data/ folder to see results here."
        )

# --- Tab 2: Live classification ---
with tab_live:
    st.subheader("Paste reviews and classify them live")
    st.markdown(
        "Paste up to 30 reviews (one per line) and run the same "
        "Claude classification pipeline that processed the full dataset."
    )

    raw = st.text_area(
        "Reviews",
        height=200,
        placeholder="Paste one review per line. Minimum 10 characters each.",
    )

    if st.button("Classify with Claude", type="primary"):
        lines = [ln.strip() for ln in raw.splitlines() if len(ln.strip()) > 10][:30]
        if not lines:
            st.warning("Paste at least one review with 10 or more characters.")
        else:
            api_key = st.secrets.get("ANTHROPIC_API_KEY", os.environ.get("ANTHROPIC_API_KEY", ""))
            if not api_key:
                st.error("No API key found. Add ANTHROPIC_API_KEY in app settings > Secrets.")
            else:
                try:
                    import anthropic

                    client = anthropic.Anthropic(api_key=api_key)
                    numbered = "\n".join(f"{i}. {t[:400]}" for i, t in enumerate(lines))
                    system = (
                        f"You are tagging user feedback for a quick commerce product team. "
                        f"For each numbered review, return one JSON object. Fields: "
                        f"id (the review number), theme (one of {THEMES}), "
                        f"sentiment (positive, neutral, or negative), "
                        f"discovery_flag (yes if the review touches on discovering, trying, "
                        f"hesitating about, or avoiding new products or categories, else no). "
                        f"Return ONLY a JSON array. No markdown, no commentary."
                    )
                    with st.spinner("Classifying..."):
                        msg = client.messages.create(
                            model=MODEL,
                            max_tokens=2000,
                            system=system,
                            messages=[{"role": "user", "content": numbered}],
                        )
                    raw_out = msg.content[0].text.replace("```json", "").replace("```", "").strip()
                    tags = json.loads(raw_out)
                    out = pd.DataFrame(
                        [
                            {
                                "Review": lines[t["id"]][:150],
                                "Theme": THEME_LABELS.get(t["theme"], t["theme"]),
                                "Sentiment": t["sentiment"],
                                "Discovery related": t["discovery_flag"],
                            }
                            for t in tags
                            if isinstance(t.get("id"), int) and t["id"] < len(lines)
                        ]
                    )
                    st.dataframe(out, use_container_width=True, hide_index=True)

                    disc_count = sum(1 for t in tags if t.get("discovery_flag") == "yes")
                    st.metric("Discovery related items", f"{disc_count} of {len(lines)}")

                except Exception as exc:
                    st.error(f"Classification failed: {exc}")

# --- Tab 3: How it works ---
with tab_how:
    st.subheader("Pipeline architecture")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown("**1. Ingest**")
        st.markdown(
            "Play Store reviews via google-play-scraper (Python library, no auth). "
            "App Store reviews via public iTunes RSS feed. "
            "Reddit threads via public JSON search endpoints. "
            "All deduplicated into one CSV."
        )

    with col2:
        st.markdown("**2. Classify**")
        st.markdown(
            "Claude (Sonnet) tags every item against a fixed 10 theme taxonomy "
            "in batches of 60. Each item gets: theme, sentiment, category signal, "
            "and a discovery flag indicating if it touches on trying or avoiding new categories."
        )

    with col3:
        st.markdown("**3. Synthesize**")
        st.markdown(
            "Aggregate theme counts plus sampled verbatims go back to Claude "
            "to answer 8 research questions from the brief, with cited evidence "
            "per answer. Low confidence answers are flagged."
        )

    with col4:
        st.markdown("**4. Validate**")
        st.markdown(
            "100 random items are drawn and blind coded by hand (without seeing "
            "the AI tags). Agreement between human and AI tags is scored overall "
            "and per theme. This number is reported in the deck."
        )

    st.divider()
    st.subheader("Why a fixed taxonomy instead of open coding")
    st.markdown(
        "Open ended theme generation drifts across batches and inflates theme "
        "counts. A fixed taxonomy, drafted after manually reading 200 reviews, "
        "keeps tags comparable across thousands of items and makes validation "
        "possible. The 10 themes cover the complete space of what quick commerce "
        "users talk about, with a catch all 'other' for anything that does not fit."
    )

    st.divider()
    st.subheader("Data sources and volume")
    st.markdown(
        "The pipeline is designed to process 3,000 to 5,000 items per run. "
        "Primary sources are Google Play Store reviews (highest volume), "
        "Apple App Store reviews (smaller but different user base), and "
        "Reddit threads from r/india, r/delhi, r/bangalore, r/mumbai, "
        "and r/gurgaon where Blinkit is frequently discussed."
    )

# --- Tab 4: Theme taxonomy ---
with tab_themes:
    st.subheader("Classification taxonomy (10 themes)")
    st.markdown(
        "Each review is assigned exactly one theme. The taxonomy was built "
        "after manually reading 200 reviews to identify the recurring patterns. "
        "Here is what each theme captures:"
    )
    for key, label in THEME_LABELS.items():
        st.markdown(f"**{label}**")
        st.markdown(f"{THEME_DESCRIPTIONS[key]}")
        st.markdown("---")
