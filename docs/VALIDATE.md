# VALIDATE

## Purpose

Fail closed on an invalid interview, evidence index, or project document.

## Syntax

```bash
PYTHONPATH=src python3 -m project_ssot validate examples/ssot-pack.project.json
PYTHONPATH=src python3 -m project_ssot validate examples/invalid/runtime-home-wellmanifest.project.json --format json
```

## Inputs

A JSON or text project document, or an interview / evidence-index JSON file.

## Outputs

`ok` or a list of findings. `--format json` emits
`wellmanifest.project-ssot/check-result/v1`.

## Errors

| Code | When |
| --- | --- |
| `PROJECT-KIND-001` | unknown schema, field, kind, action, or forbid |
| `PROJECT-CONFLICT-001` | evidence sources disagree and interview did not resolve |
| `PROJECT-EVIDENCE-001` | missing index, unsafe path, or invalid digest |
| `PROJECT-PURPOSE-001` | missing one-sentence purpose |
| `PROJECT-ADOPT-001` | adopt is not a mapping, or adopt is used to infer home |
| `PROJECT-README-001` | README treated as authority, or missing divergence reason |
| `PROJECT-NOISE-001` | analyzer treated as debt or identity |
| `PROJECT-SHAPE-001` | unknown shape or runtimeOwner |
| `PROJECT-HOME-001` | `runtime_service` HOMEd in wellmanifest (governance rule) |

## Examples

`examples/invalid/runtime-home-wellmanifest.project.json` must fail with
`PROJECT-HOME-001`.
