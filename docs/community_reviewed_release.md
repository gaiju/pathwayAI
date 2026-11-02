# Approved community-report release — 2026-11-02

Owner approved publication of the reviewed community report changes. Merged the reviewed branch into a release based on current main (cb4cac6), preserving the already-published Lyme Treatment Foundation grant link. Unrelated alternative homepage branches are excluded.

Includes: public-health review invitation, supported cost-component reconciliation, ZIP-to-pilot-county handoff with out-of-area fallback, clearly separated published research context, compact patient/community pathways, source-linked planning questions, and the Version 1.9 four-page report layout with numbered planning points on page 3 and references/methods on page 4. Arithmetic/source years/private-record separation remain unchanged.

Release validation: desktop 1440px and mobile 390px browser checks passed; no horizontal overflow or Streamlit exceptions. PDF downloaded through the running release app verified four pages, planning heading page 3, references page 4, and no visible full URLs in the first three pages. Prior 210 report-combination validation passed. Public Streamlit verification is blocked by this environment's HTTP policy (403); push does not establish that the cloud rebuild finished.

Full regression suite: 118 tests passed in 152.634 seconds, no failures. Existing Streamlit API deprecation warnings remain outside this release scope.
