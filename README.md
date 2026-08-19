# Reasoning Formats

**Vendor-neutral, machine-readable formats for structured decision documentation and organizational context.**

[![Validate](https://github.com/reasoning-formats/reasoning-formats/actions/workflows/validate.yml/badge.svg)](https://github.com/reasoning-formats/reasoning-formats/actions/workflows/validate.yml)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![DRF Version](https://img.shields.io/badge/DRF-v0.3.0-green.svg)](./drf)
[![CRF Version](https://img.shields.io/badge/CRF-v0.3.0-green.svg)](./crf)

---

## Overview

This repository contains two complementary specification formats:

| Format | Purpose | Status |
|--------|---------|--------|
| **[DRF](./drf)** | Decision Reasoning Format - Captures decisions with explicit reasoning | Draft v0.3.0 |
| **[CRF](./crf)** | Context Reasoning Format - Models organizational context as a knowledge graph | Draft v0.3.0 |

Together, they enable **context-aware decision documentation** where decisions can reference and be validated against organizational policies, facts, and constraints.

---

## The Problem

> *"Why did we choose PostgreSQL over MongoDB?"*

The answer is usually lost in Slack threads, meeting notes, or someone's memory. When that person leaves, the knowledge goes with them.

**Reasoning Formats solve this by providing:**

1. **Structured decisions** - A consistent template for documenting what was decided and why
2. **Organizational context** - A knowledge graph of policies, systems, and constraints
3. **Validation** - Automatic detection of conflicts between decisions and context
4. **Bidirectional updates** - Decisions that produce new organizational facts

---

## Quick Start

### A Simple Decision (DRF)

```yaml
drf_version: "0.3.0"

decision:
  id: "550e8400-e29b-41d4-a716-446655440000"
  title: "Use PostgreSQL for Primary Database"
  intent: "Select a database that meets our scalability and compliance needs"

context:
  constraints:
    - description: "Must support ACID transactions"
      source: "regulatory"
    - description: "Budget limited to $5000/month"
      source: "budget"
  objectives:
    - description: "Handle 10,000 concurrent users"
      priority: "must_have"

cognitive_state:
  phase: "decision"
  confidence: 85

synthesis:
  decision: "Adopt PostgreSQL 15 on AWS RDS"
  rationale: "Best balance of compliance, cost, and team familiarity"

meta:
  status: "approved"
  created_at: "2024-01-15T09:00:00Z"
```

### Organizational Context (CRF)

```yaml
crf_version: "0.3.0"

entity:
  id: "44444444-4444-4444-4444-444444444444"
  type: policy
  name: "Kubernetes Migration Moratorium"
  description: "No Kubernetes until security audit complete"

  attributes:
    policy_type: architectural
    enforcement: mandatory

  validity:
    valid_until: "2024-06-30T23:59:59Z"  # This policy has since lapsed

  provenance:
    source: "manual"
    created_at: "2023-10-01T00:00:00Z"
```

### Connecting Them Together

```yaml
# In a DRF decision
context_validation:
  context_refs:
    - context_id: "44444444-4444-4444-4444-444444444444"
      context_type: "policy"
      context_name: "Kubernetes Migration Moratorium"
      validation_status: "acknowledged"  # Conflict found, reviewed, and accepted
      advisory_notes: "Exception granted by VP Engineering"
```

---

## Repository Structure

```
reasoning-formats/
├── drf/                    # Decision Reasoning Format
│   ├── schema/            # JSON Schema definition
│   ├── spec/              # Specification + DRF/CRF validation rules
│   └── examples/          # Example decisions
│
├── crf/                    # Context Reasoning Format
│   ├── schema/            # JSON Schema definition
│   ├── spec/              # CRF specification
│   └── examples/          # Example context entities
│
├── integration/            # Examples using both formats together
│   └── examples/
│
├── tests/invalid/          # Documents the schemas MUST reject
│
└── scripts/                # Validation tooling
    ├── validate-examples.py    # examples validate against the schemas
    ├── test-schemas.py         # invalid documents are actually rejected
    ├── validate-semantics.py   # semantic rules the schemas cannot express
    └── validate-docs.py        # YAML embedded in this documentation
```

### Validating locally

All four checks run in CI on every push and pull request:

```bash
pip install -r requirements-dev.txt

python3 scripts/validate-examples.py      # examples match the schemas
python3 scripts/test-schemas.py           # invalid documents are rejected
python3 scripts/validate-semantics.py     # add --strict to fail on warnings
python3 scripts/validate-docs.py          # YAML in the docs still validates
```

> Install from `requirements-dev.txt` rather than `pip install pyyaml jsonschema`.
> Without the pinned `rfc3339-validator`, `jsonschema` silently skips every
> `date-time` check and a passing run proves less than it looks like it does.
> `validate-examples.py` refuses to run rather than report a success it cannot
> stand behind.

---

## Key Concepts

### DRF (Decision Reasoning Format)

Documents **what** was decided and **why**:

- **Decision** - Identity and intent
- **Context** - Constraints and objectives
- **Reasoning** - Patterns applied (risk-based, comparative, etc.)
- **Assumptions** - Premises accepted
- **Tensions** - Tradeoffs acknowledged
- **Synthesis** - Final outcome with alternatives

[Read the DRF documentation →](./drf)

### CRF (Context Reasoning Format)

Models organizational knowledge as a **graph**:

- **Entities** - Organizations, systems, policies, facts, capabilities
- **Relationships** - owns, depends_on, constrains, supersedes
- **Validity** - Optional temporal bounds
- **Provenance** - Where context came from

[Read the CRF documentation →](./crf)

### Integration

When used together:

1. **Decisions reference context** for validation
2. **Conflicts are surfaced** (advisory, not blocking)
3. **Decisions produce new context** (bidirectional flow)

[See integration examples →](./integration)

---

## Design Principles

1. **Reasoning First** - Capture *how* and *why*, not just *what*
2. **Separation of Concerns** - DRF for decisions, CRF for context
3. **Advisory Validation** - Surface conflicts, don't block humans
4. **Human + Machine Readable** - YAML/JSON, not proprietary formats
5. **Vendor Neutral** - No lock-in to specific tools or platforms

---

## Use Cases

- Technical architecture decisions
- Infrastructure and platform design
- Security and risk reviews
- Post-mortems and design retrospectives
- AI-assisted decision support
- Compliance and audit trails

---

## Status

Both formats are in **Draft v0.3.0** - stabilizing core concepts before formal versioning. See the [CHANGELOG](./CHANGELOG.md) for release history.

Feedback and contributions welcome!

---

## License

Licensed under the [Apache License 2.0](./LICENSE).
