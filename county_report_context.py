"""County-specific plan context and public boundary orientation, not risk mapping."""
from functools import lru_cache
from pathlib import Path
import hashlib
import json
import math
from mid_hudson_counties import COUNTIES

BASE=Path(__file__).resolve().parent
CHIP_URL='https://www.dutchessny.gov/Departments/DBCH/Docs/Dutchess-County-Community-Health-Improvement-Plan.pdf'
BOUNDARY_URL='https://github.com/gaiju/pathwayAI/blob/2766688/us_county_boundaries.geojson'


def plan_context(county):
    if county!='Dutchess':return None
    return {
        'title':'Fit with the Dutchess 2025–2030 health plan',
        'source_url':CHIP_URL,'period':'2025–2030','evidence_type':'General county planning context, not Lyme-specific findings',
        'source_sha256':hashlib.sha256((BASE/'data/evidence/Dutchess_CHIP_2025_2030.pdf').read_bytes()).hexdigest(),
        'findings':[
            {'text':'The plan describes geographic and disability-related disparities in care access.','printed_pages':'5','pdf_pages':'6'},
            {'text':'Among 830 residents participating in informal event voting, insurance coverage and access to care was a leading topic. This was not a representative survey or a Lyme sample.','printed_pages':'6–7','pdf_pages':'7–8'},
            {'text':'The plan describes social-needs referrals through Hudson Valley Care Coalition and Unite Us; its mobile screening pathway concerns blood pressure, not Lyme.','printed_pages':'9–11','pdf_pages':'10–12'},
        ],
        'source_checked_on':'2026-11-04',
        'selected_priorities':['Nutrition Security','Preventive Services for Chronic Disease Control and Prevention','Primary Prevention, Substance Misuse, and Overdose Prevention'],
        'question':'Could reviewed Lyme visit summaries and support questions complement existing care-navigation and referral work?',
        'limits':'PathwayAI proposal for discussion; no county endorsement, service commitment or referral-platform integration. Verify current services with partners.'
    }


@lru_cache(maxsize=1)
def regional_features():
    data=json.loads((BASE/'us_county_boundaries.geojson').read_text())
    return {str(f.get('id','')).zfill(5):f for f in data.get('features',[]) if str(f.get('id','')).zfill(5) in COUNTIES.values()}


def polygons(feature):
    geom=feature['geometry']
    return geom['coordinates'] if geom['type']=='MultiPolygon' else [geom['coordinates']]


def county_location_map(county):
    """Highlight one county within the seven-county pilot; no disease data colors."""
    from reportlab.graphics.shapes import Drawing,Path,String
    from reportlab.lib.colors import HexColor
    if county not in COUNTIES:raise ValueError('Choose a supported county.')
    features=regional_features()
    if COUNTIES[county] not in features:return None
    points=[point for f in features.values() for polygon in polygons(f) for ring in polygon for point in ring]
    cosine=math.cos(math.radians(sum(p[1] for p in points)/len(points)))
    west=min(p[0]*cosine for p in points);east=max(p[0]*cosine for p in points)
    south=min(p[1] for p in points);north=max(p[1] for p in points)
    scale=min(90/(east-west),40/(north-south))
    dx=(108-(east-west)*scale)/2;dy=13+(40-(north-south)*scale)/2
    drawing=Drawing(108,60)
    # Draw selected boundary last so its outline stays visible.
    ordered=sorted(features.items(),key=lambda item:item[0]==COUNTIES[county])
    for fips,feature in ordered:
        path=Path(fillColor=HexColor('#247c8a' if fips==COUNTIES[county] else '#e8eef1'),strokeColor=HexColor('#657c86'),strokeWidth=.5)
        for polygon in polygons(feature):
            for ring in polygon:
                for index,point in enumerate(ring):
                    x=dx+(point[0]*cosine-west)*scale;y=dy+(point[1]-south)*scale
                    (path.moveTo if index==0 else path.lineTo)(x,y)
                path.closePath()
        drawing.add(path)
    drawing.add(String(98,53,'N',fontName='PathwayUnicodeV2',fontSize=6,fillColor=HexColor('#163b50')))
    drawing.add(String(54,4,'Mid-Hudson · location only',textAnchor='middle',fontName='PathwayUnicodeV2',fontSize=5.6,fillColor=HexColor('#163b50')))
    return drawing


def map_metadata(county):
    return {'selected_county':county,'county_fips':COUNTIES[county],
            'scope':'Seven-county Mid-Hudson pilot; selected county highlighted',
            'purpose':'Geographic orientation only; not disease risk, service coverage or a county-published map',
            'source_url':BOUNDARY_URL,'source_period':'Bundled boundary file; underlying vintage not independently verified',
            'source_sha256':hashlib.sha256((BASE/'us_county_boundaries.geojson').read_bytes()).hexdigest()}
