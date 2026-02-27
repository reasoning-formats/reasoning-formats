# Contributing to Reasoning Formats

Thank you for your interest in contributing to the Reasoning Formats project (DRF and CRF). This document explains how to get involved.

## Ways to Contribute

### Report Bugs or Spec Issues

If you find a problem with the schemas, validation rules, or specification text, please [open a bug report](../../issues/new?template=bug_report.md). This includes:

- Schema validation errors or inconsistencies
- Ambiguities in the specification text
- Errors in example files

### Suggest Features

Have an idea for a new field, entity type, or tooling improvement? [Open a feature request](../../issues/new?template=feature_request.md).

### Contribute Examples (Most Valuable Contribution)

Real-world examples are the single most valuable contribution you can make. They help others understand the formats, expose gaps in the spec, and serve as informal test cases.

See the [example guidelines](#example-guidelines) below, then [use the example template](../../issues/new?template=new_example.md) to propose one.

### Propose Spec Changes

Spec changes follow a two-step process:

1. **Open a GitHub Issue first** using the [spec feedback template](../../issues/new?template=spec_feedback.md). Describe the problem and your proposed solution. Wait for discussion before writing code.
2. **Submit a Pull Request** only after the approach is agreed upon in the issue. Reference the issue number in your PR description.

This avoids wasted effort on changes that may not align with the project direction.

---

## Example Guidelines

Examples live in `drf/examples/`, `crf/examples/`, and `integration/examples/`. When contributing examples, please follow these conventions:

### YAML Formatting

- Use 2-space indentation (no tabs)
- Quote all string values (e.g., `title: "My Decision"`)
- Use blank lines to separate top-level sections
- Include the version field at the top (`drf_version: "0.1.0"` or `crf_version: "0.1.0"`)

### IDs

- Use UUID v4 format for all `id` fields (e.g., `"550e8400-e29b-41d4-a716-446655440000"`)
- Use distinct UUIDs across your example -- do not reuse IDs from existing examples

### Content

- Use realistic but fictional scenarios (no real company data unless you have permission)
- Include enough detail to be useful -- minimal examples belong in the README, not in `examples/`
- Add YAML comments (`#`) sparingly to explain non-obvious choices
- Name files descriptively using kebab-case (e.g., `api-gateway-selection.yaml`)

### Validating Examples Against Schemas

You can validate your examples against the JSON Schema definitions:

```bash
# Using ajv-cli (install with: npm install -g ajv-cli)
ajv validate -s drf/schema/drf-schema.json -d drf/examples/your-example.yaml

# Using check-jsonschema (install with: pip install check-jsonschema)
check-jsonschema --schemafile drf/schema/drf-schema.json drf/examples/your-example.yaml
```

Make sure your example validates cleanly before submitting a PR.

---

## Pull Request Process

1. Fork the repository and create a branch from `main`
2. Make your changes, following the guidelines above
3. Validate any new or modified examples against the schemas
4. Submit your PR with a clear description of what changed and why
5. Reference any related issues (e.g., "Closes #12")

### What to Expect

- A maintainer will review your PR, usually within a week
- You may be asked for changes -- this is normal and collaborative
- Once approved, a maintainer will merge your PR

---

## Developer Certificate of Origin (DCO)

By contributing to this project, you agree to the [Developer Certificate of Origin](https://developercertificate.org/). This means you certify that you wrote (or have the right to submit) your contribution under the project's Apache 2.0 license.

Sign off on your commits by adding a `Signed-off-by` line:

```
Signed-off-by: Your Name <your.email@example.com>
```

You can do this automatically with `git commit -s`.

---

## Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](https://www.contributor-covenant.org/version/2/1/code_of_conduct/). By participating, you agree to uphold a welcoming, respectful, and harassment-free environment for everyone.

If you experience or witness unacceptable behavior, please report it by opening an issue or contacting a maintainer directly.

---

## Questions?

If you are unsure about anything, open a GitHub Issue or start a Discussion. There are no bad questions -- especially at v0.1.0, where everything is still taking shape.
