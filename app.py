# v51 — private email feedback without SMTP setup
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
        "A quick visual check can help you decide whether what you found is consistent with a tick. "
        "Image identification is educational only and cannot tell whether a tick carries a pathogen."
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
            "CDC notes that blacklegged ticks occur in several life stages and can be extremely small. "
            "Nymphs and adult females are among the stages more often reported on people."
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
        "If you are unsure, save a clear photo (top and underside if possible). "
        "PathwayAI can later support photo-assisted identification, but a photo alone should not be used to determine infection."
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
    table = frame.to_html(index=False, escape=True, border=0, classes="pathway-readable-table")
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


@st.cache_data(ttl=86400)
def load_nys_nymph_surveillance():
    """Load official NYSDOH county-level nymph surveillance data."""
    url = "https://health.data.ny.gov/resource/kibp-u2ip.json?$limit=50000"
    with urllib.request.urlopen(url, timeout=15) as response:
        records = json.loads(response.read().decode("utf-8"))
    df = pd.DataFrame(records)
    if df.empty:
        return df

    # Socrata field names can change presentation slightly; normalize them.
    df.columns = [
        str(c).strip().lower().replace(" ", "_").replace(".", "").replace("%", "pct")
        for c in df.columns
    ]
    return df


@st.cache_data(ttl=86400)
def load_us_county_geojson():
    """County boundaries used only for drawing the map; health values come from NYSDOH."""
    url = "https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json"
    with urllib.request.urlopen(url, timeout=15) as response:
        return json.loads(response.read().decode("utf-8"))


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
    density_col = find_column(tick, ["tick_population_density"])
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


