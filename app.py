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

# Hide ALL Streamlit chrome + outer container
st.markdown("""
<style>
html,body{background:#E8E8E8!important;margin:0;padding:0;}
.stApp{background:#E8E8E8!important;}
section[data-testid="stSidebar"]{display:none!important;}
header[data-testid="stHeader"]{display:none!important;}
[data-testid="stToolbar"],[data-testid="stDecoration"],[data-testid="stStatusWidget"]{display:none!important;}
[data-testid="stMainBlockContainer"],.block-container{
  padding:0!important;
  max-width:100%!important;
  background:transparent!important;
}
footer{display:none!important;}

/* Kill the iframe wrapper white box */
iframe{
  border:none!important;
  display:block!important;
}
[data-testid="stIFrame"]{
  background:transparent!important;
  border:none!important;
}
.element-container{
  background:transparent!important;
  border:none!important;
  box-shadow:none!important;
  padding:0!important;
  margin:0!important;
}
/* Remove any stVerticalBlock padding/margin */
[data-testid="stVerticalBlock"]{
  gap:0!important;
  padding:0!important;
}
</style>
""", unsafe_allow_html=True)

# ── Data ───────────────────────────────────────────────────────────────────────
BASKETS = [
    {"delivery":"Delivery in 8 minutes","items":[
        {"emoji":"🥛","name":"Amul Taaza Toned Milk","weight":"1 L","price":28,"qty":2},
        {"emoji":"🍞","name":"Britannia Whole Wheat Bread","weight":"400 g","price":40,"qty":1},
        {"emoji":"🥚","name":"Farm Fresh White Eggs","weight":"6 pcs","price":54,"qty":1},
        {"emoji":"☕","name":"Nescafe Classic Instant Coffee","weight":"50 g","price":120,"qty":1},
    ]},
    {"delivery":"Delivery in 9 minutes","items":[
        {"emoji":"🌽","name":"Lay's Magic Masala Chips","weight":"48 g","price":20,"qty":2},
        {"emoji":"🍘","name":"Kurkure Masala Munch Crisps","weight":"75 g","price":20,"qty":2},
        {"emoji":"🍫","name":"Hide and Seek Choco Chip Cookies","weight":"100 g","price":30,"qty":1},
        {"emoji":"🥤","name":"Thums Up Soft Drink","weight":"750 ml","price":40,"qty":1},
    ]},
    {"delivery":"Delivery in 10 minutes","items":[
        {"emoji":"🧈","name":"Amul Butter Salted","weight":"100 g","price":55,"qty":1},
        {"emoji":"🍓","name":"Kissan Mixed Fruit Jam","weight":"200 g","price":70,"qty":1},
        {"emoji":"🧃","name":"Real Activ Orange Juice","weight":"1 L","price":110,"qty":1},
        {"emoji":"🥣","name":"MTR Upma Breakfast Mix","weight":"200 g","price":65,"qty":2},
    ]},
    {"delivery":"Delivery in 8 minutes","items":[
        {"emoji":"🍼","name":"Nestle NAN Pro 1 Baby Formula","weight":"400 g","price":650,"qty":1},
        {"emoji":"🧻","name":"Pampers Baby Wipes Gentle","weight":"72 pcs","price":199,"qty":2},
        {"emoji":"👶","name":"Pampers Newborn Diapers","weight":"20 pcs","price":360,"qty":1},
        {"emoji":"🛁","name":"Johnson Baby Soap Mild","weight":"75 g","price":35,"qty":2},
    ]},
    {"delivery":"Delivery in 12 minutes","items":[
        {"emoji":"🧴","name":"Vim Dishwash Liquid Lemon","weight":"500 ml","price":89,"qty":1},
        {"emoji":"🪣","name":"Harpic Power Plus Toilet Cleaner","weight":"500 ml","price":75,"qty":1},
        {"emoji":"💧","name":"Colin Glass and Surface Cleaner","weight":"500 ml","price":95,"qty":1},
        {"emoji":"🧽","name":"Scotch-Brite Scrub Pad","weight":"3 pcs","price":45,"qty":2},
    ]},
]

