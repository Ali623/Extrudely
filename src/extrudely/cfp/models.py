"""CFP top-level models — CADFeaturePlan and PlanMetadata."""
from pydantic import BaseModel, Field

from extrudely.cfp.enums import PlanStatusEnum, SketchPlaneEnum
from extrudely.cfp.parameters import Parameter
from extrudely.cfp.sketch import Sketch


class PlanMetadata(BaseModel):
    coordinate_system: dict = Field(
        default_factory=lambda: {"X": "width", "Y": "depth", "Z": "height"},
        description="Global coordinate convention per CFP spec §5",
    )
    default_sketch_plane: SketchPlaneEnum = Field(
        default=SketchPlaneEnum.XY, description="Default sketch plane per CFP spec §13"
    )
    model_config = {"extra": "forbid"}

class CADFeaturePlan(BaseModel):
    plan_id: str = Field(..., description="Unique plan identifier, e.g. CFP_001")
    version: str = Field(default="0.1", description="CFP schema version")
    document_id: str = Field(..., description="Source CDR document ID")
    status: PlanStatusEnum = Field(default=PlanStatusEnum.CANDIDATE)
    metadata: PlanMetadata = Field(default_factory=PlanMetadata)
    parameters: dict[str, Parameter] = Field(default_factory=dict)
    sketches: list[Sketch] = Field(default_factory=list)
    features: list[dict] = Field(default_factory=list, description="Features (typed later)")
    assumptions: list[dict] = Field(default_factory=list)
    validation_targets: list[dict] = Field(default_factory=list)
    model_config = {"extra": "forbid"}
