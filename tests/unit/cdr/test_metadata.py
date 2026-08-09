"""Tests for DrawingMetadata model."""

from extrudely.cdr.models import DrawingMetadata


class TestDrawingMetadata:
    def test_full_metadata(self):
        md = DrawingMetadata.model_validate({
            "part_name": {"value": "Mounting Bracket", "confidence": 0.95, "status": "observed", "evidence_ids": []},
            "part_number": {"value": "BR-1042", "confidence": 0.98, "status": "observed", "evidence_ids": []},
            "material": {"value": "EN AW-6061", "confidence": 0.90, "status": "inferred", "evidence_ids": ["EVID_010"]},
            "language": {"value": "en", "confidence": 0.99, "status": "observed", "evidence_ids": []},
            "units": {"value": "mm", "confidence": 0.99, "status": "observed", "evidence_ids": ["EVID_014"]},
            "scale": {"value": "1:2", "confidence": 0.88, "status": "observed", "evidence_ids": []},
            "projection_system": {"value": "first_angle", "confidence": 0.95, "status": "inferred", "evidence_ids": []},
        })
        assert md.part_name.value == "Mounting Bracket"
        assert md.units.value == "mm"

    def test_default_values_are_unknown(self):
        md = DrawingMetadata()
        assert md.part_name.status.value == "unknown"
        assert md.part_name.confidence == 0.0
        assert md.part_name.value is None
        assert md.material.value is None  # Optional fields default to None
