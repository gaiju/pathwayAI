import json
import unittest
from county_burden_report import build_report, report_text, report_csv_rows

class PublishedResearchTests(unittest.TestCase):
    def test_external_context_and_separate_county_calculation(self):
        r=build_report('Orange','Getting to care',True)
        studies=r['published_research_context']
        self.assertEqual(len(studies),3)
        self.assertIn('52,795',studies[1]['sample'])
        self.assertIn('3,090',studies[2]['sample'])
        self.assertIn('self-reported',studies[2]['limit'])
        self.assertEqual(r['illustrative_total_2016_usd'],964*2032)
        self.assertEqual(len(json.loads(report_csv_rows(r)[0]['published_research_context'])),3)
        text=report_text(r)
        self.assertIn('External study populations, not county patient findings',text)
        self.assertNotIn('33 respondents',text)
        for study in studies:self.assertIn(study['url'],text)
