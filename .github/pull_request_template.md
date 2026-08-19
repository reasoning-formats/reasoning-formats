## What changed

<!-- One or two sentences. For spec changes, link the issue where the approach was agreed. -->

Closes #

## Type of change

- [ ] Example (new or corrected)
- [ ] Documentation
- [ ] Schema change (breaking)
- [ ] Schema change (backward compatible)
- [ ] Tooling / CI

## Checklist

- [ ] `pip install -r requirements-dev.txt` and all four checks pass locally:
  - [ ] `python3 scripts/validate-examples.py`
  - [ ] `python3 scripts/test-schemas.py`
  - [ ] `python3 scripts/validate-semantics.py --strict`
  - [ ] `python3 scripts/validate-docs.py`
- [ ] Schema changes add a rejection fixture under `tests/invalid/`
- [ ] Spec changes were agreed in an issue first (see CONTRIBUTING.md)
- [ ] `CHANGELOG.md` updated
- [ ] Commits are signed off (`git commit -s`)
