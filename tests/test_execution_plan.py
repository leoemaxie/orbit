from core.models.execution_plan import (
    DynamicExtractionSchema,
    ExecutionPlan,
    ExtractionField,
)


def test_dynamic_extraction_schema_to_json_schema():
    schema = DynamicExtractionSchema(
        entity_name="flight",
        fields=[
            ExtractionField(name="airline", type="string", required=True),
            ExtractionField(name="price", type="number", required=True),
            ExtractionField(
                name="stops",
                type="string",
                required=False,
                enum_values=["direct", "1_stop", "2+_stops"],
            ),
        ],
    )

    json_schema = schema.to_json_schema()
    assert json_schema["type"] == "object"
    assert "airline" in json_schema["properties"]
    assert "price" in json_schema["properties"]
    assert json_schema["required"] == ["airline", "price"]
    assert json_schema["properties"]["stops"]["enum"] == ["direct", "1_stop", "2+_stops"]
