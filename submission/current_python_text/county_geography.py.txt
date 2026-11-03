"""Match lookup coordinates to county boundaries, never to a nearest centroid."""

import math

STATE_FIPS = dict(zip(
    "AL AK AZ AR CA CO CT DE DC FL GA HI ID IL IN IA KS KY LA ME MD MA MI MN MS MO MT NE NV NH NJ NM NY NC ND OH OK OR PA RI SC SD TN TX UT VT VA WA WV WI WY PR".split(),
    "01 02 04 05 06 08 09 10 11 12 13 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40 41 42 44 45 46 47 48 49 50 51 53 54 55 56 72".split(),
))


def _ring_contains(lon, lat, ring):
    inside = False
    if len(ring) < 3:
        return False
    previous = ring[-1]
    for current in ring:
        x1, y1 = previous[:2]
        x2, y2 = current[:2]
        cross = (lon - x1) * (y2 - y1) - (lat - y1) * (x2 - x1)
        if abs(cross) < 1e-10 and min(x1, x2) <= lon <= max(x1, x2) and min(y1, y2) <= lat <= max(y1, y2):
            return True
        if (y1 > lat) != (y2 > lat):
            intersect = x1 + (lat - y1) * (x2 - x1) / (y2 - y1)
            if lon < intersect:
                inside = not inside
        previous = current
    return inside


def geometry_contains(geometry, lon, lat):
    coordinates = geometry.get("coordinates", [])
    polygons = [coordinates] if geometry.get("type") == "Polygon" else (
        coordinates if geometry.get("type") == "MultiPolygon" else [])
    return any(polygon and _ring_contains(lon, lat, polygon[0])
               and not any(_ring_contains(lon, lat, hole) for hole in polygon[1:])
               for polygon in polygons)


def containing_county(destination, geo):
    if not destination:
        return None
    try:
        lon, lat = float(destination["lon"]), float(destination["lat"])
    except (KeyError, TypeError, ValueError):
        return None
    if not math.isfinite(lon) or not math.isfinite(lat) or not (-180 <= lon <= 180 and -90 <= lat <= 90):
        return None
    state = STATE_FIPS.get(destination.get("state_code", "").upper())
    matches = []
    for feature in geo.get("features", []):
        fid = str(feature.get("id", "")).zfill(5)
        if state and not fid.startswith(state):
            continue
        if geometry_contains(feature.get("geometry") or {}, lon, lat):
            matches.append(feature)
    # Shared boundaries, overlapping geometry and uncovered points stay unresolved.
    return matches[0] if len(matches) == 1 else None
