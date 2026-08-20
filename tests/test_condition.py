import pytest
from core.agent.condition import ConditionEvaluator


def test_condition_aggregation_min():
    evaluator = ConditionEvaluator()
    records = [
        {"url": "https://example.com/1", "data": {"price": 450000}},
        {"url": "https://example.com/2", "data": {"price": 380000}},
        {"url": "https://example.com/3", "data": {"price": 420000}},
    ]

    matched, msg = evaluator.evaluate("min(price) < 400000", records)
    assert matched is True
    assert "380000" in msg


def test_condition_aggregation_min_false():
    evaluator = ConditionEvaluator()
    records = [
        {"url": "https://example.com/1", "data": {"price": 450000}},
        {"url": "https://example.com/2", "data": {"price": 420000}},
    ]

    matched, msg = evaluator.evaluate("min(price) < 400000", records)
    assert matched is False


def test_condition_simple_field():
    evaluator = ConditionEvaluator()
    records = [
        {"url": "https://example.com/job1", "data": {"salary": 90000}},
        {"url": "https://example.com/job2", "data": {"salary": 160000}},
    ]

    matched, msg = evaluator.evaluate("salary >= 150000", records)
    assert matched is True
    assert "job2" in msg


def test_condition_empty_or_none():
    evaluator = ConditionEvaluator()
    matched, msg = evaluator.evaluate(None, [{"data": {"price": 100}}])
    assert matched is False
