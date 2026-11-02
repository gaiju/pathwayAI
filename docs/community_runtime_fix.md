# Community helper compatibility fix

A reported TypeError occurred at `show_county_report(audience=...)` after publication. The older helper has no audience parameter; retaining it in a running Streamlit interpreter reproduces that failure. Live logs are not accessible here, so this is the reproduced compatibility failure, not a claim of direct log inspection.

`community_runtime.py` checks source fingerprints for the public community helper group and refreshes cached helpers in dependency order when the loaded version predates the file. It does not catch unrelated runtime TypeErrors, clear Streamlit caches/session state, read private inputs, change datasets, or reset user entries. Unchanged helpers are not repeatedly reloaded.

Nine focused tests passed: stale signature recovery, dependent-reference recovery, stable subsequent calls, preserved saved notes, seven-county navigation, downloads and existing audience/public-data behavior. The overview now uses short plain-text support areas without heading anchors, an explicit organization selector and a next-step instruction. Detailed export content and calculations are unchanged.
