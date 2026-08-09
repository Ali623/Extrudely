"""CFP enum types — plan status, sketch planes, constraints, and operations."""
from enum import StrEnum


class PlanStatusEnum(StrEnum):
    CANDIDATE = "candidate"
    VALIDATED = "validated"
    REQUIRES_REVIEW = "requires_review"
    FAILED = "failed"
    USER_CONFIRMED = "user_confirmed"
    FINAL = "final"

class SketchPlaneEnum(StrEnum):
    XY = "XY"
    XZ = "XZ"
    YZ = "YZ"

class ConstraintTypeEnum(StrEnum):
    HORIZONTAL = "horizontal"
    VERTICAL = "vertical"
    PARALLEL = "parallel"
    PERPENDICULAR = "perpendicular"
    COINCIDENT = "coincident"
    CONCENTRIC = "concentric"
    EQUAL = "equal"
    SYMMETRIC = "symmetric"
    TANGENT = "tangent"
    DISTANCE = "distance"
    RADIUS = "radius"
    DIAMETER = "diameter"

class OperationEnum(StrEnum):
    SKETCH = "SKETCH"
    EXTRUDE = "EXTRUDE"
    CUT_EXTRUDE = "CUT_EXTRUDE"
    HOLE = "HOLE"
    COUNTERBORE = "COUNTERBORE"
    COUNTERSINK = "COUNTERSINK"
    REVOLVE = "REVOLVE"
    REVOLVE_CUT = "REVOLVE_CUT"
    LINEAR_PATTERN = "LINEAR_PATTERN"
    CIRCULAR_PATTERN = "CIRCULAR_PATTERN"
    MIRROR = "MIRROR"
    CHAMFER = "CHAMFER"
    FILLET = "FILLET"
