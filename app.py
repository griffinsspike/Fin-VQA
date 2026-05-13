"""
Fin-VQA: BIST Intelligence Terminal
TradingView-style UI · Gemini AI Analysis + Chat · Auth Gate
"""
import html as _html
import logging, os
from datetime import datetime
import streamlit as st
from dotenv import load_dotenv

from src.config import (
    BIST100_TICKERS, GEMINI_MODELS, LOG_DATE_FORMAT,
    PERIOD_OPTIONS, SECTOR_CLUSTERS,
    get_sector_for_ticker, get_peers_for_ticker,
)
from src.data_pipeline import (
    fetch_fundamentals, fetch_news, fetch_stock_data, fetch_bist_overview,
    format_fundamentals_text, format_news_text,
)
from src.history_manager import AnalysisHistory
from src.indicators import add_all_indicators, get_indicator_summary
from src.visualizations import chart_to_image, create_candlestick_chart
from src.vqa_engine import analyze_stock, chat_with_ai, initialize_model

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s │ %(name)s │ %(levelname)s │ %(message)s",
                    datefmt=LOG_DATE_FORMAT)
logger = logging.getLogger(__name__)
load_dotenv()
history_manager = AnalysisHistory()

# ── Page config (must be first st call) ─────────────────────────────────────
st.set_page_config(
    page_title="Fin-VQA · BIST Intelligence Terminal",
    page_icon="◆", layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Design tokens (shared CSS variables) ─────────────────────────────────────
DESIGN_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

:root {
  --bg-primary:#0b0e1a; --bg-panel:#131722; --bg-card:#1a1f2e;
  --bg-card-hover:#1e2436; --bg-soft:#10141f;
  --border:#2a2e3f; --border-strong:#363b4f;
  --border-accent:rgba(0,212,170,.3);
  --text:#e8eaed; --text-2:#94a3b8; --text-3:#566278;
  --teal:#00d4aa; --teal-dim:rgba(0,212,170,.12);
  --up:#26a69a; --down:#ef5350; --warn:#f5a524;
  --mono:'JetBrains Mono',ui-monospace,Menlo,monospace;
}
*{box-sizing:border-box}
html,body,[class*="css"]{font-family:'Inter',system-ui,sans-serif;font-size:13px;}

/* ── Streamlit chrome reset ── */
.stApp{background:var(--bg-primary)!important;}
#MainMenu,footer,header{visibility:hidden!important;}
section[data-testid="stSidebar"]{display:none!important;}
.block-container{padding:0!important;max-width:100%!important;}
[data-testid="stDecoration"]{display:none!important;}
[data-testid="stStatusWidget"]{display:none!important;}
div[data-testid="stToolbar"]{display:none!important;}
[data-testid="stHorizontalBlock"]{gap:1px!important;background:var(--border);}
[data-testid="stHorizontalBlock"]>div{background:var(--bg-primary);}
</style>
"""

# ══════════════════════════════════════════════════════════════════════════════
# AUTH
# ══════════════════════════════════════════════════════════════════════════════

AUTH_CSS = """
<style>
/* Full-page auth background */
.stApp{
  background:
    radial-gradient(ellipse 600px 400px at 20% 30%,rgba(0,212,170,.10),transparent 60%),
    radial-gradient(ellipse 700px 500px at 80% 80%,rgba(41,98,255,.08),transparent 60%),
    #0b0e1a !important;
}
/* Grid pattern overlay */
.stApp::before{
  content:"";position:fixed;inset:0;pointer-events:none;z-index:0;
  background-image:
    linear-gradient(rgba(0,212,170,.03) 1px,transparent 1px),
    linear-gradient(90deg,rgba(0,212,170,.03) 1px,transparent 1px);
  background-size:60px 60px;
}
/* Center the form */
.block-container{
  display:flex!important;align-items:center!important;
  justify-content:center!important;min-height:100vh!important;
  padding:24px!important;max-width:100%!important;
  position:relative;z-index:1;
}
/* Auth card wrapper */
.auth-card-st{
  width:100%;max-width:440px;
  background:var(--bg-panel);border:1px solid var(--border);
  border-radius:14px;padding:32px;
  box-shadow:0 24px 80px rgba(0,0,0,.6);
  margin:0 auto;
}
.auth-brand-st{
  display:flex;align-items:center;justify-content:center;gap:10px;
  font-weight:700;font-size:18px;letter-spacing:.08em;color:var(--text);
  margin-bottom:6px;
}
.auth-sub-st{
  text-align:center;color:var(--text-3);font-size:10px;
  letter-spacing:.08em;text-transform:uppercase;margin-bottom:24px;font-weight:600;
}
.auth-divider{
  position:relative;text-align:center;margin:18px 0 14px;
  height:1px;background:var(--border);
}
.auth-divider span{
  position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);
  background:var(--bg-panel);padding:0 12px;
  color:var(--text-3);font-size:10px;letter-spacing:.1em;text-transform:uppercase;font-weight:600;
}
.guest-btn{
  width:100%;background:transparent;
  border:1px solid var(--border);border-radius:7px;
  padding:11px;font-size:13px;color:var(--text-2);font-weight:500;
  display:flex;align-items:center;justify-content:center;gap:8px;
  cursor:pointer;transition:all .15s;margin-top:8px;
}
.guest-btn:hover{background:var(--bg-card-hover);border-color:var(--border-strong);color:var(--text);}
.auth-secured{
  display:flex;align-items:center;justify-content:center;gap:6px;
  font-size:9px;color:var(--text-3);margin-top:16px;letter-spacing:.04em;
}
/* Override streamlit inputs for auth */
.auth-card-st .stTextInput>div>div>input{
  background:var(--bg-card)!important;border:1px solid var(--border)!important;
  border-radius:7px!important;padding:10px 12px!important;font-size:13px!important;
  color:var(--text)!important;height:auto!important;
}
.auth-card-st .stTextInput>div>div>input:focus{
  border-color:var(--teal)!important;
  box-shadow:0 0 0 3px rgba(0,212,170,.08)!important;
}
.auth-card-st .stTextInput label{
  color:var(--text-3)!important;font-size:10px!important;
  text-transform:uppercase!important;letter-spacing:.06em!important;font-weight:600!important;
}
.auth-card-st .stButton>button{
  width:100%!important;background:var(--teal)!important;color:#062a23!important;
  font-weight:600!important;font-size:13px!important;border-radius:7px!important;
  padding:11px!important;height:auto!important;border:none!important;
  transition:all .15s!important;
}
.auth-card-st .stButton>button:hover{background:#1eddb8!important;transform:translateY(-1px)!important;}
.auth-card-st .stCheckbox{color:var(--text-2)!important;font-size:11px!important;}
.auth-card-st .stTabs [data-baseweb="tab-list"]{
  background:var(--bg-card)!important;border:1px solid var(--border)!important;
  border-radius:8px!important;padding:3px!important;gap:2px!important;
}
.auth-card-st .stTabs [data-baseweb="tab"]{
  color:var(--text-2)!important;font-size:12px!important;font-weight:600!important;
  border-radius:5px!important;background:transparent!important;
}
.auth-card-st .stTabs [aria-selected="true"]{
  background:var(--bg-panel)!important;color:var(--teal)!important;
  box-shadow:inset 0 0 0 1px var(--border-accent)!important;
}
.auth-card-st .stTabs [data-baseweb="tab-panel"]{background:transparent!important;padding:16px 0 0!important;}
.auth-error-st{
  background:rgba(239,83,80,.08);border:1px solid rgba(239,83,80,.25);
  color:var(--down);border-radius:5px;padding:8px 10px;font-size:11px;margin-top:8px;
}
</style>
"""


def _show_auth():
    st.markdown(DESIGN_CSS + AUTH_CSS, unsafe_allow_html=True)

    # Centered column
    _, col, _ = st.columns([1, 2, 1])
    with col:
        st.markdown("""
        <div class="auth-card-st">
          <div class="auth-brand-st">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none"
                 stroke="#00d4aa" stroke-width="2" stroke-linejoin="round"
                 style="filter:drop-shadow(0 0 8px rgba(0,212,170,.5))">
              <path d="M12 2 L21 7 L21 17 L12 22 L3 17 L3 7 Z"/>
              <path d="M12 2 L12 22 M3 7 L21 17 M21 7 L3 17" stroke-width="1" opacity=".4"/>
            </svg>
            FIN-VQA
          </div>
          <div class="auth-sub-st">BIST Intelligence Terminal</div>
        """, unsafe_allow_html=True)

        tab_login, tab_signup = st.tabs(["Giriş Yap", "Kayıt Ol"])

        with tab_login:
            login_email = st.text_input("E-posta", key="li_email",
                                        placeholder="ornek@finvqa.com")
            login_pass = st.text_input("Şifre", type="password", key="li_pass",
                                       placeholder="••••••••")
            if st.session_state.get("auth_err_login"):
                st.markdown(f'<div class="auth-error-st">{st.session_state.auth_err_login}</div>',
                            unsafe_allow_html=True)
            if st.button("Giriş Yap", key="btn_login"):
                if not login_email or not login_pass:
                    st.session_state.auth_err_login = "E-posta ve şifre gereklidir."
                    st.rerun()
                elif len(login_pass) < 4:
                    st.session_state.auth_err_login = "Şifre çok kısa."
                    st.rerun()
                else:
                    name = login_email.split("@")[0].replace(".", " ").title()
                    _do_login(name, login_email, guest=False)

        with tab_signup:
            reg_name = st.text_input("Ad Soyad", key="reg_name",
                                     placeholder="Mehmet Demir")
            reg_email = st.text_input("E-posta", key="reg_email",
                                      placeholder="ornek@finvqa.com")
            reg_pass = st.text_input("Şifre", type="password", key="reg_pass",
                                     placeholder="••••••••")
            reg_terms = st.checkbox("Kullanım koşullarını kabul ediyorum", key="reg_terms")
            if st.session_state.get("auth_err_signup"):
                st.markdown(f'<div class="auth-error-st">{st.session_state.auth_err_signup}</div>',
                            unsafe_allow_html=True)
            if st.button("Hesap Oluştur", key="btn_signup"):
                if not reg_name:
                    st.session_state.auth_err_signup = "Ad soyad gereklidir."
                    st.rerun()
                elif not reg_email or not reg_pass:
                    st.session_state.auth_err_signup = "E-posta ve şifre gereklidir."
                    st.rerun()
                elif not reg_terms:
                    st.session_state.auth_err_signup = "Kullanım koşullarını kabul etmelisiniz."
                    st.rerun()
                else:
                    _do_login(reg_name, reg_email, guest=False)

        # Continue without account
        st.markdown('<div class="auth-divider"><span>veya</span></div>', unsafe_allow_html=True)
        if st.button("👤  Üye Olmadan Devam Et", key="btn_guest", use_container_width=True):
            _do_login("Misafir", "", guest=True)

        st.markdown("""
          <div class="auth-secured">
            <span style="width:10px;height:10px;background:linear-gradient(135deg,#ffa000,#f57c00);
              clip-path:polygon(0 75%,40% 0,55% 35%,80% 25%,100% 75%,50% 100%);
              display:inline-block;"></span>
            Oturum bilgileri tarayıcıda saklanır · Şifreli
          </div>
        </div>
        """, unsafe_allow_html=True)


def _do_login(name: str, email: str, guest: bool):
    st.session_state.authenticated = True
    st.session_state.guest_mode = guest
    st.session_state.user_name = name
    st.session_state.user_email = email
    st.session_state.pop("auth_err_login", None)
    st.session_state.pop("auth_err_signup", None)
    st.rerun()


def _do_logout():
    for k in ["authenticated", "guest_mode", "user_name", "user_email",
              "chat_messages", "chat_ticker", "last_analysis"]:
        st.session_state.pop(k, None)
    st.rerun()


# ── Logo helpers ──────────────────────────────────────────────────────────────
# Clearbit returns HTTP 200 with a placeholder image → onerror never fires.
# Use Google favicon (real site icon or 404) + SVG-initial as guaranteed fallback.
_BIST_DOMAINS: dict[str, str] = {
    "THYAO": "turkishairlines.com",  "PGSUS": "flypgs.com",
    "TUPRS": "tupras.com.tr",        "GARAN": "garantibbva.com.tr",
    "AKBNK": "akbank.com",           "ISCTR": "isbank.com.tr",
    "YKBNK": "yapikredi.com.tr",     "HALKB": "halkbank.com.tr",
    "VAKBN": "vakifbank.com.tr",     "EREGL": "erdemir.com.tr",
    "KRDMD": "kardemir.com.tr",      "KCHOL": "koc.com.tr",
    "SAHOL": "sabanci.com.tr",       "SISE":  "sisecam.com",
    "ASELS": "aselsan.com.tr",       "BIMAS": "bim.com.tr",
    "MGROS": "migros.com.tr",        "SASA":  "sasapolyester.com",
    "FROTO": "ford.com.tr",          "TOASO": "tofas.com.tr",
    "ARCLK": "arcelik.com.tr",       "TCELL": "turkcell.com.tr",
    "TTKOM": "turktelekom.com.tr",   "PETKM": "petkim.com.tr",
    "KOZAL": "kozaaltin.com.tr",     "ENKAI": "enka.com",
    "EKGYO": "emlakkonut.com.tr",    "BRISA": "brisa.com.tr",
    "AEFES": "anadoluefes.com",      "CCOLA": "cocacolaic.com.tr",
    "ULKER": "ulker.com.tr",         "TAVHL": "tavairports.com",
    "VESTL": "vestel.com.tr",        "ALTNY": "altinbilekci.com.tr",
    "SMRTG": "smartgrup.com.tr",     "AKCNS": "akcansa.com.tr",
    "ODAS":  "odasenerji.com.tr",    "ALARK": "alarko.com.tr",
}


def _make_logo_img(ticker_clean: str, fund_dict: dict, size: int = 22) -> str:
    """Returns an <img> tag: Google favicon primary, SVG initial fallback."""
    dom = _BIST_DOMAINS.get(ticker_clean, "")
    if not dom:
        web = fund_dict.get("website", "")
        if web:
            dom = web.replace("https://", "").replace("http://", "").replace("www.", "").split("/")[0].strip()
    initial = ticker_clean[:2]
    fs = max(7, size // 2)
    svg_fb = (
        f"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' "
        f"width='{size}' height='{size}'%3E"
        f"%3Crect width='{size}' height='{size}' rx='4' fill='%231a1f2e'/%3E"
        f"%3Crect width='{size}' height='{size}' rx='4' fill='none' "
        f"stroke='%2300d4aa' stroke-width='0.8' opacity='.4'/%3E"
        f"%3Ctext x='50%25' y='50%25' dy='.35em' text-anchor='middle' "
        f"fill='%2300d4aa' font-size='{fs}' font-family='monospace' "
        f"font-weight='700'%3E{initial}%3C/text%3E%3C/svg%3E"
    )
    st = (f"border-radius:4px;object-fit:contain;"
          f"background:rgba(255,255,255,.03);flex:0 0 {size}px;")
    if dom:
        gfav = f"https://www.google.com/s2/favicons?domain={dom}&sz=64"
        return (f'<img src="{gfav}" width="{size}" height="{size}" style="{st}" '
                f'onerror="this.onerror=null;this.src=\'{svg_fb}\'">')
    return f'<img src="{svg_fb}" width="{size}" height="{size}" style="{st}">'


# ── Session state init ────────────────────────────────────────────────────────
for _k, _v in [("authenticated", False), ("guest_mode", False),
                ("user_name", ""), ("user_email", ""),
                ("api_key", os.getenv("GOOGLE_API_KEY", ""))]:
    if _k not in st.session_state:
        st.session_state[_k] = _v

# ── Auth gate ─────────────────────────────────────────────────────────────────
if not st.session_state.authenticated:
    _show_auth()
    st.stop()


# ══════════════════════════════════════════════════════════════════════════════
# MAIN TERMINAL CSS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(DESIGN_CSS + """
<style>
/* ── Navbar ── */
.navbar{
  position:sticky;top:0;z-index:100;height:44px;
  display:flex;align-items:center;padding:0 16px;gap:14px;
  background:rgba(11,14,26,.92);backdrop-filter:blur(12px);
  border-bottom:1px solid var(--border);
}
.brand-name{font-weight:700;font-size:13px;letter-spacing:.06em;color:var(--text);}
.brand-tag{font-size:10px;color:var(--text-3);letter-spacing:.04em;
  margin-left:6px;padding-left:8px;border-left:1px solid var(--border);}
.nav-tabs{display:flex;gap:2px;margin-left:18px;}
.nav-tab{padding:6px 12px;font-size:12px;color:var(--text-2);border-radius:6px;
  font-weight:500;transition:background .15s,color .15s;}
.nav-tab.active{color:var(--teal);background:var(--teal-dim);}
.nav-right{margin-left:auto;display:flex;align-items:center;gap:10px;}
.model-pill{display:flex;align-items:center;gap:7px;background:var(--bg-card);
  border:1px solid var(--border);padding:4px 10px 4px 8px;border-radius:6px;font-size:11px;color:var(--text-2);}
.dot-live{width:6px;height:6px;border-radius:50%;background:var(--up);
  box-shadow:0 0 8px var(--up);animation:pulse 2s ease-in-out infinite;display:inline-block;}
.gem{width:14px;height:14px;display:inline-flex;align-items:center;justify-content:center;
  border-radius:3px;background:linear-gradient(135deg,#4285f4,#9b72cb 50%,#d96570);
  font-weight:700;color:#fff;font-size:8px;}
@keyframes pulse{0%,100%{opacity:1;transform:scale(1)}50%{opacity:.5;transform:scale(.85)}}
.profile-btn-nav{display:flex;align-items:center;gap:8px;padding:3px 10px 3px 3px;height:30px;
  background:var(--bg-card);border:1px solid var(--border);border-radius:18px;cursor:pointer;transition:all .15s;}
.profile-btn-nav:hover{background:var(--bg-card-hover);border-color:var(--border-strong);}
.profile-avatar{width:24px;height:24px;border-radius:50%;
  background:linear-gradient(135deg,#00d4aa,#2962ff);
  display:inline-flex;align-items:center;justify-content:center;
  color:#062a23;font-size:10px;font-weight:700;flex:0 0 24px;}
.profile-nm{font-size:11px;font-weight:600;color:var(--text);max-width:90px;
  overflow:hidden;text-overflow:ellipsis;white-space:nowrap;}
.profile-rl{font-size:8px;color:var(--teal);letter-spacing:.06em;text-transform:uppercase;font-weight:700;}

/* ── Streamlit widget overrides ── */
.stSelectbox>div>div{border-radius:6px!important;border-color:var(--border)!important;
  background:var(--bg-card)!important;font-size:11px!important;}
.stSelectbox label{color:var(--text-3)!important;font-size:9px!important;
  text-transform:uppercase!important;letter-spacing:.06em!important;font-weight:600!important;}
.stTextInput>div>div>input{border-radius:6px!important;border-color:var(--border)!important;
  background:var(--bg-card)!important;font-size:11px!important;font-family:var(--mono)!important;}
.stTextInput label{color:var(--text-3)!important;font-size:9px!important;
  text-transform:uppercase!important;letter-spacing:.06em!important;font-weight:600!important;}
.stButton>button{background:var(--teal)!important;color:#062a23!important;font-weight:600!important;
  border:none!important;border-radius:6px!important;font-size:12px!important;}
.stButton>button:hover{background:#1eddb8!important;}

/* ── Symbol toolbar ── */
.symbar{height:40px;display:flex;align-items:center;padding:0 16px;gap:10px;
  background:var(--bg-panel);border-bottom:1px solid var(--border);}
.sym-display{display:flex;align-items:center;gap:8px;background:var(--bg-card);
  border:1px solid var(--border);height:28px;padding:0 10px;border-radius:6px;min-width:260px;}
.sym-tk{font-weight:700;font-size:12px;letter-spacing:.04em;color:var(--text);}
.sym-sep{color:var(--text-3);}
.sym-nm{color:var(--text-2);font-size:11px;white-space:nowrap;overflow:hidden;
  text-overflow:ellipsis;max-width:160px;}
.tb-sep{width:1px;height:20px;background:var(--border);}
.period-btn{padding:3px 9px;font-size:11px;color:var(--text-2);border-radius:4px;
  font-family:var(--mono);font-weight:500;}
.period-btn.active{background:var(--teal-dim);color:var(--teal);}

/* ── Chart ── */
.chart-head{display:flex;align-items:center;gap:14px;padding:10px 14px;
  border-bottom:1px solid var(--border);background:var(--bg-panel);}
.ch-sym{font-size:18px;font-weight:700;letter-spacing:.02em;color:var(--text);}
.ch-price{font-family:var(--mono);font-size:20px;font-weight:600;color:var(--text);}
.ch-delta{font-family:var(--mono);font-size:12px;font-weight:600;padding:3px 8px;border-radius:4px;}
.ch-delta.up{color:var(--up);background:rgba(38,166,154,.12);}
.ch-delta.down{color:var(--down);background:rgba(239,83,80,.12);}
.ch-meta{display:flex;flex-direction:column;gap:2px;font-size:10px;color:var(--text-3);}
.ch-meta b{color:var(--text-2);font-weight:500;}
.chip{display:inline-flex;align-items:center;gap:5px;background:var(--bg-card);
  border:1px solid var(--border);padding:3px 8px;border-radius:4px;
  font-size:10px;color:var(--text-2);font-family:var(--mono);}
.chip .ck{color:var(--text-3);} .chip .cv{color:var(--text);}
.ind-overlay{display:flex;gap:6px;margin:8px 14px 0;}
.ind-badge{background:rgba(19,23,34,.92);backdrop-filter:blur(8px);border:1px solid var(--border);
  padding:4px 8px;border-radius:4px;font-size:10px;font-family:var(--mono);
  display:inline-flex;gap:6px;align-items:center;}
.ind-badge .ib-k{color:var(--text-3);font-weight:600;}
.ind-badge.ma20 .ib-v{color:#f5a524;} .ind-badge.ma50 .ib-v{color:#9c5cff;}
.ind-badge.rsi .ib-v{color:var(--teal);}
.chart-foot{display:flex;gap:18px;align-items:center;padding:8px 14px;
  border-top:1px solid var(--border);font-size:11px;background:var(--bg-panel);}
.chart-foot .grp{display:flex;gap:6px;font-family:var(--mono);}
.chart-foot .grp .k{color:var(--text-3);} .chart-foot .grp .v{color:var(--text);}

/* ── Metrics ── */
.metrics{display:grid;grid-template-columns:repeat(6,1fr);gap:1px;
  background:var(--border);margin-top:1px;}
.metric{background:var(--bg-panel);padding:10px 14px;
  display:flex;flex-direction:column;gap:4px;transition:transform .15s,background .15s;}
.metric:hover{background:var(--bg-card-hover);transform:translateY(-1px);}
.metric .mlbl{font-size:10px;color:var(--text-3);letter-spacing:.05em;text-transform:uppercase;font-weight:600;}
.metric .mval{font-family:var(--mono);font-size:14px;font-weight:600;color:var(--text);}
.metric .msub{font-size:10px;color:var(--text-2);display:flex;gap:6px;align-items:center;}
.metric .mpct{font-family:var(--mono);font-size:10px;font-weight:600;padding:1px 5px;border-radius:3px;}

/* ── Tables ── */
.tables{display:grid;grid-template-columns:1fr 1fr;gap:1px;background:var(--border);margin-top:1px;}
.tblbox{background:var(--bg-panel);display:flex;flex-direction:column;}
.panel-hdr{display:flex;align-items:center;gap:8px;padding:9px 14px;
  border-bottom:1px solid var(--border);font-size:11px;color:var(--text-2);
  letter-spacing:.06em;text-transform:uppercase;font-weight:600;}
.panel-hdr .ph-title{color:var(--text);} .panel-hdr .ph-sub{color:var(--text-3);text-transform:none;letter-spacing:0;font-weight:400;}
.panel-hdr .ph-sp{flex:1;}
.tbl{width:100%;border-collapse:collapse;font-size:12px;}
.tbl th{font-size:9px;letter-spacing:.06em;text-transform:uppercase;font-weight:600;
  color:var(--text-3);text-align:left;padding:7px 12px;
  border-bottom:1px solid var(--border);background:var(--bg-panel);}
.tbl td{padding:6px 12px;border-bottom:1px solid rgba(42,46,63,.5);
  font-family:var(--mono);font-size:12px;height:30px;}
.tbl tr:hover td{background:rgba(255,255,255,.03);}
.tbl tr:last-child td{border-bottom:0;}
.tbl .trk{color:var(--text-3);width:24px;font-size:10px;}
.tbl .ttk{color:var(--text);font-weight:600;font-family:'Inter',sans-serif;}
.sig{display:inline-flex;align-items:center;gap:4px;font-size:10px;font-weight:600;
  padding:2px 6px;border-radius:3px;font-family:'Inter',sans-serif;}
.sig.buy{background:rgba(38,166,154,.14);color:var(--up);}
.sig.hold{background:rgba(245,165,36,.14);color:var(--warn);}
.sig.sell{background:rgba(239,83,80,.14);color:var(--down);}
.bar-mini{display:inline-block;width:40px;height:4px;background:rgba(255,255,255,.06);
  border-radius:2px;overflow:hidden;vertical-align:middle;margin-right:6px;}
.bar-mini>i{display:block;height:100%;background:var(--teal);}
.up{color:var(--up);} .down{color:var(--down);}

/* ── AI right panel ── */
.ai-panel-hdr{display:flex;align-items:center;gap:10px;padding:12px 14px;
  border-bottom:1px solid var(--border);}
.ap-ttl{font-size:13px;font-weight:700;letter-spacing:.01em;color:var(--text);}
.gem-badge{display:inline-flex;align-items:center;gap:5px;
  background:linear-gradient(135deg,rgba(66,133,244,.14),rgba(217,101,112,.14));
  border:1px solid rgba(155,114,203,.3);padding:2px 7px;border-radius:10px;
  font-size:10px;color:#c8b4e6;font-weight:600;}
.gem-badge::before{content:"";width:8px;height:8px;border-radius:50%;
  background:conic-gradient(from 90deg,#4285f4,#9b72cb,#d96570,#4285f4);}
.ap-time{margin-left:auto;font-size:10px;color:var(--text-3);font-family:var(--mono);}
.sentiment{margin:14px;padding:18px;border-radius:8px;
  background:radial-gradient(ellipse at top,rgba(38,166,154,.18),rgba(38,166,154,.03) 60%),var(--bg-card);
  border:1px solid rgba(38,166,154,.25);text-align:center;overflow:hidden;}
.sentiment.bear{background:radial-gradient(ellipse at top,rgba(239,83,80,.18),rgba(239,83,80,.03) 60%),var(--bg-card);
  border-color:rgba(239,83,80,.25);}
.sentiment.neutral{background:radial-gradient(ellipse at top,rgba(245,165,36,.14),rgba(245,165,36,.02) 60%),var(--bg-card);
  border-color:rgba(245,165,36,.2);}
.sent-lbl{font-size:10px;letter-spacing:.1em;text-transform:uppercase;color:var(--text-3);font-weight:600;}
.sent-verdict{font-size:22px;font-weight:700;letter-spacing:.04em;color:var(--up);
  margin:8px 0 6px;display:flex;align-items:center;justify-content:center;gap:10px;}
.sent-verdict.bear{color:var(--down);} .sent-verdict.neutral{color:var(--warn);}
.sent-dot{width:10px;height:10px;border-radius:50%;background:var(--up);box-shadow:0 0 14px var(--up);}
.sent-dot.bear{background:var(--down);box-shadow:0 0 14px var(--down);}
.sent-dot.neutral{background:var(--warn);box-shadow:0 0 14px var(--warn);}
.sent-conf{font-size:11px;color:var(--text-2);font-family:var(--mono);}
.sent-conf b{color:var(--text);font-weight:600;}
.signals{padding:0 14px 14px;display:flex;flex-direction:column;gap:10px;}
.sig-row{display:flex;flex-direction:column;gap:5px;}
.sig-top{display:flex;justify-content:space-between;align-items:baseline;font-size:11px;}
.sig-top .sn{color:var(--text-2);font-weight:500;} .sig-top .sn b{color:var(--text);font-weight:600;font-family:var(--mono);margin-left:6px;}
.sig-top .sd{color:var(--text-3);font-size:10px;}
.sig-track{height:6px;background:rgba(255,255,255,.04);border-radius:3px;overflow:hidden;}
.sig-fill{height:100%;border-radius:3px;background:linear-gradient(90deg,var(--teal),#1eddb8);}

/* ── Analysis box ── */
.analysis-box{margin:0 14px 14px;background:var(--bg-soft);border:1px solid var(--border);
  border-radius:6px;padding:12px 14px;font-family:var(--mono);font-size:11px;
  line-height:1.65;color:#9ad8c9;max-height:260px;overflow-y:auto;}
.analysis-box::-webkit-scrollbar{width:4px;}
.analysis-box::-webkit-scrollbar-thumb{background:var(--border);border-radius:2px;}
.analysis-box .an-h{font-size:11px;margin:12px 0 4px;color:var(--teal);
  font-family:'Inter',sans-serif;font-weight:600;letter-spacing:.04em;}
.analysis-box .an-h:first-child{margin-top:0;}
.analysis-box .an-p{margin:0 0 4px;color:#9ad8c9;}

/* ── Peers ── */
.peers{padding:12px 14px;display:flex;gap:8px;overflow-x:auto;}
.peer{flex:0 0 auto;min-width:100px;background:var(--bg-card);border:1px solid var(--border);
  border-radius:6px;padding:10px 12px;cursor:pointer;transition:all .15s;}
.peer:hover{border-color:var(--border-strong);transform:translateY(-1px);}
.peer.active{border-color:var(--teal);box-shadow:0 0 0 1px rgba(0,212,170,.2);}
.peer .ptk{font-weight:700;font-size:12px;letter-spacing:.03em;color:var(--text);}
.peer .ppr{font-family:var(--mono);font-size:12px;color:var(--text);margin-top:4px;}
.peer .pdl{font-family:var(--mono);font-size:10px;font-weight:600;margin-top:2px;}

/* ── Chat panel ── */
.chat-hdr{display:flex;align-items:center;gap:8px;padding:12px 14px;
  border-top:1px solid var(--border);border-bottom:1px solid var(--border);
  background:var(--bg-panel);}
.chat-hdr-ttl{font-size:13px;font-weight:700;color:var(--text);}
.chat-hdr-sub{font-size:10px;color:var(--text-3);margin-left:auto;}

/* Streamlit chat message overrides */
[data-testid="stChatMessage"]{
  background:var(--bg-card)!important;border:1px solid var(--border)!important;
  border-radius:8px!important;padding:8px 12px!important;margin-bottom:6px!important;
}
[data-testid="stChatMessage"][data-testid*="user"]{
  background:var(--teal-dim)!important;border-color:var(--border-accent)!important;
}
[data-testid="stChatMessage"] p{
  color:var(--text-2)!important;font-size:12px!important;line-height:1.55!important;margin:0!important;
}
[data-testid="stChatMessage"] .stMarkdown{background:transparent!important;}
[data-testid="stChatInput"]{
  border:1px solid var(--border)!important;border-radius:6px!important;
  background:var(--bg-card)!important;margin:0 14px 14px!important;
}
[data-testid="stChatInput"] textarea{
  background:transparent!important;color:var(--text)!important;font-size:12px!important;
}

/* Suggestion chips */
.sug-chips{display:flex;flex-wrap:wrap;gap:6px;padding:8px 14px 0;}
.sug-chip{font-size:10px;color:var(--text-2);background:var(--bg-card);
  border:1px solid var(--border);border-radius:4px;padding:4px 8px;
  cursor:pointer;transition:all .15s;white-space:nowrap;}
.sug-chip:hover{border-color:var(--teal);color:var(--teal);}

/* ── Bento ── */
.bento{display:grid;grid-template-columns:repeat(3,1fr);gap:1px;background:var(--border);margin-top:1px;}
.bento-card{background:var(--bg-panel);padding:14px 16px;display:flex;flex-direction:column;gap:10px;position:relative;overflow:hidden;}
.bento-ttl{display:flex;align-items:center;gap:8px;font-size:10px;color:var(--text-3);letter-spacing:.08em;text-transform:uppercase;font-weight:600;}
.bento-ttl .bic{width:18px;height:18px;border-radius:4px;display:inline-flex;align-items:center;justify-content:center;background:var(--teal-dim);color:var(--teal);font-size:10px;}
.b-rows{display:flex;flex-direction:column;gap:8px;}
.b-row{display:flex;align-items:center;gap:10px;justify-content:space-between;}
.b-row .bl{display:flex;flex-direction:column;gap:2px;min-width:0;}
.b-row .bnm{font-size:12px;font-weight:600;color:var(--text);}
.b-row .bsub{font-size:10px;color:var(--text-3);font-family:var(--mono);}
.b-row .bmid{flex:1;height:22px;min-width:80px;}
.b-row .br{text-align:right;display:flex;flex-direction:column;gap:2px;}
.b-row .bpr{font-family:var(--mono);font-size:12px;font-weight:600;color:var(--text);}
.b-row .bdl{font-family:var(--mono);font-size:10px;font-weight:600;}

/* ── Sector ── */
.sector-hdr{display:flex;align-items:center;padding:9px 14px;
  border-bottom:1px solid var(--border);border-top:1px solid var(--border);background:var(--bg-panel);}
.sec-strip{display:flex;gap:8px;padding:12px;overflow-x:auto;background:var(--bg-panel);}
.sec-card{flex:0 0 auto;width:170px;background:var(--bg-card);border:1px solid var(--border);
  border-radius:6px;padding:10px 12px;cursor:pointer;display:flex;flex-direction:column;gap:6px;transition:all .15s;}
.sec-card:hover{border-color:var(--border-strong);background:var(--bg-card-hover);}
.sec-card .sc-h{display:flex;justify-content:space-between;align-items:baseline;}
.sec-card .sc-tk{font-weight:700;font-size:12px;letter-spacing:.03em;color:var(--text);}
.sec-card .sc-pr{font-family:var(--mono);font-size:12px;color:var(--text);}
.sec-card .sc-bar{height:4px;border-radius:2px;background:rgba(255,255,255,.04);overflow:hidden;}
.sec-card .sc-bar i{display:block;height:100%;}
.sec-card .sc-ft{display:flex;justify-content:space-between;font-size:10px;font-family:var(--mono);}
.sec-card .sc-dl{font-weight:600;} .sec-card .sc-vl{color:var(--text-3);}

/* Streamlit tab overrides */
.stTabs [data-baseweb="tab-list"]{gap:2px;background:var(--bg-panel)!important;
  padding:8px 12px 0;border-bottom:1px solid var(--border);}
.stTabs [data-baseweb="tab"]{background:transparent!important;color:var(--text-2)!important;
  border-radius:4px 4px 0 0!important;font-size:11px!important;padding:5px 12px!important;font-weight:500!important;}
.stTabs [aria-selected="true"]{color:var(--teal)!important;background:var(--teal-dim)!important;
  box-shadow:inset 0 -2px 0 var(--teal)!important;}
.stTabs [data-baseweb="tab-panel"]{padding:0!important;background:var(--bg-panel)!important;}

/* ── Expander ── */
.streamlit-expanderHeader{background:var(--bg-panel)!important;border:1px solid var(--border)!important;border-radius:0!important;font-size:11px!important;color:var(--text-2)!important;}
[data-testid="stExpander"]{background:var(--bg-panel)!important;border:none!important;}

/* ── Footer ── */
.ftbar{height:32px;display:flex;align-items:center;gap:14px;padding:0 16px;
  border-top:1px solid var(--border);font-size:10px;color:var(--text-3);background:var(--bg-panel);}
.ft-pwr{display:inline-flex;align-items:center;gap:5px;color:var(--teal);}
.ft-pwr::before{content:"";width:5px;height:5px;border-radius:50%;background:var(--teal);box-shadow:0 0 6px var(--teal);}

/* Plotly */
[data-testid="stPlotlyChart"]{background:var(--bg-soft)!important;border:none!important;}

/* scrollbar */
::-webkit-scrollbar{height:4px;width:4px;}
::-webkit-scrollbar-thumb{background:var(--border-strong);border-radius:2px;}
::-webkit-scrollbar-track{background:transparent;}

/* ── st.pills (period selector) ── */
[data-testid="stPills"]{padding:0!important;margin:0!important;}
[data-testid="stPills"] > label{display:none!important;}
[data-testid="stPills"] > div{display:flex!important;flex-wrap:nowrap!important;gap:1px!important;
  background:var(--bg-card)!important;border:1px solid var(--border)!important;
  border-radius:6px!important;padding:2px!important;align-items:center!important;}
[data-testid="stPills"] button{
  background:transparent!important;border:none!important;
  color:var(--text-2)!important;font-family:var(--mono)!important;
  font-size:11px!important;font-weight:500!important;
  padding:2px 9px!important;border-radius:4px!important;
  min-height:unset!important;height:26px!important;transition:all .12s!important;
}
[data-testid="stPills"] button:hover{background:rgba(255,255,255,.04)!important;color:var(--text)!important;}
[data-testid="stPills"] button[aria-pressed="true"]{
  background:var(--teal-dim)!important;color:var(--teal)!important;font-weight:600!important;
}
/* ── control bar selectbox (no label) ── */
.ctrl-bar .stSelectbox > label{display:none!important;}
/* ── popover body ── */
[data-testid="stPopoverBody"]{
  background:var(--bg-panel)!important;border:1px solid var(--border)!important;border-radius:8px!important;
}
/* ── chat fixed-height container scrollbar ── */
[data-testid="stVerticalBlockBorderWrapper"]{background:transparent!important;border:none!important;}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# NAVBAR
# ══════════════════════════════════════════════════════════════════════════════
user_name = st.session_state.user_name
is_guest = st.session_state.guest_mode
initials = "".join(w[0].upper() for w in user_name.split()[:2]) if user_name else "?"
role_lbl = "MİSAFİR" if is_guest else "ÜYE"

nav_col, logout_col = st.columns([10, 1])
with nav_col:
    st.markdown(f"""
    <div class="navbar">
      <div style="display:flex;align-items:center;gap:8px;">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none"
             stroke="#00d4aa" stroke-width="2" stroke-linejoin="round"
             style="filter:drop-shadow(0 0 6px rgba(0,212,170,.5))">
          <path d="M12 2 L21 7 L21 17 L12 22 L3 17 L3 7 Z"/>
          <path d="M12 2 L12 22 M3 7 L21 17 M21 7 L3 17" stroke-width="1" opacity=".4"/>
        </svg>
        <span class="brand-name">FIN-VQA</span>
        <span class="brand-tag">BIST Intelligence Terminal</span>
      </div>
      <nav class="nav-tabs">
        <div class="nav-tab active">Analiz</div>
        <div class="nav-tab">Makro Pulse</div>
        <div class="nav-tab">Sektör Radar</div>
        <div class="nav-tab">Geçmiş</div>
      </nav>
      <div class="nav-right">
        <div class="model-pill">
          <span class="gem">G</span>Gemini 2.5
          <span class="dot-live"></span>
        </div>
        <div class="profile-btn-nav">
          <span class="profile-avatar">{initials}</span>
          <span style="display:flex;flex-direction:column;align-items:flex-start;line-height:1.15;gap:1px;">
            <span class="profile-nm">{_html.escape(user_name)}</span>
            <span class="profile-rl">{role_lbl}</span>
          </span>
          <span style="color:var(--text-3);font-size:9px;margin-left:2px;">▾</span>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)
with logout_col:
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    if st.button("Çıkış", key="logout_btn"):
        _do_logout()

# ══════════════════════════════════════════════════════════════════════════════
# CONTROL BAR  (ticker · period pills · model · settings · analyze)
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="ctrl-bar">', unsafe_allow_html=True)
cb1, cb2, cb3, cb4, cb5 = st.columns([3.5, 3.5, 1.8, 0.5, 1.6], gap="small")
with cb1:
    t_opts = {f"{v} · {k.replace('.IS','')}": k
              for k, v in sorted(BIST100_TICKERS.items(), key=lambda x: x[1])}
    def_key = "Türk Hava Yolları · THYAO"
    def_idx = list(t_opts.keys()).index(def_key) if def_key in t_opts else 0
    sel_display = st.selectbox("HİSSE", list(t_opts.keys()), index=def_idx,
                                label_visibility="collapsed")
    sel_ticker = t_opts[sel_display]
with cb2:
    p_keys = list(PERIOD_OPTIONS.keys())
    sel_period = st.pills("DÖNEM", p_keys, default=p_keys[3],
                           key="period_pills", label_visibility="collapsed")
    if sel_period is None:
        sel_period = p_keys[3]
with cb3:
    sel_model = st.selectbox("MODEL", list(GEMINI_MODELS.keys()), index=1,
                              label_visibility="collapsed")
with cb4:
    with st.popover("⚙", use_container_width=True):
        st.markdown("<div style='font-size:11px;font-weight:600;color:var(--text-2);margin-bottom:8px'>API Ayarları</div>",
                    unsafe_allow_html=True)
        entered_key = st.text_input("Gemini API Key", type="password",
                                    value=st.session_state.api_key, key="api_key_pop")
        if st.button("Kaydet", key="save_api_key"):
            st.session_state.api_key = entered_key
            st.rerun()
        if st.session_state.api_key:
            st.markdown('<div style="color:#26a69a;font-size:10px;margin-top:4px">🟢 API bağlı</div>',
                        unsafe_allow_html=True)
        else:
            st.markdown('<div style="color:#ef5350;font-size:10px;margin-top:4px">🔴 API anahtarı girilmedi</div>',
                        unsafe_allow_html=True)
with cb5:
    analyze_btn = st.button("⚡ Analiz Başlat", use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)
api_key = st.session_state.api_key

# ══════════════════════════════════════════════════════════════════════════════
# DATA
# ══════════════════════════════════════════════════════════════════════════════
with st.spinner(""):
    stock_data = fetch_stock_data(sel_ticker, PERIOD_OPTIONS[sel_period])
    fund = fetch_fundamentals(sel_ticker)
    news = fetch_news(sel_ticker)

if stock_data is None or stock_data.empty:
    st.error(f"{sel_ticker} için veri alınamadı.")
    st.stop()

df = add_all_indicators(stock_data)
ind = get_indicator_summary(df)
clean        = sel_ticker.replace(".IS", "")
sector       = get_sector_for_ticker(sel_ticker)
price        = fund.get("currentPrice") or float(df["Close"].iloc[-1])
period_start = float(df["Close"].iloc[0])          # first candle of selected period
delta        = price - period_start
pct          = (delta / period_start * 100) if period_start else 0
prev         = fund.get("previousClose") or period_start  # kept for metric displays

logo_img = _make_logo_img(clean, fund, size=22)
pe    = fund.get("trailingPE")
pb    = fund.get("priceToBook")
mcap  = fund.get("marketCap", 0)
mcap_s = (f"{mcap/1e9:.1f}B" if mcap >= 1e9
          else (f"{mcap/1e6:.0f}M" if mcap >= 1e6 else "—"))
rsi       = ind.get("rsi", 50)
ma20      = ind.get("ma20", 0)
ma50      = ind.get("ma50", 0)
ma_signal = ind.get("ma_signal", "Nötr")
up_cls    = "up" if delta >= 0 else "down"
delta_sym = "▲" if delta >= 0 else "▼"
now_str   = datetime.now().strftime("%H:%M:%S · %d.%m.%Y")
w52h = fund.get("fiftyTwoWeekHigh", 0)
w52l = fund.get("fiftyTwoWeekLow", 0)
avg_vol  = fund.get("averageVolume", 0)
vol_today = int(df["Volume"].iloc[-1]) if not df.empty else 0


# ══════════════════════════════════════════════════════════════════════════════
# MAIN LAYOUT
# ══════════════════════════════════════════════════════════════════════════════
col_left, col_right = st.columns([3, 2], gap="small")

# ══ LEFT ═════════════════════════════════════════════════════════════════════
with col_left:

    # Chart header
    st.markdown(f"""
    <div class="chart-head">
      {logo_img}<div class="ch-sym">{clean}</div>
      <div class="ch-price">₺{price:,.2f}</div>
      <div class="ch-delta {up_cls}">{delta_sym} {abs(delta):,.2f} &nbsp;{pct:+.2f}%</div>
      <div class="ch-meta">
        <span><b>{_html.escape(fund.get('shortName',''))}</b></span>
        <span>BIST · TRY · {now_str}</span>
      </div>
      <div style="margin-left:auto;display:flex;gap:6px;">
        <span class="chip"><span class="ck">52H Y:</span><span class="cv">₺{w52h:,.2f}</span></span>
        <span class="chip"><span class="ck">52H D:</span><span class="cv">₺{w52l:,.2f}</span></span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Indicator overlay
    st.markdown(f"""
    <div class="ind-overlay">
      <div class="ind-badge ma20"><span class="ib-k">MA20</span><span class="ib-v">₺{ma20:,.2f}</span></div>
      <div class="ind-badge ma50"><span class="ib-k">MA50</span><span class="ib-v">₺{ma50:,.2f}</span></div>
      <div class="ind-badge rsi"><span class="ib-k">RSI(14)</span><span class="ib-v">{rsi:.1f}</span></div>
      <div class="ind-badge"><span class="ib-k">VOL</span><span class="ib-v">{vol_today/1e6:.1f}M</span></div>
    </div>
    """, unsafe_allow_html=True)

    # Plotly chart
    fig = create_candlestick_chart(df, sel_ticker, show_rsi=False, show_volume=True)
    fig.update_layout(
        height=360, margin=dict(l=0, r=0, t=4, b=0),
        paper_bgcolor="#10141f", plot_bgcolor="#10141f",
        font=dict(family="Inter", color="#566278", size=10),
    )
    fig.update_traces(
        increasing=dict(line=dict(color="#26a69a"), fillcolor="#26a69a"),
        decreasing=dict(line=dict(color="#ef5350"), fillcolor="#ef5350"),
        selector=dict(type="candlestick"),
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    # ── VQA trigger ───────────────────────────────────────────────────────────
    if analyze_btn:
        if not api_key:
            st.warning("⚙ butonundan API anahtarı giriniz.")
        else:
            with st.spinner("Analiz ediliyor…"):
                _model = initialize_model(api_key, GEMINI_MODELS[sel_model])
                if _model:
                    chart_img = chart_to_image(fig)
                    result = analyze_stock(
                        chart_img, sel_ticker,
                        format_fundamentals_text(fund),
                        format_news_text(news), ind, _model,
                    )
                    result["ticker"] = sel_ticker
                    st.session_state["last_analysis"] = result
                    if result["success"]:
                        history_manager.save_analysis(
                            ticker=sel_ticker,
                            sentiment=result["sentiment"],
                            confidence=result["confidence"],
                            price=price,
                            model_used=result["model_used"],
                            summary=result["analysis_text"][:200] + "…",
                            full_analysis=result["analysis_text"],
                        )
                    st.rerun()
                else:
                    st.error("Model başlatılamadı.")

    # Chart footer
    last = df.iloc[-1]
    st.markdown(f"""
    <div class="chart-foot">
      <div class="grp"><span class="k">A:</span><span class="v">₺{float(last['Open']):,.2f}</span></div>
      <div class="grp"><span class="k">Y:</span><span class="v up">₺{float(last['High']):,.2f}</span></div>
      <div class="grp"><span class="k">D:</span><span class="v down">₺{float(last['Low']):,.2f}</span></div>
      <div class="grp"><span class="k">K:</span><span class="v">₺{float(last['Close']):,.2f}</span></div>
      <div class="grp"><span class="k">Hac:</span><span class="v">{vol_today/1e6:.1f}M</span></div>
      <div class="grp"><span class="k">Δ:</span>
        <span class="v {up_cls}">{delta_sym}{abs(delta):,.2f} ({pct:+.2f}%)</span></div>
    </div>
    """, unsafe_allow_html=True)

    # ── AI Analysis (below chart) ─────────────────────────────────────────────
    if "Yükseliş" in ma_signal or "Bullish" in ma_signal:
        _trend_v, _sent_cls, _sent_txt = min(int(rsi + 20), 95), "", "OLUMLU"
    elif "Düşüş" in ma_signal or "Bearish" in ma_signal:
        _trend_v, _sent_cls, _sent_txt = max(int(100 - rsi), 15), "bear", "OLUMSUZ"
    else:
        _trend_v, _sent_cls, _sent_txt = 50, "neutral", "NÖTR"
    _mom_v  = min(max(int(rsi), 10), 95)
    _vol_v  = min(max(100 - int(rsi), 10), 90)
    _dot_cls = "bear" if _sent_cls == "bear" else ("neutral" if _sent_cls == "neutral" else "")
    _vrd_cls = _dot_cls

    _stored = st.session_state.get("last_analysis", {})
    if _stored.get("ticker") == sel_ticker and _stored.get("success"):
        _s = _stored["sentiment"]
        if "OLUMLU" in _s or "Bullish" in _s:
            _sent_cls, _sent_txt, _dot_cls, _vrd_cls = "", "OLUMLU", "", ""
        elif "OLUMSUZ" in _s or "Bearish" in _s:
            _sent_cls, _sent_txt, _dot_cls, _vrd_cls = "bear", "OLUMSUZ", "bear", "bear"
        else:
            _sent_cls, _sent_txt, _dot_cls, _vrd_cls = "neutral", "NÖTR", "neutral", "neutral"
        _conf = _stored["confidence"]
        import re as _re
        _rows = []
        for _ln in _stored["analysis_text"].split("\n"):
            _e = _html.escape(_ln)
            if _e.startswith("## ") or _e.startswith("# "):
                _rows.append(f'<div class="an-h">{_e.lstrip("#").strip()}</div>')
            elif _e.startswith("**") and _e.endswith("**"):
                _rows.append(f'<div class="an-p"><b style="color:var(--text)">{_e[2:-2]}</b></div>')
            elif _e.strip():
                _e = _re.sub(r'\*\*(.+?)\*\*', r'<b style="color:var(--text)">\1</b>', _e)
                _rows.append(f'<div class="an-p">{_e}</div>')
        _analysis_inner = "\n".join(_rows)
    else:
        _conf    = min(max(int(rsi), 40), 85)
        _rsi_d   = "Aşırı alım" if rsi > 70 else ("Aşırı satım" if rsi < 30 else "Nötr bölge")
        _ma_rel  = "MA20 üzerinde" if ma20 > ma50 else "MA20 altında"
        _news_p  = " ".join([_html.escape(n.get("title","")[:80]) for n in news[:2]]) + "…"
        pe_str_t = f"{pe:.1f}" if pe else "—"
        pb_str_t = f"{pb:.1f}" if pb else "—"
        _analysis_inner = f"""
<div class="an-h">▍ TEKNİK ANALİZ</div>
<div class="an-p">{_html.escape(clean)} ₺{price:,.2f} · RSI {rsi:.1f} ({_html.escape(_rsi_d)}) · {_html.escape(_ma_rel)} · <b style="color:var(--text)">{_html.escape(ma_signal)}</b></div>
<div class="an-h">▍ TEMEL</div>
<div class="an-p">F/K {_html.escape(pe_str_t)} · PD/DD {_html.escape(pb_str_t)} · PD ₺{mcap_s} · 52H ₺{w52l:,.2f}–₺{w52h:,.2f}</div>
<div class="an-h">▍ HABERLER</div>
<div class="an-p">{_news_p}</div>
<div class="an-p" style="color:var(--text-3);font-style:italic;margin-top:6px">
  ⚙ API anahtarı ekleyip Analiz Başlat'a tıklayın.
</div>"""

    st.markdown(f"""
    <div style="background:var(--bg-panel);margin-top:1px;">
      <div class="ai-panel-hdr">
        <span class="ap-ttl">Yapay Zeka Analizi</span>
        <span class="gem-badge">Gemini</span>
        <span class="ap-time">{now_str}</span>
      </div>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:1px;background:var(--border);">
        <div style="background:var(--bg-panel);">
          <div class="sentiment {_sent_cls}" style="margin:10px;">
            <div class="sent-lbl">Genel Duyarlılık</div>
            <div class="sent-verdict {_vrd_cls}">
              <span class="sent-dot {_dot_cls}"></span>{_sent_txt}
            </div>
            <div class="sent-conf">Güven <b>{_conf}%</b></div>
          </div>
          <div class="signals" style="padding:0 10px 10px;">
            <div class="sig-row">
              <div class="sig-top"><span class="sn">Trend <b>{_trend_v}%</b></span>
                <span class="sd">{_html.escape(ma_signal)}</span></div>
              <div class="sig-track"><div class="sig-fill" style="width:{_trend_v}%"></div></div>
            </div>
            <div class="sig-row">
              <div class="sig-top"><span class="sn">Momentum <b>{_mom_v}%</b></span>
                <span class="sd">RSI {"aşırı alım" if rsi>70 else ("aşırı satım" if rsi<30 else "nötr")}</span></div>
              <div class="sig-track"><div class="sig-fill" style="width:{_mom_v}%"></div></div>
            </div>
            <div class="sig-row">
              <div class="sig-top"><span class="sn">Volatilite <b>{_vol_v}%</b></span>
                <span class="sd">ATR bazlı</span></div>
              <div class="sig-track">
                <div class="sig-fill" style="width:{_vol_v}%;background:linear-gradient(90deg,#f5a524,#f5b54a)"></div>
              </div>
            </div>
          </div>
        </div>
        <div style="background:var(--bg-panel);">
          <div class="analysis-box" style="max-height:190px;margin:10px;">{_analysis_inner}</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Metrics row
    pe_str = f"{pe:.1f}" if pe else "—"
    pb_str = f"{pb:.1f}" if pb else "—"
    sector_pe = 12.0
    w52_dist_h = ((price - w52h) / w52h * 100) if w52h else 0
    w52_dist_l = ((price - w52l) / w52l * 100) if w52l else 0
    avg_vol_s  = f"{avg_vol/1e6:.1f}M" if avg_vol >= 1e6 else f"{avg_vol:,.0f}"
    vol_vs_avg = vol_today / avg_vol if avg_vol else 1.0
    pe_cls = "up" if pe and pe < sector_pe else "down"
    pe_lbl = "DÜŞÜK" if pe and pe < sector_pe else ("YÜKSEK" if pe else "—")
    pe_bg  = "rgba(38,166,154,.12)" if pe and pe < sector_pe else "rgba(239,83,80,.12)"

    st.markdown(f"""
    <div class="metrics">
      <div class="metric">
        <div class="mlbl">F/K</div><div class="mval">{pe_str}</div>
        <div class="msub">Sektör {sector_pe}
          <span class="mpct {pe_cls}" style="background:{pe_bg}">{pe_lbl}</span></div>
      </div>
      <div class="metric">
        <div class="mlbl">PD/DD</div><div class="mval">{pb_str}</div>
        <div class="msub" style="color:var(--text-3);">Defter değeri çarpanı</div>
      </div>
      <div class="metric">
        <div class="mlbl">52H Yüksek</div><div class="mval">₺{w52h:,.2f}</div>
        <div class="msub down">{w52_dist_h:.1f}% uzak</div>
      </div>
      <div class="metric">
        <div class="mlbl">52H Düşük</div><div class="mval">₺{w52l:,.2f}</div>
        <div class="msub up">+{abs(w52_dist_l):.1f}% üzeri</div>
      </div>
      <div class="metric">
        <div class="mlbl">Ort. Hacim</div><div class="mval">{avg_vol_s}</div>
        <div class="msub">Bugün
          <b class="{'up' if vol_vs_avg>1 else 'down'}">{vol_vs_avg:.1f}×</b></div>
      </div>
      <div class="metric">
        <div class="mlbl">Piyasa Değeri</div><div class="mval">₺{mcap_s}</div>
        <div class="msub" style="color:var(--text-3);">BIST · {_html.escape(sector[:14])}</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Opportunity tables
    ov_tickers = tuple(sorted({
        "THYAO.IS","EREGL.IS","SASA.IS","AKBNK.IS","GARAN.IS",
        "ASELS.IS","TUPRS.IS","KCHOL.IS","BIMAS.IS","SISE.IS",
        "SMRTG.IS","ALTNY.IS","PGSUS.IS","FROTO.IS","ISCTR.IS",
    }))
    with st.spinner(""):
        overview = fetch_bist_overview(ov_tickers)

    vol_leaders  = sorted([r for r in overview if r["avg_volume"]>0],
                          key=lambda x: x["avg_volume"], reverse=True)[:5]
    beta_outliers = sorted([r for r in overview if r["beta"]],
                           key=lambda x: x["beta"], reverse=True)[:5]

    def _sig(chg):
        if chg > 2:  return '<span class="sig buy">● AL</span>'
        if chg < -2: return '<span class="sig sell">● SAT</span>'
        return '<span class="sig hold">● BEKLE</span>'

    vol_rows = "".join(
        f'<tr><td class="trk">{i+1:02d}</td>'
        f'<td class="ttk">{_html.escape(r["ticker"])}</td>'
        f'<td style="text-align:right">₺{r["price"]:,.2f}</td>'
        f'<td class="{("up" if r["change"]>=0 else "down")}" style="text-align:right">'
        f'{r["change"]:+.2f}%</td>'
        f'<td style="text-align:right">'
        f'<span class="bar-mini"><i style="width:{min(100,abs(r["change"])*10+10):.0f}%"></i></span>'
        f'{r["avg_volume"]/1e6:.1f}M</td></tr>'
        for i, r in enumerate(vol_leaders)
    )
    beta_rows = "".join(
        f'<tr><td class="trk">{i+1:02d}</td>'
        f'<td class="ttk">{_html.escape(r["ticker"])}</td>'
        f'<td style="text-align:right">₺{r["price"]:,.2f}</td>'
        f'<td style="text-align:right">{r["beta"]:.2f}</td>'
        f'<td style="text-align:right">{_sig(r["change"])}</td></tr>'
        for i, r in enumerate(beta_outliers)
    )

    st.markdown(f"""
    <div class="tables">
      <div class="tblbox">
        <div class="panel-hdr">
          <span class="ph-title">Hacim Liderleri</span>
          <span class="ph-sub">· Bugün</span><span class="ph-sp"></span>
          <span style="font-size:10px;color:var(--text-3);">Ort. Hacim</span>
        </div>
        <table class="tbl">
          <thead><tr><th>#</th><th>Sembol</th>
            <th style="text-align:right">Fiyat</th>
            <th style="text-align:right">Değişim</th>
            <th style="text-align:right">Ort. Hacim</th></tr></thead>
          <tbody>{vol_rows}</tbody>
        </table>
      </div>
      <div class="tblbox">
        <div class="panel-hdr">
          <span class="ph-title">Volatilite Öncüleri</span>
          <span class="ph-sub">· Beta</span><span class="ph-sp"></span>
          <span style="font-size:10px;color:var(--text-3);">Beta · Sinyal</span>
        </div>
        <table class="tbl">
          <thead><tr><th>#</th><th>Sembol</th>
            <th style="text-align:right">Fiyat</th>
            <th style="text-align:right">Beta</th>
            <th style="text-align:right">Sinyal</th></tr></thead>
          <tbody>{beta_rows}</tbody>
        </table>
      </div>
    </div>
    """, unsafe_allow_html=True)


# ══ RIGHT ════════════════════════════════════════════════════════════════════
with col_right:

    # ── AI Chat ───────────────────────────────────────────────────────────────
    st.markdown(f"""
    <div class="chat-hdr">
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#00d4aa" stroke-width="2">
        <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
      </svg>
      <span class="chat-hdr-ttl">Yapay Zeka ile Sohbet</span>
      <span class="chat-hdr-sub">{_html.escape(clean)} · piyasa soruları</span>
    </div>
    <div class="sug-chips">
      <span class="sug-chip">Emsal karşılaştırma</span>
      <span class="sug-chip">RSI yorumu</span>
      <span class="sug-chip">Risk faktörleri</span>
      <span class="sug-chip">Kademeli alım planı</span>
    </div>
    """, unsafe_allow_html=True)

    if "chat_messages" not in st.session_state:
        st.session_state["chat_messages"] = []
    if st.session_state.get("chat_ticker") != sel_ticker:
        st.session_state["chat_messages"] = []
        st.session_state["chat_ticker"] = sel_ticker

    msgs = st.session_state["chat_messages"]
    # Fixed-height scrollable container for chat history
    chat_box = st.container(height=320, border=False)
    with chat_box:
        if not msgs:
            st.markdown(
                f'<div style="text-align:center;color:var(--text-3);font-size:11px;'
                f'padding:32px 14px;font-style:italic;">'
                f'{_html.escape(clean)} hissesi veya piyasa hakkında soru sor…</div>',
                unsafe_allow_html=True,
            )
        else:
            for m in msgs:
                with st.chat_message(m["role"],
                                      avatar="👤" if m["role"] == "user" else "🤖"):
                    st.markdown(m["content"])

    chat_q = st.chat_input(
        placeholder=f"{clean} hakkında soru sor…",
        key="chat_input_v2",
    )
    if chat_q:
        if not api_key:
            st.warning("Sohbet için ⚙ butonundan API anahtarı giriniz.")
        else:
            st.session_state["chat_messages"].append({"role": "user", "content": chat_q})
            _ck = f"cm_{api_key[:6]}_{sel_model}"
            if _ck not in st.session_state:
                _cm = initialize_model(api_key, GEMINI_MODELS[sel_model])
                if _cm:
                    st.session_state[_ck] = _cm
            _chat_model = st.session_state.get(_ck)
            if _chat_model:
                with st.spinner(""):
                    _ans = chat_with_ai(
                        chat_q,
                        {"ticker": clean, "price": price, "change": pct,
                         "rsi": rsi, "ma_signal": ma_signal, "pe": pe,
                         "company_name": fund.get("shortName", ""),
                         "sector": sector},
                        _chat_model,
                    )
                st.session_state["chat_messages"].append({"role": "assistant", "content": _ans})
            else:
                st.session_state["chat_messages"].append(
                    {"role": "assistant", "content": "Model başlatılamadı. API anahtarını kontrol edin."})
            st.rerun()

    # ── Peer comparison ───────────────────────────────────────────────────────
    peers = get_peers_for_ticker(sel_ticker)
    if peers:
        peer_cards = ""
        for pt in peers[:5]:
            try:
                pf    = fetch_fundamentals(pt)
                pp    = pf.get("currentPrice", 0)
                pprev = pf.get("previousClose", 0)
                pd_   = ((pp - pprev) / pprev * 100) if pprev else 0
                pcls  = "up" if pd_ >= 0 else "down"
                ptk   = pt.replace(".IS", "")
                p_logo_html = _make_logo_img(ptk, pf, size=16) + " "
                peer_cards += f"""
                <div class="peer {'active' if pt==sel_ticker else ''}">
                  <div class="ptk">{p_logo_html}{_html.escape(ptk)}</div>
                  <div class="ppr">₺{pp:,.2f}</div>
                  <div class="pdl {pcls}">{pd_:+.2f}%</div>
                </div>"""
            except Exception:
                pass
        st.markdown(f"""
        <div style="background:var(--bg-panel);margin-top:1px;">
          <div class="panel-hdr">
            <span class="ph-title">Emsal Karşılaştırma</span>
            <span class="ph-sub">· {_html.escape(sector)}</span>
          </div>
          <div class="peers">{peer_cards}</div>
        </div>
        """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# ECONOMIC PULSE
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="bento">
  <div class="bento-card">
    <div class="bento-ttl"><span class="bic">◆</span>Dijital Varlıklar</div>
    <div class="b-rows">
      <div class="b-row">
        <div class="bl"><div class="bnm">Bitcoin</div><div class="bsub">BTC/USD</div></div>
        <svg class="bmid" viewBox="0 0 80 22" preserveAspectRatio="none" style="flex:1;height:22px;min-width:80px;">
          <polyline fill="none" stroke="#26a69a" stroke-width="1.4" points="0,14 12,12 24,15 36,10 48,11 60,7 72,8 80,5"/></svg>
        <div class="br"><div class="bpr">$98,430</div><div class="bdl up">+2.1%</div></div>
      </div>
      <div class="b-row">
        <div class="bl"><div class="bnm">Ethereum</div><div class="bsub">ETH/USD</div></div>
        <svg class="bmid" viewBox="0 0 80 22" preserveAspectRatio="none" style="flex:1;height:22px;min-width:80px;">
          <polyline fill="none" stroke="#26a69a" stroke-width="1.4" points="0,12 12,14 24,11 36,12 48,9 60,10 72,7 80,8"/></svg>
        <div class="br"><div class="bpr">$3,240</div><div class="bdl up">+1.8%</div></div>
      </div>
      <div class="b-row">
        <div class="bl"><div class="bnm">Solana</div><div class="bsub">SOL/USD</div></div>
        <svg class="bmid" viewBox="0 0 80 22" preserveAspectRatio="none" style="flex:1;height:22px;min-width:80px;">
          <polyline fill="none" stroke="#ef5350" stroke-width="1.4" points="0,6 12,8 24,7 36,9 48,11 60,10 72,13 80,14"/></svg>
        <div class="br"><div class="bpr">$214.60</div><div class="bdl down">-0.6%</div></div>
      </div>
    </div>
  </div>
  <div class="bento-card">
    <div class="bento-ttl"><span class="bic">★</span>Emtialar</div>
    <div class="b-rows">
      <div class="b-row">
        <div class="bl"><div class="bnm">Altın</div><div class="bsub">XAU/USD</div></div>
        <svg class="bmid" viewBox="0 0 80 22" preserveAspectRatio="none" style="flex:1;height:22px;min-width:80px;">
          <polyline fill="none" stroke="#26a69a" stroke-width="1.4" points="0,14 12,13 24,14 36,12 48,11 60,12 72,10 80,9"/></svg>
        <div class="br"><div class="bpr">$2,380</div><div class="bdl up">+0.4%</div></div>
      </div>
      <div class="b-row">
        <div class="bl"><div class="bnm">Brent</div><div class="bsub">BCO · varil</div></div>
        <svg class="bmid" viewBox="0 0 80 22" preserveAspectRatio="none" style="flex:1;height:22px;min-width:80px;">
          <polyline fill="none" stroke="#ef5350" stroke-width="1.4" points="0,8 12,9 24,8 36,10 48,11 60,10 72,12 80,13"/></svg>
        <div class="br"><div class="bpr">$84.20</div><div class="bdl down">-0.3%</div></div>
      </div>
      <div class="b-row">
        <div class="bl"><div class="bnm">Gümüş</div><div class="bsub">XAG/USD</div></div>
        <svg class="bmid" viewBox="0 0 80 22" preserveAspectRatio="none" style="flex:1;height:22px;min-width:80px;">
          <polyline fill="none" stroke="#26a69a" stroke-width="1.4" points="0,15 12,13 24,14 36,11 48,12 60,9 72,10 80,7"/></svg>
        <div class="br"><div class="bpr">$29.10</div><div class="bdl up">+0.8%</div></div>
      </div>
    </div>
  </div>
  <div class="bento-card">
    <div class="bento-ttl"><span class="bic">▲</span>Makro Göstergeler</div>
    <div class="b-rows">
      <div class="b-row">
        <div class="bl"><div class="bnm">USD / TRY</div><div class="bsub">Spot</div></div>
        <svg class="bmid" viewBox="0 0 80 22" preserveAspectRatio="none" style="flex:1;height:22px;min-width:80px;">
          <polyline fill="none" stroke="#26a69a" stroke-width="1.4" points="0,16 12,15 24,14 36,15 48,12 60,11 72,10 80,8"/></svg>
        <div class="br"><div class="bpr">32.45</div><div class="bdl up">+0.18%</div></div>
      </div>
      <div class="b-row">
        <div class="bl"><div class="bnm">EUR / TRY</div><div class="bsub">Spot</div></div>
        <svg class="bmid" viewBox="0 0 80 22" preserveAspectRatio="none" style="flex:1;height:22px;min-width:80px;">
          <polyline fill="none" stroke="#26a69a" stroke-width="1.4" points="0,14 12,13 24,12 36,13 48,11 60,10 72,9 80,7"/></svg>
        <div class="br"><div class="bpr">35.10</div><div class="bdl up">+0.22%</div></div>
      </div>
      <div class="b-row">
        <div class="bl"><div class="bnm">BIST 100</div><div class="bsub">Endeks</div></div>
        <svg class="bmid" viewBox="0 0 80 22" preserveAspectRatio="none" style="flex:1;height:22px;min-width:80px;">
          <polyline fill="none" stroke="#26a69a" stroke-width="1.4" points="0,15 12,14 24,12 36,13 48,10 60,11 72,8 80,6"/></svg>
        <div class="br"><div class="bpr">9,842</div><div class="bdl up">+1.2%</div></div>
      </div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# SECTOR PULSE
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="sector-hdr">
  <span style="font-size:11px;font-weight:600;color:var(--text);letter-spacing:.04em;">SEKTÖR NABZI</span>
  <span style="font-size:10px;color:var(--text-3);margin-left:8px;">· canlı · yfinance</span>
</div>
""", unsafe_allow_html=True)

sector_tabs = st.tabs(list(SECTOR_CLUSTERS.keys()))
for s_name, s_tab in zip(SECTOR_CLUSTERS.keys(), sector_tabs):
    with s_tab:
        s_tickers = SECTOR_CLUSTERS[s_name]
        with st.spinner(""):
            s_data = fetch_bist_overview(tuple(s_tickers))
        cards = ""
        for r in s_data:
            up   = r["change"] >= 0
            c    = "var(--up)" if up else "var(--down)"
            bw   = min(100, abs(r["change"]) * 10 + 8)
            cards += f"""
            <div class="sec-card">
              <div class="sc-h">
                <div class="sc-tk">{_html.escape(r['ticker'])}</div>
                <div class="sc-pr">₺{r['price']:,.2f}</div>
              </div>
              <div class="sc-bar"><i style="width:{bw:.0f}%;background:{c}"></i></div>
              <div class="sc-ft">
                <div class="sc-dl" style="color:{c}">{'+' if up else ''}{r['change']:.2f}%</div>
                <div class="sc-vl">{r['avg_volume']/1e6:.1f}M</div>
              </div>
            </div>"""
        st.markdown(f'<div class="sec-strip">{cards}</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# ANALYSIS HISTORY
# ══════════════════════════════════════════════════════════════════════════════
with st.expander("📋 Analiz Geçmişi", expanded=False):
    h1, h2 = st.columns([4, 1])
    with h1:
        hf = st.radio("Filtre", ["Tümü", "Bu Hisse"], horizontal=True,
                      label_visibility="collapsed")
    with h2:
        if st.button("Temizle", key="clr"):
            history_manager.clear_history(); st.rerun()
    ht  = sel_ticker if hf == "Bu Hisse" else None
    hdf = history_manager.get_history(ticker=ht)
    if not hdf.empty:
        ddf = hdf.copy()
        ddf.columns = ["ID","Ticker","Tarih","Duygu","Güven","Fiyat","Model","Özet"]
        st.dataframe(ddf, use_container_width=True, hide_index=True, column_config={
            "ID": st.column_config.NumberColumn(width="small"),
            "Güven": st.column_config.ProgressColumn(min_value=0, max_value=100, format="%d%%"),
            "Fiyat": st.column_config.NumberColumn(format="%.2f ₺"),
        })
    else:
        st.caption("Henüz analiz geçmişi yok.")

# ══════════════════════════════════════════════════════════════════════════════
# FOOTER
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="ftbar">
  <span>© 2026 Fin-VQA · BIST Intelligence Terminal</span>
  <span style="color:var(--text-3);">Veriler sadece bilgi amaçlıdır, yatırım tavsiyesi değildir.</span>
  <span style="flex:1"></span>
  <span class="ft-pwr">Powered by Gemini</span>
  <span style="color:var(--text-3)">|</span>
  <span style="font-family:var(--mono);color:var(--text-3)">v3.1.0</span>
</div>
""", unsafe_allow_html=True)
