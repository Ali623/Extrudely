"""Tests for ConfidenceValue wrapper."""

import pytest

from extrudely.cdr.confidence import ConfidenceValue
from extrudely.cdr.enums import StatusEnum


class TestConfidenceValueDefaults:
    def test_defaults_produce_unknown(self):
        cv = ConfidenceValue()
        assert cv.value is None
        assert cv.confidence == 0.0
        assert cv.status == StatusEnum.UNKNOWN
        assert cv.evidence_ids == []

    def test_default_serialization(self):
        cv = ConfidenceValue()
        d = cv.model_dump()
        assert d == {
            "value": None,
            "confidence": 0.0,
            "status": "unknown",
            "evidence_ids": [],
        }


class TestConfidenceValueString:
    def test_observed_string(self):
        cv = ConfidenceValue[str].model_validate({
            "value": "mm",
            "confidence": 0.99,
            "status": "observed",
            "evidence_ids": ["EVID_014"],
        })
        assert cv.value == "mm"
        assert cv.confidence == 0.99
        assert cv.status == StatusEnum.OBSERVED

    def test_round_trip(self):
        data = {
            "value": "EN AW-6061",
            "confidence": 0.85,
            "status": "observed",
            "evidence_ids": [],
        }
        cv = ConfidenceValue[str].model_validate(data)
        assert cv.model_dump() == data


class TestConfidenceValueFloat:
    def test_observed_float(self):
        cv = ConfidenceValue[float].model_validate({
            "value": 16.0,
            "confidence": 0.97,
            "status": "observed",
            "evidence_ids": ["EVID_101"],
        })
        assert cv.value == 16.0
        assert cv.confidence == 0.97

    def test_inferred_with_evidence(self):
        cv = ConfidenceValue[float].model_validate({
            "value": 8.5,
            "confidence": 0.72,
            "status": "inferred",
            "evidence_ids": ["EVID_201", "EVID_202"],
        })
        assert cv.status == StatusEnum.INFERRED


class TestConfidenceValueOptional:
    def test_none_optional_value(self):
        cv = ConfidenceValue[str | None].model_validate({
            "value": None,
            "confidence": 0.0,
            "status": "unknown",
            "evidence_ids": [],
        })
        assert cv.value is None

    def test_some_optional_value(self):
        cv = ConfidenceValue[str | None].model_validate({
            "value": "first_angle",
            "confidence": 0.91,
            "status": "inferred",
            "evidence_ids": ["EVID_003"],
        })
        assert cv.value == "first_angle"


class TestConfidenceValueValidation:
    def test_rejects_confidence_below_zero(self):
        with pytest.raises(ValueError):
            ConfidenceValue[str].model_validate({
                "value": "test",
                "confidence": -0.1,
                "status": "observed",
                "evidence_ids": [],
            })

    def test_rejects_confidence_above_one(self):
        with pytest.raises(ValueError):
            ConfidenceValue[str].model_validate({
                "value": "test",
                "confidence": 1.5,
                "status": "observed",
                "evidence_ids": [],
            })

    def test_accepts_confidence_boundaries(self):
        cv0 = ConfidenceValue[str].model_validate({
            "value": "zero", "confidence": 0.0, "status": "unknown", "evidence_ids": [],
        })
        assert cv0.confidence == 0.0

        cv1 = ConfidenceValue[str].model_validate({
            "value": "one", "confidence": 1.0, "status": "observed", "evidence_ids": [],
        })
        assert cv1.confidence == 1.0

    def test_rejects_invalid_status(self):
        with pytest.raises(ValueError):
            ConfidenceValue[str].model_validate({
                "value": "test",
                "confidence": 0.5,
                "status": "invalid_status",
                "evidence_ids": [],
            })

    def test_partial_input_gets_defaults(self):
        """Missing fields get their defaults (not an error — ConfidenceValue has defaults)."""
        cv = ConfidenceValue[str].model_validate({"value": "only_value"})
        assert cv.value == "only_value"
        assert cv.confidence == 0.0  # default
        assert cv.status == StatusEnum.UNKNOWN  # default
        assert cv.evidence_ids == []  # default


class TestConfidenceValueUnknownPattern:
    """Per AD-6: unknown values serialize as value=null, confidence=0.0, status=unknown."""
    def test_explicit_unknown_serialization(self):
        cv = ConfidenceValue[str].model_validate({
            "value": None,
            "confidence": 0.0,
            "status": "unknown",
            "evidence_ids": [],
        })
        d = cv.model_dump()
        assert d["value"] is None
        assert d["confidence"] == 0.0
        assert d["status"] == "unknown"
