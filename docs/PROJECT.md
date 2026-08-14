# PROJECT

## Purpose

Declare a single source of truth for a project's identity, purpose, adopted
standards, and evidence. The document composes typed sources. It does not
authorize edits, crawls, or README rewrites.

## Syntax

Canonical form is UTF-8 JSON conforming to
`schemas/project-ssot.schema.json`. The text projection starts with
`DOCUMENT PROJECT` and is emitted by `project_ssot suggest`.

```text
DOCUMENT PROJECT
ID <identifier>
NAME "<name>"
VERSION <semver>
SCHEMA wellmanifest.project-ssot/v1
PURPOSE "<one sentence>"
PLACEMENT
  HOME wellmanifest|subactor|semcod
  SHAPE domain_pack|runtime_service|both
  RUNTIME_OWNER wellmanifest|subactor|semcod
  ADOPT wellmanifest/<pack>
POLICY project
  DESCRIPTION_IS_PROJECTION true
  README_AUTHORITY generated_from_document
  UNKNOWN_POLICY reject
  EFFECT propose-only
  FORBID treat_readme_as_authority
EVIDENCE <id>
  KIND dsl-manifest|intent|readme|analyzer-map|...
RELATION <id>
  KIND facade|generated_mirror|allowed_divergence
```

## Inputs

A project document, typed interview answers, a listed evidence index,
`intent.json`, or `dsl-manifest.json`. Analyzer reports are evidence, not
classifications. This pack does not crawl a repository.

## Outputs

A propose-only `wellmanifest.project-ssot/v1` document and optional
`DOCUMENT PROJECT` text projection.

## Errors

See `docs/ERROR/` for `PROJECT-KIND-001`, `PROJECT-CONFLICT-001`,
`PROJECT-EVIDENCE-001`, `PROJECT-PURPOSE-001`, `PROJECT-ADOPT-001`,
`PROJECT-README-001`, `PROJECT-NOISE-001`, and `PROJECT-SHAPE-001`.
HOMEing a runtime service in wellmanifest is
`docs/CRITICAL/PROJECT-HOME-001.md`.

## Examples

`examples/ssot-pack.project.json` encodes wellmanifest/ssot as a domain pack.
`examples/widget.project.json` encodes a fictional subactor runtime that
ADOPTs wellmanifest packs without HOMEing there.
