# BreakGuard V0.1

BreakGuard scans a code repository for known Shopify API deprecations, points to the affected file and line, provides the official source and remediation, and applies conservative fixes for rules that are safe enough to automate.

## Current V0.1 rules

- Customer.lastIncompleteCheckout
- DraftOrderDiscountNotAppliedWarning.priceRule
- ScriptTag usage (manual review only)

## Run

```bash
python -m breakguard.cli /path/to/repo
python -m breakguard.cli /path/to/repo --apply-fixes
python -m pytest -q
```

The scanner returns non-zero while findings remain, which makes it suitable for CI once the repository has tests/workflows configured.
