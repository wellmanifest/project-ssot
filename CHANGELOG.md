# Changelog

All notable changes to this project are documented in this file.

## [0.2.0-dev]

- Add the `capability` block (`wellmanifest.project-ssot/v2`): `verbs`,
  `keywords`, `inputs`, `outputs`, `entrypoints`, `install`, `maturity`,
  `siblings`, `useWhen`, `doNotUseWhen`, `stacks`, `workstreamHints`.
  `verbs`, `useWhen` and `doNotUseWhen` are required, because no analyzer can
  derive them and a wrong guess is what makes a consumer select the wrong
  project. `verbs` is a closed vocabulary capped at eight.
- Open `placement.home`. It was a closed enum of three literal organization
  names, replicated across schemas and Python validators, so a fourth adopter
  could not produce a valid document at all. It is now a registry-backed
  identifier: `registry/homes.json` lists known homes, an unknown but
  well-formed home reports `PROJECT-HOME-002` (warning), and adoption never
  requires editing this pack's schemas.
- `classify` composes `capability` from interview answers and emits v2. With
  the human-only answers unanswered it emits v1 plus a question, never an
  invented capability: composition stays propose-only.
- Extend the interview with ten `capability_*` questions.
- Carry `capability` through the `DOCUMENT PROJECT` text projection as a
  `CAPABILITY` section; the projection stays lossless round-trip.
- New findings: `PROJECT-CAPABILITY-001..004`, `PROJECT-HOME-002`.
- Accept both `wellmanifest.project-ssot/v2` and `/v1` documents.

## [0.1.0-dev]

- Bootstrap the project-ssot domain pack on wellmanifest/dsl: interview,
  listed evidence index, classifier, document schema, `DOCUMENT PROJECT`
  projection, and ssot-pack / widget examples.
- Reuse new-project `intent.json` `placement` (`home`, `shape`,
  `runtimeOwner`, `adopt`). No parallel top-level HOME fields. `shape=
  runtime_service` must not HOME wellmanifest.
