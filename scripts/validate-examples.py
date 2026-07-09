#!/usr/bin/env python3
"""Validate all example files against the DRF and CRF JSON Schemas.

Handles multi-document YAML streams (used by CRF examples, where each
document is an independent CRF entity document). Integration examples are
dispatched per document based on the presence of `drf_version` or
`crf_version`.

Usage:
    python3 scripts/validate-examples.py

Requires: pyyaml, jsonschema
    pip install pyyaml jsonschema
"""

import json
import sys
from pathlib import Path

import yaml
from jsonschema import Draft7Validator, FormatChecker

REPO_ROOT = Path(__file__).resolve().parent.parent

EXAMPLE_GLOBS = [
    "drf/examples/*.yaml",
    "crf/examples/*.yaml",
    "integration/examples/*.yaml",
]


def load_validator(schema_path: Path) -> Draft7Validator:
    with open(schema_path, encoding="utf-8") as f:
        schema = json.load(f)
    Draft7Validator.check_schema(schema)
    return Draft7Validator(schema, format_checker=FormatChecker())


def pick_validator(doc: dict, validators: dict, path: Path):
    if "drf_version" in doc:
        return validators["drf"]
    if "crf_version" in doc:
        return validators["crf"]
    return None


def main() -> int:
    validators = {
        "drf": load_validator(REPO_ROOT / "drf/schema/drf-schema.json"),
        "crf": load_validator(REPO_ROOT / "crf/schema/crf-schema.json"),
    }

    errors = 0
    files_checked = 0
    docs_checked = 0

    for pattern in EXAMPLE_GLOBS:
        for path in sorted(REPO_ROOT.glob(pattern)):
            files_checked += 1
            file_errors = 0
            rel = path.relative_to(REPO_ROOT)
            with open(path, encoding="utf-8") as f:
                try:
                    docs = list(yaml.safe_load_all(f))
                except yaml.YAMLError as exc:
                    print(f"FAIL  {rel}: YAML parse error: {exc}")
                    errors += 1
                    continue

            for index, doc in enumerate(docs):
                if doc is None:
                    continue
                docs_checked += 1
                validator = pick_validator(doc, validators, path)
                if validator is None:
                    print(
                        f"FAIL  {rel} [doc {index}]: missing "
                        f"'drf_version' or 'crf_version' field"
                    )
                    file_errors += 1
                    continue
                for error in validator.iter_errors(doc):
                    location = "/".join(str(p) for p in error.absolute_path) or "<root>"
                    print(f"FAIL  {rel} [doc {index}] at {location}: {error.message}")
                    file_errors += 1

            errors += file_errors
            if file_errors == 0:
                print(f"ok    {rel} ({len([d for d in docs if d is not None])} document(s))")

    print(
        f"\nChecked {docs_checked} document(s) across {files_checked} file(s): "
        f"{'all valid' if errors == 0 else f'{errors} error(s)'}"
    )
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
