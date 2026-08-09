"""Tests for CFP enum types."""
from extrudely.cfp.enums import (
    ConstraintTypeEnum,
    OperationEnum,
    PlanStatusEnum,
    SketchPlaneEnum,
)


class TestPlanStatusEnum:
    def test_all_statuses(self):
        expected = {"candidate", "validated", "requires_review", "failed", "user_confirmed", "final"}
        assert {e.value for e in PlanStatusEnum} == expected

class TestSketchPlaneEnum:
    def test_valid_planes(self):
        assert SketchPlaneEnum.XY.value == "XY"
        assert SketchPlaneEnum.XZ.value == "XZ"
        assert SketchPlaneEnum.YZ.value == "YZ"

class TestConstraintTypeEnum:
    def test_constraint_count(self):
        types = list(ConstraintTypeEnum)
        assert len(types) == 12

class TestOperationEnum:
    def test_phase_1_ops(self):
        phase1 = {OperationEnum.SKETCH, OperationEnum.EXTRUDE, OperationEnum.CUT_EXTRUDE, OperationEnum.HOLE}
        assert len(phase1) == 4

    def test_all_13_operations(self):
        assert len(list(OperationEnum)) == 13
