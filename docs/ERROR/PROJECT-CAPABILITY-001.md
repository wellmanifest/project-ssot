# PROJECT-CAPABILITY-001

The `capability` block is malformed, or absent from a `wellmanifest.project-ssot/v2` document.

## Why this is an error

A project SSOT that says who owns a repository but not what it can do is not
selectable. A consumer choosing between two hundred projects needs the shape of
the work, not the shape of the org chart.

`capability` is required by v2 and absent from v1. A composition that cannot fill
it MUST emit v1 and record a question, never invent one: composition is
propose-only.

## Vocabulary

`verbs` is closed, and capped at eight. A project claiming more than eight verbs
is under-decomposed, and the cap is the finding that says so.

## Fix

Answer `capability_verbs`, `capability_use_when`, `capability_do_not_use_when` in
the interview, then re-run `classify`.