DEFAULT_RECS = [
    {"emoji":"🌶️","name":"Everest Tikhalal Chilli Powder","weight":"100 g","category":"Spices","rating":4.4,"reviews":"32,104","price":62,"social_proof":"","reason":""},
    {"emoji":"🫙","name":"Saffola Active Blended Edible Oil","weight":"1 L","category":"Edible Oils","rating":4.5,"reviews":"18,239","price":145,"social_proof":"","reason":""},
    {"emoji":"🧹","name":"Lizol Disinfectant Surface Cleaner","weight":"500 ml","category":"Cleaners","rating":4.6,"reviews":"41,882","price":119,"social_proof":"","reason":""},
]

def get_ai_recommendations(basket_items):
    client = anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])
    basket_str = ", ".join([f"{i['name']} ({i['weight']})" for i in basket_items])
    existing_cats = set()
    for i in basket_items:
        n = i["name"].lower()
        if any(k in n for k in ["milk","butter","cheese","curd","paneer"]): existing_cats.add("dairy")
        elif any(k in n for k in ["chips","kurkure","bingo","lay","cookie","biscuit"]): existing_cats.add("snacks")
        elif any(k in n for k in ["drink","juice","water","tea","coffee","thums"]): existing_cats.add("beverages")
        elif any(k in n for k in ["pamper","baby","nestle","johnson"]): existing_cats.add("baby")
        elif any(k in n for k in ["vim","harpic","colin","lizol","scotch"]): existing_cats.add("cleaning")
        else: existing_cats.add("staples")
    system = """You are the Blinkit Smart Basket AI. Suggest exactly 3 products from NEW categories not in the basket.
Rules: real Indian FMCG products, different categories, natural complements, realistic social proof.
Respond ONLY with a valid JSON array, no markdown:
[{"emoji":"🌶️","name":"Product Name","weight":"100 g","category":"Spices","rating":4.4,"reviews":"32,104","price":62,"social_proof":"Added by 71% of users with similar baskets.","reason":"Natural complement to your setup."}]"""
    msg = client.messages.create(
        model="claude-sonnet-4-6", max_tokens=800, system=system,
        messages=[{"role":"user","content":f"Basket: {basket_str}. Existing: {', '.join(existing_cats)}. Suggest 3 from different categories."}]
    )
    raw = msg.content[0].text.strip()
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

basket  = st.session_state.basket
qtys    = st.session_state.qtys
analyzed = st.session_state.analyzed and bool(st.session_state.ai_recs)

# ── Check query param trigger (set by JS inside iframe) ───────────────────────
if st.query_params.get("analyze") == "1" and not st.session_state.analyzed:
    try:
        visible = [i for i in basket["items"] if qtys.get(i["name"], 0) > 0]
        recs = get_ai_recommendations(visible)
        st.session_state.ai_recs = recs
        st.session_state.analyzed = True
    except Exception as e:
        st.session_state.analyzed = False
    st.query_params.clear()
    st.rerun()

# ── Build data for the iframe ──────────────────────────────────────────────────
recs_data    = st.session_state.ai_recs if analyzed else DEFAULT_RECS
recs_title   = "Smart Basket Picks" if analyzed else "You might also like"
ai_badge     = "visible" if analyzed else ""
btn_class    = "done" if analyzed else ""
btn_label    = "Basket Analyzed" if analyzed else "Analyze My Basket"
btn_disabled = "true" if analyzed else "false"
animate      = "true" if analyzed else "false"

# Serialize to JS
items_js   = json.dumps(basket["items"])
qtys_js    = json.dumps(qtys)
recs_js    = json.dumps(recs_data)
delivery   = json.dumps(basket["delivery"])

