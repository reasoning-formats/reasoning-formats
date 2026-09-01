# DRF and CRF Validation Rules

**Version:** 0.3.0
**Status:** Draft

This document defines the semantic validation rules for DRF and CRF documents
beyond JSON Schema structural validation. Sections 1-11 cover DRF; section 12
covers CRF entities.

## How these rules are enforced

Each rule below is enforced by one of two mechanisms. Neither is optional in
this repository: both run in CI on every push and pull request.

| Mechanism | What it covers | Command |
|-----------|----------------|---------|
| **JSON Schema** | Shape of a single document: required fields, types, enumerations, conditional requirements | `python3 scripts/validate-examples.py` |
| **Semantic validator** | Everything JSON Schema cannot express: cross-document references, temporal ordering, identifier uniqueness, acyclicity, advisory consistency | `python3 scripts/validate-semantics.py --strict` |

Rules marked **(schema)** below are structural and fail schema validation.
Rules marked **(semantic)** are checked by `scripts/validate-semantics.py`,
whose rule identifiers match the `RULE:` names used here. Rules marked
**(stateful)** cannot be checked from a document corpus at all and require a
tool that observes documents changing over time.

A third script, `scripts/test-schemas.py`, asserts that the fixtures in
`tests/invalid/` are *rejected*, so that a schema cannot be loosened by
accident without failing the build.

---

## 1. Lifecycle State Transitions

DRF enforces strict state transitions. The following transitions are **valid**:

```
draft       → review
draft       → archived      (abandoned before review)
review      → approved
review      → rejected
review      → draft         (sent back for revision)
approved    → superseded
approved    → archived
rejected    → draft         (reopened for revision)
rejected    → archived
superseded  → archived
```

### Invalid Transitions

The following transitions MUST be rejected:

- `draft → approved` (must go through review)
- `draft → superseded` (cannot supersede without approval)
- `archived → *` (archived is terminal)
- `approved → draft` (cannot demote approved decisions)
- `approved → rejected` (cannot reject after approval)

### Validation Rule

```
RULE: state_transition_valid                                       (stateful)
WHEN: meta.status changes from {old} to {new}
THEN: transition must exist in valid_transitions map
ERROR: "Invalid state transition from '{old}' to '{new}'"
```

> **A DRF document cannot be checked against this rule on its own.**
> A document records only its current `meta.status`; it carries no record of
> the status it held previously. This rule is therefore enforceable only by a
> system that observes the same `decision.id` over time - a document store, a
> review workflow, or a git history walk. A validator handed a single file has
> no way to know which transition, if any, just occurred.
>
> Tools that persist DRF documents SHOULD record the prior status alongside the
> document. A future revision may add an optional `meta.status_history` field
> so that a single document can carry its own audit trail; that change needs
> agreement in an issue first (see CONTRIBUTING.md).

---

## 2. Confidence Scoring

### Range Validation

- `cognitive_state.confidence` MUST be integer in range [0, 100]
- `assumptions[].confidence` MUST be integer in range [0, 100]

### Semantic Guidelines (Advisory)

| Confidence | Interpretation |
|------------|----------------|
| 0-25       | High uncertainty; major unknowns |
| 26-50      | Moderate uncertainty; some validation needed |
| 51-75      | Reasonable confidence; minor unknowns |
| 76-90      | High confidence; well-validated |
| 91-100     | Very high confidence; thoroughly validated |

### Consistency Rule

```
RULE: confidence_phase_consistency
WHEN: cognitive_state.phase = "decision"
ADVISORY: cognitive_state.confidence SHOULD be >= 50
RATIONALE: Decisions made with <50% confidence should remain in earlier phases
```

---

## 3. Reasoning Pattern Constraints

### Valid Patterns (Enumeration)

**Analytical Patterns:**
- `operational` - How does this work in practice?
- `risk_based` - What could go wrong?
- `counterfactual` - What if we chose differently?
- `comparative` - How does this compare to alternatives?
- `cost_benefit` - What are the trade-offs?

