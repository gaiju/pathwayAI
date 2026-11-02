# Additional county planning indicators — review only

This extends the unmerged `feature/community-action-summary` branch. It is not deployed and is not described as part of the original HHS-submitted MVP.

## Added context

- NYSDOH 2024 cases and published rates for Dutchess, Orange and New York State, using the existing verified JSON snapshots. No inferred population denominator or county totals.
- Selected-county 2022–2024 rate history, reusing the regional-assessment and NYSDOH source values already used by the app. No pre-2022 trend or causal interpretation.
- Census language-other-than-English-at-home percentages for residents age 5+, ACS 2020–2024, reusing the app's existing QuickFacts snapshots (Dutchess 16.2%; Orange 30.2%). Not English proficiency, immigration status or interpreter demand.
- Existing county initiative links from `pathwayai_county_assets.csv`. Dutchess has three listings. Orange has none in this file; this is missing directory information, not absence of services. Contacts, activity and availability require verification.
- HRSA AHRF uninsured-under-65 rates (2022: Dutchess 4.7%, Orange 5.5%) and poverty rates (2023: Dutchess 8.0%, Orange 12.7%), read from their named fields rather than relabeled as ACS 2020–2024. The selected file fields do not supply MOEs. These are general population context, not Lyme-attributable needs.
- Four plain-language planning questions that connect these indicators to local investigation. No recommendation to allocate resources solely from these values.

The county planning view has a collapsed additional-data section. Both county PDF and methods CSV contain the selected county context and source provenance. Existing original-dollar cost calculations, optional inflation method, county selection, audience actions and patient-record separation are unchanged.

## Deferred

Newer Census/QuickFacts insurance and poverty estimates, broadband, shortage-designation and disability figures are deferred until the specific measure, denominator, source and reporting period are checked. The newly extracted older AHRF insurance/poverty figures remain explicitly year-labeled. No underreporting adjustment, risk score, ranking, savings, population-level survey extrapolation or patient-data collection is introduced. Top-ten county work remains incomplete.

## Checks

- Eight targeted tests passed: new indicator consistency, explicit missingness, no county substitution, selected-county exports and unchanged economic arithmetic, plus existing community UI/privacy/report tests.
- Desktop (1440px) and mobile (390px) browser checks cover the expanded section, changing to Orange, missing initiative directory and no page overflow/UI exceptions.
- Both counties' optional-inflation PDFs generated with all text within page bounds; five pages each. Dutchess has 11 clickable source/directory/CPI links; Orange has eight.
- Review artifacts: `docs/review/county_additional_indicators_desktop.png` and `docs/review/PathwayAI_Dutchess_Additional_Indicators_Preview.pdf`.
- No fresh retrieval of official source pages; these are reused source snapshots, not claims of latest releases or current service availability.

External verification request: for uninsured residents under 65, poverty and households without broadband, supply the exact official table/link, estimate, reporting period, population/denominator and margin of error if available for both counties. Local service verification needs a county staff member or navigator to confirm current contacts and availability.


## Formal export revision (version 1.3)

County PDFs now use a dedicated numbers-first layout, reusing the existing multilingual font utilities. Page 1 presents rounded key figures and local indicators, page 2 presents planning actions and resident-engagement questions, and page 3 uses smaller readable text for linked references and methods. Price basis and illustrative status stay next to the headline amount. Original arithmetic and full-precision CPI provenance remain in Methods/CSV.

The noncounty 33-person survey has been removed from county PDF, text and CSV outputs to avoid geographic ambiguity. It remains in the broader community Evidence & Methods context, with its original sampling limitations. County exports record that county-specific patient-reported findings have not been established; suggested resident priorities are questions, not collected findings. This supersedes earlier review documentation describing noncounty survey context inside county downloads.

All 60 county/priority/audience/inflation combinations produced three-page PDFs with text inside page bounds. Eight targeted data/UI/privacy/export tests passed. No shared patient PDF defaults changed. No merge or deployment.
