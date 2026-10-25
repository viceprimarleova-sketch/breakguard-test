# Pilot commercial terms and data notice — working draft

**Not an approved contract or legal opinion. Complete and review before use.**

## Information still required before live sales

- Complete legal seller name, lawful establishment, postal contact, support
  email and applicable registration/tax details in the private order record.
  Seller registration and the business activity classification are **not yet
  verified**. This repository template intentionally contains no personal
  seller or customer record.
- Intended customer type and location, applicable contractual/tax treatment,
  invoice details, approved customer total and payment account eligibility:
  **not verified**.
- Approved license duration, delivery date, support availability, refund terms,
  data retention/deletion contacts and governing terms: **Founder decision pending**.

An existing personal payment account or citizenship document alone does not
resolve those facts. Do not complete them using assumptions or activate sales
first. The proposed first offer is for a professional/business customer; verify
that status and jurisdiction rather than applying this draft to consumers.

For a seller operating in Moldova, confirm the actual activity and legal route.
The official independent-entrepreneur guidance distinguishes eligible services
from product sales. A software license plus support cannot simply be relabeled
as consulting to assume eligibility. This draft does not determine registration
or tax treatment: https://freelance.mded.gov.md/.

## Proposed GBP total, delivery and support

Proposed one-time customer total: GBP 42.00, subject to the actual tax review
and a complete accepted order. No subscription or automatic renewal is included.
The invoice currency is GBP; exchange rates and conversion charges are set by
the payment provider/card issuer. No fixed EUR equivalent is promised.

Set a written delivery deadline in the order, proposed within two business days
after the agreed start conditions and verified payment. The seller must approve
that deadline before sending the offer. Deliver the agreed pinned build, its
checksum, examples and instructions through access limited to the actual buyer.
No private project transfer is required.

Proposed support: up to two asynchronous email exchanges during seven calendar
days from the explicit agreed start date. One exchange means one customer
question/report and one response, with a clarification if needed to understand
that issue. Scope: installation, supported CLI behavior, interpreting redacted
findings and restore instructions. No round-the-clock response, new rule,
private-code review, store work or general migration service is promised.

## Proposed limited pilot

The offer would identify one customer, repository, build, three supported rule
families, environment and agreed period. Proposed grant: use the delivered build
locally for the one agreed repository, with no automatic expiry of that pinned
build and with the customer's own right to inspect its source repository.
Redistribution/resale, later maintenance, new rules and subscriptions are not
included unless separately agreed. This proposed grant is subject to ownership
and final license review and is not in force. It does not restrict separate
rights granted by dependencies or charge for an already free evaluation kit.

The seller would deliver the package and instructions on an agreed date and
provide the support explicitly accepted in the offer. The developer reviews
every proposed change, confirms its API/version and response consumers, and runs
application tests before any integration or deployment. No automatic merge,
store API access or production deployment is part of the pilot.

Findings are limited source candidates. Syntax checks do not validate a live
Shopify schema or guarantee runtime behavior. The proposal contains no promise
to eliminate all deprecations, remove dashboard warnings or prevent disruption.
Final warranties, responsibilities and any limitations need jurisdiction-specific
review; this draft does not waive mandatory customer rights.

Proposed discretionary refund: the full GBP 42.00 on request within seven
calendar days from the agreed start, or if the agreed delivery deadline cannot
be met. Proposed seller action: initiate an approved refund against the original
provider transaction within five business days of the request. Actual bank or
provider posting time is not guaranteed. Currency conversion can change the
equivalent in the buyer's funding currency; do not promise a fixed EUR refund.
This is a commercial proposal, not a statement of a statutory deadline.

The policy needs the Founder's explicit approval and a verified way to perform
it in the actual account. No automatic refund, payout or expense is authorized
by this document. Keep a private acceptance/delivery/payment/refund record and
preserve applicable customer/provider rights. Match `PILOT_OFFER_DRAFT.md`.

## Factual data notice for this candidate

- Main scanner/preview/apply/restore commands run locally and have no network
  calls, telemetry or login. Source stays on the developer's machine.
- Backups under `.breakguard/backups` contain original changed source and the
  local absolute repository path. They are ignored by Git and excluded from
  scans; the developer controls their retention. They are not encrypted storage.
- Optional JSON reports contain relative file paths, rule IDs, findings,
  coverage, hashes of the rule set and operation metadata, without source
  snippets. File paths themselves may be sensitive. Sharing is voluntary and
  should be redacted; we do not ask for source files or backups.
- The separate opt-in GitHub helper sends branch/PR data to GitHub when an
  operator explicitly runs it with a token. The scanner never runs it on its own.
- The separate Sandbox module connects only to PayPal Sandbox when explicitly
  selected. Its credentials remain in environment variables and memory. CLI
  output retains order/capture IDs and test totals, not payer details or secrets.
  Offline simulation never contacts PayPal and receives no money.
- Before any real checkout, the seller must supply its actual privacy notice,
  processing purposes, contact/retention details and provider disclosures. This
  candidate has no real checkout, production payment storage or live fulfillment.

## IP and dependencies

The project metadata currently says Proprietary. Final license text and ownership
review remain pending. The kit includes the dependency wheel and license notice
for graphql-core; its permissions are separate from BreakGuard's proposed terms.
Do not include third-party public project source in a customer kit without its
license/notice review; this kit uses synthetic examples instead.

## Provider references checked October 25–26, 2026

- PayPal Sandbox: https://developer.paypal.com/sandbox-testing/overview
- PayPal legal agreements: https://www.paypal.com/legalhub
- https://developer.paypal.com/payment-links-buttons/overview
- https://www.paypal.com/md/cshelp/article/how-do-i-get-a-refund-help100
- https://www.paypal.com/md/cshelp/article/where-is-my-refund-help130
- https://freelance.mded.gov.md/

Select the agreement actually applicable to the eventual merchant account; a
GBP balance or Romanian citizenship does not establish that account's country.

Selecting PayPal Sandbox is a technical test choice, not confirmation that a
particular live account or legal seller can accept these payments.