**Cognitive Patterns:**
- `intuitive` - Gut feeling / pattern recognition
- `deliberative` - Careful step-by-step analysis
- `heuristic` - Rule-of-thumb shortcuts
- `systematic` - Comprehensive evaluation
- `creative` - Novel / divergent thinking

**Decision Patterns:**
- `consensus` - Group agreement reached
- `authority` - Decided by designated authority
- `delegation` - Deferred to specialist/team
- `voting` - Majority/weighted vote
- `escalation` - Elevated to higher authority

> **Deprecated spelling.** Releases up to 0.2.0 spelled `counterfactual` as
> `contrafactual`. The misspelling remains a valid enumeration value so that
> existing documents keep validating, and will be removed in 1.0.0. New
> documents MUST use `counterfactual`.

### Order Semantics

```
RULE: patterns_order_meaningful
WHEN: reasoning.patterns_applied contains multiple entries
THEN: first entry = primary pattern, subsequent = supporting
```

---

## 4. Intervention Type Semantics

| Type | Definition | Expected Content |
|------|------------|------------------|
| `question` | Inquiry that prompted exploration | Interrogative statement |
| `challenge` | Objection or counterargument raised | Critical statement with basis |
| `constraint` | New limitation discovered or imposed | Constraint description |
| `insight` | Key realization or discovery | Declarative finding |
| `external_input` | Information from outside the decision process | Citation or reference |

### Validation Rule

```
RULE: intervention_has_impact
WHEN: intervention is added
ADVISORY: impact field SHOULD be populated
RATIONALE: Interventions without documented impact may indicate incomplete reasoning capture
```

---

## 5. Related Decision Relationships

### Relationship Semantics

| Relationship | Meaning | Reciprocal |
|--------------|---------|------------|
| `supersedes` | This decision replaces the referenced one | `superseded_by` |
| `superseded_by` | This decision was replaced by the referenced one | `supersedes` |
| `depends_on` | This decision requires the referenced one | `dependency_of` |
| `dependency_of` | Referenced decision depends on this one | `depends_on` |
| `triggers` | This decision causes or necessitates the referenced one | `triggered_by` |
| `triggered_by` | This decision was caused or necessitated by the referenced one | `triggers` |
| `related_to` | General association (symmetric) | `related_to` |
| `conflicts_with` | Decisions are in tension (symmetric) | `conflicts_with` |

### Consistency Rules

```
RULE: supersedes_state_consistency
WHEN: decision A supersedes decision B
THEN: decision B status SHOULD be "superseded"

RULE: circular_dependency_prevention
WHEN: evaluating depends_on relationships
THEN: no circular dependency chains allowed
ERROR: "Circular dependency detected: {chain}"
```

---

## 6. Assumption Validation

### Required Fields

- `description` - REQUIRED
- `validated` - REQUIRED (boolean)
- `confidence` - OPTIONAL but recommended
- `source` - OPTIONAL but recommended

### Semantic Rules

```
RULE: validated_assumption_confidence
WHEN: assumption.validated = true
ADVISORY: assumption.confidence SHOULD be >= 60
RATIONALE: Validated assumptions with low confidence indicate validation quality issues

RULE: unvalidated_critical_assumptions
WHEN: assumption.validated = false AND assumption.confidence >= 80
ADVISORY: High-confidence unvalidated assumptions should be flagged for validation
```

---

## 7. Synthesis Completeness

### When synthesis is required

`synthesis` is not required for every document. A decision still in the
`exploration` or `analysis` phase legitimately has no outcome yet, and forcing
one produces placeholder text that is worse than an absent field.

```
RULE: synthesis_required_when_concluded                            (schema)
WHEN: cognitive_state.phase is "synthesis" or "decision",
      OR meta.status is "approved", "rejected", or "superseded"
THEN: synthesis MUST be present
ERROR: "'synthesis' is a required property"
```

See `drf/examples/draft-vector-database-evaluation.drf.yaml` for a document that
legitimately omits it.

### Required for Approved Decisions

