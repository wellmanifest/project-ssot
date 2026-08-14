# PROJECT-SHAPE-001

## Meaning

`placement.shape` or `placement.runtimeOwner` is missing or not in the
closed new-project vocabulary.

## Cause

A competing word was invented (`app`, `daemon`, `library`, `standard`)
instead of `domain_pack` | `runtime_service` | `both`.

## Resolution

Use `intent.json` `placement` as declared in wellmanifest/new-project:
`shape` is `domain_pack` | `runtime_service` | `both`. `runtimeOwner` uses
the same enum as `home` and may be omitted to inherit `home`.
