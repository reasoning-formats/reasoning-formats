# Security Policy

## What this repository contains

This repository holds specification text, JSON Schemas, example documents, and
the Python scripts that validate them. It ships no runtime library and no
service. The realistic security surface is therefore small, but not empty:

- The validation scripts parse untrusted YAML and JSON.
- The schemas are consumed by third-party tooling, so a schema that fails to
  reject a malformed document can weaken a downstream validator.
- The examples are copied into other people's documents.

## Supported versions

Only the latest draft receives fixes. The formats are pre-1.0 and evolve
through the CHANGELOG rather than through backported patches.

| Version | Supported |
|---------|-----------|
| 0.3.x   | Yes       |
| < 0.3   | No        |

## Reporting a vulnerability

Please report suspected vulnerabilities privately, **not** through a public
issue:

1. Preferred: open a
   [private security advisory](https://github.com/reasoning-formats/reasoning-formats/security/advisories/new).
2. Alternatively, email **set.is.set@gmail.com** with "SECURITY" in the subject.

Please include what you observed, how to reproduce it, and the impact you
believe it has. You can expect an acknowledgement within seven days and an
assessment within thirty.

## Things that are not vulnerabilities

- A schema accepting a document you consider semantically wrong. Semantic rules
  live in `drf/spec/validation-rules.md` and are enforced by
  `scripts/validate-semantics.py`; open a normal issue for those.
- The examples describing a fictional company with weak-sounding practices.
  They are illustrations, not recommendations.
- Advisory validation not blocking a decision. That is the design, documented
  under "Advisory Validation" in both specifications.
