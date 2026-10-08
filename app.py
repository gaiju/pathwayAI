# v61 — readable research cards and compact study methods
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import re
import math
import json
import os
import html
import sqlite3
import time
import hashlib
import hmac
import ipaddress
import zipfile
import urllib.request
import urllib.error
from io import BytesIO
from pathlib import Path
from urllib.parse import quote_plus, urlencode


def show_tick_identification_guide():
    """Low-burden educational visual to help users distinguish a possible tick from common look-alikes."""
    st.markdown("### 🕷️ Found a possible tick?")
    st.write(
        'Compare its appearance with the guide. Appearance alone cannot show whether it carries an infection.'
    )
    c1, c2 = st.columns([1.15, 1])
    with c1:
        st.markdown("**Blacklegged tick — quick visual guide**")
        st.markdown(
            """
            **Adult / nymph:** 8 legs • no wings • no antennae • compact oval body  
            **Larva:** 6 legs (important exception) • very small  
            **After feeding:** the body can become much larger and rounder
            """
        )
        st.caption(
            'Young ticks can be very small and easy to miss.'
        )
    with c2:
        st.markdown("**Common look-alikes**")
        st.markdown(
            """
            **Beetle:** 6 legs + antennae; often visible wing covers  
            **Spider:** 8 legs, but usually a more visibly divided body shape  
            **Flea:** 6 legs; enlarged hind legs; can jump
            """
        )
    st.info(
        'Unsure? Save clear photos of the top and underside and ask TickSpotters for identification.'
    )
    st.markdown("[Ask URI TickSpotters to help identify a tick](https://web.uri.edu/tickencounter/tickspotters/)")
    st.caption("External tick identification service; no photo is uploaded by PathwayAI. Identification does not establish whether you have an infection.")
    with st.expander("Why life stage matters"):
        st.write(
            "Ticks change substantially in size and appearance across larva, nymph, and adult stages. "
            "CDC describes larvae as six-legged and nymphs/adults as eight-legged."
        )
        st.markdown("[CDC: Tick lifecycles](https://www.cdc.gov/ticks/about/tick-lifecycles.html)")
        st.markdown("[CDC: Where ticks live / identification context](https://www.cdc.gov/ticks/about/where-ticks-live.html)")


def show_section_hero(kind, title, subtitle):
    """Self-contained visual hero: calm, fast, and deployment-safe."""
    palettes = {
        "travel": ("#eef8f2", "#245b45", "🌲  ✈️  🥾", "Plan ahead • prevent exposure • know what to do next"),
        "journey": ("#f4f3fb", "#51467a", "👩‍💻  📝  🤝", "Organize the story • prepare for care • be heard"),
        "policy": ("#eef4f8", "#244a63", "🗺️  ▥  📊", "Local burden • hidden burden • action"),
    }
    bg, fg, icons, strap = palettes[kind]
    html = f"""<div style='background:{bg};border:1px solid {fg}22;border-radius:18px;padding:22px 24px;margin:4px 0 18px 0;'>
    <div style='font-size:29px;letter-spacing:6px;float:right;opacity:.88'>{icons}</div>
    <div style='font-size:24px;font-weight:750;color:{fg};overflow-wrap:break-word'>{title}</div>
    <div style='font-size:16px;margin-top:6px;color:#263238;max-width:100%'>{subtitle}</div>
    <div style='font-size:12px;margin-top:13px;color:{fg};font-weight:650;letter-spacing:.25px'>{strap}</div>
    <div style='clear:both'></div></div>"""
    st.markdown(html, unsafe_allow_html=True)

st.set_page_config(
    page_title="PathwayAI",
    page_icon="🧭",
    layout="wide"
)

# Readable presentation tables: escape all cell text and wrap complete sentences.
def show_readable_table(data, **kwargs):
    frame = data if isinstance(data, pd.DataFrame) else pd.DataFrame(data)
    table = frame.to_html(index=not kwargs.get("hide_index", True), escape=True, border=0, classes="pathway-readable-table")
    st.markdown('<div class="pathway-table-wrap">' + table + '</div>', unsafe_allow_html=True)

st.markdown("""<style>
.pathway-table-wrap {width:100%; overflow-x:auto; margin:0.6rem 0 1rem;}
.pathway-readable-table {width:100%; border-collapse:collapse; table-layout:auto; font-size:0.95rem;}
.pathway-readable-table th, .pathway-readable-table td {white-space:normal !important; overflow-wrap:anywhere; text-overflow:clip; padding:0.7rem 0.8rem; border-bottom:1px solid #d4dbe3; text-align:left; vertical-align:top; min-width:110px; max-width:420px; line-height:1.5;}
.pathway-readable-table th {background:rgba(125,145,165,0.12); font-weight:650;}
[data-testid="stMetricValue"] {white-space:normal !important; overflow:visible !important; text-overflow:clip !important; font-size:1.7rem !important;}
[data-testid="stMetricLabel"] p {white-space:normal !important; overflow:visible !important; text-overflow:clip !important;}
[data-testid="stHeading"] h1, [data-testid="stHeading"] h2, [data-testid="stHeading"] h3 {overflow-wrap:break-word;}
</style>""", unsafe_allow_html=True)

# -----------------------------
# V43 CONTROLLED PILOT ACCESS
# -----------------------------
def _secret(name, default=""):
    """Read Streamlit secret first, then environment variable; never hard-code credentials."""
    try:
        value = st.secrets.get(name, default)
    except Exception:
        value = default
    return str(value or os.getenv(name, default) or "").strip()

PILOT_PASSWORD = _secret("PATHWAYAI_PILOT_PASSWORD")
ADMIN_PASSWORD = _secret("PATHWAYAI_ADMIN_PASSWORD")
def positive_config_integer(name, default):
    try:
        value = int(_secret(name, str(default)))
        return value if value > 0 else default
    except (ValueError, TypeError, OverflowError):
        return default

MAX_STORY_CHARS = positive_config_integer("PATHWAYAI_MAX_STORY_CHARS", 5000)
MAX_AI_CALLS_PER_SESSION = positive_config_integer("PATHWAYAI_MAX_AI_CALLS_PER_SESSION", 5)
OPENAI_API_KEY = _secret("OPENAI_API_KEY")
PATHWAYAI_LLM_MODEL = _secret("PATHWAYAI_LLM_MODEL")

AI_WINDOW_SECONDS = 30 * 60
AI_WINDOW_MAX_REQUESTS = 3

class AIRateLimitError(RuntimeError):
    pass

def _ai_bucket():
    # Use the framework connection address; do not trust arbitrary forwarded headers.
    try:
        raw = st.context.ip_address
        address = str(ipaddress.ip_address(raw)) if raw else "unidentified-connection"
    except (AttributeError, ValueError, TypeError):
        address = "unidentified-connection"
    # Store a keyed digest, never the raw IP. Unknown connections share one bucket.
    return hmac.new(OPENAI_API_KEY.encode(), address.encode(), hashlib.sha256).hexdigest()

def _ai_quota(db_path, bucket, consume=False, now=None):
    """Atomic sliding-window reservation across sessions/processes on this server."""
    now = time.time() if now is None else now
    with sqlite3.connect(str(db_path), timeout=10) as db:
        db.execute("CREATE TABLE IF NOT EXISTS ai_requests (bucket TEXT, requested REAL)")
        db.execute("CREATE INDEX IF NOT EXISTS ai_bucket_time ON ai_requests(bucket, requested)")
        db.execute("BEGIN IMMEDIATE")
        db.execute("DELETE FROM ai_requests WHERE requested <= ?", (now - AI_WINDOW_SECONDS,))
        count, oldest = db.execute("SELECT COUNT(*), MIN(requested) FROM ai_requests WHERE bucket=?", (bucket,)).fetchone()
        if count >= AI_WINDOW_MAX_REQUESTS:
            wait_minutes = max(1, math.ceil((oldest + AI_WINDOW_SECONDS - now) / 60))
            return False, f"You’ve reached the AI request limit (3 requests in 30 minutes). Please try again in about {wait_minutes} minute(s). Other PathwayAI features remain available."
        if consume:
            db.execute("INSERT INTO ai_requests VALUES (?, ?)", (bucket, now))
        return True, ""

def ai_call_allowed(kind="AI"):
    try:
        return _ai_quota(Path(__file__).resolve().parent / ".pathwayai_ai_limits.sqlite3", _ai_bucket())
    except (sqlite3.Error, OSError):
        return False, "AI usage tracking is temporarily unavailable. Please try again later; other features remain available."

def _limited_ai_urlopen(request, timeout=60):
    try:
        allowed, message = _ai_quota(Path(__file__).resolve().parent / ".pathwayai_ai_limits.sqlite3", _ai_bucket(), consume=True)
    except (sqlite3.Error, OSError):
        raise AIRateLimitError("AI usage tracking is unavailable. No API request was sent.")
    if not allowed:
        raise AIRateLimitError(message)
    # Reserve before sending: failed requests also consume quota. No automatic retries.
    return urllib.request.urlopen(request, timeout=timeout)

def record_completed_ai_call():
    # Compatibility with existing UI: quota is reserved per HTTP request above.
    pass


BASE_DIR = Path(__file__).resolve().parent

DATA_FILE = BASE_DIR / "pathwayAI_data.xlsx"

NY_TICK_FILE = BASE_DIR / "ny_tick_data.csv"

POPULATION_FILE = BASE_DIR / "pathwayai_population_data.csv"
CDC_TICK_FILE = BASE_DIR / "cdc_ixodes_county_2025.xlsx"
CDC_LYME_FILE = BASE_DIR / "cdc_tickborne_county_2019_2022.xlsx"
AHRF_ZIP_FILE = BASE_DIR / "AHRF_2024-2025_CSV.zip"
PLACES_FILE = BASE_DIR / "PLACES__Local_Data_for_Better_Health,_County_Data,_2025_release_20261005.csv"


