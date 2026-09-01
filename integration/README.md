# DRF + CRF Integration

This directory contains examples showing how [DRF](../drf) (Decision Reasoning Format) and [CRF](../crf) (Context Reasoning Format) work together.

---

## The Bidirectional Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         CRF Knowledge Graph                              │
│  ┌──────────┐    owns     ┌──────────┐    constrains   ┌──────────┐    │
│  │   Org    │───────────►│  System  │◄────────────────│  Policy  │    │
│  │  "ACME"  │            │"Prod Infra│                │ "No K8s" │    │
│  └──────────┘            └──────────┘                 └──────────┘    │
│       │                       ▲                            │          │
│       │                       │ produces                   │          │
│       │                       │                            │          │
│       │                  ┌────┴─────┐                      │          │
│       │                  │ New Fact │                      │          │
│       │                  │"EKS Live"│                      │          │
│       │                  └──────────┘                      │          │
└───────│──────────────────────▲─────────────────────────────│──────────┘
        │                      │                             │
        │              context_outputs                       │
        │              (creates new fact)                    │
        │                      │                             │
        │                      │            context_refs     │
        │                      │            (validates)      │
        │                      │                             ▼
┌───────│──────────────────────│─────────────────────────────────────────┐
│       │              DRF Decision                                       │
│       │                                                                 │
│       │  decision: "Migrate to EKS"                                    │
│       │                                                                 │
│       │  context_validation:                                           │
│       │    context_refs:                                               │
│       │      - context_name: "No K8s Policy"                           │
│       │        validation_status: acknowledged  ◄── Conflict detected! │
│       │        advisory_notes: "VP approved exception"                 │
│       │                                                                 │
│       │    context_outputs:                                            │
│       │      - action: creates                                         │
│       │        entity_type: fact                                       │
│       │        entity_data: { name: "EKS Production Live" }            │
│       │                                                                 │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## How It Works

### 1. Context References (CRF → DRF)

Decisions reference CRF entities to validate against organizational context:

```yaml
# In DRF document
context_validation:
  validated_at: "2024-02-28T10:00:00Z"
  context_refs:
    - context_id: "44444444-4444-4444-4444-444444444444"
      context_type: policy
      context_name: "Kubernetes Migration Moratorium"
      validation_status: acknowledged
      advisory_notes: "Exception approved by VP Engineering"
```

### Validation Statuses

| Status | Meaning |
|--------|---------|
| `satisfied` | Decision complies with context |
| `violated` | Decision conflicts (needs attention) |
| `acknowledged` | Conflict accepted with justification |
| `not_applicable` | Referenced but not directly relevant |

### 2. Context Outputs (DRF → CRF)

Decisions can create, update, or invalidate CRF entities:

```yaml
# In DRF document
context_validation:
  context_outputs:
    - action: "creates"
      entity_type: "fact"
      entity_data:
        id: "99999999-9999-4999-8999-999999999999"
        type: fact
        name: "EKS Production Environment"
        attributes:
          fact_type: status
          value: "production"
        provenance:
          source: "decision:a1b2c3d4-..."  # Links back to decision
```

### Output Actions

| Action | Description |
|--------|-------------|
| `creates` | Decision creates new context entity |
| `updates` | Decision modifies existing entity |
| `invalidates` | Decision makes entity no longer valid |

---

## Workflow Example

```
1. CONTEXT EXISTS
   Policy: "No Kubernetes until Q4 2024"

              │
              ▼

2. DECISION REFERENCES CONTEXT
   Decision: "Migrate to EKS"
   → References policy
   → validation_status: "violated"

              │
              ▼

3. CONFLICT SURFACED (Advisory)
   "This decision conflicts with policy X"

              │
              ▼

4. HUMAN REVIEWS
   VP Engineering: "Business need justifies exception"
   → Changes status to "acknowledged"
   → Adds advisory_notes with justification

              │
              ▼

5. DECISION APPROVED
   Status: approved

              │
              ▼

6. CONTEXT UPDATED (via context_outputs)
   New fact created: "EKS Production Live"
   Architecture standard updated
   Policy may be superseded
```

---

## Key Principles

### Advisory, Not Blocking

All validation is **advisory**. The system surfaces conflicts but never blocks decisions automatically. This:

- Preserves human judgment
- Allows documented exceptions
- Creates audit trail for compliance

### Explicit Over Implicit

Decisions must **explicitly reference** the context they were validated against. This:

- Makes reasoning transparent
- Enables replay/audit
- Prevents hidden assumptions

### Bidirectional Updates

Decisions don't just consume context - they **produce** it. Every significant decision should consider:

- What new facts does this establish?
- What existing context does this change?
- What policies should be reconsidered?

---

## Examples

### Full Integration Examples

[`infrastructure-eks-with-context.drf.yaml`](./examples/infrastructure-eks-with-context.drf.yaml)

A complete example showing:
- A Kubernetes migration decision
- References to multiple CRF entities (policy, system, capability)
- An acknowledged policy violation with justification
- Context outputs that create new organizational facts

[`security-credential-rotation-with-context.drf.yaml`](./examples/security-credential-rotation-with-context.drf.yaml)

A time-critical security decision showing:
- Credential rotation after an API key compromise
- Validation against compliance policies under incident-response pressure
- Context outputs recording the incident as a new organizational fact

---

## Getting Started

1. **Start with CRF**: Document your organizational context
   - Policies, systems, teams, capabilities

2. **Create DRF decisions**: Reference relevant context
   - Use `context_refs` to link to CRF entities

3. **Handle conflicts**: When violations occur
   - Review and either modify decision or acknowledge

4. **Update context**: When decisions change reality
   - Use `context_outputs` to create new facts

---

## Related Documentation

- [DRF Specification](../drf/README.md)
- [CRF Specification](../crf/README.md)
- [Validation Rules](../drf/spec/validation-rules.md) (includes context validation rules)
