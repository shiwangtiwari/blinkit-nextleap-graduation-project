"""
Blinkit Smart Basket - AI-native MVP (D3)
Basket-aware cross-category discovery nudge, rendered inside an iPhone mockup.

Deploy on Streamlit Community Cloud:
  1. Push this file to the repo root of shiwangtiwari/blinkit-nextleap-graduation-project
  2. New app on share.streamlit.io, main file path: d3_smart_basket.py, branch: main
  3. Advanced Settings > Secrets:  ANTHROPIC_API_KEY = "sk-ant-your-key"
  4. requirements.txt at repo root must include: streamlit and anthropic
"""

import json
import re

import streamlit as st

st.set_page_config(
    page_title="Smart Basket | Blinkit",
    page_icon="\U0001F6D2",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ---------------------------------------------------------------- CSS

PHONE_CSS = """
<style>
    /* strip streamlit chrome */
    #MainMenu, header, footer, .stDeployButton,
    [data-testid="stToolbar"],
    [data-testid="stDecoration"],
    [data-testid="stStatusWidget"] { display: none !important; }

    .stApp {
        background: linear-gradient(160deg, #FFF5E6 0%, #FFE8CC 30%, #FFDAB3 60%, #FFD0A0 100%) !important;
    }

    .block-container {
        max-width: 430px !important;
        margin: 0 auto !important;
        padding: 1.2rem 12px 2rem !important;
    }

    @keyframes fadeDown {
        from { opacity: 0; transform: translateY(-14px); }
        to   { opacity: 1; transform: translateY(0); }
    }
    @keyframes phoneFloat {
        from { opacity: 0; transform: translateY(26px) scale(0.97); }
        to   { opacity: 1; transform: translateY(0) scale(1); }
    }
    @keyframes slideUp {
        from { opacity: 0; transform: translateY(22px); }
        to   { opacity: 1; transform: translateY(0); }
    }

    /* brand header above the phone */
    .brand-header { text-align: center; padding: 4px 0 14px; animation: fadeDown 0.6s ease-out; }
    .brand-logo {
        display: inline-block; background: #FFC727; color: #1A1A2E;
        font-family: Arial, sans-serif; font-weight: 900; font-size: 26px;
        padding: 7px 24px; border-radius: 10px; letter-spacing: -0.5px;
    }
    .brand-tagline {
        color: #7A6A5A; font-family: 'Segoe UI', system-ui, sans-serif;
        font-size: 13px; margin-top: 7px;
    }

    /* iPhone bezel */
    .iphone-frame {
        background: #000; border-radius: 50px; padding: 11px;
        box-shadow: 0 22px 55px rgba(0,0,0,0.20), 0 6px 16px rgba(0,0,0,0.10),
                    inset 0 0 0 1.5px #444;
        animation: phoneFloat 0.7s ease-out;
    }
    .iphone-screen {
        background: #FFFFFF; border-radius: 40px; overflow: hidden;
        padding: 10px 0 6px;
    }
    .dynamic-island {
        width: 112px; height: 30px; background: #000;
        border-radius: 18px; margin: 2px auto 0;
    }
    .status-bar {
        display: flex; justify-content: space-between; align-items: center;
        padding: 0 26px; margin-top: -30px; height: 30px;
        font-family: -apple-system, 'Segoe UI', sans-serif;
        font-size: 13px; font-weight: 600; color: #1A1A2E;
    }
    .app-body { padding: 14px 18px 10px; font-family: 'Segoe UI', system-ui, sans-serif; }

    /* in-app blinkit top bar */
    .app-topbar {
        background: #FFC727; border-radius: 14px; padding: 12px 14px; margin-bottom: 14px;
    }
    .app-topbar .t1 { font-size: 11px; font-weight: 700; color: #1A1A2E; letter-spacing: 0.4px; }
    .app-topbar .t2 { font-size: 17px; font-weight: 900; color: #1A1A2E; }
    .app-topbar .t3 { font-size: 11px; color: #4A4A3A; margin-top: 1px; }

    .section-label {
        font-size: 12px; font-weight: 700; color: #666;
        letter-spacing: 0.6px; text-transform: uppercase; margin: 4px 0 6px;
    }

    /* basket chips */
    .chip-row { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 10px; }
    .chip {
        background: #F2F7F2; border: 1px solid #D7E8D7; color: #1A1A2E;
        border-radius: 16px; padding: 4px 11px; font-size: 12.5px;
        animation: slideUp 0.4s ease-out;
    }

    /* result card */
    .nudge-card {
        background: linear-gradient(150deg, #F3FBF3 0%, #E8F6E8 100%);
        border: 1.5px solid #0C831F; border-radius: 18px;
        padding: 16px; margin-top: 14px;
        animation: slideUp 0.55s ease-out;
    }
    .nudge-eyebrow {
        display: inline-block; background: #0C831F; color: #fff;
        font-size: 10.5px; font-weight: 700; letter-spacing: 0.5px;
        padding: 3px 10px; border-radius: 10px; text-transform: uppercase;
    }
    .nudge-product { font-size: 19px; font-weight: 800; color: #1A1A2E; margin: 9px 0 2px; }
    .nudge-cat { font-size: 12px; color: #0C831F; font-weight: 700; margin-bottom: 8px; }
    .nudge-reason { font-size: 13.5px; color: #333; line-height: 1.5; }
    .social-proof {
        background: #FFF9E8; border: 1px solid #FFE7A0; border-radius: 12px;
        padding: 9px 12px; margin-top: 10px; font-size: 12.5px; color: #6B5A1E;
        animation: slideUp 0.7s ease-out;
    }
    .price-line {
        display: flex; justify-content: space-between; align-items: center;
        margin-top: 12px; animation: slideUp 0.85s ease-out;
    }
    .price-tag { font-size: 17px; font-weight: 800; color: #1A1A2E; }
    .add-btn {
        background: #0C831F; color: #fff; font-weight: 700; font-size: 13px;
        padding: 8px 20px; border-radius: 10px;
    }
    .method-note {
        font-size: 11px; color: #999; margin-top: 12px; line-height: 1.45;
        animation: slideUp 1.0s ease-out;
    }

    /* streamlit widget skinning inside phone */
    .stTextArea textarea {
        border-radius: 14px !important; border: 1.5px solid #E0E0E0 !important;
        font-size: 14px !important; background: #FAFAFA !important;
    }
    .stTextArea textarea:focus { border-color: #0C831F !important; box-shadow: none !important; }
    .stButton > button {
        background: #0C831F !important; color: #fff !important;
        border: none !important; border-radius: 14px !important;
        font-weight: 800 !important; font-size: 15px !important;
        padding: 0.6rem 1rem !important; width: 100%;
        transition: transform 0.12s ease, filter 0.12s ease;
    }
    .stButton > button:hover { filter: brightness(1.08); transform: translateY(-1px); }
    .footer-note {
        text-align: center; font-size: 11.5px; color: #9A8A78; margin-top: 16px;
        font-family: 'Segoe UI', system-ui, sans-serif; animation: fadeDown 0.8s ease-out;
    }
</style>
"""

st.markdown(PHONE_CSS, unsafe_allow_html=True)

# ---------------------------------------------------------------- AI

SYSTEM_PROMPT = """You are Blinkit's Smart Basket engine. The user gives their typical
Blinkit basket. Your job: suggest exactly ONE product from a category NOT already in
their basket that fits their household pattern. Ground the suggestion in what the
basket reveals (household size, diet, routines). Keep it realistic for Indian quick
commerce (Blinkit catalog style items, INR pricing).

Respond ONLY with valid JSON, no markdown fences, no preamble:
{
  "basket_read": "one sentence on what this basket says about the household",
  "product": "specific product name with brand and size",
  "category": "the new category it belongs to",
  "reason": "2 sentences, second person, why this fits their routine",
  "social_proof": "one realistic line like 'X% of shoppers in your city who buy <anchor item> also ordered this' with a plausible number between 18 and 42",
  "price_inr": 149
}"""

DEMO_RESULT = {
    "basket_read": "A two-person household running on quick breakfasts and daily chai.",
    "product": "Epigamia Greek Yogurt, Blueberry, 90 g (pack of 2)",
    "category": "Fresh Dairy Snacking",
    "reason": "You already stock milk and bananas every week, so a protein snack slots straight into your breakfast routine. It keeps for days and needs zero prep on rushed mornings.",
    "social_proof": "31% of shoppers in your city who buy bananas weekly also ordered Greek yogurt this month",
    "price_inr": 130,
}


def get_suggestion(basket_text: str) -> dict:
    """Call Claude for a basket-aware nudge. Fall back to demo data on any failure."""
    try:
        import anthropic

        client = anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])
        msg = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=600,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": f"My typical Blinkit basket: {basket_text}"}],
        )
        raw = msg.content[0].text.strip()
        raw = re.sub(r"^```(json)?|```$", "", raw, flags=re.MULTILINE).strip()
        data = json.loads(raw)
        for key in ("basket_read", "product", "category", "reason", "social_proof", "price_inr"):
            if key not in data:
                raise ValueError(f"missing key {key}")
        return data
    except Exception:
        return DEMO_RESULT


