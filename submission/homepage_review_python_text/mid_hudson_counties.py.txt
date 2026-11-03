"""Explicit seven-county scope and source-backed surveillance availability."""
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent
COUNTIES = {'Dutchess': '36027', 'Orange': '36071', 'Putnam': '36079',
            'Rockland': '36087', 'Sullivan': '36105', 'Ulster': '36111', 'Westchester': '36119'}
REGION = 'Mid-Hudson: Dutchess, Orange, Putnam, Rockland, Sullivan, Ulster and Westchester'


def _json(path):
    try:
        return json.loads(path.read_text())
    except (OSError, ValueError):
        return {}


def surveillance(county, base=None):
    if county not in COUNTIES:
        raise ValueError('Choose a supported Mid-Hudson county.')
    root = Path(base) if base is not None else BASE
    cases = _json(root / 'data/ny_lyme_cases_2024_verification.json')
    verified = _json(root / 'data/ny_lyme_rates_2024_verification.json')
    statewide = _json(root / 'data/ny_lyme_map_rates_2024.json')
    count = cases.get('verified_lyme_case_counts', {}).get(county)
    rate = verified.get('verified_rates', {}).get(county)
    if rate is None:
        rate = statewide.get('county_rates', {}).get(county.upper())
    return {'county': county, 'fips': COUNTIES[county], 'year': 2024,
            'reported_cases': count, 'reported_rate': rate,
            'case_count_status': 'Verified stored NYSDOH count.' if count is not None else 'Not available: official county case count still requires verification.',
            'rate_status': 'Stored NYSDOH published rate; not freshly retrieved.' if rate is not None else 'Not available.',
            'case_source': cases.get('source_url', 'https://www.health.ny.gov/statistics/diseases/communicable/2024/docs/cases.pdf'),
            'rate_source': statewide.get('source_url', 'https://www.health.ny.gov/statistics/diseases/communicable/2024/docs/rates.pdf')}


def regional_coverage(base=None):
    return [surveillance(county, base=base) for county in COUNTIES]
