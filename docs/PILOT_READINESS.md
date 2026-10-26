# Pilot readiness — October 26, 2026

## Verified candidate

Version `0.1.0rc2` is integrated for controlled testing at product source
`a711aad687018cc25b8a5919a30c25d1c2929824`, following the Founder's approval of
PR #9. That exact merged source passed 88 tests and six hosted checks:

- Python 3.10/3.11/3.12:
  https://github.com/viceprimarleova-sketch/breakguard-test/actions/runs/40244402264
- Ubuntu/macOS/Windows installed workflow:
  https://github.com/viceprimarleova-sketch/breakguard-test/actions/runs/40244402224

The previously delivered free evaluation remains pinned to earlier source
`461558f3d7bc8db06fe89a6137b278163a1ec7c5` (85 tests). Its wheel SHA-256 is
`892c653d9e2d3fc9fdb4eab6a853c8e17befae3c764d4ae92044697920d68628`.
That frozen kit passed offline scan, preview, two guarded edits, rescan, exact
restore and later-edit protection on synthetic files. Four manual cases stayed
unchanged. It does not silently acquire later changes. New delivery builds must
record their own source and wheel hashes using `EVALUATION_PACKAGING.md`.
These are technical checks, not independent customer acceptance.

This is not a final 0.1.0 release or commercial launch. The private synthetic web
demonstration remains separate. See `PUBLIC_SOURCE_VALIDATION_2026-10-25.md` for
current source evidence and `PILOT_ELIGIBILITY.md` for the proposed selection step.

## Delivered or prepared

- Source locations, official guidance and coverage counts for three rule families.
- Scan → preview → apply → rescan/report → conflict-aware restore.
- Installable wheels, offline installers, synthetic/manual/coverage examples,
  English/Romanian instructions and a 30–60 minute developer test protocol.
- A technical-only external evaluation kit separated from private seller intake.
- Current GBP 42 one-repository offer proposal, bounded support and draft terms.
- A manual individual-invoice delivery runbook and an unfilled order template.
- The functional free evaluation remains separate from a paid assisted pilot.
- Offline payment simulation plus a Sandbox-only adapter and actual-test plan.

## Separate gates

| Gate | State | Next evidence/action |
| --- | --- | --- |
| Candidate functionality | Integrated a711aad source passed 88 tests and six hosted checks | Keep the source/wheel pin; block release for unsafe edits or false success |
| Evaluation packaging | Reproducible builder and actual-installer protocol prepared on a separate local review branch | Review the new changes, then run hosted checks before integration/distribution |
| Representative sources | Official Ruby/React Router controls and two public applications scanned read-only; no application execution | Developer checks relevance, response consumers and application tests |
| Customer usefulness | Not independently validated | Complete `TESTER_GUIDE.md` with a consenting Shopify developer |
| Buyer fit | Not established from migration-task titles | Confirm an actual useful supported case using `PILOT_ELIGIBILITY.md` |
| Price | GBP 42 current proposal, not commercially validated | Match the invoice currency; do not promise a fixed EUR 49 equivalent |
| PayPal Sandbox | Fake-transport/offline tests pass; no actual account transaction | Owner configures app/buyer securely, then execute the actual test plan |
| Commercial terms | Working draft; seller/account/tax facts unresolved | Complete seller details and obtain approval of total, support and final terms |
| Live API payments | No live adapter or automatic fulfillment | Keep separate from owner-created provider invoices; approve any production integration |
| First manual paid pilot | Proposed individual invoice after fit, seller review and accepted terms | Follow `PAID_PILOT_RUNBOOK.md`; no reusable invoice button or unapproved charge |
| Revenue | No documented payment | Record only a verified real customer payment |

## Integrated GBP quote and separate delivery review

PR #9 integrated the GBP 42 Sandbox test quote and regressions for old EUR 49
orders/captures. `GBP42_REVIEW_2026-10-26.md` is the earlier preparation snapshot;
the exact integrated source and final hosted runs are recorded above. The
separate `work/evaluation-delivery-2026-10-26` branch prepares reproducible,
technical-only packaging, delivery verification and updated tester instructions.
It requires its own review, hosted checks and approval before integration.
Older dated audits and the contact history below retain the earlier EUR 49
proposal as history, not a current quote or an exchange-rate guarantee.

## Contact evidence

On October 25 the Founder approved one individual email requesting free technical
feedback and asking about possible interest in a EUR 49 pilot. Gmail confirmed it
was sent without attachments. No incoming response from that address was found
in the subsequent check for this update. Sending, receiving, reading, developer
acceptance and payment are separate outcomes; only sending is confirmed.

Shopify forum invitations remain paused following the supplied account-hold
notice. The earlier Reddit introduction was blocked and was not sent. No new
outreach, follow-up, publication or payment is authorized by this evidence update.

## Next validation session

One consenting Shopify developer spends 30–60 minutes on a disposable local/public
project. Independently confirm relevant/missed/irrelevant findings, actual API
surface and version, preview/diff, application tests and restore. Record the
developer's own judgment about usefulness before price. If the actual migration
is outside the three rules, retain the person as an expert feedback candidate;
do not present the narrow checker as a general Hydrogen migration service.

Any scope expansion should be justified by concrete developer evidence. A zero
finding is a control within disclosed coverage, not a compatibility certificate.
