#!/usr/bin/env python3
"""Project SSOT interview, composition, and propose-only DSL emission.

This is a domain pack on wellmanifest/dsl. Canonical documents are JSON AST
conforming to wellmanifest.project-ssot/v1. DOCUMENT PROJECT is a projection.

The pack composes already-typed JSON (interview answers, intent.json,
dsl-manifest mappings, a listed evidence index). It does not crawl a live
repository. A later generator in semcod/code2llm may produce the index.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


SCHEMA_DOCUMENT = "wellmanifest.project-ssot/v2"
SCHEMA_DOCUMENT_V1 = "wellmanifest.project-ssot/v1"
SCHEMA_DOCUMENTS = (SCHEMA_DOCUMENT, SCHEMA_DOCUMENT_V1)
SCHEMA_INTERVIEW = "wellmanifest.project-ssot/interview/v1"
SCHEMA_EVIDENCE = "wellmanifest.project-ssot/evidence-index/v1"
SCHEMA_CHECK = "wellmanifest.project-ssot/check-result/v1"
IDENTIFIER = re.compile(r"^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$")
SEMVER = re.compile(
    r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)"
    r"(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$"
)
RELATIVE_PATH = re.compile(r"^(?!/)(?!.*(?:^|/)\.\.(?:/|$))(?!.*\\).+$")
ADOPT_ID = re.compile(r"^wellmanifest/[a-z0-9][a-z0-9-]*$")
DIGEST = re.compile(r"^sha256:[a-f0-9]{64}$")

HOME_ID = re.compile(r"^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$")

#: Fallback used only when registry/homes.json is unreadable. HOME is deliberately
#: NOT a closed enum: a standard whose schema hardcodes its own adopters cannot be
#: adopted by a fourth party. An unknown-but-well-formed home is a warning.
DEFAULT_HOMES = ("wellmanifest", "subactor", "semcod", "autogrammar")


def load_homes(path: Path | None = None) -> set[str]:
    """Known placement HOMEs, from registry/homes.json."""
    target = path or (repo_root() / "registry" / "homes.json")
    try:
        document = load_json(target)
        homes = {
            str(entry["id"])
            for entry in document.get("homes", [])
            if isinstance(entry, Mapping) and entry.get("id")
        }
        return homes or set(DEFAULT_HOMES)
    except (OSError, ValueError, KeyError, TypeError):
        return set(DEFAULT_HOMES)


HOMES = set(DEFAULT_HOMES)
SHAPES = {"domain_pack", "runtime_service", "both"}
CAPABILITY_VERBS = {
    "analyze", "audit", "discover", "index", "query",
    "generate", "transform", "convert", "document", "package",
    "validate", "test", "lint", "repair", "refactor",
    "plan", "orchestrate", "execute", "schedule",
    "deploy", "serve", "monitor", "publish", "sync",
}
CAPABILITY_IO_KINDS = {
    "directory", "repository", "file", "json", "yaml", "markdown",
    "sqlite", "protobuf", "http", "stream", "stdout", "database", "other",
}
ENTRYPOINT_KINDS = {"cli", "module", "http", "library", "make", "script"}
INSTALL_STATUSES = {"pypi", "npm", "binary", "src-only", "container", "none"}
MATURITY_LEVELS = {"experimental", "beta", "stable", "maintenance", "deprecated"}
SIBLING_RELATIONS = {
    "invokes", "extends", "overlaps", "superseded-by", "supersedes",
    "exports-to", "facade-of", "depends-on", "alternative-to",
}
PLACEMENT_KEYS = {"home", "shape", "runtimeOwner", "adopt"}
README_ROLES = {"facade", "generated_mirror", "allowed_divergence", "unknown"}
ANALYZER_KINDS = {"code2llm-toon", "map-toon-yaml", "redup", "other", "none"}
ANALYZER_SOURCES = {"analyzer-toon", "analyzer-map"}
SOURCE_KINDS = {
    "interview",
    "intent",
    "ticket",
    "governance-manifest",
    "agents",
    "dsl-manifest",
    "readme",
    "docs",
    "schema",
    "ssot-decision",
    "analyzer-toon",
    "analyzer-map",
    "pyproject",
    "package-json",
    "other",
}
PRECEDENCE = {
    "interview": 100,
    "intent": 85,
    "ticket": 82,
    "governance-manifest": 80,
    "agents": 78,
    "dsl-manifest": 70,
    "ssot-decision": 60,
    "schema": 55,
    "docs": 50,
    "readme": 48,
    "pyproject": 40,
    "package-json": 40,
    "other": 20,
    "analyzer-toon": 10,
    "analyzer-map": 10,
}
AUTHORITY_KINDS = {
    "interview",
    "intent",
    "ticket",
    "governance-manifest",
    "agents",
    "dsl-manifest",
    "ssot-decision",
    "schema",
}
PACKAGING_KINDS = {"none", "pip", "npm", "other"}
IDENTITY_FIELDS = (
    "id",
    "name",
    "version",
    "home",
    "shape",
    "runtimeOwner",
    "purpose",
)
FACT_KEYS = {
    "id",
    "name",
    "version",
    "placement",
    "home",
    "shape",
    "runtimeOwner",
    "purpose",
    "owners",
    "adopted",
    "languages",
    "packaging",
}
SSOT_KINDS = {"generated_mirror", "facade", "allowed_divergence"}
RELATIONS_MAP = {"extends", "implements", "maps-to", "compatible-with"}
OWNER_KINDS = {"repository", "organization", "team", "person"}
FORBIDS = {
    "treat_readme_as_authority",
    "treat_analyzer_as_debt",
    "infer_home_from_adopt",
    "runtime_service_in_wellmanifest",
    "keep_competing_readme_authority",
    "crawl_live_repository",
    "copy_adopted_standard",
}
ACTIONS = {
    "use_document_as_ssot",
    "generate_readme_from_document",
    "keep_readme_as_facade",
    "document_known_divergent",
    "ask_clarifying_questions",
    "ignore_analyzer_until_interview",
    "map_adopted_standard",
    "record_evidence_digest",
}
REQUIRED_FORBIDS = (
    "treat_readme_as_authority",
    "treat_analyzer_as_debt",
    "infer_home_from_adopt",
    "runtime_service_in_wellmanifest",
    "crawl_live_repository",
    "copy_adopted_standard",
)
INTENT_SCHEMAS = {"new-project.intent/v2", "new-project.intent/v3"}
PURPOSE_QUESTION = (
    "Evidence sources disagree on the one-sentence purpose. Which source is "
    "authoritative (dsl-manifest, intent, interview), or what is the resolved "
    "sentence?"
)
HOME_QUESTION = (
    "placement.home is not stated. Adopting wellmanifest/* MUST NOT imply "
    "home=wellmanifest (\"w ramach wellmanifest\" means ADOPT, not HOME). "
    "Which org HOMEs this repository: wellmanifest, subactor, or semcod?"
)
README_QUESTION = (
    "README exists beside this document. Is it a facade, a generated mirror, "
    "or allowed marketing divergence from the schema purpose?"
)


class Finding:
    def __init__(self, code: str, message: str, path: str = "$") -> None:
        self.code = code
        self.message = message
        self.path = path

    def as_dict(self) -> dict[str, str]:
        return {"code": self.code, "path": self.path, "message": self.message}


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def dump_json(document: Mapping[str, Any]) -> str:
    return json.dumps(document, indent=2, ensure_ascii=False, sort_keys=False) + "\n"


def _is_identifier(value: Any) -> bool:
    return isinstance(value, str) and bool(IDENTIFIER.fullmatch(value))


def _is_semver(value: Any) -> bool:
    return isinstance(value, str) and bool(SEMVER.fullmatch(value))


def _is_path(value: Any) -> bool:
    return isinstance(value, str) and 0 < len(value) <= 500 and bool(
        RELATIVE_PATH.fullmatch(value)
    )


def _is_digest(value: Any) -> bool:
    return isinstance(value, str) and bool(DIGEST.fullmatch(value))


def _is_adopt_id(value: Any) -> bool:
    return isinstance(value, str) and bool(ADOPT_ID.fullmatch(value))


def load_questionnaire(path: Path | None = None) -> dict[str, Any]:
    questionnaire = path or repo_root() / "questions" / "interview.json"
    return load_json(questionnaire)


def _as_bool(raw: str) -> bool:
    value = raw.strip().lower()
    if value in {"y", "yes", "true", "1"}:
        return True
    if value in {"n", "no", "false", "0"}:
        return False
    raise ValueError(f"expected yes/no, got {raw!r}")


def _as_list(raw: str) -> list[str]:
    return [part.strip() for part in raw.split(",") if part.strip()]


def parse_answer(question: Mapping[str, Any], raw: str) -> Any:
    kind = question["type"]
    text = raw.strip()
    if not text:
        if question.get("required"):
            raise ValueError(f"{question['id']} is required")
        return None
    if kind == "bool":
        return _as_bool(text)
    if kind == "identifier":
        value = text.replace(" ", "-").lower()
        if not _is_identifier(value):
            raise ValueError(f"{question['id']} must be a stable identifier")
        return value
    if kind in {"string-list", "path-list", "enum-list"}:
        items = _as_list(text)
        choices = question.get("choices")
        if choices:
            unknown = [item for item in items if item not in choices]
            if unknown:
                raise ValueError(f"{question['id']} unknown values: {unknown}")
        return items
    if kind == "enum":
        if text not in question.get("choices", []):
            raise ValueError(f"{question['id']} must be one of {question['choices']}")
        return text
    return text


def interview_from_answers(answers: Mapping[str, Any]) -> dict[str, Any]:
    document = dict(answers)
    document.setdefault("schema", SCHEMA_INTERVIEW)
    return normalize_interview(document)


def normalize_interview(answers: Mapping[str, Any]) -> dict[str, Any]:
    """Nest new-project placement. Interactive questions stay flat, then fold here."""

    document = dict(answers)
    document.setdefault("schema", SCHEMA_INTERVIEW)
    if isinstance(document.get("placement"), dict):
        for key in ("home", "shape", "runtimeOwner", "adopt"):
            document.pop(key, None)
        return document
    placement: dict[str, Any] = {}
    for key in ("home", "shape", "runtimeOwner"):
        if key in document:
            placement[key] = document.pop(key)
    if "adopt" in document:
        placement["adopt"] = document.pop("adopt")
    if placement:
        document["placement"] = placement
    return document


def interview_placement(answers: Mapping[str, Any]) -> dict[str, Any]:
    normalized = normalize_interview(answers)
    placement = normalized.get("placement")
    return dict(placement) if isinstance(placement, dict) else {}


def placement_findings(value: Any, path: str = "$.placement") -> list[Finding]:
    """Same closed checks as new-project governance_check.placement_error."""

    required = {"home", "shape"}
    allowed = required | {"runtimeOwner", "adopt"}
    if not isinstance(value, dict) or not required <= set(value) or not set(value) <= allowed:
        return [Finding("PROJECT-HOME-001", "placement must contain home and shape", path)]
    findings: list[Finding] = []
    home_value = value["home"]
    if not isinstance(home_value, str) or not HOME_ID.match(home_value):
        findings.append(Finding("PROJECT-HOME-001", "placement home is not a well-formed id", f"{path}.home"))
    elif home_value not in load_homes():
        findings.append(
            Finding(
                "PROJECT-HOME-002",
                f"home {home_value!r} is not in registry/homes.json; add it there rather than editing schemas",
                f"{path}.home",
            )
        )
    if value["shape"] not in SHAPES:
        findings.append(Finding("PROJECT-SHAPE-001", "placement shape is invalid", f"{path}.shape"))
    runtime_owner = value.get("runtimeOwner")
    if runtime_owner is not None and runtime_owner not in HOMES:
        findings.append(
            Finding("PROJECT-SHAPE-001", "placement runtimeOwner is invalid", f"{path}.runtimeOwner")
        )
    if value["home"] == "wellmanifest" and value["shape"] == "runtime_service":
        findings.append(
            Finding(
                "PROJECT-HOME-001",
                "runtime_service must not HOME wellmanifest; ADOPT packs from subactor or semcod",
                path,
            )
        )
    adopt = value.get("adopt")
    if adopt is not None and (
        not isinstance(adopt, list) or any(not _is_adopt_id(item) for item in adopt)
    ):
        findings.append(
            Finding("PROJECT-ADOPT-001", "placement adopt must be wellmanifest/<pack> ids", f"{path}.adopt")
        )
    return findings


def _facts_placement(facts: Mapping[str, Any]) -> dict[str, Any]:
    placement = facts.get("placement")
    if isinstance(placement, dict):
        return {key: placement[key] for key in ("home", "shape", "runtimeOwner") if placement.get(key)}
    return {
        key: facts[key]
        for key in ("home", "shape", "runtimeOwner")
        if facts.get(key)
    }


def dotted_standard(value: str) -> str:
    text = value.strip()
    if "/" in text:
        return text.replace("/", ".")
    return text


def slash_adopt(value: str) -> str:
    text = value.strip()
    if "/" in text:
        return text
    parts = text.split(".")
    if len(parts) >= 2:
        return f"{parts[0]}/{'-'.join(parts[1:])}"
    return text


def _normalize_adopted_item(item: Any) -> dict[str, str] | None:
    if isinstance(item, str) and item.strip():
        standard = dotted_standard(item)
        relation = "maps-to"
        result = {"standard": standard, "relation": relation}
        if _is_adopt_id(slash_adopt(item)):
            return result
        if IDENTIFIER.fullmatch(standard):
            return result
        return None
    if not isinstance(item, dict):
        return None
    standard = item.get("standard")
    if not isinstance(standard, str) or not standard.strip():
        return None
    relation = item.get("relation") or "maps-to"
    if relation not in RELATIONS_MAP:
        return None
    result = {"standard": dotted_standard(standard), "relation": relation}
    uri = item.get("uri")
    if isinstance(uri, str) and uri.strip():
        result["uri"] = uri.strip()
    return result


def _owner_from_id(raw: Any) -> dict[str, str] | None:
    if isinstance(raw, dict):
        kind = raw.get("kind")
        ident = raw.get("id")
        if kind in OWNER_KINDS and isinstance(ident, str) and ident.strip():
            return {"kind": kind, "id": ident.strip()}
        return None
    if isinstance(raw, str) and raw.strip():
        return {"kind": "repository", "id": raw.strip()}
    return None


def wrap_intent(document: Mapping[str, Any], path: str) -> dict[str, Any]:
    placement = document.get("placement") or {}
    facts: dict[str, Any] = {}
    if isinstance(document.get("summary"), str) and document["summary"].strip():
        facts["purpose"] = document["summary"].strip()
    if isinstance(placement, dict) and placement:
        facts["placement"] = {
            key: placement[key] for key in ("home", "shape", "runtimeOwner", "adopt") if key in placement
        }
        adopted = placement.get("adopt") or []
        if isinstance(adopted, list) and adopted:
            facts["adopted"] = list(adopted)
    subject = document.get("workstream") or document.get("ticket") or "intent"
    if isinstance(subject, str):
        subject = subject.replace("_", "-").lower()
        if not _is_identifier(subject):
            subject = "intent"
    rel = path if _is_path(path) else "intent.json"
    return {
        "schema": SCHEMA_EVIDENCE,
        "subject_id": subject,
        "sources": [
            {
                "id": "intent",
                "kind": "intent",
                "path": rel,
                "facts": facts,
            }
        ],
    }


def wrap_dsl_manifest(document: Mapping[str, Any], path: str) -> dict[str, Any]:
    facts: dict[str, Any] = {}
    for key in ("id", "name", "version", "purpose"):
        if isinstance(document.get(key), str) and document[key].strip():
            facts[key] = document[key].strip()
    owners = document.get("owners")
    if isinstance(owners, list):
        facts["owners"] = [
            item
            for item in (_owner_from_id(owner) for owner in owners)
            if item is not None
        ]
    mappings = document.get("mappings")
    if isinstance(mappings, list):
        facts["adopted"] = mappings
    subject = facts.get("id") or "dsl-manifest"
    rel = path if _is_path(path) else "dsl-manifest.json"
    return {
        "schema": SCHEMA_EVIDENCE,
        "subject_id": subject if _is_identifier(subject) else "dsl-manifest",
        "sources": [
            {
                "id": "dsl-manifest",
                "kind": "dsl-manifest",
                "path": rel,
                "facts": facts,
            }
        ],
    }


def wrap_ssot_decision(document: Mapping[str, Any], path: str) -> dict[str, Any]:
    facts: dict[str, Any] = {}
    if isinstance(document.get("id"), str):
        facts["id"] = document["id"]
    if isinstance(document.get("purpose"), str):
        facts["purpose"] = document["purpose"]
    subject = facts.get("id") or "ssot-decision"
    rel = path if _is_path(path) else "ssot-decision.json"
    return {
        "schema": SCHEMA_EVIDENCE,
        "subject_id": subject if _is_identifier(subject) else "ssot-decision",
        "sources": [
            {
                "id": "ssot-decision",
                "kind": "ssot-decision",
                "path": rel,
                "facts": facts,
            }
        ],
    }


def ingest_typed(document: Mapping[str, Any], path: str = "input.json") -> dict[str, str | dict[str, Any]]:
    """Classify an already-typed JSON object. Never walks a repository."""

    schema = document.get("schema")
    if schema == SCHEMA_DOCUMENT:
        return {"kind": "document", "payload": dict(document)}
    if schema == SCHEMA_INTERVIEW:
        return {"kind": "interview", "payload": dict(document)}
    if schema == SCHEMA_EVIDENCE:
        return {"kind": "evidence", "payload": dict(document)}
    if schema in INTENT_SCHEMAS:
        return {"kind": "evidence", "payload": wrap_intent(document, path)}
    if schema == "wellmanifest.dsl/manifest/v1":
        return {"kind": "evidence", "payload": wrap_dsl_manifest(document, path)}
    if schema == "wellmanifest.ssot/decision/v1":
        return {"kind": "evidence", "payload": wrap_ssot_decision(document, path)}
    raise ValueError(
        "unknown typed JSON schema; pass interview, evidence-index, "
        "project-ssot, new-project intent, dsl-manifest, or ssot decision"
    )


def validate_interview(document: Mapping[str, Any], *, partial: bool = False) -> list[Finding]:
    document = normalize_interview(document)
    findings: list[Finding] = []
    if document.get("schema") != SCHEMA_INTERVIEW:
        findings.append(
            Finding("PROJECT-KIND-001", "interview schema must be wellmanifest.project-ssot/interview/v1")
        )
    if not _is_identifier(document.get("subject_id")):
        findings.append(Finding("PROJECT-KIND-001", "subject_id must be a stable identifier", "$.subject_id"))
    placement = document.get("placement")
    if not partial:
        if not isinstance(document.get("name"), str) or not document["name"].strip():
            findings.append(Finding("PROJECT-KIND-001", "name is required", "$.name"))
        if not _is_semver(document.get("version")):
            findings.append(Finding("PROJECT-KIND-001", "version must be SemVer", "$.version"))
        findings.extend(placement_findings(placement))
        purpose = document.get("purpose")
        if not isinstance(purpose, str) or not purpose.strip():
            findings.append(Finding("PROJECT-PURPOSE-001", "one-sentence purpose is required", "$.purpose"))
        owners = document.get("owners")
        if not isinstance(owners, list) or not owners:
            findings.append(Finding("PROJECT-KIND-001", "owners must be a non-empty list", "$.owners"))
        if document.get("readme_role") not in README_ROLES:
            findings.append(Finding("PROJECT-README-001", "unknown readme_role", "$.readme_role"))
        if document.get("analyzer_kind") not in ANALYZER_KINDS:
            findings.append(Finding("PROJECT-KIND-001", "unknown analyzer_kind", "$.analyzer_kind"))
        if not isinstance(document.get("analyzer_present"), bool):
            findings.append(Finding("PROJECT-KIND-001", "analyzer_present must be boolean", "$.analyzer_present"))
        if not isinstance(document.get("human_confirmed_debt"), bool):
            findings.append(Finding("PROJECT-KIND-001", "human_confirmed_debt must be boolean", "$.human_confirmed_debt"))
    elif placement is not None:
        findings.extend(placement_findings(placement))
    unknown = sorted(set(document) - {
        "$schema",
        "schema",
        "subject_id",
        "name",
        "version",
        "placement",
        "purpose",
        "owners",
        "purpose_authority",
        "readme_role",
        "divergence_reason",
        "analyzer_present",
        "analyzer_kind",
        "analyzer_noise",
        "human_confirmed_debt",
        "capability_verbs",
        "capability_keywords",
        "capability_use_when",
        "capability_do_not_use_when",
        "capability_install_status",
        "capability_install_package",
        "capability_entrypoint",
        "capability_maturity",
        "capability_stacks",
        "capability_siblings",
    })
    if unknown:
        findings.append(
            Finding("PROJECT-KIND-001", f"unknown interview fields: {unknown}", "$")
        )
    return findings


def validate_evidence_index(document: Mapping[str, Any]) -> list[Finding]:
    findings: list[Finding] = []
    if document.get("schema") != SCHEMA_EVIDENCE:
        findings.append(
            Finding("PROJECT-EVIDENCE-001", "evidence index schema must be wellmanifest.project-ssot/evidence-index/v1")
        )
    if not _is_identifier(document.get("subject_id")):
        findings.append(Finding("PROJECT-KIND-001", "subject_id must be a stable identifier", "$.subject_id"))
    sources = document.get("sources")
    if not isinstance(sources, list) or not sources:
        findings.append(Finding("PROJECT-EVIDENCE-001", "at least one listed source is required", "$.sources"))
        return findings
    seen: set[str] = set()
    for index, source in enumerate(sources):
        prefix = f"$.sources[{index}]"
        if not isinstance(source, dict):
            findings.append(Finding("PROJECT-EVIDENCE-001", "source must be an object", prefix))
            continue
        unknown = sorted(set(source) - {"id", "kind", "path", "digest", "facts"})
        if unknown:
            findings.append(Finding("PROJECT-KIND-001", f"unknown source fields: {unknown}", prefix))
        ident = source.get("id")
        if not _is_identifier(ident):
            findings.append(Finding("PROJECT-KIND-001", "source id must be a stable identifier", f"{prefix}.id"))
        elif ident in seen:
            findings.append(Finding("PROJECT-EVIDENCE-001", f"duplicate source id {ident}", f"{prefix}.id"))
        else:
            seen.add(str(ident))
        kind = source.get("kind")
        if kind not in SOURCE_KINDS or kind == "interview":
            findings.append(Finding("PROJECT-KIND-001", f"unknown evidence kind {kind!r}", f"{prefix}.kind"))
        if not _is_path(source.get("path")):
            findings.append(Finding("PROJECT-EVIDENCE-001", "path must be repository-relative", f"{prefix}.path"))
        digest = source.get("digest")
        if digest is not None and not _is_digest(digest):
            findings.append(Finding("PROJECT-EVIDENCE-001", "digest must be sha256:<hex>", f"{prefix}.digest"))
        facts = source.get("facts")
        if not isinstance(facts, dict):
            findings.append(Finding("PROJECT-EVIDENCE-001", "facts must be an object", f"{prefix}.facts"))
            continue
        extra = sorted(set(facts) - FACT_KEYS)
        if extra:
            findings.append(
                Finding("PROJECT-KIND-001", f"unknown fact keys {extra} (unknownPolicy=reject)", f"{prefix}.facts")
            )
        if kind in ANALYZER_SOURCES:
            identity = sorted(set(facts) & set(IDENTITY_FIELDS))
            if identity:
                findings.append(
                    Finding(
                        "PROJECT-NOISE-001",
                        "analyzer artifacts are evidence, never identity or debt",
                        f"{prefix}.facts",
                    )
                )
        if facts.get("placement") is not None:
            findings.extend(placement_findings(facts.get("placement"), f"{prefix}.facts.placement"))
        extracted = _facts_placement(facts)
        if extracted.get("home") is not None and extracted.get("home") not in HOMES:
            findings.append(Finding("PROJECT-HOME-001", "unknown home fact", f"{prefix}.facts.home"))
        if extracted.get("shape") is not None and extracted.get("shape") not in SHAPES:
            findings.append(Finding("PROJECT-SHAPE-001", "unknown shape fact", f"{prefix}.facts.shape"))
        if extracted.get("runtimeOwner") is not None and extracted.get("runtimeOwner") not in HOMES:
            findings.append(Finding("PROJECT-SHAPE-001", "unknown runtimeOwner fact", f"{prefix}.facts.runtimeOwner"))
    return findings


def _claims_from_source(source: Mapping[str, Any]) -> list[dict[str, Any]]:
    kind = str(source.get("kind"))
    if kind in ANALYZER_SOURCES:
        return []
    facts = source.get("facts") or {}
    claims: list[dict[str, Any]] = []
    identity = dict(facts)
    identity.update(_facts_placement(facts))
    for field in IDENTITY_FIELDS:
        value = identity.get(field)
        if value is None or value == "":
            continue
        claims.append(
            {
                "field": field,
                "value": value if isinstance(value, str) else json.dumps(value, sort_keys=True),
                "source": source.get("id"),
                "kind": kind,
                "precedence": PRECEDENCE.get(kind, 0),
            }
        )
    return claims


def _claims_from_interview(answers: Mapping[str, Any]) -> list[dict[str, Any]]:
    answers = normalize_interview(answers)
    placement = interview_placement(answers)
    mapping = {
        "id": answers.get("subject_id"),
        "name": answers.get("name"),
        "version": answers.get("version"),
        "home": placement.get("home"),
        "shape": placement.get("shape"),
        "runtimeOwner": placement.get("runtimeOwner") or placement.get("home"),
        "purpose": answers.get("purpose"),
    }
    claims: list[dict[str, Any]] = []
    for field, value in mapping.items():
        if value is None or value == "":
            continue
        claims.append(
            {
                "field": field,
                "value": str(value),
                "source": "interview",
                "kind": "interview",
                "precedence": 100,
            }
        )
    return claims


def _unique_values(claims: Sequence[Mapping[str, Any]]) -> list[str]:
    seen: list[str] = []
    for claim in claims:
        value = str(claim["value"])
        if value not in seen:
            seen.append(value)
    return seen


def _pick_field(
    field: str,
    claims: Sequence[Mapping[str, Any]],
    answers: Mapping[str, Any],
    conflicts: list[dict[str, Any]],
    questions: list[str],
) -> str | None:
    if not claims:
        return None
    values = _unique_values(claims)
    if len(values) == 1:
        return values[0]
    interview_claims = [item for item in claims if item["kind"] == "interview"]
    authority = (answers.get("purpose_authority") or "").strip()
    record = {
        "field": field,
        "values": [{"source": str(item["source"]), "value": str(item["value"])} for item in claims],
    }
    if interview_claims:
        picked = str(interview_claims[-1]["value"])
        record["resolvedBy"] = "interview"
        conflicts.append(record)
        return picked
    if field == "purpose" and authority:
        named = [item for item in claims if str(item["source"]) == authority]
        if named:
            record["resolvedBy"] = authority
            conflicts.append(record)
            return str(named[-1]["value"])
    conflicts.append(record)
    if field == "purpose" and PURPOSE_QUESTION not in questions:
        questions.append(PURPOSE_QUESTION)
    elif field == "home" and HOME_QUESTION not in questions:
        questions.append(HOME_QUESTION)
    else:
        question = (
            f"Evidence sources disagree on {field} and the interview did not "
            "resolve it. Fail closed until a typed answer names the winner."
        )
        if question not in questions:
            questions.append(question)
    return None


def _merge_adopted(answers: Mapping[str, Any], sources: Sequence[Mapping[str, Any]]) -> list[dict[str, str]]:
    merged: dict[str, dict[str, str]] = {}
    for source in sources:
        if source.get("kind") in ANALYZER_SOURCES:
            continue
        facts = source.get("facts") or {}
        adopted_items = list(facts.get("adopted") or [])
        placement = facts.get("placement") or {}
        if isinstance(placement, dict):
            adopted_items.extend(placement.get("adopt") or [])
        for item in adopted_items:
            normalized = _normalize_adopted_item(item)
            if not normalized:
                continue
            merged.setdefault(normalized["standard"], normalized)
    for item in interview_placement(answers).get("adopt") or []:
        normalized = _normalize_adopted_item(item)
        if not normalized:
            continue
        merged.setdefault(normalized["standard"], normalized)
        slash = slash_adopt(item if isinstance(item, str) else normalized["standard"])
        if _is_adopt_id(slash):
            merged[normalized["standard"]]["standard"] = dotted_standard(slash)
    return [merged[key] for key in sorted(merged)]


def _adopt_ids(adopted: Sequence[Mapping[str, str]], answers: Mapping[str, Any]) -> list[str]:
    ids: list[str] = []
    for item in interview_placement(answers).get("adopt") or []:
        slash = slash_adopt(item)
        if _is_adopt_id(slash) and slash not in ids:
            ids.append(slash)
    for item in adopted:
        slash = slash_adopt(item["standard"])
        if _is_adopt_id(slash) and slash not in ids:
            ids.append(slash)
    return ids


def _merge_owners(answers: Mapping[str, Any], sources: Sequence[Mapping[str, Any]]) -> list[dict[str, str]]:
    owners: list[dict[str, str]] = []
    seen: set[str] = set()
    for raw in answers.get("owners") or []:
        owner = _owner_from_id(raw)
        if owner and owner["id"] not in seen:
            owners.append(owner)
            seen.add(owner["id"])
    for source in sources:
        for raw in source.get("facts", {}).get("owners") or []:
            owner = _owner_from_id(raw)
            if owner and owner["id"] not in seen:
                owners.append(owner)
                seen.add(owner["id"])
    return owners


def _packaging(sources: Sequence[Mapping[str, Any]]) -> dict[str, str]:
    for source in sources:
        kind = source.get("kind")
        if kind == "pyproject":
            return {"kind": "pip", "path": str(source.get("path"))}
        if kind == "package-json":
            return {"kind": "npm", "path": str(source.get("path"))}
        packaging = source.get("facts", {}).get("packaging") or []
        if isinstance(packaging, list) and packaging:
            first = packaging[0]
            if first in PACKAGING_KINDS:
                result = {"kind": first}
                if source.get("path"):
                    result["path"] = str(source["path"])
                return result
    return {"kind": "none"}


def _evidence_entries(sources: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    for source in sources:
        kind = str(source.get("kind"))
        if kind in ANALYZER_SOURCES:
            role = "evidence"
        elif kind in {"pyproject", "package-json"}:
            role = "packaging"
        elif kind == "readme":
            role = "projection_candidate"
        elif kind in AUTHORITY_KINDS:
            role = "authority"
        else:
            role = "evidence"
        entry: dict[str, Any] = {
            "id": source["id"],
            "kind": kind,
            "path": source["path"],
            "precedence": PRECEDENCE.get(kind, 0),
            "role": role,
        }
        if source.get("digest"):
            entry["digest"] = source["digest"]
        if kind == "readme":
            entry["ssotKind"] = "facade"
        elif kind in {"docs", "schema"}:
            entry["ssotKind"] = "generated_mirror"
        entries.append(entry)
    return entries


def _receipt(sources: Sequence[Mapping[str, Any]]) -> dict[str, Any] | None:
    digests = [
        {"path": str(source["path"]), "digest": str(source["digest"])}
        for source in sources
        if source.get("digest")
    ]
    if not digests:
        return None
    return {"sourceDigests": digests}


def _capability_from_answers(answers: Mapping[str, Any]) -> dict[str, Any] | None:
    """Compose the v2 capability block from interview answers.

    Returns None when the human-only fields are unanswered: composition is
    propose-only, so an unanswered capability yields a v1 document plus a
    question, never an invented capability.
    """

    def _list(key: str) -> list[str]:
        raw = answers.get(key)
        if isinstance(raw, str):
            raw = [part.strip() for part in raw.split(",")]
        if not isinstance(raw, list):
            return []
        return [str(item).strip() for item in raw if str(item).strip()]

    verbs = _list("capability_verbs")
    use_when = _list("capability_use_when")
    do_not = _list("capability_do_not_use_when")
    if not (verbs and use_when and do_not):
        return None

    capability: dict[str, Any] = {
        "verbs": verbs,
        "useWhen": use_when,
        "doNotUseWhen": do_not,
    }
    for key, field in (("capability_keywords", "keywords"), ("capability_stacks", "stacks")):
        values = _list(key)
        if values:
            capability[field] = values

    status = answers.get("capability_install_status")
    if isinstance(status, str) and status.strip():
        install: dict[str, str] = {"status": status.strip()}
        package = answers.get("capability_install_package")
        if isinstance(package, str) and package.strip():
            install["package"] = package.strip()
        capability["install"] = install

    level = answers.get("capability_maturity")
    if isinstance(level, str) and level.strip():
        capability["maturity"] = {"level": level.strip()}

    entrypoint = answers.get("capability_entrypoint")
    if isinstance(entrypoint, str) and entrypoint.count(":") >= 2:
        kind, name, invoke = entrypoint.split(":", 2)
        if kind.strip() and name.strip() and invoke.strip():
            capability["entrypoints"] = [
                {"kind": kind.strip(), "name": name.strip(), "invoke": invoke.strip()}
            ]

    siblings: list[dict[str, str]] = []
    for spec in _list("capability_siblings"):
        parts = [part.strip() for part in spec.split(":")]
        if len(parts) >= 2 and parts[0] and parts[1]:
            entry = {"id": parts[0], "relation": parts[1]}
            if len(parts) > 2 and parts[2]:
                entry["target"] = parts[2]
            siblings.append(entry)
    if siblings:
        capability["siblings"] = siblings

    return capability


def classify(
    answers: Mapping[str, Any] | None = None,
    evidence: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Compose typed interview answers and a listed evidence index into a document."""

    answers = normalize_interview(dict(answers or {}))
    sources = list((evidence or {}).get("sources") or [])
    questions: list[str] = []
    conflicts: list[dict[str, Any]] = []

    claims_by_field: dict[str, list[dict[str, Any]]] = {field: [] for field in IDENTITY_FIELDS}
    for source in sources:
        for claim in _claims_from_source(source):
            claims_by_field[claim["field"]].append(claim)
    for claim in _claims_from_interview(answers):
        claims_by_field[claim["field"]].append(claim)

    picked: dict[str, str | None] = {}
    for field in IDENTITY_FIELDS:
        picked[field] = _pick_field(field, claims_by_field[field], answers, conflicts, questions)

    subject = picked["id"] or answers.get("subject_id") or (evidence or {}).get("subject_id")
    if not _is_identifier(subject):
        subject = "unspecified.project"

    shape = picked["shape"]
    home = picked["home"]
    runtime_owner = picked["runtimeOwner"]
    if shape == "domain_pack" and not runtime_owner and home:
        runtime_owner = home
        picked["runtimeOwner"] = home

    if not home:
        questions.append(HOME_QUESTION)

    adopted = _merge_adopted(answers, sources)
    adopt_ids = _adopt_ids(adopted, answers)
    owners = _merge_owners(answers, sources)
    if not owners:
        owners = [{"kind": "repository", "id": f"github:unspecified/{subject}"}]
        questions.append("Who owns this project's semantics? Name a repository or org id.")

    purpose = picked["purpose"]
    if not purpose:
        questions.append("What is the one-sentence purpose? README is not authority until classified.")

    readme_sources = [item for item in sources if item.get("kind") == "readme"]
    readme_role = answers.get("readme_role") or ("facade" if readme_sources else "unknown")
    divergence_reason = (answers.get("divergence_reason") or "").strip()
    purpose_conflict = next((item for item in conflicts if item["field"] == "purpose"), None)

    relations: list[dict[str, Any]] = []
    if readme_sources:
        readme_path = str(readme_sources[0]["path"])
        if readme_role in {"facade", "unknown"}:
            relations.append(
                {
                    "id": "readme.facade",
                    "kind": "facade",
                    "subject": readme_path,
                    "canonical": "this-document",
                    "rationale": (
                        "README is a facade over this project-ssot document. "
                        "Do not keep a second competing README as authority. "
                        "A later generator may emit README FROM this AST."
                    ),
                }
            )
        if readme_role == "generated_mirror":
            relations.append(
                {
                    "id": "readme.mirror",
                    "kind": "generated_mirror",
                    "subject": readme_path,
                    "canonical": "this-document",
                    "rationale": (
                        "README is a generated mirror of this document. Edit the "
                        "JSON AST and regenerate the projection; do not edit README as SSOT."
                    ),
                }
            )
        if readme_role == "allowed_divergence" or (
            purpose_conflict and purpose_conflict.get("resolvedBy")
        ):
            reason = divergence_reason or (
                "Marketing or locale intro may differ from the schema purpose; "
                "the JSON AST remains canonical."
            )
            relations.append(
                {
                    "id": "readme.divergence",
                    "kind": "allowed_divergence",
                    "subject": readme_path,
                    "canonical": "$.purpose",
                    "knownDivergent": {"reason": reason},
                    "rationale": reason,
                }
            )
        if readme_role == "unknown" and README_QUESTION not in questions:
            questions.append(README_QUESTION)

    docs_sources = [item for item in sources if item.get("kind") in {"docs", "schema"}]
    if docs_sources:
        relations.append(
            {
                "id": "docs.mirror",
                "kind": "generated_mirror",
                "subject": str(docs_sources[0]["path"]),
                "canonical": "this-document",
                "rationale": (
                    "Docs and schemas listed here are generated mirrors or "
                    "projections of the project SSOT, not a second description authority."
                ),
            }
        )

    analyzer_present = bool(answers.get("analyzer_present")) or any(
        item.get("kind") in ANALYZER_SOURCES for item in sources
    )
    human_confirmed = bool(answers.get("human_confirmed_debt"))
    treat_as_debt = False
    if analyzer_present and not human_confirmed:
        treat_as_debt = False

    actions = [
        {"do": "use_document_as_ssot"},
        {"do": "map_adopted_standard"},
        {"do": "record_evidence_digest"},
    ]
    if readme_sources:
        actions.append({"do": "keep_readme_as_facade", "target": str(readme_sources[0]["path"])})
        actions.append({"do": "generate_readme_from_document"})
    if analyzer_present and not human_confirmed:
        actions.append({"do": "ignore_analyzer_until_interview"})
    if any(item["kind"] == "allowed_divergence" for item in relations):
        actions.append({"do": "document_known_divergent"})
    if questions:
        actions.append({"do": "ask_clarifying_questions"})

    unresolved = [item for item in conflicts if not item.get("resolvedBy")]
    name = picked["name"] or subject
    version = picked["version"] or "0.1.0"
    if not _is_semver(version):
        version = "0.1.0"
        questions.append("version from evidence is not SemVer; declare it in the interview.")

    capability = _capability_from_answers(answers or {})
    if capability is None:
        questions.append(
            "capability.verbs/useWhen/doNotUseWhen are unanswered; the document stays at "
            "wellmanifest.project-ssot/v1 and is not map-ready until the interview fills them."
        )

    document: dict[str, Any] = {
        "schema": SCHEMA_DOCUMENT if capability else SCHEMA_DOCUMENT_V1,
        "id": subject,
        "name": name,
        "version": version,
        "purpose": purpose or f"Project SSOT for {subject}",
        "placement": {
            key: value
            for key, value in {
                "home": home,
                "shape": shape,
                "runtimeOwner": runtime_owner or home,
                "adopt": adopt_ids,
            }.items()
            if value is not None
        },
        "owners": owners,
        "policy": {
            "kind": "project_policy",
            "descriptionIsProjection": True,
            "readmeAuthority": "generated_from_document",
            "unknownPolicy": "reject",
            "effectModel": "propose-only",
            "analyzerTreatAsDebtUntilInterview": treat_as_debt,
            "adoptDoesNotImplyHome": True,
            "forbid": list(REQUIRED_FORBIDS) + (["keep_competing_readme_authority"] if readme_sources else []),
            "actions": actions,
        },
        "adopted": adopted,
        "evidence": _evidence_entries(sources),
        "relations": relations,
        "packaging": _packaging(sources),
        "questions": questions,
    }
    if capability:
        document["capability"] = capability
    receipt = _receipt(sources)
    if receipt:
        document["receipt"] = receipt
    if conflicts:
        document["conflicts"] = conflicts
    if unresolved:
        # Placeholder identity is not a resolution; validate will fail closed.
        document.setdefault("questions", questions)
    return document


