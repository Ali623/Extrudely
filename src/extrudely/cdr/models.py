"""CDR top-level Pydantic models — DrawingDocument, DrawingMetadata, DrawingView, SectionView.

Per AD-1: These models are the universal interface all parsers produce and all consumers read.
Per AD-2: CDR is separate from CFP — no CadQuery operations or CFP types belong here.
"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from extrudely.cdr.confidence import ConfidenceValue
from extrudely.cdr.coordinates import CoordinateFrame
from extrudely.cdr.enums import InputTypeEnum, ProcessingModeEnum, ViewTypeEnum
from extrudely.cdr.evidence import SourceFile


class DrawingMetadata(BaseModel):
    """Metadata extracted from the drawing title block and surrounding context.

    Every field uses the standard ConfidenceValue wrapper per CDR spec §6-7.
    Fields that are often missing (material, scale, projection_system) use
    ConfidenceValue[str | None] to accept None without error.
    """

    part_name: ConfidenceValue[str] = Field(default_factory=ConfidenceValue[str])
    part_number: ConfidenceValue[str] = Field(default_factory=ConfidenceValue[str])
    material: ConfidenceValue[str | None] = Field(
        default_factory=lambda: ConfidenceValue[str | None](value=None)
    )
    language: ConfidenceValue[str] = Field(default_factory=ConfidenceValue[str])
    units: ConfidenceValue[str] = Field(default_factory=ConfidenceValue[str])
    scale: ConfidenceValue[str | None] = Field(
        default_factory=lambda: ConfidenceValue[str | None](value=None)
    )
    projection_system: ConfidenceValue[str | None] = Field(
        default_factory=lambda: ConfidenceValue[str | None](value=None)
    )

    model_config = {"extra": "forbid"}


class DrawingView(BaseModel):
    """An identified orthographic view within the drawing.

    Each view has a type, bounding box, and coordinate frame mapping its local
    (u, v) axes to the part-global (X, Y, Z) axes per CDR spec §13-14.
    """

    view_id: str = Field(..., description="Unique view identifier, e.g. VIEW_FRONT")
    view_type: ViewTypeEnum = Field(..., description="Orthographic view type")
    confidence: float = Field(..., ge=0.0, le=1.0, description="View detection confidence")
    projection_system: str | None = Field(
        default=None, description="Projection system (first_angle, third_angle)"
    )
    bounding_box: list[float] | None = Field(
        default=None,
        description="Normalized bounding box [x_min, y_min, x_max, y_max]",
    )
    coordinate_frame: CoordinateFrame | None = Field(
        default=None, description="Local (u,v) → global (X,Y,Z) axis mapping"
    )

    model_config = {"extra": "forbid"}


class SectionView(DrawingView):
    """A section view extends DrawingView with section-specific metadata per CDR spec §15."""

    section_label: str = Field(..., description="Section label, e.g. A-A")
    section_type: str = Field(default="full", description="Section type: full, half, offset")

    model_config = {"extra": "forbid"}


class DrawingDocument(BaseModel):
    """Top-level CDR document — the universal interface for all parsers and consumers.

    Per AD-1: Every parser MUST produce a DrawingDocument. Every consumer MUST read
    only from CDR. No module below Layer A may branch on input_type.

    Per AD-8: benchmark_mode is an architectural switch that disables vector evidence,
    user correction, and external metadata during inference.
    """

    document_id: str = Field(..., description="Unique document identifier, e.g. DOC_000123")
    schema_version: Literal["0.1"] = Field(
        default="0.1", description="CDR schema version — only 0.1 is valid"
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(datetime.now().astimezone().tzinfo),
        description="Document creation timestamp",
    )
    input_type: InputTypeEnum = Field(..., description="Input format of the source drawing")
    source_files: list[SourceFile] = Field(
        default_factory=list, description="Source files used to produce this CDR"
    )
    processing_mode: ProcessingModeEnum = Field(
        ..., description="Pipeline processing mode: raster, vector, or hybrid"
    )
    benchmark_mode: bool = Field(
        default=False,
        description="When true, enforces Ortho2CAD-compatible restrictions",
    )
    metadata: DrawingMetadata = Field(
        default_factory=DrawingMetadata, description="Drawing metadata from title block"
    )
    views: list[DrawingView] = Field(
        default_factory=list, description="Detected orthographic views"
    )
    sheets: list[dict] = Field(
        default_factory=list, description="Sheets (exactly 1 for POC 1)"
    )
    primitives: list[dict] = Field(
        default_factory=list,
        description="Geometric primitives — typed in a later story (1-3+)",
    )
    annotations: list[dict] = Field(
        default_factory=list, description="Text annotations"
    )
    dimensions: list[dict] = Field(
        default_factory=list, description="Dimension entities"
    )
    constraints: list[dict] = Field(
        default_factory=list, description="Geometric constraints"
    )
    cross_view_links: list[dict] = Field(
        default_factory=list, description="Cross-view entity links"
    )
    feature_hypotheses: list[dict] = Field(
        default_factory=list, description="3D feature hypotheses"
    )
    conflicts: list[dict] = Field(
        default_factory=list, description="Evidence conflicts"
    )
    uncertainties: list[dict] = Field(
        default_factory=list, description="Uncertainty records"
    )

    model_config = {"extra": "forbid"}
