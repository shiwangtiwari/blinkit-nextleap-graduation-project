"""
Blinkit Smart Basket
AI-native MVP that demonstrates cross-category discovery nudges.

How it works:
  1. User enters their typical Blinkit order items.
  2. AI analyzes the basket to identify current categories and shopping patterns.
  3. AI generates a personalized suggestion from a category the user
     has never ordered from, with contextual reasoning and social proof.

This is the D3 deliverable for the NextLeap PM Fellowship graduation project.

Deploy on Streamlit Community Cloud:
  1. Push this file to the GitHub repo.
  2. Create a new Streamlit app pointing to this file.
  3. Add ANTHROPIC_API_KEY in Secrets.
"""

import json
import os
import time

import streamlit as st

st.set_page_config(
    page_title="Smart Basket | Blinkit",
    page_icon="cart_with_goods",
    layout="wide",
)

# --- styling ---
st.markdown("""
<style>
    .main-header {
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .category-chip {
        display: inline-block;
        background: #F0F0F0;
        border-radius: 20px;
        padding: 6px 16px;
        margin: 4px;
        font-size: 0.9rem;
        font-weight: 500;
    }
    .nudge-card {
        background: linear-gradient(135deg, #FFF9E6 0%, #FFFFFF 100%);
        border: 2px solid #F8C634;
        border-radius: 16px;
        padding: 24px;
        margin: 16px 0;
    }
    .nudge-title {
        font-size: 1.4rem;
        font-weight: 700;
        margin-bottom: 8px;
    }
    .nudge-category {
        display: inline-block;
        background: #F8C634;
        color: #1A1A2E;
        border-radius: 12px;
        padding: 4px 12px;
        font-size: 0.85rem;
        font-weight: 600;
        margin-bottom: 12px;
    }
    .nudge-reason {
        font-size: 1rem;
        color: #333;
        margin-bottom: 12px;
        line-height: 1.5;
    }
    .social-proof {
        background: #F7F7F7;
        border-radius: 8px;
        padding: 10px 16px;
        font-size: 0.9rem;
        color: #555;
        margin-bottom: 12px;
    }
    .price-tag {
        font-size: 1.2rem;
        font-weight: 700;
        color: #1A1A2E;
    }
    .pattern-box {
        background: #FAFAFA;
        border-radius: 12px;
        padding: 20px;
        margin: 8px 0;
    }
    .pattern-label {
        font-size: 0.85rem;
        color: #888;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 4px;
    }
    .pattern-value {
        font-size: 1.1rem;
        font-weight: 600;
        color: #1A1A2E;
    }
    .how-section {
        background: #1A1A2E;
        color: white;
        border-radius: 12px;
        padding: 24px;
        margin-top: 24px;
    }
    .how-title {
        color: #F8C634;
        font-size: 1.1rem;
        font-weight: 600;
        margin-bottom: 8px;
    }
    .how-text {
        color: #CCC;
        font-size: 0.95rem;
        line-height: 1.6;
    }
</style>
""", unsafe_allow_html=True)

# --- header ---
st.markdown('<div class="main-header">Smart Basket</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-header">'
    'Enter your typical Blinkit order. The AI analyzes your shopping pattern '
    'and suggests one product from a category you have never tried.'
    '</div>',
    unsafe_allow_html=True,
)

# --- example baskets ---
EXAMPLES = {
    "Weekly grocery run": "Toned milk, whole wheat bread, eggs, atta (5kg), rice, toor dal, mustard oil, onions, tomatoes, green chillies",
    "Student survival kit": "Maggi noodles, Lays chips, Coca-Cola, bread, eggs, instant coffee, Kurkure, peanut butter",
    "Household restock": "Harpic toilet cleaner, Vim dishwash bar, Surf Excel, garbage bags, room freshener, paper towels, hand wash, floor cleaner",
    "Snack and beverage run": "Oreo cookies, Hide and Seek, Real fruit juice, Pepsi, Haldirams namkeen, Dark Fantasy, Green tea bags",
}

# --- input ---
col_input, col_examples = st.columns([3, 2])

with col_input:
    basket_text = st.text_area(
        "Your typical order",
        placeholder="Type items separated by commas. E.g., milk, bread, eggs, Maggi, floor cleaner",
        height=120,
        label_visibility="collapsed",
    )

with col_examples:
    st.markdown("**Try an example basket:**")
    for label, items in EXAMPLES.items():
        if st.button(label, use_container_width=True):
            st.session_state["use_example"] = items
            st.rerun()

if "use_example" in st.session_state:
    basket_text = st.session_state.pop("use_example")

analyze = st.button("Analyze my basket", type="primary", use_container_width=False)

