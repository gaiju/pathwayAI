# Approved county-report publication — November 4, 2026

Owner explicitly authorized “Publish the revised county reports.” Release merges only the reviewed county-location/plan branch and Version 1.11 meeting-first PDF changes into main 2766688. The independent embedded-multiscript PDF remediation is not included.

The four-page report leads with county facts, selected planning question and county comparison; original 2016-dollar illustration is primary and optional 11-month 2025 purchasing-power comparison is secondary. Page 2 shows resources and practical follow-up, with Dutchess Tick Task Force/Mobile Health Unit directory links requiring local verification. Dutchess 2025–2030 plan findings are county-specific and separate from Lyme surveillance; references/methods remain last. Other counties do not inherit Dutchess entries. Arithmetic/data years unchanged.

The homepage sample cache now keys the county PDF by report version after refreshing community helpers, preventing a warm process from retaining the previous report layout. A regression test checks reuse within a version and regeneration when the version changes.

Release checks: 210 report combinations previously passed four-page, selected-priority, original-dollar-first, county-specific scope, links and overflow checks. Browser on the release build verified Version 1.11 homepage sample and Dutchess/Orange downloads, correct resource scope, references page 4, no app exceptions and mobile no page overflow. Two focused homepage/cache tests passed. Public Streamlit verification remains blocked by this environment's HTTP policy; a successful push does not confirm completion of the cloud rebuild.

Full release regression suite: 121 tests passed in 143.806 seconds. The additional cache-version regression was separately included in the two passing focused homepage tests. Python compilation passed.
