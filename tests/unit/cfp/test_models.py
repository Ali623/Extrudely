"""Tests for CFP CADFeaturePlan and PlanMetadata."""
import pytest

from extrudely.cfp.enums import PlanStatusEnum, SketchPlaneEnum
from extrudely.cfp.models import CADFeaturePlan, PlanMetadata


class TestPlanMetadata:
    def test_defaults(self):
        pm = PlanMetadata()
        assert pm.coordinate_system == {"X": "width", "Y": "depth", "Z": "height"}
        assert pm.default_sketch_plane == SketchPlaneEnum.XY

class TestCADFeaturePlan:
    def test_minimal_plan(self):
        plan = CADFeaturePlan.model_validate({
            "plan_id": "CFP_001",
            "document_id": "DOC_001",
        })
        assert plan.plan_id == "CFP_001"
        assert plan.status == PlanStatusEnum.CANDIDATE
        assert plan.sketches == []

    def test_plan_with_parameters(self):
        plan = CADFeaturePlan.model_validate({
            "plan_id": "CFP_002",
            "document_id": "DOC_002",
            "parameters": {
                "part_width": {"value": 100.0},
                "hole_dia": {"value": 8.0, "unit": "mm"},
            },
        })
        assert plan.parameters["part_width"].value == 100.0
        assert plan.parameters["hole_dia"].value == 8.0

    def test_plan_with_sketch(self):
        plan = CADFeaturePlan.model_validate({
            "plan_id": "CFP_003",
            "document_id": "DOC_003",
            "sketches": [
                {
                    "sketch_id": "SK001",
                    "plane": "XY",
                    "geometry": [{"type": "CIRCLE", "id": "C1", "center": [50, 50], "radius": 20}],
                },
            ],
        })
        assert len(plan.sketches) == 1
        assert plan.sketches[0].sketch_id == "SK001"

    def test_invalid_status_rejected(self):
        with pytest.raises(ValueError):
            CADFeaturePlan.model_validate({
                "plan_id": "CFP_004",
                "document_id": "DOC_004",
                "status": "bogus_status",
            })

    def test_round_trip_minimal(self):
        data = {
            "plan_id": "CFP_010",
            "version": "0.1",
            "document_id": "DOC_010",
            "status": "candidate",
            "metadata": {"coordinate_system": {"X": "width", "Y": "depth", "Z": "height"}, "default_sketch_plane": "XY"},
            "parameters": {},
            "sketches": [],
            "features": [],
            "assumptions": [],
            "validation_targets": [],
        }
        plan = CADFeaturePlan.model_validate(data)
        assert plan.model_dump() == data
