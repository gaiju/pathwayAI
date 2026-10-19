import unittest
from copy import deepcopy
from medicare_county_context import load_records, common_years, payment_rows


class MedicareCountyContextTests(unittest.TestCase):
    def test_supplied_county_extract_and_dictionary_fields(self):
        rows = load_records()
        self.assertEqual(len(rows), 22)
        self.assertEqual(common_years(rows), list(range(2024, 2013, -1)))
        actual = payment_rows(standardized=False)
        self.assertEqual([(r['County'], r['Year'], r['Original Medicare beneficiaries'], r['Inpatient'], r['Hospital outpatient']) for r in actual],
                         [('Dutchess', 2024, 33439, 5219.40, 2522.31), ('Orange', 2024, 38188, 4689.79, 2295.46)])
        standard = payment_rows()
        self.assertEqual([(r['Inpatient'], r['Hospital outpatient']) for r in standard], [(3277.17, 2154.84), (3079.13, 1970.27)])

    def test_latest_common_year_and_nonoverlapping_age_group(self):
        records = [r for r in load_records() if not (r['YEAR'] == '2024' and r['BENE_GEO_CD'] == '36071')]
        other_age = deepcopy(records[-1]);other_age['BENE_AGE_LVL'] = '65 and older';other_age['BENES_OM_CNT'] = '999999'
        records.append(other_age)
        self.assertTrue(all(r['Year'] == 2023 for r in payment_rows(records=records)))
        self.assertTrue(all(r['Original Medicare beneficiaries'] != 999999 for r in payment_rows(records=records)))
        with self.assertRaises(ValueError):payment_rows(2024, records=records)

    def test_suppression_and_duplicates_do_not_become_estimates(self):
        records = deepcopy(load_records())
        for r in records:
            if r['YEAR'] == '2024' and r['BENE_GEO_CD'] == '36027':r['IP_MDCR_STDZD_PYMT_PC'] = '*'
        self.assertIsNone(payment_rows(records=records)[0]['Inpatient'])
        with self.assertRaises(ValueError):payment_rows(records=records + [deepcopy(records[0])])

    def test_optional_ui_works_without_patient_inputs(self):
        from streamlit.testing.v1 import AppTest
        app = AppTest.from_string('from medicare_county_context import show_medicare_county_context\nshow_medicare_county_context()').run()
        self.assertEqual(len(app.exception), 0)
        self.assertEqual(app.selectbox[0].value, 2024)
        app.radio[0].set_value('Actual').run()
        self.assertEqual(len(app.exception), 0)
        self.assertAlmostEqual(float(app.dataframe[0].value.iloc[0]['Inpatient']), 5219.40)


if __name__ == '__main__':
    unittest.main()
