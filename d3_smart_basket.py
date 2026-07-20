import streamlit as st
import anthropic
import json
import random

st.set_page_config(page_title="Blinkit Smart Basket", page_icon="🛒", layout="centered")

# ── Basket data ────────────────────────────────────────────────────────────────
BASKETS = [
    {
        "delivery": "Delivery in 8 minutes",
        "items": [
            {"emoji": "🥛", "name": "Amul Taaza Toned Milk", "weight": "1 L", "price": 28, "qty": 2},
            {"emoji": "🍞", "name": "Britannia Whole Wheat Bread", "weight": "400 g", "price": 40, "qty": 1},
            {"emoji": "🥚", "name": "Farm Fresh White Eggs", "weight": "6 pcs", "price": 54, "qty": 1},
            {"emoji": "☕", "name": "Nescafe Classic Instant Coffee", "weight": "50 g", "price": 120, "qty": 1},
        ]
    },
    {
        "delivery": "Delivery in 9 minutes",
        "items": [
            {"emoji": "🌽", "name": "Lay's India's Magic Masala Chips", "weight": "48 g", "price": 20, "qty": 2},
            {"emoji": "🍘", "name": "Kurkure Masala Munch Crisps", "weight": "75 g", "price": 20, "qty": 2},
            {"emoji": "🍫", "name": "Hide & Seek Choco Chip Cookies", "weight": "100 g", "price": 30, "qty": 1},
            {"emoji": "🥤", "name": "Thums Up Soft Drink", "weight": "750 ml", "price": 40, "qty": 1},
        ]
    },
    {
        "delivery": "Delivery in 10 minutes",
        "items": [
            {"emoji": "🧈", "name": "Amul Butter Salted", "weight": "100 g", "price": 55, "qty": 1},
            {"emoji": "🍓", "name": "Kissan Mixed Fruit Jam", "weight": "200 g", "price": 70, "qty": 1},
            {"emoji": "🧃", "name": "Real Activ Orange Juice", "weight": "1 L", "price": 110, "qty": 1},
            {"emoji": "🥣", "name": "MTR Upma Breakfast Mix", "weight": "200 g", "price": 65, "qty": 2},
        ]
    },
    {
        "delivery": "Delivery in 8 minutes",
        "items": [
            {"emoji": "🍼", "name": "Nestlé NAN Pro 1 Baby Formula", "weight": "400 g", "price": 650, "qty": 1},
            {"emoji": "🧻", "name": "Pampers Baby Wipes Gentle", "weight": "72 pcs", "price": 199, "qty": 2},
            {"emoji": "👶", "name": "Pampers Newborn Diapers", "weight": "20 pcs", "price": 360, "qty": 1},
            {"emoji": "🛁", "name": "Johnson's Baby Soap Mild", "weight": "75 g", "price": 35, "qty": 2},
        ]
    },
    {
        "delivery": "Delivery in 12 minutes",
        "items": [
            {"emoji": "🧴", "name": "Vim Dishwash Liquid Lemon", "weight": "500 ml", "price": 89, "qty": 1},
            {"emoji": "🪣", "name": "Harpic Power Plus Toilet Cleaner", "weight": "500 ml", "price": 75, "qty": 1},
            {"emoji": "💧", "name": "Colin Glass and Surface Cleaner", "weight": "500 ml", "price": 95, "qty": 1},
            {"emoji": "🧽", "name": "Scotch-Brite Scrub Pad", "weight": "3 pcs", "price": 45, "qty": 2},
        ]
    },
]

DEFAULT_RECS = [
    {"emoji": "🌶️", "name": "Everest Tikhalal Chilli Powder", "weight": "100 g", "category": "Spices", "rating": 4.4, "reviews": "32,104", "price": 62},
    {"emoji": "🫙", "name": "Saffola Active Blended Edible Oil", "weight": "1 L", "category": "Edible Oils", "rating": 4.5, "reviews": "18,239", "price": 145},
    {"emoji": "🧹", "name": "Lizol Disinfectant Surface Cleaner", "weight": "500 ml", "category": "Cleaners", "rating": 4.6, "reviews": "41,882", "price": 119},
]

