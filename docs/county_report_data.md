# Adding a county report

Current verified coverage is Dutchess and Orange, New York. A registry entry does not itself verify data. No nationwide CDC feed or automatic retrieval is implemented. Use the county-data checklist in the app to prepare additional coverage; it sends no request and collects no patient data.

`data/county_report_registry.json` holds schema version 1 and county entries. Each entry requires a unique display `name`, `state`, unique five-digit `fips`, reporting `year`, local `cases_record` and `rates_record` JSON filenames, `county_key`, and `state_rate_key`. Use a state-qualified display name if county names collide. Keep record paths directly inside `data/`.

Case records require `verified_lyme_case_counts[county_key]`. Rate records require `verified_rates[county_key]` and `verified_rates[state_rate_key]`. Counts must be actual nonnegative integer counts, rates finite nonnegative numbers; suppressed/missing values must not be replaced with zero. Registry year must match the underlying count/rate period. A new county may use separate source records with the same schema. Preserve original URLs, source definitions, data year, verification status/date, table/page and supplied-file SHA-256. Source verification metadata is a record of a previous check, not proof of current authenticity or live retrieval.

Before adding coverage, verify FIPS, geography, case definition, rate units, year, suppression, state comparator and original tables. Add a real county only after review; do not seed counties with copied pilot values. The existing 2022–2024 chart is restricted to the verified Dutchess/Orange NY series. Other counties show no historical chart until source-backed series support is added.

Cost transfer remains an assumption. The current Hook-based illustration is not observed local spending and may not transfer to another population. No productivity/other component split is invented. Published component data need source-table verification before adding a stacked chart. Demographic and service data remain separately sourced context; the registry does not manufacture them.

Optional local notes are public planning context only. The app holds them in server-side session state, separately by county, and includes them in the full PDF/text/CSV as unverified local context. They do not change public numbers or become shared records. The one-page executive brief points to the full report instead of silently truncating long notes. Use the existing clear-session action to clear session entries; downloads, hosting logs and backups have separate lifecycles.

The Community page now opens on county comparison; existing national, planning, methods and personal workflows remain available. Use `docs/community_review.md` for the five-minute Dutchess script. No deployment, county endorsement or partner commitment is implied.
