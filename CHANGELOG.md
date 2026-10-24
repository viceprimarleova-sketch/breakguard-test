# Changelog

All notable changes to BreakGuard are recorded here.

## 0.1.0rc2 — Pilot review candidate, not yet integrated or published

### Follow-up prepared for review

- Protect each new backup snapshot with its own ignore file, preserving a
  project's existing `.breakguard/.gitignore`. Regression tests reproduce the
  old behavior where originals and manifests appeared in ordinary Git add
  candidates. This does not remove already tracked files or alter older backups.

- Detect supported GraphQL fields in recognized static JS/TS templates and Ruby
  heredocs, with physical source lines and manual-only findings.
- Report coverage, skipped documents, explicit limits and a rule fingerprint.
- Fail with exit 2 on missing/invalid repositories and operational errors; keep
  `--json --apply-fixes` machine-readable.
- Exclude symlinks/out-of-root sources and validate edit paths.
- Snapshot originals before edits, use atomic file replacement and support
  integrity-checked restore that refuses subsequent source edits.
- Preserve existing local review branches and validate GitHub access before
  making branch changes; remove force-push from the optional PR helper.
- Add installed-package smoke checks for preview/apply/restore/conflicts.
- Prepare an operator-only PayPal Sandbox adapter and an explicitly offline fake
  checkout demonstration. No live payment, fulfillment or actual Sandbox
  transaction has been enabled or claimed.
- Add bounded pilot offer, price hypothesis, draft terms and a 30–60 minute
  Shopify developer validation protocol.

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
