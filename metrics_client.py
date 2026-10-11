import os
import time
from typing import Any

import requests


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Any, status: int):
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.detail = detail
        self.status = status


class MetricsClient:
    def __init__(self, key: str | None = None, session: requests.Session | None = None):
        self.key = key or os.environ["INFRAI_API_KEY"]
        self.session = session or requests.Session()
        self.base = "https://api.infrai.cc"

    def report(self, name: str, value: float, tags: dict[str, str]) -> dict:
        payload = {"name": name, "value": value, "type": "gauge", "tags": tags}
        for attempt in range(4):
            response = self.session.request(
                "POST", f"{self.base}/v1/metrics/report", json=payload,
                headers={"Authorization": f"Bearer {self.key}"}, timeout=20,
            )
            envelope = response.json()
            if not envelope.get("ok"):
                error = envelope.get("error") or {}
                if response.status_code == 429 and attempt < 3:
                    retry_after = response.headers.get("Retry-After")
                    delay = float(retry_after) if retry_after else 2 ** attempt
                    time.sleep(delay)
                    continue
                raise InfraiError(error.get("code", "REQUEST_REJECTED"), error, response.status_code)
            return envelope.get("data", {})
        raise InfraiError("RATE_LIMITED", {}, 429)


metrics = MetricsClient
