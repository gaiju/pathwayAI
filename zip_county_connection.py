"""Session-only geographic handoff; never transfers patient notes to reports."""
from mid_hudson_counties import COUNTIES
from county_geography import containing_county


def remember_location(state, zip_code, resolved, boundaries, source):
    """Retain only the ZIP lookup's geographic suggestion across page cleanup."""
    if len(str(zip_code)) != 5 or not str(zip_code).isdigit():
        state.pop('community_location_hint', None)
        return None
    match = containing_county(resolved, boundaries) if resolved else None
    fips = str(match.get('id', '')).zfill(5) if match else None
    county = next((name for name, code in COUNTIES.items() if code == fips), None)
    hint = {'zip': str(zip_code), 'county': county, 'source': source}
    state['community_location_hint'] = hint
    return hint


def apply_county_hint(state):
    hint = state.get('community_location_hint')
    if not hint:
        return None
    signature = (hint['zip'], hint['county'], hint['source'])
    if signature != state.get('community_location_applied'):
        if hint['county'] in COUNTIES:
            state['county_report_county'] = hint['county']
        state['community_location_applied'] = signature
    return hint