# Checked NYSDOH snapshot and county drawing boundaries: no network needed for the map.
NYS_TICK_SNAPSHOT = json.loads('{"year":2025,"retrieved":"2026-10-07","source":"https://health.data.ny.gov/resource/kibp-u2ip.json","records":[{"year":"2025","county":"Albany","nymphal_density":"38.6","b_burgdorferi":"25.00"},{"year":"2025","county":"Allegany","nymphal_density":"15.6","b_burgdorferi":"24.00"},{"year":"2025","county":"Cattaraugus","nymphal_density":"30.03","b_burgdorferi":"31.600"},{"year":"2025","county":"Chautauqua","nymphal_density":"0","b_burgdorferi":null},{"year":"2025","county":"Chemung","nymphal_density":"51.2","b_burgdorferi":"14.00"},{"year":"2025","county":"Chenango","nymphal_density":"5.7","b_burgdorferi":"11.100"},{"year":"2025","county":"Clinton","nymphal_density":"13.94","b_burgdorferi":"16.200"},{"year":"2025","county":"Columbia","nymphal_density":"54.83","b_burgdorferi":"30.00"},{"year":"2025","county":"Cortland","nymphal_density":"32.5","b_burgdorferi":"32.00"},{"year":"2025","county":"Delaware","nymphal_density":"45","b_burgdorferi":"28.800"},{"year":"2025","county":"Dutchess","nymphal_density":"88.88","b_burgdorferi":"43.100"},{"year":"2025","county":"Erie","nymphal_density":"39.57","b_burgdorferi":"25.500"},{"year":"2025","county":"Essex","nymphal_density":"9.2","b_burgdorferi":"30.00"},{"year":"2025","county":"Franklin","nymphal_density":"15.1","b_burgdorferi":"30.00"},{"year":"2025","county":"Fulton","nymphal_density":"8.97","b_burgdorferi":"25.400"},{"year":"2025","county":"Genesee","nymphal_density":"26.8","b_burgdorferi":"24.00"},{"year":"2025","county":"Greene","nymphal_density":"29.42","b_burgdorferi":"25.500"},{"year":"2025","county":"Hamilton","nymphal_density":"1.38","b_burgdorferi":"16.700"},{"year":"2025","county":"Herkimer","nymphal_density":"7.7","b_burgdorferi":"22.700"},{"year":"2025","county":"Jefferson","nymphal_density":"1.2","b_burgdorferi":null},{"year":"2025","county":"Livingston","nymphal_density":"64.8","b_burgdorferi":"24.00"},{"year":"2025","county":"Monroe","nymphal_density":"22.23","b_burgdorferi":"25.700"},{"year":"2025","county":"Montgomery","nymphal_density":"18.55","b_burgdorferi":"22.400"},{"year":"2025","county":"Nassau","nymphal_density":"11.2","b_burgdorferi":"38.500"},{"year":"2025","county":"Niagara","nymphal_density":"17.33","b_burgdorferi":"24.00"},{"year":"2025","county":"Oneida","nymphal_density":"92.05","b_burgdorferi":"16.00"},{"year":"2025","county":"Onondaga","nymphal_density":"14.3","b_burgdorferi":"43.100"},{"year":"2025","county":"Ontario","nymphal_density":"22.17","b_burgdorferi":"21.600"},{"year":"2025","county":"Orange","nymphal_density":"301.5","b_burgdorferi":"29.400"},{"year":"2025","county":"Orleans","nymphal_density":"67.95","b_burgdorferi":"42.00"},{"year":"2025","county":"Oswego","nymphal_density":"14.45","b_burgdorferi":"24.600"},{"year":"2025","county":"Otsego","nymphal_density":"25.87","b_burgdorferi":"38.600"},{"year":"2025","county":"Putnam","nymphal_density":"19.68","b_burgdorferi":"17.300"},{"year":"2025","county":"Rensselaer","nymphal_density":"27","b_burgdorferi":"20.500"},{"year":"2025","county":"Rockland","nymphal_density":"6.3","b_burgdorferi":"15.700"},{"year":"2025","county":"Saratoga","nymphal_density":"20.75","b_burgdorferi":"19.500"},{"year":"2025","county":"Schenectady","nymphal_density":"45.63","b_burgdorferi":"20.200"},{"year":"2025","county":"Schoharie","nymphal_density":"26.5","b_burgdorferi":"20.400"},{"year":"2025","county":"Schuyler","nymphal_density":"54.4","b_burgdorferi":"14.00"},{"year":"2025","county":"Seneca","nymphal_density":"15.5","b_burgdorferi":"38.00"},{"year":"2025","county":"Steuben","nymphal_density":"4.15","b_burgdorferi":"36.400"},{"year":"2025","county":"Suffolk","nymphal_density":"61.04","b_burgdorferi":"26.600"},{"year":"2025","county":"Sullivan","nymphal_density":"39.93","b_burgdorferi":"10.400"},{"year":"2025","county":"Tioga","nymphal_density":"61.3","b_burgdorferi":"52.00"},{"year":"2025","county":"Tompkins","nymphal_density":"26.8","b_burgdorferi":"54.00"},{"year":"2025","county":"Ulster","nymphal_density":"33.9","b_burgdorferi":"22.00"},{"year":"2025","county":"Warren","nymphal_density":"9.3","b_burgdorferi":"12.300"},{"year":"2025","county":"Washington","nymphal_density":"14.96","b_burgdorferi":"21.00"},{"year":"2025","county":"Wayne","nymphal_density":"12.93","b_burgdorferi":"34.00"},{"year":"2025","county":"Westchester","nymphal_density":"37.35","b_burgdorferi":"36.900"},{"year":"2025","county":"Wyoming","nymphal_density":"84.2","b_burgdorferi":"20.00"},{"year":"2025","county":"Yates","nymphal_density":"19","b_burgdorferi":"20.00"}]}')
NYS_MAP_BOUNDARIES = json.loads('{"type":"FeatureCollection","features":[{"type":"Feature","properties":{"GEO_ID":"0500000US36003","STATE":"36","COUNTY":"003","NAME":"Allegany","LSAD":"County","CENSUSAREA":1029.308},"geometry":{"type":"Polygon","coordinates":[[[-78.206606,41.999989],[-78.308128,41.999415],[-78.308839,42.521217],[-78.040241,42.520968],[-78.038261,42.521522],[-77.840901,42.517767],[-77.840231,42.474576],[-77.722964,42.471216],[-77.749931,41.998782],[-77.822799,41.998547],[-77.83203,41.998524],[-78.030963,41.999392],[-78.031177,41.999415],[-78.12473,42.000452],[-78.206606,41.999989]]]},"id":"36003"},{"type":"Feature","properties":{"GEO_ID":"0500000US36021","STATE":"36","COUNTY":"021","NAME":"Columbia","LSAD":"County","CENSUSAREA":634.705},"geometry":{"type":"Polygon","coordinates":[[[-73.929626,42.078778],[-73.921465,42.110025],[-73.910675,42.127293],[-73.789502,42.267738],[-73.783721,42.464231],[-73.352527,42.510002],[-73.410647,42.351738],[-73.508142,42.086257],[-73.496879,42.049675],[-73.527072,41.97798],[-73.71093,42.005488],[-73.929626,42.078778]]]},"id":"36021"},{"type":"Feature","properties":{"GEO_ID":"0500000US36037","STATE":"36","COUNTY":"037","NAME":"Genesee","LSAD":"County","CENSUSAREA":492.936},"geometry":{"type":"Polygon","coordinates":[[[-78.464381,42.867461],[-78.463887,42.924325],[-78.464449,43.088703],[-78.464306,43.091514],[-78.465505,43.128619],[-78.410876,43.130643],[-77.99729,43.132981],[-77.905934,43.133561],[-77.951044,43.039544],[-77.909832,42.987762],[-77.954964,42.862754],[-78.464381,42.867461]]]},"id":"36037"},{"type":"Feature","properties":{"GEO_ID":"0500000US36043","STATE":"36","COUNTY":"043","NAME":"Herkimer","LSAD":"County","CENSUSAREA":1411.47},"geometry":{"type":"Polygon","coordinates":[[[-75.212158,42.879973],[-75.219106,43.052469],[-75.069165,43.227333],[-75.16035,43.255805],[-75.076581,43.330705],[-75.086851,43.41701],[-75.11016,43.615229],[-75.170159,44.096959],[-75.062779,44.0504],[-74.854171,44.070089],[-74.775617,43.486677],[-74.867712,43.339826],[-74.712615,43.286143],[-74.696333,43.173515],[-74.759895,43.047423],[-74.763303,42.863237],[-74.878822,42.898274],[-74.906738,42.824943],[-75.100999,42.908363],[-75.13987,42.85976],[-75.212158,42.879973]]]},"id":"36043"},{"type":"Feature","properties":{"GEO_ID":"0500000US36057","STATE":"36","COUNTY":"057","NAME":"Montgomery","LSAD":"County","CENSUSAREA":403.043},"geometry":{"type":"Polygon","coordinates":[[[-74.289304,42.984415],[-74.097467,42.982934],[-74.093814,42.959378],[-74.09298,42.955868],[-74.083883,42.897354],[-74.263314,42.796534],[-74.454911,42.772979],[-74.648298,42.829558],[-74.650213,42.829941],[-74.702054,42.845305],[-74.763303,42.863237],[-74.759895,43.047423],[-74.542367,42.98553],[-74.488844,42.985118],[-74.289304,42.984415]]]},"id":"36057"},{"type":"Feature","properties":{"GEO_ID":"0500000US36069","STATE":"36","COUNTY":"069","NAME":"Ontario","LSAD":"County","CENSUSAREA":644.065},"geometry":{"type":"Polygon","coordinates":[[[-76.971392,42.764223],[-77.018626,42.7638],[-77.313004,42.761265],[-77.367106,42.667866],[-77.366505,42.576368],[-77.490889,42.577288],[-77.486875,42.670279],[-77.598815,42.671965],[-77.61167,42.763169],[-77.580377,42.943963],[-77.482517,42.943164],[-77.485418,43.034564],[-77.371478,43.034696],[-77.134335,43.039926],[-77.133397,43.012463],[-76.963926,43.013157],[-76.96335,42.90302],[-76.971392,42.764223]]]},"id":"36069"},{"type":"Feature","properties":{"GEO_ID":"0500000US36083","STATE":"36","COUNTY":"083","NAME":"Rensselaer","LSAD":"County","CENSUSAREA":652.431},"geometry":{"type":"Polygon","coordinates":[[[-73.659663,42.818978],[-73.68461,42.892399],[-73.635463,42.94129],[-73.274294,42.943652],[-73.274393,42.942482],[-73.274466,42.940361],[-73.278673,42.83341],[-73.285388,42.834093],[-73.290944,42.80192],[-73.276421,42.746019],[-73.264957,42.74594],[-73.307004,42.632653],[-73.352527,42.510002],[-73.783721,42.464231],[-73.784594,42.489947],[-73.773161,42.509377],[-73.761265,42.610379],[-73.676762,42.783277],[-73.673463,42.790276],[-73.672355,42.795791],[-73.661362,42.802977],[-73.659663,42.818978]]]},"id":"36083"},{"type":"Feature","properties":{"GEO_ID":"0500000US36095","STATE":"36","COUNTY":"095","NAME":"Schoharie","LSAD":"County","CENSUSAREA":621.819},"geometry":{"type":"Polygon","coordinates":[[[-74.443506,42.355017],[-74.618895,42.424389],[-74.71158,42.517799],[-74.630631,42.626674],[-74.667512,42.75071],[-74.648298,42.829558],[-74.454911,42.772979],[-74.263314,42.796534],[-74.272295,42.71427],[-74.180274,42.729979],[-74.169725,42.667426],[-74.241572,42.550802],[-74.254303,42.408207],[-74.244692,42.377159],[-74.443506,42.355017]]]},"id":"36095"},{"type":"Feature","properties":{"GEO_ID":"0500000US36109","STATE":"36","COUNTY":"109","NAME":"Tompkins","LSAD":"County","CENSUSAREA":474.649},"geometry":{"type":"Polygon","coordinates":[[[-76.253359,42.407568],[-76.250149,42.296676],[-76.39465,42.318509],[-76.415305,42.318368],[-76.416199,42.262976],[-76.538349,42.281755],[-76.561601,42.281986],[-76.619303,42.282853],[-76.691406,42.284307],[-76.696655,42.54679],[-76.585989,42.54991],[-76.666543,42.623457],[-76.265584,42.623588],[-76.253359,42.407568]]]},"id":"36109"},{"type":"Feature","properties":{"GEO_ID":"0500000US36121","STATE":"36","COUNTY":"121","NAME":"Wyoming","LSAD":"County","CENSUSAREA":592.746},"geometry":{"type":"Polygon","coordinates":[[[-78.46394,42.536332],[-78.464381,42.867461],[-77.954964,42.862754],[-77.956334,42.667322],[-78.048247,42.579306],[-78.038261,42.521522],[-78.040241,42.520968],[-78.308839,42.521217],[-78.464556,42.519166],[-78.46394,42.536332]]]},"id":"36121"},{"type":"Feature","properties":{"GEO_ID":"0500000US36123","STATE":"36","COUNTY":"123","NAME":"Yates","LSAD":"County","CENSUSAREA":338.143},"geometry":{"type":"Polygon","coordinates":[[[-77.366505,42.576368],[-77.367106,42.667866],[-77.313004,42.761265],[-77.018626,42.7638],[-76.971392,42.764223],[-76.895349,42.656255],[-76.895596,42.541537],[-76.889805,42.463054],[-77.107203,42.483771],[-77.143795,42.576869],[-77.366505,42.576368]]]},"id":"36123"},{"type":"Feature","properties":{"GEO_ID":"0500000US36007","STATE":"36","COUNTY":"007","NAME":"Broome","LSAD":"County","CENSUSAREA":705.766},"geometry":{"type":"Polygon","coordinates":[[[-75.359579,41.999445],[-75.431961,41.999363],[-75.436216,41.999353],[-75.477144,41.999407],[-75.48315,41.999259],[-75.483738,41.999244],[-75.98025,41.999035],[-75.983082,41.999035],[-76.10584,41.998858],[-76.111106,42.112436],[-76.114033,42.153418],[-76.081134,42.230495],[-76.130181,42.410337],[-75.86402,42.415702],[-75.843792,42.259707],[-75.638299,42.248686],[-75.63711,42.195628],[-75.532776,42.195241],[-75.419907,42.194918],[-75.418421,42.195032],[-75.418544,42.189504],[-75.418807,42.188104],[-75.418689,42.188022],[-75.418438,42.186797],[-75.418827,42.180702],[-75.419664,42.150436],[-75.421776,42.04203],[-75.359579,41.999445]]]},"id":"36007"},{"type":"Feature","properties":{"GEO_ID":"0500000US36011","STATE":"36","COUNTY":"011","NAME":"Cayuga","LSAD":"County","CENSUSAREA":691.582},"geometry":{"type":"Polygon","coordinates":[[[-76.479224,43.227519],[-76.499312,43.097949],[-76.462999,43.006316],[-76.450738,42.84576],[-76.356974,42.84945],[-76.274673,42.771257],[-76.265584,42.623588],[-76.666543,42.623457],[-76.733454,42.727895],[-76.73674,42.970286],[-76.713806,43.024035],[-76.705345,43.125463],[-76.722501,43.343686],[-76.69836,43.344436],[-76.684856,43.352691],[-76.669624,43.366526],[-76.642672,43.401241],[-76.630774,43.413356],[-76.617109,43.419137],[-76.605012,43.25357],[-76.479224,43.227519]]]},"id":"36011"},{"type":"Feature","properties":{"GEO_ID":"0500000US36013","STATE":"36","COUNTY":"013","NAME":"Chautauqua","LSAD":"County","CENSUSAREA":1060.226},"geometry":{"type":"Polygon","coordinates":[[[-79.610839,41.998989],[-79.625301,41.999068],[-79.625287,41.999003],[-79.761374,41.999067],[-79.762122,42.131246],[-79.761861,42.150712],[-79.761759,42.162675],[-79.761921,42.173319],[-79.761929,42.179693],[-79.761833,42.183627],[-79.762152,42.243054],[-79.761964,42.251354],[-79.761951,42.26986],[-79.717825,42.284711],[-79.645358,42.315631],[-79.593992,42.341641],[-79.546262,42.363417],[-79.510999,42.382373],[-79.474794,42.404291],[-79.453533,42.411157],[-79.429119,42.42838],[-79.405458,42.453281],[-79.381943,42.466491],[-79.36213,42.480195],[-79.351989,42.48892],[-79.342316,42.489664],[-79.335129,42.488321],[-79.331483,42.489076],[-79.323079,42.494795],[-79.31774,42.499884],[-79.283364,42.511228],[-79.264624,42.523159],[-79.242889,42.531757],[-79.223195,42.536087],[-79.193232,42.545881],[-79.148723,42.553672],[-79.138569,42.564462],[-79.136725,42.569693],[-79.060777,42.537853],[-79.061265,41.999259],[-79.538445,41.998527],[-79.551385,41.998666],[-79.610839,41.998989]]]},"id":"36013"},{"type":"Feature","properties":{"GEO_ID":"0500000US36019","STATE":"36","COUNTY":"019","NAME":"Clinton","LSAD":"County","CENSUSAREA":1037.852},"geometry":{"type":"Polygon","coordinates":[[[-73.909687,44.429699],[-73.966148,44.709118],[-73.986382,44.707773],[-74.027392,44.995765],[-73.874597,45.001223],[-73.624588,45.003954],[-73.343124,45.01084],[-73.350188,44.994304],[-73.35945,44.915684],[-73.369647,44.829136],[-73.339958,44.778893],[-73.365326,44.703294],[-73.390231,44.618353],[-73.374389,44.575455],[-73.361952,44.563064],[-73.356788,44.557918],[-73.338634,44.546847],[-73.463838,44.537681],[-73.496604,44.486081],[-73.700717,44.445571],[-73.909687,44.429699]]]},"id":"36019"},{"type":"Feature","properties":{"GEO_ID":"0500000US36027","STATE":"36","COUNTY":"027","NAME":"Dutchess","LSAD":"County","CENSUSAREA":795.63},"geometry":{"type":"Polygon","coordinates":[[[-73.953307,41.589977],[-73.947382,41.667493],[-73.942482,41.684093],[-73.943482,41.690293],[-73.945782,41.695593],[-73.946682,41.699396],[-73.944435,41.714634],[-73.941081,41.732693],[-73.941081,41.735993],[-73.962221,41.90102],[-73.929626,42.078778],[-73.71093,42.005488],[-73.527072,41.97798],[-73.496879,42.049675],[-73.487314,42.049638],[-73.504944,41.824285],[-73.505008,41.823773],[-73.510171,41.758686],[-73.517473,41.666646],[-73.521457,41.616429],[-73.530067,41.527194],[-73.933775,41.488279],[-73.981486,41.438905],[-74.000108,41.456549],[-73.997609,41.487212],[-73.953307,41.589977]]]},"id":"36027"},{"type":"Feature","properties":{"GEO_ID":"0500000US36033","STATE":"36","COUNTY":"033","NAME":"Franklin","LSAD":"County","CENSUSAREA":1629.119},"geometry":{"type":"Polygon","coordinates":[[[-74.09349,44.137615],[-74.28187,44.120552],[-74.535156,44.09925],[-74.525683,44.170636],[-74.641872,44.952621],[-74.720307,44.953011],[-74.72498,45.005915],[-74.702018,45.003322],[-74.291307,44.992058],[-74.146814,44.9915],[-74.027392,44.995765],[-73.986382,44.707773],[-73.966148,44.709118],[-73.909687,44.429699],[-74.141424,44.407268],[-74.12756,44.330211],[-74.09349,44.137615]]]},"id":"36033"},{"type":"Feature","properties":{"GEO_ID":"0500000US36035","STATE":"36","COUNTY":"035","NAME":"Fulton","LSAD":"County","CENSUSAREA":495.469},"geometry":{"type":"Polygon","coordinates":[[[-74.097467,42.982934],[-74.289304,42.984415],[-74.488844,42.985118],[-74.542367,42.98553],[-74.759895,43.047423],[-74.696333,43.173515],[-74.712615,43.286143],[-74.534657,43.228115],[-74.326378,43.241635],[-74.220902,43.221403],[-74.140147,43.253979],[-74.097467,42.982934]]]},"id":"36035"},{"type":"Feature","properties":{"GEO_ID":"0500000US36039","STATE":"36","COUNTY":"039","NAME":"Greene","LSAD":"County","CENSUSAREA":647.161},"geometry":{"type":"Polygon","coordinates":[[[-74.451713,42.169225],[-74.53731,42.201424],[-74.443506,42.355017],[-74.244692,42.377159],[-74.254303,42.408207],[-73.783721,42.464231],[-73.789502,42.267738],[-73.910675,42.127293],[-74.042393,42.170386],[-74.074797,42.096589],[-74.307571,42.114346],[-74.451713,42.169225]]]},"id":"36039"},{"type":"Feature","properties":{"GEO_ID":"0500000US36041","STATE":"36","COUNTY":"041","NAME":"Hamilton","LSAD":"County","CENSUSAREA":1717.373},"geometry":{"type":"Polygon","coordinates":[[[-74.535156,44.09925],[-74.28187,44.120552],[-74.255998,43.969797],[-74.336826,43.925223],[-74.213734,43.810875],[-74.047062,43.796343],[-74.057005,43.744513],[-74.214625,43.728703],[-74.1601,43.371532],[-74.140147,43.253979],[-74.220902,43.221403],[-74.326378,43.241635],[-74.534657,43.228115],[-74.712615,43.286143],[-74.867712,43.339826],[-74.775617,43.486677],[-74.854171,44.070089],[-74.535156,44.09925]]]},"id":"36041"},{"type":"Feature","properties":{"GEO_ID":"0500000US36045","STATE":"36","COUNTY":"045","NAME":"Jefferson","LSAD":"County","CENSUSAREA":1268.59},"geometry":{"type":"Polygon","coordinates":[[[-76.355679,44.133258],[-76.312647,44.199044],[-76.286547,44.203773],[-76.245487,44.203669],[-76.206777,44.214543],[-76.191328,44.221244],[-76.164265,44.239603],[-76.118136,44.29485],[-76.045228,44.331724],[-76.000998,44.347534],[-75.978281,44.34688],[-75.970185,44.342835],[-75.94954,44.349129],[-75.912985,44.368084],[-75.871496,44.394839],[-75.86006,44.403282],[-75.446124,44.217655],[-75.545886,44.102978],[-75.484528,44.074172],[-75.542898,43.967795],[-75.60367,43.971363],[-75.758157,43.878785],[-75.84056,43.883976],[-75.850534,43.791886],[-75.786759,43.78832],[-75.774553,43.688884],[-76.025087,43.707018],[-76.022003,43.668143],[-76.2005,43.680231],[-76.205436,43.718751],[-76.213205,43.753513],[-76.229268,43.804135],[-76.250135,43.825713],[-76.266977,43.838046],[-76.277812,43.841205],[-76.283307,43.843923],[-76.284481,43.850968],[-76.28272,43.858601],[-76.276262,43.863297],[-76.269217,43.868581],[-76.261584,43.873278],[-76.249842,43.875626],[-76.243384,43.877975],[-76.234578,43.877388],[-76.227485,43.875061],[-76.219313,43.86682],[-76.202257,43.864898],[-76.192777,43.869175],[-76.180604,43.877529],[-76.158249,43.887542],[-76.145506,43.888681],[-76.133267,43.892975],[-76.127285,43.897889],[-76.125023,43.912773],[-76.130446,43.933082],[-76.133697,43.940356],[-76.134359,43.945614],[-76.134296,43.954726],[-76.139086,43.962111],[-76.146072,43.964705],[-76.169802,43.962202],[-76.184874,43.971128],[-76.22805,43.982737],[-76.236864,43.9779],[-76.244439,43.975803],[-76.252318,43.975803],[-76.258306,43.976118],[-76.264294,43.978009],[-76.268706,43.980846],[-76.268702,43.987278],[-76.266733,43.995578],[-76.269672,44.001148],[-76.281928,44.009177],[-76.287821,44.01142],[-76.296755,44.013307],[-76.298962,44.017719],[-76.300222,44.022762],[-76.299592,44.030956],[-76.296986,44.045455],[-76.300532,44.057188],[-76.304207,44.059445],[-76.360306,44.070907],[-76.360798,44.087644],[-76.366972,44.100409],[-76.363835,44.111696],[-76.358163,44.123337],[-76.355679,44.133258]]]},"id":"36045"},{"type":"Feature","properties":{"GEO_ID":"0500000US36051","STATE":"36","COUNTY":"051","NAME":"Livingston","LSAD":"County","CENSUSAREA":631.763},"geometry":{"type":"Polygon","coordinates":[[[-77.909832,42.987762],[-77.730957,42.988372],[-77.732378,42.945285],[-77.580377,42.943963],[-77.61167,42.763169],[-77.598815,42.671965],[-77.486875,42.670279],[-77.490889,42.577288],[-77.659917,42.580409],[-77.722964,42.471216],[-77.840231,42.474576],[-77.840901,42.517767],[-78.038261,42.521522],[-78.048247,42.579306],[-77.956334,42.667322],[-77.954964,42.862754],[-77.909832,42.987762]]]},"id":"36051"},{"type":"Feature","properties":{"GEO_ID":"0500000US36055","STATE":"36","COUNTY":"055","NAME":"Monroe","LSAD":"County","CENSUSAREA":657.205},"geometry":{"type":"Polygon","coordinates":[[[-77.995591,43.365293],[-77.994838,43.365259],[-77.976438,43.369159],[-77.965238,43.368059],[-77.952937,43.36346],[-77.922736,43.35696],[-77.904836,43.35696],[-77.875335,43.34966],[-77.816533,43.34356],[-77.797381,43.339857],[-77.785132,43.339261],[-77.760231,43.341161],[-77.756931,43.337361],[-77.73063,43.330161],[-77.714129,43.323561],[-77.701429,43.308261],[-77.660359,43.282998],[-77.653759,43.279484],[-77.628315,43.271303],[-77.602161,43.256949],[-77.577223,43.243263],[-77.551022,43.235763],[-77.534184,43.234569],[-77.50092,43.250363],[-77.476642,43.254522],[-77.436831,43.265701],[-77.414516,43.269263],[-77.391015,43.276363],[-77.385388,43.276847],[-77.376038,43.277652],[-77.374351,43.152584],[-77.371478,43.034696],[-77.485418,43.034564],[-77.482517,42.943164],[-77.580377,42.943963],[-77.732378,42.945285],[-77.730957,42.988372],[-77.909832,42.987762],[-77.951044,43.039544],[-77.905934,43.133561],[-77.99729,43.132981],[-77.995723,43.284963],[-77.995665,43.287448],[-77.995591,43.365293]]]},"id":"36055"},{"type":"Feature","properties":{"GEO_ID":"0500000US36059","STATE":"36","COUNTY":"059","NAME":"Nassau","LSAD":"County","CENSUSAREA":284.716},"geometry":{"type":"Polygon","coordinates":[[[-73.754323,40.586357],[-73.700582,40.743184],[-73.700872,40.746866],[-73.701744,40.75253],[-73.74676,40.780382],[-73.768431,40.800704],[-73.768301,40.800797],[-73.754032,40.820941],[-73.7544,40.826837],[-73.728275,40.8529],[-73.726675,40.8568],[-73.730675,40.8654],[-73.729575,40.8665],[-73.713674,40.870099],[-73.675573,40.856999],[-73.670692,40.858708],[-73.655872,40.863899],[-73.654372,40.878199],[-73.641072,40.892599],[-73.633771,40.898198],[-73.626972,40.899397],[-73.617571,40.897898],[-73.60187,40.902798],[-73.59517,40.907298],[-73.569969,40.915398],[-73.566169,40.915798],[-73.548068,40.908698],[-73.519267,40.914298],[-73.514999,40.912821],[-73.499941,40.918166],[-73.497061,40.922801],[-73.454172,40.834097],[-73.440967,40.764399],[-73.424758,40.679052],[-73.423269,40.670893],[-73.424618,40.666272],[-73.425586,40.656291],[-73.423806,40.609869],[-73.450369,40.603501],[-73.562372,40.583703],[-73.583773,40.586703],[-73.610873,40.587703],[-73.646674,40.582804],[-73.701138,40.58361],[-73.754776,40.584404],[-73.754323,40.586357]]]},"id":"36059"},{"type":"Feature","properties":{"GEO_ID":"0500000US36063","STATE":"36","COUNTY":"063","NAME":"Niagara","LSAD":"County","CENSUSAREA":522.359},"geometry":{"type":"Polygon","coordinates":[[[-78.828805,43.030139],[-78.945262,43.066956],[-79.009664,43.069558],[-79.028353,43.066897],[-79.028653,43.069474],[-79.058399,43.075231],[-79.066269,43.09097],[-79.056767,43.126855],[-79.044066,43.138055],[-79.042366,43.143655],[-79.058399,43.238924],[-79.070469,43.262454],[-79.019848,43.273686],[-78.971866,43.281254],[-78.930764,43.293254],[-78.859362,43.310955],[-78.836261,43.318455],[-78.834061,43.317555],[-78.777759,43.327055],[-78.747158,43.334555],[-78.696856,43.341255],[-78.634346,43.357624],[-78.547395,43.369541],[-78.488857,43.374763],[-78.482526,43.374425],[-78.473099,43.370812],[-78.465502,43.371232],[-78.466429,43.302775],[-78.460416,43.216222],[-78.465505,43.128619],[-78.464306,43.091514],[-78.464449,43.088703],[-78.733606,43.084219],[-78.828805,43.030139]]]},"id":"36063"},{"type":"Feature","properties":{"GEO_ID":"0500000US36071","STATE":"36","COUNTY":"071","NAME":"Orange","LSAD":"County","CENSUSAREA":811.686},"geometry":{"type":"Polygon","coordinates":[[[-73.953307,41.589977],[-73.997609,41.487212],[-74.000108,41.456549],[-73.981486,41.438905],[-73.981384,41.324693],[-74.161789,41.195794],[-74.234473,41.142883],[-74.365664,41.2034],[-74.392098,41.215594],[-74.457584,41.248225],[-74.694914,41.357423],[-74.689767,41.361558],[-74.691129,41.367324],[-74.752562,41.426518],[-74.75595,41.426804],[-74.752399,41.493743],[-74.475591,41.504334],[-74.367055,41.590977],[-74.264093,41.632738],[-74.126393,41.582544],[-73.953307,41.589977]]]},"id":"36071"},{"type":"Feature","properties":{"GEO_ID":"0500000US36073","STATE":"36","COUNTY":"073","NAME":"Orleans","LSAD":"County","CENSUSAREA":391.259},"geometry":{"type":"Polygon","coordinates":[[[-77.995665,43.287448],[-77.995723,43.284963],[-77.99729,43.132981],[-78.410876,43.130643],[-78.465505,43.128619],[-78.460416,43.216222],[-78.466429,43.302775],[-78.465502,43.371232],[-78.370221,43.376505],[-78.358711,43.373988],[-78.250641,43.370866],[-78.233609,43.36907],[-78.145195,43.37551],[-78.104509,43.375628],[-78.023609,43.366575],[-77.995591,43.365293],[-77.995665,43.287448]]]},"id":"36073"},{"type":"Feature","properties":{"GEO_ID":"0500000US36075","STATE":"36","COUNTY":"075","NAME":"Oswego","LSAD":"County","CENSUSAREA":951.65},"geometry":{"type":"Polygon","coordinates":[[[-76.479224,43.227519],[-76.605012,43.25357],[-76.617109,43.419137],[-76.607093,43.423374],[-76.562826,43.448537],[-76.53181,43.460299],[-76.521999,43.468617],[-76.515882,43.471136],[-76.506858,43.469127],[-76.486962,43.47535],[-76.472498,43.492781],[-76.437473,43.509213],[-76.417581,43.521285],[-76.410636,43.523159],[-76.368849,43.525822],[-76.345492,43.513437],[-76.330911,43.511978],[-76.297103,43.51287],[-76.259858,43.524728],[-76.235834,43.529256],[-76.228701,43.532987],[-76.217958,43.545156],[-76.209853,43.560136],[-76.203473,43.574978],[-76.199138,43.600454],[-76.196596,43.649761],[-76.2005,43.680231],[-76.022003,43.668143],[-76.025087,43.707018],[-75.774553,43.688884],[-75.756213,43.470388],[-75.814627,43.483578],[-75.886756,43.325021],[-75.884275,43.155562],[-75.927453,43.162738],[-75.932778,43.176583],[-75.955599,43.172182],[-75.959359,43.180389],[-75.973438,43.179898],[-75.979489,43.177401],[-75.986894,43.183938],[-75.992428,43.185164],[-75.993394,43.183376],[-76.202944,43.271605],[-76.258951,43.237468],[-76.479224,43.227519]]]},"id":"36075"},{"type":"Feature","properties":{"GEO_ID":"0500000US36081","STATE":"36","COUNTY":"081","NAME":"Queens","LSAD":"County","CENSUSAREA":108.532},"geometry":{"type":"Polygon","coordinates":[[[-73.868917,40.69515],[-73.874021,40.694191],[-73.889575,40.68418],[-73.896497,40.682447],[-73.904425,40.695671],[-73.912058,40.703446],[-73.921473,40.709004],[-73.923865,40.720056],[-73.929223,40.727849],[-73.937339,40.72992],[-73.947064,40.737516],[-73.954732,40.739292],[-73.961188,40.737091],[-73.962795,40.737674],[-73.961544,40.743081],[-73.9583,40.745731],[-73.95492,40.751509],[-73.943951,40.764434],[-73.940844,40.767399],[-73.936536,40.769835],[-73.93519,40.771745],[-73.938076,40.772551],[-73.938399,40.774606],[-73.93508,40.779218],[-73.92797,40.776762],[-73.916316,40.786601],[-73.910551,40.790988],[-73.912506,40.79618],[-73.899809,40.792524],[-73.892205,40.79038],[-73.890586,40.790145],[-73.889918,40.787398],[-73.884867,40.786621],[-73.870992,40.786979],[-73.866707,40.793653],[-73.862704,40.797276],[-73.830548,40.803162],[-73.811001,40.805077],[-73.793403,40.799881],[-73.785964,40.800862],[-73.781369,40.794907],[-73.776032,40.795275],[-73.768431,40.800704],[-73.74676,40.780382],[-73.701744,40.75253],[-73.700872,40.746866],[-73.700582,40.743184],[-73.754323,40.586357],[-73.753349,40.59056],[-73.774928,40.590759],[-73.80143,40.585659],[-73.806834,40.584619],[-73.834408,40.577201],[-73.878906,40.560888],[-73.934512,40.545175],[-73.934466,40.555281],[-73.932729,40.560266],[-73.935686,40.564914],[-73.938598,40.566161],[-73.849852,40.588669],[-73.86049,40.654655],[-73.85566,40.663802],[-73.866027,40.681918],[-73.868917,40.69515]]]},"id":"36081"},{"type":"Feature","properties":{"GEO_ID":"0500000US36087","STATE":"36","COUNTY":"087","NAME":"Rockland","LSAD":"County","CENSUSAREA":173.55},"geometry":{"type":"Polygon","coordinates":[[[-73.947965,41.223101],[-73.931482,41.204994],[-73.909281,41.164395],[-73.895381,41.153995],[-73.88718,41.133095],[-73.89488,41.082396],[-73.8947,41.069937],[-73.88938,41.037597],[-73.893979,40.997197],[-73.90268,40.997297],[-73.91188,41.001297],[-74.041049,41.059086],[-74.041054,41.059088],[-74.092486,41.081896],[-74.096786,41.083796],[-74.213373,41.133828],[-74.234473,41.142883],[-74.161789,41.195794],[-73.981384,41.324693],[-73.982584,41.321693],[-73.947965,41.223101]]]},"id":"36087"},{"type":"Feature","properties":{"GEO_ID":"0500000US36089","STATE":"36","COUNTY":"089","NAME":"St. Lawrence","LSAD":"County","CENSUSAREA":2680.377},"geometry":{"type":"Polygon","coordinates":[[[-74.72498,45.005915],[-74.720307,44.953011],[-74.641872,44.952621],[-74.525683,44.170636],[-74.535156,44.09925],[-74.854171,44.070089],[-75.062779,44.0504],[-75.170159,44.096959],[-75.446124,44.217655],[-75.86006,44.403282],[-75.82083,44.432244],[-75.807778,44.471644],[-75.765495,44.516285],[-75.696586,44.567583],[-75.491201,44.712947],[-75.433124,44.750062],[-75.333744,44.806378],[-75.301975,44.826637],[-75.30763,44.836813],[-75.283136,44.849156],[-75.216486,44.877478],[-75.189313,44.883037],[-75.139868,44.896676],[-75.064826,44.929449],[-75.027125,44.946568],[-75.005155,44.958402],[-74.999655,44.965921],[-74.99927,44.971638],[-74.992756,44.977449],[-74.972463,44.983402],[-74.826578,45.01585],[-74.801625,45.014571],[-74.72498,45.005915]]]},"id":"36089"},{"type":"Feature","properties":{"GEO_ID":"0500000US36093","STATE":"36","COUNTY":"093","NAME":"Schenectady","LSAD":"County","CENSUSAREA":204.516},"geometry":{"type":"Polygon","coordinates":[[[-74.180274,42.729979],[-74.272295,42.71427],[-74.263314,42.796534],[-74.083883,42.897354],[-74.09298,42.955868],[-73.895938,42.851076],[-73.809369,42.778869],[-73.809603,42.775016],[-74.180274,42.729979]]]},"id":"36093"},{"type":"Feature","properties":{"GEO_ID":"0500000US36099","STATE":"36","COUNTY":"099","NAME":"Seneca","LSAD":"County","CENSUSAREA":323.705},"geometry":{"type":"Polygon","coordinates":[[[-76.96335,42.90302],[-76.963926,43.013157],[-76.713806,43.024035],[-76.73674,42.970286],[-76.733454,42.727895],[-76.666543,42.623457],[-76.585989,42.54991],[-76.696655,42.54679],[-76.895596,42.541537],[-76.895349,42.656255],[-76.971392,42.764223],[-76.96335,42.90302]]]},"id":"36099"},{"type":"Feature","properties":{"GEO_ID":"0500000US36103","STATE":"36","COUNTY":"103","NAME":"Suffolk","LSAD":"County","CENSUSAREA":912.051},"geometry":{"type":"MultiPolygon","coordinates":[[[[-72.132225,41.104387],[-72.128352,41.108131],[-72.126704,41.115139],[-72.084207,41.101524],[-72.081167,41.09394],[-72.086975,41.058292],[-72.095711,41.05402],[-72.0972,41.054884],[-72.097136,41.075844],[-72.103152,41.086484],[-72.1064,41.088883],[-72.12056,41.093171],[-72.139233,41.092451],[-72.141921,41.094371],[-72.142929,41.097811],[-72.140737,41.100835],[-72.132225,41.104387]]],[[[-71.943563,41.286675],[-71.926802,41.290122],[-71.935259,41.280579],[-71.94627,41.276306],[-71.962598,41.270968],[-71.978926,41.265002],[-71.994717,41.256451],[-72.002461,41.252867],[-72.036846,41.249794],[-72.034958,41.255458],[-72.029438,41.26309],[-72.023422,41.270994],[-72.018926,41.274114],[-72.006872,41.27348],[-71.991117,41.281331],[-71.980061,41.280291],[-71.952864,41.285098],[-71.943563,41.286675]]],[[[-73.454172,40.834097],[-73.497061,40.922801],[-73.496642,40.923476],[-73.491765,40.942097],[-73.485365,40.946397],[-73.484798,40.946065],[-73.48011,40.943319],[-73.478365,40.942297],[-73.47441,40.941056],[-73.463708,40.937697],[-73.460603,40.937375],[-73.456523,40.936953],[-73.445026,40.935763],[-73.437509,40.934985],[-73.436664,40.934897],[-73.429863,40.929797],[-73.429665,40.928203],[-73.428836,40.921506],[-73.406074,40.920235],[-73.402963,40.925097],[-73.403462,40.942197],[-73.400862,40.953997],[-73.399762,40.955197],[-73.392862,40.955297],[-73.374462,40.937597],[-73.365961,40.931697],[-73.352761,40.926697],[-73.345561,40.925297],[-73.344161,40.927297],[-73.33136,40.929597],[-73.295061,40.924497],[-73.295059,40.924497],[-73.229285,40.905121],[-73.148994,40.928898],[-73.146242,40.935074],[-73.144673,40.955842],[-73.140785,40.966178],[-73.110368,40.971938],[-73.081582,40.973058],[-73.043701,40.962185],[-73.040445,40.964498],[-72.995931,40.966498],[-72.955163,40.966146],[-72.913834,40.962466],[-72.88825,40.962962],[-72.826057,40.969794],[-72.774104,40.965314],[-72.760031,40.975334],[-72.714425,40.985596],[-72.689341,40.989776],[-72.665018,40.987496],[-72.635374,40.990536],[-72.585327,40.997587],[-72.565406,41.009508],[-72.560974,41.015444],[-72.549853,41.019844],[-72.521548,41.037652],[-72.477306,41.052212],[-72.460778,41.067012],[-72.445242,41.086116],[-72.417945,41.087955],[-72.397,41.096307],[-72.356087,41.133635],[-72.333351,41.138018],[-72.322381,41.140664],[-72.291109,41.155874],[-72.278789,41.158722],[-72.272997,41.15501],[-72.2681,41.154146],[-72.245348,41.161217],[-72.238211,41.15949],[-72.237731,41.156434],[-72.253572,41.137138],[-72.265124,41.128482],[-72.300374,41.112274],[-72.300044,41.132059],[-72.306381,41.13784],[-72.312734,41.138546],[-72.318146,41.137134],[-72.32663,41.132162],[-72.335271,41.120274],[-72.335177,41.106917],[-72.317238,41.088659],[-72.297718,41.081042],[-72.280373,41.080402],[-72.276709,41.076722],[-72.283093,41.067874],[-72.273657,41.051533],[-72.260515,41.042065],[-72.241252,41.04477],[-72.229364,41.044355],[-72.217476,41.040611],[-72.201859,41.032275],[-72.190563,41.032579],[-72.183266,41.035619],[-72.17949,41.038435],[-72.174882,41.046147],[-72.162898,41.053187],[-72.16037,41.053827],[-72.153857,41.051859],[-72.137297,41.039684],[-72.135137,41.031284],[-72.137409,41.023908],[-72.116368,40.999796],[-72.109008,40.994084],[-72.10216,40.991509],[-72.095456,40.991349],[-72.083039,40.996453],[-72.079951,41.003429],[-72.079208,41.006437],[-72.076175,41.009093],[-72.061448,41.009442],[-72.057934,41.004789],[-72.057075,41.004893],[-72.055188,41.005236],[-72.051585,41.006437],[-72.049526,41.009697],[-72.051549,41.015741],[-72.051928,41.020506],[-72.047468,41.022565],[-72.035792,41.020759],[-72.015013,41.028348],[-71.99926,41.039669],[-71.96704,41.047772],[-71.961078,41.054277],[-71.960355,41.059878],[-71.961563,41.064021],[-71.959595,41.071237],[-71.93825,41.077413],[-71.919385,41.080517],[-71.899256,41.080837],[-71.895496,41.077381],[-71.889543,41.075701],[-71.869558,41.075046],[-71.86447,41.076918],[-71.857494,41.073558],[-71.856214,41.070598],[-71.87391,41.052278],[-71.903736,41.040166],[-71.935689,41.034182],[-72.029357,40.999909],[-72.114448,40.972085],[-72.39585,40.86666],[-72.469996,40.84274],[-72.573441,40.813251],[-72.745208,40.767091],[-72.753112,40.763571],[-72.757176,40.764371],[-72.768152,40.761587],[-72.863164,40.732962],[-72.923214,40.713282],[-73.012545,40.679651],[-73.054963,40.666371],[-73.145266,40.645491],[-73.20844,40.630884],[-73.23914,40.6251],[-73.262106,40.621476],[-73.264493,40.621437],[-73.306396,40.620756],[-73.30974,40.622532],[-73.319257,40.635795],[-73.351465,40.6305],[-73.391967,40.617501],[-73.423806,40.609869],[-73.425586,40.656291],[-73.424618,40.666272],[-73.423269,40.670893],[-73.424758,40.679052],[-73.440967,40.764399],[-73.454172,40.834097]]]]},"id":"36103"},{"type":"Feature","properties":{"GEO_ID":"0500000US36107","STATE":"36","COUNTY":"107","NAME":"Tioga","LSAD":"County","CENSUSAREA":518.602},"geometry":{"type":"Polygon","coordinates":[[[-76.145519,41.998913],[-76.343722,41.998346],[-76.349898,41.99841],[-76.462155,41.998934],[-76.46654,41.999025],[-76.557624,42.000149],[-76.538349,42.281755],[-76.416199,42.262976],[-76.415305,42.318368],[-76.39465,42.318509],[-76.250149,42.296676],[-76.253359,42.407568],[-76.130181,42.410337],[-76.081134,42.230495],[-76.114033,42.153418],[-76.111106,42.112436],[-76.10584,41.998858],[-76.123696,41.998954],[-76.131201,41.998954],[-76.145519,41.998913]]]},"id":"36107"},{"type":"Feature","properties":{"GEO_ID":"0500000US36117","STATE":"36","COUNTY":"117","NAME":"Wayne","LSAD":"County","CENSUSAREA":603.826},"geometry":{"type":"Polygon","coordinates":[[[-77.374351,43.152584],[-77.376038,43.277652],[-77.341092,43.280661],[-77.314619,43.28103],[-77.303979,43.27815],[-77.264177,43.277363],[-77.214058,43.284114],[-77.173088,43.281509],[-77.143416,43.287561],[-77.130429,43.285635],[-77.111866,43.287945],[-77.067295,43.280937],[-77.033875,43.271218],[-76.999691,43.271456],[-76.988445,43.2745],[-76.958402,43.270005],[-76.952174,43.270692],[-76.922351,43.285006],[-76.904288,43.291816],[-76.886913,43.293891],[-76.877397,43.292926],[-76.854976,43.298443],[-76.841675,43.305399],[-76.794708,43.309632],[-76.769025,43.318452],[-76.747067,43.331477],[-76.731039,43.343421],[-76.722501,43.343686],[-76.705345,43.125463],[-76.713806,43.024035],[-76.963926,43.013157],[-77.133397,43.012463],[-77.134335,43.039926],[-77.371478,43.034696],[-77.374351,43.152584]]]},"id":"36117"},{"type":"Feature","properties":{"GEO_ID":"0500000US36017","STATE":"36","COUNTY":"017","NAME":"Chenango","LSAD":"County","CENSUSAREA":893.548},"geometry":{"type":"Polygon","coordinates":[[[-75.532776,42.195241],[-75.63711,42.195628],[-75.638299,42.248686],[-75.843792,42.259707],[-75.86402,42.415702],[-75.889832,42.723844],[-75.295877,42.744106],[-75.330143,42.568082],[-75.404464,42.479117],[-75.374905,42.410784],[-75.415319,42.314151],[-75.418421,42.195032],[-75.419907,42.194918],[-75.532776,42.195241]]]},"id":"36017"},{"type":"Feature","properties":{"GEO_ID":"0500000US36031","STATE":"36","COUNTY":"031","NAME":"Essex","LSAD":"County","CENSUSAREA":1794.228},"geometry":{"type":"Polygon","coordinates":[[[-73.324681,44.243614],[-73.350806,44.225943],[-73.390583,44.190886],[-73.403686,44.153102],[-73.429239,44.079414],[-73.437429,44.046861],[-73.43688,44.042578],[-73.410776,44.026944],[-73.405999,44.016229],[-73.405525,43.948813],[-73.407742,43.929887],[-73.397256,43.905668],[-73.388389,43.832404],[-73.379312,43.808478],[-73.433237,43.804083],[-73.435909,43.803836],[-73.43812,43.803687],[-73.495503,43.799319],[-73.86869,43.762803],[-74.057005,43.744513],[-74.047062,43.796343],[-74.213734,43.810875],[-74.336826,43.925223],[-74.255998,43.969797],[-74.28187,44.120552],[-74.09349,44.137615],[-74.12756,44.330211],[-74.141424,44.407268],[-73.909687,44.429699],[-73.700717,44.445571],[-73.496604,44.486081],[-73.463838,44.537681],[-73.338634,44.546847],[-73.33863,44.546844],[-73.306707,44.500334],[-73.299885,44.476652],[-73.293613,44.438903],[-73.296031,44.428339],[-73.315016,44.388513],[-73.323268,44.264796],[-73.324681,44.243614]]]},"id":"36031"},{"type":"Feature","properties":{"GEO_ID":"0500000US36049","STATE":"36","COUNTY":"049","NAME":"Lewis","LSAD":"County","CENSUSAREA":1274.679},"geometry":{"type":"Polygon","coordinates":[[[-75.170159,44.096959],[-75.11016,43.615229],[-75.5335,43.419756],[-75.756213,43.470388],[-75.774553,43.688884],[-75.786759,43.78832],[-75.850534,43.791886],[-75.84056,43.883976],[-75.758157,43.878785],[-75.60367,43.971363],[-75.542898,43.967795],[-75.484528,44.074172],[-75.545886,44.102978],[-75.446124,44.217655],[-75.170159,44.096959]]]},"id":"36049"},{"type":"Feature","properties":{"GEO_ID":"0500000US36065","STATE":"36","COUNTY":"065","NAME":"Oneida","LSAD":"County","CENSUSAREA":1212.429},"geometry":{"type":"Polygon","coordinates":[[[-75.247963,42.871604],[-75.437167,42.863319],[-75.444173,42.933089],[-75.544211,42.93177],[-75.552774,43.037554],[-75.737774,43.164673],[-75.884275,43.155562],[-75.886756,43.325021],[-75.814627,43.483578],[-75.756213,43.470388],[-75.5335,43.419756],[-75.11016,43.615229],[-75.086851,43.41701],[-75.076581,43.330705],[-75.16035,43.255805],[-75.069165,43.227333],[-75.219106,43.052469],[-75.212158,42.879973],[-75.242745,42.877869],[-75.247963,42.871604]]]},"id":"36065"},{"type":"Feature","properties":{"GEO_ID":"0500000US36077","STATE":"36","COUNTY":"077","NAME":"Otsego","LSAD":"County","CENSUSAREA":1001.7},"geometry":{"type":"Polygon","coordinates":[[[-74.71158,42.517799],[-74.97494,42.467488],[-75.197237,42.358329],[-75.415319,42.314151],[-75.374905,42.410784],[-75.404464,42.479117],[-75.330143,42.568082],[-75.295877,42.744106],[-75.247963,42.871604],[-75.242745,42.877869],[-75.212158,42.879973],[-75.13987,42.85976],[-75.100999,42.908363],[-74.906738,42.824943],[-74.878822,42.898274],[-74.763303,42.863237],[-74.702054,42.845305],[-74.650213,42.829941],[-74.648298,42.829558],[-74.667512,42.75071],[-74.630631,42.626674],[-74.71158,42.517799]]]},"id":"36077"},{"type":"Feature","properties":{"GEO_ID":"0500000US36091","STATE":"36","COUNTY":"091","NAME":"Saratoga","LSAD":"County","CENSUSAREA":809.984},"geometry":{"type":"Polygon","coordinates":[[[-73.676762,42.783277],[-73.688362,42.775477],[-73.719863,42.801277],[-73.722663,42.820677],[-73.809369,42.778869],[-73.895938,42.851076],[-74.09298,42.955868],[-74.093814,42.959378],[-74.097467,42.982934],[-74.140147,43.253979],[-74.1601,43.371532],[-73.884139,43.398041],[-73.835811,43.253756],[-73.59496,43.306118],[-73.573342,43.100545],[-73.635463,42.94129],[-73.68461,42.892399],[-73.659663,42.818978],[-73.661362,42.802977],[-73.672355,42.795791],[-73.673463,42.790276],[-73.676762,42.783277]]]},"id":"36091"},{"type":"Feature","properties":{"GEO_ID":"0500000US36101","STATE":"36","COUNTY":"101","NAME":"Steuben","LSAD":"County","CENSUSAREA":1390.559},"geometry":{"type":"Polygon","coordinates":[[[-76.965728,42.001274],[-77.007536,42.000819],[-77.007635,42.000848],[-77.124693,41.999395],[-77.505308,42.00007],[-77.610028,41.999519],[-77.749931,41.998782],[-77.722964,42.471216],[-77.659917,42.580409],[-77.490889,42.577288],[-77.366505,42.576368],[-77.143795,42.576869],[-77.107203,42.483771],[-77.099657,42.272356],[-76.965028,42.278495],[-76.965728,42.001274]]]},"id":"36101"},{"type":"Feature","properties":{"GEO_ID":"0500000US36113","STATE":"36","COUNTY":"113","NAME":"Warren","LSAD":"County","CENSUSAREA":866.952},"geometry":{"type":"Polygon","coordinates":[[[-73.86869,43.762803],[-73.495503,43.799319],[-73.43812,43.803687],[-73.492893,43.657303],[-73.62894,43.486391],[-73.59496,43.306118],[-73.835811,43.253756],[-73.884139,43.398041],[-74.1601,43.371532],[-74.214625,43.728703],[-74.057005,43.744513],[-73.86869,43.762803]]]},"id":"36113"},{"type":"Feature","properties":{"GEO_ID":"0500000US36001","STATE":"36","COUNTY":"001","NAME":"Albany","LSAD":"County","CENSUSAREA":522.804},"geometry":{"type":"Polygon","coordinates":[[[-73.809369,42.778869],[-73.722663,42.820677],[-73.719863,42.801277],[-73.688362,42.775477],[-73.676762,42.783277],[-73.761265,42.610379],[-73.773161,42.509377],[-73.784594,42.489947],[-73.783721,42.464231],[-74.254303,42.408207],[-74.241572,42.550802],[-74.169725,42.667426],[-74.180274,42.729979],[-73.809603,42.775016],[-73.809369,42.778869]]]},"id":"36001"},{"type":"Feature","properties":{"GEO_ID":"0500000US36005","STATE":"36","COUNTY":"005","NAME":"Bronx","LSAD":"County","CENSUSAREA":42.096},"geometry":{"type":"MultiPolygon","coordinates":[[[[-73.773361,40.859449],[-73.770552,40.86033],[-73.766333,40.857317],[-73.765128,40.854228],[-73.766032,40.844961],[-73.769648,40.84466],[-73.773038,40.848125],[-73.773717,40.854831],[-73.773361,40.859449]]],[[[-73.785964,40.800862],[-73.793403,40.799881],[-73.811001,40.805077],[-73.830548,40.803162],[-73.862704,40.797276],[-73.866707,40.793653],[-73.870992,40.786979],[-73.884867,40.786621],[-73.889918,40.787398],[-73.890586,40.790145],[-73.892205,40.79038],[-73.899809,40.792524],[-73.912506,40.79618],[-73.907,40.873455],[-73.907105,40.876277],[-73.911405,40.879278],[-73.9152,40.875581],[-73.933408,40.882075],[-73.933406,40.882078],[-73.92747,40.895682],[-73.919705,40.913478],[-73.917905,40.917577],[-73.824047,40.889866],[-73.823557,40.889865],[-73.823617,40.890413],[-73.82312,40.890648],[-73.823244,40.891199],[-73.806395,40.886801],[-73.804789,40.886505],[-73.783545,40.88104],[-73.784803,40.878528],[-73.785502,40.869079],[-73.788786,40.858485],[-73.78806,40.854131],[-73.784754,40.851793],[-73.782174,40.847358],[-73.782093,40.844616],[-73.782254,40.842359],[-73.781206,40.838891],[-73.782577,40.837601],[-73.783867,40.836795],[-73.785399,40.838004],[-73.788221,40.842036],[-73.791044,40.846552],[-73.789512,40.85139],[-73.792253,40.855825],[-73.793785,40.855583],[-73.797252,40.852196],[-73.799543,40.848027],[-73.806914,40.849501],[-73.81281,40.846737],[-73.815574,40.835129],[-73.815205,40.831075],[-73.811889,40.825363],[-73.804518,40.818546],[-73.797332,40.815597],[-73.785964,40.800862]]]]},"id":"36005"},{"type":"Feature","properties":{"GEO_ID":"0500000US36015","STATE":"36","COUNTY":"015","NAME":"Chemung","LSAD":"County","CENSUSAREA":407.352},"geometry":{"type":"Polygon","coordinates":[[[-76.927084,42.001674],[-76.937084,42.001674],[-76.942585,42.001574],[-76.965686,42.001274],[-76.965728,42.001274],[-76.965028,42.278495],[-76.733912,42.29372],[-76.642256,42.233721],[-76.619303,42.282853],[-76.561601,42.281986],[-76.538349,42.281755],[-76.557624,42.000149],[-76.558118,42.000155],[-76.815878,42.001673],[-76.835079,42.001773],[-76.920784,42.001774],[-76.921884,42.001674],[-76.927084,42.001674]]]},"id":"36015"},{"type":"Feature","properties":{"GEO_ID":"0500000US36023","STATE":"36","COUNTY":"023","NAME":"Cortland","LSAD":"County","CENSUSAREA":498.76},"geometry":{"type":"Polygon","coordinates":[[[-76.130181,42.410337],[-76.253359,42.407568],[-76.265584,42.623588],[-76.274673,42.771257],[-75.896079,42.790964],[-75.889832,42.723844],[-75.86402,42.415702],[-76.130181,42.410337]]]},"id":"36023"},{"type":"Feature","properties":{"GEO_ID":"0500000US36025","STATE":"36","COUNTY":"025","NAME":"Delaware","LSAD":"County","CENSUSAREA":1442.44},"geometry":{"type":"Polygon","coordinates":[[[-75.359579,41.999445],[-75.421776,42.04203],[-75.419664,42.150436],[-75.418827,42.180702],[-75.418438,42.186797],[-75.418689,42.188022],[-75.418807,42.188104],[-75.418544,42.189504],[-75.418421,42.195032],[-75.415319,42.314151],[-75.197237,42.358329],[-74.97494,42.467488],[-74.71158,42.517799],[-74.618895,42.424389],[-74.443506,42.355017],[-74.53731,42.201424],[-74.451713,42.169225],[-74.780693,42.016375],[-74.997252,41.918485],[-75.146446,41.850899],[-75.263005,41.885109],[-75.279094,41.938917],[-75.292589,41.953897],[-75.341868,41.993262],[-75.359579,41.999445]]]},"id":"36025"},{"type":"Feature","properties":{"GEO_ID":"0500000US36029","STATE":"36","COUNTY":"029","NAME":"Erie","LSAD":"County","CENSUSAREA":1042.693},"geometry":{"type":"Polygon","coordinates":[[[-79.136725,42.569693],[-79.12963,42.589824],[-79.126261,42.590937],[-79.121921,42.594234],[-79.113713,42.605994],[-79.111361,42.613358],[-79.078761,42.640058],[-79.073261,42.639958],[-79.06376,42.644758],[-79.062261,42.668358],[-79.04886,42.689158],[-79.01886,42.701558],[-79.00616,42.704558],[-78.991159,42.705358],[-78.944158,42.731958],[-78.918157,42.737258],[-78.868556,42.770258],[-78.853455,42.783958],[-78.851355,42.791758],[-78.856456,42.800258],[-78.859356,42.800658],[-78.863656,42.813058],[-78.865656,42.826758],[-78.860445,42.83511],[-78.859456,42.841358],[-78.865592,42.852358],[-78.872227,42.853306],[-78.882557,42.867258],[-78.891655,42.884845],[-78.912458,42.886557],[-78.905758,42.899957],[-78.905659,42.923357],[-78.909159,42.933257],[-78.918859,42.946857],[-78.921206,42.948422],[-78.93236,42.955857],[-78.972524,42.966804],[-79.011563,42.985256],[-79.019964,42.994756],[-79.028353,43.066897],[-79.009664,43.069558],[-78.945262,43.066956],[-78.828805,43.030139],[-78.733606,43.084219],[-78.464449,43.088703],[-78.463887,42.924325],[-78.464381,42.867461],[-78.46394,42.536332],[-78.695937,42.47194],[-78.920446,42.442556],[-78.991702,42.529249],[-79.060777,42.537853],[-79.136725,42.569693]]]},"id":"36029"},{"type":"Feature","properties":{"GEO_ID":"0500000US36047","STATE":"36","COUNTY":"047","NAME":"Kings","LSAD":"County","CENSUSAREA":70.816},"geometry":{"type":"Polygon","coordinates":[[[-73.868917,40.69515],[-73.866027,40.681918],[-73.85566,40.663802],[-73.86049,40.654655],[-73.849852,40.588669],[-73.938598,40.566161],[-73.944558,40.568716],[-73.95005,40.573363],[-73.95938,40.572682],[-73.991346,40.57035],[-74.002056,40.570623],[-74.00903,40.572846],[-74.012022,40.574528],[-74.012996,40.578169],[-74.007276,40.583616],[-74.00635,40.584767],[-74.001591,40.590684],[-74.003281,40.595754],[-74.010926,40.600789],[-74.032856,40.604421],[-74.03959,40.612934],[-74.042412,40.624847],[-74.038336,40.637074],[-74.035868,40.640776],[-74.032066,40.646479],[-74.018272,40.659019],[-74.020467,40.67877],[-74.022911,40.681267],[-74.019347,40.679548],[-74.008117,40.686615],[-74.003946,40.689047],[-73.994648,40.704135],[-73.969845,40.709047],[-73.962645,40.722747],[-73.961543,40.723876],[-73.962795,40.737674],[-73.961188,40.737091],[-73.954732,40.739292],[-73.947064,40.737516],[-73.937339,40.72992],[-73.929223,40.727849],[-73.923865,40.720056],[-73.921473,40.709004],[-73.912058,40.703446],[-73.904425,40.695671],[-73.896497,40.682447],[-73.889575,40.68418],[-73.874021,40.694191],[-73.868917,40.69515]]]},"id":"36047"},{"type":"Feature","properties":{"GEO_ID":"0500000US36053","STATE":"36","COUNTY":"053","NAME":"Madison","LSAD":"County","CENSUSAREA":654.842},"geometry":{"type":"Polygon","coordinates":[[[-75.884275,43.155562],[-75.737774,43.164673],[-75.552774,43.037554],[-75.544211,42.93177],[-75.444173,42.933089],[-75.437167,42.863319],[-75.247963,42.871604],[-75.295877,42.744106],[-75.889832,42.723844],[-75.896079,42.790964],[-75.917189,43.085779],[-75.975588,43.091278],[-75.975849,43.094606],[-75.974724,43.096919],[-75.976286,43.098489],[-75.975641,43.100336],[-75.976396,43.103038],[-75.974149,43.103563],[-75.971524,43.104914],[-75.972988,43.106379],[-75.97203,43.107522],[-75.970349,43.107567],[-75.971725,43.109186],[-75.969201,43.110504],[-75.96543,43.116721],[-75.965594,43.119552],[-75.964695,43.119811],[-75.963383,43.119043],[-75.963517,43.117563],[-75.959703,43.115459],[-75.956023,43.115148],[-75.955995,43.11623],[-75.9544,43.116857],[-75.955843,43.118314],[-75.957416,43.118194],[-75.95595,43.119515],[-75.95713,43.120241],[-75.959414,43.119808],[-75.95701,43.121973],[-75.958339,43.123728],[-75.960494,43.122969],[-75.958817,43.125112],[-75.958833,43.128093],[-75.956763,43.126804],[-75.954592,43.127986],[-75.952421,43.130705],[-75.950287,43.132551],[-75.953277,43.133363],[-75.950066,43.134376],[-75.950296,43.135195],[-75.953405,43.135459],[-75.954803,43.134008],[-75.957129,43.136297],[-75.958196,43.135082],[-75.957184,43.133947],[-75.960459,43.13284],[-75.961672,43.133941],[-75.963961,43.133799],[-75.964403,43.135128],[-75.967318,43.134819],[-75.969221,43.136765],[-75.96992,43.13863],[-75.972347,43.140476],[-75.975318,43.138939],[-75.973837,43.137342],[-75.975602,43.136169],[-75.977349,43.136343],[-75.97678,43.137905],[-75.977515,43.139791],[-75.976964,43.140754],[-75.972648,43.142995],[-75.971783,43.143847],[-75.972702,43.145473],[-75.973342,43.149225],[-75.971235,43.154639],[-75.972903,43.155894],[-75.977068,43.157646],[-75.976752,43.160269],[-75.974629,43.161917],[-75.97438,43.163175],[-75.97788,43.164591],[-75.979131,43.166262],[-75.978319,43.167706],[-75.981008,43.167704],[-75.979478,43.170698],[-75.982668,43.173631],[-75.986514,43.171572],[-75.988447,43.172616],[-75.990028,43.171527],[-75.991933,43.172953],[-75.992635,43.173849],[-75.989672,43.179591],[-75.990766,43.180917],[-75.991437,43.18325],[-75.993394,43.183376],[-75.992428,43.185164],[-75.986894,43.183938],[-75.979489,43.177401],[-75.973438,43.179898],[-75.959359,43.180389],[-75.955599,43.172182],[-75.932778,43.176583],[-75.927453,43.162738],[-75.884275,43.155562]]]},"id":"36053"},{"type":"Feature","properties":{"GEO_ID":"0500000US36061","STATE":"36","COUNTY":"061","NAME":"New York","LSAD":"County","CENSUSAREA":22.829},"geometry":{"type":"MultiPolygon","coordinates":[[[[-74.04086,40.700117],[-74.040018,40.700678],[-74.039401,40.700454],[-74.037998,40.698995],[-74.043441,40.68968],[-74.044451,40.688445],[-74.046359,40.689175],[-74.047313,40.690466],[-74.04692,40.691139],[-74.04086,40.700117]]],[[[-73.962795,40.737674],[-73.961543,40.723876],[-73.962645,40.722747],[-73.969845,40.709047],[-73.994648,40.704135],[-74.003946,40.689047],[-74.008117,40.686615],[-74.019347,40.679548],[-74.022911,40.681267],[-74.023982,40.68236],[-74.024827,40.687007],[-74.021721,40.693504],[-74.01849,40.695457],[-74.0168,40.701794],[-74.019526,40.706985],[-74.024543,40.709436],[-74.013784,40.756601],[-74.009184,40.763601],[-74.000905,40.776488],[-73.993029,40.788746],[-73.986864,40.798344],[-73.948281,40.858399],[-73.938081,40.874699],[-73.933408,40.882075],[-73.9152,40.875581],[-73.911405,40.879278],[-73.907105,40.876277],[-73.907,40.873455],[-73.912506,40.79618],[-73.910551,40.790988],[-73.916316,40.786601],[-73.92797,40.776762],[-73.93508,40.779218],[-73.938399,40.774606],[-73.938076,40.772551],[-73.93519,40.771745],[-73.936536,40.769835],[-73.940844,40.767399],[-73.943951,40.764434],[-73.95492,40.751509],[-73.9583,40.745731],[-73.961544,40.743081],[-73.962795,40.737674]]]]},"id":"36061"},{"type":"Feature","properties":{"GEO_ID":"0500000US36067","STATE":"36","COUNTY":"067","NAME":"Onondaga","LSAD":"County","CENSUSAREA":778.39},"geometry":{"type":"Polygon","coordinates":[[[-76.499312,43.097949],[-76.479224,43.227519],[-76.258951,43.237468],[-76.202944,43.271605],[-75.993394,43.183376],[-75.991437,43.18325],[-75.990766,43.180917],[-75.989672,43.179591],[-75.992635,43.173849],[-75.991933,43.172953],[-75.990028,43.171527],[-75.988447,43.172616],[-75.986514,43.171572],[-75.982668,43.173631],[-75.979478,43.170698],[-75.981008,43.167704],[-75.978319,43.167706],[-75.979131,43.166262],[-75.97788,43.164591],[-75.97438,43.163175],[-75.974629,43.161917],[-75.976752,43.160269],[-75.977068,43.157646],[-75.972903,43.155894],[-75.971235,43.154639],[-75.973342,43.149225],[-75.972702,43.145473],[-75.971783,43.143847],[-75.972648,43.142995],[-75.976964,43.140754],[-75.977515,43.139791],[-75.97678,43.137905],[-75.977349,43.136343],[-75.975602,43.136169],[-75.973837,43.137342],[-75.975318,43.138939],[-75.972347,43.140476],[-75.96992,43.13863],[-75.969221,43.136765],[-75.967318,43.134819],[-75.964403,43.135128],[-75.963961,43.133799],[-75.961672,43.133941],[-75.960459,43.13284],[-75.957184,43.133947],[-75.958196,43.135082],[-75.957129,43.136297],[-75.954803,43.134008],[-75.953405,43.135459],[-75.950296,43.135195],[-75.950066,43.134376],[-75.953277,43.133363],[-75.950287,43.132551],[-75.952421,43.130705],[-75.954592,43.127986],[-75.956763,43.126804],[-75.958833,43.128093],[-75.958817,43.125112],[-75.960494,43.122969],[-75.958339,43.123728],[-75.95701,43.121973],[-75.959414,43.119808],[-75.95713,43.120241],[-75.95595,43.119515],[-75.957416,43.118194],[-75.955843,43.118314],[-75.9544,43.116857],[-75.955995,43.11623],[-75.956023,43.115148],[-75.959703,43.115459],[-75.963517,43.117563],[-75.963383,43.119043],[-75.964695,43.119811],[-75.965594,43.119552],[-75.96543,43.116721],[-75.969201,43.110504],[-75.971725,43.109186],[-75.970349,43.107567],[-75.97203,43.107522],[-75.972988,43.106379],[-75.971524,43.104914],[-75.974149,43.103563],[-75.976396,43.103038],[-75.975641,43.100336],[-75.976286,43.098489],[-75.974724,43.096919],[-75.975849,43.094606],[-75.975588,43.091278],[-75.917189,43.085779],[-75.896079,42.790964],[-76.274673,42.771257],[-76.356974,42.84945],[-76.450738,42.84576],[-76.462999,43.006316],[-76.499312,43.097949]]]},"id":"36067"},{"type":"Feature","properties":{"GEO_ID":"0500000US36079","STATE":"36","COUNTY":"079","NAME":"Putnam","LSAD":"County","CENSUSAREA":230.312},"geometry":{"type":"Polygon","coordinates":[[[-73.982584,41.321693],[-73.981384,41.324693],[-73.981486,41.438905],[-73.933775,41.488279],[-73.530067,41.527194],[-73.533969,41.479693],[-73.534055,41.478968],[-73.53415,41.47806],[-73.534269,41.476911],[-73.534269,41.476394],[-73.534369,41.475894],[-73.535769,41.457159],[-73.535857,41.455709],[-73.535885,41.455236],[-73.535986,41.45306],[-73.536067,41.451331],[-73.536969,41.441094],[-73.537469,41.43589],[-73.537673,41.433905],[-73.543641,41.376778],[-73.544728,41.366375],[-73.982584,41.321693]]]},"id":"36079"},{"type":"Feature","properties":{"GEO_ID":"0500000US36085","STATE":"36","COUNTY":"085","NAME":"Richmond","LSAD":"County","CENSUSAREA":58.37},"geometry":{"type":"Polygon","coordinates":[[[-74.144428,40.53516],[-74.148697,40.534489],[-74.160859,40.52679],[-74.177986,40.519603],[-74.182157,40.520634],[-74.199923,40.511729],[-74.210474,40.509448],[-74.219787,40.502603],[-74.23324,40.501299],[-74.246688,40.496103],[-74.250188,40.496703],[-74.254588,40.502303],[-74.256088,40.507903],[-74.252702,40.513895],[-74.242888,40.520903],[-74.241732,40.531273],[-74.247808,40.543396],[-74.229002,40.555041],[-74.216997,40.554991],[-74.210887,40.560902],[-74.204054,40.589336],[-74.19682,40.597037],[-74.195407,40.601806],[-74.196096,40.616169],[-74.200994,40.616906],[-74.201812,40.619507],[-74.20058,40.631448],[-74.1894,40.642121],[-74.180191,40.645521],[-74.174085,40.645109],[-74.170187,40.642201],[-74.152973,40.638886],[-74.120186,40.642201],[-74.086485,40.648601],[-74.075884,40.648101],[-74.0697,40.641216],[-74.067598,40.623865],[-74.060345,40.611999],[-74.053125,40.603678],[-74.059184,40.593502],[-74.068184,40.584102],[-74.090797,40.566463],[-74.111471,40.546908],[-74.112585,40.547603],[-74.121672,40.542691],[-74.137241,40.530076],[-74.14023,40.533738],[-74.144428,40.53516]]]},"id":"36085"},{"type":"Feature","properties":{"GEO_ID":"0500000US36097","STATE":"36","COUNTY":"097","NAME":"Schuyler","LSAD":"County","CENSUSAREA":328.333},"geometry":{"type":"Polygon","coordinates":[[[-76.895596,42.541537],[-76.696655,42.54679],[-76.691406,42.284307],[-76.619303,42.282853],[-76.642256,42.233721],[-76.733912,42.29372],[-76.965028,42.278495],[-77.099657,42.272356],[-77.107203,42.483771],[-76.889805,42.463054],[-76.895596,42.541537]]]},"id":"36097"},{"type":"Feature","properties":{"GEO_ID":"0500000US36105","STATE":"36","COUNTY":"105","NAME":"Sullivan","LSAD":"County","CENSUSAREA":968.132},"geometry":{"type":"Polygon","coordinates":[[[-75.050074,41.606893],[-75.053077,41.618552],[-75.048199,41.632011],[-75.053431,41.752538],[-75.090799,41.811991],[-75.114399,41.843583],[-75.140241,41.852078],[-75.146446,41.850899],[-74.997252,41.918485],[-74.780693,42.016375],[-74.453685,41.875595],[-74.575086,41.745258],[-74.395071,41.644876],[-74.367055,41.590977],[-74.475591,41.504334],[-74.752399,41.493743],[-74.75595,41.426804],[-74.799165,41.430451],[-74.876721,41.440338],[-74.891948,41.448853],[-74.912517,41.475605],[-74.93976,41.483371],[-74.984226,41.506299],[-75.04049,41.569688],[-75.050074,41.606893]]]},"id":"36105"},{"type":"Feature","properties":{"GEO_ID":"0500000US36111","STATE":"36","COUNTY":"111","NAME":"Ulster","LSAD":"County","CENSUSAREA":1124.235},"geometry":{"type":"Polygon","coordinates":[[[-73.942482,41.684093],[-73.947382,41.667493],[-73.953307,41.589977],[-74.126393,41.582544],[-74.264093,41.632738],[-74.367055,41.590977],[-74.395071,41.644876],[-74.575086,41.745258],[-74.453685,41.875595],[-74.780693,42.016375],[-74.451713,42.169225],[-74.307571,42.114346],[-74.074797,42.096589],[-74.042393,42.170386],[-73.910675,42.127293],[-73.921465,42.110025],[-73.929626,42.078778],[-73.962221,41.90102],[-73.941081,41.735993],[-73.941081,41.732693],[-73.944435,41.714634],[-73.946682,41.699396],[-73.945782,41.695593],[-73.943482,41.690293],[-73.942482,41.684093]]]},"id":"36111"},{"type":"Feature","properties":{"GEO_ID":"0500000US36115","STATE":"36","COUNTY":"115","NAME":"Washington","LSAD":"County","CENSUSAREA":831.184},"geometry":{"type":"Polygon","coordinates":[[[-73.269472,43.030686],[-73.274294,42.943652],[-73.635463,42.94129],[-73.573342,43.100545],[-73.59496,43.306118],[-73.62894,43.486391],[-73.492893,43.657303],[-73.43812,43.803687],[-73.435909,43.803836],[-73.433237,43.804083],[-73.379312,43.808478],[-73.379279,43.808391],[-73.357547,43.785933],[-73.350431,43.771438],[-73.360711,43.753268],[-73.370724,43.735571],[-73.403517,43.685032],[-73.408697,43.67402],[-73.421606,43.646577],[-73.431229,43.588285],[-73.428636,43.583994],[-73.400295,43.568889],[-73.375594,43.61335],[-73.366537,43.623462],[-73.306234,43.628018],[-73.302552,43.625708],[-73.245594,43.540253],[-73.242042,43.534925],[-73.247061,43.514919],[-73.252582,43.370997],[-73.252674,43.370285],[-73.252832,43.363493],[-73.253084,43.354714],[-73.254848,43.314684],[-73.259159,43.216848],[-73.269472,43.030686]]]},"id":"36115"},{"type":"Feature","properties":{"GEO_ID":"0500000US36119","STATE":"36","COUNTY":"119","NAME":"Westchester","LSAD":"County","CENSUSAREA":430.497},"geometry":{"type":"MultiPolygon","coordinates":[[[[-73.767176,40.886299],[-73.767076,40.885399],[-73.767076,40.884799],[-73.767076,40.883499],[-73.766276,40.881099],[-73.766976,40.880099],[-73.770876,40.879299],[-73.775276,40.882199],[-73.775176,40.884199],[-73.772776,40.884599],[-73.772276,40.887499],[-73.770576,40.888399],[-73.768276,40.887599],[-73.767276,40.886899],[-73.767176,40.886299]]],[[[-73.514617,41.198434],[-73.614407,41.153001],[-73.632153,41.144921],[-73.639672,41.141495],[-73.727775,41.100696],[-73.694273,41.059296],[-73.687173,41.050697],[-73.679973,41.041797],[-73.670472,41.030097],[-73.655371,41.012797],[-73.654671,41.011697],[-73.657336,40.985171],[-73.655972,40.979597],[-73.659972,40.968398],[-73.662072,40.966198],[-73.664472,40.967198],[-73.678073,40.962798],[-73.683273,40.948998],[-73.686473,40.945198],[-73.697974,40.939598],[-73.721739,40.932037],[-73.731775,40.924999],[-73.756776,40.912599],[-73.781338,40.885447],[-73.783545,40.88104],[-73.804789,40.886505],[-73.806395,40.886801],[-73.823244,40.891199],[-73.82312,40.890648],[-73.823617,40.890413],[-73.823557,40.889865],[-73.824047,40.889866],[-73.917905,40.917577],[-73.893979,40.997197],[-73.88938,41.037597],[-73.8947,41.069937],[-73.89488,41.082396],[-73.88718,41.133095],[-73.895381,41.153995],[-73.909281,41.164395],[-73.931482,41.204994],[-73.947965,41.223101],[-73.982584,41.321693],[-73.544728,41.366375],[-73.550961,41.295422],[-73.482709,41.21276],[-73.509487,41.200814],[-73.514617,41.198434]]]]},"id":"36119"},{"type":"Feature","properties":{"GEO_ID":"0500000US36009","STATE":"36","COUNTY":"009","NAME":"Cattaraugus","LSAD":"County","CENSUSAREA":1308.35},"geometry":{"type":"Polygon","coordinates":[[[-78.918854,41.997961],[-79.052473,41.999179],[-79.061265,41.999259],[-79.060777,42.537853],[-78.991702,42.529249],[-78.920446,42.442556],[-78.695937,42.47194],[-78.46394,42.536332],[-78.464556,42.519166],[-78.308839,42.521217],[-78.308128,41.999415],[-78.59665,41.999877],[-78.874759,41.997559],[-78.918854,41.997961]]]},"id":"36009"}]}')

