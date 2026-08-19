"""Shared helpers for the repository validation scripts."""

import json
import sys
from pathlib import Path

import yaml
from jsonschema import Draft7Validator, FormatChecker

REPO_ROOT = Path(__file__).resolve().parent.parent

EXAMPLE_GLOBS = (
    "drf/examples/*.yaml",
    "crf/examples/*.yaml",
    "integration/examples/*.yaml",
)

SCHEMAS = {
    "drf": REPO_ROOT / "drf/schema/drf-schema.json",
    "crf": REPO_ROOT / "crf/schema/crf-schema.json",
}


def require_datetime_format_checker() -> FormatChecker:
    """Return a FormatChecker, refusing to run if date-time support is absent.

    `jsonschema` only registers the "date-time" format when the optional
    `rfc3339-validator` package is installed. Without it every date-time
    assertion in both schemas is silently skipped, so a validation run that
    reports success proves far less than it appears to.
    """
    checker = FormatChecker()
    missing = [f for f in ("date-time", "date", "uuid", "email") if f not in checker.checkers]
    if missing:
        sys.stderr.write(
            "ERROR: the installed jsonschema cannot check these formats: "
            f"{', '.join(missing)}.\n"
            "       Timestamps would be silently accepted. Install the pinned\n"
            "       tooling dependencies first:\n\n"
            "           pip install -r requirements-dev.txt\n\n"
        )
        raise SystemExit(2)
    return checker


def load_validators() -> dict:
    checker = require_datetime_format_checker()
    validators = {}
    for name, path in SCHEMAS.items():
        with open(path, encoding="utf-8") as f:
            schema = json.load(f)
        Draft7Validator.check_schema(schema)
        validators[name] = Draft7Validator(schema, format_checker=checker)
    return validators


def pick_kind(doc) -> str | None:
    """Return 'drf', 'crf', or None for a parsed document."""
    if not isinstance(doc, dict):
        return None
    if "drf_version" in doc:
        return "drf"
    if "crf_version" in doc:
        return "crf"
    return None


def iter_example_docs():
    """Yield (relative_path, doc_index, document) for every example document."""
    for pattern in EXAMPLE_GLOBS:
        for path in sorted(REPO_ROOT.glob(pattern)):
            rel = path.relative_to(REPO_ROOT)
            with open(path, encoding="utf-8") as f:
                for index, doc in enumerate(yaml.safe_load_all(f)):
                    if doc is not None:
                        yield rel, index, doc
