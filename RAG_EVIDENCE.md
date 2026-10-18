# Research & Strategy Agent evidence

The lowercase `app.py` entrypoint uses `evidence_rag.py`. The old uppercase
entrypoint has been removed to avoid case-insensitive filename collisions. No hosted index, embedding service, API key, or new dependency
is required. The local corpus is retrieved on every strategy request; existing
planner-selected tools and optional live research remain available.

The corpus consists of editorial summaries, **not verbatim quotations**.
On October 14, 2026, Hook 2022 Methods, Results and Discussion were checked
against the user-supplied public article text. Its bounded summary now includes
the checked societal and patient-burden figures, their separate denominators,
2016 dollar year and limitations. Linked tables were not separately retrieved.
Verification metadata is recorded in `data/hook_2022_article_verification.json`.
Other sources retain their own pending verification status; in particular,
the Yu 2026 reference still requires original-table review. Live source access
was blocked by the network proxy. Clinical testing guidance remains absent.
Retrieval never updates patient guidance or application calculations.

Horn 2025 was subsequently checked against the supplied full public paper PDF
(Methods, Results, Table 5 and Limitations). Its summary distinguishes 466
enrolled cases, 253 returners, 55 reporting ongoing symptoms and the treated
subgroup (47 of 226). The selected approximately three-month outcome is not a
county long-Lyme/PTLDS rate or an incremental-cost measurement. Verification
metadata is in `data/horn_2025_publication_verification.json`. The participant
workbook, IDs, comments and private analyses are not part of the corpus or
public repository. Observational antibiotic patterns do not modify clinical
guidance or get added to the baseline medical cost.

To expand the collection, inspect the authoritative source first. Add bounded
public passages with a stable source ID, title, canonical URL, publication or
update date, section/table, study population, cost perspective, dollar year,
and limitations. Distinguish quotations from editorial summaries. Record the
source check date and verification status only after inspecting the source.
Recommended additions are CDC diagnosis/testing and prevention guidance,
verified Hook Table 5 and Yu Table 2 passages and their methods/limitations.
Do not import patient stories, Community Voice records, credentials, arbitrary
uploads, or private HHS/project notes into this public evidence corpus.

BM25 ranks authored passages locally. Generic or unmatched questions return
`insufficient_evidence`; partial matches do not imply full question coverage.
The answer prompt requires citations and evidence gaps. A runtime check rejects
unknown curated citation IDs and answers omitting all curated citations, with
no additional paid retry. It does not prove every claim is supported or detect
every missing citation. Human source review remains required. A deterministic
provenance list is appended to accepted answers. Live-web citations remain
separate and provisional.

Existing secret loading, admin access, story AI opt-in, `store=False`, quota
reservations, patient-data handling, and consent rules are unchanged.

Run the focused checks from the checkout:

```sh
python -m unittest discover -s tests -v
```

Before external use, review responses about surveillance versus personal risk,
medical versus societal versus OOP cost, different dollar years, unsupported
diagnostic-delay savings, missing clinical guidance, and irrelevant questions.
Test live synthesis with the configured model, including citation failures.
