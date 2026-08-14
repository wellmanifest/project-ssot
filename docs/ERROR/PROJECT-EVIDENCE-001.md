# PROJECT-EVIDENCE-001

## Meaning

The evidence index is missing, uses an unsafe path, has an invalid digest,
or is not `wellmanifest.project-ssot/evidence-index/v1`.

## Cause

A caller passed a live repository root instead of a listed artifact index,
or a path that is absolute or contains `..`.

## Resolution

List already-typed sources with repository-relative paths. This pack MUST
NOT crawl a tree. Map `intent.json` `placement` when present. A later
generator may produce the index; `suggest` only composes it.
