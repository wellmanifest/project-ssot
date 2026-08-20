# PROJECT-CAPABILITY-002

`capability.useWhen` or `capability.doNotUseWhen` is missing or empty.

## Why this is an error

These two lists are the only fields in the document that no analyzer can ever
derive, and they are the fields that decide whether a consumer picks the right
project.

`doNotUseWhen` in particular exists to defuse a name. A repository called
`registry` that is a tenant catalogue rather than a registry of repositories will
be mis-selected every time until the document says so in its own words.

## Fix

State at least one concrete situation for each, and name the alternative to reach
for instead.
