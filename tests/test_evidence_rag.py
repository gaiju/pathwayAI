import ast
import json
from pathlib import Path
import re
import unittest

from evidence_rag import search_evidence, source_list, validate_answer_citations


class EvidenceTests(unittest.TestCase):
    def test_cost_retrieval_and_provenance(self):
        result = search_evidence("economic burden medical costs productivity OOP")
        items = {item["source_id"]: item for item in result["items"]}
        self.assertIn("HOOK-2022", items)
        self.assertIn("YU-2026", items)
        self.assertEqual(items["HOOK-2022"]["dollar_year"], 2016)
        self.assertEqual(items["YU-2026"]["dollar_year"], 2022)
        self.assertIn("verification pending", items["YU-2026"]["verification_status"])
        self.assertIn("not an additional amount", items["HOOK-2022"]["passage"])

    def test_surveillance_limitations(self):
        items = search_evidence("county surveillance residence exposure risk")["items"]
        cdc = next(item for item in items if item["source_id"] == "CDC-SURVEILLANCE")
        self.assertIn("not individual", cdc["passage"])
        self.assertTrue(cdc["url"].startswith("https://www.cdc.gov/"))

    def test_abstains_on_unrelated_empty_or_generic_query(self):
        for query in ("", "Lyme disease", "quantum computing zzzzz", "CDC diagnostic testing antibodies"):
            with self.subTest(query=query):
                result = search_evidence(query)
                self.assertEqual(result["status"], "insufficient_evidence")
                self.assertEqual(result["items"], [])

    def test_unknown_and_missing_citations_fail(self):
        result = search_evidence("societal productivity")
        self.assertFalse(validate_answer_citations("unsupported [E:FAKE]", result)[0])
        self.assertFalse(validate_answer_citations("no citations", result)[0])
        self.assertTrue(validate_answer_citations("summary [E:HOOK-2022]", result)[0])
        self.assertIn("https://wwwnc.cdc.gov/", source_list(result))

    def test_agent_integration_without_network_or_patient_data(self):
        # Exercise the real orchestration in isolation from Streamlit's UI.
        tree = ast.parse(Path("app.py").read_text())
        functions = [node for node in tree.body if isinstance(node, ast.FunctionDef)
                     and node.name == "run_strategy_agent"]
        from evidence_rag import validate_answer_citations, source_list
        for answer, expected in (("Societal costs include work [E:HOOK-2022]", "connected"),
                                 ("Invented evidence [E:FAKE]", "citation_error")):
            calls = []
            def request(system, user):
                calls.append((system, user))
                return (json.dumps({"tools": ["search_pathwayai"], "reason": "test"})
                        if len(calls) == 1 else answer), None
            namespace = dict(re=re, json=json, _openai_text_request=request,
                             simple_reading_view=lambda: True,
                             validate_answer_citations=validate_answer_citations,
                             source_list=source_list,
                             AGENT_TOOL_MAP={"search_pathwayai": lambda q: {"current_app": {}},
                                             "search_evidence": search_evidence})
            exec(compile(ast.Module(body=functions, type_ignores=[]), "app.py", "exec"), namespace)
            output, meta = namespace["run_strategy_agent"]("societal productivity costs")
            self.assertEqual(meta["state"], expected)
            self.assertEqual(len(calls), 2)
            self.assertIn("Use familiar words", calls[1][0])
            self.assertIn("search_evidence", meta["selected_tools"])
            bundle = json.loads(calls[1][1])
            self.assertIn("HOOK-2022", str(bundle["tool_results"]))
            self.assertEqual(output is None, expected == "citation_error")


if __name__ == "__main__":
    unittest.main()
