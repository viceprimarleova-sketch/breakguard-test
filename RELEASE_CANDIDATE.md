# BreakGuard V0.1 release checklist

Candidate: **0.1.0rc2**, integrated into `breakguard/product-v0.1` via PR #6 with
the Founder's explicit approval. Merge commit:
`f0976e2125dfd12c6aae9c680e2696ca17c328bf`.
This remains a controlled testing candidate. Unattended merge stays disabled.
See `docs/PILOT_READINESS.md` for distinct release/market gates.

The response-name follow-up for some `priceRule` edits is tracked in PR #7:
https://github.com/viceprimarleova-sketch/breakguard-test/pull/7
The dated `docs/GRAPHQL_RESPONSE_REVIEW_2026-10-25.md` records evidence captured
before publication; use the PR for current hosted checks and integration state.
The earlier delivery kit at product commit
`2a56d555931b436551e84b3b8b32803c9c064094` did not contain this correction.

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

## Verified technical and integration gates

- [x] 77 tests against a separately installed wheel with isolated imports
- [x] reviewed head `b111a9ed2d6f92c88d35c2c40f61ae632368443f` passed hosted
  Python 3.10/3.11/3.12 and Windows/macOS/Linux installed workflow checks
- [x] Founder approved PR #6 integration for controlled testing

Current product-branch checks are recorded in GitHub Actions. Historical audit
files preserve their preparation-time status rather than claiming later runs.

## Before final 0.1.0 or commercial launch

- [ ] independent Shopify developer validation on representative supported code,
  including proposed edits, response consumers and the application's own tests
- [ ] actual PayPal Sandbox create/approve/capture/cancel/retry evidence after
  owner-controlled secure configuration
- [ ] Founder approval of final 0.1.0 release and distribution choice
- [ ] approved seller/customer terms, support, total/tax treatment and legal review
- [ ] approved live payment/fulfillment implementation before charging

## Historical evidence

The rc1 correction commit `788c3b6e3f805a0d39e0593d08bef9fcf7ca6eba` passed
39 local tests and hosted Python 3.10–3.12 / Ubuntu / macOS / Windows checks.
Those historical hosted results alone did not validate rc2. At that point,
PR #6 was Draft and unmerged; it was subsequently approved and integrated:
https://github.com/viceprimarleova-sketch/breakguard-test/pull/6

Oleg supplied a Windows screenshot on October 23 showing two changed files and
one remaining manual finding. It does not establish the installed source SHA,
all installation steps or Shopify developer usefulness.
