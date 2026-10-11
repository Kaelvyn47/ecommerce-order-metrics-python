from dataclasses import dataclass

from metrics_client import MetricsClient


@dataclass(frozen=True)
class Order:
    order_id: str
    total: float
    fulfilled: bool
    receipt_sent: bool
    customer_updated: bool


def business_metrics(order: Order) -> dict[str, float]:
    """Return metrics only after the order has cleared each operational step."""
    return {
        "checkout_total": order.total,
        "fulfilled_orders": float(order.fulfilled),
        "receipts_sent": float(order.receipt_sent),
        "customer_updates": float(order.customer_updated),
    }


def report_order(order: Order, client: MetricsClient) -> dict[str, dict]:
    tags = {"order_id": order.order_id}
    report = MetricsClient.report.__get__(client, MetricsClient) if isinstance(client, MetricsClient) else client.report
    return {
        name: report(name, value, tags)
        for name, value in business_metrics(order).items()
    }


if __name__ == "__main__":
    sample = Order("order-1042", 129.50, True, True, True)
    print(report_order(sample, MetricsClient()))
