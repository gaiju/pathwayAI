import ast
import json
import math
from pathlib import Path
import unittest

from county_geography import containing_county, geometry_contains


class CountyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.geo = json.loads(Path("us_county_boundaries.geojson").read_text())
        # Representative Vienna coordinates; no live ZIP API or patient data.
        cls.vienna = {"zip": "22180", "city": "Vienna", "state_code": "VA",
                      "lat": 38.9014, "lon": -77.2653}

    def test_vienna_is_fairfax_not_richmond(self):
        county = containing_county(self.vienna, self.geo)
        self.assertEqual(county["id"], "51059")
        self.assertEqual(county["properties"]["NAME"], "Fairfax")

    def test_new_york_only_data_cannot_match_virginia(self):
        ny = {"features": [f for f in self.geo["features"] if f["id"].startswith("36")]}
        self.assertIsNone(containing_county(self.vienna, ny))

    def test_state_mismatch_missing_invalid_and_outside(self):
        for point in ({}, dict(self.vienna, state_code="NY"),
                      dict(self.vienna, lat=None), dict(self.vienna, lat=float("nan")),
                      dict(self.vienna, lon=0, lat=0)):
            self.assertIsNone(containing_county(point, self.geo))

    def test_holes_multipolygons_and_shared_boundary(self):
        ring = [[0, 0], [4, 0], [4, 4], [0, 4], [0, 0]]
        hole = [[1, 1], [3, 1], [3, 3], [1, 3], [1, 1]]
        geometry = {"type": "Polygon", "coordinates": [ring, hole]}
        self.assertTrue(geometry_contains(geometry, .5, .5))
        self.assertFalse(geometry_contains(geometry, 2, 2))
        self.assertTrue(geometry_contains({"type": "MultiPolygon", "coordinates": [[ring]]}, 2, 2))
        feature = {"id": "51059", "geometry": geometry}
        self.assertIsNone(containing_county({"lon": 0, "lat": 0}, {"features": [feature, feature]}))

    def test_real_comparison_joins_fairfax_cdc_values(self):
        tree = ast.parse(Path("app.py").read_text())
        functions = [node for node in tree.body if isinstance(node, ast.FunctionDef)
                     and node.name in {"_destination_county_context", "_geometry_centroid"}]
        namespace = {"math": math, "containing_county": containing_county}
        exec(compile(ast.Module(body=functions, type_ignores=[]), "app.py", "exec"), namespace)
        destination, nearby = namespace["_destination_county_context"](
            self.vienna, self.geo, {"51059": "Established"}, {"51059": 123})
        self.assertEqual(destination["fips"], "51059")
        self.assertEqual(destination["tick"], "Established")
        self.assertEqual(destination["lyme_cases"], 123)
        self.assertNotIn("51059", [row["fips"] for row in nearby])
        self.assertEqual(len(nearby), 8)


if __name__ == "__main__":
    unittest.main()
