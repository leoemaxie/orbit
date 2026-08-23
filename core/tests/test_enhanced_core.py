from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from core.agent.condition import ConditionEvaluator
from core.models.enums import Frequency
from core.pipeline.retrieval.link_extractor import LinkExtractor
from core.pipeline.validation.anomaly_detector import AnomalyDetector
from core.scheduler.cron import calculate_next_run


def test_historical_price_drop_condition():
    evaluator = ConditionEvaluator()

    prev_records = [
        {"url": "https://example.com/1", "data": {"price": 400000}},
        {"url": "https://example.com/2", "data": {"price": 420000}},
    ]

    # Dropped from 400,000 to 350,000 (12.5% drop)
    curr_records = [
        {"url": "https://example.com/1", "data": {"price": 350000}},
        {"url": "https://example.com/2", "data": {"price": 410000}},
    ]

    matched, msg = evaluator.evaluate("price drops by 10%", curr_records, previous_records=prev_records)
    assert matched is True
    assert "12.5%" in msg


def test_historical_price_drop_not_met():
    evaluator = ConditionEvaluator()

    prev_records = [{"url": "https://example.com/1", "data": {"price": 400000}}]
    # Dropped only 5% (to 380,000)
    curr_records = [{"url": "https://example.com/1", "data": {"price": 380000}}]

    matched, _ = evaluator.evaluate("price drops by 10%", curr_records, previous_records=prev_records)
    assert matched is False


def test_link_extractor():
    extractor = LinkExtractor()
    markdown = """
    # Search Results
    - [Sony PS5 Slim Console](/p/sony-ps5-slim-1tb)
    - [PS5 Digital Edition](https://konga.com/product/ps5-digital)
    - [Privacy Policy](/privacy)
    - [External Site](https://google.com/about)
    """
    links = extractor.extract_child_links("https://konga.com/category/gaming", markdown)
    assert len(links) >= 2
    assert any("sony-ps5-slim" in l for l in links)
    assert any("ps5-digital" in l for l in links)
    assert not any("google.com" in l for l in links)


def test_anomaly_detector():
    detector = AnomalyDetector()
    records = [
        {"url": "https://example.com/1", "data": {"price": 400000}},
        {"url": "https://example.com/2", "data": {"price": 410000}},
        {"url": "https://example.com/3", "data": {"price": 395000}},
        {"url": "https://example.com/4", "data": {"price": 4000}}, # 100x lower (accessory outlier)
    ]
    annotated = detector.filter_and_annotate_outliers(records)
    outlier = [r for r in annotated if r.get("anomalies")]
    assert len(outlier) == 1
    assert outlier[0]["data"]["price"] == 4000


def test_calculate_next_run_wall_clock():
    now_utc = datetime(2026, 8, 21, 6, 0, tzinfo=timezone.utc)
    next_dt = calculate_next_run(
        frequency=Frequency.daily,
        schedule_time="08:00",
        tz_name="Africa/Lagos",
        now=now_utc,
    )
    assert next_dt is not None
    # 08:00 in Africa/Lagos (UTC+1) is 07:00 UTC
    next_lagos = next_dt.astimezone(ZoneInfo("Africa/Lagos"))
    assert next_lagos.hour == 8
    assert next_lagos.minute == 0
