# DRF - Decision Reasoning Format

**Version:** 0.2.0 (Draft)

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
drf_version: "0.2.0"

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
draft → review → approved → superseded → archived
                    ↓
               rejected → archived
```

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
- `contrafactual` - What if we chose differently?
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

### Required Fields

- `drf_version` - Schema version
- `decision.id` - UUID
- `decision.title` - Human-readable title
- `decision.intent` - What is being decided
- `context.constraints` - Hard constraints
- `context.objectives` - Goals
- `cognitive_state.phase` - Current phase
- `cognitive_state.confidence` - Confidence level
- `synthesis.decision` - Final decision
- `synthesis.rationale` - Why this decision
- `meta.created_at` - Creation timestamp
- `meta.status` - Lifecycle status

---

## Integration with CRF

DRF documents can reference [CRF](../crf) (Context Reasoning Format) entities:

```yaml
context_validation:
  context_refs:
    - context_id: "uuid-of-policy"
      context_type: "policy"
      validation_status: "satisfied"  # or violated, acknowledged
```

This enables:
- Validation against organizational policies
- Detection of conflicts
- Bidirectional context updates

See [integration examples](../integration) for details.

---

## Examples

- [`database-selection.yaml`](./examples/database-selection.yaml) - Simple database decision
- [`api-versioning-strategy.yaml`](./examples/api-versioning-strategy.yaml) - API versioning strategy decision
- [`build-vs-buy-observability.yaml`](./examples/build-vs-buy-observability.yaml) - Build-vs-buy evaluation
- [`infrastructure-kubernetes-migration.yaml`](./examples/infrastructure-kubernetes-migration.yaml) - Complex infrastructure decision
- [`security-incident-response.yaml`](./examples/security-incident-response.yaml) - Time-critical security decision

---

## Specification

For the complete specification including design principles, related work comparisons, and rationale:

**[Read the full DRF Specification →](./spec/drf-specification.md)**

---

## Validation Rules

See [`spec/validation-rules.md`](./spec/validation-rules.md) for semantic validation rules beyond JSON Schema.
