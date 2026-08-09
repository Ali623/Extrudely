"""CFP sketch models — 2D sketch geometry, primitives, and constraints."""
from typing import Annotated, Literal

from pydantic import BaseModel, Field

from extrudely.cfp.enums import ConstraintTypeEnum, SketchPlaneEnum


class LinePrimitive(BaseModel):
    type: Literal["LINE"] = "LINE"
    id: str = Field(..., description="Entity identifier within sketch")
    start: list[float] = Field(..., min_length=2, max_length=2, description="[x, y]")
    end: list[float] = Field(..., min_length=2, max_length=2, description="[x, y]")
    model_config = {"extra": "forbid"}

class ArcPrimitive(BaseModel):
    type: Literal["ARC"] = "ARC"
    id: str = Field(..., description="Entity identifier within sketch")
    center: list[float] = Field(..., min_length=2, max_length=2, description="[x, y]")
    radius: float = Field(..., gt=0)
    start_angle: float = Field(..., description="Start angle in degrees")
    end_angle: float = Field(..., description="End angle in degrees")
    model_config = {"extra": "forbid"}

class CirclePrimitive(BaseModel):
    type: Literal["CIRCLE"] = "CIRCLE"
    id: str = Field(..., description="Entity identifier within sketch")
    center: list[float] = Field(..., min_length=2, max_length=2, description="[x, y]")
    radius: float = Field(..., gt=0)
    model_config = {"extra": "forbid"}

class RectanglePrimitive(BaseModel):
    type: Literal["RECTANGLE"] = "RECTANGLE"
    id: str = Field(..., description="Entity identifier within sketch")
    width: float = Field(..., gt=0)
    height: float = Field(..., gt=0)
    center: list[float] = Field(..., min_length=2, max_length=2, description="[x, y]")
    model_config = {"extra": "forbid"}

class PolylinePrimitive(BaseModel):
    type: Literal["POLYLINE"] = "POLYLINE"
    id: str = Field(..., description="Entity identifier within sketch")
    points: list[list[float]] = Field(..., min_length=2, description="List of [x, y] points")
    model_config = {"extra": "forbid"}

SketchPrimitive = Annotated[
    LinePrimitive | ArcPrimitive | CirclePrimitive | RectanglePrimitive | PolylinePrimitive,
    Field(discriminator="type"),
]

class SketchConstraint(BaseModel):
    constraint_id: str = Field(..., description="Constraint identifier")
    constraint_type: ConstraintTypeEnum
    entities: list[str] = Field(..., min_length=1, description="Entity IDs for this constraint")
    value: float | None = Field(default=None, description="Value for dimensional constraints")
    model_config = {"extra": "forbid"}

class Sketch(BaseModel):
    sketch_id: str = Field(..., description="Sketch identifier, e.g. SK001")
    plane: SketchPlaneEnum
    origin: list[float] = Field(default=[0, 0, 0], min_length=3, max_length=3)
    geometry: list[SketchPrimitive] = Field(default_factory=list)
    constraints: list[SketchConstraint] = Field(default_factory=list)
    cdr_references: list[str] = Field(default_factory=list, description="CDR profile/primitive IDs")
    closed: bool = Field(default=False, description="Whether the profile forms a closed loop")
    model_config = {"extra": "forbid"}
