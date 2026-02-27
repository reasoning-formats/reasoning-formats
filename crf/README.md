# CRF - Context Reasoning Format

**Version:** 0.1.0 (Draft)

A graph-based format for representing organizational context that informs and constrains decisions. Companion format to [DRF](../drf).

---

## What is CRF?

CRF models organizational knowledge as a **knowledge graph** where:

- **Entities** (nodes) represent discrete pieces of context
- **Relationships** (edges) connect entities with typed semantics

```
┌─────────────────────────────────────────────────────────────────┐
│                    CRF Knowledge Graph                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│    ┌──────────┐     owns      ┌──────────┐                      │
│    │   Org    │──────────────►│  System  │                      │
│    └──────────┘               └──────────┘                      │
│         │                          ▲                             │
│         │ part_of                  │ constrains                  │
│         ▼                          │                             │
│    ┌──────────┐               ┌──────────┐                      │
│    │   Team   │               │  Policy  │                      │
│    └──────────┘               └──────────┘                      │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Quick Example

```yaml
crf_version: "0.1.0"

entity:
  id: "44444444-4444-4444-4444-444444444444"
  type: policy
  name: "Kubernetes Migration Moratorium"
  description: "No Kubernetes until security audit complete"

  attributes:
    policy_type: architectural
    enforcement: mandatory
    scope: "All production workloads"
    rationale: "Pending security team readiness assessment"
    owner: "VP Engineering"

  validity:
    valid_from: "2023-10-01T00:00:00Z"
    valid_until: "2024-06-30T23:59:59Z"

  relationships:
    - target_id: "33333333-..."
      type: constrains
      description: "Applies to production infrastructure"

  provenance:
    source: "manual"
    created_at: "2023-10-01T00:00:00Z"
    created_by: "security@example.com"

  tags:
    - "policy"
    - "kubernetes"
    - "security"
```

---

## Entity Types

### Organization

Companies, divisions, teams, squads.

```yaml
type: organization
attributes:
  org_type: team          # company, division, department, team, squad
  size: medium            # startup, small, medium, large, enterprise
  headcount: 15
  compliance_frameworks: ["SOC 2", "HIPAA"]
```

### System

Applications, services, infrastructure.

```yaml
type: system
attributes:
  system_type: platform    # application, service, platform, infrastructure
  status: production       # planned, development, staging, production
  criticality: critical    # low, medium, high, critical
  technology_stack: ["AWS", "Kubernetes", "PostgreSQL"]
  data_classification: confidential
```

### Policy

Rules, guidelines, constraints.

```yaml
type: policy
attributes:
  policy_type: security     # governance, security, compliance, architectural
  enforcement: mandatory    # mandatory, recommended, advisory
  scope: "All production systems"
  exceptions_process: "Requires VP approval"
```

### Fact

Environmental facts: contracts, budgets, timelines.

```yaml
type: fact
attributes:
  fact_type: contract      # contract, budget, timeline, metric
  value:
    vendor: "AWS"
    committed_spend: 500000
  confidence: 100
  verified: true
```

### Architecture

Patterns, standards, guidelines.

```yaml
type: architecture
attributes:
  architecture_type: standard   # pattern, principle, standard, guideline
  domain: infrastructure
  maturity: mature              # emerging, established, mature, deprecated
  adoption_status: adopted
```

### Capability

Team skills, tools, processes.

```yaml
type: capability
attributes:
  capability_type: skill    # skill, tool, process, practice
  proficiency: intermediate # none, beginner, intermediate, advanced, expert
  coverage: 60              # % of team with this capability
  strategic_importance: high
```

---

## Relationships

| Relationship | Inverse | Description |
|--------------|---------|-------------|
| `owns` | `owned_by` | Ownership |
| `depends_on` | `dependency_of` | Dependency |
| `constrains` | `constrained_by` | Policy applies to |
| `invalidates` | `invalidated_by` | Fact invalidates assumption |
| `part_of` | `contains` | Composition |
| `produces` | `produced_by` | Decision creates context |
| `related_to` | `related_to` | General association |

---

## Temporal Validity

Entities can have optional time bounds:

```yaml
validity:
  valid_from: "2024-01-01T00:00:00Z"
  valid_until: "2024-12-31T23:59:59Z"
```

- Expired context triggers advisory warnings
- No bounds = always valid

---

## Supersession

Context evolves through replacement, not versioning:

```yaml
supersedes:
  entity_id: "uuid-of-previous-entity"
  reason: "Updated policy based on Q1 review"
  superseded_at: "2024-03-15T10:00:00Z"
```

- Old entity remains in graph (history)
- Only latest in chain is "active"

---

## Provenance

Every entity tracks its origin:

```yaml
provenance:
  source: "manual"              # or "decision:uuid", "import:cmdb"
  created_at: "2024-01-15T09:00:00Z"
  created_by: "alice@example.com"
```

---

## Integration with DRF

DRF decisions can:

1. **Reference CRF context** for validation
2. **Produce new CRF entities** (bidirectional)

```yaml
# In DRF decision
context_validation:
  context_refs:
    - context_id: "policy-uuid"
      validation_status: "violated"
      advisory_notes: "Exception approved by VP"

  context_outputs:
    - action: "creates"
      entity_type: "fact"
      entity_data: { ... }
```

See [integration examples](../integration) for details.

---

## Examples

- [`organization-acme.yaml`](./examples/organization-acme.yaml) - Organization, team, system, capability
- [`policy-no-kubernetes.yaml`](./examples/policy-no-kubernetes.yaml) - Policy with related facts

---

## Schema

The full JSON Schema is available at [`schema/crf-schema.json`](./schema/crf-schema.json).

---

## Specification

See [`spec/crf-specification.md`](./spec/crf-specification.md) for the complete specification.
