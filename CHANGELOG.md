# Changelog

All notable changes to the DRF and CRF specifications are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and both specifications adhere to [Semantic Versioning](https://semver.org/).

## [0.2.0] - 2026-07-09

### Added

- **DRF**: `triggers` and `triggered_by` relationship types for `decision.related_decisions`, covering decisions that cause or necessitate other decisions (e.g., an incident response triggering a post-incident review).
- **CRF**: Document Conventions section in the specification, formally defining multi-document YAML streams as the way to store multiple entities in one file. Each document validates independently.
- `scripts/validate-examples.py`: repository validation script that checks every example (including multi-document CRF files) against the schemas.
- Continuous integration workflow that validates both schemas and all examples on every push and pull request.
- Changelog (this file).

### Changed

- **CRF schema (breaking)**: entity `attributes` are now validated conditionally by `entity.type` instead of a `oneOf` across all attribute definitions. The previous `oneOf` could never match exactly one definition (all attribute definitions were satisfiable by any object), so no attributes object could validate.
- **CRF schema (breaking)**: `entity.provenance` is now required, with `source` and `created_at` mandatory. This aligns the schema with the `provenance_required` validation rule, which already specified ERROR severity.
- **Both schemas (breaking)**: unknown fields without the `x_` extension prefix are now rejected — at the document root in DRF, and at the document root, entity, and attributes levels in CRF. Previously the `x_` convention was documented but not enforced.
- Schema `$id` values now point to versioned raw repository URLs.
- Examples updated to `0.2.0` and to use `x_`-prefixed extension fields for custom attributes.

### Fixed

- `security-incident-response` and `security-credential-rotation` examples used the relationship type `triggers` before it existed in the schema enum.
- `security-credential-rotation` example used `fact_type: incident`, which is not a valid `fact_type`; changed to `event`.
- The root README DRF quick-start example was missing the required `cognitive_state` section.
- The root README CRF quick-start example was missing the now-required `provenance` section, and its `context_refs` snippet was missing the required `context_type` field.
- Broken example link in `integration/README.md`.
- Issue template contact link pointed to the wrong repository owner.

## [0.1.0] - 2026-02-27

### Added

- Initial release of the DRF (Decision Reasoning Format) specification, JSON Schema, validation rules, and examples.
- Initial release of the CRF (Context Reasoning Format) specification, JSON Schema, and examples.
- Integration examples showing DRF and CRF used together.
- Contributing guidelines and issue templates.

[0.2.0]: https://github.com/reasoning-formats/reasoning-formats/releases/tag/v0.2.0
[0.1.0]: https://github.com/reasoning-formats/reasoning-formats/commit/4bb238d
