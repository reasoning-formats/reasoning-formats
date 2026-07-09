# CRF - Context Reasoning Format

**Version:** 0.2.0
**Status:** Draft
**Companion to:** DRF (Decision Reasoning Format)

---

## Purpose

CRF (Context Reasoning Format) is a graph-based format for representing organizational context that informs and constrains decisions. It serves as a companion format to DRF (Decision Reasoning Format), enabling:

1. **Context-aware decisions** - Decisions can reference organizational policies, facts, and constraints
2. **Conflict detection** - Surface violations of policies or constraints (advisory, not blocking)
3. **Bidirectional updates** - Decisions can create new context or invalidate existing context
4. **Knowledge continuity** - Maintain organizational knowledge across decision cycles

---

## Design Principles

### 1. Graph-Based Structure
CRF models organizational context as a knowledge graph where:
- **Entities** (nodes) represent discrete pieces of context
- **Relationships** (edges) connect entities with typed semantics
- **Traversal** enables discovery of relevant context for decisions

### 2. Advisory Validation
All validation between CRF and DRF is **advisory**:
- Conflicts are surfaced for human review
- Decisions are never automatically blocked
- Enables explicit acknowledgment of policy violations with justification

### 3. Bidirectional Flow
```
CRF ──────────────► DRF
     context_refs    │
     (validation)    │
                     │ context_outputs
                     │ (creates/updates/invalidates)
                     ▼
CRF ◄────────────── DRF
```

### 4. Evolution via Supersession
Context evolves through replacement, not versioning:
- New entities can `supersede` old ones
- Full history maintained through supersession chains
- No explicit version numbers

---

## Document Conventions

### One Entity per Document

A CRF document contains exactly one `entity`. This keeps each document independently validatable and addressable.

### Multiple Entities per File

Related entities MAY be stored in a single file as a **multi-document YAML stream**, with documents separated by `---`:

```yaml
crf_version: "0.2.0"
entity:
  id: "11111111-1111-1111-1111-111111111111"
  # ...
---
crf_version: "0.2.0"
entity:
  id: "22222222-2222-2222-2222-222222222222"
  # ...
```

Each document in the stream MUST validate independently against the CRF schema, including its own `crf_version` field. Validators MUST process every document in a stream, not just the first. The repository's [`scripts/validate-examples.py`](../../scripts/validate-examples.py) implements this behavior.

### Extension Fields

Fields not defined by this specification MUST use the `x_` prefix (e.g., `x_mycompany_sla`). This applies at the document root, within `entity`, and within `attributes`. Unprefixed unknown fields are rejected by the schema.

---

## Entity Types

### Organization
Represents organizational units: companies, divisions, teams.

```yaml
type: organization
attributes:
  org_type: company | division | department | team | squad | working_group
  size: startup | small | medium | large | enterprise
  headcount: integer
  location: string
  industry: string
  compliance_frameworks: [string]
```

**Use cases:**
- Track team structures and ownership
- Document compliance requirements
- Establish organizational constraints

### System
Represents technical systems, applications, and infrastructure.

```yaml
type: system
attributes:
  system_type: application | service | platform | infrastructure | database | integration | tool
  status: planned | development | staging | production | deprecated | decommissioned
  criticality: low | medium | high | critical
  technology_stack: [string]
  hosting: string
  data_classification: public | internal | confidential | restricted
```

**Use cases:**
- Document the technical landscape
- Track system dependencies
- Establish data sensitivity constraints

### Policy
Represents rules, guidelines, and constraints.

```yaml
type: policy
attributes:
  policy_type: governance | security | compliance | architectural | operational | financial
  enforcement: mandatory | recommended | advisory
  scope: string (what this applies to)
  rationale: string (why this exists)
  exceptions_process: string
  owner: string
  review_cycle: string
```

**Use cases:**
- Document organizational policies
- Establish guardrails for decisions
- Track policy violations (advisory)

### Fact
Represents environmental facts: contracts, budgets, timelines.

```yaml
type: fact
attributes:
  fact_type: contract | budget | timeline | constraint | metric | event | status
  value: string | number | boolean | object
  unit: string
  confidence: integer (0-100)
  source_reference: string
  verified: boolean
  verified_at: datetime
```

**Use cases:**
- Track hard constraints (budgets, deadlines)
- Document external dependencies (contracts)
- Capture environmental factors

### Architecture
Represents architectural patterns, standards, and decisions.

```yaml
type: architecture
attributes:
  architecture_type: pattern | principle | standard | guideline | reference | decision
  domain: string (data, security, integration, infrastructure, etc.)
  maturity: emerging | established | mature | declining | deprecated
  adoption_status: proposed | pilot | adopted | standard | retiring
  alternatives: [string]
```

