"""Small, public-only evidence retriever; no network, secrets or patient files.

The initial passages are editorial summaries migrated from app.py, not quotes
from independently verified publications. See RAG_EVIDENCE.md before extending.
"""

import math
import re
from collections import Counter


def _passage(source_id, title, url, year, section, text, limitation,
             perspective=None, dollar_year=None, evidence_type="public evidence"):
    return {
        "source_id": source_id, "source": title, "url": url,
        "publication_year": year, "section": section, "passage": text,
        "limitation": limitation, "cost_perspective": perspective,
        "dollar_year": dollar_year, "evidence_type": evidence_type,
        "content_type": "editorial summary, not a verbatim source excerpt",
        "verification_status": "Existing application summary; primary source verification pending",
        "source_checked_on": None,
    }


# Explicit immutable-in-practice public corpus: never scan arbitrary folders.
PASSAGES = (
    _passage("CDC-SURVEILLANCE", "CDC Lyme disease surveillance",
             "https://www.cdc.gov/lyme/data-research/facts-stats/index.html",
             None, "Reported-case interpretation",
             "Reported Lyme disease cases describe surveillance by county of residence, "
             "not necessarily the county of exposure. Historical 2019–2022 county "
             "records are context, not individual infection risk or current incidence.",
             "Surveillance counts do not establish personal risk or local prevalence."),
    _passage("CDC-TICKS", "CDC blacklegged tick surveillance",
             "https://www.cdc.gov/ticks/data-research/facts-stats/blacklegged-tick-surveillance.html",
             None, "Distribution interpretation",
             "Established or reported blacklegged tick distribution status is not "
             "tick density. Historical sampling periods must stay labeled; tick "
             "observations do not predict a person's infection risk.",
             "Distribution, density, pathogen findings and human cases are different measures."),
    _passage("HOOK-2022", "Hook et al., Emerging Infectious Diseases 2022",
             "https://wwwnc.cdc.gov/eid/article/28/6/21-1335_article",
             2022, "Table 5: societal cost perspective",
             "Lyme disease economic burden research in high-incidence areas includes "
             "medical, nonmedical and productivity costs. Patient medical spending "
             "is already part of societal cost, not an additional amount to add. "
             "Localized and disseminated study groups are observational comparisons.",
             "Not a Dutchess County estimate, pre-diagnosis-only cost, personal prediction "
             "or evidence of savings caused by earlier diagnosis. Verify the original table "
             "before using numerical estimates.", "societal", 2016,
             "published research reference"),
    _passage("YU-2026", "Yu et al., JAMA Network Open 2026 (application reference)",
             "https://jamanetwork.com/journals/jamanetworkopen/fullarticle/2843880",
             2026, "Table 2: medical episode and recorded patient OOP",
             "Lyme disease medical episode cost research distinguishes total direct "
             "medical spending from patient out-of-pocket (OOP) spending. The recorded "
             "OOP subset is a separate denominator. Pharmacy costs are excluded. "
             "Localized and disseminated groups are not predictions of patient progression.",
             "Publication details and tables require primary-source verification. "
             "Do not add OOP to total medical spending or combine these episode costs "
             "with Hook societal costs in a different dollar year.",
             "direct medical episode; patient medical OOP separately", 2022,
             "published research reference"),
    _passage("HORN-2025", "Horn et al., Frontiers in Medicine 2025",
             "https://www.frontiersin.org/journals/medicine/articles/10.3389/fmed.2025.1577936/full",
             2025, "Lyme Disease Biobank follow-up",
             "Selected Lyme Disease Biobank returning participants provide evidence "
             "about continuing symptoms and follow-up care gaps, not a cost valuation.",
             "Selected follow-up participants do not establish county risk, personal "
             "prognosis or ongoing infection.", evidence_type="published research reference"),
    _passage("NYSDOH-TICKS", "NYSDOH tick surveillance",
             "https://health.data.ny.gov/resource/kibp-u2ip.json",
             None, "County sampling observations",
             "Observed county-level nymph tick population density and B. burgdorferi "
             "surveillance describe sampled exposure context where available.",
             "A sampling-site observation is not county-wide exposure or individual risk."),
    _passage("HRSA-AHRF", "HRSA AHRF 2024–2025",
             "https://data.hrsa.gov/topics/health-workforce/nchwa/ahrf",
             None, "County healthcare capacity",
             "County population, primary-care and emergency physician counts, hospitals "
             "and beds provide healthcare capacity context.",
             "Counts do not measure appointment availability or verify Lyme expertise."),
    _passage("PATHWAYAI-SURVEY", "PathwayAI pilot survey aggregate summary",
             None, None, "Previously supplied aggregate snapshot",
             "Aggregate pilot survey themes include diagnostic delay, clinicians seen, "
             "out-of-pocket burden and work or function. This national convenience "
             "sample stays separate from county prevalence.",
             "Not peer-reviewed research. Reporting periods and denominators require "
             "confirmation; no patient-level records are retrieved.",
             evidence_type="patient-reported aggregate project evidence"),
)

