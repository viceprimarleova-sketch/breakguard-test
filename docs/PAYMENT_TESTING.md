# Pilot payments — test mode only

This module has no live mode, real-money receipt, automatic license activation,
subscription or public checkout. It is an operator tool, separate from the local
source scanner and from any invoice the account owner creates in PayPal itself.
Its fixed test quote is GBP 42.00; it does not perform a EUR/GBP conversion.
The proposed commercial offer still requires separate approval.

## Offline demonstration — ready without an account

```sh
python -m breakguard.pilot_payments --simulate
```

This uses an in-memory fake provider. It exercises create → approve → capture,
repeated capture without a second capture request, and a cancelled-order refusal.
Output is explicitly `OFFLINE_SIMULATION`; a simulated completion is not a PayPal
Sandbox transaction. No network request, credential or money is involved.

## PayPal Sandbox adapter — prepared, not yet tested with an account

An actual Sandbox test needs an owner-controlled developer application, Sandbox
merchant and buyer, and HTTPS return/cancel URLs. The current environment has no
configured Sandbox application access. No account has been probed or activated.
The owner configures `PAYPAL_SANDBOX_CLIENT_ID` and
`PAYPAL_SANDBOX_CLIENT_SECRET` locally through an approved secure environment;
never send a password, API secret or access token through chat.

From that configured environment, substitute actual test URLs and persistent
request identifiers (the following placeholders are not an operational checkout):

```sh
python -m breakguard.pilot_payments --sandbox-create --request-id CREATE_REQUEST_ID --return-url https://YOUR-TEST-HOST/return --cancel-url https://YOUR-TEST-HOST/cancel
# Open the returned sandbox approval URL and approve using a Sandbox buyer.
python -m breakguard.pilot_payments --sandbox-capture ORDER_ID --request-id CAPTURE_REQUEST_ID
```

Preserve and reuse the same request ID when retrying the same operation after an
unclear result; use a different persistent ID for creation and capture. Do not
assume a timeout means no capture happened. A browser return URL or screenshot
does not confirm payment. This CLI verifies the provider's order and capture.

All requests are fixed to `api-m.sandbox.paypal.com`; redirects are refused.
Only sandbox approval links are accepted. Amount/currency and the pilot ID are
server-defined, and checked again before/after capture. Created, cancelled,
pending, declined or mismatched orders cannot return confirmed completion.
Repeated completed capture checks use the already completed result. Provider
errors do not echo response bodies, tokens or secrets. There is no fulfillment
even after a successful Sandbox capture.

## Remaining acceptance test with owner access

1. Create a Sandbox order for the GBP 42.00 test total.
2. Cancel one test and confirm no completed receipt is produced.
3. Approve another using a Sandbox buyer and verify a completed capture by API.
4. Retry using the saved request identifiers and confirm no duplicate capture.
5. Exercise a declined/pending scenario and capture an uncertain timeout/retry
   outcome using Sandbox-supported facilities; record actual results separately
   from the fake-transport unit tests.

The three GBP quote regression tests independently check the exact test total,
refusal of the former EUR 49 order before capture, and rejection of a capture
using that old total. Orders created for the old quote do not match the current
one. Create a new order and new persistent request IDs for a new quote; reusing
a request ID is only for retrying the same unchanged operation.

A provider-hosted invoice for one agreed customer is a separate, proposed manual
route. Follow `PAID_PILOT_RUNBOOK.md`; this module does not create that invoice,
verify a live payment, reconcile its refund or deliver a customer package. Do not
use a single invoice as a reusable website checkout.

An automated live API release would additionally need the approved seller/offer/tax and account
setup, a real buyer-facing application, authenticated server-side order records,
provider callbacks/reconciliation, fulfillment/refund/dispute handling and the
Founder's explicit approval. Those production features are intentionally not
activated or claimed by this Sandbox preparation.

## Primary sources checked October 25–26, 2026

- https://developer.paypal.com/sandbox-testing/overview
- https://developer.paypal.com/api/orders/v2/orders-create
- https://developer.paypal.com/api/orders/v2/orders-get
- https://developer.paypal.com/api/orders/v2/orders-capture
- https://developer.paypal.com/api/rest/reference/idempotency/
- https://developer.paypal.com/api/codes/currency
- https://developer.paypal.com/payment-links-buttons/overview