@st.cache_data
def load_nys_nymph_surveillance():
    """Official observed latest-year snapshot; blank values remain missing."""
    return pd.DataFrame(NYS_TICK_SNAPSHOT["records"])

@st.cache_data
def load_us_county_geojson():
    """Drawing geometry only; no patient or health values in the boundaries."""
    return json.loads(json.dumps(NYS_MAP_BOUNDARIES))


def find_column(df, candidates):
    """Return the first matching normalized column name."""
    for candidate in candidates:
        if candidate in df.columns:
            return candidate
    # Fuzzy fallback for minor Socrata naming differences.
    for col in df.columns:
        compact = col.replace("_", "")
        for candidate in candidates:
            if candidate.replace("_", "") in compact:
                return col
    return None


def build_nys_tick_density_geojson():
    """Join latest NYSDOH nymph density observations to NY county boundaries."""
    tick = load_nys_nymph_surveillance()
    if tick.empty:
        return None, None

    year_col = find_column(tick, ["year"])
    county_col = find_column(tick, ["county"])
    density_col = find_column(tick, ["nymphal_density", "tick_population_density"])
    bb_col = find_column(tick, ["b_burgdorferi_pct", "b_burgdorferi"])

    if not year_col or not county_col or not density_col:
        return None, None

    tick[year_col] = pd.to_numeric(tick[year_col], errors="coerce")
    tick[density_col] = pd.to_numeric(tick[density_col], errors="coerce")
    latest_year = int(tick[year_col].dropna().max())
    latest = tick[tick[year_col] == latest_year].copy()
    latest["_county_key"] = latest[county_col].astype(str).str.strip().str.lower()
    latest = latest.drop_duplicates("_county_key", keep="last")

    # Normalize density to a 0-1 display intensity. This is NOT a clinical risk score.
    max_density = latest[density_col].max()
    if pd.isna(max_density) or max_density <= 0:
        max_density = 1.0

    values = {}
    for _, row in latest.iterrows():
        density = row[density_col]
        if pd.isna(density):
            continue
        intensity = max(0.0, min(float(density) / float(max_density), 1.0))
        bb_value = row[bb_col] if bb_col and bb_col in row.index else None
        values[row["_county_key"]] = {
            "density": float(density),
            "bb": bb_value,
            "intensity": intensity,
        }

    geo = load_us_county_geojson()
    features = []
    for feature in geo.get("features", []):
        # NY county FIPS begins with state FIPS 36.
        fid = str(feature.get("id", ""))
        if not fid.startswith("36"):
            continue
        name = str(feature.get("properties", {}).get("NAME", "")).strip()
        key = name.lower()
        item = values.get(key)
        if item is None:
            # Keep unsampled / unavailable counties neutral.
            fill = [190, 190, 190, 45]
            density_label = "No observation in latest year"
            bb_label = "—"
        else:
            x = item["intensity"]
            # Yellow -> orange -> red style intensity ramp.
            fill = [
                int(255),
                int(220 - 150 * x),
                int(80 - 55 * x),
                175,
            ]
            density_label = f'{item["density"]:.2f}'
            bb_label = str(item["bb"]) if item["bb"] is not None else "—"

        props = feature.setdefault("properties", {})
        props["county_label"] = f"{name} County"
        props["density_label"] = density_label
        props["bb_label"] = bb_label
        props["fill_color"] = fill
        features.append(feature)

    return {"type": "FeatureCollection", "features": features}, latest_year


def _project_svg(lon, lat, bounds, width, height, pad=16):
    min_lon, min_lat, max_lon, max_lat = bounds
    x = pad + (lon - min_lon) / (max_lon - min_lon) * (width - 2 * pad)
    y = pad + (max_lat - lat) / (max_lat - min_lat) * (height - 2 * pad)
    return x, y


def _geom_paths(geometry, bounds, width, height):
    """Convert Polygon/MultiPolygon GeoJSON to simple SVG paths."""
    paths = []
    if not geometry:
        return paths
    gtype = geometry.get("type")
    coords = geometry.get("coordinates", [])
    polygons = [coords] if gtype == "Polygon" else coords if gtype == "MultiPolygon" else []
    for polygon in polygons:
        if not polygon:
            continue
        ring = polygon[0]  # exterior ring is sufficient for this surveillance display
        pts = [_project_svg(float(lon), float(lat), bounds, width, height) for lon, lat in ring]
        if pts:
            d = "M " + " L ".join(f"{x:.1f},{y:.1f}" for x, y in pts) + " Z"
            paths.append(d)
    return paths


NY_LYME_RATE_SNAPSHOT = {'36001': {'cases': 667, 'population': 316659, 'rate': 52.66}, '36003': {'cases': 168, 'population': 46651, 'rate': 90.03}, '36005': {'cases': 192, 'population': 1356476, 'rate': 3.54}, '36007': {'cases': 506, 'population': 196077, 'rate': 64.52}, '36009': {'cases': 209, 'population': 75600, 'rate': 69.11}, '36011': {'cases': 159, 'population': 74485, 'rate': 53.37}, '36013': {'cases': 136, 'population': 124891, 'rate': 27.22}, '36015': {'cases': 98, 'population': 81325, 'rate': 30.13}, '36017': {'cases': 259, 'population': 45920, 'rate': 141.01}, '36019': {'cases': 156, 'population': 78115, 'rate': 49.93}, '36021': {'cases': 554, 'population': 60470, 'rate': 229.04}, '36023': {'cases': 276, 'population': 45752, 'rate': 150.81}, '36025': {'cases': 328, 'population': 44410, 'rate': 184.64}, '36027': {'cases': 1586, 'population': 297150, 'rate': 133.43}, '36029': {'cases': 346, 'population': 946147, 'rate': 9.14}, '36031': {'cases': 144, 'population': 36775, 'rate': 97.89}, '36033': {'cases': 143, 'population': 46502, 'rate': 76.88}, '36035': {'cases': 211, 'population': 52234, 'rate': 100.99}, '36037': {'cases': 41, 'population': 57529, 'rate': 17.82}, '36039': {'cases': 379, 'population': 47062, 'rate': 201.33}, '36041': {'cases': 6, 'population': 5082, 'rate': 29.52}, '36043': {'cases': 209, 'population': 59484, 'rate': 87.84}, '36045': {'cases': 198, 'population': 114787, 'rate': 43.12}, '36047': {'cases': 1677, 'population': 2561225, 'rate': 16.37}, '36049': {'cases': 176, 'population': 26548, 'rate': 165.74}, '36051': {'cases': 148, 'population': 61158, 'rate': 60.5}, '36053': {'cases': 179, 'population': 66921, 'rate': 66.87}, '36055': {'cases': 395, 'population': 748482, 'rate': 13.19}, '36057': {'cases': 146, 'population': 49368, 'rate': 73.93}, '36059': {'cases': 597, 'population': 1381715, 'rate': 10.8}, '36061': {'cases': 1589, 'population': 1597451, 'rate': 24.87}, '36063': {'cases': 30, 'population': 209457, 'rate': 3.58}, '36065': {'cases': 383, 'population': 227555, 'rate': 42.08}, '36067': {'cases': 441, 'population': 467873, 'rate': 23.56}, '36069': {'cases': 225, 'population': 112494, 'rate': 50.0}, '36071': {'cases': 1199, 'population': 407470, 'rate': 73.56}, '36073': {'cases': 22, 'population': 39124, 'rate': 14.06}, '36075': {'cases': 290, 'population': 118162, 'rate': 61.36}, '36077': {'cases': 448, 'population': 60126, 'rate': 186.28}, '36079': {'cases': 522, 'population': 98060, 'rate': 133.08}, '36081': {'cases': 559, 'population': 2252196, 'rate': 6.21}, '36083': {'cases': 744, 'population': 159305, 'rate': 116.76}, '36085': {'cases': 283, 'population': 490687, 'rate': 14.42}, '36087': {'cases': 708, 'population': 340807, 'rate': 51.94}, '36089': {'cases': 375, 'population': 106940, 'rate': 87.67}, '36091': {'cases': 466, 'population': 238711, 'rate': 48.8}, '36093': {'cases': 140, 'population': 159902, 'rate': 21.89}, '36095': {'cases': 208, 'population': 30105, 'rate': 172.73}, '36097': {'cases': 131, 'population': 17507, 'rate': 187.07}, '36099': {'cases': 71, 'population': 32349, 'rate': 54.87}, '36101': {'cases': 205, 'population': 92162, 'rate': 55.61}, '36103': {'cases': 3068, 'population': 1523170, 'rate': 50.36}, '36105': {'cases': 299, 'population': 79920, 'rate': 93.53}, '36107': {'cases': 172, 'population': 47715, 'rate': 90.12}, '36109': {'cases': 402, 'population': 103558, 'rate': 97.05}, '36111': {'cases': 1004, 'population': 182333, 'rate': 137.66}, '36113': {'cases': 245, 'population': 65380, 'rate': 93.68}, '36115': {'cases': 334, 'population': 60047, 'rate': 139.06}, '36117': {'cases': 166, 'population': 90829, 'rate': 45.69}, '36119': {'cases': 1110, 'population': 990817, 'rate': 28.01}, '36121': {'cases': 52, 'population': 39532, 'rate': 32.88}, '36123': {'cases': 104, 'population': 24472, 'rate': 106.24}}

def show_nys_tick_density_map():
    """Render NY surveillance on a guaranteed white SVG background (no map tiles)."""
    try:
        geojson, latest_year = build_nys_tick_density_geojson()
        if not geojson:
            st.warning("The statewide surveillance map is temporarily unavailable.")
            return
        st.markdown("#### Tick activity and reported Lyme rates across New York")
        st.caption("Dutchess County is highlighted as our pilot.")
        width, height = 760, 420
        bounds = (-79.9, 40.35, -71.7, 45.15)
        parts = [f'<svg role="img" aria-label="New York observed tick surveillance by county" viewBox="0 0 {width} {height}" width="100%" height="100%" xmlns="http://www.w3.org/2000/svg"><title>Observed tick density by New York county; missing observations are gray</title>',
                 '<rect width="100%" height="100%" fill="#ffffff"/>']
        for feature in geojson.get("features", []):
            props = feature.get("properties", {})
            rgb = props.get("fill_color", [235,235,235,255])[:3]
            fill = '#%02x%02x%02x' % tuple(int(v) for v in rgb)
            title = html.escape((f"{props.get('county_label','')} | Nymph density: {props.get('density_label','N/A')} | "
                     f"B. burgdorferi positive: {props.get('bb_label','N/A')}"), quote=True)
            for d in _geom_paths(feature.get("geometry"), bounds, width, height):
                parts.append(f'<path d="{d}" fill="{fill}" stroke="#6b7280" stroke-width="0.8"><title>{title}</title></path>')
        # Overlay reported-case rates; circle AREA is proportional to the rate.
        for feature in geojson.get("features", []):
            fid = str(feature.get("id", "")).zfill(5)
            item = NY_LYME_RATE_SNAPSHOT.get(fid)
            center = _geometry_centroid(feature.get("geometry"))
            if not center:
                continue
            cx, cy = _project_svg(*center, bounds, width, height)
            if item is not None and item["rate"] > 0:
                radius = math.sqrt(item["rate"]) * 0.7
                county = html.escape(feature["properties"].get("county_label", "County"))
                parts.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{radius:.2f}" fill="#174b73" fill-opacity="0.25" stroke="#174b73" stroke-width="1.2"><title>{county}: approximate annualized reported Lyme rate {item["rate"]:.2f} per 100,000; {item["cases"]} cases, 2019–2022; 2023 population {item["population"]}</title></circle>')
        # Draw pilot boundary LAST so neighboring symbols cannot hide it.
        for feature in geojson.get("features", []):
            if str(feature.get("id", "")).zfill(5) != "36027":
                continue
            for d in _geom_paths(feature.get("geometry"), bounds, width, height):
                parts.append(f'<path d="{d}" fill="none" stroke="white" stroke-width="5"/><path d="{d}" fill="none" stroke="#12324a" stroke-width="2.5"><title>Dutchess County — pilot</title></path>')
            cx, cy = _project_svg(-73.74, 41.76, bounds, width, height)
            parts.append(f'<text x="{cx:.1f}" y="{cy:.1f}" text-anchor="middle" font-size="20" fill="#12324a" stroke="white" stroke-width="0.8">★<title>Dutchess County pilot</title></text>')
            parts.append(f'<text x="{cx+17:.1f}" y="{cy-17:.1f}" font-size="13" font-weight="bold" fill="#12324a" stroke="white" stroke-width="3" paint-order="stroke">Dutchess — pilot</text>')
        parts.append('</svg>')
        components.html(
            '<div style="background:white;border:1px solid #d1d5db;border-radius:10px;padding:8px;height:440px;">'
            + ''.join(parts) + '</div>', height=460, scrolling=False
        )
        observed = [float(f["properties"]["density_label"]) for f in geojson["features"]
                    if f["properties"]["density_label"] != "No observation in latest year"]
        scale_max = max(observed, default=0.0)
        st.markdown(
            '<div style="max-width:560px;padding:8px 0" aria-label="Observed tick density legend">'
            '<strong>Observed tick density</strong><br><span style="font-size:0.9rem">Nymphs per 1,000 m² sampled</span>'
            '<div style="height:16px;margin-top:8px;border:1px solid #6b7280;border-radius:3px;'
            'background:linear-gradient(to right,rgb(255,220,80),rgb(255,70,25))"></div>'
            f'<div style="display:flex;justify-content:space-between;font-size:0.9rem"><span>0</span>'
            f'<span>{scale_max / 2:g}</span><span>{scale_max:g}</span></div>'
            '<div style="display:flex;align-items:center;gap:8px;margin-top:8px;font-size:0.9rem">'
            '<span aria-hidden="true" style="display:inline-block;width:18px;height:14px;'
            'background:#bebebe;border:1px solid #6b7280"></span>No observation available</div></div>',
            unsafe_allow_html=True,
        )
        symbols = []
        for rate in (50, 150, 300):
            radius = math.sqrt(rate) * 0.7
            symbols.append(f'<span style="display:inline-flex;align-items:center;gap:5px;margin-right:18px"><span aria-hidden="true" style="width:{radius*2:.2f}px;height:{radius*2:.2f}px;display:inline-block;border-radius:50%;background:rgba(23,75,115,0.25);border:1px solid #174b73;box-sizing:content-box"></span>{rate}</span>')
        st.markdown('<strong>Approximate annualized reported Lyme rate</strong><br><span>Cases per 100,000 residents · circle area</span><br>' + ''.join(symbols), unsafe_allow_html=True)
        st.caption("Circles: CDC reported cases, 2019–2022 total ÷ 4 ÷ HRSA 2023 population × 100,000. Approximate annualized rate, not year-specific incidence. Cases reflect residence, not necessarily exposure location; reporting changed in 2022.")
        with st.expander("County Lyme rates in text"):
            table = []
            for feature in geojson["features"]:
                item = NY_LYME_RATE_SNAPSHOT.get(str(feature.get("id", "")).zfill(5))
                table.append({"County": feature["properties"].get("county_label"), "Tick density / 1,000 m²": feature["properties"].get("density_label"), "Reported Lyme cases · 2019–2022": item["cases"] if item else None, "Population · 2023": item["population"] if item else None, "Approx. annual rate / 100,000": item["rate"] if item else None})
            st.dataframe(pd.DataFrame(table).sort_values("County"), hide_index=True, use_container_width=True)
        st.caption(f"NYSDOH • {latest_year} observations • Snapshot checked October 7, 2026. Hover for county values; a text table is available below.")
        st.caption("Darker colors mean more ticks observed at sampled sites, not a person's infection risk. Gray does not mean no ticks.")
    except Exception:
        st.warning("The statewide surveillance map could not load. Your Dutchess County summary below is still available.")

@st.cache_data
def load_data():
    if not DATA_FILE.exists():
        return pd.DataFrame(), pd.DataFrame()
    try:
        geography = pd.read_excel(DATA_FILE, sheet_name="Geography")
        clinical = pd.read_excel(DATA_FILE, sheet_name="Clinical_Evidence")
        return geography, clinical
    except Exception:
        return pd.DataFrame(), pd.DataFrame()

@st.cache_data
def load_ny_tick_data():
    try:
        return pd.read_csv(NY_TICK_FILE) if NY_TICK_FILE.exists() else pd.DataFrame()
    except Exception:
        return pd.DataFrame()

@st.cache_data
def load_population_data():
    try:
        return pd.read_csv(POPULATION_FILE) if POPULATION_FILE.exists() else pd.DataFrame()
    except Exception:
        return pd.DataFrame()

@st.cache_data
def load_ahrf_county(fips):
    """Load selected county directly from the HRSA AHRF 2024-2025 source ZIP."""
    if not AHRF_ZIP_FILE.exists():
        return None
    try:
        with zipfile.ZipFile(AHRF_ZIP_FILE) as z:
            name = next(n for n in z.namelist() if n.endswith("AHRF2025.csv"))
            df = pd.read_csv(z.open(name), dtype={"fips_st_cnty": str}, low_memory=False)
        row = df[df["fips_st_cnty"].astype(str).str.zfill(5) == str(fips).zfill(5)]
        if row.empty:
            return None
        r = row.iloc[0]
        return {
            "population": r.get("popn_est_23"),
            "pcp": r.get("phys_nf_prim_care_pc_exc_rsdt_23"),
            "em": r.get("md_nf_emerg_med_23"),
            "hosp": r.get("hosp_23"),
            "beds": r.get("hosp_beds_23"),
            "hpsa": r.get("hpsa_prim_care_25"),
            "source": "HRSA Area Health Resources Files (AHRF), 2024-2025 release",
            "fields": "popn_est_23; phys_nf_prim_care_pc_exc_rsdt_23; md_nf_emerg_med_23; hosp_23; hosp_beds_23; hpsa_prim_care_25",
        }
    except Exception:
        return None

@st.cache_data
def load_places_county(fips):
    """Load CDC PLACES county context; returns missing rather than substituting another county."""
    if not PLACES_FILE.exists():
        return None
    try:
        df = pd.read_csv(PLACES_FILE, dtype={"LocationID": str}, low_memory=False)
        d = df[df["LocationID"].astype(str).str.zfill(5) == str(fips).zfill(5)].copy()
        if d.empty:
            return None
        wanted = ["DISABILITY","EMOTIONSPT","GHLTH","PHLTH","MOBILITY","COGNITION","INDEPLIVE","SELFCARE","LACKTRPT"]
        d = d[d["MeasureId"].isin(wanted) & d["Data_Value"].notna()]
        if d.empty:
            return None
        # Keep prevalence definitions consistent instead of choosing an arbitrary row.
        if "Data_Value_Type" in d.columns:
            d = d[d["Data_Value_Type"].astype(str).str.casefold() == "crude prevalence"]
        if d.empty:
            return None
        # Prefer the newest available row for each measure; never convert missing to zero.
        d["Year_num"] = pd.to_numeric(d["Year"], errors="coerce")
        d = d.sort_values("Year_num").groupby("MeasureId", as_index=False).tail(1)
        return d
    except Exception:
        return None

geography, clinical = load_data()
ny_tick_data = load_ny_tick_data()
population_data = load_population_data()

PATIENT_VOICE_FILE = BASE_DIR / "pathwayai_patient_voice.csv"
COUNTY_ASSETS_FILE = BASE_DIR / "pathwayai_county_assets.csv"

