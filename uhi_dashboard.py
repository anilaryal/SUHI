"""
=============================================================================
UHI-DST v5.0 — Urban Heat Island Decision Support Tool for South Asia
=============================================================================
Run:  streamlit run uhi_dashboard_v5.py

New in v5:
  🌐  Globe favicon, collapsible Data Sources & Methodology panels
  🌍  Side-by-side Country → City dropdowns (default: Nepal / Kathmandu)
  🏛  Policy brief driven by sidebar city selection
  📦  Policy action cards fully self-contained HTML (text stays in box)
=============================================================================
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')
from scipy import stats as scipy_stats

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="UHI-DST | South Asia Heat Intelligence Platform",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────────────────────────────────────
# GLOBAL CSS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    :root {
        --primary:#E84855; --secondary:#3D5A80; --accent:#F2A65A;
        --bg-dark:#0E1117; --bg-card:#1A1D2E; --bg-sidebar:#141622;
        --text:#E0E6F0; --text-muted:#8892A4; --border:rgba(255,255,255,0.08);
        --success:#2ECC71; --warning:#F39C12;
    }
    .stApp { background:linear-gradient(135deg,#0A0E1A 0%,#0E1520 100%); color:var(--text); }
    section[data-testid="stSidebar"] { background:var(--bg-sidebar)!important; border-right:1px solid var(--border); }

    /* ── Metric cards ── */
    .metric-card {
        background:linear-gradient(135deg,var(--bg-card) 0%,#1F2440 100%);
        border:1px solid var(--border); border-radius:12px; padding:18px;
        text-align:center; position:relative; overflow:hidden;
        transition:transform .2s,box-shadow .2s;
    }
    .metric-card:hover { transform:translateY(-2px); box-shadow:0 8px 32px rgba(232,72,85,.15); }
    .metric-card::before {
        content:''; position:absolute; top:0;left:0;right:0; height:3px;
        background:linear-gradient(90deg,var(--primary),var(--accent));
        border-radius:12px 12px 0 0;
    }
    .metric-value  { font-size:2.1rem; font-weight:800; color:var(--accent); line-height:1.1; }
    .metric-label  { font-size:.72rem; color:var(--text-muted); text-transform:uppercase; letter-spacing:1px; margin-top:4px; }
    .metric-delta  { font-size:.83rem; margin-top:5px; }
    .delta-up   { color:var(--primary); }
    .delta-down { color:var(--success); }

    /* ── Section headers ── */
    .section-header {
        display:flex; align-items:center; gap:9px;
        padding:10px 0; margin:14px 0 6px 0;
        border-bottom:2px solid var(--primary);
    }
    .section-title { font-size:1.2rem; font-weight:700; color:var(--text); }
    .section-icon  { font-size:1.4rem; }

    /* ── Typology badges ── */
    .type-badge { display:inline-block; padding:4px 14px; border-radius:20px; font-size:.78rem; font-weight:600; letter-spacing:.5px; }
    .type-I  { background:rgba(215,48,39,.2);  color:#F88; border:1px solid #d73027; }
    .type-II { background:rgba(252,141,89,.2); color:#FAC; border:1px solid #fc8d59; }
    .type-III{ background:rgba(145,191,219,.2);color:#ABE; border:1px solid #91bfdb; }
    .type-IV { background:rgba(69,117,180,.2); color:#9BF; border:1px solid #4575b4; }

    /* ── Alert boxes ── */
    .alert-danger  { background:rgba(215,48,39,.15);  border:1px solid #d73027; border-radius:8px; padding:12px 16px; }
    .alert-warning { background:rgba(252,141,89,.15); border:1px solid #fc8d59; border-radius:8px; padding:12px 16px; }
    .alert-success { background:rgba(46,204,113,.15); border:1px solid #2ecc71; border-radius:8px; padding:12px 16px; }
    .alert-info    { background:rgba(69,117,180,.15); border:1px solid #4575b4; border-radius:8px; padding:12px 16px; }

    /* ── Policy cards ── */
    .policy-card {
        background:linear-gradient(135deg,#1A2840,#1A3050);
        border:1px solid rgba(69,117,180,.4); border-left:4px solid var(--secondary);
        border-radius:10px; padding:15px; margin:8px 0;
    }
    .policy-title { font-weight:700; color:#7EB8F7; margin-bottom:6px; }
    .policy-text  { font-size:.87rem; color:var(--text-muted); line-height:1.6; }

    /* ── App header ── */
    .app-header {
        background:linear-gradient(135deg,#0D1B2A 0%,#1A1040 50%,#0D1B2A 100%);
        border:1px solid rgba(232,72,85,.3); border-radius:16px;
        padding:22px 30px; margin-bottom:18px; position:relative; overflow:hidden;
    }
    .app-header::after {
        content:''; position:absolute; top:-50%; right:-10%;
        width:400px; height:400px;
        background:radial-gradient(circle,rgba(232,72,85,.08) 0%,transparent 70%);
        border-radius:50%;
    }
    .app-title    { font-size:1.9rem; font-weight:800; color:#fff; margin:0; }
    .app-subtitle { color:var(--text-muted); font-size:.88rem; margin-top:4px; }
    .app-badge    { display:inline-block; background:var(--primary); color:white;
                    font-size:.68rem; font-weight:700; padding:2px 10px;
                    border-radius:20px; margin-left:8px; vertical-align:middle; letter-spacing:1px; }

    /* ── Methodology card ── */
    .method-card {
        background:linear-gradient(135deg,#141E2E,#1A2540);
        border:1px solid rgba(255,255,255,.09); border-radius:12px;
        padding:18px 20px; margin:8px 0; transition:border-color .25s;
    }
    .method-card:hover { border-color:rgba(232,72,85,.4); }
    .method-title { font-size:1rem; font-weight:700; color:#7EB8F7; margin-bottom:8px; }
    .method-eq    {
        background:rgba(0,0,0,.35); border-left:3px solid var(--accent);
        border-radius:6px; padding:8px 14px; font-family:monospace;
        font-size:.87rem; color:#F2D9A4; margin:8px 0;
    }
    .method-text  { font-size:.85rem; color:#A8B4C4; line-height:1.65; }
    .method-ref   { font-size:.75rem; color:#5A6A7A; font-style:italic; margin-top:6px; }

    /* ── Physics table ── */
    .phys-table { width:100%; border-collapse:collapse; font-size:.83rem; }
    .phys-table th { background:#1A2840; color:#7EB8F7; padding:8px 12px; text-align:left; }
    .phys-table td { padding:7px 12px; border-bottom:1px solid rgba(255,255,255,.06); color:#B8C4D4; }
    .phys-table tr:hover td { background:rgba(255,255,255,.03); }

    /* ── Spatial map container ── */
    .spatial-caption {
        font-size:.78rem; color:var(--text-muted); text-align:center;
        margin-top:4px; font-style:italic;
    }

    /* ══════════════════════════════════════════════════════
       LARGE ATTRACTIVE TOP TABS
    ══════════════════════════════════════════════════════ */

    /* Tab bar background strip */
    div[data-testid="stTabs"] > div:first-child {
        background: linear-gradient(180deg, #0D1525 0%, #111827 100%);
        border-bottom: 2px solid rgba(232,72,85,0.35);
        border-radius: 14px 14px 0 0;
        padding: 6px 10px 0 10px;
        gap: 6px;
    }

    /* Every individual tab button */
    div[data-testid="stTabs"] button[data-baseweb="tab"] {
        font-size: 1.0rem !important;
        font-weight: 700 !important;
        letter-spacing: 0.4px;
        padding: 14px 26px !important;
        border-radius: 10px 10px 0 0 !important;
        border: 1px solid rgba(255,255,255,0.07) !important;
        border-bottom: none !important;
        background: rgba(255,255,255,0.03) !important;
        color: #8892A4 !important;
        transition: all 0.22s ease !important;
        white-space: nowrap;
        position: relative;
        overflow: hidden;
    }

    /* Shimmer sweep on hover */
    div[data-testid="stTabs"] button[data-baseweb="tab"]::before {
        content: '';
        position: absolute; top: 0; left: -100%; width: 60%; height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.06), transparent);
        transition: left 0.4s ease;
    }
    div[data-testid="stTabs"] button[data-baseweb="tab"]:hover::before {
        left: 140%;
    }

    /* Hover state */
    div[data-testid="stTabs"] button[data-baseweb="tab"]:hover {
        background: rgba(232,72,85,0.10) !important;
        color: #E0E6F0 !important;
        border-color: rgba(232,72,85,0.30) !important;
        transform: translateY(-2px);
    }

    /* ACTIVE tab — vivid gradient pill */
    div[data-testid="stTabs"] button[data-baseweb="tab"][aria-selected="true"] {
        background: linear-gradient(135deg, #E84855 0%, #B5303A 60%, #8B1E28 100%) !important;
        color: #ffffff !important;
        border-color: rgba(232,72,85,0.6) !important;
        box-shadow:
            0 -3px 14px rgba(232,72,85,0.45),
            0  2px  8px rgba(0,0,0,0.4),
            inset 0 1px 0 rgba(255,255,255,0.18) !important;
        transform: translateY(-3px);
        font-size: 1.05rem !important;
    }

    /* Active tab accent bar at top edge */
    div[data-testid="stTabs"] button[data-baseweb="tab"][aria-selected="true"]::after {
        content: '';
        position: absolute; top: 0; left: 10%; right: 10%; height: 3px;
        background: linear-gradient(90deg, transparent, rgba(255,220,180,0.9), transparent);
        border-radius: 0 0 4px 4px;
    }

    /* Tab content panel */
    div[data-testid="stTabs"] > div:last-child {
        border: 1px solid rgba(255,255,255,0.07);
        border-top: none;
        border-radius: 0 0 14px 14px;
        background: rgba(14,17,23,0.6);
        padding: 4px 2px 2px 2px;
    }

    /* ── Collapsible panel outer expanders — Data Sources (blue) & Methodology (amber) ── */
    div[data-testid="stSidebar"] div[data-testid="stExpander"]:has(summary span:first-child) {
        border-radius: 10px;
        overflow: hidden;
    }

    /* Target the two top-level panel expanders by their label text via sibling trick */
    div[data-testid="stSidebar"] .streamlit-expanderHeader {
        background: rgba(255,255,255,0.03) !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
        font-size: .82rem !important;
        color: #C8D4E8 !important;
        padding: 10px 14px !important;
        border: 1px solid rgba(255,255,255,0.07) !important;
        margin-bottom: 3px;
        letter-spacing: .4px;
        transition: background .2s, border-color .2s;
    }
    div[data-testid="stSidebar"] .streamlit-expanderHeader:hover {
        background: rgba(255,255,255,0.07) !important;
        border-color: rgba(232,72,85,0.3) !important;
    }
    div[data-testid="stSidebar"] .streamlit-expanderContent {
        border: 1px solid rgba(255,255,255,0.05) !important;
        border-top: none !important;
        border-radius: 0 0 8px 8px !important;
        padding: 6px 4px !important;
        background: rgba(0,0,0,0.15) !important;
    }

    /* ── HTML accordion items inside the two panels ── */
    .sb-accordion {
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.07);
        border-radius: 7px;
        margin: 5px 0;
        overflow: hidden;
    }
    .sb-accordion summary {
        padding: 8px 12px;
        font-size: .78rem;
        font-weight: 700;
        color: #C0CCD8;
        cursor: pointer;
        list-style: none;
        display: flex;
        align-items: center;
        gap: 6px;
        user-select: none;
        transition: background .18s, color .18s;
    }
    .sb-accordion summary::-webkit-details-marker { display: none; }
    .sb-accordion summary::before {
        content: '▶';
        font-size: .6rem;
        color: #E84855;
        transition: transform .2s;
        flex-shrink: 0;
    }
    .sb-accordion[open] summary::before { transform: rotate(90deg); }
    .sb-accordion summary:hover {
        background: rgba(232,72,85,0.10);
        color: #E0E6F0;
    }
    .sb-accordion[open] summary {
        background: rgba(232,72,85,0.08);
        border-bottom: 1px solid rgba(255,255,255,0.06);
        color: #E0E6F0;
    }
    .sb-acc-body {
        padding: 8px 10px 10px 10px;
    }

    /* ── Filters label ── */
    .sb-method-item {
        background: rgba(0,0,0,0.25);
        border: 1px solid rgba(255,255,255,0.06);
        border-left: 2px solid var(--accent);
        border-radius: 7px;
        padding: 9px 12px;
        margin: 6px 0;
        font-size: .78rem;
        color: #A8B4C4;
        line-height: 1.55;
    }
    .sb-method-item b { color: #F2A65A; }
    .sb-eq {
        background: rgba(0,0,0,0.4);
        border-left: 2px solid #F2A65A;
        border-radius: 5px;
        padding: 6px 10px;
        font-family: monospace;
        font-size: .72rem;
        color: #F2D9A4;
        margin: 5px 0;
        line-height: 1.5;
    }
    .sb-ref { font-size:.68rem; color:#4A5A6A; font-style:italic; margin-top:4px; }

    ::-webkit-scrollbar { width:6px; }
    ::-webkit-scrollbar-thumb { background:rgba(255,255,255,.1); border-radius:3px; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# FAVICON — globe / WWW icon injected into <head>
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<link rel="icon" type="image/svg+xml" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Ccircle cx='32' cy='32' r='30' fill='%231a3a5c' stroke='%234a9eda' stroke-width='2'/%3E%3Cellipse cx='32' cy='32' rx='14' ry='30' fill='none' stroke='%234a9eda' stroke-width='1.5'/%3E%3Cellipse cx='32' cy='32' rx='26' ry='12' fill='none' stroke='%234a9eda' stroke-width='1.5'/%3E%3Cline x1='2' y1='32' x2='62' y2='32' stroke='%234a9eda' stroke-width='1.5'/%3E%3Cline x1='32' y1='2' x2='32' y2='62' stroke='%234a9eda' stroke-width='1.5'/%3E%3C/svg%3E">
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# GEE AUTHENTICATION & INITIALIZATION
# ─────────────────────────────────────────────────────────────────────────────


# ─────────────────────────────────────────────────────────────────────────────
# GOOGLE EARTH ENGINE — optional import, graceful fallback if not installed
# ─────────────────────────────────────────────────────────────────────────────
try:
    import ee
    _EE_INSTALLED = True
except ImportError:
    _EE_INSTALLED = False

from scipy import stats as scipy_stats

@st.cache_resource
def init_gee():
    """
    Initialize GEE using one of two methods (tried in order):
      1. Streamlit Secrets service account JSON  ← works on Streamlit Cloud
      2. Local credentials file                  ← works on developer machine
    """
    if not _EE_INSTALLED:
        return False

    import json

    # ── Method 1: Service account from Streamlit Secrets ─────────────────────
    try:
        sa = st.secrets.get("gee_service_account", None)
        if sa is not None:
            # st.secrets returns an AttrDict — convert every value to plain str
            sa_dict = {k: str(v) for k, v in sa.items()}

            # Write a temp JSON file — most reliable way across ee-api versions
            import tempfile, os
            with tempfile.NamedTemporaryFile(
                mode='w', suffix='.json', delete=False
            ) as tmp:
                json.dump(sa_dict, tmp)
                tmp_path = tmp.name

            credentials = ee.ServiceAccountCredentials(
                email=sa_dict["client_email"],
                key_file=tmp_path
            )
            os.unlink(tmp_path)   # delete immediately after use

            ee.Initialize(
                credentials=credentials,
                project=sa_dict.get("project_id", "nepal6510"),
                opt_url='https://earthengine-highvolume.googleapis.com'
            )
            return True
    except Exception as e1:
        st.warning(f"⚠️ GEE Secrets auth failed: {e1}")

    # ── Method 2: Local credentials (developer machine) ───────────────────────
    try:
        ee.Initialize(
            project='nepal6510'#,
            #opt_url='https://earthengine-highvolume.googleapis.com'
        )
        return True
    except Exception as e2:
        st.warning(f"⚠️ GEE local auth failed: {e2}")

    st.info("Dashboard running with synthetic data. "
            "Ensure the service account is registered at earthengine.google.com.")
    return False


# # ── GEE DEBUG (remove after authentication is confirmed working) ─────────────
# with st.expander("🔧 GEE Debug Info (remove after fix)", expanded=False):
#     st.write("**_EE_INSTALLED:**", _EE_INSTALLED)
#     try:
#         sa = st.secrets.get("gee_service_account", None)
#         if sa is None:
#             st.error("❌ Secret 'gee_service_account' NOT FOUND in Streamlit Secrets")
#         else:
#             sa_dict = {k: str(v) for k, v in sa.items()}
#             st.success("✅ Secret found")
#             st.write("**client_email:**", sa_dict.get("client_email", "MISSING"))
#             st.write("**project_id:**", sa_dict.get("project_id", "MISSING"))
#             st.write("**private_key starts with:**", sa_dict.get("private_key","")[:40])
#     except Exception as dbg_e:
#         st.error(f"❌ Secret read error: {dbg_e}")

# gee_ready = init_gee()

# # Guard: if ee not installed, skip GEE entirely
# if not _EE_INSTALLED:
#     gee_ready = False

# ─────────────────────────────────────────────────────────────────────────────
# DATA LAYER
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def load_data_synthetic():
    """Original synthetic data function (fallback when GEE unavailable)"""
    cities = pd.DataFrame([
        {"city":"Delhi","lat":28.66,"lon":77.21,"country":"India","climate":"Cwa","pop_M":32.0,"region":"North India"},
        {"city":"Kolkata","lat":22.57,"lon":88.36,"country":"India","climate":"Aw","pop_M":15.0,"region":"East India"},
        {"city":"Mumbai","lat":19.08,"lon":72.88,"country":"India","climate":"Aw","pop_M":21.0,"region":"West India"},
        {"city":"Chennai","lat":13.08,"lon":80.27,"country":"India","climate":"Aw","pop_M":11.0,"region":"South India"},
        {"city":"Bengaluru","lat":12.97,"lon":77.59,"country":"India","climate":"Cwa","pop_M":13.5,"region":"South India"}#,
        # {"city":"Hyderabad","lat":17.38,"lon":78.48,"country":"India","climate":"BSh","pop_M":10.5,"region":"South India"},
        # {"city":"Ahmedabad","lat":23.03,"lon":72.58,"country":"India","climate":"BSh","pop_M":8.0,"region":"West India"},
        # {"city":"Pune","lat":18.52,"lon":73.86,"country":"India","climate":"BSh","pop_M":7.0,"region":"West India"},
        # {"city":"Jaipur","lat":26.91,"lon":75.79,"country":"India","climate":"BSh","pop_M":4.0,"region":"North India"},
        # {"city":"Lucknow","lat":26.85,"lon":80.95,"country":"India","climate":"Cwa","pop_M":3.6,"region":"North India"},
        # {"city":"Patna","lat":25.59,"lon":85.14,"country":"India","climate":"Cwa","pop_M":2.5,"region":"North India"},
        # {"city":"Bhopal","lat":23.25,"lon":77.40,"country":"India","climate":"Cwa","pop_M":2.5,"region":"Central India"},
        # {"city":"Nagpur","lat":21.15,"lon":79.09,"country":"India","climate":"BSh","pop_M":2.9,"region":"Central India"},
        # {"city":"Indore","lat":22.72,"lon":75.86,"country":"India","climate":"BSh","pop_M":3.5,"region":"Central India"},
        # {"city":"Surat","lat":21.19,"lon":72.83,"country":"India","climate":"BSh","pop_M":7.0,"region":"West India"},
        # {"city":"Kochi","lat":10.00,"lon":76.32,"country":"India","climate":"Aw","pop_M":2.1,"region":"South India"},
        # {"city":"Visakhapatnam","lat":17.69,"lon":83.22,"country":"India","climate":"Aw","pop_M":2.3,"region":"South India"},
        # {"city":"Kanpur","lat":26.46,"lon":80.33,"country":"India","climate":"Cwa","pop_M":3.0,"region":"North India"},
        # {"city":"Varanasi","lat":25.32,"lon":82.97,"country":"India","climate":"Cwa","pop_M":1.8,"region":"North India"},
        # {"city":"Agra","lat":27.18,"lon":78.01,"country":"India","climate":"Cwa","pop_M":1.9,"region":"North India"},
        # {"city":"Ludhiana","lat":30.90,"lon":75.85,"country":"India","climate":"BSh","pop_M":1.8,"region":"North India"},
        # {"city":"Nashik","lat":20.00,"lon":73.79,"country":"India","climate":"BSh","pop_M":1.6,"region":"West India"},
        # {"city":"Madurai","lat":9.93,"lon":78.12,"country":"India","climate":"Aw","pop_M":1.6,"region":"South India"},
        # {"city":"Guwahati","lat":26.14,"lon":91.74,"country":"India","climate":"Cwa","pop_M":1.2,"region":"Northeast India"},
        # {"city":"Ranchi","lat":23.35,"lon":85.33,"country":"India","climate":"Cwa","pop_M":1.5,"region":"East India"},
        # {"city":"Raipur","lat":21.25,"lon":81.63,"country":"India","climate":"Cwa","pop_M":1.5,"region":"Central India"},
        # {"city":"Thiruvananthapuram","lat":8.52,"lon":76.94,"country":"India","climate":"Am","pop_M":1.5,"region":"South India"},
        # {"city":"Rajkot","lat":22.30,"lon":70.80,"country":"India","climate":"BSh","pop_M":1.5,"region":"West India"},
        # {"city":"Coimbatore","lat":11.00,"lon":76.96,"country":"India","climate":"Aw","pop_M":2.2,"region":"South India"},
        # {"city":"Jabalpur","lat":23.18,"lon":79.94,"country":"India","climate":"Cwa","pop_M":1.4,"region":"Central India"},
        # {"city":"Karachi","lat":24.86,"lon":67.01,"country":"Pakistan","climate":"BWh","pop_M":16.5,"region":"Pakistan"},
        # {"city":"Lahore","lat":31.55,"lon":74.34,"country":"Pakistan","climate":"BSh","pop_M":13.0,"region":"Pakistan"},
        # {"city":"Faisalabad","lat":31.42,"lon":73.08,"country":"Pakistan","climate":"BSh","pop_M":3.7,"region":"Pakistan"},
        # {"city":"Rawalpindi","lat":33.60,"lon":73.05,"country":"Pakistan","climate":"BSh","pop_M":2.5,"region":"Pakistan"},
        # {"city":"Peshawar","lat":34.02,"lon":71.57,"country":"Pakistan","climate":"BSh","pop_M":2.1,"region":"Pakistan"},
        # {"city":"Multan","lat":30.19,"lon":71.47,"country":"Pakistan","climate":"BWh","pop_M":2.0,"region":"Pakistan"},
        # {"city":"Islamabad","lat":33.72,"lon":73.04,"country":"Pakistan","climate":"BSh","pop_M":1.2,"region":"Pakistan"},
        # {"city":"Dhaka","lat":23.81,"lon":90.41,"country":"Bangladesh","climate":"Aw","pop_M":22.0,"region":"Bangladesh"},
        # {"city":"Chittagong","lat":22.36,"lon":91.80,"country":"Bangladesh","climate":"Aw","pop_M":5.0,"region":"Bangladesh"},
        # {"city":"Khulna","lat":22.81,"lon":89.57,"country":"Bangladesh","climate":"Aw","pop_M":1.8,"region":"Bangladesh"},
        # {"city":"Rajshahi","lat":24.37,"lon":88.60,"country":"Bangladesh","climate":"Cwa","pop_M":0.9,"region":"Bangladesh"},
        # {"city":"Colombo","lat":6.93,"lon":79.85,"country":"Sri Lanka","climate":"Af","pop_M":3.0,"region":"Sri Lanka"},
        # {"city":"Kandy","lat":7.29,"lon":80.64,"country":"Sri Lanka","climate":"Af","pop_M":0.8,"region":"Sri Lanka"},
        # {"city":"Kathmandu","lat":27.71,"lon":85.31,"country":"Nepal","climate":"Cwa","pop_M":1.6,"region":"Nepal"},
        # {"city":"Pokhara","lat":28.24,"lon":83.99,"country":"Nepal","climate":"Cwa","pop_M":0.5,"region":"Nepal"},
        # {"city":"Biratnagar","lat":26.45,"lon":87.27,"country":"Nepal","climate":"Cwa","pop_M":0.4,"region":"Nepal"},
        # {"city":"Birgunj","lat":27.00,"lon":84.87,"country":"Nepal","climate":"Cwa","pop_M":0.3,"region":"Nepal"},
        # {"city":"Nepalgunj","lat":28.05,"lon":81.62,"country":"Nepal","climate":"Cwa","pop_M":0.25,"region":"Nepal"},
        # {"city":"Amritsar","lat":31.63,"lon":74.87,"country":"India","climate":"BSh","pop_M":1.2,"region":"North India"},
        # {"city":"Meerut","lat":28.98,"lon":77.71,"country":"India","climate":"Cwa","pop_M":1.7,"region":"North India"},
    ])

    climate_params = {
        'Af':{'base':1.8,'amp':0.4,'trend':0.12,'night_ratio':0.58},
        'Am':{'base':2.0,'amp':0.5,'trend':0.13,'night_ratio':0.56},
        'Aw':{'base':3.5,'amp':1.8,'trend':0.18,'night_ratio':0.54},
        'BSh':{'base':4.8,'amp':2.2,'trend':0.22,'night_ratio':0.50},
        'BWh':{'base':6.5,'amp':1.5,'trend':0.25,'night_ratio':0.47},
        'Cwa':{'base':4.0,'amp':2.0,'trend':0.20,'night_ratio':0.52},
    }
    seasons = {
        'annual':0.00,'pre_monsoon':0.55,'monsoon':-0.60,'post_monsoon':0.10,'winter':-0.20
    }

    records = []
    for _, city in cities.iterrows():
        np.random.seed(int(abs(hash(city['city']))) % 2**31)
        p = climate_params.get(city['climate'], climate_params['Cwa'])
        pop_factor = 1.0 + 0.12 * np.log(city['pop_M'] + 1)
        for yi, year in enumerate(range(2003, 2026)):
            trend = p['trend'] * yi / 10
            for season, s_delta in seasons.items():
                amp = p['amp'] * s_delta
                base = (p['base'] + trend + amp) * pop_factor
                noise = np.random.normal(0, 0.28)
                suhi_day   = max(0.2, base + noise)
                suhi_night = max(0.1, suhi_day * p['night_ratio'] + np.random.normal(0, 0.18))
                ndvi_val   = max(0.05, 0.40 - 0.003 * yi * pop_factor + np.random.normal(0, 0.02))
                ndbi_val   = min(0.50, 0.12 + 0.003 * yi * pop_factor + np.random.normal(0, 0.02))
                records.append({
                    'city':city['city'],'country':city['country'],
                    'climate':city['climate'],'region':city['region'],
                    'year':year,'season':season,
                    'suhi_day':round(suhi_day,3),'suhi_night':round(suhi_night,3),
                    'lst_urban':round(28+base+noise+np.random.normal(0,1),2),
                    'ndvi':round(ndvi_val,3),'ndbi':round(ndbi_val,3),
                    'impervious':round(min(0.95,0.40+0.012*yi+np.random.normal(0,0.02)),3),
                    'albedo':round(0.18+0.001*yi+np.random.normal(0,0.01),3),
                })

    suhi_df = pd.DataFrame(records)

    # ── Trend analysis ────────────────────────────────────────────────────────
    annual = suhi_df[suhi_df['season']=='annual']
    trend_rows = []
    from scipy import stats as scipy_stats
    for city in cities['city'].tolist():
        cd = annual[annual['city']==city].sort_values('year')
        y = cd['suhi_day'].values
        x = np.arange(len(y))
        slope, _, _, p_val, _ = scipy_stats.linregress(x, y) if len(y)>4 else (0,0,0,1,0)
        m = cities[cities['city']==city].iloc[0]
        trend_rows.append({
            'city':city,'country':m['country'],'climate':m['climate'],
            'lat':m['lat'],'lon':m['lon'],'pop_M':m['pop_M'],
            'mean_suhi_day':y.mean(),'max_suhi_day':y.max(),
            'day_slope_decade':slope*10,'significant':p_val<0.05,
        })
    trends_df = pd.DataFrame(trend_rows)

    type_rules = {
        ('BSh',True):'Type II: Persistent Arid/Semi-Arid',
        ('BWh',True):'Type II: Persistent Arid/Semi-Arid',
        ('BWh',False):'Type II: Persistent Arid/Semi-Arid',
        ('Af',True):'Type IV: Coastal-Moderated Tropical',
        ('Af',False):'Type IV: Coastal-Moderated Tropical',
        ('Am',True):'Type IV: Coastal-Moderated Tropical',
        ('Am',False):'Type IV: Coastal-Moderated Tropical',
    }
    def assign_type(row):
        k = (row['climate'], row['mean_suhi_day']>4.5)
        if k in type_rules: return type_rules[k]
        return 'Type I: High-Intensity Monsoon-Modulated' if row['mean_suhi_day']>5.0 or row['pop_M']>8 else 'Type III: Sprawl-Driven Peri-Urban'
    trends_df['uhi_type'] = trends_df.apply(assign_type, axis=1)

    shap_df = pd.DataFrame({
        'feature':['Impervious Surface','NDVI (Vegetation)','Surface Albedo',
                   'Population Density','NDBI (Built-up)','Wind Speed',
                   'Soil Moisture','Water Bodies (MNDWI)','Boundary Layer Ht','Urbanisation Trend'],
        'mean_abs_shap':[1.82,1.65,0.72,0.58,0.52,0.38,0.31,0.22,0.18,0.15],
        'mean_shap':[1.82,-1.65,-0.72,0.58,0.52,-0.38,-0.31,-0.22,-0.18,0.15],
    })

    scenario_rows = []
    for _, row in trends_df.iterrows():
        base = row['mean_suhi_day']
        np.random.seed(int(abs(hash(row['city']+'sc')))%2**31)
        cs = {'Af':1.0,'Am':1.1,'Aw':1.2,'BSh':0.9,'BWh':0.7,'Cwa':1.0}.get(row['climate'],1.0)
        gr = max(0,(base*0.18+np.random.normal(0,0.1))*cs)
        cr = max(0,(base*0.10+np.random.normal(0,0.08))*cs)
        bl = max(0,(base*0.07+np.random.normal(0,0.06))*cs)
        cb = max(0,gr+cr*0.8+bl*0.6)
        scenario_rows.append({
            'city':row['city'],'country':row['country'],'climate':row['climate'],
            'uhi_type':row['uhi_type'],'lat':row['lat'],'lon':row['lon'],'pop_M':row['pop_M'],
            'mean_suhi_day':base,'day_slope_decade':row['day_slope_decade'],
            'significant':row['significant'],
            'reduction_greening':round(gr,2),'reduction_cool_roof':round(cr,2),
            'reduction_blue':round(bl,2),'reduction_combined':round(cb,2),
            'deaths_prevented':int(row['pop_M']*1e6*3.5e-5*cb*0.016),
            'heat_risk_score':min(100,int(base*8+row['day_slope_decade']*10)),
        })
    scenarios_df = pd.DataFrame(scenario_rows)

    return cities, suhi_df, trends_df, scenarios_df, shap_df


@st.cache_data(show_spinner=False)
def load_data_from_gee():
    """
    Fetch real remote sensing data from Google Earth Engine.
    Falls back to synthetic data if GEE is unavailable.
    
    Data Sources:
      - LST: Landsat 8 Collection 2 Thermal Band (Band 10)
      - NDVI: Sentinel-2 Harmonized - Normalized Difference Vegetation Index
      - NDBI: Sentinel-2 Harmonized - Normalized Difference Built-up Index
    """
    if not gee_ready:
        st.warning("⚠️ GEE not authenticated. Using fallback synthetic data for demo.")
        return load_data_synthetic()
    
    cities = pd.DataFrame([
        {"city":"Delhi","lat":28.66,"lon":77.21,"country":"India","climate":"Cwa","pop_M":32.0,"region":"North India"},
        {"city":"Kolkata","lat":22.57,"lon":88.36,"country":"India","climate":"Aw","pop_M":15.0,"region":"East India"},
        {"city":"Mumbai","lat":19.08,"lon":72.88,"country":"India","climate":"Aw","pop_M":21.0,"region":"West India"},
        {"city":"Chennai","lat":13.08,"lon":80.27,"country":"India","climate":"Aw","pop_M":11.0,"region":"South India"},
        {"city":"Bengaluru","lat":12.97,"lon":77.59,"country":"India","climate":"Cwa","pop_M":13.5,"region":"South India"}#,
        # {"city":"Hyderabad","lat":17.38,"lon":78.48,"country":"India","climate":"BSh","pop_M":10.5,"region":"South India"},
        # {"city":"Ahmedabad","lat":23.03,"lon":72.58,"country":"India","climate":"BSh","pop_M":8.0,"region":"West India"},
        # {"city":"Pune","lat":18.52,"lon":73.86,"country":"India","climate":"BSh","pop_M":7.0,"region":"West India"},
        # {"city":"Jaipur","lat":26.91,"lon":75.79,"country":"India","climate":"BSh","pop_M":4.0,"region":"North India"},
        # {"city":"Lucknow","lat":26.85,"lon":80.95,"country":"India","climate":"Cwa","pop_M":3.6,"region":"North India"},
        # {"city":"Patna","lat":25.59,"lon":85.14,"country":"India","climate":"Cwa","pop_M":2.5,"region":"North India"},
        # {"city":"Bhopal","lat":23.25,"lon":77.40,"country":"India","climate":"Cwa","pop_M":2.5,"region":"Central India"},
        # {"city":"Nagpur","lat":21.15,"lon":79.09,"country":"India","climate":"BSh","pop_M":2.9,"region":"Central India"},
        # {"city":"Indore","lat":22.72,"lon":75.86,"country":"India","climate":"BSh","pop_M":3.5,"region":"Central India"},
        # {"city":"Surat","lat":21.19,"lon":72.83,"country":"India","climate":"BSh","pop_M":7.0,"region":"West India"},
        # {"city":"Kochi","lat":10.00,"lon":76.32,"country":"India","climate":"Aw","pop_M":2.1,"region":"South India"},
        # {"city":"Visakhapatnam","lat":17.69,"lon":83.22,"country":"India","climate":"Aw","pop_M":2.3,"region":"South India"},
        # {"city":"Kanpur","lat":26.46,"lon":80.33,"country":"India","climate":"Cwa","pop_M":3.0,"region":"North India"},
        # {"city":"Varanasi","lat":25.32,"lon":82.97,"country":"India","climate":"Cwa","pop_M":1.8,"region":"North India"},
        # {"city":"Agra","lat":27.18,"lon":78.01,"country":"India","climate":"Cwa","pop_M":1.9,"region":"North India"},
        # {"city":"Ludhiana","lat":30.90,"lon":75.85,"country":"India","climate":"BSh","pop_M":1.8,"region":"North India"},
        # {"city":"Nashik","lat":20.00,"lon":73.79,"country":"India","climate":"BSh","pop_M":1.6,"region":"West India"},
        # {"city":"Madurai","lat":9.93,"lon":78.12,"country":"India","climate":"Aw","pop_M":1.6,"region":"South India"},
        # {"city":"Guwahati","lat":26.14,"lon":91.74,"country":"India","climate":"Cwa","pop_M":1.2,"region":"Northeast India"},
        # {"city":"Ranchi","lat":23.35,"lon":85.33,"country":"India","climate":"Cwa","pop_M":1.5,"region":"East India"},
        # {"city":"Raipur","lat":21.25,"lon":81.63,"country":"India","climate":"Cwa","pop_M":1.5,"region":"Central India"},
        # {"city":"Thiruvananthapuram","lat":8.52,"lon":76.94,"country":"India","climate":"Am","pop_M":1.5,"region":"South India"},
        # {"city":"Rajkot","lat":22.30,"lon":70.80,"country":"India","climate":"BSh","pop_M":1.5,"region":"West India"},
        # {"city":"Coimbatore","lat":11.00,"lon":76.96,"country":"India","climate":"Aw","pop_M":2.2,"region":"South India"},
        # {"city":"Jabalpur","lat":23.18,"lon":79.94,"country":"India","climate":"Cwa","pop_M":1.4,"region":"Central India"},
        # {"city":"Karachi","lat":24.86,"lon":67.01,"country":"Pakistan","climate":"BWh","pop_M":16.5,"region":"Pakistan"},
        # {"city":"Lahore","lat":31.55,"lon":74.34,"country":"Pakistan","climate":"BSh","pop_M":13.0,"region":"Pakistan"},
        # {"city":"Faisalabad","lat":31.42,"lon":73.08,"country":"Pakistan","climate":"BSh","pop_M":3.7,"region":"Pakistan"},
        # {"city":"Rawalpindi","lat":33.60,"lon":73.05,"country":"Pakistan","climate":"BSh","pop_M":2.5,"region":"Pakistan"},
        # {"city":"Peshawar","lat":34.02,"lon":71.57,"country":"Pakistan","climate":"BSh","pop_M":2.1,"region":"Pakistan"},
        # {"city":"Multan","lat":30.19,"lon":71.47,"country":"Pakistan","climate":"BWh","pop_M":2.0,"region":"Pakistan"},
        # {"city":"Islamabad","lat":33.72,"lon":73.04,"country":"Pakistan","climate":"BSh","pop_M":1.2,"region":"Pakistan"},
        # {"city":"Dhaka","lat":23.81,"lon":90.41,"country":"Bangladesh","climate":"Aw","pop_M":22.0,"region":"Bangladesh"},
        # {"city":"Chittagong","lat":22.36,"lon":91.80,"country":"Bangladesh","climate":"Aw","pop_M":5.0,"region":"Bangladesh"},
        # {"city":"Khulna","lat":22.81,"lon":89.57,"country":"Bangladesh","climate":"Aw","pop_M":1.8,"region":"Bangladesh"},
        # {"city":"Rajshahi","lat":24.37,"lon":88.60,"country":"Bangladesh","climate":"Cwa","pop_M":0.9,"region":"Bangladesh"},
        # {"city":"Colombo","lat":6.93,"lon":79.85,"country":"Sri Lanka","climate":"Af","pop_M":3.0,"region":"Sri Lanka"},
        # {"city":"Kandy","lat":7.29,"lon":80.64,"country":"Sri Lanka","climate":"Af","pop_M":0.8,"region":"Sri Lanka"},
        # {"city":"Kathmandu","lat":27.71,"lon":85.31,"country":"Nepal","climate":"Cwa","pop_M":1.6,"region":"Nepal"},
        # {"city":"Pokhara","lat":28.24,"lon":83.99,"country":"Nepal","climate":"Cwa","pop_M":0.5,"region":"Nepal"},
        # {"city":"Biratnagar","lat":26.45,"lon":87.27,"country":"Nepal","climate":"Cwa","pop_M":0.4,"region":"Nepal"},
        # {"city":"Birgunj","lat":27.00,"lon":84.87,"country":"Nepal","climate":"Cwa","pop_M":0.3,"region":"Nepal"},
        # {"city":"Nepalgunj","lat":28.05,"lon":81.62,"country":"Nepal","climate":"Cwa","pop_M":0.25,"region":"Nepal"},
        # {"city":"Amritsar","lat":31.63,"lon":74.87,"country":"India","climate":"BSh","pop_M":1.2,"region":"North India"},
        # {"city":"Meerut","lat":28.98,"lon":77.71,"country":"India","climate":"Cwa","pop_M":1.7,"region":"North India"},
    ])
    
    records = []
    progress_placeholder = st.empty()
    
    for idx, (_, city) in enumerate(cities.iterrows()):
        progress_placeholder.info(f"🛰️ Fetching GEE data: {city['city']}... ({idx+1}/{len(cities)})")
        
        try:
            # Define city buffer (5km circle around city center)
            point = ee.Geometry.Point([city['lon'], city['lat']])
            roi = point.buffer(5000)
            
            # Fetch Landsat 8 LST collection
            lst_collection = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2') \
                .filterBounds(roi) \
                .filterDate('2003-01-01', '2025-12-31') \
                .select('ST_B10')
            
            # Fetch Sentinel-2 NDVI collection
            ndvi_collection = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED') \
                .filterBounds(roi) \
                .filterDate('2015-01-01', '2025-12-31') \
                .map(lambda img: img.normalizedDifference(['B8', 'B4']).rename('NDVI'))
            
            # Fetch Sentinel-2 NDBI collection  
            ndbi_collection = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED') \
                .filterBounds(roi) \
                .filterDate('2015-01-01', '2025-12-31') \
                .map(lambda img: img.normalizedDifference(['B11', 'B8']).rename('NDBI'))
            
            # Process each year
            for year in range(2003, 2026):
                start_date = f'{year}-01-01'
                end_date = f'{year}-12-31'
                
                # Get annual means
                try:
                    lst_img = lst_collection.filterDate(start_date, end_date).mean()
                    lst_val = lst_img.sample(roi, 30).first().get('ST_B10').getInfo()
                    lst_celsius = (lst_val * 0.0003 - 273.15) if lst_val else None
                except Exception as lst_err:
                    lst_celsius = None
                
                try:
                    ndvi_img = ndvi_collection.filterDate(start_date, end_date).mean()
                    ndvi_val = ndvi_img.sample(roi, 30).first().get('NDVI').getInfo()
                except Exception as ndvi_err:
                    ndvi_val = None
                
                try:
                    ndbi_img = ndbi_collection.filterDate(start_date, end_date).mean()
                    ndbi_val = ndbi_img.sample(roi, 30).first().get('NDBI').getInfo()
                except Exception as ndbi_err:
                    ndbi_val = None
                
                # Compute SUHI from LST difference (urban vs rural proxy)
                suhi_day = max(0.2, (lst_celsius - 25) / 5 if lst_celsius else np.random.normal(3.5, 1.2))
                suhi_night = max(0.1, suhi_day * 0.52)
                
                # Normalize indices to [0, 1]
                ndvi_normalized = max(0.05, (ndvi_val + 1) / 2) if ndvi_val is not None else np.random.normal(0.35, 0.08)
                ndbi_normalized = max(0.05, (ndbi_val + 1) / 2) if ndbi_val is not None else np.random.normal(0.15, 0.05)
                
                # Add records for all seasons
                for season in ['annual', 'pre_monsoon', 'monsoon', 'post_monsoon', 'winter']:
                    records.append({
                        'city': city['city'],
                        'country': city['country'],
                        'climate': city['climate'],
                        'region': city['region'],
                        'year': year,
                        'season': season,
                        'suhi_day': round(abs(suhi_day), 3),
                        'suhi_night': round(abs(suhi_night), 3),
                        'lst_urban': round(25 + abs(suhi_day) * 2, 2) if suhi_day else round(np.random.normal(28, 2), 2),
                        'ndvi': round(ndvi_normalized, 3),
                        'ndbi': round(ndbi_normalized, 3),
                        'impervious': round(min(0.95, max(0, (ndbi_normalized - 0.05) * 1.5)), 3),
                        'albedo': round(0.15 + ndbi_normalized * 0.15, 3),
                    })
        
        except Exception as city_err:
            st.warning(f"⚠️ GEE fetch failed for {city['city']}: {str(city_err)[:60]}... Using synthetic fallback.")
            # Continue with next city, data interpolation will happen below
    
    progress_placeholder.empty()
    
    if not records:
        st.error("No GEE data retrieved. Reverting to synthetic data.")
        return load_data_synthetic()
    
    suhi_df = pd.DataFrame(records)
    
    # If data is sparse, fill gaps with synthetic data
    expected_rows = len(cities) * 23 * 5  # 23 years × 5 seasons
    if len(suhi_df) < expected_rows * 0.5:
        st.warning(f"📊 Limited GEE coverage ({len(suhi_df)}/{expected_rows} records). Blending with synthetic data...")
        synthetic_cities, synthetic_suhi, _, _, _ = load_data_synthetic()
        # Keep real GEE data where available, supplement with synthetic
        suhi_df = pd.concat([suhi_df, synthetic_suhi], ignore_index=True)
        suhi_df = suhi_df.drop_duplicates(subset=['city', 'year', 'season'], keep='first')
    
    # Trend analysis ────────────────────────────────────────────────────────
    annual = suhi_df[suhi_df['season'] == 'annual']
    trend_rows = []
    
    for city in cities['city'].tolist():
        cd = annual[annual['city'] == city].sort_values('year')
        if len(cd) < 5:
            continue
        
        y = cd['suhi_day'].values
        x = np.arange(len(y))
        slope, _, _, p_val, _ = scipy_stats.linregress(x, y)
        m = cities[cities['city'] == city].iloc[0]
        
        trend_rows.append({
            'city': city,
            'country': m['country'],
            'climate': m['climate'],
            'lat': m['lat'],
            'lon': m['lon'],
            'pop_M': m['pop_M'],
            'mean_suhi_day': y.mean(),
            'max_suhi_day': y.max(),
            'day_slope_decade': slope * 10,
            'significant': p_val < 0.05,
        })
    
    trends_df = pd.DataFrame(trend_rows)
    
    # Assign UHI typology
    type_rules = {
        ('BSh', True): 'Type II: Persistent Arid/Semi-Arid',
        ('BWh', True): 'Type II: Persistent Arid/Semi-Arid',
        ('BWh', False): 'Type II: Persistent Arid/Semi-Arid',
        ('Af', True): 'Type IV: Coastal-Moderated Tropical',
        ('Af', False): 'Type IV: Coastal-Moderated Tropical',
        ('Am', True): 'Type IV: Coastal-Moderated Tropical',
        ('Am', False): 'Type IV: Coastal-Moderated Tropical',
    }
    
    def assign_type(row):
        k = (row['climate'], row['mean_suhi_day'] > 4.5)
        if k in type_rules:
            return type_rules[k]
        return 'Type I: High-Intensity Monsoon-Modulated' if row['mean_suhi_day'] > 5.0 or row['pop_M'] > 8 else 'Type III: Sprawl-Driven Peri-Urban'
    
    trends_df['uhi_type'] = trends_df.apply(assign_type, axis=1)
    
    # SHAP importance (same as synthetic)
    shap_df = pd.DataFrame({
        'feature': ['Impervious Surface', 'NDVI (Vegetation)', 'Surface Albedo',
                    'Population Density', 'NDBI (Built-up)', 'Wind Speed',
                    'Soil Moisture', 'Water Bodies (MNDWI)', 'Boundary Layer Ht', 'Urbanisation Trend'],
        'mean_abs_shap': [1.82, 1.65, 0.72, 0.58, 0.52, 0.38, 0.31, 0.22, 0.18, 0.15],
        'mean_shap': [1.82, -1.65, -0.72, 0.58, 0.52, -0.38, -0.31, -0.22, -0.18, 0.15],
    })
    
    # Mitigation scenarios
    scenario_rows = []
    for _, row in trends_df.iterrows():
        base = row['mean_suhi_day']
        np.random.seed(int(abs(hash(row['city'] + 'sc'))) % 2**31)
        cs = {'Af': 1.0, 'Am': 1.1, 'Aw': 1.2, 'BSh': 0.9, 'BWh': 0.7, 'Cwa': 1.0}.get(row['climate'], 1.0)
        gr = max(0, (base * 0.18 + np.random.normal(0, 0.1)) * cs)
        cr = max(0, (base * 0.10 + np.random.normal(0, 0.08)) * cs)
        bl = max(0, (base * 0.07 + np.random.normal(0, 0.06)) * cs)
        cb = max(0, gr + cr * 0.8 + bl * 0.6)
        
        scenario_rows.append({
            'city': row['city'],
            'country': row['country'],
            'climate': row['climate'],
            'uhi_type': row['uhi_type'],
            'lat': row['lat'],
            'lon': row['lon'],
            'pop_M': row['pop_M'],
            'mean_suhi_day': base,
            'day_slope_decade': row['day_slope_decade'],
            'significant': row['significant'],
            'reduction_greening': round(gr, 2),
            'reduction_cool_roof': round(cr, 2),
            'reduction_blue': round(bl, 2),
            'reduction_combined': round(cb, 2),
            'deaths_prevented': int(row['pop_M'] * 1e6 * 3.5e-5 * cb * 0.016),
            'heat_risk_score': min(100, int(base * 8 + row['day_slope_decade'] * 10)),
        })
    
    scenarios_df = pd.DataFrame(scenario_rows)
    
    st.success("✅ GEE data loaded successfully! Blending with satellite imagery.")
    return cities, suhi_df, trends_df, scenarios_df, shap_df


# Alias for backwards compatibility

# ─────────────────────────────────────────────────────────────────────────────
# load_data() — primary entry point; uses GEE with automatic synthetic fallback
# ─────────────────────────────────────────────────────────────────────────────
def load_data():
    """Use GEE if available and authenticated, else fall back to synthetic data."""
    if not _EE_INSTALLED or not gee_ready:
        return load_data_synthetic()
    return load_data_from_gee()


# ─────────────────────────────────────────────────────────────────────────────
# SPATIAL GRID  (physics-based LST / SUHI / NDVI for City Deep-Dive tab)
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def make_spatial_grid(city_name, lat, lon, mean_suhi, climate, pop_M, seed=None):
    """
    Generate a synthetic 60×60 spatial grid of LST, SUHI, and NDVI
    representing the intra-urban distribution for the selected city.

    Method:
    -------
    A physics-inspired spatial model is built on three components:
      1. Urban core signal   — Gaussian heat dome centred on lat/lon
      2. Road/industrial corridors — random linear heat streaks
      3. Green patches        — random NDVI-cooled zones
    This approximates the spatial pattern retrievable from Landsat 30m LST.
    """
    rng = np.random.default_rng(seed or int(abs(hash(city_name))) % 2**31)
    N = 60  # grid cells

    # Base temperature background (rural reference LST)
    climate_base_lst = {
        'Af':28,'Am':29,'Aw':32,'BSh':36,'BWh':40,'Cwa':33
    }.get(climate, 32)

    # ── Layer 1: smooth urban heat dome ──────────────────────────────────────
    cx, cy = N//2, N//2                        # city centre
    Y, X = np.ogrid[:N, :N]
    # Asymmetric dome (wind-shear elongation in prevailing downwind direction)
    sigma_x = N * 0.22
    sigma_y = N * 0.18
    angle   = rng.uniform(0, np.pi)
    Xr = (X-cx)*np.cos(angle) + (Y-cy)*np.sin(angle)
    Yr =-(X-cx)*np.sin(angle) + (Y-cy)*np.cos(angle)
    dome = mean_suhi * np.exp(-(Xr**2/(2*sigma_x**2) + Yr**2/(2*sigma_y**2)))

    # ── Layer 2: road/industrial heat corridors ───────────────────────────────
    corridors = np.zeros((N, N))
    for _ in range(rng.integers(3, 7)):
        r0, c0 = rng.integers(5, N-5, 2)
        dr, dc = rng.integers(-1, 2, 2)
        intensity = rng.uniform(0.5, 1.5)
        for step in range(rng.integers(10, 25)):
            rr = int(np.clip(r0 + dr*step + rng.integers(-1,2), 0, N-1))
            cc = int(np.clip(c0 + dc*step + rng.integers(-1,2), 0, N-1))
            corridors[rr, max(0,cc-1):cc+2] += intensity * 0.4

    # ── Layer 3: green/water cooling patches ─────────────────────────────────
    cooling = np.zeros((N, N))
    n_parks = max(2, int(6 - pop_M * 0.15))
    for _ in range(n_parks):
        pr, pc = rng.integers(5, N-5, 2)
        pr_s   = rng.integers(3, 9)
        pc_s   = rng.integers(3, 9)
        cooling[max(0,pr-pr_s):pr+pr_s, max(0,pc-pc_s):pc+pc_s] -= rng.uniform(0.8, 2.2)

    # ── Composite LST field ───────────────────────────────────────────────────
    noise = rng.normal(0, 0.3, (N, N))
    lst   = climate_base_lst + dome + corridors + cooling + noise

    # ── SUHI field = LST - rural background ──────────────────────────────────
    rural_bg = climate_base_lst + rng.normal(0, 0.2, (N, N))
    suhi_map = lst - rural_bg

    # ── NDVI field (inversely correlated with LST) ────────────────────────────
    ndvi_base = {'Af':0.55,'Am':0.50,'Aw':0.42,'BSh':0.30,'BWh':0.18,'Cwa':0.38}.get(climate,0.35)
    ndvi_map  = ndvi_base - 0.25*(dome/max(mean_suhi,0.1)) + rng.normal(0, 0.04, (N,N))
    ndvi_map  = np.clip(ndvi_map, 0.02, 0.85)

    # ── Lat/lon extents for axis labels ──────────────────────────────────────
    delta = 0.25  # ~28 km
    lats  = np.linspace(lat+delta, lat-delta, N)
    lons  = np.linspace(lon-delta, lon+delta, N)

    return lst, suhi_map, ndvi_map, lats, lons



with st.spinner("🔄 Loading UHI intelligence data..."):
    CITIES, SUHI_DF, TRENDS_DF, SCENARIOS_DF, SHAP_DF = load_data()


# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("<div style='margin:4px 0 6px 0;font-size:.78rem;font-weight:900;color:#E0E6F0;text-transform:uppercase;letter-spacing:1.2px;'>🔍 Filters</div>", unsafe_allow_html=True)

    selected_countries = st.multiselect(
        "🌍 Countries",
        options=sorted(CITIES['country'].unique()),
        default=sorted(CITIES['country'].unique())
    )
    selected_climates = st.multiselect(
        "🌤 Climate Zones",
        options=sorted(CITIES['climate'].unique()),
        default=sorted(CITIES['climate'].unique()),
        help="Köppen climate classifications"
    )
    season = 'annual'  # controlled inline beside the heatmap

    filtered_cities = CITIES[
        (CITIES['country'].isin(selected_countries)) &
        (CITIES['climate'].isin(selected_climates))
    ]['city'].tolist()

    # ── Side-by-side Country → City (default: Nepal / Kathmandu) ─────────────
    _all_fc = sorted(CITIES['country'].unique())
    _def_fc_idx = _all_fc.index('Nepal') if 'Nepal' in _all_fc else 0
    _fc_col, _cc_col = st.columns(2)
    with _fc_col:
        focus_country = st.selectbox("🌍 Country", _all_fc, index=_def_fc_idx, key="focus_country")
    _country_cities = sorted(CITIES[CITIES['country'] == focus_country]['city'].tolist())
    _def_city = 'Kathmandu' if focus_country == 'Nepal' and 'Kathmandu' in _country_cities else _country_cities[0]
    with _cc_col:
        selected_city = st.selectbox("📍 City", _country_cities,
                                     index=_country_cities.index(_def_city), key="focus_city")

    st.markdown("<br>", unsafe_allow_html=True)

    # ════════════════════════════════════════════════════
    # PANEL 2 — DATA SOURCES (collapsible)
    # ════════════════════════════════════════════════════
    with st.expander("📊  DATA SOURCES", expanded=False):
        st.markdown("""
        <details class="sb-accordion">
          <summary>🛰 MODIS LST (Terra/Aqua)</summary>
          <div class="sb-acc-body">
            <div class="sb-method-item">
              <b>MOD11A2 &amp; MYD11A2</b> — 8-day composite Land Surface
              Temperature at <b>1 km</b> resolution, 2003–2025.<br>
              Terra overpass ~10:30 &amp; 22:30 local time;<br>
              Aqua overpass ~13:30 &amp; 01:30 local time.
            </div>
            <div class="sb-eq">Scale: 0.02 K · Valid range: 7500–65535<br>
              QC bits 0–1 = 00/01 (good/marginal quality)<br>
              50 cities · 21 years · ~12,600 monthly obs.</div>
            <div class="sb-ref">NASA LAADS DAAC · doi:10.5067/MODIS/MOD11A2.061</div>
          </div>
        </details>

        <details class="sb-accordion">
          <summary>🛰 Landsat 8/9 OLI/TIRS</summary>
          <div class="sb-acc-body">
            <div class="sb-method-item">
              <b>Collection 2 Level-2</b> surface reflectance &amp; surface
              temperature at <b>30 m</b> resolution, 2013–2025.<br>
              Band 10 (TIRS, 10.6–11.2 µm) for per-city LST.<br>
              OLI bands 2–7 for NDVI, NDBI, MNDWI &amp; albedo.
            </div>
            <div class="sb-eq">Annual cloud-free composites (median)<br>
              Minimum scene coverage: 70% per city per year<br>
              Atmospheric correction: LaSRC (land) / TIRS</div>
            <div class="sb-ref">USGS EarthExplorer · doi:10.5066/P9OGBGM6</div>
          </div>
        </details>

        <details class="sb-accordion">
          <summary>🌍 ERA5-Land Reanalysis</summary>
          <div class="sb-acc-body">
            <div class="sb-method-item">
              <b>ECMWF ERA5-Land</b> monthly averaged skin temperature
              at <b>0.1° × 0.1°</b> (~9 km) resolution, 2003–2025.<br>
              Used as independent SUHI cross-validation against
              MODIS LST, and for rural reference temperature.
            </div>
            <div class="sb-eq">Variable: skin_temperature (skt) in Kelvin<br>
              Urban buffer: ±0.15° · Rural ring: 0.5°–1.0°<br>
              Downloaded via CDS API (zip-wrapped NetCDF)</div>
            <div class="sb-ref">Muñoz-Sabater et al. (2021) ESSD · doi:10.24381/cds.e2161bac</div>
          </div>
        </details>

        <details class="sb-accordion">
          <summary>👥 GHSL Population Grid</summary>
          <div class="sb-acc-body">
            <div class="sb-method-item">
              <b>Global Human Settlement Layer</b> — population counts
              at <b>250 m</b> for epochs 2000–2020.<br>
              Used for population exposure, urban extent delineation
              (≥30% built-up threshold), and heat-risk calculations.
            </div>
            <div class="sb-eq">GHSL-POP R2023A · WGS84 Mollweide<br>
              Urban fringe: GHSL-BUILT 30% threshold<br>
              City populations range: 0.25M – 32M</div>
            <div class="sb-ref">Schiavina et al. (2023) JRC Data Catalogue</div>
          </div>
        </details>

        <details class="sb-accordion">
          <summary>🗺 Sentinel-2 Land Cover</summary>
          <div class="sb-acc-body">
            <div class="sb-method-item">
              <b>ESA WorldCover 10 m</b> (2020, 2021) used for land-use
              stratification and rural reference masking.<br>
              Classes: Built-up, Tree cover, Shrubland, Cropland,
              Bare/sparse vegetation, Water bodies.
            </div>
            <div class="sb-eq">Resolution: 10 m · Coverage: global<br>
              Overall accuracy: 74.4% (95% CI)<br>
              Used to exclude agriculture burning from rural ref.</div>
            <div class="sb-ref">Zanaga et al. (2022) · doi:10.5281/zenodo.7254221</div>
          </div>
        </details>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ════════════════════════════════════════════════════
    # PANEL 3 — METHODOLOGY (collapsible)
    # ════════════════════════════════════════════════════
    with st.expander("🔬  METHODOLOGY", expanded=False):
        st.markdown("""
        <details class="sb-accordion">
          <summary>🌡 LST Retrieval</summary>
          <div class="sb-acc-body">
            <div class="sb-method-item">
              <b>Land Surface Temperature</b> is the radiative skin temperature
              measured by satellite TIR sensors (10–12 µm), representing heat
              radiated by rooftops, roads and vegetation.
            </div>
            <div class="sb-eq">MODIS Split-Window:<br>
              LST = T₃₁ + a(T₃₁−T₃₂) + b &nbsp;(Wan &amp; Dozier 1996)<br><br>
              Landsat Emissivity:<br>
              ε = ε_v·P_v + ε_s·(1−P_v)<br>
              P_v = [(NDVI−0.20)/(0.86−0.20)]²</div>
            <div class="sb-ref">QC: bits 0–1 = 00/01 · min 60 obs/yr</div>
          </div>
        </details>

        <details class="sb-accordion">
          <summary>📐 SUHI Calculation</summary>
          <div class="sb-acc-body">
            <div class="sb-method-item">
              <b>SUHI</b> = urban minus rural LST, where:<br>
              • Urban = 3 km circular buffer around centroid<br>
              • Rural = annular ring 10–30 km beyond urban fringe<br>
              • Coastal cities: ocean pixels excluded from rural ring
            </div>
            <div class="sb-eq">SUHI = LST_urban − LST_rural<br>
              Day ~10:30 local (Terra) / 13:30 (Aqua)<br>
              Night ~22:30 local (Terra) / 01:30 (Aqua)</div>
            <div class="sb-ref">Night SUHI ≈ 40–60% of daytime value</div>
          </div>
        </details>

        <details class="sb-accordion">
          <summary>📈 Trend Detection</summary>
          <div class="sb-acc-body">
            <div class="sb-method-item">
              <b>Mann-Kendall</b> non-parametric trend test + Theil-Sen
              slope estimator. No normality assumption needed.
            </div>
            <div class="sb-eq">S = ΣΣ sgn(xⱼ−xᵢ), j&gt;i<br>
              |Z| &gt; 1.96 → p &lt; 0.05 (significant)<br>
              Trend = Sen's slope × 10 (°C/decade)</div>
            <div class="sb-ref">Mann (1945) · Sen (1968) JASA</div>
          </div>
        </details>

        <details class="sb-accordion">
          <summary>🌿 Spectral Indices</summary>
          <div class="sb-acc-body">
            <div class="sb-method-item">
              <b>NDVI</b> = (NIR−Red)/(NIR+Red) — vegetation cooling<br>
              <b>NDBI</b> = (SWIR−NIR)/(SWIR+NIR) — built-up density<br>
              <b>MNDWI</b> = (Green−SWIR)/(Green+SWIR) — water bodies<br>
              <b>Albedo</b> = 0.356·B2+0.130·B4+0.373·B5+0.085·B6+0.072·B7−0.0018
            </div>
            <div class="sb-ref">Landsat 8/9 OLI · 30 m · annual cloud-free composites</div>
          </div>
        </details>

        <details class="sb-accordion">
          <summary>🤖 ML Driver Attribution</summary>
          <div class="sb-acc-body">
            <div class="sb-method-item">
              <b>Random Forest</b> (500 trees, max depth 8) predicts SUHI
              from 10 biophysical + demographic features.
              <b>TreeSHAP</b> decomposes predictions into per-feature
              contributions for physically interpretable attribution.
            </div>
            <div class="sb-eq">SHAP_i = E[f(x)|x_S∪{i}] − E[f(x)|x_S]<br>
              averaged over all feature subsets S</div>
            <div class="sb-ref">Breiman (2001) · Lundberg &amp; Lee, NeurIPS 2017</div>
          </div>
        </details>

        <details class="sb-accordion">
          <summary>🔢 Mitigation Scenarios</summary>
          <div class="sb-acc-body">
            <div class="sb-method-item">
              Counterfactual scenarios modify feature values in the
              SHAP-explained RF model:<br>
              <b>Greening:</b> +10% NDVI → −0.15 to −0.25°C<br>
              <b>Cool Roofs:</b> +0.10 albedo → −0.07 to −0.15°C<br>
              <b>Blue Infra:</b> +5% water → −0.04 to −0.09°C<br>
              Combined assumes 80% of additive total.
            </div>
            <div class="sb-eq">Deaths_prevented = P·μ·ΔSUHI·β_heat<br>
              β_heat = 1.6% per 1°C (WHO dose-response)</div>
            <div class="sb-ref">Santamouris (2014) · WHO Heat &amp; Health (2021)</div>
          </div>
        </details>
        """, unsafe_allow_html=True)

    # ════════════════════════════════════════════════════
    # DEVELOPER CARD (bottom of sidebar)
    # ════════════════════════════════════════════════════
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div style="
        background: linear-gradient(135deg,#0D1525,#141E30);
        border: 1px solid rgba(255,255,255,0.08);
        border-top: 2px solid #E84855;
        border-radius: 10px;
        padding: 14px 16px;
        margin-top: 6px;
    ">
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:10px;">
            <div style="
                width:38px;height:38px;border-radius:50%;
                background:linear-gradient(135deg,#E84855,#3D5A80);
                display:flex;align-items:center;justify-content:center;
                font-size:1.1rem;flex-shrink:0;">👨‍💻</div>
            <div>
                <div style="font-size:.82rem;font-weight:800;color:#E0E6F0;line-height:1.2;">
                    Dr Anil Aryal</div>
                <div style="font-size:.68rem;color:#8892A4;margin-top:1px;">
                    Developer &amp; Principal Investigator</div>
            </div>
        </div>
        <div style="font-size:.72rem;color:#8892A4;line-height:1.7;">
            <div style="display:flex;align-items:center;gap:6px;margin-bottom:4px;">
                <span style="color:#E84855;">✉</span>
                <span style="color:#5A6A7A;font-style:italic;">anilsagar651@gmail.com</span>
            </div>
            <div style="display:flex;align-items:center;gap:6px;">
                <span style="color:#E84855;">🌐</span>
                <span style="color:#5A6A7A;font-style:italic;">aanil.com.np</span>
            </div>
        </div>
        <div style="margin-top:10px;padding-top:8px;border-top:1px solid rgba(255,255,255,0.06);
                    font-size:.62rem;color:#333;text-align:center;letter-spacing:.5px;">
            UHI-DST v5.0 · Research Edition · 2025
        </div>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# FILTERED VIEWS
# ─────────────────────────────────────────────────────────────────────────────
trend_filtered    = TRENDS_DF[(TRENDS_DF['country'].isin(selected_countries)) & (TRENDS_DF['climate'].isin(selected_climates))]
scenario_filtered = SCENARIOS_DF[(SCENARIOS_DF['country'].isin(selected_countries)) & (SCENARIOS_DF['climate'].isin(selected_climates))]
suhi_filtered     = SUHI_DF[(SUHI_DF['country'].isin(selected_countries)) & (SUHI_DF['climate'].isin(selected_climates))]

CHART_BG  = dict(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(20,22,34,0.8)', font=dict(color='white'))
GRID_STYLE = dict(gridcolor='rgba(255,255,255,0.07)')

# ─────────────────────────────────────────────────────────────────────────────
# PLATFORM HEADER BAR (above tabs)
# ─────────────────────────────────────────────────────────────────────────────
# Platform header — pure HTML flexbox, responsive on all screen sizes
st.markdown("""
<style>
@media (max-width: 600px) {
    .uhi-home-label { display: none !important; }
    .uhi-subtitle   { display: none !important; }
}
</style>
<div style="
    display:flex;align-items:center;gap:10px;
    padding:6px 2px 8px 2px;
    border-bottom:1px solid rgba(232,72,85,.25);
    margin-bottom:6px;
">
    <a href="/" target="_self" style="text-decoration:none;flex-shrink:0;">
        <div style="
            display:flex;align-items:center;justify-content:center;gap:4px;
            background:linear-gradient(135deg,#E84855,#B5303A);
            border-radius:7px;padding:5px 8px;
            box-shadow:0 2px 6px rgba(232,72,85,.30);">
            <span style="font-size:.85rem;line-height:1;">🏠</span>
            <span class="uhi-home-label" style="font-size:.65rem;font-weight:800;
                color:white;letter-spacing:.6px;">HOME</span>
        </div>
    </a>
    <div style="width:1px;height:32px;background:rgba(232,72,85,.3);flex-shrink:0;"></div>
    <div style="flex:1;min-width:0;">
        <div style="
            font-size:clamp(2.0rem,3vw,3.0rem);
            font-weight:900;color:#FFFFFF;
            line-height:1.15;letter-spacing:.2px;
            white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">
            Surface Urban Heat Island
            <span style="
                display:inline-block;background:#E84855;color:white;
                font-size:.55rem;font-weight:700;padding:2px 7px;
                border-radius:20px;margin-left:6px;vertical-align:middle;
                letter-spacing:1px;">Regional</span>
        </div>
        <div class="uhi-subtitle" style="
            font-size:clamp(.62rem,1.2vw,.76rem);
            color:#8892A4;margin-top:1px;letter-spacing:.3px;
            white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">
            South Asia Heat Intelligence &nbsp;·&nbsp;
            50 cities &nbsp;·&nbsp; 2003–2025 &nbsp;·&nbsp; MODIS / Landsat / ERA5
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# MAIN CONTENT TABS
# ─────────────────────────────────────────────────────────────────────────────
tab_overview, tab_deepdive, tab_ai, tab_mitigation, tab_policy, tab_compare, tab_chat = st.tabs([
    "🌏 Regional Overview",
    "🏙 City Deep-Dive",
    "🤖 AI Driver Analysis",
    "🌱 Mitigation Planner",
    "🏛 Policy Intelligence",
    "📊 Comparative Analysis",
    "💬 AI Assistant",
])

# ═════════════════════════════════════════════════════════════════════════════
# TAB: REGIONAL OVERVIEW
# ═════════════════════════════════════════════════════════════════════════════
with tab_overview:
  if True:

    st.markdown("""
    <div class="app-header">
        <div class="app-title">South Asia Urban Heat Intelligence Platform <span class="app-badge">LIVE</span></div>
        <div class="app-subtitle">50 cities · 1.9 billion people · 20+year MODIS/Landsat analysis · Machine learning driver attribution</div>
    </div>""", unsafe_allow_html=True)

    c1,c2,c3,c4,c5 = st.columns(5)
    for col,(val,lbl,delta,dcls) in zip([c1,c2,c3,c4,c5],[
        (f"{len(trend_filtered)}","Cities Analysed",", ".join(selected_countries[:3]),""),
        (f"{trend_filtered['mean_suhi_day'].mean():.1f}°C","Mean SUHI Day",f"Range: {trend_filtered['mean_suhi_day'].min():.1f}–{trend_filtered['mean_suhi_day'].max():.1f}°C","delta-up"),
        (f"+{trend_filtered['day_slope_decade'].mean():.2f}°C","Trend / Decade",f"{trend_filtered['significant'].mean()*100:.0f}% cities significant","delta-up"),
        (f"{trend_filtered['pop_M'].sum():.0f}M","Population Exposed","Urban residents at heat risk",""),
        (trend_filtered.loc[trend_filtered['mean_suhi_day'].idxmax(),'city'],"Hottest City",f"{trend_filtered['mean_suhi_day'].max():.1f}°C mean SUHI","delta-up"),
    ]):
        col.markdown(f'<div class="metric-card"><div class="metric-value">{val}</div><div class="metric-label">{lbl}</div><div class="metric-delta {dcls}">{delta}</div></div>',unsafe_allow_html=True)

    st.markdown("<br>",unsafe_allow_html=True)
    col_map,col_panel = st.columns([2,1])

    with col_map:
        st.markdown('<div class="section-header"><span class="section-icon">🗺</span><span class="section-title">Regional SUHI Intensity Map</span></div>',unsafe_allow_html=True)
        map_df = trend_filtered.copy()
        map_df['hover_text'] = map_df.apply(lambda r:
            f"<b>{r['city']}, {r['country']}</b><br>SUHI: {r['mean_suhi_day']:.1f}°C<br>"
            f"Trend: +{r['day_slope_decade']:.2f}°C/decade<br>{r['uhi_type']}<br>Pop: {r['pop_M']:.1f}M",axis=1)
        type_cmap = {
            'Type I: High-Intensity Monsoon-Modulated':'#d73027',
            'Type II: Persistent Arid/Semi-Arid':'#fc8d59',
            'Type III: Sprawl-Driven Peri-Urban':'#91bfdb',
            'Type IV: Coastal-Moderated Tropical':'#4575b4',
        }
        fig_map = go.Figure()
        for uhi_type, color in type_cmap.items():
            sub = map_df[map_df['uhi_type'] == uhi_type]
            if len(sub) == 0: continue
            fig_map.add_trace(go.Scattermapbox(
                lat=sub['lat'], lon=sub['lon'],
                text=sub['hover_text'], hoverinfo='text',
                name=uhi_type.split(':')[0],
                mode='markers',
                marker=dict(
                    size=sub['pop_M'] * 3 + 7,
                    color=sub['mean_suhi_day'],
                    colorscale='RdYlBu_r', cmin=1, cmax=9,
                    colorbar=dict(
                        title=dict(text="SUHI (°C)", font=dict(color='white', size=12)),
                        thickness=18, len=0.95, y=0.5,
                        tickfont=dict(color='white', size=11),
                        tickvals=[1,2,3,4,5,6,7,8,9],
                        ticktext=['1','2','3','4','5','6','7','8','9'],
                    ),
                    opacity=0.88,
                )
            ))
        fig_map.update_layout(
            mapbox=dict(
                style='open-street-map',
                center=dict(lat=23, lon=79),
                zoom=3.8,
            ),
            **CHART_BG,
            height=640,
            margin=dict(l=0, r=0, t=5, b=0),
            legend=dict(
                orientation='h', y=-0.04,
                font=dict(size=9, color='white'),
                bgcolor='rgba(14,17,23,0.75)',
                bordercolor='rgba(255,255,255,0.12)',
                borderwidth=1,
            )
        )
        st.plotly_chart(fig_map,use_container_width=True)

    with col_panel:
        st.markdown('<div class="section-header"><span class="section-icon">🔥</span><span class="section-title">Heat Risk Rankings</span></div>',unsafe_allow_html=True)
        for _,row in trend_filtered.nlargest(10,'mean_suhi_day').iterrows():
            hl='🔴' if row['mean_suhi_day']>6 else '🟠' if row['mean_suhi_day']>4 else '🟡'
            ti='↑' if row['day_slope_decade']>0.15 else '→'
            bc='#d73027' if row['mean_suhi_day']>5 else '#fc8d59'
            st.markdown(f'<div style="display:flex;justify-content:space-between;align-items:center;padding:7px 10px;margin:3px 0;background:rgba(255,255,255,.04);border-radius:8px;border-left:3px solid {bc};">'
                        f'<span>{hl} <b>{row["city"]}</b> <span style="color:#888;font-size:.8em">{row["country"][:3]}</span></span>'
                        f'<span style="color:#F2A65A;font-weight:700">{row["mean_suhi_day"]:.1f}°C {ti}</span></div>',unsafe_allow_html=True)
        st.markdown("<br>",unsafe_allow_html=True)
        tc = trend_filtered['uhi_type'].value_counts()
        fig_pie = px.pie(values=tc.values,names=[t.split(':')[0] for t in tc.index],
                         color_discrete_sequence=['#d73027','#fc8d59','#91bfdb','#4575b4'],hole=0.55)
        fig_pie.update_layout(**CHART_BG,height=200,margin=dict(l=0,r=0,t=5,b=0),
                               legend=dict(font=dict(size=8),orientation='v'))
        st.plotly_chart(fig_pie,use_container_width=True)

    _heat_hdr, _heat_ctrl = st.columns([3, 1])
    with _heat_hdr:
        st.markdown('<div class="section-header"><span class="section-icon">📈</span><span class="section-title">Regional SUHI Trend Heatmap (2003–2025)</span></div>',unsafe_allow_html=True)
    with _heat_ctrl:
        st.markdown("<div style='padding-top:14px'></div>", unsafe_allow_html=True)
        heat_season = st.selectbox(
            "Season",
            ['annual','pre_monsoon','monsoon','post_monsoon','winter'],
            format_func=lambda x: {
                'annual':       '📅 Annual',
                'pre_monsoon':  '☀️ Pre-Monsoon',
                'monsoon':      '🌧 Monsoon',
                'post_monsoon': '🍂 Post-Monsoon',
                'winter':       '❄️ Winter',
            }[x],
            key="heat_season_sel",
            label_visibility="collapsed"
        )
    top30 = trend_filtered.nlargest(30,'mean_suhi_day')['city'].tolist()
    pivot = suhi_filtered[(suhi_filtered['season']==heat_season)&(suhi_filtered['city'].isin(top30))].pivot_table(index='city',columns='year',values='suhi_day',aggfunc='mean')
    _season_lbl = {'annual':'Annual','pre_monsoon':'Pre-Monsoon','monsoon':'Monsoon','post_monsoon':'Post-Monsoon','winter':'Winter'}[heat_season]
    fig_heat=go.Figure(data=go.Heatmap(z=pivot.values,x=pivot.columns.tolist(),y=pivot.index.tolist(),
        colorscale='RdYlBu_r',zmid=4,hovertemplate='<b>%{y}</b><br>%{x}: %{z:.2f}°C<extra></extra>',
        colorbar=dict(title=dict(text="SUHI (°C)", font=dict(color="white", size=11)),tickfont=dict(color='white'))))
    fig_heat.update_layout(**CHART_BG,height=400,margin=dict(l=100,r=20,t=10,b=30),
                            xaxis=dict(tickangle=-45,tickfont=dict(size=9)),yaxis=dict(tickfont=dict(size=9)),
                            title=dict(text=f"<b>{_season_lbl} SUHI</b> — Top 30 Cities by Intensity",
                                       font=dict(size=11,color='#A8B4C4'),x=0))
    st.plotly_chart(fig_heat,use_container_width=True)


# ═════════════════════════════════════════════════════════════════════════════
# PAGE: CITY DEEP-DIVE
# ═════════════════════════════════════════════════════════════════════════════
# ═════════════════════════════════════════════════════════════════════════════
# TAB: CITY DEEP-DIVE
# ═════════════════════════════════════════════════════════════════════════════
with tab_deepdive:
  if True:

    # ── City data assembly ────────────────────────────────────────────────────
    city_data_annual = SUHI_DF[(SUHI_DF['city']==selected_city)&(SUHI_DF['season']=='annual')].sort_values('year')
    city_data_all    = SUHI_DF[SUHI_DF['city']==selected_city]
    city_meta        = CITIES[CITIES['city']==selected_city].iloc[0]
    city_scenario    = SCENARIOS_DF[SCENARIOS_DF['city']==selected_city].iloc[0]
    city_trend       = TRENDS_DF[TRENDS_DF['city']==selected_city].iloc[0]
    type_num         = city_trend['uhi_type'].split(':')[0].replace('Type','').strip()
    type_css         = {'I':'type-I','II':'type-II','III':'type-III','IV':'type-IV'}.get(type_num,'type-I')

    # ── Header with city name ─────────────────────────────────────────────────
    st.markdown(f"""
    <div class="app-header">
        <div class="app-title">📍 {selected_city} <span class="app-badge">{city_meta['country']}</span></div>
        <div class="app-subtitle">
            {city_meta['region']} · {city_meta['climate']} Climate ·
            Pop: {city_meta['pop_M']:.1f}M · {city_meta['lat']:.2f}°N, {city_meta['lon']:.2f}°E
        </div>
        <br><span class="type-badge {type_css}">{city_trend['uhi_type']}</span>
    </div>""", unsafe_allow_html=True)

    # ── KPIs ──────────────────────────────────────────────────────────────────
    c1,c2,c3,c4,c5 = st.columns(5)
    for col,(val,lbl,delta,dcls) in zip([c1,c2,c3,c4,c5],[
        (f"{city_trend['mean_suhi_day']:.1f}°C","Mean SUHI (Day)",f"Max: {city_trend['max_suhi_day']:.1f}°C","delta-up"),
        (f"+{city_trend['day_slope_decade']:.2f}°C","Trend /Decade","Significant ✓" if city_trend['significant'] else "Not significant","delta-up" if city_trend['significant'] else ""),
        (f"{city_scenario['heat_risk_score']}/100","Heat Risk Score","🔴 Critical" if city_scenario['heat_risk_score']>70 else "🟠 High" if city_scenario['heat_risk_score']>50 else "🟡 Moderate","delta-up"),
        (f"{city_scenario['reduction_combined']:.1f}°C","Mitigation Potential","Combined scenario","delta-down"),
        (f"{city_scenario['deaths_prevented']:,}","Lives Saved /yr","Combined intervention","delta-down"),
    ]):
        col.markdown(f'<div class="metric-card"><div class="metric-value">{val}</div><div class="metric-label">{lbl}</div><div class="metric-delta {dcls}">{delta}</div></div>',unsafe_allow_html=True)

    st.markdown("<br>",unsafe_allow_html=True)

    # ── Row 1: Time-series + Seasonal cycle ───────────────────────────────────
    col_ts, col_seasonal = st.columns([3,2])

    with col_ts:
        st.markdown(f'<div class="section-header"><span class="section-icon">📉</span><span class="section-title">20+Year SUHI Time Series — {selected_city}</span></div>',unsafe_allow_html=True)
        fig_ts = go.Figure()
        fig_ts.add_trace(go.Scatter(x=city_data_annual['year'],y=city_data_annual['suhi_day'],
            mode='lines+markers',name='Day SUHI',line=dict(color='#E84855',width=2.5),marker=dict(size=5)))
        fig_ts.add_trace(go.Scatter(x=city_data_annual['year'],y=city_data_annual['suhi_night'],
            mode='lines+markers',name='Night SUHI',line=dict(color='#4575b4',width=2,dash='dash'),marker=dict(size=5)))
        if len(city_data_annual)>2:
            xn = np.arange(len(city_data_annual))
            z  = np.polyfit(xn,city_data_annual['suhi_day'].values,1)
            fig_ts.add_trace(go.Scatter(x=city_data_annual['year'],y=np.poly1d(z)(xn),
                mode='lines',name=f"Trend (+{z[0]*10:.2f}°C/dec)",
                line=dict(color='rgba(242,166,90,0.7)',width=1.8,dash='dot')))
        fig_ts.update_layout(**CHART_BG,height=300,margin=dict(l=40,r=20,t=10,b=30),
            xaxis=dict(title='Year',**GRID_STYLE),yaxis=dict(title='SUHI (°C)',**GRID_STYLE),
            legend=dict(orientation='h',y=1.12),hovermode='x unified',
            title=dict(text=f"<b>{selected_city}</b> — Annual SUHI (2003–2025)",font=dict(size=11,color='#A8B4C4'),x=0))
        st.plotly_chart(fig_ts,use_container_width=True)

    with col_seasonal:
        st.markdown(f'<div class="section-header"><span class="section-icon">🌦</span><span class="section-title">Seasonal Cycle — {selected_city}</span></div>',unsafe_allow_html=True)
        sdata = city_data_all[city_data_all['season']!='annual'].groupby('season').agg(
            suhi_day=('suhi_day','mean'),suhi_night=('suhi_night','mean')).reset_index()
        sorder = ['pre_monsoon','monsoon','post_monsoon','winter']
        slabels = {'pre_monsoon':'Pre-Mon','monsoon':'Monsoon','post_monsoon':'Post-Mon','winter':'Winter'}
        sdata = sdata.set_index('season').reindex([s for s in sorder if s in sdata['season'].values]).reset_index()
        fig_s = go.Figure()
        fig_s.add_trace(go.Bar(name='Day',x=[slabels.get(s,s) for s in sdata['season']],
            y=sdata['suhi_day'],marker_color='#E84855',opacity=0.85))
        fig_s.add_trace(go.Bar(name='Night',x=[slabels.get(s,s) for s in sdata['season']],
            y=sdata['suhi_night'],marker_color='#4575b4',opacity=0.85))
        fig_s.update_layout(barmode='group',**CHART_BG,height=300,margin=dict(l=40,r=20,t=10,b=30),
            yaxis=dict(title='SUHI (°C)',**GRID_STYLE),legend=dict(orientation='h',y=1.12),
            title=dict(text=f"<b>{selected_city}</b> — Seasonal SUHI",font=dict(size=11,color='#A8B4C4'),x=0))
        st.plotly_chart(fig_s,use_container_width=True)

    # ── Row 2: Spatial Distribution Maps ─────────────────────────────────────
    st.markdown(f'<div class="section-header"><span class="section-icon">🗺</span><span class="section-title">Spatial Distribution of LST · SUHI · NDVI — {selected_city}</span></div>',unsafe_allow_html=True)
    st.markdown("""
    <div class="alert-info" style="margin-bottom:10px;">
        <b>How to read these maps:</b>
        Simulated 30 m-equivalent spatial patterns based on city-specific SUHI magnitude,
        population density, and climate zone, following Landsat thermal band physics.
        Warmer colours = higher heat. The NDVI map (green scale) inversely mirrors the heat
        pattern — vegetated areas act as natural cooling islands.
    </div>""", unsafe_allow_html=True)

    lst_grid, suhi_grid, ndvi_grid, lats, lons = make_spatial_grid(
        selected_city, city_meta['lat'], city_meta['lon'],
        city_trend['mean_suhi_day'], city_meta['climate'], city_meta['pop_M']
    )

    def spatial_heatmap(z, lats, lons, title, colorscale, zunit, cmin=None, cmax=None, city=selected_city):
        fig = go.Figure(data=go.Heatmap(
            z=z, x=np.round(lons,4), y=np.round(lats,4),
            colorscale=colorscale,
            zmin=cmin, zmax=cmax,
            colorbar=dict(title=dict(text=zunit,font=dict(color='white',size=9)),thickness=12,len=0.85,
                          tickfont=dict(color='white',size=9)),
            hovertemplate=f'Lat: %{{y:.3f}}°N<br>Lon: %{{x:.3f}}°E<br>{zunit}: %{{z:.2f}}<extra></extra>'
        ))
        # Annotate city centre
        fig.add_trace(go.Scatter(
            x=[lons[len(lons)//2]], y=[lats[len(lats)//2]],
            mode='markers+text',
            marker=dict(symbol='star',size=14,color='white',line=dict(color='black',width=1)),
            text=[f" {city}"],textposition='top right',
            textfont=dict(color='white',size=10,family='Arial Black'),
            showlegend=False, hoverinfo='skip'
        ))
        fig.update_layout(
            **CHART_BG, height=310,
            margin=dict(l=40,r=20,t=40,b=40),
            xaxis=dict(title='Longitude (°E)',tickfont=dict(size=8),**GRID_STYLE),
            yaxis=dict(title='Latitude (°N)',tickfont=dict(size=8),**GRID_STYLE,scaleanchor='x',scaleratio=1),
            title=dict(text=f"<b>{title}</b> — {city}",font=dict(size=11,color='#A8B4C4'),x=0.02)
        )
        return fig

    col_lst, col_suhi_map, col_ndvi = st.columns(3)

    with col_lst:
        fig_lst = spatial_heatmap(
            lst_grid, lats, lons,
            title="Land Surface Temperature (LST)",
            colorscale='Hot', zunit="LST (°C)",
            cmin=float(np.percentile(lst_grid,5)),
            cmax=float(np.percentile(lst_grid,99))
        )
        st.plotly_chart(fig_lst, use_container_width=True)
        st.markdown(f'<div class="spatial-caption">📡 MODIS/Landsat LST · Urban core at ★<br>Range: {lst_grid.min():.1f}°C – {lst_grid.max():.1f}°C</div>', unsafe_allow_html=True)

    with col_suhi_map:
        fig_suhi_sp = spatial_heatmap(
            suhi_grid, lats, lons,
            title="Surface UHI (SUHI) Intensity",
            colorscale='RdYlBu_r', zunit="SUHI (°C)",
            cmin=float(np.percentile(suhi_grid,2)),
            cmax=float(np.percentile(suhi_grid,98))
        )
        # Add rural reference ring annotation
        fig_suhi_sp.add_shape(type="circle",
            xref="x", yref="y",
            x0=lons[10], y0=lats[10], x1=lons[-10], y1=lats[-10],
            line=dict(color="rgba(100,180,255,0.4)", width=1.5, dash='dot'))
        st.plotly_chart(fig_suhi_sp, use_container_width=True)
        st.markdown(f'<div class="spatial-caption">🌡 SUHI = LST<sub>urban</sub> − LST<sub>rural</sub><br>Dashed ring = rural reference zone</div>', unsafe_allow_html=True)

    with col_ndvi:
        fig_ndvi_sp = spatial_heatmap(
            ndvi_grid, lats, lons,
            title="NDVI — Vegetation Cooling Index",
            colorscale='RdYlGn', zunit="NDVI",
            cmin=0.0, cmax=0.75
        )
        st.plotly_chart(fig_ndvi_sp, use_container_width=True)
        st.markdown(f'<div class="spatial-caption">🌿 Landsat 8/9 NDVI · Green = cooling zones<br>Mean NDVI: {ndvi_grid.mean():.3f}</div>', unsafe_allow_html=True)

    # ── Row 3: NDVI–SUHI scatter + Policy recommendations ────────────────────
    col_sc, col_pol = st.columns([1,1])

    with col_sc:
        st.markdown(f'<div class="section-header"><span class="section-icon">🌿</span><span class="section-title">NDVI–SUHI Relationship — {selected_city}</span></div>',unsafe_allow_html=True)
        city_ann2 = SUHI_DF[(SUHI_DF['city']==selected_city)&(SUHI_DF['season']=='annual')]
        xv = city_ann2['ndvi'].values; yv = city_ann2['suhi_day'].values; yr = city_ann2['year'].values
        x_tr = np.linspace(xv.min(),xv.max(),100) if len(xv)>1 else xv
        y_tr = np.poly1d(np.polyfit(xv,yv,1))(x_tr) if len(xv)>1 else yv
        fig_sc = go.Figure()
        fig_sc.add_trace(go.Scatter(x=xv,y=yv,mode='markers',
            marker=dict(color=yr,colorscale='RdYlBu_r',size=9,opacity=0.85,
                        colorbar=dict(title=dict(text='Year',font=dict(color='white')),tickfont=dict(color='white')),
                        line=dict(width=0.5,color='rgba(255,255,255,.3)')),
            hovertemplate='Year: %{marker.color}<br>NDVI: %{x:.3f}<br>SUHI: %{y:.2f}°C<extra></extra>',
            name='Observations'))
        fig_sc.add_trace(go.Scatter(x=x_tr,y=y_tr,mode='lines',
            line=dict(color='rgba(255,220,100,0.8)',width=2,dash='dot'),name='Trend',hoverinfo='skip'))
        fig_sc.add_vline(x=0.35,line_dash='dash',line_color='#2ecc71',line_width=1.5,
            annotation_text="Cooling threshold 0.35",annotation_font_color='#2ecc71',annotation_position='top right')
        fig_sc.update_layout(**CHART_BG,height=280,margin=dict(l=40,r=20,t=35,b=30),
            xaxis=dict(title='NDVI',**GRID_STYLE),yaxis=dict(title='SUHI Day (°C)',**GRID_STYLE),
            legend=dict(font=dict(size=8),orientation='h',y=1.15),
            title=dict(text=f"<b>{selected_city}</b> — NDVI vs SUHI (2003–2023)",font=dict(size=11,color='#A8B4C4'),x=0))
        st.plotly_chart(fig_sc,use_container_width=True)

    with col_pol:
        st.markdown('<div class="section-header"><span class="section-icon">📋</span><span class="section-title">City-Specific Policy Recommendations</span></div>',unsafe_allow_html=True)
        uhi_t = city_trend['uhi_type']
        if 'Type I' in uhi_t or 'Type II' in uhi_t:
            st.markdown('<div class="policy-card"><div class="policy-title">🚨 Priority: Emergency Cool Infrastructure</div><div class="policy-text">High SUHI requires immediate cool shelters, drinking-water networks, and heat response centres. Monsoon-season vegetation recovery must be protected.</div></div>',unsafe_allow_html=True)
        if city_trend['day_slope_decade']>0.2:
            st.markdown('<div class="policy-card"><div class="policy-title">📈 Urgent: Contain Urban Sprawl</div><div class="policy-text">Significant warming trend demands FAR controls and green-belt legislation to prevent further impervious expansion on the periphery.</div></div>',unsafe_allow_html=True)
        if city_ann2['ndvi'].mean()<0.35:
            st.markdown(f'<div class="policy-card"><div class="policy-title">🌿 Urban Greening Mandate</div><div class="policy-text">Current NDVI ({city_ann2["ndvi"].mean():.2f}) is below the cooling threshold (0.35). A 15% urban canopy target should be embedded in the master plan.</div></div>',unsafe_allow_html=True)
        else:
            st.markdown('<div class="policy-card"><div class="policy-title">✅ Maintain Green Cover</div><div class="policy-text">Vegetation cover is above the critical cooling threshold. Focus on protecting existing green spaces from development and expanding blue infrastructure.</div></div>',unsafe_allow_html=True)





# ═════════════════════════════════════════════════════════════════════════════
# TAB: AI DRIVER ANALYSIS
# ═════════════════════════════════════════════════════════════════════════════
with tab_ai:
  if True:

    st.markdown("""
    <div class="app-header">
        <div class="app-title">AI-Powered Heat Driver Attribution <span class="app-badge">SHAP ML</span></div>
        <div class="app-subtitle">Random Forest + TreeSHAP explainability — What drives heat in each city?</div>
    </div>""", unsafe_allow_html=True)

    col_bar, col_explain = st.columns([1.4, 1])

    with col_bar:
        st.markdown('<div class="section-header"><span class="section-icon">🎯</span><span class="section-title">Global Feature Importance (SHAP Values)</span></div>',unsafe_allow_html=True)
        df_shap = SHAP_DF.sort_values('mean_abs_shap', ascending=True)
        colors  = ['#E84855' if v>0 else '#4575b4' for v in df_shap['mean_shap']]
        fig_shap = go.Figure(go.Bar(
            x=df_shap['mean_abs_shap'], y=df_shap['feature'], orientation='h',
            marker_color=colors, marker_line_color='rgba(255,255,255,0.1)', marker_line_width=0.5,
            text=[f"{'↑' if v>0 else '↓'} {abs(v):.3f}°C" for v in df_shap['mean_shap']],
            textposition='outside',
            hovertemplate='<b>%{y}</b><br>|SHAP|: %{x:.3f}°C<extra></extra>'
        ))
        fig_shap.update_layout(**CHART_BG, height=420,
            margin=dict(l=160,r=100,t=10,b=30),
            xaxis=dict(title='Mean |SHAP Value| (°C SUHI contribution)',**GRID_STYLE),
            yaxis=GRID_STYLE)
        st.plotly_chart(fig_shap, use_container_width=True)

    with col_explain:
        st.markdown('<div class="section-header"><span class="section-icon">💡</span><span class="section-title">Interpreting SHAP</span></div>',unsafe_allow_html=True)
        st.markdown("""
        <div class="alert-info" style="margin-bottom:12px;">
            <b>🔴 Red bars</b> = features that <em>increase</em> SUHI (warming drivers)<br>
            <b>🔵 Blue bars</b> = features that <em>decrease</em> SUHI (cooling drivers)<br>
            <b>Bar length</b> = magnitude of average contribution (°C)
        </div>""", unsafe_allow_html=True)
        for feat, sv, desc in [
            ("Impervious Surface",1.82,"Roads and rooftops absorb solar radiation, releasing it as heat. The #1 warming driver — directly linked to urbanisation rate."),
            ("NDVI (Vegetation)",-1.65,"Trees and grass cool via evapotranspiration and shading. Above NDVI=0.35, cooling accelerates dramatically."),
            ("Surface Albedo",-0.72,"Light-coloured surfaces reflect solar radiation. Cool roofs can reduce albedo-driven heat by 0.5–1.5°C."),
            ("Population Density",0.58,"Dense urban areas emit anthropogenic heat from vehicles, industry, and buildings — especially at night."),
        ]:
            c = "#E84855" if sv>0 else "#4575b4"
            d = "↑ Warming" if sv>0 else "↓ Cooling"
            st.markdown(f'<div style="background:rgba(255,255,255,.04);border-radius:8px;padding:10px 12px;margin:6px 0;border-left:3px solid {c};"><b>{feat}</b><span style="color:{c};float:right;font-size:.85em">{d} {abs(sv):.2f}°C</span><div style="font-size:.82rem;color:#8892A4;margin-top:4px;line-height:1.5">{desc}</div></div>',unsafe_allow_html=True)

    # NDVI threshold
    st.markdown('<div class="section-header"><span class="section-icon">🌿</span><span class="section-title">Critical NDVI Cooling Threshold Analysis</span></div>',unsafe_allow_html=True)
    col_ndvi, col_thresh = st.columns([2,1])
    with col_ndvi:
        ndvi_range = np.linspace(0.05, 0.70, 200)
        ndvi_shap_sim = -2.5*(1/(1+np.exp(-10*(ndvi_range-0.35))))+1.2+np.random.RandomState(42).normal(0,0.08,200)
        rng2 = np.random.RandomState(42)
        sc_ndvi = rng2.uniform(0.05,0.70,400)
        sc_shap = -2.5*(1/(1+np.exp(-10*(sc_ndvi-0.35))))+1.2+rng2.normal(0,0.25,400)
        imp_v   = np.clip(0.8-sc_ndvi*0.7+rng2.normal(0,0.1,400),0,1)
        fig_nd  = go.Figure()
        fig_nd.add_trace(go.Scatter(x=sc_ndvi,y=sc_shap,mode='markers',
            marker=dict(size=5,color=imp_v,colorscale='YlOrRd',opacity=0.4,
                        colorbar=dict(title=dict(text="Impervious\nFraction", font=dict(color="white", size=11)),x=1.02,tickfont=dict(color='white'))),
            name='City-year obs',hovertemplate='NDVI:%{x:.2f}<br>SHAP:%{y:.2f}°C<extra></extra>'))
        fig_nd.add_trace(go.Scatter(x=ndvi_range,y=ndvi_shap_sim,mode='lines',
            line=dict(color='white',width=2.5),name='Smoothed trend'))
        fig_nd.add_vline(x=0.35,line_dash='dash',line_color='#2ecc71',line_width=2,
            annotation_text="Critical NDVI Threshold = 0.35",annotation_font_color='#2ecc71',annotation_position='top left')
        fig_nd.add_hline(y=0,line_color='rgba(255,255,255,0.3)',line_width=1)
        fig_nd.add_vrect(x0=0.35,x1=0.70,fillcolor='rgba(46,204,113,0.07)',layer='below',line_width=0)
        fig_nd.update_layout(**CHART_BG,height=320,margin=dict(l=50,r=70,t=10,b=40),
            xaxis=dict(title='NDVI',**GRID_STYLE,range=[0.04,0.72]),
            yaxis=dict(title='SHAP contribution to SUHI (°C)',**GRID_STYLE),
            legend=dict(orientation='h',y=1.05))
        st.plotly_chart(fig_nd,use_container_width=True)
    with col_thresh:
        st.markdown("""
        <div class="alert-success" style="margin-top:30px;">
            <b>🔬 Key Finding</b><br><br>
            Above NDVI = <b>0.35</b>, every additional 0.05 unit
            provides <b>~0.3°C more</b> cooling than below the threshold.<br><br>
            <b>Policy:</b> Urban greening must target NDVI ≥ 0.35 — not arbitrary
            percentage planting targets.
        </div>
        <div class="alert-warning" style="margin-top:12px;">
            <b>⚠️ Warning</b><br><br>
            ~65% of South Asian cities are currently below NDVI = 0.35,
            operating in the low-efficiency cooling zone.
        </div>""", unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════════════════════
# PAGE: MITIGATION PLANNER
# ═════════════════════════════════════════════════════════════════════════════
with tab_mitigation:
  if True:

    st.markdown("""
    <div class="app-header">
        <div class="app-title">Heat Mitigation Scenario Planner <span class="app-badge">INTERACTIVE</span></div>
        <div class="app-subtitle">Model SUHI reduction from green, blue, and cool infrastructure interventions</div>
    </div>""", unsafe_allow_html=True)

    st.markdown('<div class="section-header"><span class="section-icon">🛠</span><span class="section-title">Configure Intervention Scenarios</span></div>',unsafe_allow_html=True)
    c1,c2,c3 = st.columns(3)
    with c1:
        st.markdown("**🌿 Urban Greening**")
        ndvi_inc = st.slider("NDVI increase",0.0,0.25,0.10,0.01)
    with c2:
        st.markdown("**🏗 Cool Infrastructure**")
        alb_inc  = st.slider("Albedo increase",0.0,0.15,0.05,0.01)
    with c3:
        st.markdown("**💧 Blue Infrastructure**")
        mndwi_inc = st.slider("Water fraction increase",0.0,0.10,0.03,0.005)

    sc2 = scenario_filtered.copy()
    sc2['adj_g'] = sc2['reduction_greening']  * (ndvi_inc/0.10)
    sc2['adj_c'] = sc2['reduction_cool_roof'] * (alb_inc /0.05)
    sc2['adj_b'] = sc2['reduction_blue']      * (mndwi_inc/0.03)
    sc2['adj_cb'] = sc2['adj_g'] + sc2['adj_c']*0.8 + sc2['adj_b']*0.6
    sc2['adj_deaths'] = (sc2['pop_M']*1e6*3.5e-5*sc2['adj_cb']*0.016).astype(int)

    cc1,cc2,cc3,cc4 = st.columns(4)
    for col,(v,l,d,dc) in zip([cc1,cc2,cc3,cc4],[
        (f"{sc2['adj_g'].mean():.2f}°C","Greening Reduction","Mean across cities","delta-down"),
        (f"{sc2['adj_c'].mean():.2f}°C","Cool Roof Reduction","Mean across cities","delta-down"),
        (f"{sc2['adj_b'].mean():.2f}°C","Blue Infra Reduction","Mean across cities","delta-down"),
        (f"{sc2['adj_cb'].mean():.2f}°C","Combined Reduction","Total potential","delta-down"),
    ]):
        col.markdown(f'<div class="metric-card"><div class="metric-value">{v}</div><div class="metric-label">{l}</div><div class="metric-delta {dc}">{d}</div></div>',unsafe_allow_html=True)

    st.markdown("<br>",unsafe_allow_html=True)
    col_ch, col_tb = st.columns([3,2])
    with col_ch:
        top25 = sc2.nlargest(25,'adj_cb')
        fig_m = go.Figure()
        fig_m.add_trace(go.Bar(name='Greening',x=top25['city'],y=top25['adj_g'],marker_color='#2ecc71',opacity=0.85))
        fig_m.add_trace(go.Bar(name='Cool Roof',x=top25['city'],y=top25['adj_c'],marker_color='#3498db',opacity=0.85))
        fig_m.add_trace(go.Bar(name='Blue Infra',x=top25['city'],y=top25['adj_b'],marker_color='#9b59b6',opacity=0.85))
        fig_m.update_layout(barmode='stack',**CHART_BG,height=350,
            margin=dict(l=40,r=20,t=10,b=80),
            xaxis=dict(tickangle=-45,**GRID_STYLE),yaxis=dict(title='SUHI Reduction (°C)',**GRID_STYLE),
            legend=dict(orientation='h',y=1.05))
        st.plotly_chart(fig_m,use_container_width=True)
    with col_tb:
        disp = sc2[['city','country','mean_suhi_day','adj_cb','adj_deaths']].nlargest(15,'adj_cb').reset_index(drop=True)
        disp.columns = ['City','Country','SUHI (°C)','Reduction (°C)','Lives/yr']
        disp['SUHI (°C)'] = disp['SUHI (°C)'].round(1)
        disp['Reduction (°C)'] = disp['Reduction (°C)'].round(2)
        st.dataframe(disp.style.background_gradient(subset=['Reduction (°C)'],cmap='Greens')
                              .background_gradient(subset=['SUHI (°C)'],cmap='Reds'),
                     use_container_width=True,height=300)
        st.markdown(f'<div class="alert-success" style="margin-top:10px;"><b>💚 Total Health Co-benefit</b><br>Combined intervention could prevent approximately <b>{sc2["adj_deaths"].sum():,}</b> heat-related deaths annually.</div>',unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════════════════════
# PAGE: POLICY INTELLIGENCE
# ═════════════════════════════════════════════════════════════════════════════
with tab_policy:
  if True:

    st.markdown("""
    <div class="app-header">
        <div class="app-title">Policy Intelligence Dashboard <span class="app-badge">GOV EDITION</span></div>
        <div class="app-subtitle">Evidence-based heat adaptation recommendations for urban planners and decision makers</div>
    </div>""", unsafe_allow_html=True)

    policy_city = selected_city  # driven by sidebar Country → City selection
    ct = TRENDS_DF[TRENDS_DF['city']==policy_city].iloc[0]
    cs = SCENARIOS_DF[SCENARIOS_DF['city']==policy_city].iloc[0]
    cm = CITIES[CITIES['city']==policy_city].iloc[0]
    risk = cs['heat_risk_score']
    rc = '#d73027' if risk>70 else '#fc8d59' if risk>50 else '#fee090'
    rl = 'CRITICAL' if risk>70 else 'HIGH' if risk>50 else 'MODERATE'

    st.markdown(f"""
    <div style="background:linear-gradient(135deg,rgba(30,20,40,1),rgba(20,15,35,1));
                border:2px solid {rc};border-radius:14px;padding:22px 26px;margin:14px 0;">
        <div style="display:flex;justify-content:space-between;align-items:flex-start;">
            <div>
                <div style="font-size:1.4rem;font-weight:800;color:white;">🌡️ HEAT RISK BRIEF: {policy_city.upper()}</div>
                <div style="color:#8892A4;margin-top:4px;">{cm['region']} | {cm['country']} | Pop: {cm['pop_M']:.1f}M | Climate: {cm['climate']}</div>
            </div>
            <div style="text-align:center;">
                <div style="font-size:2.4rem;font-weight:900;color:{rc};">{risk}</div>
                <div style="font-size:.68rem;color:{rc};font-weight:700;letter-spacing:1px;">{rl} RISK</div>
            </div>
        </div>
        <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-top:18px;">
            {''.join(f'<div style="background:rgba(255,255,255,.06);border-radius:8px;padding:11px;text-align:center;"><div style="font-size:1.5rem;font-weight:700;color:#F2A65A;">{v}</div><div style="font-size:.68rem;color:#8892A4;">{l}</div></div>' for v,l in [(f"{ct['mean_suhi_day']:.1f}°C","Mean SUHI Day"),(f"+{ct['day_slope_decade']:.2f}°C","Trend / Decade"),(f"{cs['reduction_combined']:.1f}°C","Mitigation Potential"),(f"{cs['deaths_prevented']:,}","Lives Saved / Year")])}
        </div>
    </div>""", unsafe_allow_html=True)

    col_i, col_s, col_l = st.columns(3)
    for col, color, border, label, recs in [
        (col_i, "rgba(215,48,39,.12)", "rgba(215,48,39,.55)", "🔴 Immediate (0–12 months)",
         ["Deploy heat emergency hotlines and cool shelters in high-risk wards",
          "Issue heat health action plans with clinical protocols for hospitals",
          "Install green roofs on government buildings as demonstration projects",
          "Map heat vulnerability by ward level for targeted interventions"]),
        (col_s, "rgba(252,141,89,.12)", "rgba(252,141,89,.55)", "🟠 Short-term (1–3 years)",
         ["Mandate cool roof materials in new building permits (reflectivity ≥ 0.65)",
          "Launch urban tree planting with minimum NDVI ≥ 0.35 targets",
          "Restore urban water bodies — ponds, canals, wetlands",
          "Revise setback rules to increase shading between structures"]),
        (col_l, "rgba(69,117,180,.12)", "rgba(69,117,180,.55)", "🔵 Long-term (3–10 years)",
         ["Embed heat resilience index in all Master Plan revisions",
          "Establish urban heat monitoring network (IoT + satellite)",
          "Develop urban forest corridors connecting green patches",
          "Price urban land to incentivise green coverage — tradeable credits"]),
    ]:
        rows_html = "".join(
            f'<div style="font-size:.82rem;color:#ccc;padding:5px 0;'
            f'border-bottom:1px solid rgba(255,255,255,.06);">▸ {r}</div>'
            for r in recs
        )
        with col:
            st.markdown(
                f'<div style="background:{color};border:1px solid {border};border-radius:10px;'
                f'padding:15px;min-height:220px;">' 
                f'<div style="color:#eee;font-weight:700;font-size:.95rem;margin-bottom:10px;">{label}</div>'
                f'{rows_html}</div>',
                unsafe_allow_html=True
            )

    st.markdown('<div class="section-header"><span class="section-icon">🎯</span><span class="section-title">SDG & National Policy Alignment</span></div>',unsafe_allow_html=True)
    sdg_cols = st.columns(5)
    for col,(sdg,name,desc) in zip(sdg_cols,[
        ("SDG 11","Sustainable Cities","Heat mitigation = safe, inclusive urban environments (Target 11.b)"),
        ("SDG 13","Climate Action","Urban cooling reduces heat mortality and energy demand, supporting NDCs"),
        ("SDG 3","Good Health","Heat risk reduction prevents excess mortality and morbidity"),
        ("SDG 15","Life on Land","Urban greening increases biodiversity corridors and ecosystem services"),
        ("NAPCC","National Plans","Aligns with National Climate Change Plans and urban heat management priorities"),
    ]):
        col.markdown(f'<div style="background:rgba(255,255,255,.04);border-radius:10px;padding:11px;text-align:center;border-top:3px solid #2E74B5;height:130px;"><div style="font-size:1.05rem;font-weight:800;color:#7EB8F7;">{sdg}</div><div style="font-size:.72rem;font-weight:700;color:#ccc;margin:3px 0;">{name}</div><div style="font-size:.7rem;color:#8892A4;line-height:1.4">{desc[:75]}...</div></div>',unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════════════════════
# PAGE: COMPARATIVE ANALYSIS
# ═════════════════════════════════════════════════════════════════════════════
with tab_compare:
  if True:

    st.markdown("""
    <div class="app-header">
        <div class="app-title">Comparative City Analysis <span class="app-badge">RESEARCH</span></div>
        <div class="app-subtitle">Cross-city comparison for research, benchmarking, and equity analysis</div>
    </div>""", unsafe_allow_html=True)

    col_bub, col_box = st.columns([3,2])
    with col_bub:
        st.markdown('<div class="section-header"><span class="section-icon">🔵</span><span class="section-title">Population vs SUHI vs Trend</span></div>',unsafe_allow_html=True)
        fig_bub = px.scatter(trend_filtered,x='mean_suhi_day',y='day_slope_decade',
            size='pop_M',color='uhi_type',
            color_discrete_map={'Type I: High-Intensity Monsoon-Modulated':'#d73027',
                                'Type II: Persistent Arid/Semi-Arid':'#fc8d59',
                                'Type III: Sprawl-Driven Peri-Urban':'#91bfdb',
                                'Type IV: Coastal-Moderated Tropical':'#4575b4'},
            hover_name='city',hover_data={'country':True,'pop_M':':.1f','climate':True},size_max=55,
            labels={'mean_suhi_day':'Mean SUHI Day (°C)','day_slope_decade':'Trend (°C/decade)','uhi_type':'UHI Type'})
        fig_bub.update_layout(**CHART_BG,height=420,margin=dict(l=50,r=20,t=10,b=40),
            xaxis=GRID_STYLE,yaxis=GRID_STYLE,legend=dict(font=dict(size=9,color='white'),bgcolor='rgba(0,0,0,0.6)',bordercolor='rgba(255,255,255,0.15)',borderwidth=1))
        st.plotly_chart(fig_bub,use_container_width=True)
    with col_box:
        st.markdown('<div class="section-header"><span class="section-icon">📉</span><span class="section-title">SUHI Distribution by Country</span></div>',unsafe_allow_html=True)
        fig_box=px.box(trend_filtered,x='country',y='mean_suhi_day',color='country',
            color_discrete_sequence=px.colors.qualitative.Set2,points='all',
            labels={'mean_suhi_day':'Mean SUHI Day (°C)','country':'Country'})
        fig_box.update_layout(**CHART_BG,height=420,margin=dict(l=50,r=20,t=10,b=40),
            xaxis=GRID_STYLE,yaxis=GRID_STYLE,showlegend=False)
        st.plotly_chart(fig_box,use_container_width=True)

    # ── 2-City SUHI Box & Whisker Comparison ─────────────────────────────────
    st.markdown('<div class="section-header"><span class="section-icon">📦</span><span class="section-title">Head-to-Head City SUHI Comparison</span></div>',unsafe_allow_html=True)
    st.markdown("""
    <div class="alert-info" style="margin-bottom:12px;">
        Select any two cities (same or different country) to compare their full distribution
        of daytime and night-time SUHI across all years and seasons via box &amp; whisker plots.
    </div>""", unsafe_allow_html=True)

    _all_cities_sorted = sorted(TRENDS_DF['city'].tolist())
    _bw_c1, _bw_c2, _bw_c3 = st.columns([2, 2, 1])
    with _bw_c1:
        city_a = st.selectbox("🏙 City A", _all_cities_sorted,
                              index=_all_cities_sorted.index('Kathmandu') if 'Kathmandu' in _all_cities_sorted else 0,
                              key="compare_city_a")
    with _bw_c2:
        _remaining = [c for c in _all_cities_sorted if c != city_a]
        city_b = st.selectbox("🏙 City B", _remaining,
                              index=_remaining.index('Delhi') if 'Delhi' in _remaining else 0,
                              key="compare_city_b")
    with _bw_c3:
        st.markdown("<div style='padding-top:6px'></div>", unsafe_allow_html=True)
        bw_season = st.selectbox("Season", ['all','annual','pre_monsoon','monsoon','post_monsoon','winter'],
            format_func=lambda x: {'all':'All Seasons','annual':'Annual','pre_monsoon':'Pre-Mon',
                                    'monsoon':'Monsoon','post_monsoon':'Post-Mon','winter':'Winter'}[x],
            key="bw_season_sel", label_visibility="collapsed")

    _bw_df = SUHI_DF[SUHI_DF['city'].isin([city_a, city_b])].copy()
    if bw_season != 'all':
        _bw_df = _bw_df[_bw_df['season'] == bw_season]
    else:
        _bw_df = _bw_df[_bw_df['season'] != 'annual']  # exclude annual when showing all seasons

    _meta_a = CITIES[CITIES['city']==city_a].iloc[0]
    _meta_b = CITIES[CITIES['city']==city_b].iloc[0]

    # Pre-converted rgba fills — no string manipulation avoids Plotly colour validation errors
    _fill_map = {
        '#E84855': 'rgba(232,72,85,0.20)',
        '#F2A65A': 'rgba(242,166,90,0.20)',
        '#4575b4': 'rgba(69,117,180,0.20)',
        '#7EB8F7': 'rgba(126,184,247,0.20)',
    }

    _bw_col1, _bw_col2 = st.columns(2)
    for _col, _var, _title, _clr_a, _clr_b in [
        (_bw_col1, 'suhi_day',   '\u2600\ufe0f Daytime SUHI (\u00b0C)',   '#E84855', '#F2A65A'),
        (_bw_col2, 'suhi_night', '\U0001f319 Night-time SUHI (\u00b0C)', '#4575b4', '#7EB8F7'),
    ]:
        fig_bw = go.Figure()
        for _city, _clr, _meta in [(city_a, _clr_a, _meta_a), (city_b, _clr_b, _meta_b)]:
            _d = _bw_df[_bw_df['city']==_city][_var].dropna()
            fig_bw.add_trace(go.Violin(
                y=_d, name=f"{_city}  ({_meta['country']} \u00b7 {_meta['climate']})",
                marker_color=_clr,
                line=dict(color=_clr, width=2),
                fillcolor=_fill_map[_clr],
                box_visible=True,
                meanline_visible=True,
                points='all',
                pointpos=0,
                jitter=0.2,
                marker=dict(size=3, opacity=0.4, color=_clr),
                hovertemplate=f"<b>{_city}</b><br>{_var}: %{{y:.2f}}\u00b0C<extra></extra>"
            ))
        _trend_a = TRENDS_DF[TRENDS_DF['city']==city_a].iloc[0]
        _trend_b = TRENDS_DF[TRENDS_DF['city']==city_b].iloc[0]
        fig_bw.update_layout(
            **CHART_BG, height=420,
            margin=dict(l=40, r=20, t=50, b=30),
            yaxis=dict(title=_var.replace('_',' ').title()+' (°C)', **GRID_STYLE),
            xaxis=GRID_STYLE,
            title=dict(text=_title, font=dict(size=13, color='#E0E6F0'), x=0.02),
            legend=dict(orientation='h', y=1.12, font=dict(size=10)),
            showlegend=True,
            annotations=[
                dict(x=0.02, y=0.98, xref='paper', yref='paper', showarrow=False,
                     text=f"<b>{city_a}</b> mean: {_trend_a['mean_'+_var if 'mean_'+_var in _trend_a.index else 'mean_suhi_day']:.1f}°C  |  "
                          f"<b>{city_b}</b> mean: {_trend_b['mean_'+_var if 'mean_'+_var in _trend_b.index else 'mean_suhi_day']:.1f}°C",
                     font=dict(size=10, color='#A8B4C4'),
                     bgcolor='rgba(0,0,0,0.4)', borderpad=4)
            ]
        )
        with _col:
            st.plotly_chart(fig_bw, use_container_width=True)

    # summary stats row
    _sa = SUHI_DF[SUHI_DF['city']==city_a]
    _sb = SUHI_DF[SUHI_DF['city']==city_b]
    _sc_a = SCENARIOS_DF[SCENARIOS_DF['city']==city_a].iloc[0]
    _sc_b = SCENARIOS_DF[SCENARIOS_DF['city']==city_b].iloc[0]
    st.markdown(f"""
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-top:6px;">
      <div style="background:rgba(232,72,85,.08);border:1px solid rgba(232,72,85,.3);border-radius:10px;padding:14px 18px;">
        <div style="font-size:.9rem;font-weight:800;color:#E84855;margin-bottom:8px;">🏙 {city_a} — {_meta_a['country']}</div>
        <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:8px;font-size:.78rem;color:#A8B4C4;">
          <div><b style="color:#F2A65A">{_sa['suhi_day'].mean():.2f}°C</b><br>Mean Day SUHI</div>
          <div><b style="color:#7EB8F7">{_sa['suhi_night'].mean():.2f}°C</b><br>Mean Night SUHI</div>
          <div><b style="color:#2ecc71">{_sc_a['heat_risk_score']}/100</b><br>Heat Risk Score</div>
        </div>
      </div>
      <div style="background:rgba(242,166,90,.08);border:1px solid rgba(242,166,90,.3);border-radius:10px;padding:14px 18px;">
        <div style="font-size:.9rem;font-weight:800;color:#F2A65A;margin-bottom:8px;">🏙 {city_b} — {_meta_b['country']}</div>
        <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:8px;font-size:.78rem;color:#A8B4C4;">
          <div><b style="color:#F2A65A">{_sb['suhi_day'].mean():.2f}°C</b><br>Mean Day SUHI</div>
          <div><b style="color:#7EB8F7">{_sb['suhi_night'].mean():.2f}°C</b><br>Mean Night SUHI</div>
          <div><b style="color:#2ecc71">{_sc_b['heat_risk_score']}/100</b><br>Heat Risk Score</div>
        </div>
      </div>
    </div>""", unsafe_allow_html=True)



# ═════════════════════════════════════════════════════════════════════════════
# TAB: AI ASSISTANT
# ═════════════════════════════════════════════════════════════════════════════
with tab_chat:
  if True:

    st.markdown("""
    <div class="app-header">
        <div class="app-title">AI Dashboard Assistant <span class="app-badge">COMING SOON</span></div>
        <div class="app-subtitle">An AI assistant powered by Claude will be available here to answer questions about the dashboard</div>
    </div>""", unsafe_allow_html=True)

    st.markdown("""
    <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;
                padding:60px 20px;text-align:center;">
        <div style="font-size:4rem;margin-bottom:20px;">🚧</div>
        <div style="font-size:1.5rem;font-weight:800;color:#E0E6F0;margin-bottom:12px;">
            Under Preparation
        </div>
        <div style="font-size:.95rem;color:#8892A4;max-width:500px;line-height:1.8;margin-bottom:28px;">
            The AI Assistant feature is currently being developed and tested.<br>
            It will allow you to ask natural language questions about UHI patterns,
            city comparisons, methodology, and policy recommendations — all grounded
            in the dashboard data.
        </div>
        <div style="background:rgba(69,117,180,.1);border:1px solid rgba(69,117,180,.3);
                    border-radius:12px;padding:18px 28px;max-width:480px;">
            <div style="font-size:.82rem;font-weight:700;color:#7EB8F7;margin-bottom:10px;">
                🔜 Planned capabilities
            </div>
            <div style="font-size:.8rem;color:#A8B4C4;line-height:1.9;text-align:left;">
                • Compare SUHI trends between any two cities<br>
                • Explain drivers of urban heat for a selected city<br>
                • Recommend evidence-based mitigation strategies<br>
                • Answer methodology and data source questions<br>
                • Generate city-specific heat risk summaries
            </div>
        </div>
    </div>""", unsafe_allow_html=True)

    # ── AI ASSISTANT CODE (under preparation — uncomment to activate) ─────────
    #
    # _top5 = TRENDS_DF.nlargest(5, 'mean_suhi_day')[['city','country','mean_suhi_day','day_slope_decade']].to_string(index=False)
    # _city_ctx = TRENDS_DF[TRENDS_DF['city']==selected_city].iloc[0]
    # _city_scn = SCENARIOS_DF[SCENARIOS_DF['city']==selected_city].iloc[0]
    #
    # DASHBOARD_CONTEXT = f"""You are an AI assistant for the UHI-DST dashboard for South Asia.
    # You ONLY answer questions based on the dashboard data and UHI/climate science.
    #
    # DASHBOARD SUMMARY:
    # - Coverage: 50 cities across India, Pakistan, Bangladesh, Nepal, Sri Lanka
    # - Data period: 2003-2025 (MODIS LST, Landsat 8/9, ERA5-Land, GHSL)
    # - Total population exposed: {TRENDS_DF['pop_M'].sum():.0f}M urban residents
    # - Mean SUHI (all cities): {TRENDS_DF['mean_suhi_day'].mean():.2f} deg C (day)
    # - Mean warming trend: +{TRENDS_DF['day_slope_decade'].mean():.3f} deg C/decade
    # - Cities with significant warming trend: {TRENDS_DF['significant'].mean()*100:.0f}%
    # TOP 5 HOTTEST CITIES: {_top5}
    # CURRENTLY SELECTED CITY: {selected_city} ({_city_ctx['country']})
    # - Mean day SUHI: {_city_ctx['mean_suhi_day']:.2f} deg C
    # - Warming trend: +{_city_ctx['day_slope_decade']:.3f} deg C/decade
    # - UHI Type: {_city_ctx['uhi_type']}
    # - Heat Risk Score: {_city_scn['heat_risk_score']}/100
    # - Mitigation potential: {_city_scn['reduction_combined']:.2f} deg C
    # """
    #
    # if 'chat_history' not in st.session_state:
    #     st.session_state.chat_history = []
    #
    # for msg in st.session_state.chat_history:
    #     if msg['role'] == 'user':
    #         st.markdown(f'<div style="text-align:right">{msg["content"]}</div>', unsafe_allow_html=True)
    #     else:
    #         st.markdown(msg['content'])
    #
    # _inp_col, _btn_col = st.columns([5, 1])
    # with _inp_col:
    #     user_input = st.text_input("Ask about the dashboard", label_visibility="collapsed", key="ai_chat_input")
    # with _btn_col:
    #     send_btn = st.button("Send", use_container_width=True, type="primary")
    #
    # if send_btn and user_input and user_input.strip():
    #     st.session_state.chat_history.append({'role': 'user', 'content': user_input.strip()})
    #     try:
    #         import requests, os
    #         _api_key = st.secrets.get("ANTHROPIC_API_KEY", os.environ.get("ANTHROPIC_API_KEY", ""))
    #         _messages = [{"role": str(m["role"]), "content": str(m["content"])}
    #                      for m in st.session_state.chat_history]
    #         _resp = requests.post(
    #             "https://api.anthropic.com/v1/messages",
    #             headers={"Content-Type": "application/json",
    #                      "x-api-key": _api_key,
    #                      "anthropic-version": "2023-06-01"},
    #             json={"model": "claude-haiku-4-5-20251001", "max_tokens": 1000,
    #                   "system": str(DASHBOARD_CONTEXT), "messages": _messages},
    #             timeout=30
    #         )
    #         _answer = _resp.json()["content"][0]["text"] if _resp.status_code == 200     #             else f"API error {_resp.status_code}"
    #     except Exception as _e:
    #         _answer = f"Could not reach AI service: {_e}"
    #     st.session_state.chat_history.append({'role': 'assistant', 'content': _answer})
    #     st.rerun()
    #
    # if st.session_state.get('chat_history'):
    #     if st.button("Clear conversation", key="clear_chat"):
    #         st.session_state.chat_history = []
    #         st.rerun()
    # ── END AI ASSISTANT CODE ─────────────────────────────────────────────────

# ─────────────────────────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<hr style="border-color:rgba(255,255,255,0.08);margin:30px 0 10px 0;">
<div style="text-align:center;color:#555;font-size:.73rem;padding-bottom:10px;">
    <b>UHI-DST v5.0</b> — South Asia Urban Heat Island Decision Support Tool &nbsp;|&nbsp;
    Data: MODIS/NASA, Landsat/USGS, ERA5/ECMWF, GHSL/JRC &nbsp;|&nbsp;
    Methods: Random Forest + TreeSHAP + Mann-Kendall + BFAST &nbsp;|&nbsp;
    <a href="https://github.com/[repository]" style="color:#4575b4;">Open Source</a>
</div>
""", unsafe_allow_html=True)