CAPABILITY_KEYS = {
    "verbs", "keywords", "inputs", "outputs", "entrypoints", "install",
    "maturity", "siblings", "useWhen", "doNotUseWhen", "stacks", "workstreamHints",
}


def _string_list_findings(
    value: Any, path: str, code: str, *, minimum: int = 0, maximum: int = 64
) -> list[Finding]:
    if value is None:
        if minimum:
            return [Finding(code, f"{path} is required", path)]
        return []
    if not isinstance(value, list) or any(not isinstance(item, str) or not item.strip() for item in value):
        return [Finding(code, f"{path} must be a list of non-empty strings", path)]
    if len(value) < minimum:
        return [Finding(code, f"{path} needs at least {minimum} entry/entries", path)]
    if len(value) > maximum:
        return [Finding(code, f"{path} must hold at most {maximum} entries", path)]
    if len(set(value)) != len(value):
        return [Finding(code, f"{path} must not repeat entries", path)]
    return []


def capability_findings(value: Any, schema_id: str | None = None) -> list[Finding]:
    """Validate the v2 capability block.

    The block is what lets a consumer decide whether to use this project at all.
    verbs/useWhen/doNotUseWhen are required because no analyzer can derive them and
    a wrong guess is exactly what makes a consumer pick the wrong project.
    """
    path = "$.capability"
    if value is None:
        if schema_id == SCHEMA_DOCUMENT:
            return [
                Finding(
                    "PROJECT-CAPABILITY-001",
                    "capability block is required by wellmanifest.project-ssot/v2",
                    path,
                )
            ]
        return []
    if not isinstance(value, Mapping):
        return [Finding("PROJECT-CAPABILITY-001", "capability must be an object", path)]

    findings: list[Finding] = []
    unknown = sorted(set(value) - CAPABILITY_KEYS)
    if unknown:
        findings.append(
            Finding("PROJECT-CAPABILITY-001", f"unknown capability fields {unknown} (unknownPolicy=reject)", path)
        )

    verbs = value.get("verbs")
    if not isinstance(verbs, list) or not verbs:
        findings.append(Finding("PROJECT-CAPABILITY-001", "at least one capability verb is required", f"{path}.verbs"))
    else:
        if len(verbs) > 8:
            findings.append(
                Finding("PROJECT-CAPABILITY-001", "at most 8 verbs; a project doing more is under-decomposed", f"{path}.verbs")
            )
        for index, verb in enumerate(verbs):
            if verb not in CAPABILITY_VERBS:
                findings.append(
                    Finding("PROJECT-CAPABILITY-001", f"unknown capability verb {verb!r}", f"{path}.verbs[{index}]")
                )

    findings.extend(_string_list_findings(value.get("keywords"), f"{path}.keywords", "PROJECT-CAPABILITY-001", maximum=12))
    findings.extend(
        _string_list_findings(value.get("useWhen"), f"{path}.useWhen", "PROJECT-CAPABILITY-002", minimum=1, maximum=6)
    )
    findings.extend(
        _string_list_findings(
            value.get("doNotUseWhen"), f"{path}.doNotUseWhen", "PROJECT-CAPABILITY-002", minimum=1, maximum=6
        )
    )
    findings.extend(_string_list_findings(value.get("stacks"), f"{path}.stacks", "PROJECT-CAPABILITY-001"))

    for key in ("inputs", "outputs"):
        items = value.get(key)
        if items is None:
            continue
        if not isinstance(items, list):
            findings.append(Finding("PROJECT-CAPABILITY-001", f"{key} must be a list", f"{path}.{key}"))
            continue
        for index, item in enumerate(items):
            where = f"{path}.{key}[{index}]"
            if not isinstance(item, Mapping) or item.get("kind") not in CAPABILITY_IO_KINDS:
                findings.append(Finding("PROJECT-CAPABILITY-001", f"unknown {key} kind", where))

    entrypoints = value.get("entrypoints")
    if entrypoints is not None:
        if not isinstance(entrypoints, list):
            findings.append(Finding("PROJECT-CAPABILITY-003", "entrypoints must be a list", f"{path}.entrypoints"))
        else:
            for index, item in enumerate(entrypoints):
                where = f"{path}.entrypoints[{index}]"
                if not isinstance(item, Mapping):
                    findings.append(Finding("PROJECT-CAPABILITY-003", "entrypoint must be an object", where))
                    continue
                if item.get("kind") not in ENTRYPOINT_KINDS:
                    findings.append(Finding("PROJECT-CAPABILITY-003", "unknown entrypoint kind", f"{where}.kind"))
                for field in ("name", "invoke"):
                    if not isinstance(item.get(field), str) or not item.get(field, "").strip():
                        findings.append(Finding("PROJECT-CAPABILITY-003", f"entrypoint {field} is required", f"{where}.{field}"))
                declared = item.get("declaredIn")
                if declared is not None and not _is_path(declared):
                    findings.append(Finding("PROJECT-CAPABILITY-003", "declaredIn must be a repo-relative path", f"{where}.declaredIn"))

    install = value.get("install")
    if install is not None:
        if not isinstance(install, Mapping) or install.get("status") not in INSTALL_STATUSES:
            findings.append(Finding("PROJECT-CAPABILITY-001", "unknown install status", f"{path}.install"))
        elif install.get("status") in {"pypi", "npm", "container"} and not install.get("package"):
            findings.append(
                Finding("PROJECT-CAPABILITY-001", "a published install status must name the package", f"{path}.install.package")
            )

    maturity = value.get("maturity")
    if maturity is not None:
        if not isinstance(maturity, Mapping) or maturity.get("level") not in MATURITY_LEVELS:
            findings.append(Finding("PROJECT-CAPABILITY-001", "unknown maturity level", f"{path}.maturity"))

    siblings = value.get("siblings")
    if siblings is not None:
        if not isinstance(siblings, list):
            findings.append(Finding("PROJECT-CAPABILITY-004", "siblings must be a list", f"{path}.siblings"))
        else:
            for index, item in enumerate(siblings):
                where = f"{path}.siblings[{index}]"
                if not isinstance(item, Mapping):
                    findings.append(Finding("PROJECT-CAPABILITY-004", "sibling must be an object", where))
                    continue
                if not _is_identifier(item.get("id")):
                    findings.append(Finding("PROJECT-CAPABILITY-004", "sibling id must be an identifier", f"{where}.id"))
                relation = item.get("relation")
                if relation not in SIBLING_RELATIONS:
                    findings.append(Finding("PROJECT-CAPABILITY-004", f"unknown sibling relation {relation!r}", f"{where}.relation"))
                if relation in {"superseded-by", "supersedes"} and not _is_identifier(item.get("target")):
                    findings.append(
                        Finding(
                            "PROJECT-CAPABILITY-004",
                            f"{relation} must name the other project in target",
                            f"{where}.target",
                        )
                    )

    hints = value.get("workstreamHints")
    if hints is not None:
        if not isinstance(hints, Mapping):
            findings.append(Finding("PROJECT-CAPABILITY-001", "workstreamHints must be an object", f"{path}.workstreamHints"))
        else:
            for key, globs in hints.items():
                findings.extend(
                    _string_list_findings(globs, f"{path}.workstreamHints.{key}", "PROJECT-CAPABILITY-001", minimum=1)
                )

    return findings


