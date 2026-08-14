DOCUMENT PROJECT
ID subactor.widget
NAME "Widget runtime"
VERSION 0.1.0
SCHEMA wellmanifest.project-ssot/v1
PURPOSE "Serve widget commands on a LAN host under subactor ownership."

PLACEMENT
  HOME subactor
  SHAPE runtime_service
  RUNTIME_OWNER subactor
  ADOPT wellmanifest/dsl
  ADOPT wellmanifest/logs
  ADOPT wellmanifest/new-project

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
  ACTION use_document_as_ssot
  ACTION map_adopted_standard
  ACTION record_evidence_digest

OWNER repository github:subactor/widget

ADOPTED wellmanifest.dsl maps-to

ADOPTED wellmanifest.logs maps-to

ADOPTED wellmanifest.new-project maps-to

EVIDENCE intent
  KIND intent
  PATH project/ticket-001/intent.json
  PRECEDENCE 85
  ROLE authority

EVIDENCE governance
  KIND governance-manifest
  PATH .governance/manifest.json
  PRECEDENCE 80
  ROLE authority

EVIDENCE pyproject
  KIND pyproject
  PATH pyproject.toml
  PRECEDENCE 40
  ROLE packaging

PACKAGING pip pyproject.toml

CONFLICT name resolvedBy=interview
  VALUE pyproject "widget"
  VALUE interview "Widget runtime"
