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

/* ---- iPhone 15 Pro status bar + Dynamic Island ---- */
.iphone-top {
    position: relative;
    height: 54px;
    margin: 2px 0 0;
}
.dynamic-island {
    width: 126px; height: 36px;
    background: #111; border-radius: 20px;
    position: absolute;
    top: 4px; left: 50%; transform: translateX(-50%);
    z-index: 2;
}
.status-time {
    position: absolute;
    top: 12px; left: 16px;
    font: 600 15px/1 -apple-system, BlinkMacSystemFont, 'SF Pro Text', sans-serif;
    color: #1a1a1a;
    z-index: 1;
    letter-spacing: 0.2px;
}
.status-icons {
    position: absolute;
    top: 10px; right: 14px;
    display: flex; gap: 6px; align-items: center;
    z-index: 1;
}

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
    prompt = (
        "You are Blinkit's Smart Basket engine. The company's strategic goal is:\n"
        "INCREASE the percentage of users who purchase from at least one NEW CATEGORY every month.\n\n"
        "Blinkit has these TOP-LEVEL categories (treat as distinct groups):\n"
        "1. Dairy, Bread & Eggs\n"
        "2. Fruits & Vegetables\n"
        "3. Snacks & Munchies\n"
        "4. Cold Drinks & Juices\n"
        "5. Instant & Frozen Food\n"
        "6. Sweet Tooth (chocolates, cakes, ice cream, desserts)\n"
        "7. Atta, Rice, Dal & Dry Fruits\n"
        "8. Masala, Oil & More\n"
        "9. Cleaning Essentials\n"
        "10. Personal Care (skincare, haircare, grooming, oral care)\n"
        "11. Baby Care\n"
        "12. Pet Care\n"
        "13. Pharmacy & Wellness\n"
        "14. Home & Office\n"
        "15. Electronics & Accessories\n"
        "16. Meat, Fish & Eggs\n"
        "17. Paan Corner & Fragrances\n"
        "18. Print Store & Stationery\n\n"
        f"A user's typical basket is:\n{basket_text}\n\n"
        "STEP 1: Map every basket item to its top-level category number from the list above.\n"
        "STEP 2: Identify which top-level categories are ABSENT from the basket.\n"
        "STEP 3: Suggest exactly 3 products, each from a DIFFERENT absent top-level category.\n\n"
        "CRITICAL RULES:\n"
        "- Each suggestion MUST come from a genuinely different top-level category that the user "
        "has NEVER bought from. Do NOT suggest items from the same or adjacent food categories.\n"
        "- Example: if basket has cake, milk, chocolate -> those are Sweet Tooth + Dairy. "
        "Do NOT suggest cookies, sprinkles, or biscuits (still Sweet Tooth/Snacks). "
        "Instead suggest from Cleaning, Personal Care, Pharmacy, Home & Office, etc.\n"
        "- The reason should bridge the basket context to the new category naturally.\n"
        "- Include realistic social proof.\n\n"
        "Respond ONLY with this JSON (no markdown, no backticks, no extra text):\n"
        '{"basket_categories":["Dairy, Bread & Eggs","Sweet Tooth"],"suggestions":['
        '{"product_name":"Brand Product Size","price":"99","category":"Cleaning Essentials",'
        '"reason":"One line bridging basket to this new category","social_proof":"Stat"},'
        '{"product_name":"...","price":"...","category":"...","reason":"...","social_proof":"..."},'
        '{"product_name":"...","price":"...","category":"...","reason":"...","social_proof":"..."}'
        "]}"
    )
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])
        resp = client.messages.create(
            model="claude-haiku-4-5",
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
        # Basket = Dairy + Bakery + Fruits + Instant Food
        return {
            "basket_categories": ["Dairy, Bread & Eggs", "Fruits & Vegetables", "Instant & Frozen Food"],
            "suggestions": [
                {"product_name": "Dettol Handwash Original 200ml", "price": "55", "category": "Personal Care",
                 "reason": "Breakfast prep means hands in food every morning; handwash sits right at the kitchen sink",
                 "social_proof": "74% of daily-dairy buyers also restock personal care monthly"},
                {"product_name": "Vim Dishwash Gel 500ml", "price": "99", "category": "Cleaning Essentials",
                 "reason": "Daily milk and eggs means daily dishes; cleaning restocks align with your grocery cycle",
                 "social_proof": "Added by 4 out of 5 similar households this week"},
                {"product_name": "Crocin Advance 10 tablets", "price": "25", "category": "Pharmacy & Wellness",
                 "reason": "A medicine-cabinet staple you can add while you are already ordering essentials",
                 "social_proof": "62% of weekly grocery shoppers batch their pharmacy refills too"},
            ],
        }
    elif any(w in bl for w in ["paneer", "butter", "pav", "onion"]):
        # Basket = Dairy + Bakery + Vegetables
        return {
            "basket_categories": ["Dairy, Bread & Eggs", "Fruits & Vegetables"],
            "suggestions": [
                {"product_name": "Scotch-Brite Scrub Pad (3-pack)", "price": "49", "category": "Cleaning Essentials",
                 "reason": "Heavy cooking like pav bhaji leaves greasy pans; scrub pads are the first thing to run out",
                 "social_proof": "83% of weekend-cooking baskets include a cleaning add-on"},
                {"product_name": "Nivea Soft Cream 100ml", "price": "149", "category": "Personal Care",
                 "reason": "Kitchen heat dries skin out; a moisturizer is an easy personal care add while ordering",
                 "social_proof": "Personal care adoption up 38% among users who started with grocery"},
                {"product_name": "Classmate Notebook 180 pages", "price": "60", "category": "Print Store & Stationery",
                 "reason": "If you have school-age kids at home eating pav bhaji, they probably need notebooks too",
                 "social_proof": "Stationery is the fastest-growing cross-category add for family households"},
            ],
        }
    elif any(w in bl for w in ["diaper", "huggies", "cerelac", "baby", "dettol"]):
        # Basket = Baby Care + Cleaning
        return {
            "basket_categories": ["Baby Care", "Cleaning Essentials"],
            "suggestions": [
                {"product_name": "Good Knight Gold Flash Refill", "price": "89", "category": "Home & Office",
                 "reason": "Baby in the house means extra mosquito protection matters",
                 "social_proof": "Top-selling home add-on for baby-care households"},
                {"product_name": "Pedigree Puppy Food 400g", "price": "99", "category": "Pet Care",
                 "reason": "Families with babies often also have pets; batch your care-routine orders",
                 "social_proof": "Pet care adoption is 2.3x higher in households that already buy baby care"},
                {"product_name": "Colgate MaxFresh Toothpaste 150g", "price": "95", "category": "Personal Care",
                 "reason": "Running low on toothpaste? Add personal care while your baby-care order ships",
                 "social_proof": "58% of baby-care buyers add a personal care item within their first month"},
            ],
        }
    elif any(w in bl for w in ["oats", "dry fruit", "honey", "green tea", "skim"]):
        # Basket = Health Foods + Dry Fruits + Dairy + Beverages
        return {
            "basket_categories": ["Atta, Rice, Dal & Dry Fruits", "Dairy, Bread & Eggs", "Cold Drinks & Juices"],
            "suggestions": [
                {"product_name": "Himalaya Purifying Neem Face Wash 150ml", "price": "130", "category": "Personal Care",
                 "reason": "Health-conscious inside and out; face wash is the top personal care add for health-food buyers",
                 "social_proof": "65% of health-food buyers add a personal care product within 3 orders"},
                {"product_name": "Odonil Air Freshener 75g (2-pack)", "price": "99", "category": "Home & Office",
                 "reason": "You care about what goes into your body; makes sense to care about your living space too",
                 "social_proof": "Home freshener adoption up 42% among wellness-focused shoppers"},
                {"product_name": "Whiskas Cat Food Tuna 85g (3-pack)", "price": "105", "category": "Pet Care",
                 "reason": "Health-first shoppers are 2x more likely to also care for pets; batch your care orders",
                 "social_proof": "Pet care is the top new-category entry for health-conscious users"},
            ],
        }
    elif any(w in bl for w in ["cake", "chocolate", "milkshake", "cookie", "ice cream", "sweet"]):
        # Basket = Sweet Tooth + possibly Dairy
        return {
            "basket_categories": ["Sweet Tooth", "Dairy, Bread & Eggs"],
            "suggestions": [
                {"product_name": "Closeup Toothpaste Menthol Fresh 150g", "price": "89", "category": "Personal Care",
                 "reason": "All that cake and chocolate calls for a fresh mouth after; oral care is a natural add",
                 "social_proof": "71% of sweet-tooth buyers also purchase oral care monthly"},
                {"product_name": "Harpic Powerplus 500ml", "price": "79", "category": "Cleaning Essentials",
                 "reason": "You are already ordering home delivery; add household cleaning to skip a separate trip",
                 "social_proof": "Cleaning products are the #1 cross-category add for dessert buyers"},
                {"product_name": "Moov Pain Relief Spray 50g", "price": "130", "category": "Pharmacy & Wellness",
                 "reason": "A medicine-cabinet essential you can add while your dessert order is on the way",
                 "social_proof": "48% of users add pharmacy items once they realize Blinkit stocks them"},
            ],
        }
    elif any(w in bl for w in ["maggi", "cola", "lay", "chips", "pepsi", "coke", "biscuit"]):
        # Basket = Snacks + Beverages + Instant Food
        return {
            "basket_categories": ["Snacks & Munchies", "Cold Drinks & Juices", "Instant & Frozen Food"],
            "suggestions": [
                {"product_name": "Set Wet Hair Gel 100ml", "price": "99", "category": "Personal Care",
                 "reason": "Movie night sorted, but grooming is another routine you can batch on Blinkit",
                 "social_proof": "Personal care is the #1 new category snack-buyers expand into"},
                {"product_name": "Lizol Floor Cleaner Citrus 500ml", "price": "89", "category": "Cleaning Essentials",
                 "reason": "Snack crumbs and cola spills mean the floor needs attention; add cleaning to the same order",
                 "social_proof": "67% of snack-heavy baskets add a cleaning item within 2 orders"},
                {"product_name": "Duracell AA Batteries (4-pack)", "price": "130", "category": "Electronics & Accessories",
                 "reason": "Batteries for your remote, torch, or gaming controller; never run out mid-movie-night",
                 "social_proof": "Electronics is the fastest-growing add-on category for young-adult baskets"},
            ],
        }
    else:
        # Generic basket
        return {
            "basket_categories": ["Grocery", "Staples"],
            "suggestions": [
                {"product_name": "Surf Excel Matic Liquid 1L", "price": "225", "category": "Cleaning Essentials",
                 "reason": "Most grocery shoppers batch household refills on the same order to save a delivery",
                 "social_proof": "Cleaning is the #1 new category grocery-only users expand into"},
                {"product_name": "Garnier Men Face Wash 100ml", "price": "115", "category": "Personal Care",
                 "reason": "Personal care is a daily essential just like your groceries; skip the separate trip",
                 "social_proof": "39% of grocery-first users add personal care within their first month"},
                {"product_name": "Vicks Inhaler", "price": "35", "category": "Pharmacy & Wellness",
                 "reason": "A medicine-cabinet staple you probably need; add it while ordering anyway",
                 "social_proof": "Pharmacy adoption jumps 4x once users realize Blinkit delivers it in 10 min"},
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
    st.session_state.phase = "input"  # input | results


# ---------------------------------------------------------------------------
# PHONE CONTENT
# ---------------------------------------------------------------------------

# iPhone status bar + Dynamic Island (always shown)
st.markdown("""
<div class="iphone-top">
    <span class="status-time">9:41</span>
    <div class="dynamic-island"></div>
    <div class="status-icons">
        <!-- Signal bars -->
        <svg width="17" height="12" viewBox="0 0 17 12" fill="none" xmlns="http://www.w3.org/2000/svg">
            <rect x="0" y="9" width="3" height="3" rx="0.5" fill="#1a1a1a"/>
            <rect x="4.5" y="6" width="3" height="6" rx="0.5" fill="#1a1a1a"/>
            <rect x="9" y="3" width="3" height="9" rx="0.5" fill="#1a1a1a"/>
            <rect x="13.5" y="0" width="3" height="12" rx="0.5" fill="#1a1a1a"/>
        </svg>
        <!-- WiFi -->
        <svg width="16" height="12" viewBox="0 0 16 12" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M8 10.5a1.2 1.2 0 110 2.4 1.2 1.2 0 010-2.4z" fill="#1a1a1a" transform="translate(0,-1.5)"/>
            <path d="M4.7 9.3a4.7 4.7 0 016.6 0" stroke="#1a1a1a" stroke-width="1.4" stroke-linecap="round" fill="none" transform="translate(0,-1.5)"/>
            <path d="M2 6.5a8.5 8.5 0 0112 0" stroke="#1a1a1a" stroke-width="1.4" stroke-linecap="round" fill="none" transform="translate(0,-1.5)"/>
            <path d="M-.2 3.8a12 12 0 0116.4 0" stroke="#1a1a1a" stroke-width="1.4" stroke-linecap="round" fill="none" transform="translate(0,-1.5)"/>
        </svg>
        <!-- Battery -->
        <svg width="27" height="13" viewBox="0 0 27 13" fill="none" xmlns="http://www.w3.org/2000/svg">
            <rect x="0.5" y="0.5" width="22" height="12" rx="2.5" stroke="#1a1a1a" stroke-opacity="0.35"/>
            <rect x="2" y="2" width="17" height="9" rx="1.5" fill="#0C831F"/>
            <path d="M24 4.5v4a2 2 0 000-4z" fill="#1a1a1a" fill-opacity="0.4"/>
        </svg>
    </div>
</div>
""", unsafe_allow_html=True)

# ---------- RESULTS PHASE ----------
if st.session_state.phase == "results" and st.session_state.results:
    data = st.session_state.results
    items = [i.strip() for i in st.session_state.basket.split(",") if i.strip()]
    chips = "".join(f'<span class="bchip">{it}</span>' for it in items)
    cats = ", ".join(data.get("basket_categories", []))

    cards = ""
    for s in data.get("suggestions", []):
        cards += (
            '<div class="pcard">'
            f'<div class="pname">{s["product_name"]}</div>'
            f'<div class="pprice">₹{s["price"]}</div>'
            '<span class="addbtn">+ ADD</span>'
            f'<div class="preason">{s["reason"]}</div>'
            f'<div class="psocial">📊 {s["social_proof"]}</div>'
            '</div>'
        )

    st.markdown(
        '<div class="smart-banner">'
        '<div class="dtag">DELIVERY IN 8 MINUTES</div>'
        '<h2>Smart Basket</h2>'
        '<div class="sub">Here\'s what we found for you</div>'
        '</div>'
        '<div class="sec-label">Your basket</div>'
        f'<div class="basket-chips">{chips}</div>'
        '<div class="sug-title">You might also need</div>'
        f'<div class="sug-sub">Based on your {cats} basket · Pick any to add</div>'
        f'{cards}'
        '<div class="mnote">'
        'Built on Blinkit review analysis (1,718 reviews, 10 themes). Discovery friction '
        'is just 2.3% of complaints because users never attempt it. Smart Basket meets them '
        'at checkout, the highest-intent moment, with contextual cross-category nudges.'
        '</div>',
        unsafe_allow_html=True,
    )

    # Reset button
    if st.button("← Try another basket", use_container_width=True):
        st.session_state.basket = ""
        st.session_state.ta = ""
        st.session_state.results = None
        st.session_state.phase = "input"
        st.rerun()

# ---------- INPUT PHASE ----------
else:
    st.markdown(
        '<div class="smart-banner">'
        '<div class="dtag">DELIVERY IN 8 MINUTES</div>'
        '<h2>Smart Basket</h2>'
        '<div class="sub">One new find, matched to how you already shop</div>'
        '</div>'
        '<div class="sec-label">Your usual basket</div>'
        '<div class="hint-label">Tap a preset or type your own</div>',
        unsafe_allow_html=True,
    )

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

    # Analyze button - calls API inline, no separate loading phase
    if st.button(
        "Analyze my basket →",
        type="primary",
        use_container_width=True,
        disabled=not st.session_state.basket.strip(),
    ):
        with st.spinner("Finding suggestions..."):
            data = get_suggestions(st.session_state.basket)
        st.session_state.results = data
        st.session_state.phase = "results"
        st.rerun()


# Home indicator
st.markdown('<div class="home-ind"></div>', unsafe_allow_html=True)

# Footer
st.markdown(
    '<div class="pgfoot">Built for the NextLeap PM Fellowship · D3 MVP · Powered by Claude</div>',
    unsafe_allow_html=True,
)
