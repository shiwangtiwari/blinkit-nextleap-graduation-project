"""
Blinkit Smart Basket - D3 MVP
Basket-aware cross-category discovery nudge inside a full iPhone mockup.

Deploy on Streamlit Community Cloud:
  1. Push to repo root of shiwangtiwari/blinkit-nextleap-graduation-project
  2. New app on share.streamlit.io  ->  main file: d3_smart_basket.py, branch: main
  3. Add ANTHROPIC_API_KEY in Advanced Settings > Secrets
"""

import streamlit as st
import json

st.set_page_config(page_title="Smart Basket | Blinkit", page_icon="🛒", layout="centered")

# ---------------------------------------------------------------------------
# Preset baskets
# ---------------------------------------------------------------------------
PRESETS = {
    "🥛 Morning Essentials": "Amul Taaza 1L, brown bread, eggs 6-pack, Nescafe Classic 50g, bananas",
    "🍳 Weekend Brunch": "paneer 200g, butter, pav, onions, tomatoes, green chillies",
    "👶 Baby & Home": "Huggies diapers M, Cerelac wheat 300g, Dettol handwash, Vim bar, garbage bags",
    "🥗 Health Kick": "oats 1kg, mixed dry fruits, skimmed milk 500ml, honey, green tea bags",
    "🍿 Movie Night": "Maggi 4-pack, Coca-Cola 750ml, Lay's classic, Hide & Seek, Amul cheese slice",
}