if analyze and basket_text.strip():
    try:
        from anthropic import Anthropic
    except ImportError:
        st.error("Missing dependency: pip install anthropic")
        st.stop()

    api_key = os.environ.get("ANTHROPIC_API_KEY") or st.secrets.get("ANTHROPIC_API_KEY")
    if not api_key:
        st.error("Set ANTHROPIC_API_KEY in environment or Streamlit secrets.")
        st.stop()

    client = Anthropic(api_key=api_key)

    with st.spinner("Reading your basket and finding a match..."):
        prompt = f"""You are a recommendation engine for Blinkit, a quick commerce app in India that delivers in 10 minutes.

The user's typical order basket: {basket_text}

Analyze this basket and suggest ONE product from a category they clearly do NOT order from. The suggestion must feel contextually relevant to their lifestyle, not random.

Respond in this exact JSON format and nothing else. No markdown, no backticks, just the raw JSON:
{{
  "current_categories": ["category1", "category2", "category3"],
  "shopping_pattern": "One sentence describing their shopping behavior, e.g. 'Weekly grocery shopper focused on cooking staples'",
  "basket_personality": "A short fun label like 'The Meal Prepper' or 'The Snack Enthusiast'",
  "suggested_product": "Specific product name available on Blinkit",
  "suggested_category": "The new category this belongs to",
  "price_estimate": "Price in rupees like '149' or '299'",
  "why_this_fits": "Two sentences explaining why this specific product connects to what they already buy. Be concrete, reference their actual basket items.",
  "social_proof": "A realistic neighborhood stat, e.g. 'Ordered by 280 households in your area this week'",
  "when_to_show": "The ideal moment to show this nudge in the shopping flow, e.g. 'Right after adding eggs to cart' or 'At checkout review screen'"
}}

Rules:
- The suggestion MUST be from a different category than anything in the basket
- Product must realistically exist on Blinkit
- Price must be under 500 rupees (low risk for a first try)
- Social proof stat should feel believable for a metro city neighborhood
- The "why_this_fits" must reference specific items from their basket, not be generic
- Keep language natural, no corporate buzzwords, no exclamation marks"""

        try:
            response = client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=600,
                messages=[{"role": "user", "content": prompt}],
            )

            raw = response.content[0].text.strip()
            raw = raw.replace("```json", "").replace("```", "").strip()
            result = json.loads(raw)

            # --- shopping pattern analysis ---
            st.markdown("---")
            st.markdown("### Your shopping pattern")

            p1, p2, p3 = st.columns(3)
            with p1:
                st.markdown(
                    f'<div class="pattern-box">'
                    f'<div class="pattern-label">Basket personality</div>'
                    f'<div class="pattern-value">{result["basket_personality"]}</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
            with p2:
                st.markdown(
                    f'<div class="pattern-box">'
                    f'<div class="pattern-label">Shopping pattern</div>'
                    f'<div class="pattern-value">{result["shopping_pattern"]}</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
            with p3:
                cat_chips = " ".join(
                    f'<span class="category-chip">{c}</span>'
                    for c in result["current_categories"]
                )
                st.markdown(
                    f'<div class="pattern-box">'
                    f'<div class="pattern-label">Your categories</div>'
                    f'{cat_chips}'
                    f'</div>',
                    unsafe_allow_html=True,
                )

            # --- the nudge card ---
            st.markdown("### The nudge you would see")
            st.markdown(
                f'<div class="nudge-card">'
                f'<div class="nudge-category">{result["suggested_category"]}</div>'
                f'<div class="nudge-title">{result["suggested_product"]}</div>'
                f'<div class="nudge-reason">{result["why_this_fits"]}</div>'
                f'<div class="social-proof">{result["social_proof"]}</div>'
                f'<div class="price-tag">Rs {result["price_estimate"]}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

            # --- placement ---
            st.markdown(
                f'<div class="how-section">'
                f'<div class="how-title">When this nudge appears</div>'
                f'<div class="how-text">{result["when_to_show"]}. '
                f'The suggestion is generated in real time based on the items in your cart, '
                f'not from a static banner or a pre-built list. This is what makes it '
                f'different from the promotions users currently ignore.</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

        except json.JSONDecodeError:
            st.error("The AI returned an unexpected format. Try again.")
        except Exception as e:
            st.error(f"Something went wrong: {e}")

elif analyze:
    st.warning("Enter at least a few items to analyze.")

# --- footer ---
st.markdown("---")
st.caption(
    "Built for the NextLeap PM Fellowship graduation project. "
    "This prototype demonstrates how an AI-powered cross-category nudge "
    "could work inside the Blinkit checkout flow. The recommendation is "
    "generated by Claude based on basket context, not a rules engine."
)