When `meta.status = "approved"`:

```
RULE: approved_synthesis_complete                                  (semantic)
REQUIRED: synthesis.decision (non-empty string)
REQUIRED: synthesis.rationale (non-empty string)
ADVISORY: synthesis.follow_ups SHOULD have at least one entry
ADVISORY: synthesis.alternatives SHOULD have at least one entry
```

### Alternatives Ranking

```
RULE: alternatives_ranked
WHEN: synthesis.alternatives contains multiple entries
THEN: order represents ranking (first = highest-ranked alternative)
```

---

## 8. Temporal Consistency

```
RULE: created_before_updated                                       (semantic)
WHEN: meta.updated_at is present (DRF), or provenance.updated_at (CRF)
THEN: created_at <= updated_at
ERROR: "updated_at cannot be before created_at"

RULE: validity_window_ordered                                      (semantic)
WHEN: a CRF entity sets both validity.valid_from and validity.valid_until
THEN: valid_until MUST be later than valid_from
ERROR: "validity.valid_until is not after valid_from"

RULE: intervention_timestamps_ordered                              (semantic)
ADVISORY: interventions SHOULD be ordered chronologically by timestamp
```

> **Timestamps are only checked when the tooling can check them.**
> `jsonschema` silently skips every `"format": "date-time"` assertion unless the
> `rfc3339-validator` package is installed, which turns a passing validation run
> into a false negative. `scripts/validate-examples.py` refuses to run if that
> support is missing rather than reporting a success it cannot back up. Install
> the pinned dependencies with `pip install -r requirements-dev.txt`.

---

## 9. Extension Field Rules

### Naming Convention

```
RULE: extension_prefix
WHEN: field name starts with "x_"
THEN: field is treated as extension (permissive validation)
FORMAT: x_{namespace}_{field_name}
EXAMPLES: x_mycompany_audit_id, x_security_classification

RULE: unknown_field_rejected
WHEN: an unrecognized field does not start with "x_"
THEN: the field is rejected at the document root (DRF) and at the
      document root, entity, and attributes levels (CRF)
ERROR: "Additional properties are not allowed ('{field}' was unexpected)"
```

### Extension Isolation

Extensions MUST NOT:
- Override core field semantics
- Use reserved field names without prefix
- Introduce circular dependencies on core fields

---

## 10. Document Integrity

### UUID Uniqueness

```
RULE: unique_decision_id
SCOPE: within a DRF repository/system
THEN: decision.id MUST be globally unique
```

```
RULE: unique_entity_id                                             (semantic)
SCOPE: within a CRF repository/system
THEN: entity.id MUST be globally unique
```

> Two documents describing the same decision - for instance a standalone
> version and a context-aware version - are still two documents and MUST NOT
> share an id. Link them with `related_decisions` instead. The pairs in
> `drf/examples/` and `integration/examples/` demonstrate this.

### Intervention ID Uniqueness

```
RULE: unique_intervention_ids                                      (semantic)
SCOPE: within a single DRF document
THEN: interventions[].id MUST be unique within the document
```

Note that `interventions[].id` is a free-form slug (`int-sec-001`), not a UUID.
It only has to be unique inside its own document.

### Self-Reference

```
RULE: no_self_reference                                            (semantic)
THEN: decision.related_decisions[].id MUST NOT equal decision.id
      entity.relationships[].target_id MUST NOT equal entity.id
      entity.supersedes.entity_id MUST NOT equal entity.id
ERROR: "document references itself"
```

---

## Validation Severity Levels

| Level | Meaning | Behavior |
|-------|---------|----------|
| `ERROR` | Document is invalid | MUST reject |
| `WARNING` | Document is valid but problematic | SHOULD warn |
| `ADVISORY` | Recommendation for best practice | MAY inform |

Validators MUST support configurable severity levels for ADVISORY rules.

---

## 11. Context Validation (CRF Integration)

DRF documents may reference CRF (Context Reasoning Format) entities for validation. All context validation is **advisory** - conflicts are surfaced but do not block decisions.

