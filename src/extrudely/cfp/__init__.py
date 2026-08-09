"""CAD Feature Plan (CFP) — Pydantic models, parameter table, dependency graph.

Per AD-2: CFP is separate from CDR. CFP stores the proposed CAD construction plan.
Per AD-3: The deterministic compiler consumes CFP to generate CadQuery.
"""
from extrudely.cfp.enums import (
    ConstraintTypeEnum,
    OperationEnum,
    PlanStatusEnum,
    SketchPlaneEnum,
)
from extrudely.cfp.features import CutExtrudeFeature, ExtrudeFeature
from extrudely.cfp.models import CADFeaturePlan, PlanMetadata
from extrudely.cfp.parameters import Parameter
from extrudely.cfp.sketch import (
    ArcPrimitive,
    CirclePrimitive,
    LinePrimitive,
    PolylinePrimitive,
    RectanglePrimitive,
    Sketch,
    SketchConstraint,
    SketchPrimitive,
)

__all__ = [
    "CADFeaturePlan",
    "CutExtrudeFeature",
    "ExtrudeFeature",
    "PlanMetadata",
    "Parameter",
    "Sketch",
    "SketchConstraint",
    "SketchPrimitive",
    "LinePrimitive",
    "ArcPrimitive",
    "CirclePrimitive",
    "RectanglePrimitive",
    "PolylinePrimitive",
    "PlanStatusEnum",
    "SketchPlaneEnum",
    "ConstraintTypeEnum",
    "OperationEnum",
]
