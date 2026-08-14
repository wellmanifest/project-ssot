# PROJECT-CONFLICT-001

## Meaning

Two typed evidence sources disagree on an identity field (id, name, version,
home, shape, runtimeOwner, purpose) and the interview did not name a winner.

## Cause

README purpose vs `dsl-manifest` purpose, or packaging name vs display name,
without `purpose_authority` or an interview value for that field.

## Resolution

Fill the interview field, or set `purpose_authority` to a listed source id
(for example `dsl-manifest`). The classifier records the conflict with
`resolvedBy` when the interview wins. Unresolved conflicts fail closed.