def show_nys_tick_density_map():
    """Render NY surveillance on a guaranteed white SVG background (no map tiles)."""
    try:
        geojson, latest_year = build_nys_tick_density_geojson()
        if not geojson:
            st.warning("The statewide surveillance map is temporarily unavailable.")
            return
        width, height = 760, 420
        bounds = (-79.9, 40.35, -71.7, 45.15)
        parts = [f'<svg viewBox="0 0 {width} {height}" width="100%" height="100%" xmlns="http://www.w3.org/2000/svg">',
                 '<rect width="100%" height="100%" fill="#ffffff"/>']
        for feature in geojson.get("features", []):
            props = feature.get("properties", {})
            rgb = props.get("fill_color", [235,235,235,255])[:3]
            fill = '#%02x%02x%02x' % tuple(int(v) for v in rgb)
            title = html.escape((f"{props.get('county_label','')} | Nymph density: {props.get('density_label','N/A')} | "
                     f"B. burgdorferi positive: {props.get('bb_label','N/A')}"), quote=True)
            for d in _geom_paths(feature.get("geometry"), bounds, width, height):
                parts.append(f'<path d="{d}" fill="{fill}" stroke="#6b7280" stroke-width="0.8"><title>{title}</title></path>')
        parts.append('</svg>')
        components.html(
            '<div style="background:white;border:1px solid #d1d5db;border-radius:10px;padding:8px;height:440px;">'
            + ''.join(parts) + '</div>', height=460, scrolling=False
        )
        st.caption(
            f"Observed NYSDOH nymph tick population density, latest available surveillance year: {latest_year}. "
            "Hover over a county for details. Gray indicates no observation for that year. "
            "Environmental surveillance does not estimate an individual's probability of infection."
        )
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
        "description": "Location-based directory of ILADS members. Inclusion is not an endorsement or guarantee of clinical quality.",
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
            lyme["_cases"] = pd.to_numeric(lyme[case_col], errors="coerce").fillna(0)
        else:
            # Some public-use files contain one record/point per reported case.
            lyme["_cases"] = 1
    else:
        # Wide format: a Lyme-specific numeric column.
        lyme_col = next((c for c in df.columns if "lyme" in c), None)
        if not lyme_col:
            return {}
        lyme = df.copy()
        lyme["_cases"] = pd.to_numeric(lyme[lyme_col], errors="coerce").fillna(0)

    def clean_fips(v):
        raw = re.sub(r"\.0$", "", str(v).strip())
        digits = re.sub(r"\D", "", raw)
        return digits.zfill(5) if digits else ""
    lyme["_fips"] = lyme[fips_col].map(clean_fips)
    lyme = lyme[lyme["_fips"].str.len() == 5]
    if lyme.empty:
        return {}
    return lyme.groupby("_fips")["_cases"].sum().round().astype(int).to_dict()


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

        parts = [f'<svg viewBox="0 0 {width} {height}" width="100%" height="100%" xmlns="http://www.w3.org/2000/svg">',
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
            st.info("**Read the two layers separately:** county shading shows reported human Lyme burden; blue/yellow markers show blacklegged-tick surveillance. Geography can vary substantially within a state, so PathwayAI keeps the county view visible rather than assigning one statewide risk label.")

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
                st.info("County-level human Lyme data are not loaded yet. PathwayAI will not substitute state shading or invent a county value.")

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
    st.write("PathwayAI uses what you shared to organize your journey, connect it with relevant published evidence, and help you and a caregiver prepare for the next conversation with a healthcare professional. It does **not** predict your individual outcome.")

    # A compact patient-specific journey line.
    stages = ["Exposure / concern"]
    if symptoms: stages.append("Symptoms")
    if tested: stages.append("Testing")
    if providers: stages.append("Care journey")
    if function or work_impact: stages.append("Function / work impact")
    stages.append("You are here")
    st.markdown("**Your journey:**  " + " → ".join(stages))

    st.markdown("### What larger studies can add to the picture")
    e1, e2, e3 = st.columns(3)
    with e1:
        st.metric("52,795", "treated Lyme patients")
        st.caption("U.S. commercial claims study; compared with 263,975 matched controls. The Lyme group had higher 12-month healthcare costs and outpatient use. This is population evidence, not an individual forecast.")
    with e2:
        st.metric("2,424", "patient survey respondents")
        st.caption("Published U.S. access-to-care study. 51% reported seeing 7+ physicians before diagnosis. This selected patient population should not be treated as prevalence for all Lyme disease.")
    with e3:
        st.metric("253", "longitudinal participants")
        st.caption("Lyme Disease Biobank initial + ~3-month follow-up cohort: 78% reported no Lyme symptoms at follow-up and 22% reported ongoing symptoms. This does not predict your outcome.")

    # Surface only context that is relevant to what this person reported.
    if providers is not None and providers >= 4:
        st.info(f"**Your care journey:** You reported about {providers} healthcare professionals. A published 2,424-person access-to-care study found that 51% of its respondents reported seeing 7 or more physicians before diagnosis. Your experience overlaps with a burden pattern reported in that selected patient population; it does not mean your future journey will be the same.")
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
    st.write("PathwayAI uses your reported timing and symptoms to surface relevant evidence—not to predict your individual outcome. Patient experiences vary, and new or worsening symptoms should be evaluated in clinical context.")
    st.caption("Evidence context is shown only when relevant to what you reported. It is not a prognosis.")

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
        "PathwayAI does not rank or endorse clinicians. Use the links below to "
        "compare nearby options, current Google information/reviews, credentials, "
        "insurance participation, availability, and services."
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
        "Google ratings and reviews are third-party consumer information and can change. "
        "They do not establish clinical quality. PathwayAI does not copy, score, or rank "
        "providers based on reviews."
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
    ("Benefits.gov", "https://www.benefits.gov/", "Government benefit finder covering health, income, food, housing and other programs."),
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
    st.caption("Start with the few actions most connected to your story. Your city/county is enough for navigation; a ZIP code only makes nearby results more precise.")

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
        st.markdown("**Patient organizations / provider directories**")
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
        st.write("Organizer template: MVP Demo Milestone, reviewed October 7, 2026.")
        st.write("Walkthrough: complete user journey, core features, communities involved, and what testing taught us.")
        st.write("Impact & Evidence: intended users, federal datasets actually incorporated, and documented user validation.")
        st.write("Deployment Strategy: launch plan, sustainability, post-sprint roadmap, and ways to support the tool.")
        st.caption("Technical checks are not user validation. County adoption, clinical benefit and savings remain unestablished.")

st.title("PathwayAI")
st.markdown("### Know about ticks. Find your next step.")
st.write("A tick bite can leave you wondering what to do. Symptoms can bring more uncertainty. PathwayAI helps you find guidance for your situation—from preparing for outdoor activities to navigating care and support.")
with st.expander("Why does this matter?"):
    st.write("CDC estimates approximately 476,000 people were diagnosed and treated for Lyme disease annually in the United States, based on insurance-claims research from 2010–2018. Most people recover with appropriate treatment, especially when treated early.¹")
    st.caption("This is an estimate of diagnoses and treatment, not a count of confirmed infections or a new 2026 case count.")
st.subheader("What brings you here today?")
def select_public_pathway(target, intent):
    st.session_state["pathway_view"] = target
    st.session_state["public_pathway_intent"] = intent
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
for start in range(0, len(paths), 2):
    cols = st.columns(2)
    for col, (label, detail, target, intent) in zip(cols, paths[start:start+2]):
        with col:
            st.button(label, key="route_"+intent, on_click=select_public_pathway, args=(target, intent), use_container_width=True)
            st.caption(detail)
st.caption("Existing health conditions: the prevention page offers optional health-context choices. Share only what you are comfortable entering.")
st.caption("Education and navigation only. PathwayAI does not diagnose illness or calculate your personal chance of infection.")
st.caption("¹ Sources: [CDC diagnoses study](https://wwwnc.cdc.gov/eid/article/27/2/20-2731_article) · [CDC prevention](https://www.cdc.gov/ticks/prevention/)")

if "pathway_view" not in st.session_state:
    st.session_state["pathway_view"] = "📊 Community Burden & Action"
available_views = ["📚 Learn", "🛡️ Prevention", "🧭 Timely Care & Support", "📊 Community Burden & Action", "💬 Contribute"]
if st.session_state.get("admin_authenticated"):
    available_views.append("🧠 Research & Strategy Agent")
if st.session_state.get("pathway_view") not in available_views:
    st.session_state["pathway_view"] = "📊 Community Burden & Action"
view = st.radio(
    "Choose view",
    available_views,
    horizontal=True,
    key="pathway_view"
)


def show_brief_feedback():
    st.subheader("Help us improve PathwayAI")
    st.write("What helped, what was confusing, or what would you like us to add? A sentence or two is enough. You can also tell us how you would like to help.")
    st.caption("Please leave out personal medical details. Your message will go privately to the project inbox, not appear on this website.")
    address = "pathwayai.feedback@gmail.com"
    st.markdown("[**Email feedback**](mailto:" + address + "?" + urlencode({"subject": "PathwayAI Feedback"}, quote_via=quote_plus) + ")")
    st.write("**" + address + "**")
    st.caption("The button opens your email app. Write your note there and press Send. If it does not open, copy the address into Gmail or another email service. PathwayAI does not send or store the message for you.")
    st.write("Thank you so much for your contribution!")

if view == "📚 Learn":
    st.header("Learn about Lyme and tick-borne illness")
    st.write("Start here if you are curious, helping someone, or planning a visit. You do not need to enter a ZIP code, describe symptoms, or use AI.")
    st.markdown("**Explore the basics**\n\n[CDC: About Lyme disease](https://www.cdc.gov/lyme/about/index.html) · [CDC: Tick-bite prevention](https://www.cdc.gov/ticks/prevention/index.html) · [CDC: After a tick bite](https://www.cdc.gov/ticks/after-a-tick-bite/index.html)")
    st.markdown("**Choose your next step**\n\n- Planning a visit? Open Prevention for destination surveillance and an outdoor plan.\n- Preparing for care? Open Timely Care & Support to organize your story.\n- Exploring local needs? Open Community Burden & Action for the Dutchess pilot.\n- Have an idea? Open Contribute and leave a short note.")
    st.caption("County surveillance describes population context, not your individual chance of infection. Reported case counts and tick-presence categories are different measures.")
    st.stop()

if view == "💬 Contribute":
    show_brief_feedback()
    st.caption("To optionally contribute structured Patient Voice information, use Timely Care & Support, review the fields and consent there. Website feedback is kept separate from Patient Voice.")
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
        st.caption("ZIP selects the destination. The combined surveillance map below compares tick surveillance and Lyme disease surveillance without converting either into an individual risk score.")

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
        st.info("This plan summarizes available destination information and prevention steps. It does not establish that you were bitten or estimate your personal chance of infection.")
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
                "PathwayAI combines regional tick-risk context with local surveillance "
                "data to help travelers understand environmental exposure before a trip."
            )

            # 2025 NYSDOH regional context reported for the Hudson Valley.
            hudson_valley_score = 2.1
            score_pct = min(max(hudson_valley_score / 5.0, 0.0), 1.0) * 100

            st.markdown(
                f"""
                <div style="padding:18px;border:1px solid rgba(128,128,128,.35);
                            border-radius:12px;margin:8px 0 10px 0;">
                  <div style="font-size:0.95rem;opacity:.8;">NYSDOH regional encounter-risk context</div>
                  <div style="font-size:2rem;font-weight:700;margin:2px 0;">
                    Hudson Valley: {hudson_valley_score:.1f} / 5
                  </div>
                  <div style="height:16px;background:rgba(128,128,128,.25);
                              border-radius:10px;overflow:hidden;margin:10px 0;">
                    <div style="width:{score_pct:.0f}%;height:100%;
                                background:linear-gradient(90deg,#f2c94c,#f2994a,#eb5757);"></div>
                  </div>
                  <div style="font-size:0.9rem;opacity:.8;">
                    Regional environmental context — not an individual's probability of infection.
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.caption(
                "Fixed sourced snapshot: NYSDOH Tick Risk Score by Region (2025); not a live API result. NYSDOH notes "
                "that its regional score uses tick population density and pathogen prevalence "
                "measured at multiple locations and averaged by region, so it may not reflect "
                "every location within the region."
            )

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
                "This combined view keeps two different surveillance signals separate: blacklegged-tick surveillance and reported human Lyme disease surveillance. "
                "It does not predict whether you personally will be bitten by a tick or develop Lyme disease."
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
                "This combined view keeps two different surveillance signals separate: blacklegged-tick surveillance and reported human Lyme disease surveillance. "
                "It does not predict whether you personally will be bitten by a tick or develop Lyme disease."
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
    st.caption("Dutchess is the demonstration. The County Pack architecture is designed to be populated with corresponding state and local data for additional counties.")
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

    st.markdown("## County at a glance")
    cards=[]
    if exposure_density is not None: cards.append(("Tick density", f"{exposure_density:.1f} / 1,000 m²"))
    if exposure_pathogen is not None: cards.append(("B. burgdorferi positive", exposure_pathogen))
    if lyme_cases is not None: cards.append(("Reported Lyme cases", f"{int(lyme_cases):,}"))
    if crude_rate is not None: cards.append(("Approx. annualized crude rate", f"{crude_rate:.1f} / 100k"))
    if ahrf and pd.notna(ahrf.get("pcp")) and pop: cards.append(("Primary-care capacity", f"{float(ahrf['pcp'])/pop*10000:.1f} / 10k"))
    if ahrf and pd.notna(ahrf.get("beds")): cards.append(("Hospital beds", f"{int(float(ahrf['beds'])):,}"))
    if cards:
        cols=st.columns(min(4,len(cards)))
        for i,(label,value) in enumerate(cards): cols[i % len(cols)].metric(label,value)
    source_bits=[]
    if exposure_density is not None: source_bits.append(f"Tick surveillance: NYSDOH, {exposure_year or 'year unavailable'}")
    if lyme_cases is not None: source_bits.append("Reported Lyme cases: CDC, 2019–2022 total. Rate: approximate annual average over four years.")
    if ahrf: source_bits.append("HRSA AHRF 2024–2025")
    if source_bits:
        for source_line in source_bits: st.caption(source_line)

    st.markdown("## 1. Who may need more support?")
    st.write("Start with measurable county context that can shape how illness affects residents and how easily people can stay connected to care, work and daily life.")
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Population", f"{census_context['population_2025_estimate']:,}")
    c2.metric("Living in poverty", f"{census_context['poverty_percent_2020_2024']:.1f}%")
    c3.metric("Uninsured, under 65", f"{census_context['uninsured_under65_percent_2020_2024']:.1f}%")
    c4.metric("Labor force, age 16+", f"{census_context['civilian_labor_force_percent_2020_2024']:.1f}%")

    context_rows = []
    if ahrf and pop and pd.notna(ahrf.get("pcp")):
        context_rows.append(["Primary-care capacity", f"{float(ahrf['pcp'])/pop*10000:.1f} physicians / 10,000 residents", "HRSA AHRF"])
    if ahrf and pd.notna(ahrf.get("hosp")):
        context_rows.append(["Hospitals", f"{int(float(ahrf['hosp'])):,}", "HRSA AHRF"])
    if ahrf and pd.notna(ahrf.get("beds")):
        context_rows.append(["Hospital beds", f"{int(float(ahrf['beds'])):,}", "HRSA AHRF"])
    if places is not None and not places.empty:
        lookup = {str(r.MeasureId): r for _, r in places.iterrows()}
        for mid,label in [("DISABILITY","Any disability"),("COGNITION","Cognitive disability"),("MOBILITY","Mobility disability"),("LACKTRPT","Transportation barrier")]:
            if mid in lookup and pd.notna(lookup[mid].Data_Value):
                context_rows.append([label, f"{float(lookup[mid].Data_Value):.1f}%", "CDC PLACES"])
    if context_rows:
        show_readable_table(pd.DataFrame(context_rows, columns=["County signal", "Dutchess County", "Source"]), hide_index=True, width="stretch")
    st.caption("Census QuickFacts: population estimate July 1, 2025; poverty, insurance and labor-force measures 2020–2024. HRSA and CDC PLACES measures are shown only when loaded. These describe community context; they are not attributed to Lyme disease.")

    st.markdown("## 2. Where can earlier care and support help?")
    st.write("The invisible journey extends beyond a reported case: symptoms, repeated visits, delayed answers, disrupted work and the effort of finding support.")
    journey_plan = pd.DataFrame([
        ["Exposure / symptoms", "Difficulty recognizing when to seek assessment", "Prevention information and a clear route to clinical assessment", "Time from symptoms to first assessment"],
        ["Assessment / repeated visits", "Repeated history, uncertain next steps and referral barriers", "Patient-reviewed journey summary; clinical review or second opinion when appropriate", "Appointment wait and completed referrals"],
        ["Treatment / follow-up", "Persistent symptoms and functional limitations may go unrecorded", "Clinical partners agree on follow-up; patients report function", "Follow-up completion and function over time"],
        ["Work / household support", "Lost work, travel costs, caregiver time and benefit barriers", "Navigation to transport, workplace and financial/disability resources", "Support accessed and patient-reported unmet needs"],
    ], columns=["Journey stage", "Burden to investigate", "Proposed response", "Measure in the pilot"])
    show_readable_table(journey_plan, hide_index=True, width="stretch")
    st.caption("Proposed service pathway • not measured Dutchess journey results. Early diagnosis and appropriate antibiotic treatment can help prevent more severe Lyme disease; this app does not estimate disability prevented or prescribe treatment.")

    st.markdown("## 3. Which burdens can the county address?")
    burden_priorities = pd.DataFrame([
        ["Repeated visits / delayed answers", "Patient Voice: long diagnostic journeys and repeated healthcare professionals", "Journey summary and verified referral navigation", "Completed connection to care"],
        ["Medical and out-of-pocket spending", "Published cost evidence + Patient Voice spending signals", "Insurance and financial-support navigation", "Spending over the same stated period"],
        ["Travel / caregiver effort", "County access context + patient-journey framework", "Assess transport and caregiver-support needs", "Travel time, cost and caregiver hours"],
        ["Lost work / disability-related needs", "Patient Voice work-loss signals + county disability context", "Benefits and workplace-support navigation", "Days affected, function and unmet support needs"],
    ], columns=["Burden", "Evidence signal", "Action to consider", "What to track"])
    show_readable_table(burden_priorities, hide_index=True, width="stretch")
    st.caption("These are candidate priorities, not a local burden ranking. Published costs, patient reports and county context stay separate; no total or savings is inferred.")

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

    st.markdown("## Suggested actions — a 90-day county pilot")
    actions = pd.DataFrame([
        ["1. Target prevention outreach", "Page 1 exposure context", "County outreach / parks partners", "Choose outreach locations using loaded surveillance; record missing locations", "Reach, materials delivered and knowledge feedback"],
        ["2. Offer journey navigation", "Survey: delay and repeated professionals", "Public health / primary-care partners", "Offer Page 2 summary, a verified referral route and a second clinical opinion when appropriate", "Summary completion, referral connection and time to appointment"],
        ["3. Address household barriers", "Survey: spending and work loss", "Social services / navigation partners", "Screen voluntarily for transport, insurance and financial support needs", "Support referrals offered and successfully accessed"],
        ["4. Explore clinical follow-up", "Biobank: persistent symptoms and follow-up gap", "Clinical partners", "Agree on a symptom/function check-in workflow; clinicians determine care", "Follow-up completion and patient-reported function"],
        ["5. Build a local burden baseline", "Page 2 consented county fields", "County evaluation team", "Collect delay, encounters, OOP period, days lost and caregiver time; repeat measures consistently", "Completeness and paired change; no assumed savings"],
    ], columns=["Proposed action","Why consider it","Suggested owner","First step","What to measure"])
    actions["Evidence status"] = [
        "Public exposure context; local intervention effect untested",
        "Patient survey themes; local service effect untested",
        "Patient survey themes; local support needs unmeasured",
        "Published Biobank follow-up evidence; local effect untested",
        "Proposed measurement protocol; no intervention effect claimed",
    ]
    show_readable_table(actions,hide_index=True,width="stretch")
    st.caption("Planning suggestions, not adopted county programs or demonstrated intervention effects. Validate local feasibility with county and clinical partners.")
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

    with st.expander("Patient survey, invisible journey & Biobank methods", expanded=False):
        st.markdown("## Patient Voice — what respondents tell us")
        st.write("Patient reports point to four burdens routine case counts miss: long diagnostic journeys, repeated encounters, substantial personal spending, and disrupted work or school.")
        survey_rows = [
            ["Selected more than 5 years to diagnosis",20,33,"3 additional free-text answers describe >5 years; not included in this exact-category count"],
            ["Selected more than 10 healthcare professionals",16,33,"1 unsure response"],
            ["Selected $10,000 or more before diagnosis",14,33,"5 unsure and 1 prefer not to answer"],
            ["Selected more than 100 work/school days lost",18,33,"3 unsure and 3 not applicable"],
            ["Reported disability benefits or unable to work",20,33,"1 unsure, 2 prefer not to answer, 1 not applicable"],
        ]
        voice = pd.DataFrame(survey_rows, columns=["Reported burden","Respondents","Eligible respondents","Interpretation / missingness"])
        voice["Share of eligible respondents"] = voice["Respondents"].map(lambda n: f"{n/33:.0%}")
        burden_chart = pd.DataFrame({
            "Burden reported": [
                "20/33 (61%)  •  >5 years to diagnosis",
                "16/33 (48%)  •  >10 professionals",
                "14/33 (42%)  •  ≥$10,000 out of pocket",
                "18/33 (55%)  •  >100 days lost",
            ],
            "Share of survey respondents (%)": [round(20/33*100,1),round(16/33*100,1),round(14/33*100,1),round(18/33*100,1)],
        })
        st.bar_chart(burden_chart,x="Burden reported",y="Share of survey respondents (%)",horizontal=True,color="#28785c")
        st.caption("Each bar shows n/N (%) • Patient-reported pilot findings • not county prevalence or predicted savings • methods below")
        with st.expander("Sources & methods",expanded=False):
            st.caption("35 submitted responses; 33 reported a healthcare-professional Lyme diagnosis. All chart denominators are 33, including unknown/not-applicable answers. Retrieved October 6, 2026. No county assignment or population weighting.")
            show_readable_table(voice,hide_index=True,width="stretch")
        st.write("**Themes behind the numbers:** difficulty obtaining an explanation; repeated encounters; financial strain; disrupted work and daily life. These are summarized themes, not verbatim patient quotations.")
        st.caption("County contributions from Page 2 remain a separate local layer; national survey findings are not assigned to Dutchess.")

        # Live pilot layer: consented structured submissions refresh on the next Streamlit rerun.
        # Keep this separate from the original national survey so provenance remains auditable.
        if len(pv) >= 5:
            st.markdown("### Live county Patient Voice")
            st.caption(f"{len(pv)} consented structured pilot contributions currently loaded for Dutchess County. This layer updates as reviewed records are contributed; it is not a population estimate.")
            live_rows = []
            for label, col in [
                ("Healthcare professionals reported", "providers_seen"),
                ("Workdays affected", "workdays"),
                ("Out-of-pocket burden", "oop_band"),
                ("Functional impact", "function"),
            ]:
                if col not in pv.columns:
                    continue
                vals = pv[col].dropna()
                vals = vals[vals.astype(str).str.strip().ne("") & vals.astype(str).str.lower().ne("not reported")]
                n = int(len(vals))
                if n < 5:
                    continue
                if col in ("providers_seen", "workdays"):
                    nums = usable_burden_numbers(vals)
                    if len(nums) >= 5:
                        live_rows.append([label, f"Median {nums.median():g}", f"n={len(nums)}"])
                else:
                    mode = vals.astype(str).mode()
                    if not mode.empty:
                        live_rows.append([label, mode.iloc[0], f"n={n}"])
            if live_rows:
                show_readable_table(pd.DataFrame(live_rows, columns=["Measure", "Current signal", "Usable responses"]), hide_index=True, width="stretch")
                st.caption("Live pilot submissions are displayed only when at least 5 usable responses are available for a field. Missing responses remain missing, not zero.")
        if len(pv) == 0:
            st.caption("To build the county layer: open Page 2, review the fields, choose Dutchess, consent, and press the contribution button. Local-file storage is a prototype; hosted use needs persistent storage.")
        elif len(pv) < 5:
            st.caption("County field summaries are withheld while fewer than 5 records are loaded; national pilot evidence remains separate. Five is a display threshold, not a guarantee against re-identification.")
    
        with st.expander("How Biobank and survey evidence add value"):
            st.write("**Survey → burden and barriers:** diagnostic delay, healthcare encounters, pre-diagnosis spending, lost work/school and disability. These identify outcomes a county pilot can measure.")
            st.write("**Biobank publication → clinical follow-up:** in a study of 253 participants with paired samples, 22% reported ongoing symptoms at the second draw; only 35% of those reporting ongoing symptoms had seen a provider about them. This supports examining follow-up gaps, not assigning a 22% risk to this county.")
            st.write("**Combined use:** clinical evidence suggests a follow-up question; the survey identifies financial and functional outcomes to collect alongside it. They are complementary evidence layers, not linked individuals or an AI training dataset.")
            st.caption("Horn et al., 2025 • early-Lyme cohort, Long Island NY / central Wisconsin • DOI: 10.3389/fmed.2025.1577936. This view uses the published findings; individual-level Biobank data have not been loaded into this version.")
            st.markdown("[Read the Biobank study](https://doi.org/10.3389/fmed.2025.1577936)")
    with st.expander("Optional disability support & treatment-spending illustration", expanded=False):
        st.markdown("## Disability, household support & additional treatment costs")
        benefit_col, cost_col = st.columns(2)
        with benefit_col:
            st.markdown("**Unable to work is not the same as receiving benefits.**")
            st.write("The survey includes people receiving disability benefits and people unable to work without those benefits. County navigators can help residents understand application routes, documentation and local support.")
            st.markdown("[SSA disability information](https://www.ssa.gov/disability) · [New York disability benefits](https://www.wcb.ny.gov/content/main/DisabilityBenefits/what-are-disability-benefits.jsp) · [211 support](https://www.211.org/)")
            st.caption("Eligibility and payments depend on the program and individual circumstances. PathwayAI does not determine entitlement. Benefit payments are household income support and should not be added to medical spending as a societal resource cost.")
        with cost_col:
            st.markdown("**Additional treatment burden — including IVIG when prescribed**")
            st.write("Record drug, infusion/facility, travel, caregiving and time costs separately. IVIG use does not establish a Lyme diagnosis or imply that it is appropriate treatment for Lyme disease. Clinical decisions belong to the treating team.")
            st.caption("No representative IVIG price or county IVIG total is loaded. Use an actual bill, insurer statement or documented estimate; do not apply an individual case cost to every patient.")
        with st.expander("Illustrate additional household spending — optional inputs"):
            st.caption("Illustrative monthly patient-spending scenario, not survey evidence or a treatment recommendation. Enter patient-paid amounts only, after reimbursement; leave unknown fields blank.")
            sc1,sc2,sc3 = st.columns(3)
            drug_oop = sc1.number_input("IVIG / other prescribed drug: patient-paid per month ($)",min_value=0.0,value=None,key="policy_drug_oop")
            infusion_oop = sc2.number_input("Infusion/facility: patient-paid per month ($)",min_value=0.0,value=None,key="policy_infusion_oop")
            transport_oop = sc3.number_input("Travel / paid caregiving per month ($)",min_value=0.0,value=None,key="policy_transport_oop")
            values=[drug_oop,infusion_oop,transport_oop]
            if any(v is not None for v in values):
                subtotal=sum(v for v in values if v is not None)
                st.metric("Entered monthly household spending subtotal",f"${subtotal:,.0f}")
                st.caption(f"{sum(v is None for v in values)} category/categories not entered. Subtotal may be incomplete; do not count infusion fees again if already included in the drug bill. Billed charges and insurer payments are excluded.")
                chart=pd.DataFrame({"Category":["Drug","Infusion/facility","Travel/caregiving"],"Entered patient spending ($/month)":values}).dropna()
                st.bar_chart(chart,x="Category",y="Entered patient spending ($/month)",color="#bc7040")
    with st.expander("Additional county context & complementary resources", expanded=False):
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
    with st.expander("ⓘ Sources, assumptions & transparency", expanded=False):
        st.markdown("[Hook societal costs](https://wwwnc.cdc.gov/eid/article/28/6/21-1335-t5) · [Yu medical costs](https://jamanetwork.com/journals/jamanetworkopen/fullarticle/2843880) · [CDC early treatment](https://www.cdc.gov/lyme/treatment/index.html)")
        st.markdown("[HRSA shortage definitions](https://bhw.hrsa.gov/workforce-shortage-areas/shortage-designation) · [County Health Rankings strategies](https://www.countyhealthrankings.org/strategies-and-solutions/what-works-for-health) · [CDC/ATSDR community profiles](https://www.atsdr.cdc.gov/place-health/php/communication-resources/index.html) · [MyLymeData](https://www.lymedisease.org/mylymedata/)")
        st.caption("Public website review: October 6, 2026. These references inform design; no external registry or shortage data are linked into this pilot.")
        st.write("**Exposure:** county/state surveillance only when a compatible source is loaded.")
        st.write("**Reported disease:** CDC 2019–2022 cumulative county cases are shown as a count. The displayed crude rate is annualized by dividing the four-year case count by 4 before applying the population denominator; it is an approximate annualized rate, not a year-specific incidence rate.")
        st.write("**Census:** U.S. Census Bureau QuickFacts provides population and socioeconomic context. These measures are contextual and are not attributed to Lyme disease. The Lyme rate continues to use the separately labeled 2023 HRSA population denominator.")
        st.write("**Patient Voice:** only consented, de-identified structured fields are aggregated; missing remains missing, never zero.")
        st.write("**Biobank:** the published clinical follow-up findings are shown above; individual-level data are not loaded. **Survey:** the national aggregate snapshot is separate from the local consented layer. Neither supplies county prevalence.")
        st.write("**Savings:** not estimated without observed baseline and follow-up measurements.")
        if ahrf: st.caption("HRSA fields: " + ahrf["fields"])

    st.caption("Pilot development note: PathwayAI is expanding local healthcare-access, patient-journey and follow-up measurement layers. The main county view displays available evidence; unsupported values are not substituted or treated as zero.")

    # Real county evidence brief: one row per actual field/source, with explicit missingness.
    brief_rows=[]
    def add_brief(metric,value,source,year=""):
        brief_rows.append({"county":policy_place,"fips":fips,"metric":metric,"value":value if value not in (None,"") else "not yet collected","source":source,"year":year})
    add_brief("surveillance_year", exposure_year, "State surveillance", exposure_year or "")
    add_brief("nymph_density_per_1000_m2", exposure_density, "State surveillance", exposure_year or "")
    add_brief("pathogen_positive_percent", exposure_pathogen, "State surveillance", exposure_year or "")
    add_brief("reported_lyme_cases_2019_2022", lyme_cases, "CDC county reported cases", "2019-2022")
    add_brief("average_annual_reported_cases_2019_2022", round(annual_avg_cases,2) if annual_avg_cases is not None else None, "CDC county reported cases; 4-year total divided by 4", "2019-2022")
    add_brief("approx_annualized_crude_rate_per_100000", round(crude_rate,2) if crude_rate is not None else None, "CDC cases + HRSA population; 4-year cases divided by 4", "2019-2022 cases / 2023 population")
    add_brief("census_population_estimate", census_context["population_2025_estimate"], "U.S. Census Bureau QuickFacts", "2025")
    add_brief("census_poverty_percent", census_context["poverty_percent_2020_2024"], "U.S. Census Bureau QuickFacts", "2020-2024")
    add_brief("census_uninsured_under65_percent", census_context["uninsured_under65_percent_2020_2024"], "U.S. Census Bureau QuickFacts", "2020-2024")
    add_brief("census_civilian_labor_force_percent_16plus", census_context["civilian_labor_force_percent_2020_2024"], "U.S. Census Bureau QuickFacts", "2020-2024")
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
    st.download_button("Download County Evidence Brief", brief.to_csv(index=False).encode("utf-8"), file_name=f"pathwayai_county_brief_{fips}.csv", mime="text/csv")
    st.download_button("Download County Action Plan", actions.to_csv(index=False).encode("utf-8"), file_name=f"pathwayai_action_plan_{fips}.csv", mime="text/csv")
    st.stop()

st.header("🧭 TIMELY CARE & SUPPORT")
show_section_hero("journey", "Understand Your Journey. Plan Your Next Step.", "Organize symptoms, testing, healthcare visits, costs, work/function, and support needs so important details are easier to carry into the next conversation.")
st.caption("🔒 **MVP data guardrail:** Patient Voice is currently a small national pilot used to develop the measurement framework. It is not local prevalence. Any aggregated result must show its denominator (n) and track missing responses separately from zero. The local CSV is an MVP collection path; production deployment requires persistent storage.")
st.write("Tell your story once. PathwayAI organizes the journey, helps you prepare for care, and—only with your permission—can turn de-identified parts of your experience into Patient Voice for policy insight.")
# QUICK START — STORY FIRST

# Location is intentionally optional and comes after the patient receives immediate value.
# This keeps the opening experience supportive rather than feeling like data collection.
current_location_start = st.session_state.get("current_location_start", "")

st.markdown("## 💬 TELL US YOUR STORY")
st.markdown("**Low on energy? Start here. One or two sentences are enough.**")
st.write("Tell us what happened in your own words. PathwayAI can organize what you share into a simple Journey Record for you to review — you do not need to complete the long form first.")
st.warning("🔒 **Protect your privacy:** Please do not enter your name, date of birth, street address, phone number, email, medical record number, or other identifying information.")

STORY_SAMPLE = 'I visited Maryland in June and had a tick bite. A few days later I developed a rash and became extremely tired and dizzy. I have felt this way for about two weeks. I had a Lyme blood test last week and was told it was negative. I have seen two doctors, missed five days of work, and spent about $600. I am now back home in Boston.'
st.markdown("#### Not sure what to write? Follow this example")
st.caption("The example stays visible while you type. You do not need to include every item.")
st.markdown(f"> {STORY_SAMPLE}")

if "quick_story_value" not in st.session_state:
    st.session_state.quick_story_value = ""

if st.button("Try this example", help="Copies the example into the story box so you can edit only the details that apply to you."):
    st.session_state.quick_story_value = STORY_SAMPLE

st.caption("AI processing notice: if the optional AI extraction is enabled, your story may be sent to the configured AI service for processing. Do not include names or other direct identifiers. Raw story text is not written to the Patient Voice CSV by PathwayAI.")
quick_story = st.text_area(
    "Tell us what happened in your own words",
    key="quick_story_value",
    placeholder="Start anywhere — even one or two sentences are enough.",
    height=180,
    max_chars=MAX_STORY_CHARS,
)
st.caption("You can edit the sample, write your own story, or keep it short. PathwayAI will not treat details you leave out as No or zero.")
organize_story = st.button("✨ Organize My Story", type="primary", use_container_width=True, disabled=not bool(quick_story.strip()))
if organize_story:
    st.session_state["story_organized"] = True
    # Use the configured LLM only after an explicit click and within the pilot call limit.
    # A failed/unavailable LLM never blocks the local rule-based fallback.
    rule_now = extract_quick_story(quick_story)
    allowed, limit_message = ai_call_allowed("story-extraction")
    if allowed and OPENAI_API_KEY and PATHWAYAI_LLM_MODEL:
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
        st.caption("Extraction method: AI structured extraction with validation.")
    else:
        st.caption("Extraction method: backup rule-based extraction used. The AI service was unavailable, not configured, limited, or did not return a valid structured result.")

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
    st.info("Click **✨ Organize My Story** above to see your Journey Record here immediately — no need to scroll to the bottom and come back.")
else:
    st.caption("Prefer structured questions? You can skip the story box and use the optional details below.")

# OPTIONAL LOCAL SUPPORT — ask only after the story/AI value exchange.
st.markdown("### 📍 Find Support Near You *(Optional)*")
st.write("Your location is needed **only if you want local resources**. Add a ZIP code or county to tailor healthcare, public-health, work/disability, and practical-support navigation.")
st.caption("🔒 **We don't need your street address.** You can leave this blank and continue.")
current_location_start = st.text_input(
    "ZIP code or county (optional)",
    key="current_location_start",
    placeholder="e.g., 21044 or Howard County, MD",
    help="Optional. Used only to tailor local navigation and resources; not to determine a diagnosis."
)
if current_location_start.strip():
    st.success("✓ Local-support area added. You can change or remove it at any time.")

# PATIENT VOICE — explicit review/permission; MVP demonstrates the consent loop without publishing raw narrative.
if quick_story.strip() and st.session_state.get("story_organized", False):
    st.markdown("### 🗣️ Make Your Experience Count *(Optional)*")
    st.write("Your story may reveal burdens that healthcare data alone cannot see. With your permission, PathwayAI can use **de-identified structured themes** from your experience to strengthen Patient Voice insights for policymakers.")
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
st.caption("Additional details can help PathwayAI build a more complete picture of your journey and connect you with more relevant support. You may stop after organizing your story; the questions below are optional.")

# 1. LOCATION & EXPOSURE CONTEXT

st.subheader("1. Location & Exposure Context *(Optional)*")
st.write("If you added a ZIP code/county above—or mentioned a location in your story—PathwayAI can use it for care and support navigation. You can leave this section blank.")

top_zip = normalize_zip(current_location_start)
zip_default = quick["zip"] if quick.get("zip") else (top_zip if len(top_zip) == 5 else "")
zip_code = st.text_input(
    "Current ZIP code (optional — only for more precise nearby results)",
    value=zip_default,
    max_chars=5,
    placeholder="e.g., 10940",
    help="Only add or correct this if you want ZIP-level nearby navigation. You do not need to repeat your county."
)

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
st.caption("PathwayAI keeps **exposure location** separate from **current location**: exposure location supports surveillance context; current location helps find care and support.")

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
st.caption("Enter amounts only if known. PathwayAI keeps each component visible instead of hiding it inside one total.")
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
        st.caption("Only these de-identified structured fields are written. Your raw story is not saved to the Patient Voice file.")
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
                    st.success("✓ De-identified structured Patient Voice fields saved. The county Patient Voice layer will refresh with the new contribution.")
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

    st.subheader("Documentation Signals")

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

    if len(signals) >= 3:
        priority = "More documentation signals present"
        explanation = (
            "Multiple exposure and symptom signals are present. "
            "These signals support timely clinical evaluation and careful documentation."
        )

    elif len(signals) >= 1:
        priority = "Some documentation signals present"
        explanation = (
            "One or more exposure or symptom signals are present. "
            "Continue monitoring and document changes."
        )

    else:
        priority = "No documentation signal identified from these entries"
        explanation = (
            "No major exposure or symptom signals were reported in this prototype."
        )

    st.warning(priority)
    st.write(explanation)

    st.subheader("Why PathwayAI Flagged This")

    if signals:
        for signal in signals:
            st.write(f"• {signal.capitalize()}")
    else:
        st.write("• No major signals reported")

    st.caption(
        "This is a documentation signal for the beta prototype, not a risk score and "
        "not a validated Lyme disease prediction model."
    )

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
    st.caption("**Provenance key:** 👤 Patient-entered | 🧮 Modeled from entered values | 📚 Published/public evidence. PathwayAI does not mix these into an unexplained total.")
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
    st.caption("PathwayAI does not predict your future medical bill. Published estimates are shown only as population-level reference points, separate from what you reported above.")
    published_costs = pd.DataFrame({
        "Published measure": ["Mean Lyme-specific medical cost per episode", "Localized disease — mean episode cost", "Disseminated disease — mean episode cost", "Adjusted 6-month excess direct healthcare cost vs controls", "Lyme-attributable patient OOP cost"],
        "Estimate": ["$2,227", "$695", "$6,833", "$5,571", "$188–$399"],
        "Evidence": ["Yu et al., 70,531 U.S. patients", "Yu et al.", "Yu et al.", "Yu et al.", "Yu et al.; OOP subset"],
        "How PathwayAI uses it": ["Population benchmark", "Population benchmark", "Population benchmark", "Population benchmark", "Population benchmark — not your expected OOP"],
    })
    show_readable_table(published_costs, hide_index=True, width="stretch")
    st.write("**Your burden is different from a published average.** Insurance, disease presentation, services used, geography, work situation, caregiving, and access can all change what a person experiences.")
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

    st.markdown("#### PathwayAI Burden Outlook")
    burden_drivers = []
    if providers_seen is not None and providers_seen >= 5: burden_drivers.append("multiple healthcare encounters")
    if test_status == "Yes — more than once": burden_drivers.append("repeat testing / reassessment")
    if second_opinion == "Yes": burden_drivers.append("second opinion / specialist access (may be beneficial care)")
    if days_missed is not None and days_missed >= 10: burden_drivers.append("work/school loss")
    if daily_function in ["Major limitation", "Unable to perform usual activities"]: burden_drivers.append("functional limitation")
    if insurance_context not in ["Not reported", "Unsure / prefer not to answer", "No access or coverage barrier reported"]: burden_drivers.append("access / coverage barriers")
    if _num0(transport_cost) > 0: burden_drivers.append("transportation / lodging")
    if len(burden_drivers) >= 4:
        outlook_level = "Elevated accumulation signal"
    elif len(burden_drivers) >= 2:
        outlook_level = "Moderate accumulation signal"
    else:
        outlook_level = "Limited accumulation signal from entered factors"
    st.metric("Current burden accumulation", outlook_level)
    st.write("**Main drivers identified:** " + (", ".join(burden_drivers) if burden_drivers else "No major drivers identified from the fields entered."))
    st.caption("Prototype navigation signal — not a validated clinical, disability, or financial prediction. It summarizes entered burden drivers and does not predict diagnosis or future disability.")

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
    st.caption("The more relevant detail you provide, the more personalized this burden and preparedness summary can become. PathwayAI does not predict your actual future expenses or determine disability-benefit eligibility.")

    # Personalized support: show only the most relevant actions first.
    show_personalized_support(
        zip_code,
        work_impact,
        insurance_context,
        support_needs,
        burden_drivers,
        quick.get("current_location") or ""
    )

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
    st.caption("This timeline is a documentation view of the information you entered. It does not establish that every later event was caused by Lyme disease.")

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
        "PathwayAI separates patient-reported information, public/observed data, Biobank evidence, "
        "published evidence, and modeled outputs so users can see where each piece of information comes from."
    )

    st.error(
        "PathwayAI does not diagnose Lyme disease or prescribe treatment. "
        "Seek professional medical evaluation for concerning symptoms or "
        "illness after possible tick exposure."
    )