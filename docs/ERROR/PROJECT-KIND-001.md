# PROJECT-KIND-001

## Meaning

The document uses an unknown schema, field, kind, action, packaging value,
or fact key.

## Cause

A typo, a competing vocabulary, or a document that is not a project-ssot
interview, evidence index, or project document. `unknownPolicy=reject`.

## Resolution

Use only the kinds declared in `schemas/project-ssot.schema.json`. Reuse
new-project `placement` (`home`, `shape`, `runtimeOwner`, `adopt`). Do not
invent a parallel language; this pack sits on `wellmanifest/dsl`.
