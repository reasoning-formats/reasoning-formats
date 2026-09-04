# DRF - Decision Reasoning Format

**Version:** 0.3.1 (Draft)

A vendor-neutral, machine-readable format for representing technical and strategic decisions with explicit reasoning.

---

## What is DRF?

DRF is a structured format for documenting **decisions** along with their **reasoning**. It captures not just *what* was decided, but *how* and *why*.

```
┌─────────────────────────────────────────────────────────────────┐
│                        DRF Document                              │
├─────────────────────────────────────────────────────────────────┤
│  decision      │ What is being decided                          │
│  context       │ Constraints and objectives                     │
│  reasoning     │ Patterns applied (comparative, risk-based...)  │
│  interventions │ Questions and challenges that shaped thinking  │
│  assumptions   │ Premises accepted                              │
│  tensions      │ Tradeoffs acknowledged                         │
│  synthesis     │ Final decision with rationale                  │
│  meta          │ Status, actors, timestamps                     │
└─────────────────────────────────────────────────────────────────┘
```

---

## Quick Example

```yaml
drf_version: "0.3.1"

decision:
  id: "550e8400-e29b-41d4-a716-446655440000"
  title: "Use PostgreSQL for Primary Database"
  domain: "architecture"
  intent: "Select a database that meets our scalability and compliance requirements"

context:
  constraints:
    - description: "Must support ACID transactions"
      source: "regulatory"
      negotiable: false
    - description: "Budget limited to $5000/month"
      source: "budget"
  objectives:
    - description: "Handle 10,000 concurrent users"
      priority: "must_have"
      measurable: true

cognitive_state:
  phase: "decision"
  confidence: 85

reasoning:
  patterns_applied:
    - comparative
    - cost_benefit
    - risk_based
  notes: "Evaluated PostgreSQL, MySQL, and MongoDB against requirements"

assumptions:
  - description: "Traffic will not exceed 10K concurrent users in next 2 years"
    validated: true
    confidence: 75

unresolved_tensions:
  - description: "PostgreSQL horizontal scaling more complex than MongoDB"
    impact: "medium"
    mitigation: "Use read replicas; revisit if traffic exceeds projections"

synthesis:
  decision: "Adopt PostgreSQL 15 on AWS RDS"
  rationale: "Best balance of ACID compliance, cost, and team familiarity"
  alternatives:
    - decision: "Use MongoDB Atlas"
      rationale_against: "Lacks ACID transactions across collections"

meta:
  created_at: "2024-01-15T09:00:00Z"
  status: "approved"
  actors:
    - name: "Alice Chen"
      role: "author"
```

---

## Core Concepts

### Decision Lifecycle

```
   draft ──────► review ──────► approved ──────► superseded
     │  ▲          │ │              │                 │
     │  └──────────┘ │              │                 │
     │               ▼              │                 │
     │           rejected ──┐       │                 │
     │               │      │       │                 │
     │               └──────┘       │                 │
     │              (back to draft) │                 │
     ▼                  ▼           ▼                 ▼
   ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌ archived (terminal) ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
```

| From | May move to |
|------|-------------|
| `draft` | `review`, `archived` |
| `review` | `approved`, `rejected`, `draft` |
| `approved` | `superseded`, `archived` |
| `rejected` | `draft`, `archived` |
| `superseded` | `archived` |
| `archived` | nothing - `archived` is terminal |

