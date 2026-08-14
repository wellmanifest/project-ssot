# SUGGEST

## Purpose

Emit the text DSL projection of a validated project document so agents and
humans can review the same facts without inventing a second language. When
the input is already-typed JSON (interview, evidence index, `intent.json`,
`dsl-manifest.json`), compose the document first.

## Syntax

```bash
PYTHONPATH=src python3 -m project_ssot suggest examples/ssot-pack.project.json
PYTHONPATH=src python3 -m project_ssot suggest examples/ssot-pack.interview.json --evidence examples/ssot-pack.evidence.json
PYTHONPATH=src python3 -m project_ssot suggest examples/widget.intent.json --answers examples/widget.interview.json
```

## Inputs

A canonical JSON project document, a `.dsl` / `DOCUMENT PROJECT` text file,
or already-typed source JSON. Not a live repository path to walk.

## Outputs

The line-oriented projection (`DOCUMENT PROJECT`). Canonical JSON remains
the source of truth; text is a projection declared in the DSL manifest.
`--format json` emits the AST instead.

## Errors

Validation failures are printed and the command exits 1. See `VALIDATE`.

## Examples

```bash
PYTHONPATH=src python3 -m project_ssot suggest examples/ssot-pack.project.json | head
```