### Context Reference Rules

```
RULE: context_ref_valid_uuid
WHEN: context_validation.context_refs[].context_id is present
THEN: value MUST be valid UUID format
ERROR: "Invalid context reference UUID: {context_id}"

RULE: context_ref_type_match
WHEN: context_validation.context_refs[] references a CRF entity
ADVISORY: context_type SHOULD match the actual entity type in CRF
WARNING: "Context type mismatch: declared {declared}, actual {actual}"
```

### Validation Status Semantics

| Status | Meaning | Required Fields |
|--------|---------|-----------------|
| `satisfied` | Decision complies with this context, or the context is relevant and raises no conflict | None additional |
| `violated` | Decision conflicts with this context and the conflict is **unresolved** | `advisory_notes` SHOULD explain |
| `acknowledged` | Decision conflicts with this context and the conflict has been **explicitly accepted** by someone with the authority to accept it | `advisory_notes` MUST provide justification |
| `not_applicable` | Context referenced for completeness but not materially relevant | None additional |

The line between `violated` and `acknowledged` is *resolution*, not severity. A
conflict that has been reviewed, justified, and signed off is `acknowledged`
even if it remains a serious exception. A conflict nobody has ruled on yet is
`violated`, even if it looks minor.

`satisfied` is also the correct status for context that a decision affects
without conflicting with - an in-scope system, an owning team. Reaching for
`acknowledged` there overstates the situation: it claims a conflict was
accepted when none was found.

```
RULE: acknowledged_requires_justification                          (schema)
WHEN: context_validation.context_refs[].validation_status = "acknowledged"
THEN: advisory_notes MUST be present
ERROR: "'advisory_notes' is a required property"
RATIONALE: An acceptance with no recorded justification is not an acceptance

RULE: violated_requires_notes                                      (semantic)
WHEN: context_validation.context_refs[].validation_status = "violated"
ADVISORY: advisory_notes SHOULD be populated
RATIONALE: Violations without explanation reduce audit value
```

### Context Output Rules

```
RULE: output_creates_requires_data                                 (schema)
WHEN: context_validation.context_outputs[].action = "creates"
THEN: entity_data MUST be present, holding a complete CRF entity
ERROR: "'entity_data' is a required property"

RULE: output_updates_requires_id                                   (schema)
WHEN: context_validation.context_outputs[].action in ["updates", "invalidates"]
THEN: entity_id MUST be present
ERROR: "'entity_id' is a required property"

RULE: output_invalidates_forbids_data                              (schema)
WHEN: context_validation.context_outputs[].action = "invalidates"
THEN: entity_data MUST NOT be present
ERROR: "'entity_data' should not be valid under the given schema"
RATIONALE: Invalidation ends an entity's applicability; it carries no new data

RULE: output_target_resolves                                       (semantic)
WHEN: context_validation.context_outputs[].entity_id is present
WARNING: the referenced entity SHOULD exist in the context graph

RULE: output_reason_recommended                                    (semantic)
WHEN: context_validation.context_outputs[] is present
ADVISORY: reason SHOULD be populated
RATIONALE: Documenting why decisions affect context improves traceability
```

The payload shape differs by action, and the difference matters for
interoperability. See "Context Output Semantics" in the
[CRF specification](../../crf/spec/crf-specification.md) for the normative
definition of what `creates`, `updates`, and `invalidates` do to an entity.

### Temporal Validation

```
RULE: context_temporal_validity                                    (semantic)
WHEN: a referenced CRF entity has validity.valid_until earlier than the moment
      the validation was performed (context_validation.validated_at, falling
      back to meta.updated_at, then meta.created_at)
WARNING: "Validated against '{context_name}' after it expired on {valid_until}"
RATIONALE: Validating against context that had already lapsed is an error at
           the time it was made, and stays an error forever

RULE: context_since_expired                                        (semantic)
WHEN: a referenced CRF entity was valid at validation time but has expired since
ADVISORY: "'{context_name}' expired on {valid_until}; consider revalidating"
RATIONALE: The decision was correct when made and does not become retroactively
           wrong, but the ground it stood on has moved

RULE: validated_at_consistency                                     (semantic)
WHEN: context_validation.validated_at is present
WARNING: validated_at MUST NOT precede meta.created_at
ADVISORY: validated_at SHOULD be recent relative to meta.updated_at
RATIONALE: Stale context validation may not reflect current organizational state
```

