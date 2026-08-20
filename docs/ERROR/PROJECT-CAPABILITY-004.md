# PROJECT-CAPABILITY-004

An entry in `capability.siblings` is malformed, or a `superseded-by` /
`supersedes` relation does not name its counterpart in `target`.

## Why this is an error

`superseded-by` without a target says a project is obsolete without saying what
replaced it. That is strictly worse than silence: it removes an option without
offering one.

`overlaps` carries the same weight in the other direction — two projects that do
adjacent things need the note that separates them, or a consumer will pick by
name similarity.
