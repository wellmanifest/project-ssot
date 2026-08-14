# AGENTS.md

This repository is the generic **project description** SSOT layer for
Wellmanifest. Use it when a user wants one correct project description
assembled from code, artifacts, and specs that have already been typed.

## Before changing anything in a target repo

1. Do **not** crawl the live tree from this pack. Accept interview JSON,
   `intent.json`, `dsl-manifest.json`, or a listed evidence index.
2. Do **not** treat code2llm TOON or `map.toon.yaml` as debt.
3. Do **not** treat README as authority. The JSON AST is the SSOT;
   README is a projection (facade / generated_mirror / allowed_divergence).
4. Classify. Read `HOME`, `SHAPE`, `ADOPT`, `CONFLICT`, and `QUESTION`.
5. Only then propose edits in a generator (semcod/code2llm). This pack is
   propose-only: it never authorizes README rewrites, crawls, or merges.

```bash
PYTHONPATH=src python3 -m project_ssot questions
PYTHONPATH=src python3 -m project_ssot interview --answers <answers.json> --evidence <index.json> --format dsl
PYTHONPATH=src python3 -m project_ssot validate <project.json>
```

## Classification rules you must not invert

- `adopt: wellmanifest/{dsl,ssot,new-project,logs}` does **not** set
  `home=wellmanifest`.
- `shape=runtime_service` or `both` → `home` must not be `wellmanifest`.
- Conflicting identity fields without an interview winner → fail closed.
- Analyzer artifacts stay `role=evidence` until a human confirms debt.
- Dual description (README vs schema purpose) is `allowed_divergence` or
  a `facade`, not two authorities.

## Relation to wellmanifest/dsl

Reuse the kernel. Canonical documents are JSON AST. `DOCUMENT PROJECT`
is a projection. Do not add a second parser stack. The pack manifest is
`dsl-manifest.json` (`wellmanifest.project-ssot`).

If `wellmanifest/dsl` is available locally, optional extra check:

```bash
python3 /path/to/dsl/src/dsl_check.py validate dsl-manifest.json
```

Digest-bind artifacts after you change a normative file.

## Relation to other Wellmanifest repos

- `ssot` classifies duplicated *code* trees. This pack classifies the
  *project description* and reuses ssot kinds on README/docs.
- `new-project` owns `placement.home|shape|runtimeOwner|adopt`. Reuse
  those names. Do not invent a parallel vocabulary.
- `logs` may record receipts of "description generated from these digests".
- Do not clone code2llm / `generate_readme` here. A later generator ADOPTS
  this schema.

## Working in this repository

- Keep executable source in `src/` and tests in `tests/`.
- Questionnaire text lives in `questions/interview.json`.
- Example documents must stay generic method illustrations. Do not copy
  product secrets.
- Run `PYTHONPATH=src python3 -m unittest discover -s tests` before
  claiming the classifier changed.

English is the working language. A short Polish intro in `README.md` is
intentional.
