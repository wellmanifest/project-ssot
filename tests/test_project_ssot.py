from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

import project_ssot as pack


ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples"


def _load(name: str) -> dict:
    return json.loads((EXAMPLES / name).read_text(encoding="utf-8"))


class ClassifyTests(unittest.TestCase):
    def test_ssot_pack_homes_in_wellmanifest_as_domain_pack(self) -> None:
        document = pack.classify(_load("ssot-pack.interview.json"), _load("ssot-pack.evidence.json"))
        self.assertEqual(document["placement"]["home"], "wellmanifest")
        self.assertEqual(document["placement"]["shape"], "domain_pack")
        self.assertEqual(document["placement"]["runtimeOwner"], "wellmanifest")
        self.assertIn("wellmanifest/dsl", document["placement"]["adopt"])
        self.assertTrue(document["policy"]["adoptDoesNotImplyHome"])
        self.assertTrue(document["policy"]["descriptionIsProjection"])
        self.assertEqual(document["policy"]["effectModel"], "propose-only")
        self.assertEqual(document["policy"]["unknownPolicy"], "reject")
        self.assertFalse(document["policy"]["analyzerTreatAsDebtUntilInterview"])
        self.assertIn("crawl_live_repository", document["policy"]["forbid"])
        kinds = {item["kind"] for item in document["relations"]}
        self.assertIn("facade", kinds)
        self.assertIn("allowed_divergence", kinds)
        self.assertIn("generated_mirror", kinds)
        analyzer = [item for item in document["evidence"] if item["kind"] == "analyzer-map"]
        self.assertEqual(analyzer[0]["role"], "evidence")
        self.assertEqual(pack.validate_decision(document), [])

    def test_adopt_wellmanifest_does_not_force_home(self) -> None:
        document = pack.classify(_load("widget.interview.json"), _load("widget.evidence.json"))
        self.assertEqual(document["placement"]["home"], "subactor")
        self.assertEqual(document["placement"]["shape"], "runtime_service")
        self.assertIn("wellmanifest/dsl", document["placement"]["adopt"])
        self.assertIn("wellmanifest/logs", document["placement"]["adopt"])
        self.assertEqual(document["packaging"]["kind"], "pip")
        self.assertEqual(pack.validate_decision(document), [])

    def test_unresolved_purpose_conflict_fails_closed(self) -> None:
        document = pack.classify(None, _load("ssot-pack.evidence.json"))
        findings = pack.validate_decision(document)
        codes = {item.code for item in findings}
        self.assertIn("PROJECT-CONFLICT-001", codes)
        self.assertTrue(document["questions"])

    def test_interview_resolves_readme_vs_schema_purpose(self) -> None:
        document = pack.classify(_load("ssot-pack.interview.json"), _load("ssot-pack.evidence.json"))
        self.assertEqual(
            document["purpose"],
            "Interview-driven classification of duplicated trees into propose-only SSOT decisions",
        )
        conflict = next(item for item in document["conflicts"] if item["field"] == "purpose")
        self.assertEqual(conflict["resolvedBy"], "interview")
        self.assertEqual(pack.validate_decision(document), [])

    def test_analyzer_identity_facts_are_noise(self) -> None:
        evidence = _load("ssot-pack.evidence.json")
        evidence["sources"][-1]["facts"] = {"purpose": "analyzer invented this purpose"}
        findings = pack.validate_evidence_index(evidence)
        self.assertIn("PROJECT-NOISE-001", {item.code for item in findings})

    def test_intent_json_is_typed_evidence_not_a_crawl(self) -> None:
        ingested = pack.ingest_typed(_load("widget.intent.json"), "intent.json")
        self.assertEqual(ingested["kind"], "evidence")
        payload = ingested["payload"]
        self.assertEqual(payload["sources"][0]["kind"], "intent")
        self.assertEqual(payload["sources"][0]["facts"]["placement"]["home"], "subactor")
        self.assertEqual(payload["sources"][0]["facts"]["placement"]["shape"], "runtime_service")
        document = pack.classify(_load("widget.interview.json"), payload)
        self.assertEqual(document["placement"]["home"], "subactor")
        self.assertEqual(pack.validate_decision(document), [])

    def test_interview_uses_placement_not_toplevel_home(self) -> None:
        answers = _load("ssot-pack.interview.json")
        self.assertIn("placement", answers)
        self.assertNotIn("home", answers)
        self.assertNotIn("runtimeOwner", answers)
        findings = pack.validate_interview(answers)
        self.assertEqual(findings, [])

    def test_wellmanifest_plus_both_is_allowed(self) -> None:
        answers = _load("ssot-pack.interview.json")
        answers["placement"] = {
            "home": "wellmanifest",
            "shape": "both",
            "runtimeOwner": "wellmanifest",
            "adopt": ["wellmanifest/dsl"],
        }
        document = pack.classify(answers, None)
        self.assertEqual(document["placement"]["shape"], "both")
        codes = {item.code for item in pack.validate_decision(document)}
        self.assertNotIn("PROJECT-HOME-001", codes)

    def test_runtime_service_plus_wellmanifest_matches_governance(self) -> None:
        answers = _load("widget.interview.json")
        answers["placement"]["home"] = "wellmanifest"
        answers["placement"]["runtimeOwner"] = "wellmanifest"
        document = pack.classify(answers, None)
        codes = {item.code for item in pack.validate_decision(document)}
        self.assertIn("PROJECT-HOME-001", codes)


