"""Tests for Evidence and SourceFile models."""

import pytest

from extrudely.cdr.evidence import Evidence, SourceFile


class TestSourceFile:
    def test_valid_source_file(self):
        sf = SourceFile.model_validate({
            "source_id": "SRC_001",
            "filename": "part_123.pdf",
            "mime_type": "application/pdf",
            "sha256": "a" * 64,
            "page_count": 1,
        })
        assert sf.source_id == "SRC_001"
        assert sf.filename == "part_123.pdf"

    def test_rejects_missing_required(self):
        with pytest.raises(ValueError):
            SourceFile.model_validate({"source_id": "SRC_001"})


class TestEvidence:
    def test_valid_evidence(self):
        ev = Evidence.model_validate({
            "evidence_id": "EVID_101",
            "source_id": "SRC_001",
            "source_type": "ocr",
            "page": 1,
            "view_id": "VIEW_FRONT",
            "region": [102, 220, 166, 247],
            "raw_value": "ø16",
            "confidence": 0.98,
        })
        assert ev.evidence_id == "EVID_101"
        assert ev.source_type.value == "ocr"

    def test_minimal_evidence(self):
        ev = Evidence.model_validate({
            "evidence_id": "EVID_001",
            "source_id": "SRC_001",
            "source_type": "vector_geometry",
            "confidence": 0.99,
        })
        assert ev.page is None
        assert ev.view_id is None
        assert ev.region is None
        assert ev.raw_value is None

    def test_evidence_round_trip(self):
        data = {
            "evidence_id": "EVID_200",
            "source_id": "SRC_002",
            "source_type": "vlm",
            "page": None,
            "view_id": None,
            "region": None,
            "raw_value": None,
            "confidence": 0.75,
        }
        ev = Evidence.model_validate(data)
        assert ev.model_dump() == data

    def test_region_as_list_of_ints(self):
        ev = Evidence.model_validate({
            "evidence_id": "EVID_003",
            "source_id": "SRC_001",
            "source_type": "dimension_entity",
            "confidence": 0.85,
            "region": [10, 20, 30, 40],
        })
        assert ev.region == [10, 20, 30, 40]
