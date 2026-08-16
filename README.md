# wellmanifest/project-ssot

Warstwa do złożenia **jednego opisu projektu** (SSOT) z już wpisanego JSON-a:
intent, manifest DSL, wywiad, indeks artefaktów. Opis kanoniczny jest dokumentem
DSL; README jest projekcją, nie drugim źródłem prawdy.

A generic **project description** layer. It interviews, classifies typed
evidence, and emits a propose-only DSL document. It does not crawl a live
repository, edit README, or run a generator.

This repository is a **domain pack** on [`wellmanifest/dsl`](https://github.com/wellmanifest/dsl).
It does not invent a competing language. Canonical documents are JSON AST
(`wellmanifest.project-ssot/v1`). `DOCUMENT PROJECT` is a projection.

## Why this exists

Humans write competing project descriptions: README vs `dsl-manifest.json` vs
`intent.json` vs analyzer TOON. Analyzers are noisy. Adopting
`wellmanifest/dsl` is not the same as HOMEing the repo in wellmanifest.
A project SSOT must **ask** before it treats a report or a README as truth.

Lessons encoded here (method, not product-specific code):

1. The JSON AST is the SSOT. Generated description is a **projection**.
   Do not keep a second competing README as authority.
2. `placement.home` / `shape` / `runtimeOwner` / `adopt` reuse
   `wellmanifest/new-project` vocabulary. `adopt: wellmanifest/dsl` does
   **not** imply `home: wellmanifest`.
3. `shape=runtime_service` (or `both`) must not use `home=wellmanifest`.
   wellmanifest owns standards; product daemons HOME in `subactor` or `semcod`.
4. Evidence sources have precedence. If they conflict and the interview did
   not resolve the field, fail closed (`PROJECT-CONFLICT-001`).
5. Analyzer artifacts (code2llm TOON, `map.toon.yaml`) are **evidence**,
   never debt, until interview (ssot lesson).
6. Reuse ssot kinds on description artifacts: README as `facade` or
   `generated_mirror`; marketing copy vs schema purpose as
   `allowed_divergence`.
7. A later generator (semcod / code2llm) may crawl a repo and emit the
   evidence index. This pack only composes already-typed JSON.

## Interview → DSL

```text
questions/interview.json
        │  typed answers (wellmanifest.project-ssot/interview/v1)
        │  listed evidence index (wellmanifest.project-ssot/evidence-index/v1)
        ▼
   project_ssot classify   ← deterministic, not an LLM
        │  JSON AST (wellmanifest.project-ssot/v1)
        ▼
   project_ssot suggest    ← DOCUMENT PROJECT projection
        │
        ▼
   project_ssot validate   ← fail closed
```

`wellmanifest/dsl` owns the kernel (`dsl-manifest.json` contract,
`dsl_check`, effect/LLM rules). This pack owns the project document,
questionnaire, evidence composition, and classifier. Effect model:
**propose-only**. `unknownPolicy=reject`.

## CLI

```bash
PYTHONPATH=src python3 -m project_ssot questions
PYTHONPATH=src python3 -m project_ssot interview --answers examples/ssot-pack.interview.json --evidence examples/ssot-pack.evidence.json --format dsl
PYTHONPATH=src python3 -m project_ssot classify examples/ssot-pack.interview.json --evidence examples/ssot-pack.evidence.json
PYTHONPATH=src python3 -m project_ssot suggest examples/ssot-pack.project.json
PYTHONPATH=src python3 -m project_ssot suggest examples/widget.intent.json --answers examples/widget.interview.json
PYTHONPATH=src python3 -m project_ssot validate examples/ssot-pack.project.json
PYTHONPATH=src python3 -m unittest discover -s tests
```

`suggest` maps already-typed JSON (interview, evidence index, `intent.json`,
`dsl-manifest.json`) to `DOCUMENT PROJECT`. It does not walk a tree.

## Placement (HOME vs ADOPT)

| Field | Vocabulary | Meaning |
| --- | --- | --- |
| `placement.home` | `wellmanifest` \| `subactor` \| `semcod` | Who owns the repo |
| `placement.shape` | `domain_pack` \| `runtime_service` \| `both` | What it is |
| `placement.runtimeOwner` | same enum as `home` (omit to inherit) | Who runs the CLI/daemon |
| `placement.adopt` | `wellmanifest/<pack>` ids | Follow those packs; **ADOPT ≠ HOME** |

Same object as `new-project` `intent.json` `placement`. `shape=runtime_service` + `home=wellmanifest` is rejected. `"w ramach wellmanifest"` means ADOPT, not HOME.

## Example: wellmanifest/ssot

`examples/ssot-pack.project.json` encodes the ssot domain pack:

- `home=wellmanifest`, `shape=domain_pack` (a standard, not a daemon)
- README vs `dsl-manifest` purpose conflict resolved by interview
- README `facade` + `allowed_divergence` (Polish intro vs schema purpose)
- `docs/SSOT.md` as `generated_mirror`
- listed `map.toon.yaml` stays evidence, not debt

`examples/widget.project.json` is a tiny fictional runtime: `home=subactor`,
`adopt` includes `wellmanifest/dsl` and `wellmanifest/logs`.

## Layout

```text
questions/     questionnaire catalog
schemas/       interview + evidence index + document JSON Schema
docs/          command, error, and critical pages
examples/      ssot-pack + widget + invalid fixtures
src/project_ssot.py    interview, classify, suggest, validate
tests/         deterministic checks
dsl-manifest.json   wellmanifest.dsl/manifest/v1 for this pack
```

## Related

- [`wellmanifest/dsl`](https://github.com/wellmanifest/dsl) — kernel and conformance
- [`wellmanifest/ssot`](https://github.com/wellmanifest/ssot) — duplication kinds reused here for README/docs
- [`wellmanifest/new-project`](https://github.com/wellmanifest/new-project) — `placement` vocabulary
- [`wellmanifest/logs`](https://github.com/wellmanifest/logs) — receipt of digests that produced the description
- code2llm / generate_readme — evidence producer / later projection, not this pack

## Commercial registries

Classify public price/entitlement files as a **facade** of an adopted pack
catalog (example: portal `plans.json` → `wellmanifest/policy-dsl`
`offer-catalog.json`). Allowed divergence is presentation-only. Amount and
entitlement drift is not an interview outcome — it is a failed gate.

