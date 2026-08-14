# PROJECT-README-001

## Meaning

README is treated as description authority, or an `allowed_divergence`
relation has no `KNOWN_DIVERGENT` reason and no question.

## Cause

Someone edited README as the project SSOT, or set `readmeAuthority` to
something other than `generated_from_document` / `none`.

## Resolution

Keep the JSON AST canonical. Classify README as `facade`,
`generated_mirror`, or `allowed_divergence`. A later generator may emit
README FROM this document; that generator is out of scope for this pack.
