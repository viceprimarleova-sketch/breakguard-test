# BreakGuard V0.1

BreakGuard scans a code repository for known Shopify API deprecations, points to the affected file and line, provides the recorded source and remediation, and applies conservative fixes only for rules that are explicitly safe enough to automate.

## Current V0.1 rules

- `Customer.lastIncompleteCheckout`
- `DraftOrderDiscountNotAppliedWarning.priceRule`
- `ScriptTag` usage (manual review only)

Rules are scoped to relevant source-file extensions so documentation, YAML workflows, and unrelated text files do not create obvious false positives.

## Quick install for testers

BreakGuard is not published to PyPI yet. Install the current product branch directly from GitHub:

```bash
python -m pip install "git+https://github.com/viceprimarleova-sketch/breakguard-test.git@breakguard/product-v0.1"
breakguard --version
breakguard --help
```

For a complete safe-testing walkthrough, see `TESTER_GUIDE.md`.

## Run

```bash
breakguard /path/to/repo
breakguard /path/to/repo --json
breakguard /path/to/repo --fix-preview
breakguard /path/to/repo --apply-fixes
```

`--fix-preview` prints a unified diff for supported automatic repairs without modifying the repository. Review the preview before using `--apply-fixes`.

You can also run directly from a source checkout:

```bash
python -m breakguard.cli /path/to/repo
python -m pytest -q
```

The scanner returns non-zero while findings remain, which makes it suitable for CI. For manual testing, exit code `1` means findings remain; it does not necessarily mean BreakGuard crashed.

## Safety

Automatic fixes are deliberately conservative. Review generated diffs before merge or deployment. Manual-only findings remain unchanged.
