# INTERVIEW

## Purpose

Ask the questions that settle project identity, HOME vs ADOPT, purpose, and
README role before any generated description is treated as truth.

## Syntax

```bash
PYTHONPATH=src python3 -m project_ssot interview
PYTHONPATH=src python3 -m project_ssot interview --answers examples/ssot-pack.interview.json --evidence examples/ssot-pack.evidence.json --format dsl
PYTHONPATH=src python3 -m project_ssot questions
```

## Inputs

Interactive stdin answers, or a JSON document conforming to
`schemas/project-ssot-interview.schema.json`. Optional listed evidence index
conforming to `schemas/project-ssot-evidence-index.schema.json`. The question
catalog is `questions/interview.json`.

## Outputs

A canonical `wellmanifest.project-ssot/v1` document (`--format json`) or its
text projection (`--format dsl`).

## Errors

Invalid answers fail with `PROJECT-KIND-001`, `PROJECT-HOME-001`,
`PROJECT-SHAPE-001`, `PROJECT-ADOPT-001`, `PROJECT-PURPOSE-001`, or
`PROJECT-README-001`. The command does not crawl a tree or treat analyzer
output as debt.

## Examples

```bash
PYTHONPATH=src python3 -m project_ssot interview --answers examples/widget.interview.json --evidence examples/widget.evidence.json --format dsl
```

That interview must emit `placement.home=subactor` and
`placement.adopt` including `wellmanifest/dsl` without setting home to
wellmanifest. Interactive answers for home/shape/runtimeOwner/adopt are
folded into the same `placement` object as new-project `intent.json`.
