# PROJECT-HOME-001

## Risk

A `runtime_service` is HOMEd in wellmanifest. That turns a standards org
into a product-daemon host. wellmanifest owns patterns; CLIs and daemons
HOME in `subactor` or `semcod`. `"w ramach wellmanifest"` means ADOPT,
not HOME.

## Detection

`placement.shape` is `runtime_service` and `placement.home` is
`wellmanifest` — the same rule as new-project `governance_check.py`.
Also raised when `home` is not in `wellmanifest|subactor|semcod`, or
when `placement` lacks `home` and `shape`.

## Remediation

Move the runtime HOME to `subactor` or `semcod`. ADOPT
`wellmanifest/{dsl,logs,new-project,project-ssot}` as mappings. A
`domain_pack` with a small document CLI (`ssot classify`,
`project_ssot validate`) MAY stay `home=wellmanifest`.

## Verification

`project_ssot validate` passes, `shape=runtime_service` documents have
non-wellmanifest `home`, and `placement.adopt` still lists wellmanifest
packs.