# ---------------------------------------------------------------------------
# CSS: background + phone bezel wrapping all Streamlit content
# ---------------------------------------------------------------------------
st.markdown("""
<style>
/* ---- Hide Streamlit chrome ---- */
#MainMenu, footer, header, .stDeployButton {display:none!important;}

/* ---- Warm background ---- */
[data-testid="stAppViewContainer"] {
    background: linear-gradient(160deg, #FDEBD0 0%, #F5CBA7 40%, #FAD7A0 100%);
}

/* ---- Phone bezel = the block-container itself ---- */
/* iPhone 15 Pro: 393 x 852 CSS px screen */
.block-container {
    max-width: 393px !important;
    width: 393px !important;
    height: 852px !important;
    background: #FFFFFF;
    border-radius: 52px;
    border: 12px solid #111;
    box-shadow:
        0 30px 70px rgba(0,0,0,0.22),
        inset 0 0 0 2px #333,
        0 0 0 1px #000;
    padding: 4px 20px 20px !important;
    margin-top: 24px !important;
    margin-bottom: 40px !important;
    position: relative;
    overflow-y: auto !important;
    overflow-x: hidden !important;
}
/* Hide scrollbar for real-phone feel (still scrollable) */
.block-container::-webkit-scrollbar { width: 0; display: none; }
.block-container { -ms-overflow-style: none; scrollbar-width: none; }

/* ---- Streamlit widget overrides to match iOS look ---- */
/* Text area */
[data-testid="stTextArea"] textarea {
    border: 1.5px solid #E0E0E0 !important;
    border-radius: 12px !important;
    font-size: 13.5px !important;
    font-family: -apple-system, BlinkMacSystemFont, sans-serif !important;
    background: #FAFAFA !important;
    color: #333 !important;
    padding: 12px 14px !important;
    resize: none !important;
}
[data-testid="stTextArea"] textarea:focus {
    border-color: #0C831F !important;
    background: #fff !important;
    box-shadow: none !important;
}
[data-testid="stTextArea"] label { display: none !important; }
[data-testid="stTextArea"] .stTextArea > div { padding: 0 !important; }

/* Primary button (Analyze) */
[data-testid="stButton"] button[kind="primary"],
.stButton button[kind="primaryFormSubmit"],
button[data-testid="stBaseButton-primary"] {
    background: #0C831F !important;
    color: #fff !important;
    border: none !important;
    border-radius: 12px !important;
    font-size: 15px !important;
    font-weight: 700 !important;
    font-family: -apple-system, BlinkMacSystemFont, sans-serif !important;
    padding: 12px 0 !important;
    letter-spacing: 0.2px;
    box-shadow: none !important;
}
button[data-testid="stBaseButton-primary"]:hover {
    background: #0a6e1a !important;
    border: none !important;
}
button[data-testid="stBaseButton-primary"]:disabled {
    background: #ccc !important;
    color: #999 !important;
}

/* Secondary/small buttons (presets + reset) */
button[data-testid="stBaseButton-secondary"] {
    background: #F5F5F5 !important;
    border: 1.5px solid #E0E0E0 !important;
    border-radius: 20px !important;
    font-size: 11px !important;
    font-family: -apple-system, BlinkMacSystemFont, sans-serif !important;
    color: #444 !important;
    padding: 6px 6px !important;
    box-shadow: none !important;
    white-space: nowrap;
}
button[data-testid="stBaseButton-secondary"]:hover {
    background: #FFF8E1 !important;
    border-color: #FFC727 !important;
    color: #1A1A2E !important;
}

/* Reduce gaps */
[data-testid="stVerticalBlock"] > div { gap: 0.4rem !important; }
[data-testid="stHorizontalBlock"] { gap: 0.35rem !important; }

/* Column padding reduction */
[data-testid="stColumn"] { padding: 0 2px !important; }

/* ---- Custom HTML elements ---- */
.dynamic-island {
    width: 120px; height: 34px;
    background: #111; border-radius: 20px;
    margin: 6px auto 0;
}
.status-bar {
    display: flex; justify-content: space-between; align-items: center;
    padding: 6px 12px 2px;
    font: 600 14px -apple-system, BlinkMacSystemFont, sans-serif;
    color: #1a1a1a;
}
.status-icons { display:flex; gap:5px; align-items:center; font-size:13px; }

.smart-banner {
    background: #FFC727; border-radius: 14px;
    padding: 14px 16px; margin: 6px 0 10px;
}
.smart-banner .dtag {
    font: 700 10px/1 -apple-system, sans-serif;
    letter-spacing: 0.8px; color: #1A1A2E; text-transform: uppercase;
}
.smart-banner h2 {
    margin: 3px 0 1px; font: 800 20px -apple-system, sans-serif; color: #1A1A2E;
}
.smart-banner .sub { font-size: 12.5px; color: #333; }

.sec-label {
    font: 700 11px/1 -apple-system, sans-serif;
    letter-spacing: 1px; color: #999; text-transform: uppercase;
    margin: 8px 0 4px;
}
.hint-label {
    font-size: 10px; color: #bbb; margin-bottom: 6px;
    font-family: -apple-system, sans-serif;
}

/* ---- Result cards ---- */
.basket-chips { display:flex; flex-wrap:wrap; gap:6px; margin:8px 0; }
.bchip {
    background:#F0F0F0; border-radius:16px; padding:5px 12px;
    font:500 11.5px -apple-system, sans-serif; color:#555;
}
.sug-title {
    font: 700 15px -apple-system, sans-serif; color: #1A1A2E; margin: 14px 0 2px;
}
.sug-sub { font-size: 12px; color: #888; margin-bottom: 10px; }

.pcard {
    background: #fff; border: 1.5px solid #EAEAEA; border-radius: 14px;
    padding: 14px 16px; margin-bottom: 10px;
    animation: cslide 0.4s ease forwards; opacity: 0;
}
.pcard:nth-child(1) { animation-delay: 0.1s; }
.pcard:nth-child(2) { animation-delay: 0.25s; }
.pcard:nth-child(3) { animation-delay: 0.4s; }
@keyframes cslide {
    from { opacity:0; transform:translateY(14px); }
    to   { opacity:1; transform:translateY(0); }
}
.pcard .pname { font: 700 14px -apple-system, sans-serif; color: #1A1A2E; }
.pcard .pprice { font: 600 13px -apple-system, sans-serif; color: #0C831F; margin: 2px 0 6px; }
.pcard .preason { font-size: 12px; color: #666; line-height: 1.45; margin-bottom: 8px; }
.pcard .psocial {
    font-size: 11px; color: #888; background: #F8F8F8;
    padding: 6px 10px; border-radius: 8px; display: inline-block;
}
.pcard .addbtn {
    float: right; background: #0C831F; color: #fff; border: none;
    border-radius: 8px; padding: 6px 16px; font: 700 12px -apple-system, sans-serif;
    cursor: pointer; margin-top: -30px;
}

.mnote {
    margin: 14px 0 0; padding: 10px 14px; background: #F9F9F9;
    border-radius: 10px; font: 400 11px/1.5 -apple-system, sans-serif; color: #999;
}

.home-ind {
    width: 134px; height: 5px; background: #222;
    border-radius: 3px; margin: 18px auto 6px;
}

/* Loading */
.ld-wrap { text-align:center; padding:44px 0; }
.ld-spin {
    width:36px; height:36px; border:3px solid #E0E0E0; border-top-color:#0C831F;
    border-radius:50%; animation:sp .8s linear infinite; margin:0 auto 14px;
}
@keyframes sp { to{transform:rotate(360deg)} }
.ld-wrap p { font:400 13px -apple-system,sans-serif; color:#888; }

/* ---- Footer outside phone ---- */
.pgfoot {
    text-align:center; padding:0 0 28px;
    font: 400 12px -apple-system, sans-serif; color: #bbb;
    max-width: 390px; margin: 0 auto;
}
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Claude API
# ---------------------------------------------------------------------------
def get_suggestions(basket_text: str) -> dict:
    prompt = f"""You are Blinkit's Smart Basket engine. A user's typical basket is:
{basket_text}

Analyze which product CATEGORIES they already buy from. Then suggest exactly 3 products
from DIFFERENT categories they are NOT buying from. Each suggestion must:
- Be a real product available on Blinkit (Indian quick-commerce)
- Come from a category absent from their basket
- Include a contextual reason tied to their basket items
- Include realistic social proof data

Respond ONLY with this JSON (no markdown, no backticks, no extra text):
{{
  "basket_categories": ["category1", "category2"],
  "suggestions": [
    {{
      "product_name": "Exact product name with brand and size",
      "price": "price in rupees like 49, 129, etc",
      "category": "category this belongs to",
      "reason": "One line connecting this to their existing basket habits",
      "social_proof": "Stat like: 73% of similar baskets add this"
    }},
    {{
      "product_name": "...",
      "price": "...",
      "category": "...",
      "reason": "...",
      "social_proof": "..."
    }},
    {{
      "product_name": "...",
      "price": "...",
      "category": "...",
      "reason": "...",
      "social_proof": "..."
    }}
  ]
}}"""
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])
        resp = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=800,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = resp.content[0].text.strip()
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1]
        if raw.endswith("```"):
            raw = raw.rsplit("```", 1)[0]
        return json.loads(raw.strip())
    except Exception:
        return _fallback(basket_text)


def _fallback(bt: str) -> dict:
    bl = bt.lower()
    if any(w in bl for w in ["milk", "bread", "egg", "nescafe", "banana"]):
        return {
            "basket_categories": ["Dairy", "Bakery", "Breakfast", "Fruits"],
            "suggestions": [
                {"product_name": "Saffola Oats 1kg", "price": "169", "category": "Health Foods",
                 "reason": "Pairs with your morning milk and banana for a complete breakfast",
                 "social_proof": "68% of breakfast-basket shoppers add oats within 2 weeks"},
                {"product_name": "Vim Dishwash Gel 500ml", "price": "99", "category": "Cleaning",
                 "reason": "Daily cooking means daily dishes; most milk+bread buyers restock cleaning monthly",
                 "social_proof": "Added by 4 out of 5 similar households this week"},
                {"product_name": "Yogabar Muesli 400g", "price": "249", "category": "Snacks & Cereals",
                 "reason": "Goes with the milk you already order; a no-cook breakfast for rushed mornings",
                 "social_proof": "Trending in your area: 3x orders this month vs last"},
            ],
        }
    elif any(w in bl for w in ["paneer", "butter", "pav", "onion"]):
        return {
            "basket_categories": ["Dairy", "Bakery", "Vegetables"],
            "suggestions": [
                {"product_name": "MDH Pav Bhaji Masala 100g", "price": "56", "category": "Spices",
                 "reason": "You have pav, butter, and onions; this completes a classic pav bhaji",
                 "social_proof": "91% of pav-buyers also order this masala"},
                {"product_name": "Paper Boat Aamras 200ml (3-pack)", "price": "60", "category": "Beverages",
                 "reason": "A cold side drink for your weekend brunch spread",
                 "social_proof": "Weekend beverage orders up 45% in your pincode"},
                {"product_name": "Amul Lassi Mango 200ml (4-pack)", "price": "80", "category": "Dairy Beverages",
                 "reason": "Complements a heavy paneer meal; ready-to-drink, no prep",
                 "social_proof": "Bought together with paneer in 58% of weekend baskets"},
            ],
        }
    elif any(w in bl for w in ["diaper", "huggies", "cerelac", "baby", "dettol"]):
        return {
            "basket_categories": ["Baby Care", "Cleaning", "Hygiene"],
            "suggestions": [
                {"product_name": "Himalaya Baby Lotion 200ml", "price": "145", "category": "Baby Skin Care",
                 "reason": "Most diaper buyers also need baby skin care in the same restock cycle",
                 "social_proof": "72% of Huggies buyers add a baby lotion to their cart"},
                {"product_name": "Good Knight Gold Flash Refill", "price": "89", "category": "Home Protection",
                 "reason": "Baby in the house means extra mosquito protection matters",
                 "social_proof": "Top-selling home care add-on for baby households"},
                {"product_name": "Real Fruit Power Mixed Fruit 1L", "price": "99", "category": "Beverages",
                 "reason": "A quick drink for you while managing baby routines",
                 "social_proof": "Added by 3 in 5 parents during their baby-care restock"},
            ],
        }
    elif any(w in bl for w in ["oats", "dry fruit", "honey", "green tea", "skim"]):
        return {
            "basket_categories": ["Health Foods", "Dry Fruits", "Dairy", "Beverages"],
            "suggestions": [
                {"product_name": "Peanut Butter Crunchy 400g (MyFitness)", "price": "269", "category": "Spreads",
                 "reason": "High protein spread that pairs with your oats and health-first basket",
                 "social_proof": "65% of oats buyers add a protein spread within 3 orders"},
                {"product_name": "Epigamia Greek Yogurt Strawberry 90g", "price": "45", "category": "Dairy Snacks",
                 "reason": "Protein-rich snack that fits your health-conscious pattern",
                 "social_proof": "Trending: health basket shoppers order 2x more yogurt"},
                {"product_name": "Chia Seeds 200g (True Elements)", "price": "159", "category": "Superfoods",
                 "reason": "Add to your oats or smoothie; complements your dry fruits",
                 "social_proof": "Bought together with oats in 48% of health baskets"},
            ],
        }
    else:
        return {
            "basket_categories": ["Grocery", "Staples"],
            "suggestions": [
                {"product_name": "Tata Sampann Chana Dal 1kg", "price": "135", "category": "Pulses",
                 "reason": "A pantry staple that pairs with your existing grocery items",
                 "social_proof": "72% of similar baskets include a dal or lentil"},
                {"product_name": "Surf Excel Matic Liquid 1L", "price": "225", "category": "Household Care",
                 "reason": "Most grocery shoppers batch household refills on the same order",
                 "social_proof": "Saves an extra delivery; added by 3 in 5 weekly shoppers"},
                {"product_name": "Cadbury Dairy Milk Silk 150g", "price": "160", "category": "Chocolates",
                 "reason": "A treat to go with your essentials run; top impulse add at checkout",
                 "social_proof": "Top impulse add in your area this week"},
            ],
        }


# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------
if "basket" not in st.session_state:
    st.session_state.basket = ""
if "ta" not in st.session_state:
    st.session_state.ta = ""
if "results" not in st.session_state:
    st.session_state.results = None
if "phase" not in st.session_state:
    st.session_state.phase = "input"  # input | loading | results


# ---------------------------------------------------------------------------
# PHONE CONTENT
# ---------------------------------------------------------------------------

# Dynamic Island + Status Bar (always shown)
st.markdown("""
<div class="dynamic-island"></div>
<div class="status-bar">
    <span>9:41</span>
    <span class="status-icons">
        <span>●●●●</span>
        <span style="color:#0C831F;">▐</span>
    </span>
</div>
""", unsafe_allow_html=True)

# ---------- LOADING PHASE ----------
if st.session_state.phase == "loading":
    st.markdown("""
    <div class="smart-banner">
        <div class="dtag">DELIVERY IN 8 MINUTES</div>
        <h2>Smart Basket</h2>
        <div class="sub">Analyzing your basket...</div>
    </div>
    <div class="ld-wrap">
        <div class="ld-spin"></div>
        <p>Finding products from categories you haven't tried</p>
    </div>
    """, unsafe_allow_html=True)

    data = get_suggestions(st.session_state.basket)
    st.session_state.results = data
    st.session_state.phase = "results"
    st.rerun()

# ---------- RESULTS PHASE ----------
elif st.session_state.phase == "results" and st.session_state.results:
    data = st.session_state.results
    items = [i.strip() for i in st.session_state.basket.split(",") if i.strip()]
    chips = "".join(f'<span class="bchip">{it}</span>' for it in items)
    cats = ", ".join(data.get("basket_categories", []))

    cards = ""
    for s in data.get("suggestions", []):
        cards += f"""
        <div class="pcard">
            <div class="pname">{s['product_name']}</div>
            <div class="pprice">₹{s['price']}</div>
            <span class="addbtn">+ ADD</span>
            <div class="preason">{s['reason']}</div>
            <div class="psocial">📊 {s['social_proof']}</div>
        </div>"""

    st.markdown(f"""
    <div class="smart-banner">
        <div class="dtag">DELIVERY IN 8 MINUTES</div>
        <h2>Smart Basket</h2>
        <div class="sub">Here's what we found for you</div>
    </div>

    <div class="sec-label">Your basket</div>
    <div class="basket-chips">{chips}</div>

    <div class="sug-title">You might also need</div>
    <div class="sug-sub">Based on your {cats} basket · Pick any to add</div>

    {cards}

    <div class="mnote">
        Built on Blinkit review analysis (1,718 reviews, 10 themes). Discovery friction
        is just 2.3% of complaints because users never attempt it. Smart Basket meets them
        at checkout, the highest-intent moment, with contextual cross-category nudges.
    </div>
    """, unsafe_allow_html=True)

    # Reset button
    if st.button("← Try another basket", use_container_width=True):
        st.session_state.basket = ""
        st.session_state.ta = ""
        st.session_state.results = None
        st.session_state.phase = "input"
        st.rerun()

# ---------- INPUT PHASE ----------
else:
    st.markdown("""
    <div class="smart-banner">
        <div class="dtag">DELIVERY IN 8 MINUTES</div>
        <h2>Smart Basket</h2>
        <div class="sub">One new find, matched to how you already shop</div>
    </div>
    <div class="sec-label">Your usual basket</div>
    <div class="hint-label">Tap a preset or type your own</div>
    """, unsafe_allow_html=True)

    # Preset chips as Streamlit buttons (2 rows)
    labels = list(PRESETS.keys())
    row1 = st.columns(3)
    for i, col in enumerate(row1):
        if i < len(labels):
            with col:
                if st.button(labels[i], key=f"p{i}", use_container_width=True):
                    st.session_state.ta = PRESETS[labels[i]]
                    st.session_state.basket = PRESETS[labels[i]]
                    st.rerun()
    row2 = st.columns(3)
    for i, col in enumerate(row2):
        idx = i + 3
        if idx < len(labels):
            with col:
                if st.button(labels[idx], key=f"p{idx}", use_container_width=True):
                    st.session_state.ta = PRESETS[labels[idx]]
                    st.session_state.basket = PRESETS[labels[idx]]
                    st.rerun()

    # Text area - use ONLY key (no value= param) so widget state stays in sync
    typed = st.text_area(
        "basket",
        placeholder="e.g. Amul milk 1L, brown bread, bananas, Maggi, Tata Salt, curd 400g",
        height=72,
        key="ta",
        label_visibility="collapsed",
    )
    st.session_state.basket = typed

    # Analyze button
    if st.button(
        "Analyze my basket →",
        type="primary",
        use_container_width=True,
        disabled=not st.session_state.basket.strip(),
    ):
        st.session_state.phase = "loading"
        st.rerun()


# Home indicator
st.markdown('<div class="home-ind"></div>', unsafe_allow_html=True)

# Footer (outside phone via negative margin trick)
st.markdown("""
<div class="pgfoot" style="margin-top:30px;">
    Built for the NextLeap PM Fellowship · D3 MVP · Powered by Claude
</div>
""", unsafe_allow_html=True)
