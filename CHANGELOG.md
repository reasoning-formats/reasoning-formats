# Changelog

All notable changes to the DRF and CRF specifications are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and both specifications adhere to [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added

- **Editor support**: both schemas are now registered in
  [SchemaStore](https://www.schemastore.org) (catalog entries `Decision Reasoning
  Format (DRF)` and `Context Reasoning Format (CRF)`), so a file named
  `*.drf.yaml` or `*.crf.yaml` gets field completion and inline validation in VS
  Code, IntelliJ, and any editor using the RedHat YAML language server, with
  nothing to install. Documented in the README. The catalog references the
  schemas at their `main` URLs rather than holding a copy.
- **File naming convention (both formats)**: DRF documents SHOULD be named
  `<name>.drf.yaml`, CRF documents `<name>.crf.yaml`. Documented in both
  specifications, `CONTRIBUTING.md`, and the new-example issue template. This is
  a RECOMMENDATION, not a conformance rule - no validator rejects a differently
  named file - and exists so editors and language servers can apply the right
  schema from the filename and offer completion and inline validation while a
  document is being written. A generic `*.yaml` pattern cannot serve that
  purpose because it would claim every YAML file in a project. See #3.

### Changed

- The repository's 12 example files were renamed to follow the convention
  (`database-selection.yaml` becomes `database-selection.drf.yaml`, and so on),
  and every reference to them in the specifications and READMEs was updated.
  Document content is unchanged, and the validation scripts glob directories
  rather than fixed names, so tooling was unaffected.

## [0.3.0] - 2026-08-19

This release makes the repository enforce what it already documented. Every
convention the specifications state is now checked by tooling that runs in CI,
and the places where the examples contradicted their own rules have been fixed.

### Added

- `scripts/validate-semantics.py`: implements the rules in
  `drf/spec/validation-rules.md` that JSON Schema cannot express - cross-document
  reference integrity, temporal ordering, ID uniqueness, acyclicity, and the
  advisory DRF-to-CRF consistency checks. Rule identifiers match the `RULE:`
  names in the specification. Previously that document was 437 lines of prose
  with no implementation behind it.
- `scripts/test-schemas.py` and `tests/invalid/`: 24 fixtures asserting that
  malformed documents are **rejected**. Validating only valid examples could
  never catch a schema that had been accidentally loosened.
- `scripts/validate-docs.py`: validates the YAML embedded in Markdown. Complete
  documents are schema-checked; every `id`-shaped field in every snippet must be
  a real UUID. Two entries in the 0.2.0 "Fixed" list were bugs of exactly this
  class.
- `requirements-dev.txt` with pinned tooling, including `rfc3339-validator`.
- `drf/examples/draft-vector-database-evaluation.yaml`: the first example of an
  **in-progress** decision - exploration phase, confidence 35, unvalidated
  assumptions, no synthesis. Prospective use is listed as a differentiator from
  ADRs and nothing demonstrated it.
- A per-field reference for DRF in `drf/README.md`. The `should_have` /
  `nice_to_have` priorities and the `reviewer` / `approver` / `contributor` /
  `stakeholder` actor roles were absent from every Markdown file in the repo.
- "Context Output Semantics" in the CRF specification, defining what `creates`,
  `updates`, and `invalidates` do to an entity - including that `updates` is a
  merge patch, that arrays are replaced rather than merged, and that there is no
  deletion syntax. This was previously undefined, so two implementations could
  read the same document differently.
- Conformance section in the DRF specification: RFC 2119 keywords, and which of
  the three normative documents governs what.
- `CODE_OF_CONDUCT.md` (referenced by CONTRIBUTING but missing), `SECURITY.md`,
  a pull request template, and Dependabot configuration.
- CI: DCO sign-off enforcement, `permissions: contents: read`, and a concurrency
  group.

### Changed

- **DRF schema (breaking)**: every object is now closed. Unknown fields are
  rejected at every level rather than only at the document root, so typos such
  as `decision.titel`, `synthesis.rational`, or `constraints[].negotable` now
  fail instead of validating silently. Extension fields still work anywhere via
  the `x_` prefix.
- **DRF schema (breaking)**: `synthesis` is now *conditionally* required rather
  than always required. A document in the `exploration` or `analysis` phase has
  no outcome yet, and requiring one forced placeholder text. It becomes required
  once `cognitive_state.phase` reaches `synthesis` or `decision`, or once
  `meta.status` is `approved`, `rejected`, or `superseded`.
- **DRF schema**: `context_outputs` rules that `validation-rules.md` already
  specified at ERROR severity are now enforced structurally - `creates` requires
  `entity_data`, `updates` and `invalidates` require `entity_id`, and
  `invalidates` must not carry `entity_data`. `acknowledged` context references
  now require `advisory_notes`.
- **DRF schema**: `counterfactual` added to `reasoning.patterns_applied`. The
  previous spelling `contrafactual` remains valid for backward compatibility and
  will be removed in 1.0.0.
- **CRF schema (breaking)**: `validity`, `relationships[]`, `supersedes`, and
  `provenance` are now closed objects. `provenance.creted_at` and
  `validity.valid_untill` previously validated.
- **Both schemas**: string fields carry `minLength: 1` so empty strings no longer
  satisfy a required field; `tags`, `relationships`, and `patterns_applied` are
  `uniqueItems`.
- **Both schemas**: `id` fields are documented as accepting any RFC 4122 UUID
  rather than v4 specifically. `format: "uuid"` cannot check a version, so the
  stated v4 rule was unenforceable, and every example violated it.
- **Temporal validity semantics (specification change)**: whether context counts
  as expired is now judged relative to *when a decision validated against it*,
  not relative to the current date. Validating against already-lapsed context is
  a warning; context that has expired since remains an advisory to revalidate.
  Under the old wall-clock reading, every archived decision in the corpus would
  decay into a warning purely with the passage of time.
- `drf/spec/validation-rules.md` now marks each rule `(schema)`, `(semantic)`,
  or `(stateful)`, and states plainly that lifecycle transitions cannot be
  checked from a single document, because a document records no prior status.
- `violated` versus `acknowledged` is now defined by *resolution*, not severity,
  in both the CRF specification and the validation rules.
- CI installs from `requirements-dev.txt` and runs all four validation scripts.

### Fixed

- **`jsonschema` was never checking timestamps.** With only `pyyaml jsonschema`
  installed - exactly what CI did - the `date-time` format checker is not
  registered, so every `created_at`, `updated_at`, `validated_at`,
  `valid_from`/`valid_until`, and `verified_at` in both formats went
  unvalidated; `"not-a-timestamp"` validated cleanly. `rfc3339-validator` is now
  pinned, and `validate-examples.py` refuses to run without it rather than
  reporting a success it cannot support.
- The two `integration/examples/` documents reused the `decision.id` of their
  `drf/examples/` counterparts, violating the `unique_decision_id` MUST rule.
  They now have their own IDs and are cross-linked with `related_to`.
- `drf/README.md`'s lifecycle diagram drew `approved → rejected`, a transition
  `validation-rules.md` explicitly lists as invalid, and omitted four valid
  transitions. Replaced with the full table.
- `security-credential-rotation-with-context.yaml` marked the PCI DSS reference
  `violated` while its own `advisory_notes` opened with "EXCEPTION ACKNOWLEDGED"
  and the document was `approved`. Now `acknowledged`.
- The same file used `acknowledged` for two references with no conflict at all,
  merely recording that those systems were in scope. Now `satisfied`.
- Placeholder identifiers that the schema rejects (`"uuid-of-policy"`,
  `"abc123-policy-uuid"`, `"new-uuid"`, `"33333333-..."`) replaced with real
  UUIDs throughout the documentation, and the abbreviated multi-document stream
  example in the CRF specification made complete and valid.
- 125 unquoted string values and 29 bare sequence items across the examples, in
  violation of CONTRIBUTING's own "quote all string values" rule. Verified by
  round-trip comparison that the parsed data is unchanged.
- The 9 CRF relationship edges that lacked the inverse edge their own advisory
  rule recommends.
- `crf/README.md`'s integration snippet omitted the required `context_type`.
- The `provenance.source` pattern introduced during this work ended in `|.+`,
  which matched anything; removed rather than left as decorative validation.

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

[0.3.0]: https://github.com/reasoning-formats/reasoning-formats/releases/tag/v0.3.0
[0.2.0]: https://github.com/reasoning-formats/reasoning-formats/releases/tag/v0.2.0
[0.1.0]: https://github.com/reasoning-formats/reasoning-formats/commit/4bb238d
