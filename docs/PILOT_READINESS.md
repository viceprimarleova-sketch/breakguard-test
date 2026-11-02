# Pilot readiness — October 31, 2026

## Verified candidate

Version `0.1.0rc2` is integrated for controlled testing at product source
`b65f1125abb43f05cca659f7e645dff397901518` (PR #10). The earlier runtime-only
source `a711aad687018cc25b8a5919a30c25d1c2929824` passed 88 tests. PR #10 added
12 delivery regression tests; the recorded local suite total is 100. The
integrated source also passed the following hosted workflow jobs:

- Python 3.10/3.11/3.12:
  https://github.com/viceprimarleova-sketch/breakguard-test/actions/runs/40303103298
- Ubuntu/macOS/Windows installed workflow:
  https://github.com/viceprimarleova-sketch/breakguard-test/actions/runs/40303103299

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
| Evaluation packaging | PR #10 integrated the builder, verifier and technical-only evaluation kit; hosted external-install workflow passed on Ubuntu/macOS/Windows | Build a fresh artifact from the exact integrated commit, record identity/hashes, then independently inspect/install that ZIP before distribution |
| Representative sources | Official Ruby/React Router controls and two public applications scanned read-only; no application execution | Developer checks relevance, response consumers and application tests |
| Customer usefulness | Not independently validated | Complete `TESTER_GUIDE.md` with a consenting Shopify developer |
| Buyer fit | Not established from migration-task titles | Confirm an actual useful supported case using `PILOT_ELIGIBILITY.md` |
| Price | GBP 42 current proposal, not commercially validated | Match the invoice currency; do not promise a fixed EUR 49 equivalent |
| PayPal Sandbox | Fake-transport/offline tests pass; no actual account transaction | Owner configures app/buyer securely, then execute the actual test plan |
| Commercial terms | Working draft; seller/account/tax facts unresolved | Complete seller details and obtain approval of total, support and final terms |
| Live API payments | No live adapter or automatic fulfillment | Keep separate from owner-created provider invoices; approve any production integration |
| First manual paid pilot | Proposed individual invoice after fit, seller review and accepted terms | Follow `PAID_PILOT_RUNBOOK.md`; no reusable invoice button or unapproved charge |
| Revenue | No documented payment | Record only a verified real customer payment |

## Integrated GBP quote and delivery

PR #9 integrated the GBP 42 Sandbox test quote and regressions for old EUR 49
orders/captures. PR #10 subsequently integrated the reproducible builder,
verifier and technical-only evaluation-kit workflow into product source
b65f1125abb43f05cca659f7e645dff397901518. The earlier
work/evaluation-delivery-2026-10-26 branch is no longer awaiting integration;
its changes are part of PR #10. The package is still a technical candidate, not
a published final release. Older dated audits retain EUR 49 as history, not a
current quote or an exchange-rate guarantee.
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


## Current evidence boundary (October 31)

The hosted workflow run IDs above are recorded as successful in GitHub Actions.
The workflow artifact listing for run `40303103299` returned no downloadable
artifact. Therefore no fresh ZIP has yet been downloaded, hashed or manually
installed by this review. The previous free kit remains untouched. No Shopify
developer has completed the independent usefulness protocol; paid fit, willingness
to pay, seller eligibility, tax treatment and a real payment remain unverified.


## Status update — November 2, 2026

The hosted evidence was inspected beyond the job-level success badges. On the
integrated product commit b65f1125abb43f05cca659f7e645dff397901518:

- CI run [40303103298](https://github.com/viceprimarleova-sketch/breakguard-test/actions/runs/40303103298)
  reports **100 tests passed** on each Python 3.10, 3.11 and 3.12 matrix job.
- External-install run [40303103299](https://github.com/viceprimarleova-sketch/breakguard-test/actions/runs/40303103299)
  completed all steps on Ubuntu, macOS and Windows. Each runner built and
  extracted an offline evaluation ZIP, installed the included wheels, matched
  all 12 runtime hashes, passed the synthetic workflow with exact restore,
  preserved four manual findings and disclosed one skipped dynamic document.

The three runners recorded different wheel and archive SHA-256 values for the
same source commit (wheel prefixes: 71bb99bb122d, 2894d0e35792,
ebeeaa198a24; ZIP prefixes: c00bb2ebfcfe, 5b4914435179,
2e24e12ae79b). The runtime files matched on every OS and all jobs passed,
but the cross-runner byte-level variance has not been explained. If a single
canonical release artifact is intended, build it once in a pinned environment
and test that exact ZIP on all three OSes rather than independently building
one ZIP per runner.

The Actions artifact listing for run 40303103299 is empty. These hosted checks
therefore prove successful ephemeral runner-built offline installation, not that
a fresh ZIP was downloaded, retained, manually inspected or installed on the
Founder's physical Windows computer. PR #10 records a prior Linux candidate hash,
but that archive was not retrieved and reverified in this reporting run.

Sandu's October 28 synthetic Windows demonstration is documented separately in
EXTERNAL_EVALUATION_SANDU_2026-10-28.md. He is not a Shopify specialist and
his feedback does not establish real-project usefulness or commercial demand.
The current documentation review branch contains the evidence note and
PowerShell quick-start corrections; it is not merged and no CI result has been
claimed for those documentation-only commits.

No specialist developer response, validated buyer fit, actual PayPal Sandbox
transaction, approved final terms, live payment, revenue, new outreach or
commercial commitment is recorded as of this update. Draft test PRs #1–#5 remain
open and unmerged; no cleanup action has been taken.