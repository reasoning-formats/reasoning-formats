# CRF - Context Reasoning Format

**Version:** 0.3.0
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
crf_version: "0.3.0"
entity:
  id: "11111111-1111-1111-1111-111111111111"
  type: "organization"
  name: "ACME Corporation"
  provenance:
    source: "manual"
    created_at: "2024-01-01T00:00:00Z"
---
crf_version: "0.3.0"
entity:
  id: "22222222-2222-2222-2222-222222222222"
  type: "organization"
  name: "Platform Engineering"
  provenance:
    source: "manual"
    created_at: "2024-01-01T00:00:00Z"
```

Both documents above are complete and valid; every YAML block in this
specification is validated against the schema in CI by
`scripts/validate-docs.py`, so no example here can drift into something the
schema would reject.

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
| `satisfied` | Decision complies with this context, or touches it without conflicting |
| `violated` | Decision conflicts with this context and the conflict is **unresolved** |
| `acknowledged` | Decision conflicts with this context and the conflict has been **explicitly accepted** by someone with the authority to accept it. `advisory_notes` is required |
| `not_applicable` | Context referenced for completeness but not materially relevant |

What separates `violated` from `acknowledged` is *resolution*, not severity. A
serious exception that has been reviewed, justified, and signed off is
`acknowledged`. A minor conflict nobody has ruled on is `violated`.

`satisfied` is also the right status for context a decision merely affects - an
in-scope system, an owning team, an applicable standard it complies with.
Reaching for `acknowledged` there claims a conflict was accepted when none was
found.

---

## Temporal Validity

Entities may optionally specify temporal bounds:

```yaml
validity:
  valid_from: "2024-01-01T00:00:00Z"  # When this context becomes valid
  valid_until: "2024-12-31T23:59:59Z" # When this context expires
```

**Validation behaviour:**

- No temporal bounds means the entity is always valid.
- When both bounds are present, `valid_until` MUST be later than `valid_from`.
- Whether an entity counts as "expired" is judged **relative to the moment a
  decision validated against it**, not relative to the current date. A decision
  validated in February 2024 against a policy that ran to June 2024 was
  validated correctly, and stays correct however long ago that was.
- Validating against context that had *already* lapsed at the time is a warning
  (`context_temporal_validity`).
- Context that was in force at validation time but has expired *since* is an
  advisory to revalidate (`context_since_expired`), not an error. The decision
  was sound when made; the ground under it has moved.

`crf/examples/policy-no-kubernetes.yaml` is the worked example: its moratorium
has genuinely lapsed, and the EKS decision that validated against it while it
was in force is still reported clean.

---

## Supersession

Context evolves through replacement:

```yaml
supersedes:
  entity_id: "44444444-4444-4444-4444-444444444444"
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
    - context_id: "44444444-4444-4444-4444-444444444444"
      context_type: "policy"
      context_name: "Kubernetes Migration Moratorium"
      validation_status: "acknowledged"
      advisory_notes: "Exception granted by VP Engineering due to business urgency"
```

Note the status. The conflict here has been reviewed and accepted by someone
with the authority to accept it, which makes it `acknowledged`, not `violated`.
`violated` is for conflicts nobody has ruled on yet. See
[Validation Status Values](#validation-status-values) below.

### Producing Context (DRF → CRF)

```yaml
# In DRF document
context_validation:
  context_outputs:
    - action: "creates"
      entity_type: "fact"
      entity_data:
        id: "99999999-9999-4999-8999-999999999999"
        type: "fact"
        name: "EKS Production Environment Live"
        attributes:
          fact_type: "status"
          value: "production"
          verified: true
        provenance:
          source: "decision:a1b2c3d4-e5f6-7890-abcd-ef1234567890"
          created_at: "2024-03-01T17:45:00Z"
      reason: "EKS migration decision establishes new production environment"
```

---

## Context Output Semantics

`context_outputs` is the write path from a decision back into the context graph.
Each action has a different payload and a different effect, and implementations
must agree on all three or the same document will mean different things in
different tools.

| Action | `entity_id` | `entity_data` | Effect |
|--------|-------------|---------------|--------|
| `creates` | Not used | **Required**: a complete CRF entity | A new entity enters the graph |
| `updates` | **Required** | **Required**: a partial merge patch | Named fields on the existing entity are replaced |
| `invalidates` | **Required** | **Must be absent** | The existing entity stops applying |

All three requirements are enforced by the DRF schema.

### creates

`entity_data` holds everything that would appear under `entity:` in a
standalone CRF document - `id`, `type`, `name`, and `provenance` included. It is
a complete entity, and it MUST validate against the CRF entity definition. Do
not include `crf_version`: the version comes from the enclosing DRF document.

The new entity's `provenance.source` SHOULD be `decision:{uuid}` naming the
decision that produced it, which is what makes the write path auditable in both
directions.

### updates

`entity_data` is a **partial merge patch**, not a replacement. Only the fields
present in the patch are changed; every field absent from the patch is left
exactly as it was. Merging is key-by-key at each level of the object:

```yaml
# doc-check: skip
# Existing entity                    Patch                     Result
attributes:                          attributes:               attributes:
  policy_type: "compliance"            owner: "New Owner"        policy_type: "compliance"
  owner: "Old Owner"                                             owner: "New Owner"
  review_cycle: "annually"                                       review_cycle: "annually"
```

Because a patch is not a whole entity, `entity_data` under `updates` will not
validate against the CRF entity definition, and is not expected to: it has no
`id`, `type`, or `name`. The entity being changed is named by `entity_id`.

Two consequences worth stating explicitly:

- **Arrays are replaced, not merged.** A patch that sets `tags` replaces the
  whole list. There is no element-wise array merge, and no way to express
  "append one tag" - send the intended final list.
- **There is no deletion syntax.** A patch cannot remove a field. If context
  has genuinely stopped applying, `invalidates` it and `creates` a successor
  that `supersedes` it. Supersession, not mutation, is how CRF records that
  something is no longer true.

### invalidates

The entity named by `entity_id` stops applying from this decision onward. It is
not deleted: superseded and invalidated entities stay in the graph so that past
decisions remain interpretable. `entity_data` MUST NOT be present, because
invalidation carries no new data.

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