**Use cases:**
- Document architectural standards
- Track technology adoption
- Reference prior architectural decisions

### Capability
Represents team skills, tools, and processes.

```yaml
type: capability
attributes:
  capability_type: skill | tool | process | practice | certification
  proficiency: none | beginner | intermediate | advanced | expert
  coverage: integer (0-100, % of team with this capability)
  training_available: boolean
  strategic_importance: low | medium | high | critical
```

**Use cases:**
- Track team skills and gaps
- Document tool proficiency
- Inform resourcing decisions

---

## Relationship Types

| Relationship | Inverse | Description |
|--------------|---------|-------------|
| `owns` | `owned_by` | Ownership relationship |
| `depends_on` | `dependency_of` | Dependency relationship |
| `constrains` | `constrained_by` | Policy constrains entity |
| `invalidates` | `invalidated_by` | Fact invalidates assumption |
| `part_of` | `contains` | Composition relationship |
| `produces` | `produced_by` | Decision produces context |
| `related_to` | `related_to` | General association (symmetric) |

---

## Validation Status Values

When DRF decisions reference CRF context, they must specify a validation status:

| Status | Meaning |
|--------|---------|
| `satisfied` | Decision complies with this context |
| `violated` | Decision conflicts with this context (requires justification) |
| `acknowledged` | Conflict noted and explicitly accepted with rationale |
| `not_applicable` | Context referenced but not directly applicable |

---

## Temporal Validity

Entities may optionally specify temporal bounds:

```yaml
validity:
  valid_from: "2024-01-01T00:00:00Z"  # When this context becomes valid
  valid_until: "2024-12-31T23:59:59Z" # When this context expires
```

**Validation behavior:**
- If `valid_until` is in the past, context is considered expired
- Expired context triggers advisory warnings
- No temporal bounds = always valid

---

## Supersession

Context evolves through replacement:

```yaml
supersedes:
  entity_id: "uuid-of-previous-entity"
  reason: "Updated policy to reflect new compliance requirements"
  superseded_at: "2024-03-15T10:00:00Z"
```

**Rules:**
- Superseded entities remain in the graph (for history)
- Only the latest entity in a supersession chain is "active"
- Tooling should follow supersession chains for validation

---

## Provenance

Every entity tracks its origin. The `provenance` field is **required** on every entity, and within it `source` and `created_at` are mandatory:

```yaml
provenance:
  source: "manual"              # or "decision:uuid" or "import:system-name"
  created_at: "2024-01-15T09:00:00Z"
  created_by: "alice@example.com"
  updated_at: "2024-02-20T14:30:00Z"
  updated_by: "bob@example.com"
```

**Source types:**
- `manual` - Human-authored
- `decision:{uuid}` - Created by a DRF decision (via context_outputs)
- `import:{system}` - Imported from external system (CMDB, etc.)

---

## Integration with DRF

### Referencing Context (DRF → CRF)

```yaml
# In DRF document
context_validation:
  validated_at: "2024-02-28T10:00:00Z"
  context_refs:
    - context_id: "abc123-policy-uuid"
      context_type: policy
      context_name: "No Kubernetes Migration Policy"
      validation_status: violated
      advisory_notes: "Approved by VP Engineering due to business urgency"
```

### Producing Context (DRF → CRF)

```yaml
# In DRF document
context_validation:
  context_outputs:
    - action: creates
      entity_type: fact
      entity_data:
        id: "new-uuid"
        type: fact
        name: "EKS Production Environment Live"
        attributes:
          fact_type: status
          value: "production"
          verified: true
      reason: "EKS migration decision establishes new production environment"
```

---

## Example Workflow

```
1. CRF contains: Policy "No Kubernetes until Q4 2024"
                    │
                    ▼
2. DRF decision: "Migrate to EKS" references policy
                    │
                    ▼
3. Validation: status = "violated" (advisory)
                    │
                    ▼
4. Human review: Acknowledges violation with justification
                    │
                    ▼
5. DRF approved: context_outputs creates new CRF fact
                    │
                    ▼
6. CRF updated: New fact "EKS Production Live"
               Policy may be superseded by new policy
```

---

## Non-Goals

CRF is **not**:
- A CMDB (Configuration Management Database) - though it can integrate with one
- A workflow engine - validation is advisory, not blocking
- A replacement for existing systems - it's a reasoning-focused overlay
- Version control - it uses supersession, not branching/merging

---

## Future Considerations

1. **Query language** - For discovering applicable context
2. **Import adapters** - For popular CMDBs, cloud inventories
3. **Visualization** - Graph-based context exploration
4. **Automated validation** - Tooling to check DRF against CRF
5. **Conflict resolution** - Patterns for handling violated policies
