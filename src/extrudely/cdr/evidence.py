"""CDR evidence and source file models — provenance tracking for every interpreted value."""


from pydantic import BaseModel, Field

from extrudely.cdr.enums import SourceTypeEnum


class SourceFile(BaseModel):
    """Registration record for an uploaded source file.

    Hashes help guarantee experiment reproducibility.
    """

    source_id: str = Field(..., description="Unique source identifier, e.g. SRC_001")
    filename: str = Field(..., description="Original filename")
    mime_type: str = Field(..., description="MIME type, e.g. application/pdf")
    sha256: str = Field(..., description="SHA-256 hash of the file contents")
    page_count: int = Field(..., ge=1, description="Number of pages (1 for single-page files)")

    model_config = {"extra": "forbid"}


class Evidence(BaseModel):
    """Evidence record linking an interpreted value to its source in the drawing.

    Every meaningful interpretation should point to at least one Evidence object.
    """

    evidence_id: str = Field(..., description="Unique evidence identifier, e.g. EVID_101")
    source_id: str = Field(..., description="Reference to the source file (SRC_...)")
    source_type: SourceTypeEnum = Field(
        ..., description="How this evidence was obtained (OCR, vector geometry, VLM, etc.)"
    )
    page: int | None = Field(default=None, ge=1, description="Page number if multi-page document")
    view_id: str | None = Field(default=None, description="View this evidence belongs to")
    region: list[int] | None = Field(
        default=None,
        description="Bounding box [x_min, y_min, x_max, y_max] in pixel coordinates",
    )
    raw_value: str | None = Field(
        default=None, description="Raw extracted text or value before normalization"
    )
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in this evidence piece")

    model_config = {"extra": "forbid"}
