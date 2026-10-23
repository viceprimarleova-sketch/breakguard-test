# BreakGuard V0.1

**Current build: 0.1.0rc1 — release candidate for controlled external testing.**

BreakGuard scans a code repository for known Shopify API deprecations, points to the affected file and line, provides the recorded source and remediation, and applies conservative fixes only for rules that are explicitly safe enough to automate.

## Current V0.1 rules

- `Customer.lastIncompleteCheckout`
- `DraftOrderDiscountNotAppliedWarning.priceRule`
- ScriptTag create/update patterns in JavaScript/TypeScript, Ruby, and GraphQL (manual review only)

Rules are scoped to relevant source-file extensions so documentation, YAML workflows, and unrelated text files do not create obvious false positives.

## Coverage and edit limits

The two GraphQL field rules inspect executable queries/fragments in standalone
`.graphql` and `.gql` files. They do not inspect those fields inside JavaScript,
TypeScript, or Ruby strings. Schema declarations and GraphQL comments/string
values are not executable field selections.

GraphQL edits use parsed source ranges and preserve surrounding text. Unsafe
occurrences stay manual: aliases, removed variable/fragment references, empty
selections, malformed documents, or unsupported price-rule response data. The
price-rule fix replaces the entire supported nested selection. ScriptTag results
are candidates for manual review; read/delete operations and test/fixture paths
are excluded from that rule. Dynamic calls or other languages may be missed.

Parsing verifies GraphQL syntax only. It does not establish the target API
version, validate a live Shopify schema, or update application code that consumes
the changed response shape. Review those consumers and run application tests.

The local audit is documented in `docs/AUDIT_2026-10-23.md`.

## Quick install for testers

BreakGuard is not published to PyPI yet. Install the current product branch directly from GitHub:

```bash
python -m pip install "git+https://github.com/viceprimarleova-sketch/breakguard-test.git@breakguard/product-v0.1"
breakguard --version
breakguard --help
```

For a complete safe-testing walkthrough, see `TESTER_GUIDE.md`. Release-candidate status is tracked in `RELEASE_CANDIDATE.md`.

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
