# Changelog

All notable changes to BreakGuard are recorded here.

## 0.1.0rc1 — Release candidate

This release candidate is intended for controlled external testing.

### Added
- installable `breakguard` CLI;
- packaged Shopify rule database;
- scan output with file, line, severity, remediation, and source;
- JSON output;
- non-destructive `--fix-preview`;
- conservative `--apply-fixes`;
- GitHub Draft PR automation;
- external install smoke tests on Ubuntu, macOS, and Windows;
- CI on Python 3.10, 3.11, and 3.12;
- clean-worktree, verification, and Git diff safety guards.

### Supported Shopify rules
- Customer Account API `Customer.lastIncompleteCheckout`;
- Admin GraphQL `DraftOrderDiscountNotAppliedWarning.priceRule`;
- legacy `ScriptTag` usage as manual-review only.

### Safety
BreakGuard V0.1 is pre-release software. Generated changes must be reviewed before merge or deployment.