# ── Build complete self-contained HTML for the iframe ─────────────────────────
PAGE = (
"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
*{margin:0;padding:0;box-sizing:border-box;}
html,body{background:#E8E8E8;min-height:100%;display:flex;justify-content:center;align-items:flex-start;padding:24px 0 40px;font-family:-apple-system,BlinkMacSystemFont,'SF Pro Text',sans-serif;}
.phone{width:390px;background:#1C1C1E;border-radius:55px;border:2px solid #3A3A3C;position:relative;overflow:hidden;box-shadow:0 0 0 1px #555,0 40px 90px rgba(0,0,0,0.55);}
.phone::before{content:'';position:absolute;left:-5px;top:108px;width:4px;height:32px;background:#3A3A3C;border-radius:3px 0 0 3px;box-shadow:0 50px 0 #3A3A3C,0 94px 0 #3A3A3C;z-index:20;}
.phone::after{content:'';position:absolute;right:-5px;top:162px;width:4px;height:74px;background:#3A3A3C;border-radius:0 3px 3px 0;z-index:20;}
.screen{background:#fff;border-radius:53px;overflow:hidden;display:flex;flex-direction:column;height:844px;}
.status{background:#fff;height:56px;display:flex;align-items:flex-end;justify-content:space-between;padding:0 28px 10px;position:relative;flex-shrink:0;}
.stime{font-size:15px;font-weight:700;color:#1A1A1A;}
.di{position:absolute;top:12px;left:50%;transform:translateX(-50%);width:120px;height:36px;background:#1C1C1E;border-radius:20px;display:flex;align-items:center;justify-content:center;gap:10px;}
.di-s{width:22px;height:10px;background:#2C2C2E;border-radius:7px;border:1.5px solid #444;}
.di-c{width:10px;height:10px;background:#2C2C2E;border-radius:50%;border:1.5px solid #444;}
.icons{display:flex;align-items:center;gap:6px;}
.bars{display:flex;align-items:flex-end;gap:2px;height:12px;}
.bar{width:3px;background:#1A1A1A;border-radius:1px;}
.bat-w{display:flex;align-items:center;gap:1px;}
.bat{width:24px;height:12px;border:1.5px solid #1A1A1A;border-radius:3px;padding:1.5px;}
.bat-f{width:100%;height:100%;background:#1A1A1A;border-radius:1.5px;}
.bat-t{width:2px;height:5px;background:#1A1A1A;border-radius:0 1.5px 1.5px 0;}
.nav{background:#fff;height:50px;display:flex;align-items:center;padding:0 16px;border-bottom:1px solid #EFEFEF;flex-shrink:0;}
.nav-back{font-size:26px;color:#1A1A1A;background:none;border:none;cursor:pointer;padding:4px 12px 4px 0;line-height:1;}
.nav-title{flex:1;text-align:center;font-size:17px;font-weight:600;color:#1A1A1A;}
.nav-share{color:#0C831F;font-size:13.5px;font-weight:600;background:none;border:none;cursor:pointer;}
.scroll{flex:1;overflow-y:auto;background:#F2F3F7;scrollbar-width:none;}
.scroll::-webkit-scrollbar{display:none;}
.card{background:#fff;margin:8px 10px;border-radius:16px;border:1px solid #EBEBEB;overflow:hidden;}
.del-banner{display:flex;align-items:center;gap:10px;padding:12px 14px;border-bottom:1px solid #F2F2F2;}
.del-icon{width:34px;height:34px;background:#EAF7EE;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:16px;flex-shrink:0;}
.del-time{font-size:14.5px;font-weight:700;color:#1A1A1A;}
.del-sub{font-size:12px;color:#999;margin-top:1px;}
.ci{display:flex;align-items:center;gap:12px;padding:12px 14px;border-bottom:1px solid #F7F7F7;}
.ci:last-child{border-bottom:none;}
.ci-img{width:66px;height:66px;background:#F5F5F5;border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:34px;flex-shrink:0;}
.ci-info{flex:1;min-width:0;}
.ci-name{font-size:13px;font-weight:600;color:#1A1A1A;line-height:1.35;margin-bottom:2px;}
.ci-wt{font-size:11.5px;color:#999;margin-bottom:5px;}
.ci-wish{font-size:11.5px;color:#AAA;text-decoration:underline;text-decoration-style:dashed;background:none;border:none;cursor:pointer;padding:0;}
.ci-right{display:flex;flex-direction:column;align-items:flex-end;gap:6px;flex-shrink:0;}
.ci-price{font-size:13px;font-weight:600;color:#1A1A1A;}
.qty{display:flex;align-items:center;background:#0C831F;border-radius:7px;overflow:hidden;height:30px;width:84px;}
.qty-btn{width:28px;height:30px;background:transparent;border:none;color:#fff;font-size:18px;font-weight:700;cursor:pointer;display:flex;align-items:center;justify-content:center;}
.qty-n{color:#fff;font-size:13.5px;font-weight:700;flex:1;text-align:center;}
.sb{background:#fff;margin:0 10px 8px;border-radius:16px;border:1px solid #EBEBEB;padding:16px 14px;}
.sb-h{display:flex;align-items:center;gap:8px;margin-bottom:6px;}
.sb-icon{width:30px;height:30px;background:#FFF3E0;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:15px;}
.sb-title{font-size:15.5px;font-weight:700;color:#1A1A1A;}
.sb-badge{font-size:9px;font-weight:700;background:#E8F5E9;color:#0C831F;padding:2px 8px;border-radius:20px;}
.sb-sub{font-size:12.5px;color:#777;line-height:1.55;margin-bottom:14px;padding-left:38px;}
.abtn{width:100%;background:#0C831F;border:none;border-radius:11px;color:#fff;font-size:15px;font-weight:700;padding:13px 0;cursor:pointer;display:flex;align-items:center;justify-content:center;gap:7px;}
.abtn.done{background:transparent;border:1.5px solid #0C831F;color:#0C831F;}
.abtn:disabled{cursor:default;opacity:0.9;}
.recs{background:#fff;margin:0 10px 8px;border-radius:16px;border:1px solid #EBEBEB;padding:14px 0;}
.recs-h{display:flex;align-items:center;justify-content:space-between;padding:0 14px 12px;}
.recs-title{font-size:15.5px;font-weight:700;color:#1A1A1A;}
.recs-ai{font-size:9px;font-weight:700;background:#E8F5E9;color:#0C831F;padding:2px 8px;border-radius:20px;display:none;}
.recs-ai.visible{display:block;}
.recs-scroll{display:flex;gap:10px;overflow-x:auto;padding:0 14px 4px;scrollbar-width:none;}
.recs-scroll::-webkit-scrollbar{display:none;}
.rc{background:#fff;border:1px solid #E4E4E4;border-radius:12px;width:148px;flex-shrink:0;overflow:hidden;opacity:1;transform:translateY(0);transition:opacity 0.35s ease,transform 0.35s ease;}
.rc.entering{opacity:0;transform:translateY(16px);}
.rc-img{background:#F7F7F7;height:126px;display:flex;align-items:center;justify-content:center;position:relative;font-size:52px;}
.rc-heart{position:absolute;top:6px;right:8px;font-size:16px;color:#CCC;cursor:pointer;}
.rc-add{position:absolute;bottom:8px;left:50%;transform:translateX(-50%);background:#fff;border:1.5px solid #0C831F;border-radius:7px;color:#0C831F;font-size:13px;font-weight:700;padding:4px 0;width:106px;cursor:pointer;white-space:nowrap;}
.rc-add.added{background:#0C831F;color:#fff;}
.rc-body{padding:8px 9px 10px;}
.rc-meta{font-size:9px;color:#0C831F;font-weight:600;margin-bottom:2px;}
.rc-meta span{color:#999;font-weight:400;}
.rc-name{font-size:12px;font-weight:600;color:#1A1A1A;line-height:1.35;margin-bottom:5px;min-height:30px;}
.rc-sp{font-size:10px;color:#0C831F;background:#E8F5E9;border-radius:6px;padding:4px 8px;margin:4px 0;line-height:1.4;}
.rc-reason{font-size:10px;color:#555;font-style:italic;margin-bottom:6px;line-height:1.4;}
.rc-stars{color:#FFB800;font-size:10.5px;}
.rc-reviews{font-size:9.5px;color:#AAA;}
.rc-price{font-size:14.5px;font-weight:700;color:#1A1A1A;margin:4px 0 8px;}
.rc-more{width:100%;background:transparent;border:1px solid #D0EDD6;border-radius:6px;color:#0C831F;font-size:10px;font-weight:600;padding:5px 0;cursor:pointer;}
.see-all{background:#fff;margin:0 10px 8px;border-radius:12px;border:1px solid #EBEBEB;padding:13px 16px;display:flex;align-items:center;justify-content:center;gap:8px;cursor:pointer;}
.see-all-t{font-size:13.5px;font-weight:600;color:#0C831F;}
.bill{background:#fff;margin:0 10px 8px;border-radius:16px;border:1px solid #EBEBEB;padding:14px 14px 12px;}
.bill-title{font-size:16px;font-weight:700;color:#1A1A1A;margin-bottom:10px;}
.bill-row{display:flex;justify-content:space-between;align-items:center;padding:8px 0;border-bottom:1px solid #F9F9F9;}
.bill-label{display:flex;align-items:center;gap:7px;font-size:13.5px;color:#333;}
.bill-icon{font-size:14px;}
.bill-amt{font-size:13.5px;color:#333;}
.bill-sub{font-size:11.5px;color:#E87722;margin:2px 0 6px 22px;line-height:1.4;}
.bill-total{display:flex;justify-content:space-between;padding-top:12px;margin-top:2px;border-top:1px solid #EFEFEF;}
.bill-total-l{font-size:15px;font-weight:700;color:#1A1A1A;}
.bill-total-a{font-size:15px;font-weight:700;color:#1A1A1A;}
.gstin{background:#fff;margin:0 10px 8px;border-radius:12px;border:1px solid #EBEBEB;padding:14px;display:flex;align-items:center;gap:12px;cursor:pointer;}
.gstin-icon{width:38px;height:38px;background:#EEF2FF;border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:18px;flex-shrink:0;}
.gstin-title{font-size:14px;font-weight:700;color:#1A1A1A;}
.gstin-sub{font-size:12px;color:#999;margin-top:1px;}
.gstin-arrow{font-size:20px;color:#CCC;margin-left:auto;}
.tip{background:#fff;margin:0 10px 8px;border-radius:16px;border:1px solid #EBEBEB;padding:16px 14px 14px;}
.tip-h{display:flex;gap:10px;margin-bottom:12px;}
.tip-text{flex:1;}
.tip-heading{font-size:16px;font-weight:700;color:#1A1A1A;margin-bottom:5px;}
.tip-sub{font-size:12px;color:#666;line-height:1.55;}
.tip-e{font-size:42px;flex-shrink:0;align-self:flex-start;}
.tip-opts{display:flex;gap:8px;}
.tip-btn{flex:1;border:1.5px solid #DEDEDE;border-radius:10px;padding:9px 4px;background:#fff;cursor:pointer;font-size:12px;color:#1A1A1A;text-align:center;line-height:1.4;}
.tip-btn.sel{border-color:#0C831F;background:#E8F5E9;font-weight:700;}
.gift{background:#fff;margin:0 10px 8px;border-radius:12px;border:1px solid #EBEBEB;padding:14px;display:flex;align-items:center;gap:12px;}
.gift-icon{font-size:34px;flex-shrink:0;}
.gift-title{font-size:14px;font-weight:700;color:#1A1A1A;}
.gift-sub{font-size:12px;color:#999;margin-top:2px;}
.gift-sel{margin-left:auto;flex-shrink:0;border:1.5px solid #0C831F;border-radius:8px;background:#fff;color:#0C831F;font-size:13.5px;font-weight:700;padding:8px 16px;cursor:pointer;}
.cancel{background:#fff;margin:0 10px 8px;border-radius:12px;border:1px solid #EBEBEB;padding:14px;}
.cancel-title{font-size:14px;font-weight:700;color:#1A1A1A;margin-bottom:6px;}
.cancel-text{font-size:12.5px;color:#777;line-height:1.65;}
.cta-area{background:#fff;border-top:1px solid #F0F0F0;padding:11px 14px 0;flex-shrink:0;}
.cta{width:100%;background:#0C831F;border:none;border-radius:14px;color:#fff;font-size:15.5px;font-weight:700;padding:15px 0;cursor:pointer;}
.home{background:#fff;display:flex;justify-content:center;align-items:center;padding:10px 0 16px;flex-shrink:0;}
.home-bar{width:134px;height:5px;background:#1A1A1A;border-radius:3px;}
.dots{display:flex;gap:4px;align-items:center;}
.dot{width:7px;height:7px;background:#0C831F;border-radius:50%;animation:bounce 1.1s infinite ease-in-out;}
.dot:nth-child(2){animation-delay:.18s}.dot:nth-child(3){animation-delay:.36s}
@keyframes bounce{0%,80%,100%{transform:translateY(0)}40%{transform:translateY(-5px)}}
</style>
</head>
<body>
<div class="phone">
 <div class="screen">
  <div class="status">
   <span class="stime">9:41</span>
   <div class="di"><div class="di-s"></div><div class="di-c"></div></div>
   <div class="icons">
    <div class="bars"><div class="bar" style="height:4px"></div><div class="bar" style="height:6px"></div><div class="bar" style="height:9px"></div><div class="bar" style="height:12px"></div></div>
    <svg width="16" height="12" viewBox="0 0 16 12" fill="none"><circle cx="8" cy="10.5" r="1.4" fill="#1A1A1A"/><path d="M4.8 7.5a4.5 4.5 0 016.4 0" stroke="#1A1A1A" stroke-width="1.5" stroke-linecap="round"/><path d="M2 4.8a8.5 8.5 0 0112 0" stroke="#1A1A1A" stroke-width="1.5" stroke-linecap="round"/></svg>
    <div class="bat-w"><div class="bat"><div class="bat-f"></div></div><div class="bat-t"></div></div>
   </div>
  </div>
  <div class="nav">
   <button class="nav-back">&#8249;</button>
   <span class="nav-title">Checkout</span>
   <button class="nav-share">&#128722; Share</button>
  </div>
  <div class="scroll">
   <div class="card">
    <div class="del-banner">
     <div class="del-icon">&#9201;</div>
     <div><div class="del-time" id="delTime"></div><div class="del-sub" id="itemCount"></div></div>
    </div>
    <div id="cartItems"></div>
   </div>
   <div class="sb">
    <div class="sb-h"><div class="sb-icon">&#10022;</div><span class="sb-title">Smart Basket</span><span class="sb-badge">AI</span></div>
    <div class="sb-sub">Discover one new product that matches how you already shop.</div>
    <button class="abtn """ + btn_class + """" id="aBtn" """ + ("disabled" if analyzed else "") + """ onclick="doAnalyze()">
     """ + ("&#10003;&nbsp;Basket Analyzed" if analyzed else "&#10022; Analyze My Basket") + """
    </button>
   </div>
   <div class="recs">
    <div class="recs-h">
     <span class="recs-title" id="recsTitle">""" + recs_title + """</span>
     <span class="recs-ai """ + ai_badge + """">AI Powered</span>
    </div>
    <div class="recs-scroll" id="recsScroll"></div>
   </div>
   <div class="see-all"><span style="font-size:20px">&#128717;</span><span class="see-all-t">See all products &#9658;</span></div>
   <div class="bill">
    <div class="bill-title">Bill details</div>
    <div class="bill-row"><div class="bill-label"><span class="bill-icon">&#128203;</span> Items total</div><div class="bill-amt" id="bItems">&#8377;0</div></div>
    <div class="bill-row"><div class="bill-label"><span class="bill-icon">&#128717;</span> <span style="text-decoration:underline;text-decoration-style:dashed">Handling charge</span></div><div class="bill-amt">&#8377;2</div></div>
    <div class="bill-row"><div class="bill-label"><span class="bill-icon">&#128757;</span> <span style="text-decoration:underline;text-decoration-style:dashed">Delivery charge</span></div><div class="bill-amt" id="bDel">&#8377;30</div></div>
    <div class="bill-sub" id="delNote">Pay only &#8377;16 as delivery fee by shopping above &#8377;199</div>
    <div id="tipRow" style="display:none" class="bill-row"><div class="bill-label"><span class="bill-icon">&#128155;</span> Tip</div><div class="bill-amt" id="bTip">&#8377;0</div></div>
    <div class="bill-total"><span class="bill-total-l">Grand total</span><span class="bill-total-a" id="bGrand">&#8377;0</span></div>
   </div>
   <div class="gstin"><div class="gstin-icon">&#127991;</div><div><div class="gstin-title">Add GSTIN</div><div class="gstin-sub">Claim GST input credit up to 28% on your order</div></div><span class="gstin-arrow">&#8250;</span></div>
   <div class="tip">
    <div class="tip-h"><div class="tip-text"><div class="tip-heading">Tip your delivery partner</div><div class="tip-sub">Your kindness means a lot! 100% of your tip will go directly to your delivery partner.</div></div><div class="tip-e">&#128757;</div></div>
    <div class="tip-opts">
     <button class="tip-btn" onclick="doTip(this,20)">&#128518;<br>&#8377;20</button>
     <button class="tip-btn" onclick="doTip(this,30)">&#129321;<br>&#8377;30</button>
     <button class="tip-btn" onclick="doTip(this,50)">&#128525;<br>&#8377;50</button>
     <button class="tip-btn" onclick="doTip(this,0)">&#129309;<br>Custom</button>
    </div>
   </div>
   <div class="gift"><span class="gift-icon">&#127873;</span><div><div class="gift-title">Gift Packaging</div><div class="gift-sub">Get your items in a special gift bag for just &#8377;30</div></div><button class="gift-sel">Select</button></div>
   <div class="cancel"><div class="cancel-title">Cancellation Policy</div><div class="cancel-text">Orders cannot be cancelled once packed for delivery. In case of unexpected delays, a refund will be provided, if applicable.</div></div>
   <div style="height:10px"></div>
  </div>
  <div class="cta-area"><button class="cta">Select address at next step &#9658;</button></div>
  <div class="home"><div class="home-bar"></div></div>
 </div>
</div>
<script>
var ITEMS=""" + items_js + """;
var QTYS=""" + qtys_js + """;
var RECS=""" + recs_js + """;
var DELIVERY=""" + delivery + """;
var ANIMATE=""" + animate + """;
var tipAmt=0,added={};
function stars(r){var f=Math.floor(r),h=r-f>=0.3?'&frac12;':'',e=5-f-(h?1:0);return'&#9733;'.repeat(f)+h+'&#9734;'.repeat(e);}
function renderCart(){
  document.getElementById('delTime').textContent=DELIVERY;
  var vis=ITEMS.filter(function(i){return(QTYS[i.name]||0)>0;});
  document.getElementById('itemCount').textContent='Shipment of '+vis.length+' item'+(vis.length!==1?'s':'');
  document.getElementById('cartItems').innerHTML=vis.map(function(it){
    var q=QTYS[it.name];
    return '<div class="ci">'+
      '<div class="ci-img">'+it.emoji+'</div>'+
      '<div class="ci-info"><div class="ci-name">'+it.name+'</div><div class="ci-wt">'+it.weight+'</div><button class="ci-wish">Move to wishlist</button></div>'+
      '<div class="ci-right">'+
        '<div class="qty">'+
          '<button class="qty-btn" onclick="chgQ(\''+it.name+'\',-1)">&#8722;</button>'+
          '<span class="qty-n">'+q+'</span>'+
          '<button class="qty-btn" onclick="chgQ(\''+it.name+'\',1)">+</button>'+
        '</div>'+
        '<div class="ci-price">&#8377;'+(it.price*q)+'</div>'+
      '</div>'+
    '</div>';
  }).join('');
  updateBill();
}
function chgQ(n,d){QTYS[n]=Math.max(0,(QTYS[n]||0)+d);renderCart();}
function updateBill(){
  var tot=ITEMS.reduce(function(s,i){return s+(i.price*(QTYS[i.name]||0));},0);
  var del=tot>=199?16:30;
  document.getElementById('bItems').textContent='&#8377;'+tot;
  document.getElementById('bDel').textContent='&#8377;'+del;
  document.getElementById('bGrand').textContent='&#8377;'+(tot+2+del+tipAmt);
  document.getElementById('delNote').style.display=tot>=199?'none':'block';
  var tr=document.getElementById('tipRow');
  if(tipAmt>0){tr.style.display='flex';document.getElementById('bTip').textContent='&#8377;'+tipAmt;}
  else tr.style.display='none';
}
function doTip(b,a){document.querySelectorAll('.tip-btn').forEach(function(x){x.classList.remove('sel');});b.classList.add('sel');tipAmt=a;updateBill();}
function renderRecs(recs,anim){
  document.getElementById('recsScroll').innerHTML=recs.map(function(p){
    return '<div class="rc'+(anim?' entering':'')+'">'+
      '<div class="rc-img">'+p.emoji+'<span class="rc-heart">&#9825;</span>'+
        '<button class="rc-add'+(added[p.price]?' added':'')+'" onclick="addRec(this,'+p.price+')">'+(added[p.price]?'ADDED &#10003;':'ADD')+'</button>'+
      '</div>'+
      '<div class="rc-body">'+
        '<div class="rc-meta">'+p.weight+' &middot; <span>'+p.category+'</span></div>'+
        '<div class="rc-name">'+p.name+'</div>'+
        (p.social_proof?'<div class="rc-sp">&#128101; '+p.social_proof+'</div>':'')+
        (p.reason?'<div class="rc-reason">'+p.reason+'</div>':'')+
        '<div><span class="rc-stars">'+stars(p.rating)+'</span> <span class="rc-reviews">('+p.reviews+')</span></div>'+
        '<div class="rc-price">&#8377;'+p.price+'</div>'+
        '<button class="rc-more">See more like this &#9658;</button>'+
      '</div></div>';
  }).join('');
  if(anim){requestAnimationFrame(function(){document.querySelectorAll('.rc.entering').forEach(function(c,i){setTimeout(function(){c.style.transition='opacity .4s ease,transform .4s ease';c.classList.remove('entering');},i*90);});});}
}
function addRec(b,p){added[p]=true;b.textContent='ADDED \u2713';b.classList.add('added');}
function doAnalyze(){
  var b=document.getElementById('aBtn');
  b.className='abtn';b.style.background='#E8F5E9';b.style.color='#0C831F';
  b.innerHTML='<div class="dots"><div class="dot"></div><div class="dot"></div><div class="dot"></div></div><span>Analyzing\u2026</span>';
  b.disabled=true;
  // Navigate the TOP window to trigger Streamlit rerun with ?analyze=1
  window.top.location.href=window.top.location.pathname+'?analyze=1';
}
renderCart();
renderRecs(RECS,ANIMATE);
</script>
</body>
</html>"""
)

st.components.v1.html(PAGE, height=940, scrolling=False)
