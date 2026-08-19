#!/usr/bin/env python3
"""Validate every example file against the DRF and CRF JSON Schemas.

Handles multi-document YAML streams (used by CRF examples, where each
document is an independent CRF entity document). Integration examples are
dispatched per document based on the presence of `drf_version` or
`crf_version`.

Usage:
    python3 scripts/validate-examples.py

Requires the pinned tooling dependencies:
    pip install -r requirements-dev.txt
"""

import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import REPO_ROOT, EXAMPLE_GLOBS, load_validators, pick_kind  # noqa: E402


def main() -> int:
    validators = load_validators()
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
                kind = pick_kind(doc)
                if kind is None:
                    print(
                        f"FAIL  {rel} [doc {index}]: missing "
                        f"'drf_version' or 'crf_version' field"
                    )
                    file_errors += 1
                    continue
                for error in validators[kind].iter_errors(doc):
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
