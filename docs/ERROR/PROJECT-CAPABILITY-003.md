# PROJECT-CAPABILITY-003

An entry in `capability.entrypoints` is incomplete or malformed.

## Why this is an error

An entrypoint that cannot be executed is worse than no entrypoint: it sends a
consumer down a path that fails. Every entry needs `kind`, `name` and a literal
`invoke` string.

`install.status: src-only` means the invocation needs `PYTHONPATH` or an
equivalent. Stating the status without stating the real invocation leaves a
consumer to guess, and it will guess the installed-package form.

## Verification

Declared entrypoints are claims. They are proven separately by a
cross-reference check that confirms the command exists in source.
