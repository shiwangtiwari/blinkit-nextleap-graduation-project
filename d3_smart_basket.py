import streamlit as st
import anthropic
import json
import random

st.set_page_config(
    page_title="Blinkit Smart Basket",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
html,body{background:#E8E8E8!important;margin:0!important;padding:0!important;}
.stApp{background:#E8E8E8!important;}
.stApp>div>div{background:transparent!important;}
section[data-testid="stSidebar"]{display:none!important;}
header[data-testid="stHeader"]{display:none!important;}
[data-testid="stToolbar"]{display:none!important;}
[data-testid="stDecoration"]{display:none!important;}
[data-testid="stStatusWidget"]{display:none!important;}
[data-testid="stMainBlockContainer"]{padding:0!important;max-width:100%!important;background:transparent!important;}
.block-container{padding:0!important;max-width:100%!important;background:transparent!important;}
.element-container{background:transparent!important;}
footer{display:none!important;}
div[data-testid="stForm"]{display:none!important;position:absolute!important;}
</style>
""", unsafe_allow_html=True)

# ── Data ───────────────────────────────────────────────────────────────────────
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
    {"emoji": "🌶️", "name": "Everest Tikhalal Chilli Powder", "weight": "100 g", "category": "Spices", "rating": 4.4, "reviews": "32,104", "price": 62, "social_proof": "", "reason": ""},
    {"emoji": "🫙", "name": "Saffola Active Blended Edible Oil", "weight": "1 L", "category": "Edible Oils", "rating": 4.5, "reviews": "18,239", "price": 145, "social_proof": "", "reason": ""},
    {"emoji": "🧹", "name": "Lizol Disinfectant Surface Cleaner", "weight": "500 ml", "category": "Cleaners", "rating": 4.6, "reviews": "41,882", "price": 119, "social_proof": "", "reason": ""},
]

# ── Claude call ────────────────────────────────────────────────────────────────
def get_ai_recommendations(basket_items):
    client = anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])
    basket_str = ", ".join([f"{i['name']} ({i['weight']})" for i in basket_items])
    existing_cats = set()
    for i in basket_items:
        n = i["name"].lower()
        if any(k in n for k in ["milk","butter","cheese","curd","paneer"]): existing_cats.add("dairy")
        elif any(k in n for k in ["chips","kurkure","bingo","lay","cookie","biscuit"]): existing_cats.add("snacks")
        elif any(k in n for k in ["drink","juice","water","tea","coffee","thums","pepsi","cola"]): existing_cats.add("beverages")
        elif any(k in n for k in ["pamper","baby","nestl","johnson"]): existing_cats.add("baby")
        elif any(k in n for k in ["vim","harpic","colin","lizol","scotch"]): existing_cats.add("cleaning")
        else: existing_cats.add("staples")
    system = """You are the Blinkit Smart Basket AI. Suggest exactly 3 products from NEW categories not in the basket.
Rules: real Indian FMCG products, different categories, natural complements, realistic social proof numbers.
Respond ONLY with a valid JSON array, no markdown:
[{"emoji":"🌶️","name":"Product Name","weight":"100 g","category":"Spices","rating":4.4,"reviews":"32,104","price":62,"social_proof":"Added by 71% of users with similar baskets.","reason":"Natural complement to your breakfast setup."}]"""
    message = client.messages.create(
        model="claude-sonnet-4-6", max_tokens=800, system=system,
        messages=[{"role": "user", "content": f"Basket: {basket_str}. Existing categories: {', '.join(existing_cats)}. Suggest 3 from different categories."}]
    )
    raw = message.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"): raw = raw[4:]
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

basket = st.session_state.basket
qtys   = st.session_state.qtys

# ── Hidden form — clicked by JS inside the phone UI ───────────────────────────
with st.form(key="analyze_form"):
    submitted = st.form_submit_button("analyze")

if submitted and not st.session_state.analyzed:
    try:
        visible = [i for i in basket["items"] if qtys.get(i["name"], 0) > 0]
        recs = get_ai_recommendations(visible)
        st.session_state.ai_recs = recs
        st.session_state.analyzed = True
    except Exception as e:
        st.error(f"Analysis failed: {e}")
    st.rerun()

# ── Build data payload (injected as a separate script tag, no f-string needed) ─
items_json   = json.dumps(basket["items"])
qtys_json    = json.dumps(qtys)
delivery     = basket["delivery"]
analyzed     = st.session_state.analyzed and bool(st.session_state.ai_recs)
recs_json    = json.dumps(st.session_state.ai_recs) if analyzed else json.dumps(DEFAULT_RECS)
recs_title   = "✦ Smart Basket Picks" if analyzed else "You might also like"
ai_badge_cls = "visible" if analyzed else ""
btn_class    = "done" if analyzed else ""
btn_html     = "✓ &nbsp;Basket Analyzed" if analyzed else "✦ Analyze My Basket"
btn_disabled = "disabled" if analyzed else ""
btn_onclick  = "" if analyzed else 'onclick="bkAnalyze()"'
animate      = "true" if analyzed else "false"

# Inject data as a plain script — NO f-string, so JSON braces never escape
data_script = (
    "<script>"
    "var BK_ITEMS=" + items_json + ";"
    "var BK_QTYS=" + qtys_json + ";"
    "var BK_RECS=" + recs_json + ";"
    "var BK_ANIMATE=" + animate + ";"
    "</script>"
)
st.markdown(data_script, unsafe_allow_html=True)

# ── Render HTML (plain string, no f-string, no brace escaping issues) ─────────
# Python variables interpolated via .replace() — safe and explicit
HTML = """
<style>
*{margin:0;padding:0;box-sizing:border-box;-webkit-tap-highlight-color:transparent;}
.bk-wrap{display:flex;justify-content:center;align-items:flex-start;padding:32px 0 48px;font-family:-apple-system,BlinkMacSystemFont,'SF Pro Text','Segoe UI',sans-serif;background:#E8E8E8;min-height:100vh;}
.bk-phone{width:390px;background:#1C1C1E;border-radius:55px;border:2px solid #3A3A3C;position:relative;box-shadow:0 0 0 1px #555,0 40px 90px rgba(0,0,0,0.55),0 8px 24px rgba(0,0,0,0.3);overflow:hidden;}
.bk-phone::before{content:'';position:absolute;left:-5px;top:108px;width:4px;height:32px;background:#3A3A3C;border-radius:3px 0 0 3px;box-shadow:0 50px 0 #3A3A3C,0 94px 0 #3A3A3C;z-index:20;}
.bk-phone::after{content:'';position:absolute;right:-5px;top:162px;width:4px;height:74px;background:#3A3A3C;border-radius:0 3px 3px 0;z-index:20;}
.bk-screen{background:#fff;border-radius:53px;overflow:hidden;display:flex;flex-direction:column;height:844px;}
.bk-status{background:#fff;height:56px;display:flex;align-items:flex-end;justify-content:space-between;padding:0 28px 10px;position:relative;flex-shrink:0;}
.bk-time{font-size:15px;font-weight:700;color:#1A1A1A;letter-spacing:-0.3px;}
.bk-di{position:absolute;top:12px;left:50%;transform:translateX(-50%);width:120px;height:36px;background:#1C1C1E;border-radius:20px;display:flex;align-items:center;justify-content:center;gap:10px;}
.bk-di-s{width:22px;height:10px;background:#2C2C2E;border-radius:7px;border:1.5px solid #444;}
.bk-di-c{width:10px;height:10px;background:#2C2C2E;border-radius:50%;border:1.5px solid #444;}
.bk-icons{display:flex;align-items:center;gap:6px;}
.bk-bars{display:flex;align-items:flex-end;gap:2px;height:12px;}
.bk-bar{width:3px;background:#1A1A1A;border-radius:1px;}
.bk-bat-wrap{display:flex;align-items:center;gap:1px;}
.bk-bat{width:24px;height:12px;border:1.5px solid #1A1A1A;border-radius:3px;padding:1.5px;}
.bk-bat-fill{width:100%;height:100%;background:#1A1A1A;border-radius:1.5px;}
.bk-bat-tip{width:2px;height:5px;background:#1A1A1A;border-radius:0 1.5px 1.5px 0;}
.bk-nav{background:#fff;height:50px;display:flex;align-items:center;padding:0 16px;border-bottom:1px solid #EFEFEF;flex-shrink:0;}
.bk-back{font-size:26px;color:#1A1A1A;background:none;border:none;cursor:pointer;line-height:1;padding:4px 12px 4px 0;}
.bk-title{flex:1;text-align:center;font-size:17px;font-weight:600;color:#1A1A1A;letter-spacing:-0.2px;}
.bk-share{display:flex;align-items:center;gap:4px;color:#0C831F;font-size:13.5px;font-weight:600;background:none;border:none;cursor:pointer;}
.bk-scroll{flex:1;overflow-y:auto;background:#F2F3F7;-webkit-overflow-scrolling:touch;scrollbar-width:none;}
.bk-scroll::-webkit-scrollbar{display:none;}
.bk-card{background:#fff;margin:8px 10px;border-radius:16px;border:1px solid #EBEBEB;overflow:hidden;}
.bk-del-banner{display:flex;align-items:center;gap:10px;padding:12px 14px;border-bottom:1px solid #F2F2F2;}
.bk-del-icon{width:34px;height:34px;background:#EAF7EE;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:16px;flex-shrink:0;}
.bk-del-time{font-size:14.5px;font-weight:700;color:#1A1A1A;}
.bk-del-sub{font-size:12px;color:#999;margin-top:1px;}
.bk-ci{display:flex;align-items:center;gap:12px;padding:12px 14px;border-bottom:1px solid #F7F7F7;}
.bk-ci:last-child{border-bottom:none;}
.bk-ci-img{width:66px;height:66px;background:#F5F5F5;border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:34px;flex-shrink:0;}
.bk-ci-info{flex:1;min-width:0;}
.bk-ci-name{font-size:13px;font-weight:600;color:#1A1A1A;line-height:1.35;margin-bottom:2px;}
.bk-ci-wt{font-size:11.5px;color:#999;margin-bottom:5px;}
.bk-ci-wish{font-size:11.5px;color:#AAAAAA;text-decoration:underline;text-decoration-style:dashed;background:none;border:none;cursor:pointer;padding:0;}
.bk-ci-right{display:flex;flex-direction:column;align-items:flex-end;gap:6px;flex-shrink:0;}
.bk-ci-price{font-size:13px;font-weight:600;color:#1A1A1A;}
.bk-qty{display:flex;align-items:center;background:#0C831F;border-radius:7px;overflow:hidden;height:30px;width:84px;}
.bk-qty-btn{width:28px;height:30px;background:transparent;border:none;color:#fff;font-size:18px;font-weight:700;cursor:pointer;display:flex;align-items:center;justify-content:center;line-height:1;}
.bk-qty-n{color:#fff;font-size:13.5px;font-weight:700;flex:1;text-align:center;}
.bk-sb{background:#fff;margin:0 10px 8px;border-radius:16px;border:1px solid #EBEBEB;padding:16px 14px;}
.bk-sb-h{display:flex;align-items:center;gap:8px;margin-bottom:6px;}
.bk-sb-icon{width:30px;height:30px;background:#FFF3E0;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:15px;}
.bk-sb-title{font-size:15.5px;font-weight:700;color:#1A1A1A;}
.bk-sb-badge{font-size:9px;font-weight:700;background:#E8F5E9;color:#0C831F;padding:2px 8px;border-radius:20px;letter-spacing:0.3px;}
.bk-sb-sub{font-size:12.5px;color:#777;line-height:1.55;margin-bottom:14px;padding-left:38px;}
.bk-analyze{width:100%;background:#0C831F;border:none;border-radius:11px;color:#fff;font-size:15px;font-weight:700;padding:13px 0;cursor:pointer;display:flex;align-items:center;justify-content:center;gap:7px;}
.bk-analyze.done{background:transparent;border:1.5px solid #0C831F;color:#0C831F;}
.bk-analyze:disabled{cursor:default;opacity:0.9;}
.bk-recs{background:#fff;margin:0 10px 8px;border-radius:16px;border:1px solid #EBEBEB;padding:14px 0;}
.bk-recs-h{display:flex;align-items:center;justify-content:space-between;padding:0 14px 12px;}
.bk-recs-title{font-size:15.5px;font-weight:700;color:#1A1A1A;}
.bk-recs-ai{font-size:9px;font-weight:700;background:#E8F5E9;color:#0C831F;padding:2px 8px;border-radius:20px;display:none;}
.bk-recs-ai.visible{display:block;}
.bk-recs-scroll{display:flex;gap:10px;overflow-x:auto;padding:0 14px 4px;scrollbar-width:none;}
.bk-recs-scroll::-webkit-scrollbar{display:none;}
.bk-rc{background:#fff;border:1px solid #E4E4E4;border-radius:12px;width:148px;flex-shrink:0;overflow:hidden;opacity:1;transform:translateY(0);transition:opacity 0.35s ease,transform 0.35s ease;}
.bk-rc.entering{opacity:0;transform:translateY(16px);}
.bk-rc-img{background:#F7F7F7;height:126px;display:flex;align-items:center;justify-content:center;position:relative;font-size:52px;}
.bk-rc-heart{position:absolute;top:6px;right:8px;font-size:16px;color:#CCC;cursor:pointer;}
.bk-rc-add{position:absolute;bottom:8px;left:50%;transform:translateX(-50%);background:#fff;border:1.5px solid #0C831F;border-radius:7px;color:#0C831F;font-size:13px;font-weight:700;padding:4px 0;width:106px;cursor:pointer;white-space:nowrap;}
.bk-rc-add.added{background:#0C831F;color:#fff;}
.bk-rc-body{padding:8px 9px 10px;}
.bk-rc-meta{font-size:9px;color:#0C831F;font-weight:600;margin-bottom:2px;}
.bk-rc-meta span{color:#999;font-weight:400;}
.bk-rc-name{font-size:12px;font-weight:600;color:#1A1A1A;line-height:1.35;margin-bottom:5px;min-height:30px;}
.bk-rc-sp{font-size:10px;color:#0C831F;background:#E8F5E9;border-radius:6px;padding:4px 8px;margin:4px 0;line-height:1.4;}
.bk-rc-reason{font-size:10px;color:#555;font-style:italic;margin-bottom:6px;line-height:1.4;}
.bk-rc-stars{color:#FFB800;font-size:10.5px;}
.bk-rc-reviews{font-size:9.5px;color:#AAA;}
.bk-rc-price{font-size:14.5px;font-weight:700;color:#1A1A1A;margin:4px 0 8px;}
.bk-rc-more{width:100%;background:transparent;border:1px solid #D0EDD6;border-radius:6px;color:#0C831F;font-size:10px;font-weight:600;padding:5px 0;cursor:pointer;}
.bk-see-all{background:#fff;margin:0 10px 8px;border-radius:12px;border:1px solid #EBEBEB;padding:13px 16px;display:flex;align-items:center;justify-content:center;gap:8px;cursor:pointer;}
.bk-see-all-t{font-size:13.5px;font-weight:600;color:#0C831F;}
.bk-bill{background:#fff;margin:0 10px 8px;border-radius:16px;border:1px solid #EBEBEB;padding:14px 14px 12px;}
.bk-bill-title{font-size:16px;font-weight:700;color:#1A1A1A;margin-bottom:10px;}
.bk-bill-row{display:flex;justify-content:space-between;align-items:center;padding:8px 0;border-bottom:1px solid #F9F9F9;}
.bk-bill-label{display:flex;align-items:center;gap:7px;font-size:13.5px;color:#333;}
.bk-bill-icon{font-size:14px;}
.bk-bill-amt{font-size:13.5px;color:#333;}
.bk-bill-sub{font-size:11.5px;color:#E87722;margin:2px 0 6px 22px;line-height:1.4;}
.bk-bill-total{display:flex;justify-content:space-between;padding-top:12px;margin-top:2px;border-top:1px solid #EFEFEF;}
.bk-bill-total-l{font-size:15px;font-weight:700;color:#1A1A1A;}
.bk-bill-total-a{font-size:15px;font-weight:700;color:#1A1A1A;}
.bk-gstin{background:#fff;margin:0 10px 8px;border-radius:12px;border:1px solid #EBEBEB;padding:14px;display:flex;align-items:center;gap:12px;cursor:pointer;}
.bk-gstin-icon{width:38px;height:38px;background:#EEF2FF;border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:18px;flex-shrink:0;}
.bk-gstin-title{font-size:14px;font-weight:700;color:#1A1A1A;}
.bk-gstin-sub{font-size:12px;color:#999;margin-top:1px;}
.bk-gstin-arrow{font-size:20px;color:#CCC;margin-left:auto;}
.bk-tip{background:#fff;margin:0 10px 8px;border-radius:16px;border:1px solid #EBEBEB;padding:16px 14px 14px;}
.bk-tip-h{display:flex;gap:10px;margin-bottom:12px;}
.bk-tip-text{flex:1;}
.bk-tip-heading{font-size:16px;font-weight:700;color:#1A1A1A;margin-bottom:5px;}
.bk-tip-sub{font-size:12px;color:#666;line-height:1.55;}
.bk-tip-emoji{font-size:42px;flex-shrink:0;align-self:flex-start;}
.bk-tip-opts{display:flex;gap:8px;}
.bk-tip-btn{flex:1;border:1.5px solid #DEDEDE;border-radius:10px;padding:9px 4px;background:#fff;cursor:pointer;font-size:12px;color:#1A1A1A;text-align:center;line-height:1.4;}
.bk-tip-btn.sel{border-color:#0C831F;background:#E8F5E9;font-weight:700;}
.bk-gift{background:#fff;margin:0 10px 8px;border-radius:12px;border:1px solid #EBEBEB;padding:14px;display:flex;align-items:center;gap:12px;}
.bk-gift-icon{font-size:34px;flex-shrink:0;}
.bk-gift-title{font-size:14px;font-weight:700;color:#1A1A1A;}
.bk-gift-sub{font-size:12px;color:#999;margin-top:2px;}
.bk-gift-sel{margin-left:auto;flex-shrink:0;border:1.5px solid #0C831F;border-radius:8px;background:#fff;color:#0C831F;font-size:13.5px;font-weight:700;padding:8px 16px;cursor:pointer;}
.bk-cancel{background:#fff;margin:0 10px 8px;border-radius:12px;border:1px solid #EBEBEB;padding:14px;}
.bk-cancel-title{font-size:14px;font-weight:700;color:#1A1A1A;margin-bottom:6px;}
.bk-cancel-text{font-size:12.5px;color:#777;line-height:1.65;}
.bk-cta-area{background:#fff;border-top:1px solid #F0F0F0;padding:11px 14px 0;flex-shrink:0;}
.bk-cta{width:100%;background:#0C831F;border:none;border-radius:14px;color:#fff;font-size:15.5px;font-weight:700;padding:15px 0;cursor:pointer;letter-spacing:0.1px;}
.bk-home{background:#fff;display:flex;justify-content:center;align-items:center;padding:10px 0 16px;flex-shrink:0;}
.bk-home-bar{width:134px;height:5px;background:#1A1A1A;border-radius:3px;}
.bk-dots{display:flex;gap:4px;align-items:center;}
.bk-dot{width:7px;height:7px;background:#0C831F;border-radius:50%;animation:bkbounce 1.1s infinite ease-in-out;}
.bk-dot:nth-child(2){animation-delay:0.18s;}
.bk-dot:nth-child(3){animation-delay:0.36s;}
@keyframes bkbounce{0%,80%,100%{transform:translateY(0);}40%{transform:translateY(-5px);}}
</style>

<div class="bk-wrap">
 <div class="bk-phone">
  <div class="bk-screen">
   <div class="bk-status">
    <span class="bk-time">9:41</span>
    <div class="bk-di"><div class="bk-di-s"></div><div class="bk-di-c"></div></div>
    <div class="bk-icons">
     <div class="bk-bars">
      <div class="bk-bar" style="height:4px"></div>
      <div class="bk-bar" style="height:6px"></div>
      <div class="bk-bar" style="height:9px"></div>
      <div class="bk-bar" style="height:12px"></div>
     </div>
     <svg width="16" height="12" viewBox="0 0 16 12" fill="none">
      <circle cx="8" cy="10.5" r="1.4" fill="#1A1A1A"/>
      <path d="M4.8 7.5a4.5 4.5 0 016.4 0" stroke="#1A1A1A" stroke-width="1.5" stroke-linecap="round"/>
      <path d="M2 4.8a8.5 8.5 0 0112 0" stroke="#1A1A1A" stroke-width="1.5" stroke-linecap="round"/>
     </svg>
     <div class="bk-bat-wrap"><div class="bk-bat"><div class="bk-bat-fill"></div></div><div class="bk-bat-tip"></div></div>
    </div>
   </div>
   <div class="bk-nav">
    <button class="bk-back">&#8249;</button>
    <span class="bk-title">Checkout</span>
    <button class="bk-share">&#128722; Share</button>
   </div>
   <div class="bk-scroll">
    <div class="bk-card">
     <div class="bk-del-banner">
      <div class="bk-del-icon">&#9201;</div>
      <div>
       <div class="bk-del-time" id="bkDelTime">Loading...</div>
       <div class="bk-del-sub" id="bkItemCount">Loading...</div>
      </div>
     </div>
     <div id="bkCartItems"></div>
    </div>
    <div class="bk-sb">
     <div class="bk-sb-h">
      <div class="bk-sb-icon">&#10022;</div>
      <span class="bk-sb-title">Smart Basket</span>
      <span class="bk-sb-badge">AI</span>
     </div>
     <div class="bk-sb-sub">Discover one new product that matches how you already shop.</div>
     <button class="bk-analyze __BTN_CLASS__" id="bkAnalyzeBtn" __BTN_DISABLED__ __BTN_ONCLICK__>__BTN_HTML__</button>
    </div>
    <div class="bk-recs">
     <div class="bk-recs-h">
      <span class="bk-recs-title" id="bkRecsTitle">__RECS_TITLE__</span>
      <span class="bk-recs-ai __AI_BADGE__">AI Powered</span>
     </div>
     <div class="bk-recs-scroll" id="bkRecsScroll"></div>
    </div>
    <div class="bk-see-all"><span style="font-size:20px">&#128717;</span><span class="bk-see-all-t">See all products &#9658;</span></div>
    <div class="bk-bill">
     <div class="bk-bill-title">Bill details</div>
     <div class="bk-bill-row"><div class="bk-bill-label"><span class="bk-bill-icon">&#128203;</span> Items total</div><div class="bk-bill-amt" id="bkBillItems">&#8377;0</div></div>
     <div class="bk-bill-row"><div class="bk-bill-label"><span class="bk-bill-icon">&#128717;</span> <span style="text-decoration:underline;text-decoration-style:dashed;text-underline-offset:3px">Handling charge</span></div><div class="bk-bill-amt">&#8377;2</div></div>
     <div class="bk-bill-row"><div class="bk-bill-label"><span class="bk-bill-icon">&#128757;</span> <span style="text-decoration:underline;text-decoration-style:dashed;text-underline-offset:3px">Delivery charge</span></div><div class="bk-bill-amt" id="bkBillDelivery">&#8377;30</div></div>
     <div class="bk-bill-sub" id="bkDeliveryNote">Pay only &#8377;16 as delivery fee by shopping above &#8377;199</div>
     <div id="bkTipRow" style="display:none" class="bk-bill-row"><div class="bk-bill-label"><span class="bk-bill-icon">&#128155;</span> Tip</div><div class="bk-bill-amt" id="bkBillTip">&#8377;0</div></div>
     <div class="bk-bill-total"><span class="bk-bill-total-l">Grand total</span><span class="bk-bill-total-a" id="bkGrandTotal">&#8377;0</span></div>
    </div>
    <div class="bk-gstin"><div class="bk-gstin-icon">&#127991;</div><div><div class="bk-gstin-title">Add GSTIN</div><div class="bk-gstin-sub">Claim GST input credit up to 28% on your order</div></div><span class="bk-gstin-arrow">&#8250;</span></div>
    <div class="bk-tip">
     <div class="bk-tip-h">
      <div class="bk-tip-text"><div class="bk-tip-heading">Tip your delivery partner</div><div class="bk-tip-sub">Your kindness means a lot! 100% of your tip will go directly to your delivery partner.</div></div>
      <div class="bk-tip-emoji">&#128757;</div>
     </div>
     <div class="bk-tip-opts">
      <button class="bk-tip-btn" onclick="bkTip(this,20)">&#128518;<br>&#8377;20</button>
      <button class="bk-tip-btn" onclick="bkTip(this,30)">&#129321;<br>&#8377;30</button>
      <button class="bk-tip-btn" onclick="bkTip(this,50)">&#128525;<br>&#8377;50</button>
      <button class="bk-tip-btn" onclick="bkTip(this,0)">&#129309;<br>Custom</button>
     </div>
    </div>
    <div class="bk-gift"><span class="bk-gift-icon">&#127873;</span><div><div class="bk-gift-title">Gift Packaging</div><div class="bk-gift-sub">Get your items in a special gift bag for just &#8377;30</div></div><button class="bk-gift-sel">Select</button></div>
    <div class="bk-cancel"><div class="bk-cancel-title">Cancellation Policy</div><div class="bk-cancel-text">Orders cannot be cancelled once packed for delivery. In case of unexpected delays, a refund will be provided, if applicable.</div></div>
    <div style="height:10px"></div>
   </div>
   <div class="bk-cta-area"><button class="bk-cta">Select address at next step &#9658;</button></div>
   <div class="bk-home"><div class="bk-home-bar"></div></div>
  </div>
 </div>
</div>

<script>
var bkTipAmt=0,bkAdded={};
function bkStars(r){var f=Math.floor(r),h=r-f>=0.3?'&#189;':'',e=5-f-(h?1:0);return'&#9733;'.repeat(f)+h+'&#9734;'.repeat(e);}
function bkRenderCart(){
  var del=BK_ITEMS[0]?'__DELIVERY__':'';
  document.getElementById('bkDelTime').textContent=del||'';
  var vis=BK_ITEMS.filter(function(i){return(BK_QTYS[i.name]||0)>0;});
  document.getElementById('bkItemCount').textContent='Shipment of '+vis.length+' item'+(vis.length!==1?'s':'');
  document.getElementById('bkCartItems').innerHTML=vis.map(function(it){
    return '<div class="bk-ci">'+
      '<div class="bk-ci-img">'+it.emoji+'</div>'+
      '<div class="bk-ci-info">'+
        '<div class="bk-ci-name">'+it.name+'</div>'+
        '<div class="bk-ci-wt">'+it.weight+'</div>'+
        '<button class="bk-ci-wish">Move to wishlist</button>'+
      '</div>'+
      '<div class="bk-ci-right">'+
        '<div class="bk-qty">'+
          '<button class="bk-qty-btn" onclick="bkChgQty(\''+it.name+'\',-1)">&#8722;</button>'+
          '<span class="bk-qty-n">'+BK_QTYS[it.name]+'</span>'+
          '<button class="bk-qty-btn" onclick="bkChgQty(\''+it.name+'\',1)">+</button>'+
        '</div>'+
        '<div class="bk-ci-price">&#8377;'+(it.price*BK_QTYS[it.name])+'</div>'+
      '</div>'+
    '</div>';
  }).join('');
  bkUpdateBill();
}
function bkChgQty(name,d){BK_QTYS[name]=Math.max(0,(BK_QTYS[name]||0)+d);bkRenderCart();}
function bkUpdateBill(){
  var tot=BK_ITEMS.reduce(function(s,i){return s+(i.price*(BK_QTYS[i.name]||0));},0);
  var del=tot>=199?16:30;
  document.getElementById('bkBillItems').textContent='&#8377;'+tot;
  document.getElementById('bkBillDelivery').textContent='&#8377;'+del;
  document.getElementById('bkGrandTotal').textContent='&#8377;'+(tot+2+del+bkTipAmt);
  document.getElementById('bkDeliveryNote').style.display=tot>=199?'none':'block';
  var tr=document.getElementById('bkTipRow');
  if(bkTipAmt>0){tr.style.display='flex';document.getElementById('bkBillTip').textContent='&#8377;'+bkTipAmt;}
  else{tr.style.display='none';}
}
function bkTip(btn,amt){document.querySelectorAll('.bk-tip-btn').forEach(function(b){b.classList.remove('sel');});btn.classList.add('sel');bkTipAmt=amt;bkUpdateBill();}
function bkRenderRecs(recs,animate){
  document.getElementById('bkRecsScroll').innerHTML=recs.map(function(p){
    return '<div class="bk-rc'+(animate?' entering':'')+'">'+
      '<div class="bk-rc-img">'+p.emoji+
        '<span class="bk-rc-heart">&#9825;</span>'+
        '<button class="bk-rc-add'+(bkAdded[p.price]?' added':'')+'" onclick="bkAdd(this,'+p.price+')">'+(bkAdded[p.price]?'ADDED &#10003;':'ADD')+'</button>'+
      '</div>'+
      '<div class="bk-rc-body">'+
        '<div class="bk-rc-meta">'+p.weight+' &middot; <span>'+p.category+'</span></div>'+
        '<div class="bk-rc-name">'+p.name+'</div>'+
        (p.social_proof?'<div class="bk-rc-sp">&#128101; '+p.social_proof+'</div>':'')+
        (p.reason?'<div class="bk-rc-reason">'+p.reason+'</div>':'')+
        '<div><span class="bk-rc-stars">'+bkStars(p.rating)+'</span> <span class="bk-rc-reviews">('+p.reviews+')</span></div>'+
        '<div class="bk-rc-price">&#8377;'+p.price+'</div>'+
        '<button class="bk-rc-more">See more like this &#9658;</button>'+
      '</div>'+
    '</div>';
  }).join('');
  if(animate){
    requestAnimationFrame(function(){
      document.querySelectorAll('.bk-rc.entering').forEach(function(c,i){
        setTimeout(function(){c.style.transition='opacity 0.4s ease,transform 0.4s ease';c.classList.remove('entering');},i*90);
      });
    });
  }
}
function bkAdd(btn,price){bkAdded[price]=true;btn.textContent='ADDED \u2713';btn.classList.add('added');}
function bkAnalyze(){
  var btn=document.getElementById('bkAnalyzeBtn');
  btn.className='bk-analyze';
  btn.style.background='#E8F5E9';
  btn.style.color='#0C831F';
  btn.innerHTML='<div class="bk-dots"><div class="bk-dot"></div><div class="bk-dot"></div><div class="bk-dot"></div></div><span>Analyzing your basket\u2026</span>';
  btn.disabled=true;
  setTimeout(function(){
    var p=window.parent||window;
    var btns=p.document.querySelectorAll('button[kind="formSubmit"]');
    if(btns.length>0){btns[btns.length-1].click();return;}
    var all=p.document.querySelectorAll('button');
    for(var i=0;i<all.length;i++){if(all[i].textContent.trim()==='analyze'){all[i].click();return;}}
  },100);
}
bkRenderCart();
bkRenderRecs(BK_RECS,BK_ANIMATE);
</script>
"""

HTML = (HTML
    .replace("__DELIVERY__", delivery)
    .replace("__BTN_CLASS__", btn_class)
    .replace("__BTN_DISABLED__", btn_disabled)
    .replace("__BTN_ONCLICK__", btn_onclick)
    .replace("__BTN_HTML__", btn_html)
    .replace("__RECS_TITLE__", recs_title)
    .replace("__AI_BADGE__", ai_badge_cls)
)

st.markdown(HTML, unsafe_allow_html=True)
