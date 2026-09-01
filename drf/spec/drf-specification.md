# DRF — Decision Reasoning Format

**Draft Specification v0.3.0**

---

## Purpose

DRF (Decision Reasoning Format) is a vendor-neutral, machine-readable format for representing technical and strategic decisions together with their explicit reasoning.

It is designed to:

- **Capture how and why** a decision was made, not just the outcome
- **Enable auditability**, traceability, and post-hoc analysis
- **Be usable by humans**, automation, and AI systems
- **Remain independent** from any specific LLM, tool, or platform

> **DRF is not a prompt format.**
> It is a structured artifact representing a completed (or in-progress) decision process.

---

## Conformance

The key words MUST, MUST NOT, REQUIRED, SHALL, SHOULD, SHOULD NOT, RECOMMENDED,
MAY, and OPTIONAL in this document and in the companion documents listed under
[See Also](#see-also) are to be interpreted as described in
[RFC 2119](https://www.rfc-editor.org/rfc/rfc2119).

Normative content is split across three documents, and it is worth being precise
about which one governs what:

| Document | Governs |
|----------|---------|
| [`drf-schema.json`](../schema/drf-schema.json) | The structure of a single document: which fields exist, their types, which are required. A document that fails this schema is not DRF |
| [`validation-rules.md`](./validation-rules.md) | Semantics the schema cannot express: lifecycle transitions, cross-document references, temporal ordering, uniqueness |
| This document | Purpose, design rationale, and how DRF relates to adjacent formats |

Where this document and the schema appear to disagree, the schema wins, and the
disagreement is a bug worth reporting. A per-field reference is maintained in
the [DRF README](../README.md#field-reference).

---

## Design Principles

### Reasoning First
Decisions must expose assumptions, tensions, and reasoning paths explicitly.

### Separation of Concerns
- DRF defines **representation**
- Engines, tools, or AI systems define **generation**

### Deterministic Structure
The same decision should serialize into a predictable structure.

### Human + Machine Readable
YAML/JSON first, natural language only where unavoidable.

### Domain-Agnostic Core
Domain-specific reasoning can be layered without changing the core spec.

---

## Core Concepts

A DRF document represents a **decision session**, composed of:

| Component | Description |
|-----------|-------------|
| **Decision Context** | What is being decided, under which constraints and goals |
| **Cognitive State** | The current phase of reasoning (exploration, analysis, synthesis, decision) |
| **Reasoning Applied** | Explicit reasoning patterns used (operational, risk-based, counterfactual, etc.) |
| **Interventions** | Key questions, challenges, or prompts that shaped the reasoning |
| **Assumptions** | Explicit or implicit premises accepted during the decision |
| **Unresolved Tensions** | Known trade-offs or risks left open or accepted |
| **Synthesis** | The consolidated outcome: decision, rationale, and next steps |

---

## High-Level Structure

```yaml
# doc-check: skip
# A field-name skeleton, not a valid document: every value is intentionally blank.
drf_version:              # required

decision:
  id:
  title:
  domain:
  intent:

context:
  constraints:
  objectives:
  environment:

cognitive_state:
  phase:
  confidence:

reasoning:
  patterns_applied:
  notes:

interventions:
  - id:
    type:
    content:

assumptions:
  - description:
    confidence:

unresolved_tensions:
  - description:
    impact:

synthesis:                # required once the phase reaches synthesis/decision
  decision:
  rationale:
  follow_ups:
  alternatives:

context_validation:       # optional; links the decision to CRF entities
  validated_at:
  context_refs:
  context_outputs:

meta:
  created_at:
  status:
  actors:
  source:
```

This structure is illustrative; the [JSON Schema](../schema/drf-schema.json)
defines required vs optional fields, and the
[field reference](../README.md#field-reference) documents each one.

---

## File Naming

A DRF document SHOULD be stored in a file named `<descriptive-name>.drf.yaml`
(or `.drf.yml` / `.drf.json`). The descriptive part is free-form; the
`.drf` infix is what identifies the file as a DRF document without parsing it.

This is a RECOMMENDATION, not a conformance requirement. A document that
validates against the schema is a valid DRF document whatever its filename, and
no validator rejects a file for being named otherwise.

The reason to follow it is tooling. Editors and language servers decide which
schema to apply from the filename, so a distinctive suffix is what makes
field-name completion, enum suggestions, and inline validation work while the
document is being written. A generic `*.yaml` pattern cannot be used for this,
because it would claim every YAML file in the project.

---

## Intended Use Cases

- Technical architecture decisions
- Infrastructure and platform design
- Security and risk reviews
- Post-mortems and design retrospectives
- AI-assisted decision support
- Audio/meeting transcription → structured decision artifacts

---

## Non-Goals

- Replacing human decision-making
- Acting as a chat or conversational format
- Encoding proprietary business logic
- Enforcing a single reasoning methodology
- **Blocking anything.** Validation against organizational context is advisory
  by design. DRF records that a conflict was found and what was decided about
  it; it never arbitrates the conflict
- **Judging decision quality.** A document can be perfectly valid and describe a
  terrible decision. DRF makes reasoning inspectable so that humans can judge
  it; it has no opinion of its own

---

## Related Work

DRF is informed by but intentionally distinct from existing formats:

### Knowledge Graph Standards (RDF, OWL, JSON-LD)

These W3C standards excel at representing facts and relationships in a semantically interoperable way. DRF chose YAML/JSON over JSON-LD because:

- **Simplicity**: Developers can read/write DRF without learning RDF semantics
- **AI-native**: LLMs can generate and consume DRF more reliably than RDF triples
- **Focus**: DRF captures reasoning processes, not general knowledge

### Decision Ontologies (W3C DO, DecPROV)

The W3C Decision Ontology (2012) and DecPROV extension provide OWL vocabularies for decision modeling. DRF differs in:

- **Cognitive modeling**: DRF explicitly tracks reasoning phases and confidence
- **Intervention capture**: DRF records questions/challenges that shaped thinking
- **Tension preservation**: DRF documents unresolved trade-offs, not just outcomes
- **Prospective use**: DRF supports in-progress decisions, not just retrospective analysis

### Architecture Decision Records (ADRs)

ADRs are prose-based markdown documents popularized by Michael Nygard. DRF provides:

- **Machine-readable structure**: Every field is typed and validatable
- **Reasoning patterns**: Explicit vocabulary for how decisions were reasoned
- **Context integration**: CRF links decisions to organizational facts and policies

### Decision Model and Notation (DMN)

DMN (OMG standard) models decision **logic** (rules, tables). DRF models decision **reasoning**—the cognitive process and justification, not the execution logic.

---

## Design Choice: AI-Native Over Semantic Web

DRF prioritizes consumption and generation by AI systems over interoperability with semantic web tooling. This means:

- **Simple YAML/JSON** over RDF triples
- **Explicit field structure** over ontological inference
- **Human + AI readability** over SPARQL queryability

This trade-off enables:
- Direct LLM generation without RDF serialization complexity
- Easy validation with standard JSON Schema tools
- Simpler adoption for development teams

---

## Evolution

DRF is expected to evolve through:

- Public RFC-style discussion
- Reference implementations
- Domain-specific extensions (without breaking core compatibility)

**Backward compatibility and clarity take precedence over rapid expansion.**

---

## Status

This document represents **DRF Draft v0.3.0**.

The goal of this phase is to stabilize the core concepts and structure before formal versioning.

---

## See Also

- [DRF JSON Schema](../schema/drf-schema.json)
- [Validation Rules](./validation-rules.md)
- [CRF Specification](../../crf/spec/crf-specification.md) - Companion format for organizational context
