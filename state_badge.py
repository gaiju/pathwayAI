"""Neutral destination outline derived from bundled county geometry, not a seal."""
import json
import math
from pathlib import Path
from functools import lru_cache


@lru_cache(maxsize=1)
def state_outlines():
    return json.loads((Path(__file__).parent/'data/state_outline_badges.json').read_text())


def state_badge(code):
    from reportlab.graphics.shapes import Drawing, Path as DrawPath, String
    from reportlab.lib.colors import HexColor
    polygons=state_outlines().get(code)
    if not polygons:
        return None
    # Alaska crosses the date line. Keep its islands on the same side of the map.
    polygons=[[(x-360 if code=='AK' and x>0 else x,y) for x,y in ring] for ring in polygons]
    points=[p for ring in polygons for p in ring]
    mean_lat=sum(y for _,y in points)/len(points)
    factor=math.cos(math.radians(mean_lat))
    polygons=[[(x*factor,y) for x,y in ring] for ring in polygons]
    points=[p for ring in polygons for p in ring]
    xmin=min(x for x,y in points);xmax=max(x for x,y in points)
    ymin=min(y for x,y in points);ymax=max(y for x,y in points)
    scale=min(120/(xmax-xmin),75/(ymax-ymin))
    drawing=Drawing(490,100)
    ox=10+(120-(xmax-xmin)*scale)/2
    oy=12+(75-(ymax-ymin)*scale)/2
    for ring in polygons:
        path=DrawPath(fillColor=HexColor('#d9eef4'),strokeColor=HexColor('#2474a6'),strokeWidth=.7)
        path.moveTo(ox+(ring[0][0]-xmin)*scale,oy+(ring[0][1]-ymin)*scale)
        for x,y in ring[1:]:path.lineTo(ox+(x-xmin)*scale,oy+(y-ymin)*scale)
        path.closePath();drawing.add(path)
    drawing.add(String(155,55,code+' destination outline',fontName='PathwayText',fontSize=12,fillColor=HexColor('#163149')))
    drawing.add(String(155,33,'Illustration only; not an official seal or endorsement.',fontName='PathwayText',fontSize=9,fillColor=HexColor('#486274')))
    return drawing
