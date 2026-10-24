# Pilot payments — test mode only

There is no live mode, real-money receipt, automatic license activation,
subscription or public checkout. This module is an operator tool, separate from
the local source scanner. The proposed fee is test data until approved.

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

1. Create a Sandbox order for the EUR 49.00 test total.
2. Cancel one test and confirm no completed receipt is produced.
3. Approve another using a Sandbox buyer and verify a completed capture by API.
4. Retry using the saved request identifiers and confirm no duplicate capture.
5. Exercise a declined/pending scenario and capture an uncertain timeout/retry
   outcome using Sandbox-supported facilities; record actual results separately
   from the fake-transport unit tests.

Live release would additionally need the approved seller/offer/tax and account
setup, a real buyer-facing application, authenticated server-side order records,
provider callbacks/reconciliation, fulfillment/refund/dispute handling and the
Founder's explicit approval. Those production features are intentionally not
activated or claimed by this Sandbox preparation.

## Primary sources checked October 25, 2026

- https://developer.paypal.com/sandbox-testing/overview
- https://developer.paypal.com/api/orders/v2/orders-create
- https://developer.paypal.com/api/orders/v2/orders-get
- https://developer.paypal.com/api/orders/v2/orders-capture
- https://developer.paypal.com/api/rest/reference/idempotency/
