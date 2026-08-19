#!/usr/bin/env python3
"""Validate the YAML embedded in Markdown documentation.

Documentation snippets drift out of sync with the schemas just as easily as
example files do, but nothing used to check them. Two classes of problem are
caught here:

1. Complete documents. Any fenced ``yaml`` block containing `drf_version:` or
   `crf_version:` at the top level is a full document and is validated against
   the corresponding schema.

2. Placeholder identifiers. Fragments cannot be schema-validated on their own,
   but a fragment that writes `context_id: "uuid-of-policy"` is still teaching
   readers something the schema rejects. Every `id`-shaped key in every fenced
   YAML block must carry a real UUID.

A block may opt out of both checks with a `# doc-check: skip` comment on its
first line - use that only for deliberately abbreviated illustrations.

Usage:
    python3 scripts/validate-docs.py
"""

import re
import sys
import uuid
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import REPO_ROOT, load_validators, pick_kind  # noqa: E402

FENCE = re.compile(r"^```ya?ml[^\n]*\n(.*?)^```", re.S | re.M)
ID_KEYS = {"id", "context_id", "target_id", "entity_id"}
SKIP = "# doc-check: skip"


def iter_markdown():
    for path in sorted(REPO_ROOT.rglob("*.md")):
        if any(part in {".git", "node_modules"} for part in path.parts):
            continue
        yield path


def bad_ids(node, path=""):
    """Yield (json_pointer, value) for id-shaped keys that are not UUIDs."""
    if isinstance(node, dict):
        for key, value in node.items():
            here = f"{path}/{key}"
            if key in ID_KEYS and isinstance(value, str):
                try:
                    uuid.UUID(value)
                except ValueError:
                    yield here, value
            elif not str(key).startswith("x_"):
                yield from bad_ids(value, here)
    elif isinstance(node, list):
        for i, item in enumerate(node):
            yield from bad_ids(item, f"{path}[{i}]")


def main() -> int:
    validators = load_validators()
    errors = 0
    blocks = 0
    documents = 0

    for path in iter_markdown():
        rel = path.relative_to(REPO_ROOT)
        source = path.read_text(encoding="utf-8")
        for match in FENCE.finditer(source):
            body = match.group(1)
            line = source[: match.start()].count("\n") + 1
            if body.lstrip().startswith(SKIP):
                continue
            blocks += 1
            try:
                docs = [d for d in yaml.safe_load_all(body) if d is not None]
            except yaml.YAMLError as exc:
                print(f"FAIL  {rel}:{line}: YAML parse error: {str(exc).splitlines()[0]}")
                errors += 1
                continue

            for doc in docs:
                for pointer, value in bad_ids(doc):
                    print(
                        f"FAIL  {rel}:{line}: placeholder at {pointer or '<root>'} "
                        f"is not a UUID: {value!r}"
                    )
                    errors += 1

                kind = pick_kind(doc)
                if kind is None:
                    continue
                documents += 1
                for error in validators[kind].iter_errors(doc):
                    location = "/".join(str(p) for p in error.absolute_path) or "<root>"
                    print(f"FAIL  {rel}:{line} at {location}: {error.message}")
                    errors += 1

    print(
        f"\nChecked {blocks} YAML block(s) in documentation "
        f"({documents} complete document(s)): "
        f"{'all valid' if errors == 0 else f'{errors} error(s)'}"
    )
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
