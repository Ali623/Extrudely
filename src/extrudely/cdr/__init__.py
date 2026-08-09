"""Common Drawing Representation (CDR) — Pydantic models, evidence fusion, conflict resolution.

The CDR is the universal interface between drawing parsers and 3D CAD reasoning.
Per AD-1: every parser MUST produce a DrawingDocument; every consumer reads from CDR.
"""

from extrudely.cdr.confidence import ConfidenceValue
from extrudely.cdr.coordinates import (
    CoordinateFrame,
    EngineeringCoordinate,
    NormalizedCoordinate,
    PixelCoordinate,
)
from extrudely.cdr.enums import (
    InputTypeEnum,
    LineStyleEnum,
    ProcessingModeEnum,
    SourceTypeEnum,
    StatusEnum,
    ViewTypeEnum,
)
from extrudely.cdr.evidence import Evidence, SourceFile
from extrudely.cdr.models import (
    DrawingDocument,
    DrawingMetadata,
    DrawingView,
    SectionView,
)

__all__ = [
    # Top-level models
    "DrawingDocument",
    "DrawingMetadata",
    "DrawingView",
    "SectionView",
    # Confidence and provenance
    "ConfidenceValue",
    "Evidence",
    "SourceFile",
    # Coordinates
    "PixelCoordinate",
    "NormalizedCoordinate",
    "EngineeringCoordinate",
    "CoordinateFrame",
    # Enums
    "InputTypeEnum",
    "ProcessingModeEnum",
    "ViewTypeEnum",
    "SourceTypeEnum",
    "StatusEnum",
    "LineStyleEnum",
]
