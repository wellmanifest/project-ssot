# PROJECT-HOME-002

`placement.home` is well formed but is not listed in `registry/homes.json`.

## Why this is a warning and not an error

HOME used to be a closed enum of three literal organization names, baked into
JSON Schema and into Python validators across many packs. A fourth party could
not produce a valid document at all — an abstract standard whose machine-checkable
schema hardcodes its first adopters is not abstract.

So an unknown home is reported, not rejected. Adoption must never require editing
the standard's schemas.

## Fix

Add an entry to `registry/homes.json`. A home id matches
`^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$`.
