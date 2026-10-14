# Live release — October 14, 2026

This release promotes the tested PathwayAI version to `main`, including the
revised landing copy, four public pathways, private personal records, Lyme
testing education, county comparisons and cost illustrations, survey link,
community-pilot invitation and public-only evidence retrieval.

Streamlit configuration:

- Repository: `gaiju/pathwayAI`
- Branch: `main`
- Main file: `app.py` (lowercase)
- Existing Streamlit secrets remain in the app settings. No secrets are added
  to the repository or replaced by this release.

The legacy `APP.py` remains unchanged; it is not this release's entrypoint.
Deploy the complete repository, including modules, images and data files.

Validation: all 24 tests passed. AppTest also rendered the updated landing
copy and all four public pathways, including return navigation. These checks
do not establish clinical effectiveness, measured savings or a completed
secure shared-reporting service. Collection remains disabled by default;
review live environment configuration before enabling any collection pilot.

The previous `main` revision is preserved as
`pathwayai-before-live-2026-10-14` (commit
`639450c9eb939a704444afa2bc98a5e283b5a3fc`). A Streamlit deployment can be pointed
at that tag temporarily if a rollback is needed, or the release can be reverted
through a reviewed Git change. Do not overwrite secrets during rollback.

The known public URL is https://pathwayai.streamlit.app/ . Git publication is
separate from live Streamlit readiness. This environment cannot inspect the
live app's branch/entrypoint settings or reboot it. Confirm those settings,
allow Streamlit to redeploy, and check the updated landing text. The test app
remains https://pathwayaitest.streamlit.app/ on `rag-test`.
