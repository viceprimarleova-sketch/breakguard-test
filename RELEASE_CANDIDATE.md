# BreakGuard V0.1 release checklist

Candidate: **0.1.0rc2**, staged locally on `work/pilot-readiness-v0.1` above the
reviewed rc1 fixes. The product branch is not integrated. No automatic merge is
permitted in V0.1. See `docs/PILOT_READINESS.md` for distinct release/market gates.

## Implemented

- [x] installable CLI with packaged rules, version and help
- [x] local scan, machine-readable findings, coverage/limits report
- [x] standalone GraphQL preview and guarded edits
- [x] static embedded GraphQL detection with manual-only results
- [x] ScriptTag source-pattern review in JS/TS, Ruby and GraphQL
- [x] missing-path/error exit codes and JSON output consistency
- [x] symlink/out-of-root protection and transactional local edit snapshots
- [x] conflict/integrity-aware restore
- [x] non-overwriting review-branch creation in the opt-in GitHub helper
- [x] synthetic installed-package workflow and public-repository scan protocol
- [x] pilot offer, price hypothesis, draft commercial/data terms and feedback form
- [x] offline payment simulation and Sandbox-only adapter; no live mode

## Evidence still required for this candidate

- [ ] hosted Python 3.10/3.11/3.12 and Windows/macOS/Linux checks on the exact rc2
  review commit, after approval to publish that branch
- [ ] independent Shopify developer validation on representative supported code,
  including proposed edits, response consumers and the application's own tests
- [ ] actual PayPal Sandbox create/approve/capture/cancel/retry evidence after
  owner-controlled secure configuration
- [ ] Founder review/integration approval and final version/distribution choice
- [ ] approved seller/customer terms, support, total/tax treatment and legal review
- [ ] approved live payment/fulfillment implementation before charging

## Historical evidence

The rc1 correction commit `788c3b6e3f805a0d39e0593d08bef9fcf7ca6eba` passed
39 local tests and hosted Python 3.10–3.12 / Ubuntu / macOS / Windows checks.
Those hosted results do not validate rc2. PR #6 remains Draft and unmerged:
https://github.com/viceprimarleova-sketch/breakguard-test/pull/6

Oleg supplied a Windows screenshot on October 23 showing two changed files and
one remaining manual finding. It does not establish the installed source SHA,
all installation steps or Shopify developer usefulness.
