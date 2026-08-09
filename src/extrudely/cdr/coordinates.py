"""CDR coordinate models — pixel, normalized, engineering, and coordinate frames."""

from typing import Literal

from pydantic import BaseModel, Field


class PixelCoordinate(BaseModel):
    """Pixel-space coordinate with origin at top-left, X right, Y down."""

    coordinate_system: Literal["pixel"] = "pixel"
    x: int = Field(..., description="X coordinate in pixels")
    y: int = Field(..., description="Y coordinate in pixels")

    model_config = {"extra": "forbid"}


class NormalizedCoordinate(BaseModel):
    """Normalized coordinate space: x, y in [0, 1], resolution-independent."""

    coordinate_system: Literal["normalized"] = "normalized"
    x: float = Field(..., ge=0.0, le=1.0, description="Normalized X in [0, 1]")
    y: float = Field(..., ge=0.0, le=1.0, description="Normalized Y in [0, 1]")

    model_config = {"extra": "forbid"}


class EngineeringCoordinate(BaseModel):
    """Engineering coordinate space in real-world units (mm preferred per AD-9)."""

    coordinate_system: Literal["engineering"] = "engineering"
    x: float = Field(..., description="X coordinate in real-world units")
    y: float = Field(..., description="Y coordinate in real-world units")
    unit: str = Field(default="mm", description="Unit: mm or inch")

    model_config = {"extra": "forbid"}


class CoordinateFrame(BaseModel):
    """Maps view-local (u, v) axes to part-global (X, Y, Z) axes."""

    u_axis: str = Field(..., description="What the local u-axis maps to (X, Y, or Z)")
    v_axis: str = Field(..., description="What the local v-axis maps to (X, Y, or Z)")

    model_config = {"extra": "forbid"}
