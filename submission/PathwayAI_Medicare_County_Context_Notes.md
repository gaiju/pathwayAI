# Medicare county context: scope and planning use

The project owner supplied 22 CMS extract rows covering Dutchess (36027) and Orange (36071), 2014–2024, County geography and All Original Medicare age group. We checked all 246 source columns for completeness, unique county-year records, definitions against the supplied CMS dictionary, and 88 inpatient/outpatient total-to-per-capita relationships. The full CMS source file was not independently downloaded.

Latest common year: 2024. Annual USD per Original Medicare beneficiary:

| Measure | Dutchess | Orange |
|---|---:|---:|
| Original Medicare beneficiaries | 33,439 | 38,188 |
| Actual inpatient payment | $5,219.40 | $4,689.79 |
| Actual hospital outpatient payment | $2,522.31 | $2,295.46 |
| Standardized inpatient payment | $3,277.17 | $3,079.13 |
| Standardized hospital outpatient payment | $2,154.84 | $1,970.27 |

Standardization adjusts geographic payment rates, not health status. Hospital outpatient is not all non-hospital care. These are program payments by beneficiary residence, not hospital charges, patient bills, all-payer spending, Lyme-specific costs, savings, or evidence of unmet need. Do not add these amounts to personal records or Lyme cost scenarios.

## How this fits county planning

Use the comparison as background on Medicare spending and population, with a consistent definition and year. It cannot identify why payments differ or show which intervention a county should fund. The stronger PathwayAI planning workflow is: reported barrier → verify existing services and eligibility → agree on a feasible response, responsible partners and resources → track referrals, appointments reached, assistance received and unresolved needs.

Example for discussion, not an established county program: a care-navigation pilot for people facing insurance or bill barriers. Verify local clinic and financial-assistance contacts, identify who maintains the information and follows referrals, estimate staff time and funding, and test whether patients actually reach support. New shared patient-report collection remains off until consent, secure storage and governance are ready. Individual feedback is not a representative county needs assessment.

## Evidence and provenance

See data/cms_medicare_county_provenance.json for supplied extract and dictionary SHA-256 hashes, validation checks and limitations. The exact supplied public-data extract is retained in data/cms_medicare_dutchess_orange_source.tsv. The app uses a smaller field selection in data/cms_medicare_dutchess_orange_2014_2024.csv.

Official dataset: https://data.cms.gov/summary-statistics-on-use-and-payments/medicare-geographic-comparisons/medicare-geographic-variation-by-national-state-county
