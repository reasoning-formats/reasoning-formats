#!/usr/bin/env python3
"""Assert that the schemas REJECT the documents in tests/invalid/.

scripts/validate-examples.py proves that valid documents are accepted. On its
own that is a weak guarantee: a schema that had lost its `required` lists, or
its `additionalProperties: false`, would still pass. These fixtures pin the
rejections, so loosening a schema by accident fails the build.

Each fixture is a single YAML document whose first line declares the substring
its rejection message must contain:

    # expect: 'provenance' is a required property

Usage:
    python3 scripts/test-schemas.py

Requires the pinned tooling dependencies:
    pip install -r requirements-dev.txt
"""

import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import REPO_ROOT, load_validators, pick_kind  # noqa: E402

FIXTURES = REPO_ROOT / "tests/invalid"
MARKER = "# expect:"


def main() -> int:
    validators = load_validators()
    paths = sorted(FIXTURES.glob("*.yaml"))
    if not paths:
        print(f"FAIL  no fixtures found in {FIXTURES.relative_to(REPO_ROOT)}")
        return 1

    failures = 0
    for path in paths:
        rel = path.relative_to(REPO_ROOT)
        text = path.read_text(encoding="utf-8")
        first = text.splitlines()[0].strip()
        if not first.startswith(MARKER):
            print(f"FAIL  {rel}: first line must start with {MARKER!r}")
            failures += 1
            continue
        expected = first[len(MARKER):].strip()

        doc = yaml.safe_load(text)
        kind = pick_kind(doc)
        if kind is None:
            print(f"FAIL  {rel}: fixture has neither drf_version nor crf_version")
            failures += 1
            continue

        messages = [e.message for e in validators[kind].iter_errors(doc)]
        if not messages:
            print(f"FAIL  {rel}: expected rejection ({expected!r}) but the document validated")
            failures += 1
        elif not any(expected in m for m in messages):
            print(f"FAIL  {rel}: rejected, but no message contained {expected!r}")
            for m in messages[:3]:
                print(f"          got: {m}")
            failures += 1
        else:
            print(f"ok    {rel}")

    print(
        f"\nChecked {len(paths)} rejection fixture(s): "
        f"{'all rejected as expected' if failures == 0 else f'{failures} failure(s)'}"
    )
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
