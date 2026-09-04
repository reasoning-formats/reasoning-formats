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

Before opening one, check [DESIGN-NOTES.md](./DESIGN-NOTES.md). It records
proposals that were considered and declined, with the reasoning and with what
would reopen each - so a settled question is not re-argued, and so "no" can be
told apart from "not yet".

---

## Example Guidelines

Examples live in `drf/examples/`, `crf/examples/`, and `integration/examples/`. When contributing examples, please follow these conventions:

### YAML Formatting

- Use 2-space indentation (no tabs)
- Quote all string values (e.g., `title: "My Decision"`)
- Use blank lines to separate top-level sections
- Include the version field at the top (`drf_version: "0.3.1"` or `crf_version: "0.3.1"`)
- CRF files may contain multiple entities as a multi-document YAML stream (separated by `---`); each document must carry its own `crf_version` and validate independently

### IDs

- `decision.id`, `entity.id`, and every reference to them (`target_id`,
  `context_id`, `entity_id`) must be a syntactically valid UUID. Generating v4
  is recommended for anything real, but the schema accepts any RFC 4122 UUID,
  and the examples use readable patterned IDs such as
  `"44444444-4444-4444-4444-444444444444"` on purpose -- they are far easier to
  follow across files than random hex
- `interventions[].id` is **not** a UUID. It is a free-form slug
  (`"int-sec-001"`) that only has to be unique within its own document
- Use distinct IDs across your example -- do not reuse IDs from existing
  examples. `decision.id` and `entity.id` must be unique across the whole
  repository, and `scripts/validate-semantics.py` fails the build if they are
  not. Two documents describing the same decision are still two documents: link
  them with `related_decisions` rather than giving them the same ID

### Content

- Use realistic but fictional scenarios (no real company data unless you have permission)
- Include enough detail to be useful -- minimal examples belong in the README, not in `examples/`
- Add YAML comments (`#`) sparingly to explain non-obvious choices
- Name files descriptively using kebab-case, with the format suffix that
  identifies the document type: `api-gateway-selection.drf.yaml` for a DRF
  decision, `policy-data-residency.crf.yaml` for CRF entities. The suffix is
  what lets editors apply the right schema and offer completion as you type

### Timestamps

- All timestamps are RFC 3339 (`"2026-01-15T09:00:00Z"`). `due_date` is a plain
  date (`"2026-01-15"`)
- Do not anchor an example's correctness to the current date. Whether context
  counts as expired is judged against the moment a decision validated against
  it, never against today, precisely so that examples do not decay into
  warnings as time passes

### Validating Your Changes

Install the pinned tooling first:

```bash
pip install -r requirements-dev.txt
```

> Do not `pip install pyyaml jsonschema` by hand. Without `rfc3339-validator`,
> `jsonschema` silently skips every `date-time` format check, and a run that
> reports success has not actually validated a single timestamp.
> `validate-examples.py` exits rather than report a success it cannot back up.

Then run the same four checks CI runs:

```bash
python3 scripts/validate-examples.py       # examples match the schemas
python3 scripts/test-schemas.py            # tests/invalid/ is still rejected
python3 scripts/validate-semantics.py --strict   # cross-document semantic rules
python3 scripts/validate-docs.py           # YAML inside Markdown still validates
```

`validate-semantics.py` reports three severities. `ERROR` always fails.
`WARNING` fails under `--strict`, which is what CI uses. `ADVISORY` is
informational -- use `--quiet` to hide it while you work.

**If you change a schema, add a rejection fixture.** `tests/invalid/` holds
documents that MUST fail validation, each declaring the message it expects on
its first line:

```yaml
# expect: 'provenance' is a required property
```

Without a fixture, a future change that accidentally loosens the schema will
pass CI unnoticed. This is not optional for schema PRs.

### Using a generic validator

For a single-document file you can also use a generic validator:

```bash
# Using check-jsonschema (install with: pip install check-jsonschema)
check-jsonschema --schemafile drf/schema/drf-schema.json drf/examples/your-example.drf.yaml
```

Note that generic validators reject multi-document YAML streams; use the script for CRF files containing multiple entities.

Make sure your example validates cleanly before submitting a PR. Continuous integration runs the same script on every push and pull request, so invalid examples will fail the build.

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

You can do this automatically with `git commit -s`, or retroactively across a
branch with `git rebase --signoff main`.

CI enforces this: the `DCO sign-off` job fails a pull request if any commit in
it lacks the trailer.

---

## Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](https://www.contributor-covenant.org/version/2/1/code_of_conduct/). By participating, you agree to uphold a welcoming, respectful, and harassment-free environment for everyone.

If you experience or witness unacceptable behavior, please report it by opening an issue or contacting a maintainer directly.

---

## Questions?

If you are unsure about anything, open a GitHub Issue or start a Discussion. There are no bad questions -- especially at this early draft stage, where everything is still taking shape.