def append_csv_row_locked(path, row, stale_seconds=30):
    """Append one row with a short lock; expire stale locks left by crashed sessions."""
    import time
    path = Path(path)
    lock_path = Path(str(path) + ".lock")
    fd = None
    acquired = False
    try:
        for _ in range(40):
            if lock_path.exists():
                try:
                    if time.time() - lock_path.stat().st_mtime > stale_seconds:
                        lock_path.unlink()
                except Exception:
                    pass
            try:
                fd = os.open(str(lock_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                acquired = True
                break
            except FileExistsError:
                time.sleep(0.05)
        if fd is None:
            return False
        os.close(fd); fd = None
        pd.DataFrame([row]).to_csv(path, mode="a", header=not path.exists(), index=False)
        return True
    except Exception:
        return False
    finally:
        if fd is not None:
            try: os.close(fd)
            except Exception: pass
        try:
            if acquired and lock_path.exists(): lock_path.unlink()
        except Exception:
            pass

def usable_burden_numbers(values):
    """Keep finite nonnegative measurements; unknown/invalid values are not zero."""
    numbers = pd.to_numeric(values, errors="coerce")
    return numbers[numbers.notna() & numbers.map(lambda v: math.isfinite(v) if pd.notna(v) else False) & numbers.ge(0)]

def load_patient_voice(fips=None):
    cols = ["fips","delay_band","providers_seen","visits","oop_band","workdays","caregiver_hours","function","consent_time"]
    if not PATIENT_VOICE_FILE.exists():
        return pd.DataFrame(columns=cols)
    try:
        df = pd.read_csv(PATIENT_VOICE_FILE, dtype={"fips": str})
        for c in cols:
            if c not in df.columns: df[c] = None
        if fips is not None:
            df = df[df["fips"].astype(str).str.zfill(5) == str(fips).zfill(5)]
        return df[cols]
    except Exception:
        return pd.DataFrame(columns=cols)

def append_patient_voice(row):
    """Append reviewed structured fields only, using a small cross-platform lock file."""
    import time
    cols = ["fips","delay_band","providers_seen","visits","oop_band","workdays","caregiver_hours","function","consent_time"]
    lock_path = Path(str(PATIENT_VOICE_FILE) + ".lock")
    fd = None
    acquired = False
    try:
        for _ in range(40):
            if lock_path.exists():
                try:
                    if time.time() - lock_path.stat().st_mtime > 30:
                        lock_path.unlink()
                except Exception:
                    pass
            try:
                fd = os.open(str(lock_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                acquired = True
                break
            except FileExistsError:
                time.sleep(0.05)
        if fd is None:
            return False
        os.close(fd); fd = None
        new = pd.DataFrame([{c: row.get(c) for c in cols}])
        # Fail closed: never replace an unreadable or incompatible existing file.
        if PATIENT_VOICE_FILE.exists():
            old = pd.read_csv(PATIENT_VOICE_FILE, dtype={"fips": str})
            if not set(cols).issubset(old.columns):
                return False
            if set(old.columns) != set(cols):
                return False  # preserve unknown columns rather than silently discard them
            old = old[cols]
        else:
            old = pd.DataFrame(columns=cols)
        combined = pd.concat([old, new], ignore_index=True)
        tmp = Path(str(PATIENT_VOICE_FILE) + ".tmp")
        combined.to_csv(tmp, index=False)
        os.replace(tmp, PATIENT_VOICE_FILE)
        return True
    except Exception:
        return False
    finally:
        if fd is not None:
            try: os.close(fd)
            except Exception: pass
        try:
            if acquired and lock_path.exists(): lock_path.unlink()
        except Exception:
            pass

def load_county_assets(fips):
    if not COUNTY_ASSETS_FILE.exists():
        return pd.DataFrame(columns=["fips","name","owner","url","category"])
    try:
        df = pd.read_csv(COUNTY_ASSETS_FILE, dtype={"fips": str})
        return df[df["fips"].astype(str).str.zfill(5) == str(fips).zfill(5)].copy()
    except Exception:
        return pd.DataFrame(columns=["fips","name","owner","url","category"])

def local_lyme_cases_for_fips(fips):
    # Demo-safe: never download during page rendering. Use the local CDC workbook only.
    if not CDC_LYME_FILE.exists():
        return None
    try:
        return _cdc_lyme_cases_by_fips().get(str(fips).zfill(5))
    except Exception:
        return None

def fmt_missing(v, formatter=lambda x: str(x)):
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return "not yet collected"
    return formatter(v)


# -----------------------------
# PATHWAYAI MVP: ZIP + TRAVEL RISK + CARE NAVIGATION
# -----------------------------
# Pilot-area routing for the current PathwayAI MVP.
# ZIP code is used to select a pilot region; it is not used for diagnosis.
PILOT_ZIP_PREFIXES = {
    "Orange / Hudson Valley, New York": ("109",),
    "Dutchess County, New York": ("125", "126"),
    "Chester County, Pennsylvania": ("193", "194"),
    # Do not infer Carroll County from broad Maryland ZIP prefixes.
}

CARE_SEARCH_TERMS = {
    "Orange / Hudson Valley, New York": [
        "Lyme disease evaluation Orange County New York",
        "infectious disease Lyme disease Orange County New York",
    ],
    "Dutchess County, New York": [
        "Lyme disease specialist Dutchess County New York",
        "infectious disease Lyme disease Dutchess County New York",
    ],
    "Chester County, Pennsylvania": [
        "Lyme disease specialist Chester County Pennsylvania",
        "infectious disease Lyme disease Chester County Pennsylvania",
    ],
    "Carroll County, Maryland": [
        "Lyme disease specialist Carroll County Maryland",
        "infectious disease Lyme disease Carroll County Maryland",
    ],
}

SUPPORT_RESOURCES = [
    {
        "name": "Global Lyme Alliance — Patient Support",
        "description": "Provider directory, peer mentors, support groups, education, clinical trials, and financial-assistance resources.",
        "url": "https://www.globallymealliance.org/lyme-patient-support/",
    },
    {
        "name": "ILADS — Provider Search",
        "description": "Independent advocacy directory of ILADS members; approaches may differ from CDC guidance. Verify credentials and services directly.",
        "url": "https://www.ilads.org/patient-care/provider-search/",
    },
    {
        "name": "LymeDisease.org — Physician Directory",
        "description": "U.S. physician directory and patient education/support resources; registration may be required.",
        "url": "https://www.lymedisease.org/members/find-lyme-disease-specialist-3/",
    },
]

def normalize_zip(zip_code):
    return "".join(ch for ch in str(zip_code) if ch.isdigit())[:5]


HIGH_INCIDENCE_STATES = {
    "CT","DE","DC","ME","MD","MA","MN","NH","NJ","NY","PA","RI","VT","VA","WV","WI"
}

@st.cache_data(ttl=86400)
def resolve_us_zip(zip_code):
    """Resolve a U.S. ZIP to city/state and coordinates for display/navigation.
    Uses Zippopotam only for geographic lookup; health classifications come from CDC.
    """
    z = normalize_zip(zip_code)
    if len(z) != 5:
        return None
    try:
        url = f"https://api.zippopotam.us/us/{z}"
        with urllib.request.urlopen(url, timeout=8) as response:
            data = json.loads(response.read().decode("utf-8"))
        place = (data.get("places") or [{}])[0]
        return {
            "zip": z,
            "city": place.get("place name", ""),
            "state": place.get("state", ""),
            "state_code": place.get("state abbreviation", ""),
            "lat": float(place.get("latitude")) if place.get("latitude") else None,
            "lon": float(place.get("longitude")) if place.get("longitude") else None,
        }
    except Exception:
        return None

@st.cache_data(ttl=86400)
def load_cdc_ixodes_county_surveillance():
    """Load CDC county tick surveillance from the local demo file only."""
    if not CDC_TICK_FILE.exists():
        return pd.DataFrame()
    try:
        return pd.read_excel(CDC_TICK_FILE, sheet_name="Ixodes records 2025", header=1)
    except Exception:
        return pd.DataFrame()


def _cdc_tick_status_by_fips():
    """Normalize CDC Ixodes table to county FIPS -> blacklegged-tick status."""
    df = load_cdc_ixodes_county_surveillance()
    if df.empty:
        return {}
    df = df.copy()
    df.columns = [re.sub(r"[^a-z0-9]+", "_", str(c).strip().lower()).strip("_") for c in df.columns]

    # Locate county FIPS robustly.
    fips_col = next((c for c in df.columns if "fips" in c and ("county" in c or c == "fips")), None)
    if fips_col is None:
        fips_col = next((c for c in df.columns if "fips" in c), None)

    # CDC tables may use a direct I. scapularis status column, or species + status columns.
    scap_status_col = next((c for c in df.columns if "scapularis" in c and "status" in c), None)
    species_col = next((c for c in df.columns if c in ("species", "tick_species") or "species" in c), None)
    status_col = next((c for c in df.columns if c == "status" or c.endswith("_status")), None)

    if not fips_col:
        return {}

    out = {}
    for _, row in df.iterrows():
        raw = str(row.get(fips_col, "")).split(".")[0].strip()
        if not raw.isdigit():
            continue
        fips = raw.zfill(5)

        if scap_status_col:
            status_text = str(row.get(scap_status_col, "")).strip().lower()
        elif species_col and status_col:
            species_text = str(row.get(species_col, "")).lower()
            if "scapularis" not in species_text:
                continue
            status_text = str(row.get(status_col, "")).strip().lower()
        else:
            # Last-resort: inspect the row for an Ixodes scapularis + status phrase.
            row_text = " | ".join(str(v) for v in row.values).lower()
            if "scapularis" not in row_text:
                continue
            status_text = row_text

        if "established" in status_text:
            out[fips] = "Established"
        elif "reported" in status_text:
            out[fips] = "Reported"
    return out


def _geometry_centroid(geometry):
    """Approximate county centroid from exterior-ring coordinates for display markers."""
    if not geometry:
        return None
    coords = geometry.get("coordinates", [])
    gtype = geometry.get("type")
    polygons = [coords] if gtype == "Polygon" else coords if gtype == "MultiPolygon" else []
    pts = []
    for polygon in polygons:
        if polygon and polygon[0]:
            pts.extend(polygon[0])
    if not pts:
        return None
    return (sum(float(p[0]) for p in pts) / len(pts), sum(float(p[1]) for p in pts) / len(pts))


@st.cache_data(ttl=86400)
def load_cdc_county_lyme_cases():
    """Load CDC reported tickborne disease cases by county of residence, 2019-2022.

    Prefer a local copy for demo reliability. If it is missing, try CDC once and save it locally.
    """
    # Deployment-safe: never download a CDC workbook during page rendering.
    # Missing local evidence stays missing rather than becoming zero or another geography.
    if not CDC_LYME_FILE.exists():
        return pd.DataFrame()

    # CDC workbooks can change sheet/header formatting. Find the most plausible table.
    try:
        xls = pd.ExcelFile(CDC_LYME_FILE)
    except Exception:
        return pd.DataFrame()
    candidates = []
    for sheet in xls.sheet_names:
        for header in range(0, 5):
            try:
                df = pd.read_excel(CDC_LYME_FILE, sheet_name=sheet, header=header)
                cols = [re.sub(r"[^a-z0-9]+", "_", str(c).strip().lower()).strip("_") for c in df.columns]
                score = sum(any(k in c for c in cols) for k in ("lyme", "disease", "fips", "county", "case"))
                if score:
                    candidates.append((score, df))
            except Exception:
                pass
    if not candidates:
        return pd.DataFrame()
    candidates.sort(key=lambda x: x[0], reverse=True)
    return candidates[0][1]


def _cdc_lyme_cases_by_fips():
    """Return county FIPS -> reported Lyme disease cases, aggregating 2019-2022."""
    df = load_cdc_county_lyme_cases()
    if df.empty:
        return {}
    df = df.copy()
    df.columns = [re.sub(r"[^a-z0-9]+", "_", str(c).strip().lower()).strip("_") for c in df.columns]

    fips_col = next((c for c in df.columns if "fips" in c and ("county" in c or c == "fips")), None)
    if fips_col is None:
        fips_col = next((c for c in df.columns if "fips" in c), None)
    if not fips_col:
        return {}

    # Long format: disease is a row value (e.g., Lyme Disease).
    disease_col = next((c for c in df.columns if c in ("disease", "disease_name", "condition", "condition_name")), None)
    if disease_col:
        mask = df[disease_col].astype(str).str.contains("lyme", case=False, na=False)
        lyme = df.loc[mask].copy()
        if lyme.empty:
            return {}
        case_col = next((c for c in lyme.columns if ("case" in c or "count" in c) and pd.api.types.is_numeric_dtype(pd.to_numeric(lyme[c], errors="coerce"))), None)
        if case_col:
            lyme["_cases"] = pd.to_numeric(lyme[case_col], errors="coerce")
        else:
            # Some public-use files contain one record/point per reported case.
            lyme["_cases"] = 1
    else:
        # Wide format: a Lyme-specific numeric column.
        lyme_col = next((c for c in df.columns if "lyme" in c), None)
        if not lyme_col:
            return {}
        lyme = df.copy()
        lyme["_cases"] = pd.to_numeric(lyme[lyme_col], errors="coerce")

    def clean_fips(v):
        raw = re.sub(r"\.0$", "", str(v).strip())
        digits = re.sub(r"\D", "", raw)
        return digits.zfill(5) if digits else ""
    lyme["_fips"] = lyme[fips_col].map(clean_fips)
    lyme = lyme[lyme["_fips"].str.len() == 5]
    if lyme.empty:
        return {}
    totals = lyme.groupby("_fips")["_cases"].agg(lambda x: x.sum() if x.notna().all() else float("nan"))
    return totals.dropna().round().astype(int).to_dict()


def _destination_county_context(destination_geo, geo, tick_status, lyme_cases=None, max_nearby=8):
    """Approximate destination county from county centroids; return nearby county comparison."""
    if not destination_geo or destination_geo.get("lat") is None or destination_geo.get("lon") is None:
        return None, []
    lyme_cases = lyme_cases or {}
    dlat, dlon = float(destination_geo["lat"]), float(destination_geo["lon"])
    rows = []
    for feature in geo.get("features", []):
        center = _geometry_centroid(feature.get("geometry"))
        if not center:
            continue
        lon, lat = center
        dist2 = ((lon-dlon) * max(0.35, math.cos(math.radians(dlat))))**2 + (lat-dlat)**2
        fid = str(feature.get("id", "")).zfill(5)
        rows.append({
            "fips": fid,
            "county": str(feature.get("properties", {}).get("NAME", "County")),
            "state_fips": fid[:2],
            "tick": tick_status.get(fid, "No CDC record shown"),
            "lyme_cases": lyme_cases.get(fid),
            "dist2": dist2,
        })
    rows.sort(key=lambda x: x["dist2"])
    return (rows[0] if rows else None), rows[1:max_nearby+1]


def _lyme_fill(cases):
    """Sequential orange/red bins for reported county Lyme case counts, 2019-2022."""
    if cases is None:
        return "#f3f4f6"
    if cases == 0:
        return "#fff7ed"
    if cases < 25:
        return "#fed7aa"
    if cases < 100:
        return "#fdba74"
    if cases < 250:
        return "#fb923c"
    if cases < 500:
        return "#f97316"
    return "#dc2626"


def show_combined_tick_lyme_context(state_code=None, destination_geo=None):
    """Regional comparison: CDC tick status + reported human Lyme cases + destination."""
    try:
        geo = load_us_county_geojson()
        tick_status = _cdc_tick_status_by_fips()
        lyme_cases = _cdc_lyme_cases_by_fips()
        width, height = 900, 330

        if destination_geo and destination_geo.get("lat") is not None and destination_geo.get("lon") is not None:
            dlat = float(destination_geo["lat"]); dlon = float(destination_geo["lon"])
            bounds = (dlon - 5.8, dlat - 3.4, dlon + 5.8, dlat + 3.4)
        else:
            bounds = (-84.0, 34.5, -69.0, 45.5)

        parts = [f'<svg role="img" aria-label="New York observed tick surveillance by county" viewBox="0 0 {width} {height}" width="100%" height="100%" xmlns="http://www.w3.org/2000/svg"><title>Observed tick density by New York county; missing observations are gray</title>',
                 '<rect width="100%" height="100%" fill="#ffffff"/>']
        tick_markers = []
        visible_tick_count = 0
        min_lon, min_lat, max_lon, max_lat = bounds

        for feature in geo.get("features", []):
            center = _geometry_centroid(feature.get("geometry"))
            if not center:
                continue
            lon, lat = center
            if not (min_lon <= lon <= max_lon and min_lat <= lat <= max_lat):
                continue
            fid = str(feature.get("id", "")).zfill(5)
            tick = tick_status.get(fid)
            cases = lyme_cases.get(fid)
            fill = _lyme_fill(cases) if lyme_cases else "#f3f4f6"
            name = str(feature.get("properties", {}).get("NAME", "County"))
            tick_label = tick or "No CDC tick record shown"
            lyme_label = f"{cases:,} reported Lyme cases (2019-2022)" if cases is not None else "No county Lyme value loaded"
            title = html.escape(f"{name} County | Tick: {tick_label} | Human Lyme: {lyme_label}", quote=True)
            for d in _geom_paths(feature.get("geometry"), bounds, width, height):
                parts.append(f'<path d="{d}" fill="{fill}" stroke="#9ca3af" stroke-width="0.65"><title>{title}</title></path>')
            if tick:
                x, y = _project_svg(lon, lat, bounds, width, height, pad=28)
                r = 4.2 if tick == "Established" else 3.6
                marker_color = "#1473e6" if tick == "Established" else "#f4c430"
                tick_title = html.escape(f"{name} County | CDC blacklegged tick: {tick}", quote=True)
                tick_markers.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{marker_color}" fill-opacity="0.78" stroke="#ffffff" stroke-width="1.1"><title>{tick_title}</title></circle>')
                visible_tick_count += 1
        parts.extend(tick_markers)

        # Neutral city labels provide geographic orientation only; they are not surveillance markers.
        reference_cities = [
            ("New York City", -74.0060, 40.7128),
            ("Albany", -73.7562, 42.6526),
            ("Philadelphia", -75.1652, 39.9526),
        ]
        for city_name, city_lon, city_lat in reference_cities:
            if min_lon <= city_lon <= max_lon and min_lat <= city_lat <= max_lat:
                cx, cy = _project_svg(city_lon, city_lat, bounds, width, height, pad=28)
                # Small neutral crosshair + text; intentionally not a colored surveillance dot.
                parts.append(f'<line x1="{cx-3:.1f}" y1="{cy:.1f}" x2="{cx+3:.1f}" y2="{cy:.1f}" stroke="#374151" stroke-width="1"/>')
                parts.append(f'<line x1="{cx:.1f}" y1="{cy-3:.1f}" x2="{cx:.1f}" y2="{cy+3:.1f}" stroke="#374151" stroke-width="1"/>')
                parts.append(f'<text x="{cx+5:.1f}" y="{cy-5:.1f}" font-size="11" font-family="Arial, sans-serif" font-weight="600" fill="#374151" stroke="#ffffff" stroke-width="2.4" paint-order="stroke">{city_name}</text>')

        if destination_geo and destination_geo.get("lat") is not None and destination_geo.get("lon") is not None:
            x, y = _project_svg(float(destination_geo["lon"]), float(destination_geo["lat"]), bounds, width, height, pad=28)
            label = f"{destination_geo.get('city','Destination')}, {destination_geo.get('state_code','')}"
            safe_label = html.escape(label, quote=True)
            parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="8.8" fill="#16a34a" stroke="#ffffff" stroke-width="2.6"><title>Your destination: {safe_label}</title></circle>')
            parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="10.8" fill="none" stroke="#166534" stroke-width="1.5"/>')
            parts.append(f'<text x="{x+13:.1f}" y="{y-8:.1f}" font-size="12" font-family="Arial, sans-serif" font-weight="700" fill="#166534" stroke="#ffffff" stroke-width="2.8" paint-order="stroke">{html.escape(label)}</text>')
        parts.append('</svg>')
        components.html('<div style="background:#fff;border:1px solid #d1d5db;border-radius:10px;padding:6px;height:345px;overflow:hidden;">'+''.join(parts)+'</div>', height=365, scrolling=False)

        st.markdown("**Legend:** 🟢 Your destination &nbsp;&nbsp; 🔵 **Established** tick population &nbsp;&nbsp; 🟡 **Reported** tick presence &nbsp;&nbsp; Human Lyme cases: ⬜ no value → 🟧 fewer → 🟥 more reported cases")
        if lyme_cases:
            st.caption("Human Lyme shading = CDC cumulative reported Lyme disease cases by county of residence, 2019–2022: 0, 1–24, 25–99, 100–249, 250–499, 500+. Darker red means more reported cases, not an individual's infection probability.")
            st.info('**Read separately:** shading shows human case counts; markers show tick surveillance.')

        dest_county, nearby = _destination_county_context(destination_geo, geo, tick_status, lyme_cases)
        if dest_county:
            nearby_est = sum(1 for x in nearby if x["tick"] == "Established")
            nearby_rep = sum(1 for x in nearby if x["tick"] == "Reported")
            nearby_values = [x["lyme_cases"] for x in nearby if x["lyme_cases"] is not None]
            dest_cases = dest_county["lyme_cases"]
            st.markdown("### Destination Comparison")
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Approximate county", dest_county["county"])
            c2.metric("Blacklegged tick", dest_county["tick"])
            c3.markdown(f"**Nearby tick surveillance**\n\n{nearby_est} counties: established population\n\n{nearby_rep} counties: reported-only presence")
            c4.metric("Reported cases, 2019–2022", f"{dest_cases:,}" if dest_cases is not None else "Data not loaded")
            st.caption("County assignment uses the closest county center and is approximate. Nearby counties are the nearest county centers, not necessarily bordering counties. Case totals cover 2019–2022 and describe residents; they do not predict your travel infection risk.")
            if dest_cases is not None and nearby_values:
                med = sorted(nearby_values)[len(nearby_values)//2]
                if dest_cases > med:
                    comp = "above"
                elif dest_cases < med:
                    comp = "below"
                else:
                    comp = "similar to"
                annual_avg = dest_cases / 4.0
                regional_values = sorted([v for v in nearby_values + [dest_cases] if v is not None], reverse=True)
                visible_rank = regional_values.index(dest_cases) + 1 if dest_cases in regional_values else None
                st.markdown("#### Geographic context at a glance")
                g1, g2, g3 = st.columns(3)
                g1.metric("4-year reported cases", f"{dest_cases:,}")
                g2.metric("Average / year", f"{annual_avg:,.0f}", help="Simple annual average of 2019–2022 reported cases; not an incidence rate.")
                g3.metric("Nearby comparison", f"{comp.capitalize()} median", help=f"Nearby-county median shown: {med:,} cumulative reported cases.")
                st.caption(f"The destination county's 2019–2022 reported case count is {comp} the median of nearby counties shown ({med:,}). Counts are useful for burden context but are **not incidence rates** because county population sizes differ. PathwayAI therefore does not label this as personal risk.")
            else:
                st.info('County Lyme case data are unavailable.')

        if not tick_status:
            st.warning("CDC tick surveillance file is missing or unreadable. Put cdc_ixodes_county_2025.xlsx in the same folder as this app.")
        elif visible_tick_count == 0:
            st.info("CDC tick surveillance loaded, but no established/reported county markers fall inside this regional view. This does not mean ticks are absent.")
        else:
            st.caption(f"CDC tick surveillance loaded: {visible_tick_count} county markers are visible. Blue = Established; yellow = Reported.")
        if not lyme_cases:
            st.warning("CDC county Lyme workbook is not available. For reliable offline demos, download CDC's ‘Reported Tickborne Disease Cases by County of Residence 2019-2022.xlsx’ and save it beside this app as cdc_tickborne_county_2019_2022.xlsx.")

        st.caption("Human Lyme surveillance is reported by county of residence, not necessarily county of exposure. Surveillance can undercount disease and reporting practices vary. Tick status and human case counts are separate surveillance measures; neither is an individual infection probability.")
    except Exception as e:
        st.warning(f"The combined surveillance map could not load: {e}")

def destination_label(zip_code):
    """Resolve ZIP to a patient-friendly destination label when possible."""
    z = normalize_zip(zip_code)
    if len(z) != 5:
        return "ZIP not entered"
    geo = resolve_us_zip(z)
    if geo and geo.get("city") and geo.get("state"):
        return f"{geo['city']}, {geo['state']}"
    # Do not infer a county when the external ZIP resolver is unavailable.
    return f"U.S. ZIP {z}"


def clean_location_phrase(value):
    """Conservatively remove obvious symptom/narrative spillover from a place phrase."""
    s = (value or "").strip(" ,.;:-")
    if not s:
        return ""
    # These words usually begin the next clause rather than belonging to a U.S. place name.
    spill = re.compile(
        r"\s+(?:and\s+)?(?:i\s+)?(?:felt|feel|was|am|became|got|have|had|started|developed|"
        r"dizzy|sleepy|tired|fatigued|weak|sick|ill|confused|fainted|fever|headache|"
        r"since\s+then|after\s+that)\b.*$",
        re.I,
    )
    s = spill.sub("", s).strip(" ,.;:-")
    # Stop before obvious time-course phrases accidentally captured as part of a place.
    s = re.sub(r"\s+(?:one|two|three|four|five|six|seven|eight|nine|ten|\d+)\s+(?:day|days|week|weeks|month|months)\s+(?:later|after|afterward|afterwards)?\b.*$", "", s, flags=re.I).strip(" ,.;:-")
    return s


def extract_quick_story(text):
    """Low-burden, explainable extraction from a patient's free-text story.

    MVP note: this is deterministic NLP/rule-based extraction, not diagnosis and not an LLM.
    Extracted values are shown back to the patient for review and can be edited below.
    """
    raw = (text or "").strip()
    low = raw.lower()
    zmatch = re.search(r"(?<!\d)(\d{5})(?!\d)", raw)
    z = zmatch.group(1) if zmatch else ""

    # Age is a patient fact: only capture it when explicitly stated.
    age_value = None
    age_patterns = [
        r"\b(?:i am|i'm|im|age|aged)\s*(\d{1,3})\b",
        r"\b(\d{1,3})\s*(?:years? old|yo|y/o)\b",
    ]
    for ap in age_patterns:
        am = re.search(ap, low)
        if am:
            try:
                candidate = int(am.group(1))
                if 1 <= candidate <= 120:
                    age_value = candidate
                    break
            except Exception:
                pass
    month_aliases = {
        "january":["january","jan"], "february":["february","feb"], "march":["march","mar"],
        "april":["april","apr"], "may":["may"], "june":["june","jun"], "july":["july","jul"],
        "august":["august","aug"], "september":["september","sept","sep"], "october":["october","oct"],
        "november":["november","nov"], "december":["december","dec"]
    }
    matched_months = []
    for canonical, aliases in month_aliases.items():
        if any(re.search(rf"\b{re.escape(a)}\b", low) for a in aliases):
            matched_months.append(canonical.title())
    # A single month can be documented; multiple months are left for patient review rather than guessed.
    found_month = matched_months[0] if len(matched_months) == 1 else ""
    symptom_terms = {
        "fatigue / excessive sleepiness": ["fatigue", "tired", "exhaust", "weak", "weakness", "sleepy", "sleepiness", "slept", "sleeping", "stay awake", "stayed awake", "in bed", "bedridden"],
        "dizziness": ["dizzy", "dizziness"],
        "cognitive difficulty": ["brain fog", "concentrat", "memory", "confus"],
        "fever": ["fever"],
        "headache": ["headache"],
        "muscle/joint pain": ["joint pain", "muscle pain", "aches", "aching"],
        "rash": ["rash", "bullseye", "bull's-eye"],
    }
    found_symptoms = [name for name, terms in symptom_terms.items() if any(t in low for t in terms)]
    tick = "Yes" if re.search(r"\btick\s*(?:bite|bit|bitten|attached)?\b|\bbitten\s+by\s+(?:a\s+)?tick\b", low) else ("Unsure" if "tick" in low else "")
    no_test = bool(re.search(r"\b(?:no|not)\s+(?:lyme\s+|blood\s+)?test(?:ing|ed)?\b|\bnever\s+(?:got|had)\s+(?:a\s+)?test", low))
    tested = "No" if no_test else ("Yes" if any(t in low for t in ["lyme test", "tested", "test result", "blood test"]) else "")

    function_flags=[]
    work_impact = "Not reported"
    daily_function = "Not reported"
    unable_work = any(t in low for t in ["can't work", "cannot work", "couldn't work", "could not work", "unable to work", "stopped working", "too weak to work", "lost job", "lost my job", "had to quit", "quit my job", "out of work", "off work", "off from work", "couldn't go to work", "could not go to work", "unable to go to work", "haven't been able to work", "have not been able to work"])
    missed_work = any(t in low for t in ["missed work", "miss work", "missed school", "miss school"])
    reduced_work = any(t in low for t in ["reduced hours", "cut back hours", "working less"])
    if unable_work:
        function_flags.append("unable to work/school")
        work_impact = "Stopped working or school"
        daily_function = "Major limitation"
    elif missed_work:
        function_flags.append("missed work/school")
        work_impact = "Missed work or school"
        daily_function = "Some limitation"
    elif reduced_work:
        function_flags.append("reduced work/school")
        work_impact = "Reduced hours"
        daily_function = "Some limitation"
    if any(t in low for t in ["can't drive", "cannot drive", "couldn't drive", "trouble driving"]):
        function_flags.append("driving affected")
        daily_function = "Major limitation"
    if any(t in low for t in ["daily activities", "usual activities", "need help", "can't cook", "cannot cook", "couldn't cook", "unable to do normal"]):
        function_flags.append("daily activities affected")
        if daily_function == "Not reported": daily_function = "Major limitation"

    # Capture a simple duration attached to work/school limitation.
    days_missed = None
    duration_text = ""
    work_duration_patterns = [
        r"(?:out of work|off work|off from work|unable to work|couldn.t work|could not work|missed work)[^.!?]{0,25}?(?:for\s+)?(\d+(?:\.\d+)?)\s*(day|days|week|weeks|month|months)",
        r"(?:for\s+)?(\d+(?:\.\d+)?)\s*(day|days|week|weeks|month|months)[^.!?]{0,25}?(?:out of work|off work|unable to work|missed work)",
    ]
    duration_patterns = [
        (r"(?:for|about|approximately|around)\s+(\d+(?:\.\d+)?)\s*(day|days|week|weeks|month|months)", True),
        (r"\b(\d+(?:\.\d+)?)\s*(day|days|week|weeks|month|months)\b", True),
    ]
    # Normalize common spoken number words for duration extraction.
    duration_low = low
    for word, number in {"one":"1","two":"2","three":"3","four":"4","five":"5","six":"6","seven":"7","eight":"8","nine":"9","ten":"10"}.items():
        duration_low = re.sub(rf"\b{word}\b", number, duration_low)
    # Only convert a duration to workdays when the duration is explicitly attached to work impact.
    for pat in work_duration_patterns:
        wm = re.search(pat, duration_low)
        if wm:
            n=float(wm.group(1)); unit=wm.group(2)
            if unit.startswith('day'): days_missed=int(round(n))
            elif unit.startswith('week'): days_missed=int(round(n*5))
            elif unit.startswith('month'): days_missed=int(round(n*21.7))
            break
    for pat, generic in duration_patterns:
        m = re.search(pat, duration_low)
        if m:
            n=float(m.group(1)); unit=m.group(2)
            duration_text=f"{n:g} {unit if n == 1 else (unit if unit.endswith('s') else unit + 's')}"
            break

    # Keep exposure location separate from current/home location.
    # Capture free-text place phrases conservatively; patient can confirm/edit.
    exposure_location = ""
    current_location = ""
    exposure_patterns = [
        r"(?:visited|traveled to|travelled to|was in|went to)\s+([A-Za-z][A-Za-z .'-]+?(?:County)?)(?=\s+(?:in\s+(?:january|jan|february|feb|march|mar|april|apr|may|june|jun|july|jul|august|aug|september|sept|sep|october|oct|november|nov|december|dec)\b|and|where|when|then|but|was|got|tick\b|i\b)|[,.!?]|$)",
        r"(?:bitten|bite|tick bite)\s+(?:in|at|near)\s+([A-Za-z][A-Za-z .'-]+?(?:County)?(?:,\s*[A-Z]{2}|,\s*[A-Za-z ]+)?)(?=[,.!?]|$)"
    ]
    for pat in exposure_patterns:
        lm = re.search(pat, raw, flags=re.I)
        if lm:
            exposure_location = clean_location_phrase(lm.group(1))
            break
    current_patterns = [
        r"(?:now|currently)\s+(?:I(?:'m| am)\s+)?(?:back\s+)?(?:home\s+)?(?:in|at)\s+([A-Za-z][A-Za-z .'-]+?(?:County)?(?:,\s*[A-Z]{2}|,\s*[A-Za-z ]+)?)(?=[,.!?]|$)",
        r"(?:returned|came back|went back)\s+(?:home\s+)?(?:to\s+|in\s+)?([A-Za-z][A-Za-z .'-]+?(?:County)?(?:,\s*[A-Z]{2}|,\s*[A-Za-z ]+)?)(?=[,.!?]|$)",
        r"\bback\s+(?:home\s+)?(?:in|to)\s+([A-Za-z][A-Za-z .'-]+?(?:County)?(?:,\s*[A-Z]{2}|,\s*[A-Za-z ]+)?)(?=[,.!?]|$)",
        r"(?:live|living|home)\s+(?:is\s+)?(?:in|at)\s+([A-Za-z][A-Za-z .'-]+?(?:County)?(?:,\s*[A-Z]{2}|,\s*[A-Za-z ]+)?)(?=[,.!?]|$)"
    ]
    for pat in current_patterns:
        lm = re.search(pat, raw, flags=re.I)
        if lm:
            current_location = clean_location_phrase(lm.group(1))
            break

    # Providers seen: numeric or common number words near doctor/clinician/provider.
    providers_seen = None
    pm = re.search(r"(?:saw|seen|visited|went to)\s+(\d+)\s+(?:doctors?|clinicians?|providers?|healthcare professionals?)", low)
    if pm: providers_seen=int(pm.group(1))
    if providers_seen is None:
        words={"one":1,"two":2,"three":3,"four":4,"five":5,"six":6,"seven":7,"eight":8,"nine":9,"ten":10}
        pm=re.search(r"(?:saw|seen|visited|went to)\s+(one|two|three|four|five|six|seven|eight|nine|ten)\s+(?:doctors?|clinicians?|providers?|healthcare professionals?)", low)
        if pm: providers_seen=words[pm.group(1)]

    # Patient-reported dollar amount; keep it as a transparent story extraction.
    cost_amount = None
    cm = re.search(r"\$\s*([0-9][0-9,]*(?:\.[0-9]{1,2})?)", raw)
    if not cm:
        cm = re.search(r"\b(?:spent|paid|cost(?:\s+me)?)\s+(?:about\s+|around\s+|approximately\s+)?(?:\$\s*)?([0-9][0-9,]*(?:\.[0-9]{1,2})?)\b", raw, flags=re.I)
    if cm:
        try: cost_amount=float(cm.group(1).replace(',', ''))
        except Exception: pass
    return {"zip":z, "month":found_month, "symptoms":found_symptoms, "tick":tick, "tested":tested,
            "function":function_flags, "daily_function":daily_function, "work_impact":work_impact,
            "days_missed":days_missed, "duration_text":duration_text, "providers_seen":providers_seen,
            "cost_amount":cost_amount, "exposure_location":exposure_location,
            "current_location":current_location, "age":age_value}


def latest_tick_record(frame, county="Dutchess"):
    """Select the latest valid year; incomplete source rows cannot drive metrics."""
    required = {"County", "Year", "Tick Population Density", "B. burgdorferi (%)", "Total Ticks Collected", "Total Tested"}
    if frame.empty or not required.issubset(frame.columns):
        return None
    rows = frame[frame["County"].astype(str).str.contains(county, case=False, na=False)].copy()
    rows["Year"] = pd.to_numeric(rows["Year"], errors="coerce")
    for field in ("Tick Population Density", "Total Ticks Collected", "Total Tested"):
        rows[field] = pd.to_numeric(rows[field], errors="coerce")
    rows = rows.dropna(subset=["Year", "Tick Population Density", "Total Ticks Collected", "Total Tested"])
    rows = rows[(rows["Year"] >= 1900) & (rows["Year"] <= pd.Timestamp.today().year)]
    rows = rows[(rows[["Tick Population Density", "Total Ticks Collected", "Total Tested"]] >= 0).all(axis=1)]
    return None if rows.empty else rows.sort_values("Year", ascending=False).iloc[0]


def validate_story_result(record):
    """Reject malformed model output; this validates structure, not factual accuracy."""
    keys = {"exposure_location", "current_location", "tick_bite", "symptoms", "duration_text",
            "test_status", "test_result", "test_timing", "providers_seen", "daily_function",
            "work_impact", "days_missed", "cost_amount", "diagnostic_delay", "prior_diagnoses", "age"}
    if not isinstance(record, dict) or set(record) != keys:
        raise ValueError("Unexpected or missing story fields")
    numeric = {"providers_seen", "days_missed", "cost_amount", "age"}
    arrays = {"symptoms", "prior_diagnoses"}
    for key, value in record.items():
        if key in arrays:
            if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
                raise ValueError("Expected a list of text values")
        elif key in numeric:
            if value is not None:
                if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0:
                    raise ValueError("Invalid numeric value")
                if key != "cost_amount" and value != int(value):
                    raise ValueError("Expected a whole-number count")
                if key == "age" and value > 120:
                    raise ValueError("Age outside supported range")
        elif value is not None and not isinstance(value, str):
            raise ValueError("Expected text or null")
    if record["tick_bite"] not in (None, "Yes", "No", "Unsure"):
        raise ValueError("Invalid tick-bite category")
    return record


def extract_story_with_llm(text):
    """Optional MVP LLM extraction. Returns (parsed_dict_or_None, status_dict).

    The status is safe to show in a developer expander and never includes the API key.
    """
    api_key = OPENAI_API_KEY
    if not api_key:
        return None, {"state":"no_key", "message":"No API key detected in this app process."}
    if not (text or "").strip():
        return None, {"state":"empty", "message":"No story submitted."}

    instructions = """You are a structured information extractor for a Lyme patient-journey prototype.
Extract ONLY facts explicitly stated in the patient's text. Do not diagnose, infer causality,
invent dates, convert missing facts to zero/No, or add medical advice.
Keep exposure_location (where possible exposure happened) separate from current_location
(where the person is now). If a field is absent, use null; for arrays use [].
Return ONLY valid JSON with exactly these keys:
exposure_location, current_location, tick_bite, symptoms, duration_text,
test_status, test_result, test_timing, providers_seen, daily_function,
work_impact, days_missed, cost_amount, diagnostic_delay, prior_diagnoses, age.
tick_bite must be "Yes", "No", "Unsure", or null.
providers_seen, days_missed, cost_amount, age must be numbers or null.
symptoms and prior_diagnoses must be arrays of strings.
Do not convert a symptom duration into workdays. Only return days_missed if the patient explicitly states a number of days missed."""
    model = PATHWAYAI_LLM_MODEL
    if not model:
        return None, {"state":"no_model", "message":"No live model configured; using backup extraction."}
    payload = {
        "model": model,
        "store": False,
        "input": [
            {"role": "system", "content": instructions},
            {"role": "user", "content": text}
        ]
    }
    req = urllib.request.Request(
        "https://api.openai.com/v1/responses",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with _limited_ai_urlopen(req, timeout=45) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        output_text = ""
        for item in data.get("output", []):
            if item.get("type") == "message":
                for part in item.get("content", []):
                    if part.get("type") == "output_text":
                        output_text += part.get("text", "")
        cleaned = output_text.strip()
        if cleaned.startswith("```"):
            cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", cleaned, flags=re.I | re.S)
        parsed = json.loads(cleaned)
        if isinstance(parsed, dict):
            try:
                parsed = validate_story_result(parsed)
            except ValueError:
                return None, {"state":"validation_error", "message":"Model output failed field validation; using backup extraction. Please confirm all fields."}
            return parsed, {"state":"connected", "message":f"LLM connected ({model})."}
        return None, {"state":"parse_error", "message":"The model responded, but the structured result was not a JSON object."}
    except urllib.error.HTTPError as e:
        try:
            body = json.loads(e.read().decode("utf-8"))
            msg = body.get("error", {}).get("message", "")
        except Exception:
            msg = ""
        safe = (msg or f"HTTP {e.code}").replace(api_key, "[redacted]")[:500]
        return None, {"state":"api_error", "message":f"API HTTP {e.code}: {safe}"}
    except Exception as e:
        safe = str(e).replace(api_key, "[redacted]")[:500]
        return None, {"state":"error", "message":safe or "Unknown API connection error."}

def merge_llm_into_quick(rule_quick, llm):
    """Map LLM facts into the existing MVP record while preserving null = not reported."""
    q = dict(rule_quick)
    if not llm:
        q["extraction_method"] = "Rule-based NLP fallback"
        return q
    q["extraction_method"] = "LLM structured extraction"
    mapping = {
        "exposure_location":"exposure_location", "current_location":"current_location",
        "tick_bite":"tick", "duration_text":"duration_text", "providers_seen":"providers_seen",
        "daily_function":"daily_function", "work_impact":"work_impact",
        "days_missed":"days_missed", "cost_amount":"cost_amount", "age":"age"
    }
    for src, dst in mapping.items():
        val = llm.get(src)
        if val not in (None, "", []):
            if dst in ("exposure_location", "current_location"):
                val = clean_location_phrase(str(val))
            q[dst] = val
    if llm.get("symptoms"):
        q["symptoms"] = [str(x) for x in llm["symptoms"]]
    q["llm_test_status"] = llm.get("test_status")
    q["llm_test_result"] = llm.get("test_result")
    q["llm_test_timing"] = llm.get("test_timing")
    q["llm_diagnostic_delay"] = llm.get("diagnostic_delay")
    q["llm_prior_diagnoses"] = llm.get("prior_diagnoses") or []
    # Keep the patient-facing function/work summary consistent with LLM extraction.
    wi = str(q.get("work_impact") or "").lower()
    if wi and wi != "not reported":
        if any(x in wi for x in ["stop", "unable", "out of work", "lost job"]):
            q["function"] = ["unable to work/school"]
        elif "miss" in wi:
            q["function"] = ["missed work/school"]
        elif any(x in wi for x in ["reduced", "less", "cut back"]):
            q["function"] = ["reduced work/school"]
    return q


def show_immediate_support_from_story(quick):
    """Return immediate patient/caregiver value after story organization."""
    symptoms = quick.get("symptoms") or []
    duration = quick.get("duration_text") or ""
    function = quick.get("function") or []
    providers = quick.get("providers_seen")
    tested = quick.get("tested") or quick.get("llm_test_status")
    work_impact = quick.get("work_impact") or ""
    cost_amount = quick.get("cost_amount")
    if not bool(symptoms or duration or function or providers or tested or work_impact or cost_amount):
        return

    st.markdown("## 🧭 Your Journey in Context")
    st.write('Use your journey summary and relevant research to prepare for care. Research findings do not predict your outcome.')

    # A compact patient-specific journey line.
    stages = ["Exposure / concern"]
    if symptoms: stages.append("Symptoms")
    if tested: stages.append("Testing")
    if providers: stages.append("Care journey")
    if function or work_impact: stages.append("Function / work impact")
    stages.append("You are here")
    st.markdown("**Your journey:**  " + " → ".join(stages))

    st.markdown("### What research tells us")
    e1, e2, e3 = st.columns(3)
    for column, icon, title, finding in [
        (e1, "💳", "Care costs", "A claims study found higher healthcare spending and outpatient use among treated Lyme patients than matched controls."),
        (e2, "🧭", "Repeated visits", "An access-to-care survey described many visits before diagnosis. A clear history can help you prepare for your next visit."),
        (e3, "📅", "Follow-up", "The Biobank study found that some participants still had symptoms at follow-up. Record changes in daily life and discuss them with your clinician."),
    ]:
        with column:
            with st.container(border=True):
                st.markdown(icon + " **" + title + "**")
                st.write(finding)
    st.caption("Published study findings provide context; they do not predict your outcome.")
    with st.expander("Study details and sources", expanded=False):
        st.write("**Claims:** 52,795 treated Lyme patients and 263,975 matched controls; 12-month healthcare costs and outpatient use.")
        st.write("**Access to care:** 2,424 survey respondents; about half reported seven or more physicians before diagnosis. Selected respondents, not population prevalence.")
        st.write("**Biobank:** 55/253 (22%) reported ongoing symptoms at follow-up; 19/55 (35%) had seen a provider about them. Published aggregates, not a personal forecast.")
        st.markdown("[Claims study](https://doi.org/10.1371/journal.pone.0116767) · [Access-to-care study](https://doi.org/10.1016/j.healthpol.2011.05.007) · [Biobank study](https://doi.org/10.3389/fmed.2025.1577936)")

    # Surface only context that is relevant to what this person reported.
    if providers is not None and providers >= 4:
        st.info(f"**Your care journey:** You reported about {providers} healthcare professionals. Bring a concise visit history to your next appointment.")
    if tested:
        st.info("**Your testing journey:** Testing is best interpreted together with timing, symptoms, exposure history, and clinical evaluation. PathwayAI can help you organize those details and prepare questions; it does not interpret a test as a diagnosis.")
    if function or work_impact:
        st.info("**Your function matters:** Work, school, caregiving, and daily-activity effects are part of the burden of a health journey even when they do not appear on a medical bill. PathwayAI keeps these impacts visible for you and your caregiver.")

    st.markdown("### 👥 Prepare for Your Next Visit")
    st.write("**Bring or have ready:** your symptom timeline, testing dates/results, treatment or medication history, prior visit records, and the names/types of clinicians already seen.")
    questions = [
        "How should the timing of my testing be considered alongside my symptoms and exposure history?",
        "What follow-up is appropriate if my symptoms continue or change?",
        "Are there other conditions or explanations that should be evaluated?",
        "Would another clinical opinion be useful at this point, and what records should I bring?",
    ]
    st.write("**Questions you may want to discuss:**")
    for q in questions:
        st.write("• " + q)
    st.caption("These are preparation prompts, not treatment recommendations. A useful second opinion or clinically indicated follow-up is treated as potentially beneficial care—not automatically as waste or avoidable cost.")

    st.markdown("### What Might I Expect?")
    st.write('Experiences vary. Discuss new or worsening symptoms with a healthcare professional.')
    st.caption('Research context, not a prognosis.')

    st.markdown("### 📚 Knowledge Corner")
    with st.expander("🕷️ Know the Tick — what does it look like?"):
        st.write("Nymphs and adults have 8 legs; larvae have 6. Save a clear photo if possible. Size and appearance change after feeding.")
        st.markdown("[CDC tick lifecycle](https://www.cdc.gov/ticks/about/tick-lifecycles.html)")
    with st.expander("📅 After a Bite — what should I track?"):
        st.write("Record the date, location, tick/photo if available, and new symptoms. Prompt tick removal is recommended.")
        st.markdown("[CDC after a tick bite](https://www.cdc.gov/ticks/after-a-tick-bite/)")
    with st.expander("🧪 Understand Testing — why timing matters"):
        st.write("Antibody tests can be negative early. Keep the test date, result, exposure date, and symptom timeline together.")
        st.markdown("[CDC Lyme diagnosis and testing](https://www.cdc.gov/lyme/diagnosis-testing/index.html)")
    with st.expander("🩺 Another Opinion? — when might it help?"):
        st.write("If symptoms persist, the picture is unclear, or you have unanswered questions, ask whether another clinical opinion would be useful. Bring your timeline and prior records.")
    st.warning("If someone is very difficult to wake, newly confused, fainting, having trouble breathing, or has another severe or rapidly worsening symptom, seek urgent medical evaluation rather than relying on this tool.")

def infer_pilot_location(zip_code):
    z = normalize_zip(zip_code)
    if len(z) != 5:
        return None
    for location_name, prefixes in PILOT_ZIP_PREFIXES.items():
        if any(z.startswith(prefix) for prefix in prefixes):
            return location_name
    return None

def google_maps_search_url(query):
    return "https://www.google.com/maps/search/?api=1&query=" + quote_plus(query)

def show_care_support(zip_code, fallback_location=None):
    """Render non-endorsing care-navigation and patient-support resources."""
    z = normalize_zip(zip_code)
    pilot_location = infer_pilot_location(z) or fallback_location

    st.subheader("Care & Support Near You")

    if len(z) != 5:
        st.info("Enter a 5-digit ZIP code to personalize nearby care navigation.")
        return

    st.write(f"**ZIP code:** {z}")

    if pilot_location:
        st.write(f"**Pilot-area context:** {pilot_location}")
        searches = CARE_SEARCH_TERMS.get(pilot_location, [])
    else:
        st.info(
            "This ZIP code is outside the current NY/PA/MD pilot routing. "
            "You can still use the searches and national directories below."
        )
        searches = [
            f"Lyme disease specialist near {z}",
            f"infectious disease Lyme disease near {z}",
        ]

    st.write(
        'Compare nearby care options. Confirm credentials, insurance, appointments and services; listings are not endorsements.'
    )

    for i, search_term in enumerate(searches[:2], start=1):
        label = (
            "Lyme-focused care search"
            if i == 1
            else "Infectious-disease / Lyme care search"
        )
        st.markdown(
            f"**{i}. {label}**  \n"
            f"[Open Google Maps & current reviews]({google_maps_search_url(search_term)})"
        )

    st.caption(
        'Google reviews do not establish clinical quality.'
    )

    st.markdown("#### Lyme patient organizations & provider directories")
    for resource in SUPPORT_RESOURCES:
        st.markdown(
            f"**{resource['name']}** — {resource['description']}  \n"
            f"[Open resource]({resource['url']})"
        )

    st.info(
        "If test results, symptoms, or exposure history remain unclear, consider discussing "
        "with a qualified healthcare professional how the timing and type of testing affect "
        "interpretation and whether additional evaluation or a second clinical opinion is appropriate."
    )

    st.caption(
        "Care-navigation information only — not diagnosis, treatment advice, or an endorsement "
        "of any clinician or organization. Verify provider credentials, insurance, availability, "
        "and services directly."
    )


BENEFIT_RESOURCES = [
    ("211 — local social services", "https://www.211.org/", "Food, housing, utilities, transportation, caregiver and other community resources."),
    ("Social Security Disability", "https://www.ssa.gov/disability", "Federal disability-benefit information and application resources."),
    ("U.S. Department of Labor — FMLA", "https://www.dol.gov/agencies/whd/fmla", "Federal job-protected leave information for eligible workers and family caregivers."),
    ("USA.gov benefits", "https://www.usa.gov/benefits", "Government benefit finder covering health, income, food, housing and other programs."),
    ("HealthCare.gov", "https://www.healthcare.gov/", "Health coverage information; state Marketplace routing is provided where applicable."),
]

def show_financial_support(zip_code, work_impact, insurance_context, support_needs):
    """ZIP-guided resource navigation; never determines benefit eligibility."""
    z = normalize_zip(zip_code)
    st.subheader("Financial, Disability & Support Resources")
    if len(z) != 5:
        st.info("Enter a 5-digit U.S. ZIP code to personalize resource searches.")
        return
    st.write(f"**ZIP code:** {z}")
    if insurance_context not in ["Not reported", "Unsure / prefer not to answer", "No access or coverage barrier reported"]:
        st.write(f"**Access / coverage context:** {insurance_context}")
    if support_needs:
        st.write("**Support areas selected:** " + ", ".join(support_needs))
    if work_impact in ["Reduced hours", "Missed work or school", "Stopped working or school", "On disability"]:
        st.info("Because you reported work/function impact, disability and workplace-leave resources are included below. Eligibility depends on program-specific rules.")
    st.markdown(f"[Search 211 resources near ZIP {z}](https://www.google.com/search?q={quote_plus('211 benefits resources ZIP ' + z)})")
    st.markdown(f"[Search state/local disability and temporary-cash programs near ZIP {z}](https://www.google.com/search?q={quote_plus('state disability temporary cash assistance ZIP ' + z)})")
    for name, url, desc in BENEFIT_RESOURCES:
        st.markdown(f"**{name}** — {desc}  \n[Open resource]({url})")
    st.caption("Navigation only. PathwayAI does not determine eligibility, legal entitlement, or benefit amount. Verify requirements with the administering agency.")



def show_personalized_support(zip_code, work_impact, insurance_context, support_needs, burden_drivers, current_location_text=""):
    """Show only the most relevant support first; keep directories and full lists collapsed."""
    z = normalize_zip(zip_code)
    pilot_location = infer_pilot_location(z) if len(z) == 5 else None
    loc = (current_location_text or "").strip() or (f"ZIP {z}" if len(z) == 5 else "your current area")

    st.subheader("🧭 What May Help You Now")
    st.caption('Start with the actions relevant to your story. Add a location for nearby resources.')

    # Explain why the resources are appearing.
    if burden_drivers:
        st.write("**Burden signals guiding these suggestions:** " + ", ".join(burden_drivers[:4]))
    else:
        st.write("**Burden signals:** not enough information yet to prioritize financial or work-related support.")

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**1. Care & testing near you**")
        if len(z) == 5:
            if pilot_location:
                st.write(f"Current routing context: **{pilot_location}**")
                search_terms = CARE_SEARCH_TERMS.get(pilot_location, [f"Lyme disease evaluation near {z}"])
            else:
                search_terms = [f"Lyme disease evaluation near {z}", f"infectious disease Lyme disease near {z}"]
            st.markdown(f"[Find clinical evaluation near {loc}]({google_maps_search_url(search_terms[0])})")
            st.markdown(f"[Find infectious-disease / Lyme care near {loc}]({google_maps_search_url(search_terms[-1])})")
        elif current_location_text.strip():
            search_terms = [f"Lyme disease evaluation near {loc}", f"infectious disease Lyme disease near {loc}"]
            st.markdown(f"[Find clinical evaluation near {loc}]({google_maps_search_url(search_terms[0])})")
            st.markdown(f"[Find infectious-disease / Lyme care near {loc}]({google_maps_search_url(search_terms[-1])})")
            st.caption("City/county-level navigation from your story. Add a ZIP code only if you want more precise nearby results.")
        else:
            st.write("Add your current city, county, or ZIP code to tailor nearby healthcare navigation.")
        st.caption("Compare credentials, insurance participation, availability, and services directly. PathwayAI does not endorse providers.")

    with c2:
        st.markdown("**2. Work, financial & daily-life support**")
        work_flag = work_impact in ["Reduced hours", "Missed work or school", "Stopped working or school", "On disability"]
        disability_flag = work_impact in ["Stopped working or school", "On disability"] or "Disability benefits" in support_needs
        coverage_flag = insurance_context not in ["Not reported", "Unsure / prefer not to answer", "No access or coverage barrier reported"] or "Health coverage" in support_needs

        if work_flag:
            st.markdown("[Workplace leave / FMLA](https://www.dol.gov/agencies/whd/fmla)")
        if disability_flag:
            st.markdown("[Social Security disability information](https://www.ssa.gov/disability)")
        if coverage_flag:
            st.markdown("[Health coverage information](https://www.healthcare.gov/)")
        if (len(z) == 5 or current_location_text.strip()) and (support_needs or work_flag or coverage_flag):
            st.markdown(f"[Local 211/community support near {loc}](https://www.google.com/search?q={quote_plus('211 community support ' + loc)})")
        if not (work_flag or disability_flag or coverage_flag or support_needs):
            st.write("No specific work/financial support need was reported. You can open the full resource list below if useful.")

    st.markdown("**3. How these actions could change the burden**")
    actions = []
    if "repeat testing / additional opinions" in burden_drivers:
        actions.append("better care continuity may reduce avoidable repeated visits or testing")
    if "work/school loss" in burden_drivers or work_impact in ["Reduced hours", "Missed work or school", "Stopped working or school", "On disability"]:
        actions.append("workplace leave or disability navigation may help protect income and document limitations")
    if "transportation / lodging" in burden_drivers:
        actions.append("closer or coordinated care may reduce travel burden")
    if "access / coverage barriers" in burden_drivers or coverage_flag:
        actions.append("coverage navigation may reduce delayed/skipped care or unexpected out-of-pocket costs")
    if actions:
        for action in actions:
            st.write("• " + action.capitalize() + ".")
    else:
        st.write("As more burden information is confirmed, PathwayAI can show which support pathway is most relevant.")

    with st.expander("See all healthcare directories and support resources"):
        if len(z) == 5:
            st.markdown(f"[Search 211 resources near ZIP {z}](https://www.google.com/search?q={quote_plus('211 benefits resources ZIP ' + z)})")
            st.markdown(f"[Search state/local disability and cash-assistance programs near ZIP {z}](https://www.google.com/search?q={quote_plus('state disability temporary cash assistance ZIP ' + z)})")
        for name, url, desc in BENEFIT_RESOURCES:
            st.markdown(f"**{name}** — {desc}  \n[Open resource]({url})")
        st.markdown("**Independent advocacy organizations / directories · not federal referrals**")
        for resource in SUPPORT_RESOURCES:
            st.markdown(f"**{resource['name']}** — {resource['description']}  \n[Open resource]({resource['url']})")

    st.caption("Navigation only. PathwayAI does not determine eligibility, legal entitlement, benefit amount, diagnosis, or treatment. Verify requirements and provider information directly.")


# -----------------------------


# ============================================================
# PATHWAYAI v41 — BUILT-IN HHS / TOPx RESEARCH KNOWLEDGE
# ============================================================

PATHWAYAI_HHS_KNOWLEDGE = [
    {"id":"cms_office_hours_2026_10","category":"HHS / CMS opportunity",
     "source":"TOPx Office Hours announcement and submitted PathwayAI questions",
     "text":"CMS Office of Enterprise Data and Analytics colleagues Mindy Cohen, Deputy Director, Policy and Data Analytics Group, and Leo Meister, Data Scientist, are scheduled for October 8 and October 15 Office Hours. PathwayAI submitted three linked questions: (1) For conditions with delayed diagnosis, how can CMS data help identify the invisible patient journey before diagnosis? (2) Which CMS data sources or measures are most useful for quantifying healthcare utilization and costs during this pre-diagnosis period? (3) How can this type of analysis be designed to be most useful and actionable for policymakers? Treat CMS data as an opportunity/question, not as data already integrated into PathwayAI."},
    {"id":"organizer_mvp_showcase", "category":"HHS / MVP showcase template",
     "source":"Organizer-provided MVP Demo Milestone.pptx, reviewed October 7, 2026",
     "text":"MVP Walkthrough: show the completed product journey and core features, communities/user advocates involved, who tested it and what was learned. Impact & Evidence: identify end users, federal datasets incorporated, and documented user-validation results. Deployment Strategy: explain launch plan, sustainability model, continued development roadmap and how others can support the tool. Do not invent testing participants, results, partnerships, deployment or adoption."},
    {"id":"topx_final_submission","category":"HHS / final submission requirements",
     "source":"TOPx Phase 2 Submission Form mockup",
     "text":"The final submission should demonstrate the MVP and core functionality/intended use; identify target users and show how the solution fits a real-world workflow; explain the open and/or other data sources and how technology enables the solution; show value such as improved insight, decision-making, care coordination, efficiency, or return on investment; and explain scalability, reuse, assumptions, and next steps."},
    {"id":"beta_general_feedback","category":"HHS / Beta feedback",
     "source":"Cost of Illness Beta Demo transcript",
     "text":"Federal feedback emphasized showing what is working and not working, data needs, and readiness for the final presentation. Across demonstrations, feedback repeatedly emphasized usability, avoiding information overload, transparency of evidence and assumptions, and making outputs actionable."},
    {"id":"beta_cost_feedback","category":"HHS / cost-of-illness feedback",
     "source":"Cost of Illness Beta Demo transcript",
     "text":"For policy-oriented cost tools, feedback emphasized distinguishing where burden occurs: healthcare-system costs, patient out-of-pocket costs, and less-visible burdens such as work, caregiving, transportation, and functional impact. The purpose is not only to show a large total but to help identify where intervention could have the greatest impact. Sources and methodological assumptions behind projected numbers should be transparent."},
    {"id":"pathwayai_beta_positioning","category":"PathwayAI / current positioning",
     "source":"PathwayAI Beta presentation",
     "text":"PathwayAI's primary users are policymakers and public-health leaders, while the journey starts with patients and caregivers. The concept follows prevent, navigate, support, act. It captures exposure, symptoms, doctor visits, diagnostic delay, daily function, missed work, disability-related impact, and out-of-pocket cost. Population Insights is intended to identify patterns in diagnostic delay, financial burden, disability, and unmet needs. The final MVP asks: Where does burden begin? How does it build over time? Who is most affected? Where could early action make a difference?"},
    {"id":"competitor_topolis","category":"Competitor / Topolis","source":"Cost of Illness Beta Demo transcript",
     "text":"Topolis described an agent-based approach focused initially on POTS. Its agents simulate how a patient might navigate the web to discover plausible care resources, verify actionable next steps, and provide evidence and links from care-site websites. This overlaps most with PathwayAI care navigation, not its county burden/policy focus."},
    {"id":"competitor_signalbridge","category":"Competitor / SignalBridge","source":"Cost of Illness Beta Demo transcript",
     "text":"SignalBridge connects illness, work, care, and money, covering many conditions and modeled scenarios. It demonstrated MEPS-based out-of-pocket and all-payer care measures, burden over time, uncertainty, demographic filtering, resources, peer support, and route/cost planning. Federal feedback asked whether the interface could make the most important insights easier to find and avoid overwhelming users."},
    {"id":"competitor_impactfile","category":"Competitor / Impact File","source":"Cost of Illness Beta Demo transcript",
     "text":"Impact File captures lived-experience evidence such as medical care, functional limitations, missed work, time lost, caregiving, receipts, documents, and clinical information. It structures this evidence for uses such as medical leave, disability, insurance appeals, accommodations, doctor communication, and taxes. The user reviews AI-extracted evidence before saving it. Its strength is longitudinal evidence documentation."},
    {"id":"competitor_healthful","category":"Competitor / Healthful","source":"Cost of Illness Beta Demo transcript",
     "text":"Healthful presented a policy/economic modeling platform initially focused on Long COVID. It described AI-assisted extraction across many data sources, a smaller curated evidence set for modeling, strict source provenance, analyst-selectable assumptions, sensitivity analysis, and macroeconomic intervention scenarios. Federal feedback emphasized breaking total burden into healthcare, out-of-pocket, and invisible cost components and using those components to identify where intervention could create the largest gains."}
]

PATHWAYAI_AGENT_TEST_QUESTIONS = [
    "What are my top three priorities before the final PathwayAI MVP?",
    "Where is PathwayAI differentiated from the other Cost of Illness teams?",
    "What does HHS Beta feedback suggest I should change?",
    "How could CMS data strengthen the invisible pre-diagnosis journey analysis?",
    "What should I NOT add before the final demo?"
]

def search_builtin_hhs_knowledge(query, max_results=7):
    q = (query or "").lower().strip()
    terms = [t for t in re.findall(r"[a-z0-9]+", q) if len(t) > 2]
    scored = []
    for item in PATHWAYAI_HHS_KNOWLEDGE:
        hay = " ".join([item.get("category",""), item.get("source",""), item.get("text","")]).lower()
        score = sum(hay.count(t) for t in terms)
        if any(x in q for x in ["priority","priorities","final","mvp","improve","change","should i","should we"]):
            if item["id"] in {"topx_final_submission","beta_general_feedback","beta_cost_feedback","pathwayai_beta_positioning"}:
                score += 4
        if "cms" in q and item["id"] == "cms_office_hours_2026_10":
            score += 6
        if any(x in q for x in ["competitor","different","differentiate","overlap"]):
            if item.get("category","").startswith("Competitor"):
                score += 5
        if any(x in q for x in ["cost","burden","economic","intervention"]):
            if item["id"] in {"beta_cost_feedback","competitor_signalbridge","competitor_healthful","pathwayai_beta_positioning"}:
                score += 3
        if score > 0:
            scored.append((score, item))
    scored.sort(key=lambda x: x[0], reverse=True)
    selected = [item for _, item in scored[:max_results]]
    return selected or PATHWAYAI_HHS_KNOWLEDGE[:max_results]

def format_builtin_hhs_results(items):
    return "\n\n".join(
        f"[{item['category']}]\nSource: {item['source']}\n{item['text']}" for item in items
    )

# PATHWAYAI RESEARCH & STRATEGY AGENT (v40 prototype)
# -----------------------------
AGENT_KNOWLEDGE_DIR = BASE_DIR / "agent_knowledge"
AGENT_HHS_DIR = AGENT_KNOWLEDGE_DIR / "hhs"
AGENT_COMPETITOR_DIR = AGENT_KNOWLEDGE_DIR / "competitors"
AGENT_PROJECT_DIR = AGENT_KNOWLEDGE_DIR / "pathwayai"


def _safe_text_files(folder):
    """Read small local knowledge files only; no patient-level files are exposed to the agent."""
    if not folder.exists():
        return []
    rows = []
    for path in sorted(folder.glob("*")):
        if path.suffix.lower() not in {".txt", ".md", ".csv"} or not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")[:40000]
            rows.append((path.name, text))
        except Exception:
            pass
    return rows


def _keyword_score(query, text):
    terms = [t for t in re.findall(r"[a-z0-9]+", (query or "").lower()) if len(t) > 2]
    low = (text or "").lower()
    return sum(low.count(t) for t in set(terms))


def _search_local_knowledge(folder, query, label, max_items=4):
    docs = _safe_text_files(folder)
    if not docs:
        return {"tool": label, "status": "not_loaded", "items": [],
                "note": f"No local {label} files are loaded yet."}
    ranked = sorted(docs, key=lambda x: _keyword_score(query, x[1]), reverse=True)
    items = []
    for name, body in ranked[:max_items]:
        # Keep returned context bounded and auditable.
        compact = re.sub(r"\s+", " ", body).strip()
        items.append({"file": name, "excerpt": compact[:3500]})
    return {"tool": label, "status": "ok", "items": items}


def agent_search_hhs(query):
    return _search_local_knowledge(AGENT_HHS_DIR, query, "HHS Tech Sprint")


def agent_search_competitors(query):
    return _search_local_knowledge(AGENT_COMPETITOR_DIR, query, "competitor notes")


def agent_search_pathwayai(query):
    local = _search_local_knowledge(AGENT_PROJECT_DIR, query, "PathwayAI project notes")
    # Always include a concise live-app capability summary so the tool remains useful before notes are loaded.
    local["current_app"] = {
        "prevention": "ZIP-guided exposure context with CDC/NYSDOH tick and Lyme surveillance.",
        "journey": "Patient journey organization, testing/care preparation, function/work and transparent cost inputs.",
        "community": "Dutchess County burden/action demonstration using CDC, NYSDOH, HRSA, Census, PLACES, published cost evidence and consented Patient Voice.",
        "provenance": "Patient-reported, public/observed, published evidence and modeled outputs are kept visibly separate.",
        "llm": "Optional structured story extraction through the OpenAI Responses API with field validation and rule-based fallback."
    }
    return local


def agent_search_evidence(query):
    """Curated evidence already used by PathwayAI; this tool does not perform open-web search."""
    evidence = [
        {"source":"CDC county Lyme surveillance", "topic":"surveillance", "detail":"Reported Lyme disease cases by county of residence, 2019-2022; not individual risk and not necessarily county of exposure."},
        {"source":"NYSDOH tick surveillance", "topic":"tick exposure", "detail":"Observed county-level nymph tick population density and B. burgdorferi surveillance where available."},
        {"source":"HRSA AHRF 2024-2025", "topic":"access", "detail":"County population, primary-care/emergency physician, hospital/bed and HPSA context."},
        {"source":"Hook et al., Emerging Infectious Diseases 2022", "topic":"economic burden", "detail":"Published societal cost perspective for reported cases in high-incidence areas; not a Dutchess estimate."},
        {"source":"Yu et al., 2026", "topic":"medical costs", "detail":"Published U.S. medical-cost comparisons used as population benchmarks; not diagnostic-delay cost or predicted county savings."},
        {"source":"Horn et al., Frontiers in Medicine 2025", "topic":"follow-up burden", "detail":"Published Lyme Disease Biobank follow-up evidence; supports examining follow-up gaps, not assigning county risk."},
        {"source":"PathwayAI pilot survey", "topic":"patient burden", "detail":"Aggregate pilot themes on diagnostic delay, clinicians seen, out-of-pocket burden and work/function; national convenience sample kept separate from county prevalence."}
    ]
    ranked = sorted(evidence, key=lambda x: _keyword_score(query, " ".join(x.values())), reverse=True)
    return {"tool":"curated evidence", "status":"ok", "items":ranked[:5],
            "note":"Curated evidence already represented in this prototype; verify publication details before external use."}


def agent_search_live_evidence(query):
    """Optional live public-web evidence search through the OpenAI Responses API.

    Internal research only. Findings never automatically update patient-facing
    content, quantitative assumptions, or cost/savings estimates.
    """
    api_key = OPENAI_API_KEY
    model = PATHWAYAI_LLM_MODEL
    if not api_key or not model:
        return {"tool":"live evidence research", "status":"not_configured", "items":[],
                "note":"OpenAI API key/model is not configured."}

    instructions = """You are the live evidence-research tool for PathwayAI, an HHS Cost of Illness prototype.
Search the public web only as needed. Prioritize primary and authoritative sources: CDC, CMS, HHS, AHRQ,
NIH/PubMed-indexed research, state health departments, and peer-reviewed journals.
Focus on Lyme/tickborne disease, diagnostic delay, healthcare utilization, medical cost,
out-of-pocket burden, work/productivity/disability, caregiving, surveillance, and policy evidence.
Do not provide diagnosis or treatment recommendations.
Do not convert a published estimate into a Dutchess County estimate or predicted savings.
For each useful finding include the source/title, date/year if available, URL, what it supports,
and an important limitation. Clearly separate evidence from interpretation."""
    payload = {
        "model": model,
        "store": False,
        "tools": [{"type": "web_search"}],
        "input": [
            {"role":"system", "content":instructions},
            {"role":"user", "content":query},
        ],
    }
    req = urllib.request.Request(
        "https://api.openai.com/v1/responses",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Authorization": f"Bearer {api_key}", "Content-Type":"application/json"},
        method="POST",
    )
    try:
        with _limited_ai_urlopen(req, timeout=90) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        out = ""
        citations = []
        for item in data.get("output", []):
            if item.get("type") == "message":
                for part in item.get("content", []):
                    if part.get("type") == "output_text":
                        out += part.get("text", "")
                        for ann in part.get("annotations", []) or []:
                            if ann.get("type") == "url_citation":
                                url = ann.get("url")
                                title = ann.get("title")
                                if url and url not in [x.get("url") for x in citations]:
                                    citations.append({"title": title or url, "url": url})
        return {
            "tool":"live evidence research",
            "status":"ok",
            "items":[{"research_summary":out.strip()}] if out.strip() else [],
            "citations":citations,
            "note":"Live public-web research. Human approval is required before changing PathwayAI assumptions or outputs.",
        }
    except Exception as e:
        safe = str(e).replace(api_key, "[redacted]")[:500]
        return {"tool":"live evidence research", "status":"error", "items":[], "note":safe}


AGENT_TOOL_MAP = {
    "search_hhs": agent_search_hhs,
    "search_pathwayai": agent_search_pathwayai,
    "search_evidence": agent_search_evidence,
    "search_competitors": agent_search_competitors,
    "search_live_evidence": agent_search_live_evidence,
}


def _openai_text_request(system_text, user_text, timeout=60):
    api_key = OPENAI_API_KEY
    model = PATHWAYAI_LLM_MODEL
    if not api_key or not model:
        return None, "OpenAI API key/model is not configured."
    payload = {"model": model, "store": False, "input": [
        {"role":"system", "content":system_text},
        {"role":"user", "content":user_text},
    ]}
    req = urllib.request.Request(
        "https://api.openai.com/v1/responses",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Authorization": f"Bearer {api_key}", "Content-Type":"application/json"},
        method="POST",
    )
    try:
        with _limited_ai_urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        out = ""
        for item in data.get("output", []):
            if item.get("type") == "message":
                for part in item.get("content", []):
                    if part.get("type") == "output_text":
                        out += part.get("text", "")
        return out.strip(), None
    except Exception as e:
        safe = str(e).replace(api_key, "[redacted]")[:500]
        return None, safe


def run_strategy_agent(question):
    """Two-stage agent: model selects tools, Python executes them, model synthesizes grounded output."""
    planner = """You are the planning layer for PathwayAI's Research & Strategy Agent.
Choose only the tools needed to answer the user's question. Available tools:
search_hhs: HHS Tech Sprint requirements/messages/feedback loaded locally.
search_pathwayai: current PathwayAI capabilities and local project notes.
search_evidence: curated Lyme/tick/cost/burden evidence already used by PathwayAI.
search_competitors: competitor/comparable-solution notes loaded locally.
search_live_evidence: current public-web research for newer Lyme/tick/cost/burden/CMS evidence. Use it only when the question asks for recent/current/new evidence, external verification, or evidence not already in the curated tool.
Return ONLY JSON: {\"tools\":[\"tool_name\",...],\"reason\":\"brief reason\"}.
Use 1-5 tools. Do not claim a source is available unless a tool can provide it."""
    plan_text, err = _openai_text_request(planner, question)
    if err:
        return None, {"state":"api_error", "message":err}
    try:
        cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", plan_text.strip(), flags=re.I|re.S)
        plan = json.loads(cleaned)
        selected = [x for x in plan.get("tools", []) if x in AGENT_TOOL_MAP]
    except Exception:
        return None, {"state":"plan_error", "message":"The model did not return a valid tool plan."}
    if not selected:
        selected = ["search_pathwayai"]

    results = {}
    for tool_name in selected[:5]:
        results[tool_name] = AGENT_TOOL_MAP[tool_name](question)

    synthesizer = """You are PathwayAI's Research & Strategy Agent for an HHS innovation project.
Use ONLY the tool results provided. Do not invent facts, requirements, competitor capabilities, costs, prevalence, savings or citations.
Clearly distinguish: HHS/project information, current PathwayAI capability, published/public evidence, patient-reported evidence, and AI interpretation.
If a requested source is not loaded, say 'not loaded' and identify what should be added.
Do not diagnose or recommend treatment.
When live evidence is present, compare it against current PathwayAI capability and existing curated evidence.
For any proposed MVP change, classify it as exactly one of: KEEP, CONSIDER CHANGE, or NEEDS REVIEW.
Never automatically adopt a newly found number, cost estimate, prevalence value, clinical statement, or savings assumption.
Return concise sections: What I checked; What it shows; Impact on current MVP; Gaps/uncertainty; Recommended next 3 actions; Sources used.
Recommendations are AI interpretation and require human review."""
    bundle = json.dumps({"question":question, "selected_tools":selected, "tool_results":results}, ensure_ascii=False)
    answer, err = _openai_text_request(synthesizer, bundle)
    if err:
        return None, {"state":"api_error", "message":err, "selected_tools":selected, "results":results}
    return answer, {"state":"connected", "selected_tools":selected, "plan_reason":plan.get("reason", ""), "results":results}


def show_research_strategy_agent():
    if not st.session_state.get("admin_authenticated"):
        st.error("Admin access required for the Research & Strategy Agent.")
        st.stop()
    st.header("🧠 Research & Strategy Agent")
    st.caption("Internal prototype • agentic tool selection • curated + optional live evidence • human review required")
    st.write("Ask a strategy or research question. The model decides which approved tools it needs. It can use stored HHS/PathwayAI/competitor knowledge, curated evidence, or—when needed—live public-web research.")
    st.info("This internal prototype is not patient-facing. Live findings are recommendations only and never automatically change PathwayAI data, cost assumptions, or patient guidance.")

    q = st.text_area("Ask the agent", placeholder="Find recent evidence on delayed Lyme diagnosis and tell me whether it should change the final MVP.", height=100, key="strategy_agent_q")
    if st.button("Run Research & Strategy Agent", type="primary", key="run_strategy_agent"):
        if not q.strip():
            st.warning("Enter a question first.")
        else:
            allowed, limit_message = ai_call_allowed("research-agent")
            if not allowed:
                st.warning(limit_message)
                st.stop()
            with st.spinner("Agent is selecting tools and reviewing the available evidence..."):
                answer, meta = run_strategy_agent(q.strip())
            if answer:
                record_completed_ai_call()
                st.markdown(answer)
                with st.expander("Agent trace — what tools did it choose?"):
                    st.write("**Selected tools:** " + ", ".join(meta.get("selected_tools", [])))
                    if meta.get("plan_reason"):
                        st.write("**Planner reason:** " + str(meta.get("plan_reason")))
                    st.json(meta.get("results", {}))
                st.caption("AI interpretation • Verify source documents and quantitative claims before external use.")
            else:
                st.error(meta.get("message", "The agent could not complete the request."))

    with st.expander("Knowledge folders to add next"):
        st.code("agent_knowledge/hhs/\nagent_knowledge/pathwayai/\nagent_knowledge/competitors/", language="text")
        st.write("Add .txt, .md, or .csv notes. The agent deliberately does not read patient-level files.")


if (not ny_tick_data.empty) and ("County" in ny_tick_data.columns):
    dutchess_data = ny_tick_data[
        ny_tick_data["County"].astype(str).str.contains("Dutchess", case=False, na=False)
    ].copy()
else:
    dutchess_data = pd.DataFrame()

latest_dutchess = latest_tick_record(ny_tick_data)

# Admin unlock is intentionally separate from the shared pilot password.
with st.sidebar.expander("Admin access"):
    if st.session_state.get("admin_authenticated"):
        st.success("Admin mode enabled")
        if st.button("Exit admin mode", key="exit_admin"):
            st.session_state["admin_authenticated"] = False
            st.rerun()
    else:
        admin_try = st.text_input("Admin password", type="password", key="admin_password_entry")
        if st.button("Unlock admin tools", key="unlock_admin"):
            import hmac
            if ADMIN_PASSWORD and hmac.compare_digest(admin_try, ADMIN_PASSWORD):
                st.session_state["admin_authenticated"] = True
                st.rerun()
            else:
                st.error("Admin password not recognized.")



if st.session_state.get("admin_authenticated"):
    with st.sidebar.expander("MVP showcase checklist"):
        st.caption("Patient Voice uses local-file pilot storage. Production collection needs durable private storage and retention controls.")
        st.write("Organizer template: MVP Demo Milestone, reviewed October 7, 2026.")
        st.write("Walkthrough: complete user journey, core features, communities involved, and what testing taught us.")
        st.write("Impact & Evidence: intended users, federal datasets actually incorporated, and documented user validation.")
        st.write("Deployment Strategy: launch plan, sustainability, post-sprint roadmap, and ways to support the tool.")
        st.caption("Technical checks are not user validation. County adoption, clinical benefit and savings remain unestablished.")

def select_public_pathway(target, intent):
    st.session_state["pathway_view"] = target
    st.session_state["public_pathway_intent"] = intent
    st.session_state["pathway_open"] = True

def return_to_path_choices():
    st.session_state["pathway_open"] = False

def open_sidebar_view():
    st.session_state["pathway_open"] = True
    st.session_state["public_pathway_intent"] = "browse"

paths = [
    ("I want to learn", "Explore Lyme, tick-borne illness and prevention—no personal information needed.", "📚 Learn", "learn"),
    ("I’m planning a visit or outdoor activity", "Explore destination tick information and prepare a prevention plan.", "🛡️ Prevention", "outdoors"),
    ("I found a tick", "Find removal guidance and information about contacting a clinician.", "🛡️ Prevention", "bite"),
    ("I feel unwell after possible exposure", "Organize symptoms and prepare for a medical visit.", "🧭 Timely Care & Support", "symptoms"),
    ("I have ongoing symptoms", "Organize your journey and find care and daily-life support.", "🧭 Timely Care & Support", "ongoing"),
    ("I’m helping someone else", "Help someone prepare their story and find support, with their permission.", "🧭 Timely Care & Support", "caregiver"),
    ("I work in public health", "Review county evidence, hidden burden and suggested actions.", "📊 Community Burden & Action", "county"),
    ("I want to contribute", "Leave a brief suggestion or tell us how you would like to help.", "💬 Contribute", "contribute"),
]
available_views = ["📚 Learn", "🛡️ Prevention", "🧭 Timely Care & Support", "📊 Community Burden & Action", "💬 Contribute"]
if st.session_state.get("admin_authenticated"):
    available_views.append("🧠 Research & Strategy Agent")
if st.session_state.get("pathway_view") not in available_views:
    st.session_state["pathway_view"] = "📊 Community Burden & Action"
view = st.sidebar.radio("Explore PathwayAI", available_views, key="pathway_view", on_change=open_sidebar_view)

if not st.session_state.get("pathway_open", False):
    st.title("PathwayAI")
    st.markdown("### A tiny tick bite can have a big impact.")
    st.write("Tick-borne illnesses can affect health, work, and daily life. Knowing how to prevent bites and when to seek care matters—at home and when traveling.")
    st.markdown("**Find your next step with PathwayAI.**")
    st.write("Prepare for outdoor activities, organize your health journey, or explore the burden on your community.")
    with st.expander("Why does this matter?"):
        st.write("CDC estimates approximately 476,000 people were diagnosed and treated for Lyme disease annually in the United States, based on insurance-claims research from 2010–2018. Most people recover with appropriate treatment, especially when treated early.¹")
        st.caption("This is an estimate of diagnoses and treatment, not a count of confirmed infections or a new 2026 case count.")
    st.subheader("What brings you here today?")
    for start in range(0, len(paths), 2):
        cols = st.columns(2)
        for col, (label, detail, target, intent) in zip(cols, paths[start:start+2]):
            with col:
                st.button(label, key="route_"+intent, on_click=select_public_pathway, args=(target, intent), use_container_width=True)
                st.caption(detail)
    st.caption("Education and navigation only. PathwayAI does not diagnose illness or calculate your personal chance of infection.")
    st.caption("¹ Sources: [CDC diagnoses study](https://wwwnc.cdc.gov/eid/article/27/2/20-2731_article) · [CDC prevention](https://www.cdc.gov/ticks/prevention/)")
    st.stop()

st.button("← Change my path", key="change_path", on_click=return_to_path_choices)
st.caption("PathwayAI · " + view)


def show_brief_feedback():
    st.subheader("Help shape PathwayAI")
    st.write("Explore the tool, then tell us what could make it more useful—or how you’d like to help.")
    choices = [
        ("Explore prevention and travel", "🛡️ Prevention", "outdoors"),
        ("Explore patient journey and support", "🧭 Timely Care & Support", "ongoing"),
        ("Explore community burden", "📊 Community Burden & Action", "county"),
    ]
    for label, target, intent in choices:
        st.button(label, key="contributor_"+intent, on_click=select_public_pathway, args=(target, intent), use_container_width=True)
    st.markdown("#### Ready to share an idea?")
    st.write("What helped, what was confusing, or what would you like us to add? A sentence or two is enough. You can also tell us how you would like to help.")
    st.caption("Please leave out personal medical details. Your message will go privately to the project inbox, not appear on this website.")
    address = "pathwayai.feedback@gmail.com"
    st.markdown("[**Email feedback or offer to help**](mailto:" + address + "?" + urlencode({"subject": "PathwayAI Feedback"}, quote_via=quote_plus) + ")")
    st.write("**" + address + "**")
    st.caption('Opens your email app; press Send there. If it does not open, copy the address into your email service.')
    st.write("Thank you so much for your contribution!")

if view == "📚 Learn":
    st.header("Why pay attention to ticks?")
    st.write("A tiny tick bite can have a big impact. Ticks can spread Lyme disease and other illnesses, making prevention and timely care important—whether you’re traveling, visiting a park, or spending time in your backyard.")
    st.markdown("**Learn about tick-borne illness, protect yourself, and know what to do after a bite.**")
    st.markdown("**Explore the basics**\n\n[CDC: About Lyme disease](https://www.cdc.gov/lyme/about/index.html) · [CDC: Tick-bite prevention](https://www.cdc.gov/ticks/prevention/index.html) · [CDC: After a tick bite](https://www.cdc.gov/ticks/after-a-tick-bite/index.html)")
    st.markdown("**Choose your next step**\n\n- Planning a visit? Open Prevention for destination surveillance and an outdoor plan.\n- Preparing for care? Open Timely Care & Support to organize your story.\n- Exploring local needs? Open Community Burden & Action for the Dutchess pilot.\n- Have an idea? Open Contribute and leave a short note.")
    st.caption("County surveillance describes population context, not your individual chance of infection. Reported case counts and tick-presence categories are different measures.")
    st.stop()

if view == "💬 Contribute":
    show_brief_feedback()
    st.caption('Patient Voice is separate: review and consent to sharing structured fields in Timely Care & Support.')
    st.stop()

if view == "🧠 Research & Strategy Agent":
    show_research_strategy_agent()
    st.stop()


if view == "🛡️ Prevention":
    st.header("🛡️ PREVENTION")
    show_section_hero("travel", "Know Your Exposure. Reduce Avoidable Risk.", "Understand where and when exposure may occur, recognize what you found, and prepare after a possible bite.")
    if st.session_state.get("public_pathway_intent") == "bite":
        st.info("Found an attached tick? Remove it promptly with fine-tipped tweezers, grasping close to the skin and pulling steadily upward. Clean the area and your hands. Do not wait for this card; contact a clinician for advice about your bite, particularly if you develop symptoms.")
        st.markdown("[CDC tick-removal guidance](https://www.cdc.gov/ticks/after-a-tick-bite/index.html)")
    st.subheader("Plan Your Outdoor Activities")

    travel_zip = st.text_input(
        "Where are you going? Enter any U.S. ZIP code",
        max_chars=5,
        placeholder="e.g., 12601",
        help="ZIP is the destination selector. PathwayAI uses the best available national, state/local, or pilot surveillance layer and does not substitute New York measures for other locations."
    )
    travel_destination = destination_label(travel_zip)
    travel_geo = resolve_us_zip(travel_zip) if len(normalize_zip(travel_zip)) == 5 else None
    if len(normalize_zip(travel_zip)) == 5 and travel_geo is None:
        st.caption("ZIP accepted. The city could not be resolved from the geographic lookup service; PathwayAI will not guess a city or county.")
    if len(normalize_zip(travel_zip)) == 5:
        st.write(f"**Destination identified:** {travel_destination}")
        st.caption('Your ZIP selects destination surveillance; it does not determine personal infection risk.')

    travel_month = st.selectbox(
        "When are you traveling?",
        [
            "January", "February", "March", "April",
            "May", "June", "July", "August",
            "September", "October", "November", "December"
        ],
        index=5
    )

    outdoor_activity = st.selectbox("What will you be doing?", ["Choose an activity", "Hiking or camping", "Gardening or yard work", "Parks or outdoor events", "Mostly indoor activities"])

    health_context = st.multiselect(
        "Do any of these apply to you?",
        [
            "Age 65 or older",
            "Weakened immune system or immunosuppressive treatment",
            "No spleen or reduced spleen function",
            "Cancer or cancer treatment",
            "Kidney disease",
            "Liver disease",
            "Other relevant health condition"
        ]
    )
    if st.button("Generate My Outdoor Tick-Prevention Plan", type="primary"):
        st.divider()
        st.header("My Outdoor Tick-Prevention Plan")
        st.info('Use this plan for prevention, not diagnosis or personal risk prediction.')
        st.markdown("**Your next steps**\n- Before: prepare EPA-registered repellent and protective clothing; follow product instructions.\n- After outdoor activities: check your body, clothing, gear and pets; shower within two hours.\n- If you found a tick or feel unwell: use the bite guidance below or choose Timely Care & Support.")

        st.write(f"**Destination:** {travel_destination}")
        if normalize_zip(travel_zip):
            st.write(f"**Destination ZIP code:** {normalize_zip(travel_zip)}")
            if travel_geo:
                state_code = travel_geo.get("state_code", "")
                if state_code in HIGH_INCIDENCE_STATES:
                    st.success(f"**{travel_geo.get('state','This state')} is in CDC's higher-incidence Lyme disease group.** This means Lyme disease is reported more frequently at the population level. It does not estimate your personal chance of infection. The map below provides national context; finer local measures are shown when available.")
                else:
                    st.info(f"**{travel_geo.get('state','This state')} is not currently in CDC's higher-incidence Lyme disease group.** This does not mean zero risk. Tick exposure and Lyme disease can still occur, so PathwayAI shows national tick/pathogen surveillance and local public-health sources rather than labeling the ZIP 'low risk.'")
        st.write(f"**Travel month:** {travel_month}")
        st.write(f"**Planned activity:** {outdoor_activity}")
        if outdoor_activity == "Mostly indoor activities":
            st.caption("Consider tick precautions for any outdoor portions of your visit; an indoor visit alone does not establish tick exposure.")
        if "Kidney disease" in health_context or "Liver disease" in health_context:
            st.info("Serious kidney or liver disease can increase the risk of severe babesiosis, another infection spread by blacklegged ticks. This is not an estimate of your Lyme risk. Bring your medication list and contact a clinician promptly if you become unwell after possible tick exposure.")
            if "Kidney disease" in health_context:
                st.write("Follow your prescribed fluid guidance. Ask a clinician or pharmacist before using ibuprofen or naproxen; do not change prescribed medicines on your own.")
            st.caption("Sources: [CDC babesiosis](https://www.cdc.gov/babesiosis/hcp/clinical-overview/index.html) · [NIDDK medicine safety](https://www.niddk.nih.gov/health-information/kidney-disease/keeping-kidneys-safe)")

        if health_context:
            st.write("**Health context:** " + ", ".join(health_context))
        else:
            st.write("**Health context:** None selected")

        if normalize_zip(travel_zip).startswith("126") and latest_dutchess is not None:
            st.subheader("Environmental Surveillance")

            st.write(
                f"**Latest NYSDOH surveillance year:** {int(latest_dutchess['Year'])}"
            )

            st.write(
                f"**Nymph tick population density:** {latest_dutchess['Tick Population Density']:.2f}"
            )

            st.write(
                f"**B. burgdorferi positive:** {latest_dutchess['B. burgdorferi (%)']}"
            )

            st.caption(
                "Source: New York State Department of Health deer tick surveillance. "
                "Environmental surveillance describes local tick conditions and does "
                "not estimate an individual's probability of infection."
            )
        st.subheader("Local Tick Exposure Context")

        if normalize_zip(travel_zip).startswith("126") and latest_dutchess is not None:
            latest_year = int(latest_dutchess["Year"])
            latest_density = float(latest_dutchess["Tick Population Density"])
            latest_bb = latest_dutchess["B. burgdorferi (%)"]

            st.markdown("#### At a glance")
            c1, c2, c3 = st.columns(3)
            with c1:
                st.metric("Surveillance year", latest_year)
                st.caption("Latest local record")
            with c2:
                st.metric("Nymph density", f"{latest_density:.1f} / 1,000 m²")
                st.caption("Host-seeking nymphs found in standardized surveillance")
            with c3:
                st.metric("B. burgdorferi positive", str(latest_bb))
                try:
                    _bb = float(str(latest_bb).replace('%','').strip())
                    st.caption(f"≈ {_bb:.0f} of every 100 tested nymphs")
                except Exception:
                    st.caption("Share of tested nymphs positive")
            st.caption(f"NYSDOH • {latest_year} • Environmental surveillance, not personal infection probability")

            st.markdown("#### Tick Exposure at Your Destination")
            st.write(
                'Review regional and local tick surveillance before your trip.'
            )

            st.caption("Use the observed county surveillance above. Regional measures are not a personal infection probability.")

            st.markdown(
                "[View the official NYSDOH Tick Risk Score by Region map]"
                "(https://www.health.ny.gov/diseases/communicable/lyme/risk_score_map.htm)"
            )

            with st.expander("View Dutchess County surveillance history"):
                dutchess_plot = dutchess_data.sort_values("Year").copy()
                if "Tick Population Density" in dutchess_plot.columns:
                    trend = dutchess_plot[["Year", "Tick Population Density"]].dropna()
                    if not trend.empty:
                        trend = trend.set_index("Year")
                        st.caption(
                            "Observed nymph tick population density in the PathwayAI "
                            "Dutchess County surveillance dataset"
                        )
                        st.line_chart(trend)
                st.caption(
                    "Source: NYSDOH deer tick surveillance. Year-to-year surveillance "
                    "values can vary and should be interpreted as environmental context."
                )
            # v9.8.0: ZIPs beginning with 126 keep the NYSDOH local detail above,
            # but now ALSO receive the same combined regional map used for every other ZIP.
            state_code = travel_geo.get("state_code", "") if travel_geo else ""
            st.markdown("#### Tick & Lyme Disease Surveillance Near Your Destination")
            st.write(
                'Compare tick surveillance and reported Lyme cases separately. Neither predicts your personal risk.'
            )
            show_combined_tick_lyme_context(state_code, travel_geo)
            st.markdown("**Open the underlying county-level layers**")
            st.markdown("[🔵 CDC blacklegged tick surveillance — county level](https://www.cdc.gov/ticks/data-research/facts-stats/blacklegged-tick-surveillance.html)")
            st.markdown("[CDC tickborne pathogen surveillance map](https://www.cdc.gov/ticks/data-research/facts-stats/tickborne-pathogen-surveillance-1.html)")
            st.markdown("[🟧 CDC Lyme disease surveillance and reported-case data](https://www.cdc.gov/lyme/data-research/facts-stats/index.html)")
            st.markdown(f"[Find local/state public-health information for ZIP {normalize_zip(travel_zip)}](https://www.google.com/search?q={quote_plus('official health department tick Lyme ZIP ' + normalize_zip(travel_zip))})")
            st.caption("CDC notes that a county with no tick/pathogen surveillance record should not be interpreted as having no ticks or no pathogen; sampling and reporting vary by location.")

        else:
            state_code = travel_geo.get("state_code", "") if travel_geo else ""
            st.markdown("#### Tick & Lyme Disease Surveillance Near Your Destination")
            st.write(
                'Compare tick surveillance and reported Lyme cases separately. Neither predicts your personal risk.'
            )
            show_combined_tick_lyme_context(state_code, travel_geo)
            st.markdown("**Open the underlying county-level layers**")
            st.markdown("[🔵 CDC blacklegged tick surveillance — county level](https://www.cdc.gov/ticks/data-research/facts-stats/blacklegged-tick-surveillance.html)")
            st.markdown("[CDC tickborne pathogen surveillance map](https://www.cdc.gov/ticks/data-research/facts-stats/tickborne-pathogen-surveillance-1.html)")
            st.markdown("[🟧 CDC Lyme disease surveillance and reported-case data](https://www.cdc.gov/lyme/data-research/facts-stats/index.html)")
            st.markdown(f"[Find local/state public-health information for ZIP {normalize_zip(travel_zip)}](https://www.google.com/search?q={quote_plus('official health department tick Lyme ZIP ' + normalize_zip(travel_zip))})")
            st.caption("CDC notes that a county with no tick/pathogen surveillance record should not be interpreted as having no ticks or no pathogen; sampling and reporting vary by location.")

        show_tick_identification_guide()

        st.subheader("My Travel Snapshot")

        st.write(f"**Destination:** {travel_destination}")
        st.write(f"**Season:** {travel_month}")

        if normalize_zip(travel_zip).startswith("126") and latest_dutchess is not None:
            st.write(
                f"**Destination exposure context:** NYSDOH surveillance data are available "
                f"for Dutchess County; the latest record in this PathwayAI dataset is "
                f"{int(latest_dutchess['Year'])}. Use the surveillance measures above as "
                f"environmental context rather than an individual infection probability."
            )
        else:
            state_code = travel_geo.get("state_code", "") if travel_geo else ""
            if state_code in HIGH_INCIDENCE_STATES:
                st.write("**Destination exposure context:** Your destination is in CDC's higher-incidence Lyme disease group. Use the national map plus available state/local surveillance for trip planning; this is population-level context, not an individual infection probability.")
            else:
                st.write("**Destination exposure context:** Your destination is not currently in CDC's higher-incidence Lyme disease group. Tick exposure may still occur, so PathwayAI links national tick/pathogen surveillance and local public-health sources rather than labeling the ZIP 'low risk.'")

        if health_context:
            st.write("**Personal context:** " + ", ".join(health_context))
        else:
            st.write("**Personal context:** None selected")

        st.write(
    "**Action:** Use enhanced tick-bite precautions during outdoor, "
    "wooded, or brush exposure."
)
        
        st.subheader("What This Means for My Trip")

        if normalize_zip(travel_zip).startswith("126"):
            st.write("**Exposure context:** Local NYSDOH surveillance provides additional environmental context for this destination.")
        elif travel_geo and travel_geo.get("state_code") in HIGH_INCIDENCE_STATES:
            st.write("**Exposure context:** This destination is in CDC's higher-incidence Lyme disease group. Use tick-bite prevention during potential exposure and review the surveillance information above.")
        else:
            st.write("**Exposure context:** This destination is not currently in CDC's higher-incidence Lyme disease group. That does not mean zero risk; use the national tick/pathogen and local public-health information above for context.")

        if health_context:
            st.write(
                "**Personal context:** You selected: "
                + ", ".join(health_context)
            )

        st.write(
            "**Travel guidance:** This does not mean you need to avoid the "
            "destination. Consider additional tick-bite prevention, especially "
            "during outdoor, wooded, or brush exposure."
        )

        st.write(
            "**If a tick bite occurs:** Record the date and location, remove "
            "the tick promptly, and monitor for symptoms. Seek medical "
            "evaluation for concerning symptoms."
        )

        st.caption(
            "Exposure-navigation guidance only. Environmental surveillance "
            "does not estimate your individual probability of infection."
        )

        st.subheader("My PathwayAI Travel Plan")
        before, during, after = st.tabs(["Before the trip", "During the trip", "After the trip"])
        with before:
            st.write("• Review local and seasonal tick-exposure context.")
            st.write("• Plan tick-bite prevention for wooded, brushy, grassy, or outdoor activities.")
            st.write("• Pack appropriate repellent/protective clothing and a tick-removal tool.")
        with during:
            st.write("• Use planned tick-bite precautions during outdoor exposure.")
            st.write("• Perform tick checks after outdoor activity and remove attached ticks promptly.")
            st.write("• If a possible exposure occurs, record the date, place, and circumstances.")
        with after:
            st.write("• Keep your exposure history with your travel record.")
            st.write("• Monitor for new or changing symptoms after possible exposure.")
            st.write("• If symptoms or concerns develop, use **My Journey** to organize exposure, testing, function, and burden information for discussion with a healthcare professional.")
        st.caption("Travel-plan guidance supports prevention and documentation; it is not a diagnosis or treatment recommendation.")

    st.stop()

if view == "📊 Community Burden & Action":
    st.header("📊 DUTCHESS COUNTY — COST-OF-ILLNESS PILOT")
    show_section_hero(
        "policy",
        "Open County Evidence. Make Hidden Burden Measurable.",
        "A demonstration combining public county evidence, published cost context and a proposed 90-day burden-measurement plan."
    )

    # Oct 22 MVP: one complete demonstration county. The County Pack is the scalable product.
    policy_place = "Dutchess County, New York"
    st.markdown("### Dutchess County, New York — Demonstration County")
    st.caption('Dutchess is the current county pilot.')
    county_ids = {
        "Dutchess County, New York": {"fips": "36027", "short": "Dutchess, NY"},
    }
    cm = county_ids[policy_place]
    fips = cm["fips"]

    # U.S. Census Bureau QuickFacts snapshot for Dutchess County (FIPS 36027).
    # Kept local for contest reliability: no Census API/network call is required at runtime.
    # Population is context only; the annualized Lyme rate below continues to use the
    # explicitly labeled 2023 HRSA population denominator for methodological consistency.
    census_context = {
        "population_2025_estimate": 300708,
        "poverty_percent_2020_2024": 8.4,
        "uninsured_under65_percent_2020_2024": 4.9,
        "civilian_labor_force_percent_2020_2024": 62.8,
        "disability_under65_percent_2020_2024": 9.2,
        "source": "U.S. Census Bureau QuickFacts",
        "source_url": "https://www.census.gov/quickfacts/fact/table/dutchesscountynewyork/POP010210",
    }

    ahrf = load_ahrf_county(fips)
    places = load_places_county(fips)
    pv = load_patient_voice(fips)
    assets = load_county_assets(fips)
    lyme_cases = local_lyme_cases_for_fips(fips)
    pop = float(ahrf["population"]) if ahrf and pd.notna(ahrf.get("population")) else None
    annual_avg_cases = (float(lyme_cases) / 4.0) if lyme_cases is not None else None
    crude_rate = (annual_avg_cases / pop * 100000) if (annual_avg_cases is not None and pop) else None

    # NYSDOH exposure is county-specific; never substitute it for PA/MD.
    exposure_year = exposure_density = exposure_pathogen = None
    if policy_place == "Dutchess County, New York" and latest_dutchess is not None:
        try: exposure_year = int(latest_dutchess["Year"])
        except Exception: pass
        try: exposure_density = float(latest_dutchess["Tick Population Density"])
        except Exception: pass
        try:
            raw = latest_dutchess["B. burgdorferi (%)"]
            exposure_pathogen = str(raw)
        except Exception: pass

    st.write("Compare observed tick activity and reported Lyme illness, then identify where prevention, care navigation and support could help.")
    # Detailed implementation stays out of the opening decision flow.
    actions = pd.DataFrame([
        ["1. Target prevention outreach", "Observed tick surveillance", "County outreach / parks partners", "Choose outreach locations using loaded surveillance; record missing locations", "Reach, materials delivered and knowledge feedback"],
        ["2. Offer journey navigation", "National pilot themes: delay and repeated professionals", "Public health / primary-care partners", "Offer a reviewed care summary and referral navigation; a second opinion when appropriate", "Summary completion, referral connection and time to appointment"],
        ["3. Address household barriers", "National pilot themes: spending and work loss", "Social services / navigation partners", "Screen voluntarily for transport, insurance and financial support needs", "Support referrals offered and successfully accessed"],
        ["4. Explore clinical follow-up", "Biobank: persistent symptoms and follow-up gap", "Clinical partners", "Agree on a symptom/function check-in workflow; clinicians determine care", "Follow-up completion and patient-reported function"],
        ["5. Build a local burden baseline", "Consented patient-reported county fields", "County evaluation team", "Collect delay, encounters, OOP period, days lost and caregiver time; repeat measures consistently", "Completeness and paired change; no assumed savings"],
    ], columns=["Proposed action","Why consider it","Suggested owner","First step","What to measure"])
    actions["Evidence status"] = [
        "Public exposure context; local intervention effect untested",
        "Patient survey themes; local service effect untested",
        "Patient survey themes; local support needs unmeasured",
        "Published Biobank follow-up evidence; local effect untested",
        "Proposed measurement protocol; no intervention effect claimed",
    ]
    st.subheader("Orange and Dutchess · what differs in 2024?")
    st.caption("Same-year public data · tick density at sampled sites and reported illness among residents.")
    comparison_2024 = pd.DataFrame([
        {"County": "Orange", "Year": 2024, "Nymphs / 1,000 m²": 43.2, "Reported Lyme cases": 964, "Reported Lyme cases / 100,000": 237.0, "Tick sites visited": 1},
        {"County": "Dutchess", "Year": 2024, "Nymphs / 1,000 m²": 28.8, "Reported Lyme cases": 1060, "Reported Lyme cases / 100,000": 355.5, "Tick sites visited": 1},
    ])
    chart_left, chart_right = st.columns(2)
    with chart_left:
        st.markdown("**Observed tick density · 2024**")
        st.bar_chart(comparison_2024.set_index("County")[["Nymphs / 1,000 m²"]], color="#cf7724", height=240)
        st.caption("Nymphs per 1,000 m² at sampled sites; one site visited in each county.")
    with chart_right:
        st.markdown("**Reported Lyme rate · 2024**")
        st.bar_chart(comparison_2024.set_index("County")[["Reported Lyme cases / 100,000"]], color="#317399", height=240)
        st.caption("Reported cases per 100,000 residents; official NYSDOH annual rates.")
    st.write("Orange had higher sampled tick density; Dutchess had a higher reported Lyme rate. This contrast identifies a question to investigate, not evidence that either county's prevention works better.")
    show_readable_table(comparison_2024, hide_index=True, width="stretch")
    with st.expander("Questions and actions for county partners"):
        comparison_actions = pd.DataFrame([
            ["Are sampled sites comparable?", "Review site locations, collection dates and area sampled", "Comparable sampling coverage documented"],
            ["Does the contrast persist over time?", "Compare annual tick observations and reported cases using consistent definitions", "Same-year series with changes in reporting annotated"],
            ["Where could prevention reach more people?", "Review local outreach, outdoor activities and service access with both departments", "Outreach reach and referral connections measured"],
        ], columns=["Question", "Action to consider", "Measure to track"])
        show_readable_table(comparison_actions, hide_index=True, width="stretch")
    with st.expander("Comparison sources and limits"):
        st.markdown("[1 · NYSDOH tick sampling](https://health.data.ny.gov/d/kibp-u2ip) · [2 · 2024 county cases](https://www.health.ny.gov/statistics/diseases/communicable/2024/docs/cases.pdf) · [3 · 2024 county rates](https://www.health.ny.gov/statistics/diseases/communicable/2024/docs/rates.pdf)")
        st.caption("Cases and rates verified against official tables, page 5. Tick records retrieved October 8, 2026. A site observation is not county-wide exposure. Reported cases reflect residence and surveillance practices. Measures are placed side by side by county and year; no patient records are linked, and no causal effect, savings or disability prevented is estimated.")
    comparison_export = comparison_2024.copy()
    comparison_export["tick_source"] = "NYSDOH kibp-u2ip; 2024 sampled-site observations"
    comparison_export["case_source"] = "NYSDOH 2024 cases.pdf; page 5"
    comparison_export["rate_source"] = "NYSDOH 2024 rates.pdf; page 5; official rate"
    comparison_export["interpretation"] = "Descriptive same-year comparison; one tick site each; not causal or county-wide exposure"
    st.download_button("Download 2024 county comparison", comparison_export.to_csv(index=False).encode("utf-8"), file_name="CountyCompare2024.csv", mime="text/csv", key="comparison_download64")

    st.subheader("Dutchess at a glance")
    cards=[]
    if exposure_density is not None: cards.append(("Tick density", f"{exposure_density:.1f} / 1,000 m²"))
    if exposure_pathogen is not None: cards.append(("B. burgdorferi positive", exposure_pathogen))
    cards.append(("Reported Lyme cases · 2024", "1,060"))
    cards.append(("NYSDOH Lyme rate · 2024", "355.5 / 100k"))
    if ahrf and pd.notna(ahrf.get("pcp")) and pop: cards.append(("Primary-care capacity", f"{float(ahrf['pcp'])/pop*10000:.1f} / 10k"))
    if ahrf and pd.notna(ahrf.get("beds")): cards.append(("Hospital beds", f"{int(float(ahrf['beds'])):,}"))
    if cards:
        cols=st.columns(min(4,len(cards)))
        for i,(label,value) in enumerate(cards): cols[i % len(cols)].metric(label,value)
    source_bits=[]
    if exposure_density is not None: source_bits.append(f"Tick surveillance: NYSDOH, {exposure_year or 'year unavailable'}")
    source_bits.append("Lyme cases and official population-based rate: NYSDOH 2024 county tables, page 5. Tick observations: separate year and sampling coverage.")
    if ahrf: source_bits.append("HRSA AHRF 2024–2025")
    if source_bits:
        for source_line in source_bits: st.caption(source_line)

    st.markdown("## Figure 1 · Where is tick exposure observed?")
    show_nys_tick_density_map()
    with st.expander("Map data in text"):
        tick_text = load_nys_nymph_surveillance().copy()
        if not tick_text.empty:
            tick_text = tick_text.rename(columns={"county": "County", "year": "Year", "nymphal_density": "Observed nymphs / 1,000 m²", "b_burgdorferi": "B. burgdorferi positive (%)"})
            show_readable_table(tick_text.sort_values("County"), hide_index=True, width="stretch")
            st.caption("NYSDOH observed snapshot; unsampled counties are not listed as zero. Source: health.data.ny.gov, dataset kibp-u2ip.")
        else:
            st.write("Surveillance data unavailable.")
    st.markdown("**Takeaway:** surveillance identifies observed exposure, not each resident's infection risk. **Action:** review prevention outreach in observed areas; do not infer neighborhood hotspots from county data.")
    st.markdown("## Figure 2 · Who may need help reaching care?")
    st.write("Dutchess community partners report difficulty getting appointments, reaching services and knowing what help exists. Start by checking where referrals fail and why.³")
    st.markdown("**Who may need more support?** Residents with disability or ongoing health needs, limited income, no insurance, transport barriers or difficulty navigating services.")
    c1,c2,c3 = st.columns(3)
    c1.metric("Living in poverty¹", "8.4%")
    c2.metric("Uninsured, under 65¹", "4.9%")
    c3.metric("Disability, under 65¹", "9.2%")
    access_profile = pd.DataFrame({"Community measure": ["Poverty · source-defined population", "Uninsured · under 65", "Disability · under 65"], "Percent": [8.4, 4.9, 9.2]})
    st.bar_chart(access_profile, x="Community measure", y="Percent", horizontal=True, color="#28785c")
    if ahrf and pop and pd.notna(ahrf.get("pcp")):
        st.caption(f"HRSA context²: {int(float(ahrf['pcp'])):,} primary-care physicians in 2023 ({float(ahrf['pcp'])/pop*10000:.1f} per 10,000 residents). This is not a shortage designation or appointment-wait measure.")
    with st.expander("Disability detail and data still needed"):
        if places is not None and not places.empty:
            profile = places[places["MeasureId"].isin(["DISABILITY", "MOBILITY", "COGNITION", "LACKTRPT"])].copy()
            if not profile.empty:
                cols = [c for c in ["Measure", "Data_Value", "Year", "Data_Value_Type"] if c in profile.columns]
                show_readable_table(profile[cols], hide_index=True, width="stretch")
                st.caption("CDC PLACES: model-based adult crude prevalence estimates, not the Census under-65 disability measure. All-cause support context, not Lyme-attributable.")
        st.write("Not yet verified: current HRSA shortage boundaries, appointment waits, healthcare travel time, Census vehicle access, Medicaid coverage and Lyme-specific Medicaid payments.")
        st.markdown("[Check official HRSA shortage areas](https://data.hrsa.gov/topics/health-workforce/shortage-areas)")
    st.markdown("**Takeaway:** support needs and provider counts coexist in this county; they do not prove a local access problem for each resident. **Action:** check referral failures and transport or insurance barriers with partners.")
    st.caption("Community context, not Lyme patient counts or a ranking. Groups overlap. Existing conditions can add care needs; these figures do not establish higher Lyme risk.")
    st.markdown("**First step:** ask clinical and community partners to record appointment waits, unsuccessful referrals and the barriers patients identify. Physician counts alone do not show available appointments.")

    st.markdown("## Figure 3 · Where can the invisible journey become easier?")
    journey_steps = st.columns(3)
    for col, title, burden in zip(journey_steps, ["1 · Reach care", "2 · Navigate care", "3 · Continue daily life"], ["Waits, travel and uncertainty", "Repeated histories, visits and spending", "Work, caregiving and function"]):
        with col:
            st.markdown("**" + title + "**")
            st.write(burden)
    st.caption("Measurement framework informed by patient-reported pilot themes and published evidence. These stages do not show measured Dutchess patient outcomes or a fixed sequence for every person.")
    st.markdown("### How can we reduce burden?")
    st.write("Make the next step easier: a patient-reviewed journey summary, a confirmed route to care or a second opinion when appropriate, and help with transport, insurance and benefits.")
    st.markdown("**What to track:** completed referrals, patient-paid spending, travel costs, caregiver time and days of work or daily activity affected. Use the same reporting period at each check-in.")
    st.markdown("[Find a health center](https://findahealthcenter.hrsa.gov/) · [Dutchess transit routes](https://www.dutchessny.gov/Routes-Schedules.htm) · [Disability benefits information](https://www.ssa.gov/disability)")
    st.caption("Proposed navigation pilot. Directories do not confirm appointment availability. Medical spending, household expenses and time are separate measures; do not add overlapping costs or benefit payments to one total.")

    st.markdown("### How can we reduce the risk of disability?")
    st.write("Support timely clinical assessment and appropriate treatment, then follow up when symptoms affect daily life. CDC says early appropriate treatment can help prevent more severe Lyme disease.⁴")
    st.markdown("**For ongoing difficulties:** clinical partners evaluate persistent symptoms and other possible causes, assess function, and arrange appropriate rehabilitation, workplace or disability support.")
    st.markdown("**What to track:** time to assessment, follow-up completion, patient-reported function and unmet support needs. A second opinion is an option when questions remain, not a recommendation for everyone to repeat testing.")
    st.markdown("**Takeaway:** navigation and follow-up are actions to test. **Action:** collect comparable baseline and follow-up measures of access, spending and function.")
    st.caption("Proposed actions for county and clinical partners to consider.")

    # Local baseline is shown only when the privacy threshold is met; otherwise it stays out of the main decision flow.
    def med_num(col):
        if col not in pv.columns: return None,0
        x=usable_burden_numbers(pv[col])
        return (float(x.median()), int(x.shape[0])) if len(x) else (None,0)
    def common_text(col):
        if col not in pv.columns: return None,0
        x=pv[col].dropna().astype(str)
        x=x[(x.str.strip()!="") & (x.str.lower()!="not reported")]
        return (x.mode().iloc[0], int(x.shape[0])) if len(x) else (None,0)
    providers_med, n_prov = med_num("providers_seen")
    work_med, n_work = med_num("workdays")
    oop_mode, n_oop = common_text("oop_band")
    function_mode, n_func = common_text("function")
    if len(pv) >= 5:
        st.markdown("## Local Patient Voice baseline")
        baseline_rows=[]
        for measure,value,n in [
            ("Healthcare professionals / encounters", providers_med, n_prov),
            ("Out-of-pocket burden", oop_mode, n_oop),
            ("Workdays affected", work_med, n_work),
            ("Function", function_mode, n_func),
        ]:
            if n >= 5 and value is not None:
                shown = f"{value:g}" if isinstance(value,(int,float)) else str(value)
                baseline_rows.append([measure, shown, n])
        if baseline_rows:
            show_readable_table(pd.DataFrame(baseline_rows, columns=["Measure","Current baseline","n"]), hide_index=True, width="stretch")
            st.caption("Consented, de-identified Dutchess Patient Voice. Measures are displayed only when at least 5 usable responses are available for that field.")

    with st.expander("Plan a 90-day county pilot", expanded=False):
        st.subheader("Actions and 90-day measures")
        st.caption("Proposed plan; confirm feasibility with county and clinical partners. Effects are unmeasured.")
        # Show one action at a time rather than a six-column wall of text.
        for _, action in actions.iterrows():
            st.markdown("**" + action["Proposed action"] + "**")
            st.write(action["First step"])
            st.caption("Owner: " + action["Suggested owner"] + " • Track: " + action["What to measure"])
        st.markdown("**Local follow-up results**")
        show_readable_table(pd.DataFrame([
            ["Days from referral to appointment", "Not yet collected", "Not yet collected"],
            ["Unsuccessful referrals / reason", "Not yet collected", "Not yet collected"],
            ["Referral completion", "Not yet collected", "Not yet collected"],
            ["Patient-paid spending / stated period", "Not yet collected", "Not yet collected"],
            ["Missed workdays / stated period", "Not yet collected", "Not yet collected"],
            ["Caregiver hours / stated period", "Not yet collected", "Not yet collected"],
            ["Daily function", "Not yet collected", "Not yet collected"],
            ["Unmet support needs", "Not yet collected", "Not yet collected"],
        ], columns=["Measure", "Baseline", "90-day follow-up"]), hide_index=True, width="stretch")
        st.caption("Agree on an owner, definitions, reporting period and consent process before collection. These cells are uncollected, not zero. Before/after change alone does not establish a pilot effect.")
    with st.expander("What published studies tell us about costs", expanded=False):
        st.markdown("## Published societal burden — reported Lyme cases")
        hook = pd.DataFrame([
            ["All reported cases", "$690", "$2,032"],
            ["Confirmed localized", "$493", "$1,307"],
            ["Confirmed disseminated", "$1,081", "$3,251"],
        ], columns=["Disease category", "Median per participant", "Mean per participant"])
        show_readable_table(hook, hide_index=True, width="stretch")
        st.caption("Hook et al., CDC Emerging Infectious Diseases, 2022, Table 5 • reported cases in high-incidence areas, 2014–2016 • 2016 USD • not a Dutchess estimate. Includes medical, nonmedical and productivity costs; patient medical spending is not added again.")


        st.markdown("## Published medical costs — a separate comparison")
        yu = pd.DataFrame([
            ["Localized episode", "$695"],
            ["Disseminated episode", "$6,833"],
            ["Overall mean episode", "$2,227"],
            ["Mean attributable patient OOP across methods (where recorded)", "$188–$399"],
        ], columns=["Yu et al., 2026", "Published cost (2022 USD)"])
        show_readable_table(yu, hide_index=True, width="stretch")
        st.caption("Medical-cost evidence, not the cost of diagnostic delay, a personal forecast or predicted county savings. OOP is reported separately, not added to episode costs. Hook and Yu differ in population, perspective and dollar year: do not sum them or interpret the gap as intervention savings.")

    with st.expander("Community resources", expanded=False):
        if ahrf:
            st.markdown("## Capacity already on the ground")
            cap=[]
            if pd.notna(ahrf.get("pcp")): cap.append(("Primary-care physicians", f"{int(float(ahrf['pcp'])):,}", f"{float(ahrf['pcp'])/pop*10000:.1f} / 10k" if pop else None))
            if pd.notna(ahrf.get("hosp")): cap.append(("Hospitals", f"{int(float(ahrf['hosp'])):,}", None))
            if pd.notna(ahrf.get("beds")): cap.append(("Hospital beds", f"{int(float(ahrf['beds'])):,}", None))
            if cap:
                cols=st.columns(len(cap))
                for col,(label,val,delta) in zip(cols,cap): col.metric(label,val,delta)
            st.caption("HRSA AHRF 2024–2025 • county healthcare-capacity context")
    
        st.markdown("## Population & economic context")
        c1,c2,c3,c4 = st.columns(4)
        c1.metric("Population", f"{census_context['population_2025_estimate']:,}")
        c2.metric("Poverty", f"{census_context['poverty_percent_2020_2024']:.1f}%")
        c3.metric("Uninsured, under 65", f"{census_context['uninsured_under65_percent_2020_2024']:.1f}%")
        c4.metric("Civilian labor force, 16+", f"{census_context['civilian_labor_force_percent_2020_2024']:.1f}%")
        st.caption("U.S. Census Bureau QuickFacts • population estimate: July 1, 2025 • poverty, insurance, and labor-force measures: 2020–2024. Context only; not Lyme-attributable and not used to estimate county savings.")
    
        if places is not None and not places.empty:
            st.markdown("## Health & function context")
            lookup={str(r.MeasureId):r for _,r in places.iterrows()}
            rows=[]
            for mid,label in [("DISABILITY","Any disability"),("COGNITION","Cognitive disability"),("MOBILITY","Mobility disability"),("LACKTRPT","Transportation barriers")]:
                if mid in lookup: rows.append((label,float(lookup[mid].Data_Value)))
            if rows:
                cols=st.columns(len(rows))
                for col,(label,val) in zip(cols,rows): col.metric(label,f"{val:.1f}%")
                st.caption("CDC PLACES • crude prevalence • all-cause county context, not Lyme-attributable")
    
        st.markdown("## Local programs")
        if not assets.empty:
            cols=st.columns(min(3,len(assets)))
            for i,(_,r) in enumerate(assets.iterrows()):
                with cols[i % len(cols)]:
                    st.markdown(f"### {r['name']}")
                    if pd.notna(r.get('category')): st.caption(str(r['category']))
                    if pd.notna(r.get('url')) and str(r['url']).strip(): st.markdown(f"[Open program]({r['url']})")
    
        with st.expander("Related tools and what PathwayAI adds"):
            st.markdown("**TickEncounter / TickSpotters** provides tick identification and tick-specific risk information. [Visit TickSpotters](https://web.uri.edu/tickencounter/tickspotters/)")
            st.markdown("**MyLymeData** is a patient-driven registry and research platform. [Explore MyLymeData](https://www.lymedisease.org/mylymedata-impact/)")
            st.markdown("**CDC Lyme surveillance** provides reported-case data and dashboards. [View surveillance](https://www.cdc.gov/lyme/data-research/facts-stats/surveillance-data-1.html)")
            st.write("PathwayAI's pilot brings county surveillance, healthcare capacity, patient-reported burden, and support navigation into one workflow. These external resources are complementary; their data are not linked at the patient level here.")
            st.caption("Resource descriptions reviewed October 6, 2026. Comparison is limited to public website descriptions; no claim of superior clinical performance.")
    with st.expander("Sources and methods", expanded=False):
        st.markdown("**1. Census** — [Dutchess QuickFacts](https://www.census.gov/quickfacts/fact/table/dutchesscountynewyork/DIS010224): poverty 8.4%, uninsured under 65 4.9%, disability under 65 9.2%. Disability uses the 2020–2024 ACS period; uninsured and poverty follow QuickFacts' own source definitions. Separate populations; no combined count.")
        st.markdown("**2. HRSA** — the supplied AHRF county file provides 2023 physician, hospital and population context. It does not measure appointment availability. Live HPSA designations were not retrieved reliably and are not displayed.")
        st.markdown("**3. County assessment** — [2025 Mid-Hudson Regional Community Health Assessment](https://www.dutchessny.gov/Departments/DBCH/Docs/MHRCHA2025.pdf), printed pages 94–96: Dutchess partner survey reports resource awareness, health literacy, rural location, appointment, transport and insurance barriers. These are partner findings about general community health, not Lyme-specific patient prevalence.")
        st.markdown("**4. CDC** — [Clinical care](https://www.cdc.gov/lyme/hcp/clinical-care/index.html) and [treatment](https://www.cdc.gov/lyme/treatment/index.html): early appropriate treatment helps prevent more severe disease. Persistent symptoms need clinical evaluation; no disability reduction is quantified here.")
        st.caption("References checked October 7, 2026. Vehicle-access counts were not retrieved because the Census API required a key; no transport estimate is invented. SPARCS hospital charges have not been loaded and would not equal costs or the full household burden.")
        st.markdown("[Hook societal costs](https://wwwnc.cdc.gov/eid/article/28/6/21-1335-t5) · [Yu medical costs](https://jamanetwork.com/journals/jamanetworkopen/fullarticle/2843880) · [CDC early treatment](https://www.cdc.gov/lyme/treatment/index.html)")
        st.markdown("[HRSA shortage definitions](https://bhw.hrsa.gov/workforce-shortage-areas/shortage-designation) · [County Health Rankings strategies](https://www.countyhealthrankings.org/strategies-and-solutions/what-works-for-health) · [CDC/ATSDR community profiles](https://www.atsdr.cdc.gov/place-health/php/communication-resources/index.html) · [MyLymeData](https://www.lymedisease.org/mylymedata/)")
        st.caption("Public website review: October 6, 2026. These references inform design; no external registry or shortage data are linked into this pilot.")
        st.write("**Exposure:** county/state surveillance only when a compatible source is loaded.")
        st.write("**Reported disease:** Dutchess cards show NYSDOH official 2024 cases and rate. The statewide map and historical export retain CDC 2019–2022 cumulative cases and an approximate rate using 2023 HRSA population; those periods straddle a reporting change and are not a stable annual trend.")
        st.write("**Census:** U.S. Census Bureau QuickFacts provides population and socioeconomic context. These measures are contextual and are not attributed to Lyme disease. The official 2024 county rate uses NYSDOH’s published denominator; the historical map measure uses separately labeled 2023 HRSA population.")
        st.write("**Patient Voice:** only consented, de-identified structured fields are aggregated; missing remains missing, never zero.")
        st.markdown("[Biobank follow-up publication — Horn et al., 2025](https://doi.org/10.3389/fmed.2025.1577936)")
        st.write("**Biobank:** published clinical follow-up findings inform proposed actions; individual-level data are not loaded. **Survey:** the national aggregate snapshot is separate from the local consented layer. Neither supplies county prevalence.")
        st.write("**Savings:** not estimated without observed baseline and follow-up measurements.")
        if ahrf: st.caption("HRSA fields: " + ahrf["fields"])



    # Real county evidence brief: one row per actual field/source, with explicit missingness.
    brief_rows=[]
    def add_brief(metric,value,source,year=""):
        brief_rows.append({"county":policy_place,"fips":fips,"metric":metric,"value":value if value not in (None,"") else "not yet collected","source":source,"year":year})
    add_brief("surveillance_year", exposure_year, "State surveillance", exposure_year or "")
    add_brief("nymph_density_per_1000_m2", exposure_density, "State surveillance", exposure_year or "")
    add_brief("pathogen_positive_percent", exposure_pathogen, "State surveillance", exposure_year or "")
    add_brief("reported_lyme_cases_2024", 1060, "NYSDOH official county cases, page 5", "2024")
    add_brief("official_lyme_rate_per_100000_2024", 355.5, "NYSDOH official county rates, page 5", "2024")
    add_brief("reported_lyme_cases_2019_2022", lyme_cases, "CDC county reported cases", "2019-2022")
    add_brief("average_annual_reported_cases_2019_2022", round(annual_avg_cases,2) if annual_avg_cases is not None else None, "CDC county reported cases; 4-year total divided by 4", "2019-2022")
    add_brief("approx_annualized_crude_rate_per_100000", round(crude_rate,2) if crude_rate is not None else None, "CDC cases + HRSA population; 4-year cases divided by 4", "2019-2022 cases / 2023 population")
    add_brief("census_population_estimate", census_context["population_2025_estimate"], "U.S. Census Bureau QuickFacts", "2025")
    add_brief("census_poverty_percent", census_context["poverty_percent_2020_2024"], "U.S. Census Bureau QuickFacts", "2020-2024")
    add_brief("census_uninsured_under65_percent", census_context["uninsured_under65_percent_2020_2024"], "U.S. Census Bureau QuickFacts", "2020-2024")
    add_brief("census_civilian_labor_force_percent_16plus", census_context["civilian_labor_force_percent_2020_2024"], "U.S. Census Bureau QuickFacts", "2020-2024")
    add_brief("census_disability_under65_percent", census_context["disability_under65_percent_2020_2024"], "Census QuickFacts; not Lyme-attributable", "2020-2024")
    add_brief("ahrf_population", pop, "HRSA AHRF", "2023")
    pcp_rate=(float(ahrf['pcp'])/pop*10000) if ahrf and pop and pd.notna(ahrf.get('pcp')) else None
    add_brief("primary_care_physicians_per_10000", round(pcp_rate,2) if pcp_rate is not None else None, "HRSA AHRF", "2023")
    add_brief("hospital_beds", int(float(ahrf['beds'])) if ahrf and pd.notna(ahrf.get('beds')) else None, "HRSA AHRF", "2023")
    if places is not None and not places.empty:
        for _,r in places.iterrows(): add_brief(f"PLACES_{r['MeasureId']}", r['Data_Value'], "CDC PLACES", r.get('Year',''))
    else:
        add_brief("CDC_PLACES", None, "CDC PLACES")
    add_brief("patient_voice_n", int(len(pv)) if len(pv) >= 5 else "withheld / not yet available", "PathwayAI consented Patient Voice")
    brief=pd.DataFrame(brief_rows)
    brief["evidence_type"] = brief["source"].map(lambda source: "Patient-reported pilot" if "Patient Voice" in source else "Public model-based estimate" if "PLACES" in source else "Derived public-data measure" if "+" in source or "divided" in source else "Public county context / surveillance")
    brief["interpretation"] = brief["evidence_type"].map({
        "Patient-reported pilot": "Consented pilot contributions; not population prevalence",
        "Public model-based estimate": "All-cause adult context; not Lyme-attributable; not interchangeable with Census under-65 measures",
        "Derived public-data measure": "Approximate derived measure; source periods differ; not personal risk or predicted savings",
        "Public county context / surveillance": "County context; no inference of individual risk or Lyme-attributable cost",
    })
    st.download_button("Download County Evidence Brief", brief.to_csv(index=False).encode("utf-8"), file_name=f"pathwayai_county_brief_{fips}.csv", mime="text/csv")
    st.download_button("Download County Action Plan", actions.to_csv(index=False).encode("utf-8"), file_name=f"pathwayai_action_plan_{fips}.csv", mime="text/csv")
    st.stop()

st.header("🧭 TIMELY CARE & SUPPORT")
show_section_hero("journey", "Understand Your Journey. Plan Your Next Step.", 'Organize symptoms, tests, care, costs and daily-life impact for your next healthcare visit.')

with st.expander("Patient Voice · sources & notes"):
    st.caption("Patient-reported pilot experiences, not county-wide findings. Counts use answered fields; missing is not zero. Local summaries require consent and at least five usable responses per measure.")
st.write('Organize your story for care. Sharing structured Patient Voice information is optional.')
# QUICK START — STORY FIRST

# Location is intentionally optional and comes after the patient receives immediate value.
# This keeps the opening experience supportive rather than feeling like data collection.
current_location_start = st.session_state.get("current_location_start", "")

st.markdown("## 💬 TELL US YOUR STORY")
st.markdown("**Low on energy? Start here. One or two sentences are enough.**")
st.write('Write a sentence or two, then review your Journey Record. The detailed questions are optional.')
st.warning("🔒 **Protect your privacy:** Please do not enter your name, date of birth, street address, phone number, email, medical record number, or other identifying information.")

STORY_SAMPLE = 'I visited Maryland in June and had a tick bite. A few days later I developed a rash and became extremely tired and dizzy. I have felt this way for about two weeks. I had a Lyme blood test last week and was told it was negative. I have seen two doctors, missed five days of work, and spent about $600. I am now back home in Boston.'
st.markdown("#### Not sure what to write? Follow this example")
st.caption('Use only the details relevant to you.')
st.markdown(f"> {STORY_SAMPLE}")

if "quick_story_value" not in st.session_state:
    st.session_state.quick_story_value = ""

if st.button("Try this example", help="Copies the example into the story box so you can edit only the details that apply to you."):
    st.session_state.quick_story_value = STORY_SAMPLE

st.caption("AI processing notice: if the optional AI extraction is enabled, your story may be sent to the configured AI service for processing. Do not include names or other direct identifiers. Raw story text is not written to the Patient Voice CSV by PathwayAI.")
use_story_ai = st.checkbox("Use optional AI to organize my story", value=True, key="use_story_ai65", help="Turn off for local processing, including agency demonstrations. Daily-life answers are not sent to AI.")
quick_story = st.text_area(
    "Tell us what happened in your own words",
    key="quick_story_value",
    placeholder="Start anywhere — even one or two sentences are enough.",
    height=180,
    max_chars=MAX_STORY_CHARS,
)
st.caption('Omitted details remain Not reported.')
organize_story = st.button("✨ Organize My Story", type="primary", use_container_width=True, disabled=not bool(quick_story.strip()))
if organize_story:
    st.session_state["story_organized"] = True
    # Use the configured LLM only after an explicit click and within the pilot call limit.
    # A failed/unavailable LLM never blocks the local rule-based fallback.
    rule_now = extract_quick_story(quick_story)
    allowed, limit_message = ai_call_allowed("story-extraction")
    if use_story_ai and allowed and OPENAI_API_KEY and PATHWAYAI_LLM_MODEL:
        llm_record, llm_status = extract_story_with_llm(quick_story)
        if llm_record is not None and llm_status.get("state") == "connected":
            st.session_state["organized_story_record"] = merge_llm_into_quick(rule_now, llm_record)
            st.session_state["organized_story_source"] = quick_story
            record_completed_ai_call()
        else:
            st.session_state["organized_story_record"] = merge_llm_into_quick(rule_now, None)
            st.session_state["organized_story_source"] = quick_story
    else:
        st.session_state["organized_story_record"] = merge_llm_into_quick(rule_now, None)
        st.session_state["organized_story_source"] = quick_story
        if not allowed:
            st.info(limit_message + " Using local backup extraction.")
if not quick_story.strip():
    st.session_state["story_organized"] = False
    st.session_state.pop("organized_story_record", None)
    st.session_state.pop("organized_story_source", None)

if st.session_state.get("story_organized", False):
    method = (st.session_state.get("organized_story_record") or {}).get("extraction_method", "Rule-based NLP fallback")
    if method == "LLM structured extraction":
        st.caption("Organized with AI. Review every detail for errors.")
    else:
        st.caption('Organized with local rules. Review for errors.')

st.caption("Details you leave out remain **Not reported**.")

rule_quick = extract_quick_story(quick_story)
if st.session_state.get("organized_story_source") == quick_story:
    quick = st.session_state.get("organized_story_record", rule_quick)
else:
    quick = rule_quick

if quick_story.strip() and st.session_state.get("story_organized", False):
    st.markdown("#### Your Journey Record")
    r1, r2 = st.columns(2)
    with r1:
        st.write("**Possible exposure:** " + (quick.get("exposure_location") or "Not reported"))
        st.write("**Exposure month:** " + (quick.get("month") or "Not reported"))
        st.write("**Tick exposure:** " + (quick.get("tick") or "Not reported"))
        st.write("**Symptoms:** " + (", ".join(quick.get("symptoms", [])) if quick.get("symptoms") else "Not reported"))
    with r2:
        st.write("**Current/home location:** " + (quick.get("current_location") or quick.get("zip") or "Not reported"))
        st.write("**Duration:** " + (quick.get("duration_text") or "Not reported"))
        st.write("**Work/function:** " + ((quick.get("work_impact") if quick.get("work_impact") != "Not reported" else None) or (", ".join(quick.get("function", [])) if quick.get("function") else "Not reported")))
        st.write("**Healthcare professionals:** " + (str(quick.get("providers_seen")) if quick.get("providers_seen") is not None else "Not reported"))
    st.caption("Review the record and correct anything PathwayAI misunderstood. Missing information stays missing.")
    show_immediate_support_from_story(quick)
elif quick_story.strip():
    st.info('Click **Organize My Story** to view your record.')
else:
    st.caption("Prefer structured questions? You can skip the story box and use the optional details below.")

# Optional whole-person context: patient-reviewed, session-only, no composite score.
st.markdown("### Daily life and your next appointment")
st.caption("Optional. Use this without AI or contributing to Patient Voice.")
with st.expander("What would you like help with?"):
    daily_areas = st.multiselect("Which areas would you like to discuss?", ["Daily activities", "Sleep", "Stress", "Relationships / social connection", "Managing care", "Work / school", "Food / household bills"], key="daily_areas63")
    daily_note = st.text_area("What has changed, and what would help?", key="daily_note63", max_chars=1200, placeholder="For example: shopping is harder, and I need help arranging appointments.")
    appointment_questions = st.text_area("Questions for your clinician", key="appointment_questions63", max_chars=1200, placeholder="What follow-up should I plan? What else could explain my symptoms?")
    st.caption("Whole-person health-informed questions; not the nine-item Whole Person Health Index or a validated score. These optional answers stay in this session and your download; they are not sent to AI or saved to Patient Voice.")
    st.markdown("[Measurement research · NCHS RANDS, 2026](https://pubmed.ncbi.nlm.nih.gov/42221536/)")

# Support appears immediately beside the selections, with no ZIP requirement.
if daily_areas:
    st.markdown("**Support you selected**")
    if "Food / household bills" in daily_areas:
        st.markdown("[Food and emergency food assistance — USA.gov](https://www.usa.gov/food-help) · [Local food, housing and bill support — 211](https://www.211.org/)")
    if "Daily activities" in daily_areas:
        st.markdown("[Daily-activity and caregiver support options — USA.gov](https://www.usa.gov/disability-caregiver)")
    if "Work / school" in daily_areas:
        st.markdown("[Workplace leave information — U.S. Department of Labor](https://www.dol.gov/agencies/whd/fmla)")
    if any(x in daily_areas for x in ["Stress", "Relationships / social connection", "Managing care"]):
        st.markdown("[Find local community and caregiver resources — 211](https://www.211.org/)")
    if "Sleep" in daily_areas:
        st.write("Include sleep changes in your appointment questions.")
    st.caption("Resource navigation; services and eligibility must be confirmed with the program.")

summary_lines = ["PATHWAYAI · APPOINTMENT SUMMARY", "Patient-reported and editable; no diagnosis or test interpretation.", "", "YOUR EXPERIENCE"]
for label, value in [
    ("Possible exposure location", quick.get("exposure_location")),
    ("Exposure month", quick.get("month")),
    ("Duration", quick.get("duration_text")),
    ("Symptoms", ", ".join(quick.get("symptoms") or [])),
    ("Previous testing", quick.get("llm_test_status") or ("Testing mentioned; details to confirm" if quick.get("tested") else None)),
    ("Healthcare professionals seen", quick.get("providers_seen")),
    ("Work / daily function", quick.get("work_impact")),
]:
    summary_lines.append(f"{label}: {value if value is not None and value != '' else 'Not reported'}")
summary_lines += ["", "DAILY LIFE", ", ".join(daily_areas) or "Not reported", daily_note or "", "", "QUESTIONS FOR MY CLINICIAN", appointment_questions or "Not reported", "", "Bring original test reports and a medication list. Unknown dates remain unknown."]
summary_seed = "\n".join(summary_lines)
# Refresh derived text only when inputs change; preserve manual corrections on reruns.
if st.session_state.get("appointment_seed63") != summary_seed:
    st.session_state["appointment_edit63"] = summary_seed
    st.session_state["appointment_seed63"] = summary_seed
with st.expander("Review and download your appointment summary"):
    appointment_text = st.text_area("Correct the summary before sharing", key="appointment_edit63", height=280, max_chars=8000)
    st.download_button("Download appointment summary", appointment_text.encode("utf-8"), file_name="MyJourney.txt", mime="text/plain", key="appointment_download63")

# OPTIONAL LOCAL SUPPORT — ask only after the story/AI value exchange.
st.markdown("### 📍 Find Support Near You *(Optional)*")
st.write('Add a ZIP or county for local care and support resources.')
st.caption("ZIP or county only; no street address needed.")
current_location_start = st.text_input(
    "ZIP code or county (optional)",
    key="current_location_start",
    placeholder="e.g., 21044 or Howard County, MD",
    help="Optional. Used only to tailor local navigation and resources; not to determine a diagnosis."
)
care_location = current_location_start.strip()
care_zip = care_location if re.fullmatch(r"[0-9]{5}", care_location) else ""
valid_care_zip = bool(care_zip)
st.markdown("#### Find nearby care")
health_center_url = "https://findahealthcenter.hrsa.gov/" + ("?" + urlencode({"zip": care_zip, "radius": 25}) if care_zip else "")
if care_location and not (care_location.isdigit() and not care_zip):
    st.markdown(f"[Find primary care or infectious-disease clinicians near {html.escape(care_location)}]({google_maps_search_url('primary care or infectious disease doctor near ' + care_location)})")
    st.caption("Local map search; results are not a verified Lyme specialist directory.")
else:
    st.caption("Enter a five-digit ZIP or a county and state to see a nearby provider search.")
st.markdown(f"[Find affordable community care — HRSA]({health_center_url})")
st.markdown("[Compare clinicians who accept Medicare — Medicare Care Compare](https://www.medicare.gov/care-compare/)")
st.caption("Confirm tick-borne illness experience, availability and insurance with the provider.")
with st.expander("What to bring and ask"):
    st.write("Bring exposure and symptom dates, test reports, medicines and your reviewed journey summary. Ask how test timing affects interpretation and what follow-up is appropriate.")
    st.markdown("[CDC testing information](https://www.cdc.gov/lyme/diagnosis-testing/)")

st.markdown("#### Support for you")
st.caption("Use these resources without completing the form or sharing your story.")
support_left, support_right = st.columns(2)
with support_left:
    st.markdown("[Housing and shelter help — HUD](https://www.hud.gov/FindShelter)")
    st.markdown("[Temporary financial assistance — find your state](https://www.usa.gov/welfare-benefits)")
    st.markdown("[Disability benefits — SSA](https://www.ssa.gov/disability)")
with support_right:
    st.markdown("[Lyme peer support — Global Lyme Alliance](https://www.globallymealliance.org/lyme-patient-support/)")
    st.markdown("[State and online Lyme groups](https://www.lymedisease.org/lyme-disease-support-groups/)")
    st.markdown("[Local food, transport and other help — 211](https://www.211.org/)")
if care_zip.startswith(("125", "126")) or "dutchess" in care_location.casefold():
    with st.expander("Dutchess / New York assistance"):
        st.markdown("[New York Temporary Assistance](https://otda.ny.gov/programs/temporary-assistance/)")
        st.markdown("[Dutchess Community & Family Services](https://www.dutchessny.gov/Departments/Community-Family-Services/Community-and-Family-Services.htm) · Temporary assistance: 845-486-3190")
        st.caption("Shown for an entered Dutchess location or a Hudson Valley ZIP prefix. Confirm your county; prefixes do not establish residence or eligibility.")
st.caption("Eligibility and availability vary. Peer groups provide support, not medical care.")

# PATIENT VOICE — explicit review/permission; MVP demonstrates the consent loop without publishing raw narrative.
if quick_story.strip() and st.session_state.get("story_organized", False):
    st.markdown("### 🗣️ Make Your Experience Count *(Optional)*")
    st.write('With your consent, reviewed structured fields can contribute to aggregated Patient Voice findings.')
    heard=[]
    if quick.get("providers_seen"): heard.append("Care access / navigation")
    if quick.get("cost_amount"): heard.append("Out-of-pocket / financial burden")
    if quick.get("function") or (quick.get("work_impact") and quick.get("work_impact") != "Not reported"): heard.append("Work / daily-life impact")
    if quick.get("tested") or quick.get("llm_test_status"): heard.append("Testing journey")
    if quick.get("exposure_location"): heard.append("Exposure / travel context")
    if heard:
        st.markdown("**From your story, we heard:** " + " • ".join(heard))
    else:
        st.write("PathwayAI can still organize your journey; you do not need to contribute anything to Patient Voice.")
    accurate = st.checkbox("This is an accurate reflection of the themes I want to share.", key="pv_review")
    consent = st.checkbox("I agree that these de-identified structured themes may contribute to aggregated PathwayAI Patient Voice.", key="pv_consent", disabled=not accurate)
    if accurate and consent:
        st.success("✓ Your voice can contribute to aggregated Patient Voice after you review the structured fields below.")
        st.selectbox("County for aggregation (optional)", ["Not selected", "Dutchess County, New York", "Chester County, Pennsylvania", "Carroll County, Maryland"], key="pv_county_choice")
        st.caption("Your Journey → Your Voice → Population Insight → Policy Action")
    else:
        st.caption("Sharing is optional. You still receive the same PathwayAI journey and preparation support if you do not contribute.")

# Apply optional location to the structured journey after it is entered.
if current_location_start.strip():
    loc_start = current_location_start.strip()
    if len(normalize_zip(loc_start)) == 5 and loc_start.replace("-", "").isdigit():
        quick["zip"] = normalize_zip(loc_start)
    if not quick.get("current_location"):
        quick["current_location"] = loc_start

st.markdown("### Want to tell us more? *(Optional)*")
st.caption('Add details if useful. You can stop after organizing your story.')

# 1. LOCATION & EXPOSURE CONTEXT

st.subheader("1. Location & Exposure Context *(Optional)*")
st.write('Check your location for nearby care and support. This is optional.')

top_zip = normalize_zip(current_location_start)
zip_code = care_zip  # One editable current-care location, shared by all navigation.

location = destination_label(zip_code)
resolved_support_zip = resolve_us_zip(zip_code) if len(normalize_zip(zip_code)) == 5 else None
if len(normalize_zip(zip_code)) == 5 and resolved_support_zip is None:
    st.caption("ZIP accepted. The city could not be resolved from the geographic lookup service; PathwayAI will not guess a city or county.")
current_support_location = clean_location_phrase(quick.get("current_location") or "")
if len(normalize_zip(zip_code)) == 5:
    current_support_location = location
    st.write(f"**Current support/care location:** {location}")
elif current_support_location:
    st.success(f"**Current support/care location from your story:** {current_support_location}")
    st.caption("A ZIP code is optional. Add one above only if you want more precise nearby navigation.")

exposure_place = st.text_input(
    "Where might the exposure have happened? (city, county, state, or ZIP)",
    value=clean_location_phrase(quick.get("exposure_location") or ""),
    placeholder="e.g., Dutchess County, NY",
    help="Used for tick/environmental surveillance context. This can be somewhere you visited and does not have to be where you live."
)
st.caption('Exposure location informs surveillance; current location informs care searches.')

month_options = [
    "Not reported", "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]
month_default = month_options.index(quick["month"]) if quick["month"] in month_options else 0
month = st.selectbox(
    "When are you going or when were you there?",
    month_options,
    index=month_default,
)

# 2. PERSONAL CONTEXT

st.subheader("2. Personal Context")

age = st.number_input(
    "Age",
    min_value=1,
    max_value=120,
    value=int(quick["age"]) if quick.get("age") is not None else None,
    placeholder="Not reported",
    help="Leave blank if age was not stated. PathwayAI does not invent a default age."
)

immune = st.selectbox(
    "Are you immunocompromised or do you have a relevant immune condition?",
    ["Not reported", "No", "Yes", "Unsure"],
    index=0
)

# 3. EXPOSURE DETAILS

st.subheader("3. Exposure Details")

tick_options = ["Not reported", "No", "Yes", "Unsure"]
tick_default = tick_options.index(quick["tick"]) if quick["tick"] in tick_options else 0
tick_bite = st.selectbox(
    "Did you have a tick bite?",
    tick_options,
    index=tick_default
)

attachment = st.selectbox(
    "Approximate attachment duration",
    ["Not reported", "Unsure", "<24 hours", "24–36 hours", ">36 hours"]
)

# 4. SYMPTOMS

st.subheader("4. Symptoms")

quick_symptom_text = " ".join(quick.get("symptoms") or []).lower()
rash = st.checkbox("New or expanding rash", value=("rash" in quick_symptom_text or "erythema migrans" in quick_symptom_text))
fever = st.checkbox("Fever", value=("fever" in quick_symptom_text or "chill" in quick_symptom_text))
fatigue = st.checkbox("Fatigue", value=any(x in quick_symptom_text for x in ["fatigue","sleepy","sleepiness","weak","exhaust"]))
headache = st.checkbox("Headache", value=("headache" in quick_symptom_text))
pain = st.checkbox("Muscle or joint pain", value=("muscle" in quick_symptom_text or "joint" in quick_symptom_text))

symptoms = []

if rash:
    symptoms.append("New or expanding rash")
if fever:
    symptoms.append("Fever")
if fatigue:
    symptoms.append("Fatigue")
if headache:
    symptoms.append("Headache")
if pain:
    symptoms.append("Muscle or joint pain")

# 5. TESTING & INTERPRETATION CONTEXT

st.subheader("5. 🧪 Understanding Your Testing & Next Steps")
st.write("**If Lyme disease is being evaluated, these are tests you may commonly encounter:**")
tc1, tc2 = st.columns(2)
with tc1:
    st.markdown("**Usual laboratory approach — two-step antibody testing**")
    st.write("• First step: an FDA-cleared enzyme immunoassay (EIA) or another FDA-cleared first-tier antibody assay.")
    st.write("• If the first step is positive or equivocal, the laboratory performs the second step.")
    st.write("• Standard two-tier testing uses an EIA followed by an immunoblot/Western blot; modified two-tier testing uses two EIAs.")
with tc2:
    st.markdown("**Why timing and symptoms matter**")
    st.write("• Antibodies can take several weeks to develop, so testing may be falsely negative early.")
    st.write("• A likely erythema migrans (EM) rash with plausible exposure is a special clinical situation in which clinicians may not rely on acute serology.")
    st.write("• Testing is interpreted together with exposure history, symptoms, timing, and other possible causes.")
st.caption("Evidence basis: CDC Lyme disease testing guidance and CDC clinical guidance for erythema migrans. This is educational navigation, not a recommendation that every person needs testing.")

test_status_options = ["Not reported / not sure", "No testing yet", "Yes — once", "Yes — more than once"]
llm_ts = quick.get("llm_test_status")
test_default = 0
if isinstance(llm_ts, str):
    lo = llm_ts.lower()
    if "more than once" in lo or "multiple" in lo: test_default = 3
    elif "yes" in lo or "tested" in lo: test_default = 2
    elif "no" in lo: test_default = 1
test_status = st.selectbox("Have you already had Lyme disease testing related to this journey?", test_status_options, index=test_default)

test_type = "Not reported"
test_result = "Not reported"
test_timing = "Not reported"
second_opinion = "Not reported"
if test_status in ["Yes — once", "Yes — more than once"]:
    st.markdown("#### Help PathwayAI understand the test you already had")
    test_type = st.selectbox(
        "What test name/type appears on your report?",
        ["Not sure / not reported", "EIA / ELISA / enzyme immunoassay", "Western blot / immunoblot", "Standard two-tier testing", "Modified two-tier testing", "IgM and/or IgG reported", "Other"]
    )
    test_result_options = ["Not reported", "Positive / reported positive", "Negative / reported negative", "Equivocal / indeterminate", "Different or unclear results"]
    llm_tr = str(quick.get("llm_test_result") or "").lower()
    tr_default = 0
    if "positive" in llm_tr: tr_default = 1
    elif "negative" in llm_tr: tr_default = 2
    elif "equiv" in llm_tr or "indeterminate" in llm_tr: tr_default = 3
    elif llm_tr: tr_default = 4
    test_result = st.selectbox("What did the report say?", test_result_options, index=tr_default)
    test_timing = st.selectbox(
        "When was this test performed relative to symptom onset?",
        ["Not reported / unsure", "Within 1 week", "1–4 weeks", "More than 4 weeks", "More than 30 days"]
    )
    second_opinion = st.selectbox(
        "Did you seek another clinical opinion because results or symptoms remained unclear?",
        ["Not reported / unsure", "No", "Yes"]
    )
else:
    st.info("If you have not been tested, PathwayAI can still help you understand the usual CDC testing pathway and prepare questions for a healthcare professional.")

st.caption("PathwayAI does not diagnose Lyme disease from a laboratory result. Missing information remains Not reported rather than being treated as negative.")

st.markdown("#### Questions that may help with next steps")
st.write("• Ask how the **timing and type of testing** affect interpretation of your result.")
st.write("• Review the result together with your **symptoms and exposure history**, rather than interpreting the laboratory result by itself.")
st.write("• If symptoms, exposure history, and testing remain unclear, ask whether **additional evaluation** may be appropriate.")
st.write("• If uncertainty continues, consider whether a **second clinical opinion** would be useful.")
st.caption("These are neutral discussion prompts for a healthcare professional, not diagnosis or treatment recommendations.")

# 6. FUNCTIONAL IMPACT & DISABILITY

st.subheader("6. Protect My Function — Functional Impact & Support Preparedness")

daily_options = ["Not reported", "No limitation", "Some limitation", "Major limitation", "Unable to perform usual activities"]
daily_default = daily_options.index(quick["daily_function"]) if quick["daily_function"] in daily_options else 0
daily_function = st.selectbox("How much has your condition affected your usual daily activities?", daily_options, index=daily_default)

work_options = ["Not reported", "No impact", "Reduced hours", "Missed work or school", "Stopped working or school", "On disability", "Not applicable"]
work_default = work_options.index(quick["work_impact"]) if quick["work_impact"] in work_options else 0
work_impact = st.selectbox("Has your condition affected your work or school?", work_options, index=work_default)

days_default = int(quick["days_missed"]) if quick["days_missed"] is not None else None
days_missed_input = st.number_input("Approximately how many work or school days have you missed?", min_value=0, max_value=3650, value=days_default, placeholder="Not reported",
    help="Leave blank if not reported. If your story explicitly described inability to work for a duration, PathwayAI may prefill a modeled workday equivalent; review it before using.")
days_missed = int(days_missed_input) if days_missed_input is not None else None
days_missed_reported = days_missed_input is not None

# 7. PATIENT JOURNEY & ECONOMIC BURDEN

st.subheader("7. Patient Journey & Economic Burden")

diagnostic_delay = st.selectbox(
    "How long did it take from your first symptoms to a Lyme disease diagnosis?",
    [
        "Not reported",
        "No diagnosis yet",
        "Less than 1 month",
        "1–3 months",
        "4–6 months",
        "7–12 months",
        "More than 1 year"
    ]
)

providers_seen_input = st.number_input(
    "Approximately how many healthcare professionals have you seen for these symptoms?",
    min_value=0,
    max_value=100,
    value=int(quick["providers_seen"]) if quick["providers_seen"] is not None else None,
    placeholder="Not reported"
)
providers_seen = int(providers_seen_input) if providers_seen_input is not None else None
providers_seen_reported = providers_seen_input is not None

pre_dx_visits = st.selectbox(
    "Before diagnosis, approximately how many healthcare visits did you have related to these symptoms?",
    ["Not reported", "0", "1–2", "3–5", "6–10", "More than 10"]
)
travel_distance = st.selectbox(
    "How far did you typically travel for Lyme-related care?",
    ["Not reported", "Less than 10 miles", "10–25 miles", "26–50 miles", "51–100 miles", "More than 100 miles"]
)
outside_area_care = st.selectbox(
    "Did you travel outside your county or state for care?",
    ["Not reported", "No", "Outside my county", "Outside my state"]
)

oop_options = ["Not reported", "$0–$499", "$500–$999", "$1,000–$4,999", "$5,000–$9,999", "$10,000–$24,999", "$25,000–$49,999", "$50,000 or more", "Unsure / prefer not to answer"]
qc = quick["cost_amount"]
if qc is None: oop_default = "Not reported"
elif qc < 500: oop_default = "$0–$499"
elif qc < 1000: oop_default = "$500–$999"
elif qc < 5000: oop_default = "$1,000–$4,999"
elif qc < 10000: oop_default = "$5,000–$9,999"
else: oop_default = "$10,000 or more"
oop_cost = st.selectbox("Approximately how much have you paid out of pocket related to this illness?", oop_options, index=oop_options.index(oop_default))

st.markdown("#### Access, Coverage & Support Context")
insurance_context = st.selectbox(
    "Did insurance, coverage, or cost affect when or where you sought care?",
    ["Not reported", "No access or coverage barrier reported", "Uninsured during part of the journey", "Underinsured / high out-of-pocket costs", "Delayed or skipped care because of cost", "Insurance/network limited care options", "Unsure / prefer not to answer"]
)
support_needs = st.multiselect(
    "Which support areas would be useful to explore?",
    ["Disability benefits", "Workplace leave / FMLA", "Health coverage", "Food assistance", "Housing / rent", "Utilities", "Transportation", "Caregiver / family support"]
)

if quick["cost_amount"] is not None:
    st.info(f"From your story: approximately ${quick['cost_amount']:,.0f} in patient-reported illness-related cost. This is kept separate unless you choose to break it into categories below.")
st.markdown("#### Optional transparent cost inputs")
st.caption('Enter known amounts; leave unknown costs blank.')
medical_cost = st.number_input("Medical / healthcare spending ($)", min_value=0.0, value=None, step=100.0)
second_opinion_cost = st.number_input("Second opinion / specialist evaluation spending ($)", min_value=0.0, value=None, step=100.0, help="This may represent appropriate or beneficial care. PathwayAI does not automatically treat it as avoidable.")
repeat_testing_cost = st.number_input("Repeat / duplicative testing or fragmented-care spending ($)", min_value=0.0, value=None, step=100.0, help="Enter only costs you can reasonably distinguish from necessary follow-up or clinically indicated testing.")
transport_cost = st.number_input("Transportation / lodging for care ($)", min_value=0.0, value=None, step=50.0)
self_care_cost = st.number_input("OTC products, supplies, or other self-paid supportive care ($)", min_value=0.0, value=None, step=50.0)
caregiver_hours = st.number_input("Unpaid family/friend caregiving time (hours, optional)", min_value=0.0, value=None, step=1.0)
caregiver_missed_work = st.selectbox("Did a caregiver miss work or reduce work hours because of your illness?", ["Not reported", "No", "Yes"])

navigation_hours = st.number_input("Time spent finding care, arranging visits, dealing with insurance/benefits, or navigating support (hours, optional)", min_value=0.0, value=None, step=1.0)
income_loss_band = st.selectbox("Estimated income lost because of illness (optional)", ["Not reported", "$0", "Less than $1,000", "$1,000–$4,999", "$5,000–$9,999", "$10,000–$24,999", "$25,000–$49,999", "$50,000 or more", "Unsure / prefer not to answer"])


# Review and persist only consented, de-identified structured Patient Voice fields.
if st.session_state.get("pv_review") and st.session_state.get("pv_consent"):
    county_choice = st.session_state.get("pv_county_choice", "Not selected")
    fips_map = {"Dutchess County, New York":"36027", "Chester County, Pennsylvania":"42029", "Carroll County, Maryland":"24013"}
    chosen_fips = fips_map.get(county_choice)
    if chosen_fips:
        preview_row = {
            "FIPS": chosen_fips,
            "Delay band": None if diagnostic_delay == "Not reported" else diagnostic_delay,
            "Healthcare professionals": providers_seen,
            "Pre-diagnosis visits": None if pre_dx_visits == "Not reported" else pre_dx_visits,
            "OOP band": None if oop_cost == "Not reported" else oop_cost,
            "Workdays": days_missed,
            "Caregiver hours": caregiver_hours if caregiver_hours and caregiver_hours > 0 else None,
            "Function": None if daily_function == "Not reported" else daily_function,
        }
        st.markdown("#### Review what will be saved to Patient Voice")
        preview_df = pd.DataFrame([{"Field": k, "Value": ("Not reported" if v is None else v)} for k,v in preview_row.items()])
        show_readable_table(preview_df, hide_index=True, width="stretch")
        st.caption("Only the reviewed fields below are saved to the pilot file; your raw story is not included.")
        if not st.session_state.get("pv_saved", False):
            if st.button("Contribute these reviewed fields to Patient Voice", key="save_patient_voice"):
                row = {
                    "fips": chosen_fips,
                    "delay_band": preview_row["Delay band"],
                    "providers_seen": providers_seen,
                    "visits": preview_row["Pre-diagnosis visits"],
                    "oop_band": preview_row["OOP band"],
                    "workdays": days_missed,
                    "caregiver_hours": preview_row["Caregiver hours"],
                    "function": preview_row["Function"],
                    "consent_time": pd.Timestamp.utcnow().isoformat(),
                }
                if append_patient_voice(row):
                    st.session_state["pv_saved"] = True
                    st.success("Thank you so much for helping make the invisible journey visible. Your contribution helps us understand the challenges people face and the support they need.")
                else:
                    st.warning("The structured record could not be saved in this run. Your raw story was not written to the Patient Voice file.")
        else:
            st.success("✓ This reviewed Patient Voice record has already been saved in this session.")
    else:
        st.caption("Choose a county above if you want these fields included in a county-level Patient Voice count.")
daily_productivity_value = st.number_input("Estimated value per missed work/school day ($, optional)", min_value=0.0, value=None, step=25.0)

st.markdown("#### Optional user-entered earlier-action scenario")
st.caption("Use only amounts/days you think might plausibly have been avoided with earlier navigation or support. PathwayAI does not assume these savings or claim causality.")
avoid_repeat_cost = st.number_input("Duplicative testing / fragmented-care cost that might have been reduced ($)", min_value=0.0, value=None, step=100.0, help="Do not include a useful second opinion or clinically indicated follow-up simply because it was additional care.")
avoid_transport_cost = st.number_input("Transportation / lodging cost that might have been avoided ($)", min_value=0.0, value=None, step=50.0)
avoid_days = st.number_input("Missed work/school days that might have been avoided", min_value=0, max_value=3650, value=0)
def _num0(value):
    return 0.0 if value is None else float(value)

scenario_savings = _num0(avoid_repeat_cost) + _num0(avoid_transport_cost) + float(avoid_days) * _num0(daily_productivity_value)

# GENERATE CARD

if st.button("Generate Full Journey & Burden Card (Optional)", type="secondary"):

    symptoms = []

    if rash:
        symptoms.append("New or expanding rash")
    if fever:
        symptoms.append("Fever")
    if fatigue:
        symptoms.append("Fatigue")
    if headache:
        symptoms.append("Headache")
    if pain:
        symptoms.append("Muscle or joint pain")

    story_symptoms = [str(x) for x in (quick.get("symptoms") or [])]
    combined_symptoms = []
    for s in story_symptoms + symptoms:
        if s and s.lower() not in [x.lower() for x in combined_symptoms]:
            combined_symptoms.append(s)
    symptom_text = ", ".join(combined_symptoms) if combined_symptoms else "Not reported"

    st.divider()
    st.header("My PathwayAI Journey Card")

    # Journey at a glance — make the invisible pathway visible before details
    st.subheader("Journey at a Glance")
    j1, j2, j3, j4, j5, j6 = st.columns(6)
    j1.markdown("**1 · Exposure**")
    j1.caption("Tick / place / time")
    j2.markdown("**2 · Symptoms**")
    j2.caption(symptom_text)
    j3.markdown("**3 · Testing**")
    j3.caption(test_status)
    j4.markdown("**4 · Care**")
    j4.caption(f"{providers_seen} professionals" if providers_seen_reported else "Not reported")
    j5.markdown("**5 · Function**")
    j5.caption(daily_function)
    j6.markdown("**6 · Burden**")
    j6.caption(oop_cost)
    st.caption("PathwayAI keeps exposure, symptoms, testing, care utilization, function, and economic burden as separate signals so one does not get mistaken for another.")

    # Exposure

    st.subheader("Exposure Context")

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Location", location)
        st.metric("ZIP Code", normalize_zip(zip_code) or "Not entered")
        st.metric("Travel Month", month)

    with col2:
        st.metric("Age", age)
        st.metric("Tick Bite", tick_bite)

    st.write(f"**Attachment duration:** {attachment}")
    st.write(f"**Immune status:** {immune}")
    st.write(f"**Reported symptoms:** {symptom_text}")

    if infer_pilot_location(zip_code) == "Dutchess County, New York" and latest_dutchess is not None:
        st.subheader("Local Environmental Surveillance")

        st.write(f"**NYSDOH surveillance year:** {int(latest_dutchess['Year'])}")
        st.write(f"**Nymph ticks collected:** {int(latest_dutchess['Total Ticks Collected'])}")
        st.write(f"**Nymph tick population density:** {latest_dutchess['Tick Population Density']}")
        st.write(f"**Nymphs tested:** {int(latest_dutchess['Total Tested'])}")
        st.write(f"**B. burgdorferi positive:** {latest_dutchess['B. burgdorferi (%)']}")

        st.caption(
        "Source: New York State Department of Health deer tick surveillance. "
        "These environmental surveillance data do not represent an individual's "
        "probability of Lyme disease."
    )



    # Navigation

    st.subheader("Journey Navigator — What Needs Attention Now?")
    nav_items = []
    if tick_bite == "Yes" or attachment == "Unsure":
        nav_items.append(("Exposure record", "Capture date/place, tick details if known, and changes after exposure."))
    if symptoms:
        nav_items.append(("Symptom timeline", "Track onset, progression, and what affects daily function."))
    if str(test_status).startswith("Yes"):
        # Testing context is shown only when the patient reports testing.
        nav_items.append(("Testing context", "Keep test type, timing, result, and the clinical interpretation together."))
    if (providers_seen is not None and providers_seen >= 2) or second_opinion == "Yes":
        nav_items.append(("Care continuity", "Bring one concise timeline across clinicians to reduce fragmented history."))
    if daily_function not in ["Not reported", "No limitation"] or work_impact not in ["Not reported", "No impact", "Not applicable"]:
        nav_items.append(("Function & work", "Document activity limits, missed days, reduced hours, and support needs."))
    if _num0(medical_cost) + _num0(repeat_testing_cost) + _num0(transport_cost) > 0 or (days_missed is not None and days_missed > 0):
        nav_items.append(("Economic burden", "Keep direct spending and productivity loss separate and source-labeled."))
    if nav_items:
        for label, action in nav_items:
            st.markdown(f"**{label}:** {action}")
    else:
        st.write("No major navigation need is identifiable from the information entered so far.")
    st.caption("Navigation support only — not a diagnosis, treatment recommendation, or validated risk score.")

    st.subheader("Details for your clinician")

    signals = []

    if tick_bite == "Yes":
        signals.append("reported tick exposure")

    if attachment == "Unsure":
        signals.append("unknown attachment duration")

    if rash:
        signals.append("new or expanding rash")

    if fever:
        signals.append("fever")

    if fatigue:
        signals.append("fatigue")

    if immune == "Yes":
        signals.append("relevant immune condition")

    st.write("**You reported:** " + (", ".join(signals) if signals else "No exposure or symptom details entered in these fields."))
    st.caption("Review these entries with your clinician. Missing or unchecked details do not establish that symptoms or exposure are absent.")

    # Testing / interpretation context

    st.subheader("🧪 What Your Testing Information Means")
    t1, t2 = st.columns(2)
    with t1:
        st.metric("Testing history", test_status)
        st.write(f"**Test type:** {test_type}")
        st.write(f"**Timing:** {test_timing}")
    with t2:
        st.metric("Reported result", test_result)
        st.write(f"**Second clinical opinion:** {second_opinion}")

    if test_status in ["Not reported / not sure", "No testing yet"]:
        st.markdown("**What you may encounter:** CDC recommends FDA-cleared **two-step serologic (antibody) testing** when laboratory testing is indicated. The first step is an EIA or another FDA-cleared first-tier assay. A positive/equivocal first step is followed by a second-tier assay.")
        st.info("Whether testing is useful depends on exposure, symptoms, timing, and the clinical picture. A healthcare professional can decide whether testing is indicated for your situation.")
    else:
        if "Negative" in test_result and test_timing in ["Within 1 week", "1–4 weeks"]:
            st.warning("**Timing matters:** CDC notes that Lyme serologic assays can be falsely negative during the first 4–6 weeks after infection because antibodies may not yet be detectable. An early negative result should therefore be interpreted with the timing, symptoms, and exposure history.")
        elif "Positive" in test_result:
            st.info("**A positive antibody result needs context:** antibodies can remain detectable for months to years and cannot be used by themselves to determine whether infection is currently active or whether treatment has cured an infection.")
        elif "Equivocal" in test_result or "unclear" in test_result.lower():
            st.info("**An equivocal/unclear result is not interpreted alone:** in the CDC two-step process, a positive or equivocal first-tier test is followed by the appropriate second-tier assay before the overall serologic result is determined.")
        else:
            st.write("The meaning of a Lyme test depends on the assay, the complete two-step result when applicable, timing, symptoms, and exposure history.")

        if "IgM" in test_result and "Positive" in test_result and test_timing == "More than 30 days":
            st.warning("CDC guidance says positive IgM results should be disregarded when illness has lasted more than 30 days because of the risk of false-positive or prolonged IgM reactivity.")

    if rash and tick_bite == "Yes":
        st.info("**Rash context:** CDC notes that likely erythema migrans is primarily a clinical finding; early serologic testing can be falsely negative during the first few weeks. PathwayAI does not diagnose a rash.")

    st.markdown("[CDC: Clinical Testing and Diagnosis for Lyme Disease](https://www.cdc.gov/lyme/hcp/diagnosis-testing/index.html) · [CDC: What to Do After a Tick Bite](https://www.cdc.gov/ticks/after-a-tick-bite/index.html)")
    st.markdown("**Useful questions for your healthcare professional**")
    st.write("• Is Lyme testing indicated based on my exposure, symptoms, and timing?")
    st.write("• Was my testing the recommended two-step serologic process, and what is the overall result?")
    st.write("• Was the test performed early enough that the antibody window period affects interpretation?")
    st.write("• If uncertainty remains, is additional evaluation appropriate, including consideration of other causes or tickborne infections?")
    st.caption("Evidence-grounded testing navigation based on CDC guidance. PathwayAI explains reported information; it does not diagnose Lyme disease, prescribe testing, or replace clinical judgment.")

    # Functional impact

    st.subheader("Functional Impact & Disability")

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Daily Activities", daily_function)

    with col2:
        st.metric("Days Missed", days_missed if days_missed_reported else "Not reported")

    st.write(f"**Work/school impact:** {work_impact}")

    if (
        daily_function in ["Major limitation", "Unable to perform usual activities"]
        or work_impact in ["Stopped working or school", "On disability"]
    ):
        st.info(
            "Significant functional impact reported. PathwayAI records this "
            "separately from clinical navigation priority."
        )

    # Patient journey and economic burden

    st.subheader("💰 My Burden Snapshot")

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Healthcare Professionals Seen", providers_seen if providers_seen_reported else "Not reported")

    with col2:
        st.metric("Days Missed", days_missed if days_missed_reported else "Not reported")

    st.write(f"**Time to diagnosis:** {diagnostic_delay}")
    st.write(f"**Out-of-pocket cost:** {oop_cost}")
    st.write(f"**Work/school impact:** {work_impact}")

    st.caption(
        "These measures document patient-reported healthcare utilization, "
        "functional impact, productivity loss, and direct out-of-pocket burden."
    )

    st.markdown("#### Transparent Running Burden")
    st.caption('**Sources:** 👤 Patient-entered · 🧮 Modeled · 📚 Published/public evidence')
    productivity_loss = float(days_missed or 0) * _num0(daily_productivity_value) if daily_productivity_value is not None else 0.0
    entered_costs = [v for v in [medical_cost, second_opinion_cost, repeat_testing_cost, transport_cost, self_care_cost] if v is not None]
    productivity_entered = days_missed is not None and daily_productivity_value is not None
    known_total = sum(float(v) for v in entered_costs) + productivity_loss
    burden_table = pd.DataFrame({
        "Burden component": ["Medical / healthcare", "Second opinion / specialist evaluation", "Repeat / duplicative testing or fragmented care", "Transportation / lodging", "Self-paid supportive care / supplies", "Productivity loss"],
        "Amount entered / modeled ($)": [medical_cost, second_opinion_cost, repeat_testing_cost, transport_cost, self_care_cost, productivity_loss],
        "Interpretation": ["Care received — not assumed avoidable", "Potentially beneficial care investment — not assumed avoidable", "Potentially addressable only when truly duplicative/fragmented", "Access burden — may or may not be addressable", "Patient-borne burden that may be absent from claims", "Economic burden — scenario dependent"],
        "Provenance": ["Patient-entered", "Patient-entered", "Patient-entered", "Patient-entered", "Patient-entered", "Modeled from patient-entered days × value/day"],
    })
    show_readable_table(burden_table, hide_index=True, width="stretch")
    if entered_costs or productivity_entered:
        st.metric("Known / modeled burden subtotal", f"${known_total:,.0f}")
        st.caption("This subtotal includes only the dollar components entered above. It is not a full cost-of-illness estimate and does not assign causality to Lyme disease.")
    else:
        st.metric("Known / modeled burden subtotal", "Not reported")
        st.caption("No dollar components were entered. Missing cost information is not treated as zero.")
    nd1,nd2,nd3 = st.columns(3)
    nd1.metric("Caregiver time", f"{caregiver_hours:,.0f} h" if caregiver_hours > 0 else "Not reported")
    nd2.metric("Navigation time", f"{navigation_hours:,.0f} h" if navigation_hours > 0 else "Not reported")
    nd3.metric("Income loss", income_loss_band)
    st.caption(f"Typical travel: {travel_distance} • Pre-diagnosis visits: {pre_dx_visits} • Caregiver work impact: {caregiver_missed_work}. These are kept visible even when no defensible dollar conversion is available.")

    st.markdown("#### Where Burden Accumulates")
    accumulation = []
    if _num0(medical_cost) > 0: accumulation.append(("Medical / healthcare", _num0(medical_cost)))
    if _num0(second_opinion_cost) > 0: accumulation.append(("Second opinion / specialist evaluation", _num0(second_opinion_cost)))
    if _num0(repeat_testing_cost) > 0: accumulation.append(("Repeat / duplicative testing or fragmented care", _num0(repeat_testing_cost)))
    if _num0(transport_cost) > 0: accumulation.append(("Transportation / lodging", _num0(transport_cost)))
    if _num0(self_care_cost) > 0: accumulation.append(("Self-paid supportive care / supplies", _num0(self_care_cost)))
    if productivity_loss > 0: accumulation.append(("Work / school productivity", productivity_loss))
    if accumulation:
        accumulation = sorted(accumulation, key=lambda x: x[1], reverse=True)
        for label, amount in accumulation:
            share = (amount / known_total * 100.0) if known_total > 0 else 0
            st.write(f"**{label}:** ${amount:,.0f} ({share:.0f}% of documented subtotal)")
    else:
        st.write("Not enough dollar information has been entered to show where financial burden accumulates.")

    if known_total > 0:
        st.success(f"**Documented/modelled burden so far:** ${known_total:,.0f}. The section below keeps future scenarios separate from what has already happened.")

    st.markdown("#### 📚 Published Cost Context — Not a Personal Forecast")
    st.caption('Published averages are reference points, not your future bill.')
    published_costs = pd.DataFrame({
        "Published measure": ["Mean Lyme-specific medical cost per episode", "Localized disease — mean episode cost", "Disseminated disease — mean episode cost", "Adjusted 6-month excess direct healthcare cost vs controls", "Lyme-attributable patient OOP cost"],
        "Estimate": ["$2,227", "$695", "$6,833", "$5,571", "$188–$399"],
        "Evidence": ["Yu et al., 70,531 U.S. patients", "Yu et al.", "Yu et al.", "Yu et al.", "Yu et al.; OOP subset"],
        "How PathwayAI uses it": ["Population benchmark", "Population benchmark", "Population benchmark", "Population benchmark", "Population benchmark — not your expected OOP"],
    })
    show_readable_table(published_costs, hide_index=True, width="stretch")
    st.write('Costs vary with insurance, illness, care, work and support needs.')
    st.caption("Recent cost study values are standardized to 2022 USD. CDC/TickNET separately captures direct medical, direct nonmedical, and productivity costs, which is why PathwayAI also asks about travel, work, caregiving, and navigation.")

    st.markdown("#### Could Better Support Reduce Some of This Burden?")
    st.write("PathwayAI separates **care that may be appropriate or beneficial** from burden that might be influenced by better access, coordination, or navigation.")
    if scenario_savings > 0:
        st.metric("User-entered scenario amount", f"${scenario_savings:,.0f}")
        st.write("This is the portion of costs or missed-day value that **you identified as potentially addressable**. It is not a promise that this amount would have been saved.")
        transparency_rows=[]
        if _num0(avoid_repeat_cost)>0: transparency_rows.append(["Fragmented/repeated-care cost you marked as potentially addressable",f"${_num0(avoid_repeat_cost):,.0f}","Included in scenario"])
        if _num0(avoid_transport_cost)>0: transparency_rows.append(["Travel/access cost you marked as potentially addressable",f"${_num0(avoid_transport_cost):,.0f}","Included in scenario"])
        if float(avoid_days)>0 and _num0(daily_productivity_value)>0: transparency_rows.append(["Missed-day value you marked as potentially addressable",f"${float(avoid_days)*_num0(daily_productivity_value):,.0f}","Included in scenario"])
        if second_opinion=="Yes": transparency_rows.append(["Second opinion","Not counted","May be beneficial care"])
        transparency_rows.append(["Appropriate testing / follow-up","Not counted","Not automatically treated as savings"])
        show_readable_table(pd.DataFrame(transparency_rows,columns=["What contributed","Amount","How PathwayAI treats it"]),hide_index=True,width="stretch")
    else:
        st.info("You have not identified any costs or missed-day value as potentially addressable. That is okay. PathwayAI does not assume that more care means waste.")
    st.caption("Modeled scenario only—not a prediction or proven savings estimate. Useful second opinions, clinically indicated testing, and appropriate follow-up are not automatically counted as savings.")

    st.markdown("#### Burden you reported")
    burden_drivers = []
    if providers_seen is not None and providers_seen > 0: burden_drivers.append("multiple healthcare encounters")
    if test_status == "Yes — more than once": burden_drivers.append("repeat testing / reassessment")
    if second_opinion == "Yes": burden_drivers.append("second opinion / specialist access (may be beneficial care)")
    if days_missed is not None and days_missed > 0: burden_drivers.append("work/school loss")
    if daily_function in ["Major limitation", "Unable to perform usual activities"]: burden_drivers.append("functional limitation")
    if insurance_context not in ["Not reported", "Unsure / prefer not to answer", "No access or coverage barrier reported"]: burden_drivers.append("access / coverage barriers")
    if _num0(transport_cost) > 0: burden_drivers.append("transportation / lodging")
    st.write(", ".join(burden_drivers).capitalize() if burden_drivers else "No burden details entered in these fields.")
    st.caption("A summary of your entries, without a severity score or prediction.")

    st.markdown("#### My PathwayAI Burden & Preparedness Card")
    st.write(f"**Where is burden accumulating?** " + (", ".join(burden_drivers) if burden_drivers else "No major burden driver is identifiable from the information entered so far."))
    if known_total > 0:
        st.metric("Burden documented so far", f"${known_total:,.0f}")
        st.write("**Prepare by tracking:** upcoming healthcare/testing expenses, transportation, missed work or reduced hours, insurance payments/denials, and changes in daily function.")
    else:
        st.write("**Cost estimate:** Not enough dollar information has been entered for a defensible personalized estimate yet.")
        st.write("**Prepare by tracking:** medical/testing expenses, transportation, out-of-pocket payments, missed work/reduced hours, and functional changes.")
    if daily_function in ["Major limitation", "Unable to perform usual activities"] or work_impact in ["Stopped working or school", "On disability"]:
        st.warning("Because substantial functional impact was reported, consider documenting when limitations began, how they affect daily activities/work, and what assistance you need. This record can support conversations with clinicians, employers, insurers, and benefit programs.")
    st.caption('Review this summary before sharing. It does not predict expenses or determine benefit eligibility.')

    # Support links appear beside the single current-care location, before optional contribution.

    # Journey summary

    st.subheader("The Invisible Patient Journey")
    journey_df = pd.DataFrame({
        "Stage": ["Exposure", "Symptoms", "Testing / interpretation", "Healthcare journey", "Diagnostic journey", "Function", "Economic burden"],
        "Your journey": [
            f"{tick_bite} tick bite; {attachment} attachment",
            symptom_text,
            f"{test_status}; {test_type}; {test_result}; timing: {test_timing}",
            f"{providers_seen} healthcare professionals seen" if providers_seen_reported else "Not reported",
            diagnostic_delay,
            "; ".join([x for x in [daily_function, work_impact] if x != "Not reported"]) or "Not reported",
            "; ".join(([f"{oop_cost} out of pocket"] if oop_cost != "Not reported" else []) + ([f"{days_missed} days missed"] if days_missed_reported else [])) or "Not reported",
        ],
        "Why capture it": [
            "Connects place and timing to the story",
            "Makes onset and progression visible",
            "Preserves timing and interpretation context",
            "Shows fragmentation / utilization",
            "Makes delay visible",
            "Captures consequences beyond symptoms",
            "Makes hidden patient and productivity burden visible",
        ],
    })
    show_readable_table(journey_df, hide_index=True, width="stretch")
    st.caption('Your reported timeline; it does not establish Lyme causation.')

    # Next steps

    st.subheader("Evidence-Grounded Next Steps")

    if tick_bite == "Yes":
        st.write(
            "• Record the date and geographic location of the possible tick exposure."
        )

    if attachment == "Unsure":
        st.write(
            "• If possible, document when the tick was first noticed and when it was removed."
        )

    if fever:
        st.write(
            "• Record when the fever began and whether other symptoms develop."
        )

    if symptoms:
        st.write(
            "• Bring your exposure and symptom timeline to an appropriate healthcare professional."
        )

    if daily_function not in ["Not reported", "No limitation"] or work_impact not in ["Not reported", "No impact", "Not applicable"]:
        st.write(
            "• Document changes in daily function and work/school participation over time."
        )

    st.write(
        "• Continue monitoring for new or changing symptoms after possible tick exposure."
    )

    # Provenance

    st.subheader("Data Sources & Provenance")

    provenance = pd.DataFrame(
        {
            "Information": [
                "Travel location",
                "ZIP code",
                "Travel month",
                "Age / immune status",
                "Tick exposure",
                "Symptoms",
                "Testing history / timing / reported result",
                "Second clinical opinion",
                "Functional impact",
                "Work/school impact",
                "Diagnostic journey",
                "Healthcare utilization",
                "Out-of-pocket cost",
                "Navigation output",
            ],
            "Source": [
                "User-reported + public geographic data",
                "User-reported; used for pilot routing/care navigation",
                "User-reported + seasonal context",
                "User-reported",
                "User-reported",
                "User-reported",
                "User-reported",
                "User-reported",
                "User-reported",
                "User-reported",
                "User-reported",
                "User-reported",
                "User-reported",
                "Prototype evidence-grounded rules",
            ],
            "Role in PathwayAI": [
                "Exposure context",
                "Geographic navigation",
                "Seasonal context",
                "Personal context",
                "Exposure history",
                "Clinical context",
                "Testing / interpretation context",
                "Diagnostic-uncertainty pathway",
                "Functional burden",
                "Productivity impact",
                "Diagnostic delay",
                "Healthcare utilization",
                "Direct economic burden",
                "Explainable navigation",
            ],
        }
    )

    show_readable_table(
        provenance,
        hide_index=True,
        width="stretch"
    )

    st.info(
        'Patient reports, public data, published findings and modeled scenarios are labeled separately.'
    )

    st.error(
        "PathwayAI does not diagnose Lyme disease or prescribe treatment. "
        "Seek professional medical evaluation for concerning symptoms or "
        "illness after possible tick exposure."
    )