`approved → rejected` is **not** a legal transition: an approved decision is
retired by superseding or archiving it, never by rejecting it after the fact.
The full table, including why a single document cannot be checked against it,
is in [`spec/validation-rules.md`](./spec/validation-rules.md#1-lifecycle-state-transitions).

| Status | Meaning |
|--------|---------|
| `draft` | Work in progress |
| `review` | Under consideration |
| `approved` | Accepted and active |
| `rejected` | Not accepted |
| `superseded` | Replaced by another decision |
| `archived` | No longer relevant |

### Reasoning Patterns

DRF uses enumerated reasoning patterns organized into three categories:

**Analytical:**
- `operational` - How does this work in practice?
- `risk_based` - What could go wrong?
- `counterfactual` - What if we chose differently?
- `comparative` - How does this compare to alternatives?
- `cost_benefit` - What are the trade-offs?

**Cognitive:**
- `intuitive` - Pattern recognition
- `deliberative` - Step-by-step analysis
- `heuristic` - Rules of thumb
- `systematic` - Comprehensive evaluation
- `creative` - Divergent thinking

**Decision:**
- `consensus` - Group agreement
- `authority` - Designated decision-maker
- `delegation` - Deferred to specialist
- `voting` - Majority decision
- `escalation` - Elevated to higher authority

### Confidence Scoring

Confidence is expressed as an integer from 0-100:

| Range | Interpretation |
|-------|----------------|
| 0-25 | High uncertainty |
| 26-50 | Moderate uncertainty |
| 51-75 | Reasonable confidence |
| 76-90 | High confidence |
| 91-100 | Very high confidence |

---

## Schema

The full JSON Schema is available at [`schema/drf-schema.json`](./schema/drf-schema.json).

### Field Reference

Every object in the schema is **closed**: a field that is not listed here and
does not begin with `x_` is rejected. `R` marks a required field.

#### `decision` — R

| Field | | Type | Notes |
|-------|---|------|-------|
| `id` | R | UUID | Globally unique across your repository |
| `title` | R | string | 1-200 characters |
| `intent` | R | string | What is being decided, and why it matters |
| `domain` | | string | Free text, e.g. `architecture`, `security`, `infrastructure` |
| `related_decisions[]` | | list | Each entry needs `id` + `relationship`; optional `description` |
| `related_decisions[].relationship` | R | enum | `supersedes`, `superseded_by`, `depends_on`, `dependency_of`, `triggers`, `triggered_by`, `related_to`, `conflicts_with` |

#### `context` — R

| Field | | Type | Notes |
|-------|---|------|-------|
| `constraints[]` | R | list | Each entry needs `description` |
| `constraints[].source` | | string | Where the constraint comes from, e.g. `regulatory`, `budget`, `technical`. An open vocabulary, not an enum — see [Constraint Sources](./spec/drf-specification.md#constraint-sources) for the recommended values |
| `constraints[].negotiable` | | boolean | Defaults to `false` |
| `objectives[]` | R | list | Each entry needs `description` |
| `objectives[].priority` | | enum | `must_have`, `should_have`, `nice_to_have` |
| `objectives[].measurable` | | boolean | Defaults to `false` |
| `environment.technical` | | string | The technical landscape the decision lands in |
| `environment.organizational` | | string | Teams, ownership, politics |
| `environment.temporal` | | string | Deadlines, urgency, timing pressure |

Both `constraints` and `objectives` must be present, but either may be an empty
list — a decision genuinely without hard constraints says so explicitly rather
than leaving the reader guessing.

#### `cognitive_state` — R

| Field | | Type | Notes |
|-------|---|------|-------|
| `phase` | R | enum | `exploration`, `analysis`, `synthesis`, `decision` |
| `confidence` | R | integer | 0-100 |
| `phase_notes` | | string | Why the document is at this phase |

#### `reasoning`

| Field | | Type | Notes |
|-------|---|------|-------|
| `patterns_applied[]` | | enum list | Unique values, ordered: first entry is the primary pattern |
| `notes` | | string | Methodology, or reasoning that does not fit a pattern |

#### `interventions[]`

| Field | | Type | Notes |
|-------|---|------|-------|
| `id` | R | slug | Unique **within the document**. A free-form slug such as `int-sec-001`, not a UUID |
| `type` | R | enum | `question`, `challenge`, `constraint`, `insight`, `external_input` |
| `content` | R | string | What was raised |
| `source` | | string | Who or what raised it |
| `timestamp` | | date-time | RFC 3339 |
| `impact` | | string | How it changed the decision. Strongly recommended: an intervention with no recorded impact is a question nobody answered |

#### `assumptions[]`

| Field | | Type | Notes |
|-------|---|------|-------|
| `description` | R | string | The premise being accepted |
| `validated` | R | boolean | Whether it has actually been checked |
| `confidence` | | integer | 0-100 |
| `source` | | string | Basis for the assumption |

#### `unresolved_tensions[]`

| Field | | Type | Notes |
|-------|---|------|-------|
| `description` | R | string | The trade-off left open |
| `impact` | R | enum | `low`, `medium`, `high`, `critical` |
| `mitigation` | | string | Plan, if any |
| `accepted_by` | | string | Who accepted living with it |

#### `synthesis` — conditionally required

Required once `cognitive_state.phase` reaches `synthesis` or `decision`, or once
`meta.status` is `approved`, `rejected`, or `superseded`. A document still in
`exploration` or `analysis` may omit it entirely.

| Field | | Type | Notes |
|-------|---|------|-------|
| `decision` | R | string | The outcome |
| `rationale` | R | string | Why this outcome |
| `follow_ups[]` | | list | Each needs `action`; optional `owner`, `due_date` (a date, not a date-time) |
| `alternatives[]` | | list | Each needs `decision` + `rationale_against`; optional `conditions_for_reconsideration`. Ordered: first is the highest-ranked alternative |
| `alternatives[].retracted_by` | | string | Id of the intervention that withdrew this position, marking it as one actually held and then abandoned rather than merely evaluated. Must resolve within the same document — see [Retracted Positions](./spec/drf-specification.md#retracted-positions) |

#### `context_validation`

Links the decision to CRF entities. See [Integration with CRF](#integration-with-crf).

| Field | | Type | Notes |
|-------|---|------|-------|
| `validated_at` | | date-time | When validation was performed |
| `context_refs[]` | | list | Each needs `context_id`, `context_type`, `validation_status` |
| `context_refs[].validation_status` | R | enum | `satisfied`, `violated`, `acknowledged`, `not_applicable` |
| `context_refs[].advisory_notes` | | string | **Required** when `validation_status` is `acknowledged` |
| `context_outputs[]` | | list | Each needs `action` + `entity_type`; the rest depends on the action |
| `context_outputs[].action` | R | enum | `creates` (needs `entity_data`), `updates` / `invalidates` (need `entity_id`) |

#### `meta` — R

| Field | | Type | Notes |
|-------|---|------|-------|
| `created_at` | R | date-time | RFC 3339 |
| `status` | R | enum | `draft`, `review`, `approved`, `rejected`, `superseded`, `archived` |
| `updated_at` | | date-time | Must not precede `created_at` |
| `actors[]` | | list | Each needs `name` + `role`; optional `email` |
| `actors[].role` | R | enum | `author`, `reviewer`, `approver`, `contributor`, `stakeholder` |
| `source` | | string | Where the decision came from, e.g. `meeting`, `AI-assisted`, `document` |
| `tags[]` | | string list | Unique values |

### Extension fields

Any field prefixed `x_` is accepted anywhere in the document and is not
otherwise validated. Use a namespace: `x_mycompany_audit_id`, not `x_id`.

---

## Integration with CRF

DRF documents can reference [CRF](../crf) (Context Reasoning Format) entities:

```yaml
# doc-check: skip
context_validation:
  context_refs:
    - context_id: "44444444-4444-4444-4444-444444444444"
      context_type: "policy"
      context_name: "Kubernetes Migration Moratorium"
      validation_status: "satisfied"  # or violated, acknowledged, not_applicable
```

This enables:
- Validation against organizational policies
- Detection of conflicts
- Bidirectional context updates

See [integration examples](../integration) for details.

---

## Examples

- [`draft-vector-database-evaluation.drf.yaml`](./examples/draft-vector-database-evaluation.drf.yaml) - An **in-progress** decision: exploration phase, low confidence, no synthesis yet
- [`database-selection.drf.yaml`](./examples/database-selection.drf.yaml) - Simple database decision
- [`api-versioning-strategy.drf.yaml`](./examples/api-versioning-strategy.drf.yaml) - API versioning strategy decision
- [`build-vs-buy-observability.drf.yaml`](./examples/build-vs-buy-observability.drf.yaml) - Build-vs-buy evaluation
- [`infrastructure-kubernetes-migration.drf.yaml`](./examples/infrastructure-kubernetes-migration.drf.yaml) - Complex infrastructure decision
- [`security-incident-response.drf.yaml`](./examples/security-incident-response.drf.yaml) - Time-critical security decision

---

## Specification

For the complete specification including design principles, related work comparisons, and rationale:

**[Read the full DRF Specification →](./spec/drf-specification.md)**

---

## Validation Rules

See [`spec/validation-rules.md`](./spec/validation-rules.md) for semantic validation rules beyond JSON Schema.
