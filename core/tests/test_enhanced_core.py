from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from core.agent.condition import ConditionEvaluator
from core.models.enums import Frequency
from core.models.execution_plan import (
    DynamicExtractionSchema,
    ExecutionPlan,
    ExtractionField,
)
from core.pipeline.retrieval.link_extractor import LinkExtractor
from core.pipeline.validation.anomaly_detector import AnomalyDetector
from core.pipeline.verification.engine import VerificationEngine
from core.scheduler.cron import calculate_next_run


def test_historical_generic_drop_condition():
    evaluator = ConditionEvaluator()

    prev_records = [
        {"url": "https://example.com/job1", "data": {"salary": 160000}},
        {"url": "https://example.com/job2", "data": {"salary": 170000}},
    ]

    # Salary dropped from 160,000 to 140,000 (12.5% drop)
    curr_records = [
        {"url": "https://example.com/job1", "data": {"salary": 140000}},
        {"url": "https://example.com/job2", "data": {"salary": 165000}},
    ]

    matched, msg = evaluator.evaluate("salary drops by 10%", curr_records, previous_records=prev_records)
    assert matched is True
    assert "12.5%" in msg


def test_categorical_condition_evaluation():
    evaluator = ConditionEvaluator()
    records = [
        {"url": "https://example.com/apt1", "data": {"rent": 2400, "status": "available"}},
        {"url": "https://example.com/apt2", "data": {"rent": 2800, "status": "rented"}},
    ]

    matched, msg = evaluator.evaluate("status == 'available'", records)
    assert matched is True
    assert "1 record(s)" in msg


def test_aggregation_condition_on_non_price():
    evaluator = ConditionEvaluator()
    records = [
        {"url": "https://example.com/flight1", "data": {"fare": 750, "airline": "Delta"}},
        {"url": "https://example.com/flight2", "data": {"fare": 890, "airline": "Virgin"}},
    ]
    matched, msg = evaluator.evaluate("min(fare) < 800", records)
    assert matched is True
    assert "750.0" in msg


def test_link_extractor():
    extractor = LinkExtractor()
    markdown = """
    # Search Results
    - [Senior Python Engineer](/jobs/senior-python-engineer)
    - [2 Bedroom Flat in Lagos](https://propertypro.ng/property/2-bed-ikoyi)
    - [Privacy Policy](/privacy)
    - [External Site](https://google.com/about)
    """
    links = extractor.extract_child_links("https://jobsite.com/search", markdown)
    assert len(links) >= 2
    assert any("senior-python-engineer" in l for l in links)
    assert any("2-bed-ikoyi" in l for l in links)
    assert not any("google.com" in l for l in links)


def test_anomaly_detector_multi_domain():
    detector = AnomalyDetector()
    schema = DynamicExtractionSchema(
        entity_name="apartment",
        fields=[
            ExtractionField(name="title", type="string", required=True),
            ExtractionField(name="sqft", type="number", required=True),
        ],
    )
    plan = ExecutionPlan(
        objective="Find flats in Lagos",
        extraction_schema=schema,
    )
    records = [
        {"url": "https://example.com/1", "data": {"title": "Flat A", "sqft": 1200}},
        {"url": "https://example.com/2", "data": {"title": "Flat B", "sqft": 1150}},
        {"url": "https://example.com/3", "data": {"title": "Flat C", "sqft": 1300}},
        {"url": "https://example.com/4", "data": {"title": "Studio Outlier", "sqft": 15}},  # Outlier
    ]
    annotated = detector.filter_and_annotate_outliers(records, plan=plan)
    outliers = [r for r in annotated if r.get("anomalies")]
    assert len(outliers) == 1
    assert outliers[0]["data"]["sqft"] == 15


def test_verification_engine():
    engine = VerificationEngine()
    plan = ExecutionPlan(
        objective="Track tech salaries",
        frequency=Frequency.daily,
    )
    sources = ["https://example.com/jobs"]
    pages = {"https://example.com/jobs": "# Job Listing\nSenior Dev: $160,000"}
    extracted = [{"url": "https://example.com/jobs", "data": {"salary": 160000}}]
    validated = [{"url": "https://example.com/jobs", "data": {"salary": 160000}, "valid": True}]

    report = engine.verify_run(
        plan=plan,
        sources=sources,
        pages=pages,
        extracted_records=extracted,
        validated_records=validated,
        results_persisted=True,
        next_run_at=datetime.now(timezone.utc),
    )
    assert report.verified is True
    assert report.sources_discovered is True
    assert report.data_extracted is True
    assert report.data_validated is True


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