def validate_decision(document: Mapping[str, Any]) -> list[Finding]:
    findings: list[Finding] = []
    schema_id = document.get("schema")
    if schema_id not in SCHEMA_DOCUMENTS:
        findings.append(
            Finding("PROJECT-KIND-001", f"schema must be one of {', '.join(SCHEMA_DOCUMENTS)}")
        )
    allowed = {
        "$schema",
        "schema",
        "id",
        "name",
        "version",
        "purpose",
        "placement",
        "owners",
        "policy",
        "adopted",
        "evidence",
        "relations",
        "packaging",
        "receipt",
        "conflicts",
        "questions",
        "capability",
    }
    unknown = sorted(set(document) - allowed)
    if unknown:
        findings.append(Finding("PROJECT-KIND-001", f"unknown fields {unknown} (unknownPolicy=reject)"))
    if not _is_identifier(document.get("id")):
        findings.append(Finding("PROJECT-KIND-001", "id must be a stable identifier", "$.id"))
    if not isinstance(document.get("name"), str) or not document.get("name"):
        findings.append(Finding("PROJECT-KIND-001", "name is required", "$.name"))
    if not _is_semver(document.get("version")):
        findings.append(Finding("PROJECT-KIND-001", "version must be SemVer", "$.version"))
    purpose = document.get("purpose")
    if not isinstance(purpose, str) or not purpose.strip():
        findings.append(Finding("PROJECT-PURPOSE-001", "one-sentence purpose is required", "$.purpose"))

    placement = document.get("placement")
    if not isinstance(placement, dict):
        findings.append(Finding("PROJECT-KIND-001", "placement is required", "$.placement"))
        return findings
    findings.extend(placement_findings(placement))
    home = placement.get("home") if isinstance(placement, dict) else None
    adopt = placement.get("adopt") if isinstance(placement, dict) else None
    wellmanifest_adopt = [item for item in (adopt or []) if str(item).startswith("wellmanifest/")]
    if home == "wellmanifest" and wellmanifest_adopt and not document.get("policy", {}).get("adoptDoesNotImplyHome"):
        findings.append(
            Finding(
                "PROJECT-ADOPT-001",
                "adopt wellmanifest/* must not be used to infer home",
                "$.placement",
            )
        )

    policy = document.get("policy")
    if not isinstance(policy, dict) or policy.get("kind") != "project_policy":
        findings.append(Finding("PROJECT-KIND-001", "policy must be project_policy", "$.policy"))
    else:
        if policy.get("descriptionIsProjection") is not True:
            findings.append(
                Finding("PROJECT-README-001", "generated description is a projection of this AST", "$.policy")
            )
        if policy.get("readmeAuthority") not in {"generated_from_document", "none"}:
            findings.append(
                Finding("PROJECT-README-001", "README must not be description authority", "$.policy.readmeAuthority")
            )
        if policy.get("unknownPolicy") != "reject":
            findings.append(Finding("PROJECT-KIND-001", "unknownPolicy must be reject", "$.policy.unknownPolicy"))
        if policy.get("effectModel") != "propose-only":
            findings.append(Finding("PROJECT-KIND-001", "effectModel must be propose-only", "$.policy.effectModel"))
        if policy.get("adoptDoesNotImplyHome") is not True:
            findings.append(Finding("PROJECT-ADOPT-001", "adoptDoesNotImplyHome must be true", "$.policy"))
        if policy.get("analyzerTreatAsDebtUntilInterview"):
            findings.append(
                Finding(
                    "PROJECT-NOISE-001",
                    "analyzer output must not be treated as debt before the interview",
                    "$.policy.analyzerTreatAsDebtUntilInterview",
                )
            )
        forbid = set(policy.get("forbid") or [])
        for item in REQUIRED_FORBIDS:
            if item not in forbid:
                findings.append(
                    Finding("PROJECT-KIND-001", f"policy must forbid {item}", "$.policy.forbid")
                )
        if "treat_readme_as_authority" not in forbid:
            findings.append(
                Finding("PROJECT-README-001", "policy must forbid treat_readme_as_authority", "$.policy.forbid")
            )
        for item in forbid:
            if item not in FORBIDS:
                findings.append(Finding("PROJECT-KIND-001", f"unknown forbid {item!r}", "$.policy.forbid"))
        for action in policy.get("actions") or []:
            if action.get("do") not in ACTIONS:
                findings.append(Finding("PROJECT-KIND-001", f"unknown action {action.get('do')!r}", "$.policy.actions"))

    owners = document.get("owners")
    if not isinstance(owners, list) or not owners:
        findings.append(Finding("PROJECT-KIND-001", "owners are required", "$.owners"))
    else:
        for index, owner in enumerate(owners):
            if not isinstance(owner, dict) or owner.get("kind") not in OWNER_KINDS:
                findings.append(Finding("PROJECT-KIND-001", "invalid owner", f"$.owners[{index}]"))

    adopted = document.get("adopted")
    if not isinstance(adopted, list):
        findings.append(Finding("PROJECT-ADOPT-001", "adopted must be an array of mappings", "$.adopted"))
    else:
        for index, item in enumerate(adopted):
            prefix = f"$.adopted[{index}]"
            if not isinstance(item, dict) or item.get("relation") not in RELATIONS_MAP:
                findings.append(
                    Finding("PROJECT-ADOPT-001", "adopted standards are mappings, not copies", prefix)
                )

    evidence = document.get("evidence")
    if not isinstance(evidence, list):
        findings.append(Finding("PROJECT-EVIDENCE-001", "evidence must be an array", "$.evidence"))
    else:
        for index, item in enumerate(evidence):
            prefix = f"$.evidence[{index}]"
            if not isinstance(item, dict):
                findings.append(Finding("PROJECT-EVIDENCE-001", "evidence entry must be an object", prefix))
                continue
            if item.get("kind") not in SOURCE_KINDS:
                findings.append(Finding("PROJECT-KIND-001", "unknown evidence kind", f"{prefix}.kind"))
            if not _is_path(item.get("path")):
                findings.append(Finding("PROJECT-EVIDENCE-001", "invalid evidence path", f"{prefix}.path"))
            if item.get("kind") in ANALYZER_SOURCES and item.get("role") == "authority":
                findings.append(
                    Finding("PROJECT-NOISE-001", "analyzer must not be an authority source", prefix)
                )
            if item.get("digest") is not None and not _is_digest(item.get("digest")):
                findings.append(Finding("PROJECT-EVIDENCE-001", "invalid digest", f"{prefix}.digest"))

    relations = document.get("relations")
    if not isinstance(relations, list):
        findings.append(Finding("PROJECT-KIND-001", "relations must be an array", "$.relations"))
    else:
        for index, item in enumerate(relations):
            prefix = f"$.relations[{index}]"
            if not isinstance(item, dict) or item.get("kind") not in SSOT_KINDS:
                findings.append(Finding("PROJECT-KIND-001", "relation kind must be an ssot kind", prefix))
                continue
            if item.get("kind") == "allowed_divergence":
                known = item.get("knownDivergent") or {}
                pending = document.get("questions") or []
                if not known.get("reason") and not pending:
                    findings.append(
                        Finding(
                            "PROJECT-README-001",
                            "allowed_divergence needs a KNOWN_DIVERGENT reason or a question",
                            f"{prefix}.knownDivergent",
                        )
                    )

    questions = document.get("questions")
    if not isinstance(questions, list):
        findings.append(Finding("PROJECT-KIND-001", "questions must be an array", "$.questions"))

    for index, item in enumerate(document.get("conflicts") or []):
        if not isinstance(item, dict):
            continue
        if not item.get("resolvedBy"):
            findings.append(
                Finding(
                    "PROJECT-CONFLICT-001",
                    f"unresolved conflict on {item.get('field')}; interview must name the winner",
                    f"$.conflicts[{index}]",
                )
            )

    if document.get("packaging"):
        packaging = document["packaging"]
        if not isinstance(packaging, dict) or packaging.get("kind") not in PACKAGING_KINDS:
            findings.append(Finding("PROJECT-KIND-001", "unknown packaging kind", "$.packaging"))

    findings.extend(capability_findings(document.get("capability"), schema_id))

    return findings