# ── Claude call ────────────────────────────────────────────────────────────────
def get_ai_recommendations(basket_items):
    client = anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])
    basket_str = ", ".join([f"{i['name']} ({i['weight']})" for i in basket_items])
    existing_categories = ", ".join(set([
        "dairy" if any(k in i["name"].lower() for k in ["milk","butter","cheese","curd","paneer"]) else
        "snacks" if any(k in i["name"].lower() for k in ["chips","kurkure","bingo","lay","cookie","biscuit"]) else
        "beverage" if any(k in i["name"].lower() for k in ["drink","juice","water","tea","coffee","thums","pepsi","cola"]) else
        "baby" if any(k in i["name"].lower() for k in ["pamper","baby","nestl","johnson"]) else
        "cleaning" if any(k in i["name"].lower() for k in ["vim","harpic","colin","lizol","scotch"]) else
        "staples"
        for i in basket_items
    ]))

    system = """You are the Blinkit Smart Basket AI. Analyze the user's grocery basket and suggest exactly 3 products from NEW categories not already in their basket.

Rules:
- Each product must be from a genuinely different category than what's already in the basket
- Products must be real, commonly available Indian grocery/FMCG items sold on quick commerce
- Each suggestion must feel like a natural, useful complement to this specific basket
- Social proof must use realistic numbers (percentages, user counts)
- Price anchor must compare to something already in the basket

Respond ONLY with a valid JSON array, no markdown, no extra text:
[
  {
    "emoji": "🌶️",
    "name": "Full product name with variant (e.g. Everest Kitchen King Masala)",
    "weight": "100 g",
    "category": "Spices",
    "rating": 4.4,
    "reviews": "32,104",
    "price": 62,
    "social_proof": "Added by 71% of users who buy bread and eggs together.",
    "reason": "Completes a breakfast setup — goes naturally with what you already have."
  }
]"""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=800,
        system=system,
        messages=[{
            "role": "user",
            "content": f"My basket contains: {basket_str}. Existing categories covered: {existing_categories}. Suggest 3 products from completely different categories."
        }]
    )

    raw = message.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())

# ── Session state ──────────────────────────────────────────────────────────────
if "basket" not in st.session_state:
    st.session_state.basket = random.choice(BASKETS)

if "qtys" not in st.session_state:
    st.session_state.qtys = {i["name"]: i["qty"] for i in st.session_state.basket["items"]}

if "analyzed" not in st.session_state:
    st.session_state.analyzed = False

if "ai_recs" not in st.session_state:
    st.session_state.ai_recs = None

if "tip" not in st.session_state:
    st.session_state.tip = 0

if "added_recs" not in st.session_state:
    st.session_state.added_recs = set()

basket = st.session_state.basket
qtys = st.session_state.qtys

# ── Build the full HTML page ───────────────────────────────────────────────────
items_json = json.dumps(basket["items"])
qtys_json = json.dumps(qtys)
delivery_text = basket["delivery"]

if st.session_state.analyzed and st.session_state.ai_recs:
    recs_json = json.dumps(st.session_state.ai_recs)
    recs_title = "✦ Smart Basket Picks"
    ai_badge_visible = "visible"
    btn_class = "done"
    btn_content = "✓ &nbsp;Basket Analyzed"
    btn_disabled = "disabled"
else:
    recs_json = json.dumps(DEFAULT_RECS)
    recs_title = "You might also like"
    ai_badge_visible = ""
    btn_class = ""
    btn_content = "✦ Analyze My Basket"
    btn_disabled = ""

