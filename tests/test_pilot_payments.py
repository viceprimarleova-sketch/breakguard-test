import json

import pytest

from breakguard.pilot_payments import AMOUNT, DemoTransport, PaymentError, SandboxCheckout, simulate_checkout


def checkout():
    provider = DemoTransport()
    client = SandboxCheckout("fake-client", "fake-secret", provider)
    client.create("create-key", "https://example.com/return", "https://example.com/cancel")
    return client, provider


def test_offline_simulation_never_accesses_network(monkeypatch):
    monkeypatch.setattr("breakguard.pilot_payments._transport", lambda req: pytest.fail("Unexpected network access"))
    result = simulate_checkout()
    assert result["network_calls"] == 0 and result["repeated_capture_same_result"]
    assert result["cancelled_order_blocked"] and result["real_money_received"] is False
    assert result["fulfillment_enabled"] is False


def test_offline_simulation_uses_the_gbp_42_quote():
    result = simulate_checkout()
    assert result["receipt"]["amount"] == {"currency_code": "GBP", "value": "42.00"}
    assert result["real_money_received"] is False
    assert result["receipt"]["sandbox_payment_confirmed"] is False


def test_previous_eur_49_quote_is_refused_before_capture():
    client, provider = checkout()
    provider.order["status"] = "APPROVED"
    provider.order["purchase_units"][0]["amount"] = {
        "currency_code": "EUR", "value": "49.00"
    }
    with pytest.raises(PaymentError, match="does not match"):
        client.capture("DEMOORDER001", "capture-key")
    assert provider.capture_requests == 0


def test_old_eur_49_capture_cannot_confirm_a_gbp_42_order():
    client, provider = checkout()
    provider.order["status"] = "APPROVED"
    client.capture("DEMOORDER001", "capture-key")
    provider.order["purchase_units"][0]["payments"]["captures"][0]["amount"] = {
        "currency_code": "EUR", "value": "49.00"
    }
    with pytest.raises(PaymentError, match="not completed"):
        client.capture("DEMOORDER001", "capture-key")
    assert provider.capture_requests == 1


def test_completed_capture_is_checked_and_replays_do_not_recapture():
    client, provider = checkout()
    provider.order["status"] = "APPROVED"
    first = client.capture("DEMOORDER001", "capture-key")
    assert first == client.capture("DEMOORDER001", "capture-key")
    assert provider.capture_requests == 1


@pytest.mark.parametrize("status", ["CREATED", "CANCELLED", "VOIDED", "PAYER_ACTION_REQUIRED"])
def test_unapproved_orders_are_never_captured(status):
    client, provider = checkout()
    provider.order["status"] = status
    with pytest.raises(PaymentError, match="not completed"):
        client.capture("DEMOORDER001", "capture-key")
    assert provider.capture_requests == 0


@pytest.mark.parametrize("field,value", [("currency_code", "USD"), ("value", "0.49")])
def test_wrong_order_amount_or_currency_never_captures(field, value):
    client, provider = checkout()
    provider.order["status"] = "APPROVED"
    provider.order["purchase_units"][0]["amount"][field] = value
    with pytest.raises(PaymentError, match="does not match"):
        client.capture("DEMOORDER001", "capture-key")
    assert provider.capture_requests == 0


def test_pending_capture_cannot_unlock_anything():
    client, provider = checkout()
    provider.order["status"] = "APPROVED"
    client.capture("DEMOORDER001", "capture-key")
    provider.order["purchase_units"][0]["payments"]["captures"][0]["status"] = "PENDING"
    with pytest.raises(PaymentError, match="not completed"):
        client.capture("DEMOORDER001", "capture-key")


def test_request_url_and_secrets_never_leave_the_sandbox_host():
    observed = []
    provider = DemoTransport()
    def transport(req):
        observed.append(req)
        return provider(req)
    client = SandboxCheckout("fake-client", "fake-secret", transport)
    created = client.create("persisted-key", "https://example.com/return", "https://example.com/cancel")
    assert created["payment_confirmed"] is False
    assert all(req.full_url.startswith("https://api-m.sandbox.paypal.com/") for req in observed)
    assert observed[-1].get_header("Paypal-request-id") == "persisted-key"
    assert json.loads(observed[-1].data)["purchase_units"][0]["amount"] == AMOUNT
    assert "fake-secret" not in json.dumps(created)


def test_non_sandbox_approval_link_is_refused():
    def transport(req):
        if req.full_url.endswith("/token"):
            return {"access_token": "demo"}
        return {"id": "DEMOORDER001", "links": [{"rel": "approve", "href": "https://www.paypal.com/checkoutnow"}]}
    with pytest.raises(PaymentError, match="non-sandbox"):
        SandboxCheckout("fake", "fake", transport).create("key", "https://example.com/a", "https://example.com/b")


def test_missing_sandbox_access_fails_without_network():
    with pytest.raises(PaymentError, match="access is missing"):
        SandboxCheckout(None, None)


def test_create_retries_reuse_the_original_order():
    client, provider = checkout()
    first = provider.order.copy()
    client.create("create-key", "https://example.com/return", "https://example.com/cancel")
    assert provider.order == first


def test_completed_order_with_wrong_capture_amount_is_rejected():
    client, provider = checkout()
    provider.order["status"] = "APPROVED"
    client.capture("DEMOORDER001", "capture-key")
    provider.order["purchase_units"][0]["payments"]["captures"][0]["amount"]["value"] = "4.90"
    with pytest.raises(PaymentError, match="not completed"):
        client.capture("DEMOORDER001", "capture-key")


def test_http_error_does_not_echo_provider_body_or_credentials(monkeypatch):
    from io import BytesIO
    from urllib.error import HTTPError
    from breakguard.pilot_payments import _transport
    from urllib.request import Request
    class Opener:
        def open(self, *args, **kwargs):
            raise HTTPError("https://api-m.sandbox.paypal.com", 401, "no", {}, BytesIO(b"secret response content"))
    monkeypatch.setattr("breakguard.pilot_payments.request.build_opener", lambda *args: Opener())
    with pytest.raises(PaymentError) as exc:
        _transport(Request("https://api-m.sandbox.paypal.com/v1/oauth2/token"))
    assert "401" in str(exc.value)
    assert "secret response content" not in str(exc.value)
