"""Tests for DrawingDocument top-level model."""

from datetime import UTC, datetime

import pytest

from extrudely.cdr.models import DrawingDocument


def _make_metadata(**overrides):
    defaults = {
        "part_name": {"value": "Test Part", "confidence": 0.9, "status": "observed", "evidence_ids": []},
        "part_number": {"value": "T-001", "confidence": 0.9, "status": "observed", "evidence_ids": []},
        "material": {"value": None, "confidence": 0.0, "status": "unknown", "evidence_ids": []},
        "language": {"value": "en", "confidence": 0.9, "status": "observed", "evidence_ids": []},
        "units": {"value": "mm", "confidence": 0.9, "status": "observed", "evidence_ids": []},
        "scale": {"value": None, "confidence": 0.0, "status": "unknown", "evidence_ids": []},
        "projection_system": {"value": None, "confidence": 0.0, "status": "unknown", "evidence_ids": []},
    }
    defaults.update(overrides)
    return defaults


class TestDrawingDocument:
    def test_minimal_valid_document(self):
        doc = DrawingDocument.model_validate({
            "document_id": "DOC_000123",
            "schema_version": "0.1",
            "created_at": datetime.now(UTC),
            "input_type": "DXF",
            "source_files": [],
            "processing_mode": "vector",
            "metadata": _make_metadata(),
        })
        assert doc.document_id == "DOC_000123"
        assert doc.schema_version == "0.1"
        assert doc.benchmark_mode is False  # default

    def test_full_document(self):
        doc = DrawingDocument.model_validate({
            "document_id": "DOC_000456",
            "schema_version": "0.1",
            "created_at": datetime.now(UTC),
            "input_type": "PNG",
            "source_files": [],
            "processing_mode": "raster",
            "benchmark_mode": True,
            "metadata": _make_metadata(),
            "views": [
                {
                    "view_id": "VIEW_FRONT",
                    "view_type": "front",
                    "confidence": 0.98,
                    "projection_system": "first_angle",
                    "bounding_box": [0.10, 0.15, 0.48, 0.61],
                }
            ],
        })
        assert doc.benchmark_mode is True
        assert len(doc.views) == 1
        assert doc.views[0].view_id == "VIEW_FRONT"

    def test_missing_required_fields(self):
        with pytest.raises(ValueError):
            DrawingDocument.model_validate({"document_id": "DOC_001"})

    def test_invalid_input_type(self):
        with pytest.raises(ValueError):
            DrawingDocument.model_validate({
                "document_id": "DOC_001",
                "schema_version": "0.1",
                "created_at": datetime.now(UTC),
                "input_type": "DWG",  # Not supported
                "source_files": [],
                "processing_mode": "raster",
                "metadata": _make_metadata(),
            })

    def test_invalid_schema_version(self):
        with pytest.raises(ValueError):
            DrawingDocument.model_validate({
                "document_id": "DOC_001",
                "schema_version": "0.2",  # Only 0.1 supported
                "created_at": datetime.now(UTC),
                "input_type": "DXF",
                "source_files": [],
                "processing_mode": "vector",
                "metadata": _make_metadata(),
            })

    def test_document_round_trip(self):
        data = {
            "document_id": "DOC_000789",
            "schema_version": "0.1",
            "created_at": "2026-08-09T00:00:00Z",
            "input_type": "DXF",
            "source_files": [],
            "processing_mode": "vector",
            "benchmark_mode": False,
            "metadata": _make_metadata(),
            "views": [],
            "sheets": [],
            "primitives": [],
            "annotations": [],
            "dimensions": [],
            "constraints": [],
            "cross_view_links": [],
            "feature_hypotheses": [],
            "conflicts": [],
            "uncertainties": [],
        }
        doc = DrawingDocument.model_validate(data)
        dumped = doc.model_dump()
        dumped["created_at"] = "2026-08-09T00:00:00Z"  # normalize for comparison
        assert dumped == data
