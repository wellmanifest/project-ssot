# CLASSIFY

## Purpose

Deterministically compose typed interview answers and a listed evidence index
into a project SSOT document. Classification is ordered: interview first,
then new-project / dsl-manifest / ssot / docs / packaging, analyzer last.
Conflicts without an interview winner fail closed.

## Syntax

```bash
PYTHONPATH=src python3 -m project_ssot classify examples/ssot-pack.interview.json --evidence examples/ssot-pack.evidence.json
PYTHONPATH=src python3 -m project_ssot classify examples/ssot-pack.interview.json --evidence examples/ssot-pack.evidence.json --format dsl
```

## Inputs

A valid `wellmanifest.project-ssot/interview/v1` document and/or a
`wellmanifest.project-ssot/evidence-index/v1` listing. Also accepts
already-typed `intent.json` or `dsl-manifest.json` as the positional file.

## Outputs

One project document. Identity fields:

| Condition | Result |
| --- | --- |
| Interview `placement.home` / `shape` / `runtimeOwner` | Same object as new-project intent.placement |
| `placement.adopt` lists wellmanifest packs | Mappings only; home is unchanged |
| README vs schema purpose differ, interview resolves | Keep interview purpose; record `allowed_divergence` |
| Same conflict, no interview | `PROJECT-CONFLICT-001` |
| Analyzer listed | `role=evidence`; never identity |
| `shape=runtime_service` and `home=wellmanifest` | `PROJECT-HOME-001` (same rule as governance_check) |

Document-level `POLICY project` is always emitted.

## Errors

Interview or evidence errors: `PROJECT-KIND-001`, `PROJECT-EVIDENCE-001`,
`PROJECT-CONFLICT-001`. Runtime HOMEd in wellmanifest: `PROJECT-HOME-001`.

## Examples

`examples/ssot-pack.evidence.json` without answers fails closed on purpose
and name. The matching interview resolves both.
