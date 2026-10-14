# Destination county matching

The outdoor planner now loads national reference county boundaries and matches
the ZIP lookup coordinate using polygon containment. County centers only rank
nearby comparisons. No containment match, an inconsistent state, or multiple
matches results in an unresolved county rather than a nearest-county guess.

The prior loader returned New York geometry even for out-of-state destinations.
Nearest-center matching could therefore label Vienna, Virginia as Richmond
County, New York. The representative Vienna regression now resolves Fairfax
County, Virginia (FIPS 51059).

Boundary source: Census-derived reference GeoJSON distributed by Plotly:
https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json

The file is bundled locally in `us_county_boundaries.geojson`; downloading
boundaries at runtime is unnecessary. Metadata uses historical Census geographic
identifiers. This reference is not a guarantee of current boundaries everywhere;
boundary revisions and county-equivalent changes need a maintained update process.
The existing New York public-data drawing and surveillance snapshots remain
separate from this national geography.

ZIP coordinates still come from the existing Zippopotam geographic lookup.
A ZIP can span multiple counties, and its lookup point is not a street address.
The UI says "County at ZIP lookup point" and asks users to confirm the county
of their actual destination. No street address or new credential is collected.
Missing surveillance values remain missing, not zero. Independent cities use
their own county-equivalent FIPS identifiers.

Validation: representative Vienna coordinate resolves to 51059; New York-only
boundaries cannot assign a county to Virginia; unmatched, invalid and ambiguous
points remain unresolved; polygon holes and multipolygons are supported.
The live ZIP endpoint was blocked by this environment's network proxy, so the
live lookup for 22180 must still be checked in the Streamlit deployment.
