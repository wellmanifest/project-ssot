# PROJECT-ADOPT-001

## Meaning

Adopted standards are missing, copied instead of mapped, or used to infer
`home=wellmanifest`.

## Cause

`adopt: wellmanifest/dsl` was treated as "this repo HOMEs in wellmanifest",
or a mapping omitted `relation`.

## Resolution

Keep `placement.adopt` as `wellmanifest/<pack>` ids. Keep `adopted[]` as
dsl-manifest-style mappings (`implements`, `maps-to`, `compatible-with`,
`extends`). `adoptDoesNotImplyHome` must stay true.
