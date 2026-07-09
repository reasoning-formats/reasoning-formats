# DRF Validation Rules

**Version:** 0.2.0
**Status:** Draft

This document defines the semantic validation rules for DRF documents beyond JSON Schema structural validation.

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
RULE: state_transition_valid
WHEN: meta.status changes from {old} to {new}
THEN: transition must exist in valid_transitions map
ERROR: "Invalid state transition from '{old}' to '{new}'"
```

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
- `contrafactual` - What if we chose differently?
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

### Required for Approved Decisions

When `meta.status = "approved"`:

```
RULE: approved_synthesis_complete
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
RULE: created_before_updated
WHEN: meta.updated_at is present
THEN: meta.created_at <= meta.updated_at
ERROR: "updated_at cannot be before created_at"

RULE: intervention_timestamps_ordered
ADVISORY: interventions SHOULD be ordered chronologically by timestamp
```

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

### Intervention ID Uniqueness

```
RULE: unique_intervention_ids
SCOPE: within a single DRF document
THEN: interventions[].id MUST be unique within the document
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
| `satisfied` | Decision complies with context | None additional |
| `violated` | Decision conflicts with context | `advisory_notes` SHOULD explain |
| `acknowledged` | Conflict explicitly accepted | `advisory_notes` MUST provide justification |
| `not_applicable` | Context referenced but not directly relevant | None additional |

```
RULE: violated_requires_notes
WHEN: context_validation.context_refs[].validation_status = "violated"
ADVISORY: advisory_notes SHOULD be populated
RATIONALE: Violations without explanation reduce audit value

RULE: acknowledged_requires_justification
WHEN: context_validation.context_refs[].validation_status = "acknowledged"
ADVISORY: advisory_notes SHOULD contain justification from authorized party
RATIONALE: Acknowledged violations represent deliberate policy exceptions
```

### Context Output Rules

```
RULE: output_creates_requires_data
WHEN: context_validation.context_outputs[].action = "creates"
THEN: entity_data MUST be present with valid CRF entity structure
ERROR: "Context output 'creates' requires entity_data"

RULE: output_updates_requires_id
WHEN: context_validation.context_outputs[].action in ["updates", "invalidates"]
THEN: entity_id MUST be present
ERROR: "Context output '{action}' requires entity_id"

RULE: output_reason_recommended
WHEN: context_validation.context_outputs[] is present
ADVISORY: reason SHOULD be populated
RATIONALE: Documenting why decisions affect context improves traceability
```

### Temporal Validation

```
RULE: context_temporal_validity
WHEN: referenced CRF entity has validity.valid_until in the past
ADVISORY: Context may be expired; consider referencing current context
WARNING: "Referenced context '{context_name}' expired on {valid_until}"

RULE: validated_at_consistency
WHEN: context_validation.validated_at is present
ADVISORY: validated_at SHOULD be recent relative to meta.updated_at
RATIONALE: Stale context validation may not reflect current organizational state
```

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
RULE: approved_with_violations
WHEN: meta.status = "approved" AND any context_refs has validation_status = "violated"
ADVISORY: All violations SHOULD be changed to "acknowledged" before approval
RATIONALE: Approved decisions with unacknowledged violations indicate process gap
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
RULE: relationship_target_exists
WHEN: entity.relationships[].target_id is specified
ADVISORY: Target entity SHOULD exist in the context graph
WARNING: "Relationship target '{target_id}' not found in context"

RULE: relationship_inverse_consistency
WHEN: entity A has relationship R to entity B
ADVISORY: entity B SHOULD have inverse relationship to A
RATIONALE: Bidirectional relationships improve graph traversability
```

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

RULE: decision_provenance_format
WHEN: provenance.source starts with "decision:"
THEN: Remainder MUST be valid UUID referencing a DRF decision
ERROR: "Invalid decision provenance format: {source}"
```