_STOP = set("a an the and or of for to in on is are was were be by with from "
            "what how does do can could should would tell me about explain evidence "
            "research study studies lyme disease please my i it this that".split())
_ALIASES = {"economic": "cost", "economics": "cost", "costs": "cost",
            "spending": "cost", "expenses": "cost", "productivity": "work",
            "ticks": "tick", "cases": "case", "citations": "citation"}


def _tokens(text):
    return [_ALIASES.get(word, word) for word in
            re.findall(r"[a-z0-9]+", text.lower()) if word not in _STOP]


def search_evidence(query, max_results=5):
    """BM25 over bounded, authored passages; zero matches never return evidence."""
    query_terms = set(_tokens(query or ""))
    # There are no verified clinical guidance passages in the initial bundle.
    # A surveillance or diagnostic-delay match must not masquerade as guidance.
    clinical_terms = {"testing", "antibodies", "antibody", "antibiotic", "antibiotics",
                      "prophylaxis", "treatment", "elisa", "immunoblot", "serology"}
    if query_terms & clinical_terms:
        return {"tool": "curated evidence", "status": "insufficient_evidence", "items": [],
                "note": "Verified CDC clinical guidance is not loaded. Do not infer testing, "
                        "prevention medication or treatment guidance from surveillance or cost summaries."}
    documents = [Counter(_tokens(" ".join(str(p.get(key) or "") for key in
                 ("source", "section", "passage", "limitation")))) for p in PASSAGES]
    lengths = [sum(doc.values()) for doc in documents]
    average = sum(lengths) / len(lengths)
    ranked = []
    for index, doc in enumerate(documents):
        score = 0.0
        for term in query_terms:
            frequency = doc[term]
            if not frequency:
                continue
            document_frequency = sum(term in other for other in documents)
            idf = math.log(1 + (len(documents) - document_frequency + .5) /
                           (document_frequency + .5))
            score += idf * frequency * 2.2 / (
                frequency + 1.2 * (.25 + .75 * lengths[index] / average))
        if score > 0:
            ranked.append((score, index))
    ranked.sort(key=lambda item: (-item[0], item[1]))
    items = [dict(PASSAGES[index], retrieval_score=round(score, 4))
             for score, index in ranked[:max(0, min(max_results, 5))]]
    return {
        "tool": "curated evidence", "status": "ok" if items else "insufficient_evidence",
        "items": items,
        "note": "Retrieved editorial summaries are not verified primary-source passages. "
                "No new clinical guidance or numerical estimates are established. "
                "Missing evidence must be reported, not filled from model memory.",
    }


def validate_answer_citations(answer, evidence):
    """Check IDs, not factual entailment; human review remains necessary."""
    ids = set(re.findall(r"\[E:([^\]\n]+)\]", answer or ""))
    allowed = {item["source_id"] for item in evidence.get("items", [])}
    if ids - allowed:
        return False, "The generated answer cited evidence that was not retrieved."
    if allowed and not ids:
        return False, "The generated answer omitted retrieved-evidence citations."
    return True, ""


def source_list(evidence):
    lines = ["\n\n**Retrieved evidence provenance**"]
    for item in evidence.get("items", []):
        title = item["source"]
        reference = f"[{title}]({item['url']})" if item["url"] else title
        lines.append(f"- [E:{item['source_id']}] {reference} — {item['section']}. "
                     f"{item['verification_status']}.")
    return "\n".join(lines) if evidence.get("items") else ""