HTML = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Blinkit Smart Basket</title>
<style>
* {{ margin:0; padding:0; box-sizing:border-box; -webkit-tap-highlight-color:transparent; }}
body {{
  background:#F0F0F0;
  display:flex;
  justify-content:center;
  align-items:flex-start;
  min-height:100vh;
  padding:32px 16px 48px;
  font-family:-apple-system,BlinkMacSystemFont,"SF Pro Text","Segoe UI",sans-serif;
}}
.phone {{
  width:390px;
  background:#1C1C1E;
  border-radius:55px;
  border:2px solid #3A3A3C;
  position:relative;
  box-shadow:0 0 0 1px #555,0 40px 90px rgba(0,0,0,0.55),0 8px 24px rgba(0,0,0,0.3);
  overflow:hidden;
}}
.phone::before {{
  content:'';position:absolute;left:-5px;top:108px;
  width:4px;height:32px;background:#3A3A3C;border-radius:3px 0 0 3px;
  box-shadow:0 50px 0 #3A3A3C,0 94px 0 #3A3A3C;z-index:20;
}}
.phone::after {{
  content:'';position:absolute;right:-5px;top:162px;
  width:4px;height:74px;background:#3A3A3C;border-radius:0 3px 3px 0;z-index:20;
}}
.screen {{
  background:#fff;border-radius:53px;overflow:hidden;
  display:flex;flex-direction:column;height:844px;
}}
.status-bar {{
  background:#fff;height:56px;display:flex;align-items:flex-end;
  justify-content:space-between;padding:0 28px 10px;position:relative;flex-shrink:0;
}}
.status-time {{ font-size:15px;font-weight:700;color:#1A1A1A;letter-spacing:-0.3px; }}
.dynamic-island {{
  position:absolute;top:12px;left:50%;transform:translateX(-50%);
  width:120px;height:36px;background:#1C1C1E;border-radius:20px;
  display:flex;align-items:center;justify-content:center;gap:10px;
}}
.di-cam {{ width:10px;height:10px;background:#2C2C2E;border-radius:50%;border:1.5px solid #444; }}
.di-sensor {{ width:22px;height:10px;background:#2C2C2E;border-radius:7px;border:1.5px solid #444; }}
.status-icons {{ display:flex;align-items:center;gap:6px; }}
.signal-bars {{ display:flex;align-items:flex-end;gap:2px;height:12px; }}
.bar {{ width:3px;background:#1A1A1A;border-radius:1px; }}
.battery-wrap {{ display:flex;align-items:center;gap:1px; }}
.battery-body {{ width:24px;height:12px;border:1.5px solid #1A1A1A;border-radius:3px;padding:1.5px; }}
.battery-fill {{ width:100%;height:100%;background:#1A1A1A;border-radius:1.5px; }}
.battery-tip {{ width:2px;height:5px;background:#1A1A1A;border-radius:0 1.5px 1.5px 0; }}
.nav-bar {{
  background:#fff;height:50px;display:flex;align-items:center;
  padding:0 16px;border-bottom:1px solid #EFEFEF;flex-shrink:0;
}}
.nav-back {{ font-size:26px;color:#1A1A1A;background:none;border:none;cursor:pointer;line-height:1;padding:4px 12px 4px 0; }}
.nav-title {{ flex:1;text-align:center;font-size:17px;font-weight:600;color:#1A1A1A;letter-spacing:-0.2px; }}
.nav-share {{ display:flex;align-items:center;gap:4px;color:#0C831F;font-size:13.5px;font-weight:600;background:none;border:none;cursor:pointer; }}
.scroll-area {{
  flex:1;overflow-y:auto;background:#F2F3F7;
  -webkit-overflow-scrolling:touch;scrollbar-width:none;
}}
.scroll-area::-webkit-scrollbar {{ display:none; }}
.card {{ background:#fff;margin:8px 10px;border-radius:16px;border:1px solid #EBEBEB;overflow:hidden; }}
.delivery-banner {{ display:flex;align-items:center;gap:10px;padding:12px 14px;border-bottom:1px solid #F2F2F2; }}
.delivery-icon {{
  width:34px;height:34px;background:#EAF7EE;border-radius:50%;
  display:flex;align-items:center;justify-content:center;font-size:16px;flex-shrink:0;
}}
.delivery-time {{ font-size:14.5px;font-weight:700;color:#1A1A1A; }}
.delivery-sub {{ font-size:12px;color:#999;margin-top:1px; }}
.cart-item {{ display:flex;align-items:center;gap:12px;padding:12px 14px;border-bottom:1px solid #F7F7F7; }}
.cart-item:last-child {{ border-bottom:none; }}
.item-img {{
  width:66px;height:66px;background:#F5F5F5;border-radius:10px;
  display:flex;align-items:center;justify-content:center;font-size:34px;flex-shrink:0;
}}
.item-info {{ flex:1;min-width:0; }}
.item-name {{ font-size:13px;font-weight:600;color:#1A1A1A;line-height:1.35;margin-bottom:2px; }}
.item-weight {{ font-size:11.5px;color:#999;margin-bottom:5px; }}
.item-wishlist {{
  font-size:11.5px;color:#AAAAAA;text-decoration:underline;
  text-decoration-style:dashed;background:none;border:none;cursor:pointer;padding:0;
}}
.item-right {{ display:flex;flex-direction:column;align-items:flex-end;gap:6px;flex-shrink:0; }}
.item-price {{ font-size:13px;font-weight:600;color:#1A1A1A; }}
.qty-stepper {{
  display:flex;align-items:center;background:#0C831F;
  border-radius:7px;overflow:hidden;height:30px;width:84px;
}}
.qty-btn {{
  width:28px;height:30px;background:transparent;border:none;color:#fff;
  font-size:18px;font-weight:700;cursor:pointer;display:flex;align-items:center;justify-content:center;line-height:1;
}}
.qty-num {{ color:#fff;font-size:13.5px;font-weight:700;flex:1;text-align:center; }}
.smart-basket-card {{ background:#fff;margin:0 10px 8px;border-radius:16px;border:1px solid #EBEBEB;padding:16px 14px; }}
.sb-header {{ display:flex;align-items:center;gap:8px;margin-bottom:6px; }}
.sb-icon {{ width:30px;height:30px;background:#FFF3E0;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:15px; }}
.sb-title {{ font-size:15.5px;font-weight:700;color:#1A1A1A; }}
.sb-badge {{ font-size:9px;font-weight:700;background:#E8F5E9;color:#0C831F;padding:2px 8px;border-radius:20px;letter-spacing:0.3px; }}
.sb-sub {{ font-size:12.5px;color:#777;line-height:1.55;margin-bottom:14px;padding-left:38px; }}
.analyze-btn {{
  width:100%;background:#0C831F;border:none;border-radius:11px;color:#fff;
  font-size:15px;font-weight:700;padding:13px 0;cursor:pointer;
  display:flex;align-items:center;justify-content:center;gap:7px;
}}
.analyze-btn.done {{ background:transparent;border:1.5px solid #0C831F;color:#0C831F; }}
.analyze-btn:disabled {{ cursor:default; }}
.recs-card {{ background:#fff;margin:0 10px 8px;border-radius:16px;border:1px solid #EBEBEB;padding:14px 0; }}
.recs-header {{ display:flex;align-items:center;justify-content:space-between;padding:0 14px 12px; }}
.recs-title {{ font-size:15.5px;font-weight:700;color:#1A1A1A; }}
.recs-ai-badge {{ font-size:9px;font-weight:700;background:#E8F5E9;color:#0C831F;padding:2px 8px;border-radius:20px;display:none; }}
.recs-ai-badge.visible {{ display:block; }}
.recs-scroll {{ display:flex;gap:10px;overflow-x:auto;padding:0 14px 4px;scrollbar-width:none; }}
.recs-scroll::-webkit-scrollbar {{ display:none; }}
.rec-card {{ background:#fff;border:1px solid #E4E4E4;border-radius:12px;width:148px;flex-shrink:0;overflow:hidden; }}
.rec-img {{ background:#F7F7F7;height:126px;display:flex;align-items:center;justify-content:center;position:relative;font-size:52px; }}
.rec-heart {{ position:absolute;top:6px;right:8px;font-size:16px;color:#CCC;cursor:pointer; }}
.rec-add-btn {{
  position:absolute;bottom:8px;left:50%;transform:translateX(-50%);
  background:#fff;border:1.5px solid #0C831F;border-radius:7px;color:#0C831F;
  font-size:13px;font-weight:700;padding:4px 0;width:106px;cursor:pointer;white-space:nowrap;
}}
.rec-add-btn.added {{ background:#0C831F;color:#fff; }}
.rec-body {{ padding:8px 9px 10px; }}
.rec-meta {{ font-size:9px;color:#0C831F;font-weight:600;margin-bottom:2px; }}
.rec-meta span {{ color:#999;font-weight:400; }}
.rec-name {{ font-size:12px;font-weight:600;color:#1A1A1A;line-height:1.35;margin-bottom:5px;min-height:30px; }}
.rec-stars {{ color:#FFB800;font-size:10.5px; }}
.rec-reviews {{ font-size:9.5px;color:#AAA; }}
.rec-price {{ font-size:14.5px;font-weight:700;color:#1A1A1A;margin:4px 0 8px; }}
.rec-see-more {{ width:100%;background:transparent;border:1px solid #D0EDD6;border-radius:6px;color:#0C831F;font-size:10px;font-weight:600;padding:5px 0;cursor:pointer; }}
.see-all-card {{
  background:#fff;margin:0 10px 8px;border-radius:12px;border:1px solid #EBEBEB;
  padding:13px 16px;display:flex;align-items:center;justify-content:center;gap:8px;cursor:pointer;
}}
.see-all-text {{ font-size:13.5px;font-weight:600;color:#0C831F; }}
.bill-card {{ background:#fff;margin:0 10px 8px;border-radius:16px;border:1px solid #EBEBEB;padding:14px 14px 12px; }}
.bill-title {{ font-size:16px;font-weight:700;color:#1A1A1A;margin-bottom:10px; }}
.bill-row {{ display:flex;justify-content:space-between;align-items:center;padding:8px 0;border-bottom:1px solid #F9F9F9; }}
.bill-label {{ display:flex;align-items:center;gap:7px;font-size:13.5px;color:#333; }}
.bill-label-icon {{ font-size:14px; }}
.bill-amount {{ font-size:13.5px;color:#333; }}
.bill-sub {{ font-size:11.5px;color:#E87722;margin:2px 0 6px 22px;line-height:1.4; }}
.bill-total {{ display:flex;justify-content:space-between;padding-top:12px;margin-top:2px;border-top:1px solid #EFEFEF; }}
.bill-total-label {{ font-size:15px;font-weight:700;color:#1A1A1A; }}
.bill-total-amount {{ font-size:15px;font-weight:700;color:#1A1A1A; }}
.gstin-card {{
  background:#fff;margin:0 10px 8px;border-radius:12px;border:1px solid #EBEBEB;
  padding:14px;display:flex;align-items:center;gap:12px;cursor:pointer;
}}
.gstin-icon {{ width:38px;height:38px;background:#EEF2FF;border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:18px;flex-shrink:0; }}
.gstin-title {{ font-size:14px;font-weight:700;color:#1A1A1A; }}
.gstin-sub {{ font-size:12px;color:#999;margin-top:1px; }}
.gstin-arrow {{ font-size:20px;color:#CCC;margin-left:auto; }}
.tip-card {{ background:#fff;margin:0 10px 8px;border-radius:16px;border:1px solid #EBEBEB;padding:16px 14px 14px; }}
.tip-header {{ display:flex;gap:10px;margin-bottom:12px; }}
.tip-text {{ flex:1; }}
.tip-heading {{ font-size:16px;font-weight:700;color:#1A1A1A;margin-bottom:5px; }}
.tip-sub {{ font-size:12px;color:#666;line-height:1.55; }}
.tip-emoji {{ font-size:42px;flex-shrink:0;align-self:flex-start; }}
.tip-options {{ display:flex;gap:8px; }}
.tip-btn {{ flex:1;border:1.5px solid #DEDEDE;border-radius:10px;padding:9px 4px;background:#fff;cursor:pointer;font-size:12px;color:#1A1A1A;text-align:center;line-height:1.4; }}
.tip-btn.selected {{ border-color:#0C831F;background:#E8F5E9;font-weight:700; }}
.gift-card {{ background:#fff;margin:0 10px 8px;border-radius:12px;border:1px solid #EBEBEB;padding:14px;display:flex;align-items:center;gap:12px; }}
.gift-icon {{ font-size:34px;flex-shrink:0; }}
.gift-title {{ font-size:14px;font-weight:700;color:#1A1A1A; }}
.gift-sub {{ font-size:12px;color:#999;margin-top:2px; }}
.gift-select {{ margin-left:auto;flex-shrink:0;border:1.5px solid #0C831F;border-radius:8px;background:#fff;color:#0C831F;font-size:13.5px;font-weight:700;padding:8px 16px;cursor:pointer; }}
.cancel-card {{ background:#fff;margin:0 10px 8px;border-radius:12px;border:1px solid #EBEBEB;padding:14px; }}
.cancel-title {{ font-size:14px;font-weight:700;color:#1A1A1A;margin-bottom:6px; }}
.cancel-text {{ font-size:12.5px;color:#777;line-height:1.65; }}
.cta-area {{ background:#fff;border-top:1px solid #F0F0F0;padding:11px 14px 0;flex-shrink:0; }}
.cta-btn {{ width:100%;background:#0C831F;border:none;border-radius:14px;color:#fff;font-size:15.5px;font-weight:700;padding:15px 0;cursor:pointer;letter-spacing:0.1px; }}
.home-indicator {{ background:#fff;display:flex;justify-content:center;align-items:center;padding:10px 0 16px;flex-shrink:0; }}
.home-bar {{ width:134px;height:5px;background:#1A1A1A;border-radius:3px; }}
.dots {{ display:flex;gap:4px;align-items:center; }}
.dot {{ width:7px;height:7px;background:#0C831F;border-radius:50%;animation:bounce 1.1s infinite ease-in-out; }}
.dot:nth-child(2) {{ animation-delay:0.18s; }}
.dot:nth-child(3) {{ animation-delay:0.36s; }}
@keyframes bounce {{ 0%,80%,100% {{ transform:translateY(0); }} 40% {{ transform:translateY(-5px); }} }}
.rec-card {{ opacity:1;transform:translateY(0);transition:opacity 0.35s ease,transform 0.35s ease; }}
.rec-card.entering {{ opacity:0;transform:translateY(16px); }}
.social-proof-tag {{ font-size:10px;color:#0C831F;background:#E8F5E9;border-radius:6px;padding:4px 8px;margin-top:4px;margin-bottom:6px;line-height:1.4; }}
.reason-tag {{ font-size:10px;color:#555;font-style:italic;margin-bottom:6px;line-height:1.4; }}
</style>
</head>
<body>
<div class="phone">
  <div class="screen">
    <div class="status-bar">
      <span class="status-time">9:41</span>
      <div class="dynamic-island">
        <div class="di-sensor"></div>
        <div class="di-cam"></div>
      </div>
      <div class="status-icons">
        <div class="signal-bars">
          <div class="bar" style="height:4px"></div>
          <div class="bar" style="height:6px"></div>
          <div class="bar" style="height:9px"></div>
          <div class="bar" style="height:12px"></div>
        </div>
        <svg width="16" height="12" viewBox="0 0 16 12" fill="none">
          <circle cx="8" cy="10.5" r="1.4" fill="#1A1A1A"/>
          <path d="M4.8 7.5a4.5 4.5 0 016.4 0" stroke="#1A1A1A" stroke-width="1.5" stroke-linecap="round"/>
          <path d="M2 4.8a8.5 8.5 0 0112 0" stroke="#1A1A1A" stroke-width="1.5" stroke-linecap="round"/>
        </svg>
        <div class="battery-wrap">
          <div class="battery-body"><div class="battery-fill"></div></div>
          <div class="battery-tip"></div>
        </div>
      </div>
    </div>
    <div class="nav-bar">
      <button class="nav-back">‹</button>
      <span class="nav-title">Checkout</span>
      <button class="nav-share">🛒 Share</button>
    </div>
    <div class="scroll-area">
      <div class="card">
        <div class="delivery-banner">
          <div class="delivery-icon">⏱</div>
          <div>
            <div class="delivery-time">{delivery_text}</div>
            <div class="delivery-sub" id="itemCount">Loading...</div>
          </div>
        </div>
        <div id="cartItems"></div>
      </div>
      <div class="smart-basket-card">
        <div class="sb-header">
          <div class="sb-icon">✦</div>
          <span class="sb-title">Smart Basket</span>
          <span class="sb-badge">AI</span>
        </div>
        <div class="sb-sub">Discover one new product that matches how you already shop.</div>
        <button class="analyze-btn {btn_class}" id="analyzeBtn" {btn_disabled} onclick="handleAnalyze()">
          {btn_content}
        </button>
      </div>
      <div class="recs-card">
        <div class="recs-header">
          <span class="recs-title">{recs_title}</span>
          <span class="recs-ai-badge {ai_badge_visible}">AI Powered</span>
        </div>
        <div class="recs-scroll" id="recsScroll"></div>
      </div>
      <div class="see-all-card">
        <span style="font-size:20px">🛍</span>
        <span class="see-all-text">See all products ▶</span>
      </div>
      <div class="bill-card">
        <div class="bill-title">Bill details</div>
        <div class="bill-row">
          <div class="bill-label"><span class="bill-label-icon">📋</span> Items total</div>
          <div class="bill-amount" id="billItems">₹0</div>
        </div>
        <div class="bill-row">
          <div class="bill-label"><span class="bill-label-icon">🛍</span> <span style="text-decoration:underline;text-decoration-style:dashed;text-underline-offset:3px">Handling charge</span></div>
          <div class="bill-amount">₹2</div>
        </div>
        <div class="bill-row">
          <div class="bill-label"><span class="bill-label-icon">🛵</span> <span style="text-decoration:underline;text-decoration-style:dashed;text-underline-offset:3px">Delivery charge</span></div>
          <div class="bill-amount" id="billDelivery">₹30</div>
        </div>
        <div class="bill-sub" id="deliveryNote">Pay only ₹16 as delivery fee by shopping above ₹199</div>
        <div id="tipRow" style="display:none" class="bill-row">
          <div class="bill-label"><span class="bill-label-icon">💛</span> Tip</div>
          <div class="bill-amount" id="billTip">₹0</div>
        </div>
        <div class="bill-total">
          <span class="bill-total-label">Grand total</span>
          <span class="bill-total-amount" id="grandTotal">₹0</span>
        </div>
      </div>
      <div class="gstin-card">
        <div class="gstin-icon">🏷</div>
        <div>
          <div class="gstin-title">Add GSTIN</div>
          <div class="gstin-sub">Claim GST input credit up to 28% on your order</div>
        </div>
        <span class="gstin-arrow">›</span>
      </div>
      <div class="tip-card">
        <div class="tip-header">
          <div class="tip-text">
            <div class="tip-heading">Tip your delivery partner</div>
            <div class="tip-sub">Your kindness means a lot! 100% of your tip will go directly to your delivery partner.</div>
          </div>
          <div class="tip-emoji">🛵</div>
        </div>
        <div class="tip-options">
          <button class="tip-btn" onclick="selectTip(this,20)">😆<br>₹20</button>
          <button class="tip-btn" onclick="selectTip(this,30)">🤩<br>₹30</button>
          <button class="tip-btn" onclick="selectTip(this,50)">😍<br>₹50</button>
          <button class="tip-btn" onclick="selectTip(this,0)">🤝<br>Custom</button>
        </div>
      </div>
      <div class="gift-card">
        <span class="gift-icon">🎁</span>
        <div>
          <div class="gift-title">Gift Packaging</div>
          <div class="gift-sub">Get your items in a special gift bag for just ₹30</div>
        </div>
        <button class="gift-select">Select</button>
      </div>
      <div class="cancel-card">
        <div class="cancel-title">Cancellation Policy</div>
        <div class="cancel-text">Orders cannot be cancelled once packed for delivery. In case of unexpected delays, a refund will be provided, if applicable.</div>
      </div>
      <div style="height:10px"></div>
    </div>
    <div class="cta-area">
      <button class="cta-btn">Select address at next step ▶</button>
    </div>
    <div class="home-indicator">
      <div class="home-bar"></div>
    </div>
  </div>
</div>
<script>
const ITEMS = {items_json};
const QTYS = {qtys_json};
const RECS = {recs_json};
let tipAmount = 0;
let addedRecs = {{}};

function stars(r) {{
  const f = Math.floor(r);
  const h = r-f >= 0.3 ? '½' : '';
  const e = 5-f-(h?1:0);
  return '★'.repeat(f)+h+'☆'.repeat(e);
}}

function renderCart() {{
  const visible = ITEMS.filter(i => (QTYS[i.name]||0) > 0);
  document.getElementById('itemCount').textContent = `Shipment of ${{visible.length}} item${{visible.length!==1?'s':''}}`;
  document.getElementById('cartItems').innerHTML = visible.map(item => `
    <div class="cart-item">
      <div class="item-img">${{item.emoji}}</div>
      <div class="item-info">
        <div class="item-name">${{item.name}}</div>
        <div class="item-weight">${{item.weight}}</div>
        <button class="item-wishlist">Move to wishlist</button>
      </div>
      <div class="item-right">
        <div class="qty-stepper">
          <button class="qty-btn" onclick="changeQty('${{item.name}}',-1)">−</button>
          <span class="qty-num">${{QTYS[item.name]}}</span>
          <button class="qty-btn" onclick="changeQty('${{item.name}}',1)">+</button>
        </div>
        <div class="item-price">₹${{item.price * QTYS[item.name]}}</div>
      </div>
    </div>
  `).join('');
  updateBill();
}}

function changeQty(name, d) {{
  QTYS[name] = Math.max(0,(QTYS[name]||0)+d);
  renderCart();
}}

function updateBill() {{
  const total = ITEMS.reduce((s,i)=>s+(i.price*(QTYS[i.name]||0)),0);
  const delivery = total>=199?16:30;
  document.getElementById('billItems').textContent = `₹${{total}}`;
  document.getElementById('billDelivery').textContent = `₹${{delivery}}`;
  document.getElementById('grandTotal').textContent = `₹${{total+2+delivery+tipAmount}}`;
  document.getElementById('deliveryNote').style.display = total>=199?'none':'block';
  if(tipAmount>0){{document.getElementById('tipRow').style.display='flex';document.getElementById('billTip').textContent=`₹${{tipAmount}}`;}}
  else{{document.getElementById('tipRow').style.display='none';}}
}}

function selectTip(btn,amt) {{
  document.querySelectorAll('.tip-btn').forEach(b=>b.classList.remove('selected'));
  btn.classList.add('selected');
  tipAmount=amt;
  updateBill();
}}

function renderRecs(recs, animate) {{
  document.getElementById('recsScroll').innerHTML = recs.map(p => `
    <div class="rec-card ${{animate?'entering':''}}" id="rec-${{p.price}}">
      <div class="rec-img">
        ${{p.emoji}}
        <span class="rec-heart">♡</span>
        <button class="rec-add-btn ${{addedRecs[p.price]?'added':''}}" onclick="addRec(this,${{p.price}})">
          ${{addedRecs[p.price]?'ADDED ✓':'ADD'}}
        </button>
      </div>
      <div class="rec-body">
        <div class="rec-meta">${{p.weight}} · <span>${{p.category}}</span></div>
        <div class="rec-name">${{p.name}}</div>
        ${{p.social_proof ? `<div class="social-proof-tag">👥 ${{p.social_proof}}</div>` : ''}}
        ${{p.reason ? `<div class="reason-tag">${{p.reason}}</div>` : ''}}
        <div><span class="rec-stars">${{stars(p.rating)}}</span> <span class="rec-reviews">(${{p.reviews}})</span></div>
        <div class="rec-price">₹${{p.price}}</div>
        <button class="rec-see-more">See more like this ▶</button>
      </div>
    </div>
  `).join('');
  if(animate) {{
    requestAnimationFrame(()=>{{
      document.querySelectorAll('.rec-card.entering').forEach((c,i)=>{{
        setTimeout(()=>{{ c.style.transition='opacity 0.4s ease,transform 0.4s ease'; c.classList.remove('entering'); }},i*90);
      }});
    }});
  }}
}}

function addRec(btn,price) {{
  addedRecs[price]=true;
  btn.textContent='ADDED ✓';
  btn.classList.add('added');
}}

function handleAnalyze() {{
  const btn = document.getElementById('analyzeBtn');
  btn.className='analyze-btn loading';
  btn.innerHTML='<div class="dots"><div class="dot"></div><div class="dot"></div><div class="dot"></div></div><span>Analyzing your basket…</span>';
  btn.disabled=true;
  window.parent.postMessage({{type:'streamlit:setComponentValue', value:'analyze'}}, '*');
}}

renderCart();
renderRecs(RECS, false);
</script>
</body>
</html>"""

# ── Render ─────────────────────────────────────────────────────────────────────
st.components.v1.html(HTML, height=920, scrolling=False)

# ── Handle analyze trigger via query param ─────────────────────────────────────
analyze_trigger = st.query_params.get("analyze", None)

if not st.session_state.analyzed:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔍 Analyze My Basket", key="py_analyze", use_container_width=True, type="primary"):
            with st.spinner("Claude is analyzing your basket..."):
                try:
                    visible_items = [
                        i for i in basket["items"]
                        if st.session_state.qtys.get(i["name"], 0) > 0
                    ]
                    recs = get_ai_recommendations(visible_items)
                    st.session_state.ai_recs = recs
                    st.session_state.analyzed = True
                    st.rerun()
                except Exception as e:
                    st.error(f"Analysis failed: {e}")
