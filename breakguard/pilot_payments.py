"""Operator-only PayPal SANDBOX preparation. No live mode or fulfillment."""
from __future__ import annotations

import argparse
import base64
import copy
import json
import os
import re
import sys
from urllib import error, request
from urllib.parse import urlparse

SANDBOX_API = "https://api-m.sandbox.paypal.com"
OFFER_ID = "breakguard-v01-pilot-draft"
AMOUNT = {"currency_code": "EUR", "value": "49.00"}


class PaymentError(ValueError):
    pass


class NoRedirects(request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


def _transport(req):
    try:
        with request.build_opener(NoRedirects()).open(req, timeout=20) as response:
            return json.loads(response.read().decode("utf-8"))
    except error.HTTPError as exc:
        raise PaymentError(f"PayPal sandbox HTTP {exc.code}; no payment confirmed. Check status and reuse the same request ID for a retry.") from None
    except (error.URLError, OSError, ValueError):
        raise PaymentError("Sandbox response unavailable; payment status is unknown. Check order status before retrying.") from None


def _request_id(value):
    if not re.fullmatch(r"[A-Za-z0-9_-]{1,38}", value):
        raise PaymentError("Use a persistent request ID of 1-38 letters, digits, hyphens or underscores.")
    return value


def _order_id(value):
    if not re.fullmatch(r"[A-Za-z0-9]{6,32}", value):
        raise PaymentError("Invalid sandbox order identifier.")
    return value


def _https_url(value):
    parsed = urlparse(value)
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password or parsed.fragment:
        raise PaymentError("Use an HTTPS return/cancel URL without credentials or a fragment.")
    return value


class SandboxCheckout:
    def __init__(self, client_id, secret, transport=None):
        if not client_id or not secret:
            raise PaymentError("Sandbox application access is missing. Configure PAYPAL_SANDBOX_CLIENT_ID and PAYPAL_SANDBOX_CLIENT_SECRET locally; never paste secrets into chat.")
        self._credentials = base64.b64encode(f"{client_id}:{secret}".encode()).decode()
        self._transport = transport or _transport
        self._token = None

    def _call(self, method, path, payload=None, request_id=None):
        if not self._token:
            response = self._transport(request.Request(
                SANDBOX_API + "/v1/oauth2/token", data=b"grant_type=client_credentials",
                headers={"Authorization": "Basic " + self._credentials,
                         "Content-Type": "application/x-www-form-urlencoded"}, method="POST"))
            if not isinstance(response, dict):
                raise PaymentError("Invalid sandbox authentication response.")
            self._token = response.get("access_token")
            if not isinstance(self._token, str) or not self._token:
                raise PaymentError("Sandbox authentication failed.")
        headers = {"Authorization": "Bearer " + self._token, "Content-Type": "application/json",
                   "Accept": "application/json", "Prefer": "return=representation"}
        if request_id:
            headers["PayPal-Request-Id"] = _request_id(request_id)
        data = None if payload is None else json.dumps(payload).encode()
        result = self._transport(request.Request(SANDBOX_API + path, data=data, headers=headers, method=method))
        if not isinstance(result, dict):
            raise PaymentError("Invalid sandbox response; no payment confirmed.")
        return result

    def create(self, request_id, return_url, cancel_url):
        _request_id(request_id)
        payload = {"intent": "CAPTURE", "purchase_units": [{"reference_id": "pilot", "custom_id": OFFER_ID,
                    "description": "BreakGuard V0.1 pilot — sandbox draft, no fulfillment", "amount": AMOUNT.copy()}],
                   "payment_source": {"paypal": {"experience_context": {
                       "shipping_preference": "NO_SHIPPING", "user_action": "PAY_NOW",
                       "return_url": _https_url(return_url), "cancel_url": _https_url(cancel_url)}}}}
        result = self._call("POST", "/v2/checkout/orders", payload, request_id)
        identifier = _order_id(result.get("id", ""))
        approval = next((link.get("href") for link in result.get("links", [])
                         if link.get("rel") in {"approve", "payer-action"}), None)
        parsed = urlparse(approval or "")
        if parsed.scheme != "https" or parsed.hostname != "www.sandbox.paypal.com" or parsed.username or parsed.password:
            raise PaymentError("Missing or non-sandbox approval link; order is not confirmed paid.")
        return {"mode": "paypal_sandbox", "order_id": identifier, "approval_url": approval,
                "payment_confirmed": False, "fulfillment_enabled": False}

    @staticmethod
    def _validate_order(order, order_id):
        units = order.get("purchase_units", [])
        if (order.get("id") != order_id or order.get("intent") != "CAPTURE" or len(units) != 1
                or units[0].get("custom_id") != OFFER_ID or units[0].get("amount") != AMOUNT):
            raise PaymentError("Order does not match the proposed pilot, amount or currency.")
        return units[0]

    def capture(self, order_id, request_id):
        order_id = _order_id(order_id)
        _request_id(request_id)
        path = "/v2/checkout/orders/" + order_id
        order = self._call("GET", path)
        self._validate_order(order, order_id)
        if order.get("status") == "APPROVED":
            self._call("POST", path + "/capture", {}, request_id)
            order = self._call("GET", path)
        unit = self._validate_order(order, order_id)
        captures = unit.get("payments", {}).get("captures", [])
        if (order.get("status") != "COMPLETED" or len(captures) != 1
                or captures[0].get("status") != "COMPLETED" or captures[0].get("amount") != AMOUNT
                or not captures[0].get("id")):
            raise PaymentError("Sandbox capture is not completed and verified; no payment confirmed.")
        return {"mode": "paypal_sandbox", "order_id": order_id, "capture_id": captures[0]["id"],
                "amount": AMOUNT.copy(), "sandbox_payment_confirmed": True,
                "real_money_received": False, "fulfillment_enabled": False}


class DemoTransport:
    """In-memory fake provider, exclusively for explicit offline demonstrations."""
    def __init__(self):
        self.order = None
        self.capture_requests = 0
        self.create_request_id = None

    def __call__(self, req):
        path = urlparse(req.full_url).path
        if path == "/v1/oauth2/token":
            return {"access_token": "offline-demo-token"}
        if path == "/v2/checkout/orders":
            request_id = req.get_header("Paypal-request-id")
            if self.order and request_id == self.create_request_id:
                return copy.deepcopy(self.order)
            self.create_request_id = request_id
            self.order = json.loads(req.data)
            self.order.update({"id": "DEMOORDER001", "status": "CREATED", "links": [
                {"rel": "approve", "href": "https://www.sandbox.paypal.com/checkoutnow?token=DEMOORDER001"}]})
        elif path.endswith("/capture"):
            if self.order["status"] != "APPROVED":
                raise PaymentError("Demo order is not approved.")
            self.capture_requests += 1
            self.order["status"] = "COMPLETED"
            self.order["purchase_units"][0]["payments"] = {"captures": [
                {"id": "DEMOCAPTURE001", "status": "COMPLETED", "amount": AMOUNT.copy()}]}
        return copy.deepcopy(self.order)


def simulate_checkout():
    provider = DemoTransport()
    client = SandboxCheckout("offline-demo", "offline-demo", provider)
    created = client.create("demo-create", "https://example.com/return", "https://example.com/cancel")
    provider.order["status"] = "APPROVED"
    receipt = client.capture(created["order_id"], "demo-capture")
    replay = client.capture(created["order_id"], "demo-capture")
    cancelled = DemoTransport()
    cancelled_client = SandboxCheckout("offline-demo", "offline-demo", cancelled)
    cancelled_client.create("demo-cancel", "https://example.com/return", "https://example.com/cancel")
    cancelled.order["status"] = "CANCELLED"
    try:
        cancelled_client.capture("DEMOORDER001", "demo-cancel-capture")
    except PaymentError:
        cancellation_blocked = True
    else:
        cancellation_blocked = False
    same_result = receipt == replay and provider.capture_requests == 1
    receipt.update({"mode": "OFFLINE_SIMULATION", "sandbox_payment_confirmed": False,
                    "simulated_payment_confirmed": True})
    return {"mode": "OFFLINE_SIMULATION", "network_calls": 0, "real_money_received": False,
            "steps": ["CREATED", "APPROVED", "COMPLETED"], "receipt": receipt,
            "repeated_capture_same_result": same_result,
            "cancelled_order_blocked": cancellation_blocked, "fulfillment_enabled": False}


def main():
    parser = argparse.ArgumentParser(description="BreakGuard pilot payments: TEST ONLY; no live mode")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--simulate", action="store_true", help="Offline fake provider; no account or network")
    group.add_argument("--sandbox-create", action="store_true")
    group.add_argument("--sandbox-capture", metavar="ORDER_ID")
    parser.add_argument("--request-id", help="Persist and reuse for retries of this operation")
    parser.add_argument("--return-url")
    parser.add_argument("--cancel-url")
    args = parser.parse_args()
    try:
        if args.simulate:
            result = simulate_checkout()
        else:
            if not args.request_id or (args.sandbox_create and (not args.return_url or not args.cancel_url)):
                parser.error("Sandbox operations need --request-id; creation also needs --return-url and --cancel-url.")
            client = SandboxCheckout(os.environ.get("PAYPAL_SANDBOX_CLIENT_ID"), os.environ.get("PAYPAL_SANDBOX_CLIENT_SECRET"))
            result = (client.create(args.request_id, args.return_url, args.cancel_url) if args.sandbox_create
                      else client.capture(args.sandbox_capture, args.request_id))
        print(json.dumps(result, indent=2))
        return 0
    except (ValueError, TypeError, KeyError, AttributeError) as exc:
        print(f"payment-test: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
