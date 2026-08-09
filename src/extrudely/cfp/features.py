"""CFP feature models — per-operation Pydantic models for the CAD Feature Plan.

Per AD-13: Operations enabled in locked phases. Phase 1: SKETCH, EXTRUDE, CUT_EXTRUDE, HOLE.
"""
import math
from typing import Literal

from pydantic import BaseModel, Field, field_validator

from extrudely.cfp.enums import OperationEnum


class ExtrudeFeature(BaseModel):
    """CFP EXTRUDE feature per CFP spec §18.

    Maps a sketch to a 3D extrusion along a direction vector.
    """

    feature_id: str = Field(..., description="Feature identifier, e.g. F001")
    operation: OperationEnum = Field(default=OperationEnum.EXTRUDE)
    sketch_id: str = Field(..., description="Sketch identifier to extrude, e.g. SK001")
    direction: list[float] = Field(
        default=[0.0, 0.0, 1.0],
        min_length=3,
        max_length=3,
        description="Extrusion direction vector [x, y, z]",
    )
    distance: float | str = Field(
        ..., description="Extrusion distance in mm, or $param_name reference"
    )
    mode: Literal["add", "new_body"] = Field(
        default="add", description="Extrusion mode: add (default) or new_body"
    )
    symmetric: bool = Field(default=False, description="Extrude symmetrically if true")

    model_config = {"extra": "forbid"}

    @field_validator("direction")
    @classmethod
    def _direction_must_be_finite(cls, v: list[float]) -> list[float]:
        if not all(math.isfinite(x) for x in v):
            raise ValueError(f"Direction components must be finite, got {v}")
        return v

    @field_validator("distance", mode="before")
    @classmethod
    def _distance_string_shape(cls, v: object) -> object:
        if isinstance(v, str):
            stripped = v.strip()
            if stripped == "":
                raise ValueError("Distance string must not be empty")
            if stripped.startswith("$"):
                if len(stripped) < 2 or stripped == "$":
                    raise ValueError(
                        f"Parameter reference must be '$name', got {v!r}"
                    )
        return v
