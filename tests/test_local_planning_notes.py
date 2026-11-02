import unittest
from copy import deepcopy
from county_burden_report import build_report,report_text
from community_pathway import local_planning_notes

class LocalPlanningTests(unittest.TestCase):
    def test_values_sources_and_question(self):
        r=build_report('Orange','Getting to care')
        notes=r['local_planning_notes']
        self.assertEqual(len(notes),3)
        self.assertIn('237',notes[0]['text'])
        self.assertIn('109.8',notes[0]['text'])
        self.assertIn('5.5%',notes[1]['text'])
        self.assertEqual(notes[2]['source_url'],None)
        self.assertIn(r['planning']['decision'],notes[2]['text'])
        self.assertIn('What this means for local planning'.upper(),report_text(r))
        self.assertEqual(r['illustrative_total_2016_usd'],964*2032)

    def test_missing_and_zero_not_confused(self):
        r=deepcopy(build_report('Dutchess','Getting to care'))
        r['reported_rate_per_100000']=None
        for row in r['additional_public_context']['socioeconomic_context']:row['value']=None
        notes=local_planning_notes(r)
        self.assertIn('unavailable',notes[0]['text'])
        self.assertIn('unavailable',notes[1]['text'])
        r['reported_rate_per_100000']=0
        r['additional_public_context']['socioeconomic_context'][0]['value']=0
        notes=local_planning_notes(r)
        self.assertIn('0 per 100,000',notes[0]['text'])
        self.assertIn('0%',notes[1]['text'])
