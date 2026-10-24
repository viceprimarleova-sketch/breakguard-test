# Pilot commercial terms and data notice — working draft

**Not an approved contract or legal opinion. Complete and review before use.**

## Information still required before live sales

- Legal seller name, establishment/country, postal contact, support email and
  any applicable registration/tax details: **not supplied**.
- Intended customer type and location, applicable contractual/tax treatment,
  invoice details, approved customer total and payment account eligibility:
  **not verified**.
- Approved license duration, delivery date, support availability, refund terms,
  data retention/deletion contacts and governing terms: **Founder decision pending**.

Romanian citizenship/documents or an existing PayPal account alone do not resolve
these facts. Do not complete them using assumptions or activate payments first.

## Proposed limited pilot

The offer would identify one customer, repository, build, three supported rule
families, environment and agreed period. Proposed grant: use the delivered build
locally for that pilot, with the customer's own right to inspect its source
repository. Redistribution/resale, later maintenance, new rules and subscriptions
are not included unless separately agreed. This proposed license is not in force.

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

Proposed correction/refund handling must match the approved offer, provider
rules and applicable rights. Keep an acceptance/delivery/payment record. Do not
represent an unapproved refund window as a legal deadline.

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

## Provider references checked October 25, 2026

- PayPal Sandbox: https://developer.paypal.com/sandbox-testing/overview
- PayPal legal agreements: https://www.paypal.com/legalhub
- Romanian-resident PayPal agreement, only if applicable to the eventual account:
  https://www.paypal.com/ro/legalhub/paypal/useragreement-full

Selecting PayPal Sandbox is a technical test choice, not confirmation that a
particular live account or legal seller can accept these payments.
