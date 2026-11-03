import json
from pathlib import Path
import unittest
from zip_county_connection import remember_location, apply_county_hint


class ZipConnectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.geo = json.loads(Path('us_county_boundaries.geojson').read_text())

    def test_supported_suggestion_and_manual_override(self):
        state = {'private_notes': 'never transferred'}
        hint = remember_location(state, '12601', {'state_code': 'NY', 'lat': 41.70, 'lon': -73.92}, self.geo, 'care_location')
        self.assertEqual(hint['county'], 'Dutchess')
        apply_county_hint(state)
        self.assertEqual(state['county_report_county'], 'Dutchess')
        state['county_report_county'] = 'Orange'
        apply_county_hint(state)
        self.assertEqual(state['county_report_county'], 'Orange')
        self.assertNotIn('private_notes', hint)

    def test_outside_pilot_does_not_assign_local_report(self):
        state = {'county_report_county': 'Orange'}
        hint = remember_location(state, '22180', {'state_code': 'VA', 'lat':38.9014, 'lon':-77.2653}, self.geo, 'care_location')
        self.assertIsNone(hint['county'])
        apply_county_hint(state)
        self.assertEqual(state['county_report_county'], 'Orange')

    def test_lookup_failure_and_invalid_input(self):
        state = {}
        self.assertIsNone(remember_location(state, '10001', None, self.geo, 'care_location')['county'])
        self.assertIsNone(remember_location(state, '', None, self.geo, 'care_location'))
        self.assertNotIn('community_location_hint', state)

    def test_new_destination_updates_suggestion(self):
        state = {}
        remember_location(state, '12601', {'state_code':'NY','lat':41.70,'lon':-73.92}, self.geo, 'care_location')
        apply_county_hint(state)
        remember_location(state, '10940', {'state_code':'NY','lat':41.4459,'lon':-74.4229}, self.geo, 'outdoor_destination')
        apply_county_hint(state)
        self.assertEqual(state['county_report_county'], 'Orange')
