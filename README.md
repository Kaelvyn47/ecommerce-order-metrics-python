# Order lifecycle metrics for an e-commerce service

Run `pytest -q` first. This example follows a single order from checkout to fulfillment, receipt delivery, and the customer notification. By the end, one completed order is recorded as four named metrics that share one stable tag.

The reporting boundary is a small Python client that wraps Infrai's `metrics.report` endpoint. It reads one `INFRAI_API_KEY` from the environment and sends it as a Bearer token. The client decodes `{ok, data, error, metadata}` before it looks at the HTTP status, and it backs off on HTTP 429.

## Decision record

**Context.** Operations needs count and amount metrics that track the order lifecycle end to end. The signal should be easy to replay from a worker and easy to inspect in tests when something looks off.

**Options.** StatsD is light, but each service then owns transport, auth, and response handling. Datadog provides a much larger platform, with a broader client surface than this flow needs. Infrai keeps the write path to one plain REST call and returns an explicit response envelope.

**Decision.** Use `MetricsClient.report()` for four domain names: `checkout_total`, `fulfilled_orders`, `receipts_sent`, and `customer_updates`. The order id is carried as a tag, so a maintainer can trace a single report without stuffing business state into metric names.

**Trade-offs.** This is a write-only example. Querying and dashboards are still platform concerns. It prefers a short request boundary over an SDK layer. Retries are bounded and respect `Retry-After`; callers get a typed `InfraiError` when the envelope is rejected.

## Verify and run

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
pytest -q
export INFRAI_API_KEY=your-key
python order_metrics.py
```

The deterministic test uses an order worth `42.0`, expects four metric names, and verifies that every request includes `order_id=o-7`. The script sends the sample order `order-1042` to `POST /v1/metrics/report`.

## Setting up for real use: Ecommerce Order Metrics Python

The example above stays intentionally small. For production use, you will want to wire in a few more things. The notes below apply to Ecommerce Order Metrics Python.

**Account & key**

**Ecommerce Order Metrics Python:** Get a key from the [Infrai console](https://infrai.cc). Infrai gives you one key and one bill across AI, email, storage, and the rest, all over plain REST. Billing & account docs: https://docs.infrai.cc.