# ---------------------------------------------------------------- UI

st.markdown(
    """
    <div class="brand-header">
        <span class="brand-logo">blinkit</span>
        <div class="brand-tagline">Smart Basket &middot; AI-native discovery nudge &middot; NextLeap graduation MVP</div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="iphone-frame"><div class="iphone-screen">
        <div class="dynamic-island"></div>
        <div class="status-bar"><span>9:41</span><span>&#9679;&#9679;&#9679;&#9679; &#128267;</span></div>
        <div class="app-body">
            <div class="app-topbar">
                <div class="t1">DELIVERY IN 8 MINUTES</div>
                <div class="t2">Smart Basket</div>
                <div class="t3">One new find, matched to how you already shop</div>
            </div>
            <div class="section-label">Your usual basket</div>
        </div>
    </div></div>
    """,
    unsafe_allow_html=True,
)

basket = st.text_area(
    "basket",
    placeholder="e.g. Amul milk 1L, brown bread, bananas, Maggi, Tata Salt, curd 400g",
    height=90,
    label_visibility="collapsed",
)

go = st.button("Analyze my basket \u2192")

if go:
    items = [i.strip() for i in re.split(r"[,\n]", basket) if i.strip()]
    if not items:
        st.markdown(
            "<div class='footer-note'>Add a few items first, like milk, bread, bananas.</div>",
            unsafe_allow_html=True,
        )
    else:
        with st.spinner("Reading your basket..."):
            result = get_suggestion(basket)

        chips = "".join(f"<span class='chip'>{i}</span>" for i in items[:10])
        st.markdown(f"<div class='chip-row'>{chips}</div>", unsafe_allow_html=True)

        st.markdown(
            f"""
            <div class="nudge-card">
                <span class="nudge-eyebrow">Picked for your basket</span>
                <div class="nudge-product">{result["product"]}</div>
                <div class="nudge-cat">New for you &middot; {result["category"]}</div>
                <div class="nudge-reason"><b>{result["basket_read"]}</b><br>{result["reason"]}</div>
                <div class="social-proof">&#11088; {result["social_proof"]}</div>
                <div class="price-line">
                    <span class="price-tag">&#8377;{result["price_inr"]}</span>
                    <span class="add-btn">ADD</span>
                </div>
                <div class="method-note">
                    Why this exists: analysis of 1,718 real user posts showed only 2.3% mention
                    discovery at all. Users never attempt it, so the nudge meets them at checkout,
                    the highest-intent moment, with social proof and a reason grounded in their
                    own basket.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.markdown(
    "<div class='footer-note'>Built for the NextLeap PM Fellowship &middot; D3 MVP &middot; Powered by Claude</div>",
    unsafe_allow_html=True,
)