def _io_suffix(item: Mapping[str, Any]) -> str:
    parts = []
    if item.get("path"):
        parts.append(f"path={item['path']}")
    if item.get("schema"):
        parts.append(f"schema={item['schema']}")
    if item.get("note"):
        parts.append(f"note={_quote(item['note'])}")
    return (" " + " ".join(parts)) if parts else ""


def _quote(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def render_dsl(document: Mapping[str, Any]) -> str:
    """Lossless-enough text projection of a project SSOT document."""

    lines = [
        "DOCUMENT PROJECT",
        f"ID {document['id']}",
        f"NAME {_quote(str(document['name']))}",
        f"VERSION {document['version']}",
        f"SCHEMA {document['schema']}",
        f"PURPOSE {_quote(str(document['purpose']))}",
        "",
        "PLACEMENT",
    ]
    placement = document["placement"]
    lines.append(f"  HOME {placement['home']}")
    lines.append(f"  SHAPE {placement['shape']}")
    if placement.get("runtimeOwner"):
        lines.append(f"  RUNTIME_OWNER {placement['runtimeOwner']}")
    for item in placement.get("adopt") or []:
        lines.append(f"  ADOPT {item}")
    policy = document["policy"]
    lines.append("")
    lines.append("POLICY project")
    lines.append(f"  DESCRIPTION_IS_PROJECTION {str(bool(policy['descriptionIsProjection'])).lower()}")
    lines.append(f"  README_AUTHORITY {policy['readmeAuthority']}")
    lines.append(f"  UNKNOWN_POLICY {policy['unknownPolicy']}")
    lines.append(f"  EFFECT {policy['effectModel']}")
    lines.append(
        f"  ANALYZER_DEBT {str(bool(policy.get('analyzerTreatAsDebtUntilInterview'))).lower()}"
    )
    lines.append(f"  ADOPT_DOES_NOT_IMPLY_HOME {str(bool(policy.get('adoptDoesNotImplyHome'))).lower()}")
    for item in policy.get("forbid") or []:
        lines.append(f"  FORBID {item}")
    for action in policy.get("actions") or []:
        target = f" {action['target']}" if action.get("target") else ""
        lines.append(f"  ACTION {action['do']}{target}")
    for owner in document.get("owners") or []:
        lines.append("")
        lines.append(f"OWNER {owner['kind']} {owner['id']}")
    for item in document.get("adopted") or []:
        uri = f" {item['uri']}" if item.get("uri") else ""
        lines.append("")
        lines.append(f"ADOPTED {item['standard']} {item['relation']}{uri}")
    for item in document.get("evidence") or []:
        lines.append("")
        lines.append(f"EVIDENCE {item['id']}")
        lines.append(f"  KIND {item['kind']}")
        lines.append(f"  PATH {item['path']}")
        lines.append(f"  PRECEDENCE {item['precedence']}")
        lines.append(f"  ROLE {item['role']}")
        if item.get("digest"):
            lines.append(f"  DIGEST {item['digest']}")
        if item.get("ssotKind"):
            lines.append(f"  SSOT_KIND {item['ssotKind']}")
    for item in document.get("relations") or []:
        lines.append("")
        lines.append(f"RELATION {item['id']}")
        lines.append(f"  KIND {item['kind']}")
        lines.append(f"  SUBJECT {item['subject']}")
        lines.append(f"  CANONICAL {item['canonical']}")
        if item.get("rationale"):
            lines.append(f"  RATIONALE {_quote(item['rationale'])}")
        known = item.get("knownDivergent") or {}
        if known.get("reason"):
            lines.append(f"  REASON {_quote(known['reason'])}")
    capability = document.get("capability") or {}
    if capability:
        lines.append("")
        lines.append("CAPABILITY")
        for verb in capability.get("verbs") or []:
            lines.append(f"  VERB {verb}")
        for keyword in capability.get("keywords") or []:
            lines.append(f"  KEYWORD {_quote(keyword)}")
        for stack in capability.get("stacks") or []:
            lines.append(f"  STACK {stack}")
        for item in capability.get("inputs") or []:
            lines.append(f"  INPUT {item['kind']}{_io_suffix(item)}")
        for item in capability.get("outputs") or []:
            lines.append(f"  OUTPUT {item['kind']}{_io_suffix(item)}")
        for item in capability.get("entrypoints") or []:
            declared = f" declaredIn={item['declaredIn']}" if item.get("declaredIn") else ""
            lines.append(f"  ENTRYPOINT {item['kind']} {item['name']} {_quote(item['invoke'])}{declared}")
        install = capability.get("install") or {}
        if install:
            package = f" {install['package']}" if install.get("package") else ""
            lines.append(f"  INSTALL {install['status']}{package}")
        maturity = capability.get("maturity") or {}
        if maturity:
            grade = f" {maturity['grade']}" if maturity.get("grade") else ""
            lines.append(f"  MATURITY {maturity['level']}{grade}")
        for item in capability.get("siblings") or []:
            target = f" {item['target']}" if item.get("target") else ""
            lines.append(f"  SIBLING {item['id']} {item['relation']}{target}")
        for entry in capability.get("useWhen") or []:
            lines.append(f"  USE_WHEN {_quote(entry)}")
        for entry in capability.get("doNotUseWhen") or []:
            lines.append(f"  DO_NOT_USE_WHEN {_quote(entry)}")
        for name, globs in (capability.get("workstreamHints") or {}).items():
            for glob in globs:
                lines.append(f"  WORKSTREAM {name} {_quote(glob)}")
    packaging = document.get("packaging") or {}
    if packaging:
        lines.append("")
        extra = f" {packaging['path']}" if packaging.get("path") else ""
        lines.append(f"PACKAGING {packaging.get('kind', 'none')}{extra}")
    receipt = document.get("receipt") or {}
    if receipt.get("sourceDigests"):
        lines.append("")
        lines.append("RECEIPT")
        for item in receipt["sourceDigests"]:
            lines.append(f"  DIGEST {item['path']} {item['digest']}")
    for item in document.get("conflicts") or []:
        lines.append("")
        resolved = f" resolvedBy={item['resolvedBy']}" if item.get("resolvedBy") else ""
        lines.append(f"CONFLICT {item['field']}{resolved}")
        for value in item.get("values") or []:
            lines.append(f"  VALUE {value['source']} {_quote(value['value'])}")
    if document.get("questions"):
        lines.append("")
        lines.append("QUESTIONS")
        for question in document["questions"]:
            lines.append(f"  QUESTION {_quote(question)}")
    lines.append("")
    return "\n".join(lines)


def _unquote(value: str) -> str:
    text = value.strip()
    if len(text) >= 2 and text[0] == text[-1] == '"':
        return bytes(text[1:-1], "utf-8").decode("unicode_escape")
    return text


def _parse_io(rest: str) -> dict[str, Any]:
    kind, _, extra = rest.partition(" ")
    item: dict[str, Any] = {"kind": kind}
    for key in ("path", "schema", "note"):
        marker = f"{key}="
        if marker in extra:
            value = extra.split(marker, 1)[1]
            if key == "note":
                item[key] = _unquote(value.strip())
            else:
                item[key] = value.split(" ")[0]
    return item


def _parse_entrypoint(rest: str) -> dict[str, Any]:
    kind, _, remainder = rest.partition(" ")
    name, _, remainder = remainder.partition(" ")
    declared = None
    if " declaredIn=" in remainder:
        remainder, _, declared = remainder.partition(" declaredIn=")
    item: dict[str, Any] = {"kind": kind, "name": name, "invoke": _unquote(remainder.strip())}
    if declared:
        item["declaredIn"] = declared.strip()
    return item


def parse_dsl(text: str) -> dict[str, Any]:
    """Parse the text projection back to the canonical JSON AST."""

    document: dict[str, Any] = {
        "schema": SCHEMA_DOCUMENT,
        "placement": {"adopt": []},
        "owners": [],
        "policy": {"kind": "project_policy", "forbid": [], "actions": []},
        "adopted": [],
        "evidence": [],
        "relations": [],
        "questions": [],
        "conflicts": [],
    }
    section = "root"
    current: dict[str, Any] | None = None

    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        if not line.strip():
            continue
        indent = len(line) - len(line.lstrip())
        tokens = line.strip().split(None, 1)
        head = tokens[0]
        rest = tokens[1] if len(tokens) > 1 else ""

        if indent == 0:
            if head == "DOCUMENT":
                continue
            if head == "ID":
                document["id"] = rest
            elif head == "NAME":
                document["name"] = _unquote(rest)
            elif head == "VERSION":
                document["version"] = rest
            elif head == "SCHEMA":
                document["schema"] = rest
            elif head == "PURPOSE":
                document["purpose"] = _unquote(rest)
            elif head == "PLACEMENT":
                section = "placement"
                current = document["placement"]
            elif head == "POLICY":
                section = "policy"
                current = document["policy"]
            elif head == "OWNER":
                kind, _, ident = rest.partition(" ")
                document["owners"].append({"kind": kind, "id": ident})
                section = "root"
                current = None
            elif head == "ADOPTED":
                parts = rest.split(None, 2)
                item = {"standard": parts[0], "relation": parts[1] if len(parts) > 1 else "maps-to"}
                if len(parts) > 2:
                    item["uri"] = parts[2]
                document["adopted"].append(item)
                section = "root"
                current = None
            elif head == "EVIDENCE":
                section = "evidence"
                current = {"id": rest}
                document["evidence"].append(current)
            elif head == "RELATION":
                section = "relation"
                current = {"id": rest}
                document["relations"].append(current)
            elif head == "CAPABILITY":
                section = "capability"
                current = document.setdefault("capability", {})
            elif head == "PACKAGING":
                kind, _, path = rest.partition(" ")
                packaging = {"kind": kind}
                if path:
                    packaging["path"] = path
                document["packaging"] = packaging
                section = "root"
                current = None
            elif head == "RECEIPT":
                section = "receipt"
                document["receipt"] = {"sourceDigests": []}
                current = document["receipt"]
            elif head == "CONFLICT":
                section = "conflict"
                field, _, extra = rest.partition(" ")
                current = {"field": field, "values": []}
                if extra.startswith("resolvedBy="):
                    current["resolvedBy"] = extra.split("=", 1)[1]
                document["conflicts"].append(current)
            elif head == "QUESTIONS":
                section = "questions"
                current = document
            continue

        if section == "capability" and current is not None:
            if head == "VERB":
                current.setdefault("verbs", []).append(rest)
            elif head == "KEYWORD":
                current.setdefault("keywords", []).append(_unquote(rest))
            elif head == "STACK":
                current.setdefault("stacks", []).append(rest)
            elif head in {"INPUT", "OUTPUT"}:
                current.setdefault(head.lower() + "s", []).append(_parse_io(rest))
            elif head == "ENTRYPOINT":
                current.setdefault("entrypoints", []).append(_parse_entrypoint(rest))
            elif head == "INSTALL":
                status, _, package = rest.partition(" ")
                install = {"status": status}
                if package:
                    install["package"] = package
                current["install"] = install
            elif head == "MATURITY":
                level, _, grade = rest.partition(" ")
                maturity = {"level": level}
                if grade:
                    maturity["grade"] = grade
                current["maturity"] = maturity
            elif head == "SIBLING":
                parts = rest.split()
                if len(parts) >= 2:
                    sibling = {"id": parts[0], "relation": parts[1]}
                    if len(parts) > 2:
                        sibling["target"] = parts[2]
                    current.setdefault("siblings", []).append(sibling)
            elif head == "USE_WHEN":
                current.setdefault("useWhen", []).append(_unquote(rest))
            elif head == "DO_NOT_USE_WHEN":
                current.setdefault("doNotUseWhen", []).append(_unquote(rest))
            elif head == "WORKSTREAM":
                name, _, glob = rest.partition(" ")
                current.setdefault("workstreamHints", {}).setdefault(name, []).append(_unquote(glob))
            continue

        if section == "placement" and current is not None:
            if head == "HOME":
                current["home"] = rest
            elif head == "SHAPE":
                current["shape"] = rest
            elif head == "RUNTIME_OWNER":
                current["runtimeOwner"] = rest
            elif head == "ADOPT":
                current["adopt"].append(rest)
        elif section == "policy" and current is not None:
            if head == "DESCRIPTION_IS_PROJECTION":
                current["descriptionIsProjection"] = rest == "true"
            elif head == "README_AUTHORITY":
                current["readmeAuthority"] = rest
            elif head == "UNKNOWN_POLICY":
                current["unknownPolicy"] = rest
            elif head == "EFFECT":
                current["effectModel"] = rest
            elif head == "ANALYZER_DEBT":
                current["analyzerTreatAsDebtUntilInterview"] = rest == "true"
            elif head == "ADOPT_DOES_NOT_IMPLY_HOME":
                current["adoptDoesNotImplyHome"] = rest == "true"
            elif head == "FORBID":
                current["forbid"].append(rest)
            elif head == "ACTION":
                name, _, target = rest.partition(" ")
                item = {"do": name}
                if target:
                    item["target"] = target
                current["actions"].append(item)
        elif section == "evidence" and current is not None:
            if head == "KIND":
                current["kind"] = rest
            elif head == "PATH":
                current["path"] = rest
            elif head == "PRECEDENCE":
                current["precedence"] = int(rest)
            elif head == "ROLE":
                current["role"] = rest
            elif head == "DIGEST":
                current["digest"] = rest
            elif head == "SSOT_KIND":
                current["ssotKind"] = rest
        elif section == "relation" and current is not None:
            if head == "KIND":
                current["kind"] = rest
            elif head == "SUBJECT":
                current["subject"] = rest
            elif head == "CANONICAL":
                current["canonical"] = rest
            elif head == "RATIONALE":
                current["rationale"] = _unquote(rest)
            elif head == "REASON":
                current["knownDivergent"] = {"reason": _unquote(rest)}
        elif section == "receipt" and current is not None:
            if head == "DIGEST":
                path, _, digest = rest.partition(" ")
                current["sourceDigests"].append({"path": path, "digest": digest})
        elif section == "conflict" and current is not None:
            if head == "VALUE":
                source, _, value = rest.partition(" ")
                current["values"].append({"source": source, "value": _unquote(value)})
        elif section == "questions":
            if head == "QUESTION":
                document["questions"].append(_unquote(rest))

    if not document["conflicts"]:
        del document["conflicts"]
    if not document["policy"]["actions"]:
        del document["policy"]["actions"]
    return document


def render_findings(findings: Sequence[Finding], output_format: str) -> str:
    if output_format == "json":
        return json.dumps(
            {
                "schema": SCHEMA_CHECK,
                "status": "failed" if findings else "passed",
                "findings": [item.as_dict() for item in findings],
            },
            indent=2,
            sort_keys=True,
        )
    if not findings:
        return "ok"
    return "\n".join(f"{item.code} {item.path}: {item.message}" for item in findings)


def _read_json_or_dsl(path: Path) -> Any:
    text = path.read_text(encoding="utf-8")
    if path.suffix in {".dsl", ".project"} or text.lstrip().startswith("DOCUMENT PROJECT"):
        return parse_dsl(text)
    return json.loads(text)


def compose_from_paths(
    answers_path: Path | None,
    evidence_path: Path | None,
    typed_path: Path | None = None,
) -> tuple[dict[str, Any], list[Finding]]:
    answers: dict[str, Any] | None = None
    evidence: dict[str, Any] | None = None
    if answers_path is not None:
        answers = normalize_interview(load_json(answers_path))
    if evidence_path is not None:
        evidence = load_json(evidence_path)
    if typed_path is not None:
        payload = _read_json_or_dsl(typed_path)
        if isinstance(payload, dict) and payload.get("schema") == SCHEMA_DOCUMENT:
            return payload, validate_decision(payload)
        ingested = ingest_typed(payload, typed_path.name)
        kind = ingested["kind"]
        body = ingested["payload"]
        if kind == "document":
            return body, validate_decision(body)  # type: ignore[arg-type]
        if kind == "interview":
            answers = body  # type: ignore[assignment]
        elif kind == "evidence":
            if evidence and evidence.get("sources"):
                combined = dict(evidence)
                combined["sources"] = list(evidence.get("sources") or []) + list(body.get("sources") or [])  # type: ignore[union-attr]
                evidence = combined
            else:
                evidence = body  # type: ignore[assignment]
    interview_findings: list[Finding] = []
    if answers is not None:
        interview_findings = validate_interview(answers, partial=evidence is not None)
    evidence_findings: list[Finding] = []
    if evidence is not None:
        evidence_findings = validate_evidence_index(evidence)
    early = interview_findings + evidence_findings
    if early:
        return {}, early
    if answers is None and evidence is None:
        return {}, [Finding("PROJECT-EVIDENCE-001", "interview answers or an evidence index is required")]
    document = classify(answers, evidence)
    return document, validate_decision(document)


def run_interview(
    answers_path: Path | None,
    evidence_path: Path | None,
    output: Path | None,
    output_format: str,
) -> int:
    if answers_path is None and evidence_path is None:
        questionnaire = load_questionnaire()
        answers: dict[str, Any] = {"schema": SCHEMA_INTERVIEW}
        for question in questionnaire["questions"]:
            prompt = f"{question['prompt']}\n> "
            raw = input(prompt)
            value = parse_answer(question, raw)
            if value is not None:
                answers[question["id"]] = value
        findings = validate_interview(answers)
        if findings:
            print(render_findings(findings, "text"), file=sys.stderr)
            return 1
        document = classify(answers, None)
        decision_findings = validate_decision(document)
        if decision_findings:
            print(render_findings(decision_findings, "text"), file=sys.stderr)
            return 1
        payload = render_dsl(document) if output_format == "dsl" else dump_json(document)
        if output:
            output.write_text(payload, encoding="utf-8")
        else:
            sys.stdout.write(payload)
        return 0
    document, findings = compose_from_paths(answers_path, evidence_path, None)
    if findings:
        print(render_findings(findings, "text"), file=sys.stderr)
        return 1
    payload = render_dsl(document) if output_format == "dsl" else dump_json(document)
    if output:
        output.write_text(payload, encoding="utf-8")
    else:
        sys.stdout.write(payload)
    return 0


def cmd_questions() -> int:
    questionnaire = load_questionnaire()
    for index, question in enumerate(questionnaire["questions"], start=1):
        required = "required" if question.get("required") else "optional"
        print(f"{index:02d}. [{question['id']}] ({required}) {question['prompt']}")
    return 0


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="project_ssot", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    interview = sub.add_parser("interview", help="ask the questionnaire or compose saved answers")
    interview.add_argument("--answers", type=Path, help="JSON interview answers")
    interview.add_argument("--evidence", type=Path, help="listed evidence index JSON")
    interview.add_argument("--output", type=Path, help="write the project document")
    interview.add_argument("--format", choices=("json", "dsl"), default="json")
    classify_cmd = sub.add_parser("classify", help="compose interview and/or evidence into a document")
    classify_cmd.add_argument("answers", type=Path, nargs="?", help="interview JSON, evidence index, or typed source")
    classify_cmd.add_argument("--evidence", type=Path, help="listed evidence index JSON")
    classify_cmd.add_argument("--format", choices=("json", "dsl"), default="json")
    suggest = sub.add_parser("suggest", help="emit DOCUMENT PROJECT, composing typed JSON if needed")
    suggest.add_argument("document", type=Path, help="project document, interview, evidence index, or intent.json")
    suggest.add_argument("--answers", type=Path, help="interview overlay")
    suggest.add_argument("--evidence", type=Path, help="listed evidence index JSON")
    suggest.add_argument("--format", choices=("json", "dsl"), default="dsl")
    validate = sub.add_parser("validate", help="validate a project, interview, or evidence document")
    validate.add_argument("document", type=Path)
    validate.add_argument("--format", choices=("text", "json"), default="text")
    sub.add_parser("questions", help="print the questionnaire")
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    args = _parser().parse_args(list(argv) if argv is not None else None)
    if args.command == "questions":
        return cmd_questions()
    if args.command == "interview":
        return run_interview(args.answers, args.evidence, args.output, args.format)
    if args.command == "classify":
        document, findings = compose_from_paths(None, args.evidence, args.answers)
        if findings:
            print(render_findings(findings, "text"), file=sys.stderr)
            return 1
        sys.stdout.write(render_dsl(document) if args.format == "dsl" else dump_json(document))
        return 0
    if args.command == "suggest":
        document, findings = compose_from_paths(args.answers, args.evidence, args.document)
        if findings:
            print(render_findings(findings, "text"), file=sys.stderr)
            return 1
        sys.stdout.write(render_dsl(document) if args.format == "dsl" else dump_json(document))
        return 0
    payload = _read_json_or_dsl(args.document)
    schema = payload.get("schema") if isinstance(payload, dict) else None
    if schema == SCHEMA_INTERVIEW:
        findings = validate_interview(payload)
    elif schema == SCHEMA_EVIDENCE:
        findings = validate_evidence_index(payload)
    else:
        findings = validate_decision(payload)
    print(render_findings(findings, args.format))
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
