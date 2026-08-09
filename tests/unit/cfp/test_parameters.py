"""Tests for CFP Parameter model."""
import pytest

from extrudely.cfp.parameters import Parameter


class TestParameter:
    def test_valid_parameter(self):
        p = Parameter.model_validate({"value": 100.0, "unit": "mm", "cdr_reference": "DIM_001"})
        assert p.value == 100.0
        assert p.unit == "mm"
        assert p.cdr_reference == "DIM_001"

    def test_defaults(self):
        p = Parameter.model_validate({"value": 8.0})
        assert p.unit == "mm"
        assert p.confidence == 1.0
        assert p.status == "observed"
        assert p.cdr_reference is None

    def test_confidence_bounds(self):
        Parameter.model_validate({"value": 1.0, "confidence": 0.0})
        Parameter.model_validate({"value": 1.0, "confidence": 1.0})
        with pytest.raises(ValueError):
            Parameter.model_validate({"value": 1.0, "confidence": -0.1})
        with pytest.raises(ValueError):
            Parameter.model_validate({"value": 1.0, "confidence": 1.5})

    def test_round_trip(self):
        data = {"value": 50.0, "unit": "mm", "cdr_reference": "DIM_008", "confidence": 0.98, "status": "observed"}
        p = Parameter.model_validate(data)
        assert p.model_dump() == data

class TestParameterNameRef:
    def test_param_ref_syntax(self):
        params = {
            "part_width": Parameter.model_validate({"value": 100.0}),
            "hole_diameter": Parameter.model_validate({"value": 8.0}),
        }
        assert "part_width" in params
        assert params["part_width"].value == 100.0
