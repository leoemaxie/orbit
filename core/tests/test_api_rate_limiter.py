import asyncio
import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from core.api.rate_limiter import APIRateLimiter, rate_limit
from core.config.settings import Settings


@pytest.fixture(autouse=True)
def reset_rate_limiter():
    APIRateLimiter.reset()
    yield
    APIRateLimiter.reset()


@pytest.mark.asyncio
async def test_sliding_window_rate_limiter_logic():
    client_ip = "192.168.1.100"
    resource = "goal"
    limit = 3
    window = 2

    # 1. First 3 requests allowed
    for i in range(limit):
        allowed, remaining, retry_after = await APIRateLimiter.check(
            client_id=client_ip,
            resource_key=resource,
            limit=limit,
            window_seconds=window,
        )
        assert allowed is True
        assert remaining == limit - i - 1
        assert retry_after == 0

    # 2. 4th request blocked (429 condition)
    allowed, remaining, retry_after = await APIRateLimiter.check(
        client_id=client_ip,
        resource_key=resource,
        limit=limit,
        window_seconds=window,
    )
    assert allowed is False
    assert remaining == 0
    assert retry_after > 0

    # 3. Different client IP is unaffected (isolated buckets)
    other_ip = "10.0.0.1"
    allowed_other, _, _ = await APIRateLimiter.check(
        client_id=other_ip,
        resource_key=resource,
        limit=limit,
        window_seconds=window,
    )
    assert allowed_other is True

    # 4. Wait for sliding window to expire
    await asyncio.sleep(window + 0.1)
    allowed_after_window, remaining_after, _ = await APIRateLimiter.check(
        client_id=client_ip,
        resource_key=resource,
        limit=limit,
        window_seconds=window,
    )
    assert allowed_after_window is True
    assert remaining_after == limit - 1


def test_api_rate_limit_endpoint_integration():
    app = FastAPI()

    @app.post("/test-goal", dependencies=[Depends(rate_limit("test_goal", max_requests=2, window_seconds=60))])
    def sample_endpoint():
        return {"status": "ok"}

    with TestClient(app) as client:
        # Request 1: OK
        res1 = client.post("/test-goal", headers={"X-Forwarded-For": "203.0.113.195"})
        assert res1.status_code == 200
        assert res1.headers["X-RateLimit-Limit"] == "2"
        assert res1.headers["X-RateLimit-Remaining"] == "1"

        # Request 2: OK
        res2 = client.post("/test-goal", headers={"X-Forwarded-For": "203.0.113.195"})
        assert res2.status_code == 200
        assert res2.headers["X-RateLimit-Remaining"] == "0"

        # Request 3: Rate Limited (429)
        res3 = client.post("/test-goal", headers={"X-Forwarded-For": "203.0.113.195"})
        assert res3.status_code == 429
        assert "Rate limit exceeded" in res3.json()["detail"]
        assert "Retry-After" in res3.headers
        assert res3.headers["X-RateLimit-Remaining"] == "0"

        # Different client IP is still allowed
        res_other = client.post("/test-goal", headers={"X-Forwarded-For": "198.51.100.22"})
        assert res_other.status_code == 200