> **Expiry is judged as of the validation, not as of today.**
> A decision made in February 2024 and validated against a policy that ran to
> June 2024 was validated correctly, and a validator run in 2030 must still say
> so. Anchoring the check to wall-clock time instead would make every archived
> decision in the corpus decay into a warning as time passed - a result that
> tells the reader nothing about the decision's quality, only about the date.
> `crf/examples/policy-no-kubernetes.crf.yaml` is the corpus's worked example of
> context that has since expired.

### Policy Violation Handling

All policy violations are advisory. The recommended workflow:

1. **Detection** - Tooling identifies `validation_status: violated`
2. **Review** - Human reviews the conflict
3. **Resolution** - Either:
   - Modify decision to achieve `satisfied`
   - Change status to `acknowledged` with justification
   - Update CRF to supersede the policy
4. **Audit** - All violations (including acknowledged) are logged

```
RULE: approved_with_violations                                     (semantic)
WHEN: meta.status = "approved" AND any context_refs has validation_status = "violated"
WARNING: All violations SHOULD be resolved to "satisfied" or accepted as
         "acknowledged" before approval
RATIONALE: An approved decision that still carries an unresolved violation means
           either the conflict was never ruled on, or it was ruled on and the
           document was not updated to say so. Both are process gaps.
```

---

## 12. CRF Entity Validation

Rules for validating CRF (Context Reasoning Format) documents.

### Entity Type Consistency

```
RULE: attributes_match_type
WHEN: entity.type is specified
THEN: entity.attributes MUST only contain fields defined for that type,
      or extension fields prefixed with "x_"
ERROR: "Attribute '{field}' not defined for entity type '{type}'"
NOTE: Enforced structurally by the CRF schema (conditional attribute
      definitions selected by entity.type)
```

### Relationship Consistency

```
RULE: relationship_target_exists                                   (semantic)
WHEN: entity.relationships[].target_id is specified
WARNING: Target entity SHOULD exist in the context graph

RULE: no_self_relationship                                         (semantic)
WHEN: entity.relationships[].target_id equals entity.id
ERROR: "entity relates to itself"

RULE: relationship_inverse_consistency                             (semantic)
WHEN: entity A has relationship R to entity B
ADVISORY: entity B SHOULD have the inverse relationship to A
RATIONALE: Bidirectional relationships improve graph traversability
```

The inverse of each relationship type is fixed; see the table in the
[CRF specification](../../crf/spec/crf-specification.md#relationship-types).
Every edge in `crf/examples/` has its inverse recorded, so the reference corpus
demonstrates the practice it recommends.

### Supersession Rules

```
RULE: supersedes_creates_chain
WHEN: entity.supersedes.entity_id is specified
THEN: Referenced entity MUST exist
ERROR: "Superseded entity '{entity_id}' not found"

RULE: no_circular_supersession
WHEN: following supersession chain
THEN: Chain MUST be acyclic
ERROR: "Circular supersession detected: {chain}"

RULE: superseded_entity_inactive
WHEN: entity A supersedes entity B
ADVISORY: Entity B SHOULD be marked inactive in tooling
RATIONALE: Only latest entity in chain should be used for validation
```

### Provenance Rules

```
RULE: provenance_required
WHEN: entity is created
THEN: provenance.source and provenance.created_at MUST be present
ERROR: "Entity missing required provenance fields"

RULE: decision_provenance_format                                   (semantic)
WHEN: provenance.source starts with "decision:"
THEN: Remainder MUST be a valid UUID
WARNING: the referenced DRF decision SHOULD exist in the corpus
ERROR: "Invalid decision provenance format: {source}"
```
