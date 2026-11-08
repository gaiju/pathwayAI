"""Fixed local visual resources, independent of patient/session data."""
import base64
import json
from functools import lru_cache
from pathlib import Path

BASE = Path(__file__).resolve().parent
PHOTO_FILES = {key: BASE / 'assets' / 'page_photos' / (key+'.jpg')
               for key in ('lake', 'forest', 'tick_leaf', 'river')}


@lru_cache(maxsize=4)
def photo_data_uri(key):
    path=PHOTO_FILES.get(key)
    if path is None:return None
    try:data=path.read_bytes()
    except OSError:return None
    return 'data:image/jpeg;base64,'+base64.b64encode(data).decode('ascii')


@lru_cache(maxsize=1)
def load_nys_boundaries():
    # Exact existing public geometry moved out of app.py; no source refresh.
    return json.loads((BASE/'data'/'ny_county_map_boundaries.geojson').read_text())