class ValidateTests(unittest.TestCase):
    def test_runtime_service_cannot_home_in_wellmanifest(self) -> None:
        codes = {item.code for item in pack.validate_decision(_load("invalid/runtime-home-wellmanifest.project.json"))}
        self.assertIn("PROJECT-HOME-001", codes)

    def test_readme_must_not_be_authority(self) -> None:
        codes = {item.code for item in pack.validate_decision(_load("invalid/readme-as-authority.project.json"))}
        self.assertIn("PROJECT-README-001", codes)

    def test_analyzer_must_not_be_debt(self) -> None:
        codes = {item.code for item in pack.validate_decision(_load("invalid/analyzer-as-debt.project.json"))}
        self.assertIn("PROJECT-NOISE-001", codes)

    def test_missing_purpose_fails(self) -> None:
        codes = {item.code for item in pack.validate_decision(_load("invalid/missing-purpose.project.json"))}
        self.assertIn("PROJECT-PURPOSE-001", codes)

    def test_unknown_field_rejected(self) -> None:
        document = pack.classify(_load("widget.interview.json"), _load("widget.evidence.json"))
        document["surprise"] = True
        codes = {item.code for item in pack.validate_decision(document)}
        self.assertIn("PROJECT-KIND-001", codes)


class ProjectionTests(unittest.TestCase):
    def test_suggest_emits_document_project(self) -> None:
        document = pack.classify(_load("ssot-pack.interview.json"), _load("ssot-pack.evidence.json"))
        text = pack.render_dsl(document)
        self.assertTrue(text.startswith("DOCUMENT PROJECT"))
        self.assertIn("HOME wellmanifest", text)
        self.assertIn("SHAPE domain_pack", text)
        self.assertIn("ADOPT wellmanifest/dsl", text)
        self.assertIn("KIND facade", text)
        self.assertIn("KIND allowed_divergence", text)
        parsed = pack.parse_dsl(text)
        self.assertEqual(parsed["id"], document["id"])
        self.assertEqual(parsed["placement"]["home"], "wellmanifest")
        self.assertEqual(parsed["placement"]["shape"], "domain_pack")
        self.assertEqual(
            [item["kind"] for item in parsed["relations"]],
            [item["kind"] for item in document["relations"]],
        )
        self.assertEqual(pack.validate_decision(parsed), [])


class CliTests(unittest.TestCase):
    def test_questions_lists_catalog(self) -> None:
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            code = pack.main(["questions"])
        self.assertEqual(code, 0)
        output = buffer.getvalue()
        self.assertIn("subject_id", output)
        self.assertIn("home", output)
        self.assertIn("shape", output)
        self.assertIn("runtimeOwner", output)

    def test_classify_cli_json(self) -> None:
        buffer = io.StringIO()
        err = io.StringIO()
        with redirect_stdout(buffer), redirect_stderr(err):
            code = pack.main(
                [
                    "classify",
                    str(EXAMPLES / "ssot-pack.interview.json"),
                    "--evidence",
                    str(EXAMPLES / "ssot-pack.evidence.json"),
                ]
            )
        self.assertEqual(code, 0, err.getvalue())
        document = json.loads(buffer.getvalue())
        self.assertEqual(document["schema"], pack.SCHEMA_DOCUMENT)
        self.assertEqual(document["placement"]["home"], "wellmanifest")

    def test_suggest_cli_dsl(self) -> None:
        buffer = io.StringIO()
        err = io.StringIO()
        with redirect_stdout(buffer), redirect_stderr(err):
            code = pack.main(
                [
                    "suggest",
                    str(EXAMPLES / "ssot-pack.interview.json"),
                    "--evidence",
                    str(EXAMPLES / "ssot-pack.evidence.json"),
                ]
            )
        self.assertEqual(code, 0, err.getvalue())
        self.assertTrue(buffer.getvalue().startswith("DOCUMENT PROJECT"))

    def test_validate_cli_ok(self) -> None:
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            code = pack.main(["validate", str(EXAMPLES / "ssot-pack.project.json")])
        self.assertEqual(code, 0)
        self.assertEqual(buffer.getvalue().strip(), "ok")

    def test_golden_examples_pass(self) -> None:
        self.assertEqual(pack.validate_decision(_load("ssot-pack.project.json")), [])
        self.assertEqual(pack.validate_decision(_load("widget.project.json")), [])

    def test_validate_cli_rejects_runtime_home(self) -> None:
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            code = pack.main(
                ["validate", str(EXAMPLES / "invalid/runtime-home-wellmanifest.project.json")]
            )
        self.assertEqual(code, 1)
        self.assertIn("PROJECT-HOME-001", buffer.getvalue())


class DigestBindTests(unittest.TestCase):
    def test_dsl_manifest_digests_match_files(self) -> None:
        manifest_path = ROOT / "dsl-manifest.json"
        if not manifest_path.exists():
            self.skipTest("dsl-manifest.json not written yet")
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        self.assertEqual(manifest["semantics"]["effectModel"], "propose-only")
        self.assertEqual(manifest["semantics"]["unknownPolicy"], "reject")
        import hashlib

        for artifact in manifest["artifacts"]:
            path = ROOT / artifact["path"]
            digest = "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()
            self.assertEqual(digest, artifact["digest"], artifact["path"])


if __name__ == "__main__":
    unittest.main()
