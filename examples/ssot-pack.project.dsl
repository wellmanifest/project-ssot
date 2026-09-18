DOCUMENT PROJECT
ID wellmanifest.ssot
NAME "Wellmanifest SSOT decision DSL"
VERSION 0.2.0-dev
SCHEMA wellmanifest.project-ssot/v2
PURPOSE "Interview-driven classification of duplicated trees into propose-only SSOT decisions"

PLACEMENT
  HOME wellmanifest
  SHAPE domain_pack
  RUNTIME_OWNER wellmanifest
  ADOPT wellmanifest/dsl
  ADOPT wellmanifest/ssot
  ADOPT wellmanifest/new-project
  ADOPT wellmanifest/modularity
  ADOPT wellmanifest/poa

POLICY project
  DESCRIPTION_IS_PROJECTION true
  README_AUTHORITY generated_from_document
  UNKNOWN_POLICY reject
  EFFECT propose-only
  ANALYZER_DEBT false
  ADOPT_DOES_NOT_IMPLY_HOME true
  FORBID treat_readme_as_authority
  FORBID treat_analyzer_as_debt
  FORBID infer_home_from_adopt
  FORBID runtime_service_in_wellmanifest
  FORBID crawl_live_repository
  FORBID copy_adopted_standard
  FORBID keep_competing_readme_authority
  ACTION use_document_as_ssot
  ACTION map_adopted_standard
  ACTION record_evidence_digest
  ACTION keep_readme_as_facade README.md
  ACTION generate_readme_from_document
  ACTION ignore_analyzer_until_interview
  ACTION document_known_divergent

OWNER repository github:wellmanifest/ssot

ADOPTED wellmanifest.dsl implements https://github.com/wellmanifest/dsl

ADOPTED wellmanifest.modularity compatible-with https://github.com/wellmanifest/modularity

ADOPTED wellmanifest.new-project maps-to

ADOPTED wellmanifest.poa compatible-with https://github.com/wellmanifest/poa

ADOPTED wellmanifest.ssot maps-to

EVIDENCE dsl-manifest
  KIND dsl-manifest
  PATH dsl-manifest.json
  PRECEDENCE 70
  ROLE authority
  DIGEST sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa

EVIDENCE agents
  KIND agents
  PATH AGENTS.md
  PRECEDENCE 78
  ROLE authority

EVIDENCE readme
  KIND readme
  PATH README.md
  PRECEDENCE 48
  ROLE projection_candidate
  SSOT_KIND facade

EVIDENCE docs-ssot
  KIND docs
  PATH docs/SSOT.md
  PRECEDENCE 50
  ROLE evidence
  SSOT_KIND generated_mirror

EVIDENCE ssot-decision
  KIND ssot-decision
  PATH examples/c2004.ssot.json
  PRECEDENCE 60
  ROLE authority

EVIDENCE analyzer-map
  KIND analyzer-map
  PATH reports/map.toon.yaml
  PRECEDENCE 10
  ROLE evidence

RELATION readme.facade
  KIND facade
  SUBJECT README.md
  CANONICAL this-document
  RATIONALE "README is a facade over this project-ssot document. Do not keep a second competing README as authority. A later generator may emit README FROM this AST."

RELATION readme.divergence
  KIND allowed_divergence
  SUBJECT README.md
  CANONICAL $.purpose
  RATIONALE "Polish README intro and English marketing tone may differ from the schema purpose; the JSON AST remains canonical."
  REASON "Polish README intro and English marketing tone may differ from the schema purpose; the JSON AST remains canonical."

RELATION docs.mirror
  KIND generated_mirror
  SUBJECT docs/SSOT.md
  CANONICAL this-document
  RATIONALE "Docs and schemas listed here are generated mirrors or projections of the project SSOT, not a second description authority."

CAPABILITY
  VERB analyze
  VERB validate
  VERB generate
  KEYWORD "ssot"
  KEYWORD "interview"
  KEYWORD "propose-only"
  KEYWORD "duplication"
  KEYWORD "placement"
  STACK python
  ENTRYPOINT module project_ssot "PYTHONPATH=src python3 -m project_ssot validate <document>"
  INSTALL src-only
  MATURITY experimental
  SIBLING wellmanifest.dsl depends-on
  SIBLING wellmanifest.new-project extends
  USE_WHEN "you must decide which of several duplicated trees is canonical, and record why"
  USE_WHEN "you need a typed project description an agent can consume instead of prose"
  DO_NOT_USE_WHEN "you want the repository crawled or edited - this pack is propose-only and never writes"
  DO_NOT_USE_WHEN "you only need git state or freshness across a fleet - reach for a repository auditor instead"

PACKAGING none

RECEIPT
  DIGEST dsl-manifest.json sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa

CONFLICT name resolvedBy=interview
  VALUE dsl-manifest "Wellmanifest SSOT decision DSL"
  VALUE readme "wellmanifest/ssot"
  VALUE interview "Wellmanifest SSOT decision DSL"

CONFLICT purpose resolvedBy=interview
  VALUE dsl-manifest "Interview-driven classification of duplicated trees into propose-only SSOT decisions"
  VALUE readme "A generic SSOT creation layer. It interviews the user, classifies duplication, and emits a propose-only DSL document."
  VALUE interview "Interview-driven classification of duplicated trees into propose-only SSOT decisions"
