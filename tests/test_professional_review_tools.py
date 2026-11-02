from urllib.parse import urlsplit, parse_qs
import unittest
from streamlit.testing.v1 import AppTest
from pathlib import Path
from community_action_summary import professional_review_link, REVIEW_QUESTIONS
from county_burden_report import build_report, report_csv_rows


class ProfessionalReviewToolsTests(unittest.TestCase):
    def test_review_link_contains_four_questions_and_no_automatic_submission(self):
        url=professional_review_link('Orange')
        parsed=urlsplit(url);query=parse_qs(parsed.query)
        self.assertEqual(parsed.scheme,'mailto')
        self.assertEqual(parsed.path,'pathwayai.feedback@gmail.com')
        self.assertIn('Orange County',query['subject'][0])
        self.assertEqual(len(REVIEW_QUESTIONS),4)
        for question in REVIEW_QUESTIONS:self.assertIn(question,query['body'][0])
        self.assertIn('May we quote',query['body'][0])
        with self.assertRaises(ValueError):professional_review_link('PRIVATE SENTINEL')

    def test_components_are_a_reconciliation_not_an_added_total(self):
        for county in ['Dutchess','Orange','Putnam','Rockland','Sullivan','Ulster','Westchester']:
            r=build_report(county,'Getting to care',True);c=r['study_components']
            self.assertEqual(c['medical_mean'],1333)
            self.assertEqual(c['other_expenses_and_productivity'],699)
            self.assertEqual(c['medical_mean']+c['other_expenses_and_productivity'],c['total_societal_mean'])
            self.assertIsNone(c['caregiving_separate_amount'])
            self.assertEqual(c['dollar_year'],2016)
            self.assertEqual(r['illustrative_total_2016_usd'],r['reported_cases']*2032)
            self.assertIn('derived residual',c['method'])
            self.assertNotIn('assembles',r['ai_role'])
            self.assertIn('study_components',report_csv_rows(r)[0])

    def test_review_invitation_and_ai_description_visible_without_changing_routes(self):
        at=AppTest.from_file(str(Path(__file__).resolve().parents[1]/'app.py'),default_timeout=60).run()
        at.button(key='route_county').click().run()
        self.assertFalse(list(at.exception))
        text=' '.join(str(x.value) for x in at.markdown)
        captions=' '.join(str(x.value) for x in at.caption)
        self.assertIn('For public-health partners',text)
        self.assertIn('Optional AI helps organize mixed-language patient notes',captions)
        self.assertIn('Nothing is submitted automatically',captions)
        self.assertEqual(len(at.selectbox(key='county_report_county').options),7)
        self.assertTrue(any('What makes up the published cost figure?'==x.label for x in at.expander))
        self.assertTrue(any(x.label=='Download county burden & action report (PDF)' for x in at.get('download_button')))
