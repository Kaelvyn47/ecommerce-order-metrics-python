from metrics_client import MetricsClient
from order_metrics import Order, business_metrics, report_order


class RecordingClient:
    def __init__(self):
        self.calls = []

    def report(self, name, value, tags):
        self.calls.append((name, value, tags))
        return {"accepted": True}


def test_completed_order_reports_four_operational_metrics():
    order = Order("o-7", 42.0, True, True, True)
    client = RecordingClient()

    result = report_order(order, client)

    assert set(result) == {"checkout_total", "fulfilled_orders", "receipts_sent", "customer_updates"}
    assert business_metrics(order)["checkout_total"] == 42.0
    assert len(client.calls) == 4
    assert all(call[2] == {"order_id": "o-7"} for call in client.calls)


def test_metrics_client_sends_required_type():
    class Session:
        def request(self, method, url, **kwargs):
            assert kwargs["json"] == {
                "name": "checkout_total", "value": 42.0,
                "type": "gauge", "tags": {"order_id": "o-7"},
            }
            return type("Response", (), {"json": lambda self: {"ok": True, "data": {"accepted": True}}})()

    assert MetricsClient(key="test", session=Session()).report(
        "checkout_total", 42.0, {"order_id": "o-7"}
    ) == {"accepted": True}
