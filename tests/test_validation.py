import pytest
from orbit.models.execution_plan import (
    DynamicExtractionSchema,
    ExecutionPlan,
    ExtractionField,
)
from orbit.pipeline.validation.schema_validator import SchemaValidator


def test_schema_validator_valid_job_listing():
    schema = DynamicExtractionSchema(
        entity_name="job_listing",
        fields=[
            ExtractionField(name="title", type="string", required=True),
            ExtractionField(name="company", type="string", required=True),
            ExtractionField(name="salary_min", type="number", required=False),
            ExtractionField(
                name="employment_type",
                type="string",
                required=False,
                enum_values=["full_time", "part_time", "contract"],
            ),
        ],
    )
    plan = ExecutionPlan(
        objective="Find Python jobs",
        search_query="Python remote jobs",
        extraction_schema=schema,
    )

    validator = SchemaValidator()
    record = {
        "url": "https://example.com/job/123",
        "data": {
            "title": "Senior Python Engineer",
            "company": "Orbit Labs",
            "salary_min": 160000,
            "employment_type": "full_time",
        },
    }

    is_valid, errors = validator.validate(record, plan)
    assert is_valid is True
    assert errors == []


def test_schema_validator_missing_required():
    schema = DynamicExtractionSchema(
        entity_name="job_listing",
        fields=[
            ExtractionField(name="title", type="string", required=True),
            ExtractionField(name="company", type="string", required=True),
        ],
    )
    plan = ExecutionPlan(
        objective="Find Python jobs",
        search_query="Python jobs",
        extraction_schema=schema,
    )

    validator = SchemaValidator()
    record = {
        "url": "https://example.com/job/123",
        "data": {
            "title": "Senior Python Engineer",
            # missing company
        },
    }

    is_valid, errors = validator.validate(record, plan)
    assert is_valid is False
    assert any("Missing required field: 'company'" in e for e in errors)


def test_schema_validator_invalid_enum():
    schema = DynamicExtractionSchema(
        entity_name="product",
        fields=[
            ExtractionField(
                name="availability",
                type="string",
                enum_values=["in_stock", "out_of_stock"],
            ),
        ],
    )
    plan = ExecutionPlan(
        objective="Find products",
        search_query="product query",
        extraction_schema=schema,
    )

    validator = SchemaValidator()
    record = {
        "url": "https://example.com/p/1",
        "data": {"availability": "maybe_available"},
    }

    is_valid, errors = validator.validate(record, plan)
    assert is_valid is False
    assert any("not in allowed values" in e for e in errors)
