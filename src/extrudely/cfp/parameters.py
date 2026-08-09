"""CFP parameter model — named dimensions with provenance, referenced via $param_name syntax."""
from pydantic import BaseModel, Field


class Parameter(BaseModel):
    value: float = Field(..., description="Parameter value in internal units (mm per AD-9)")
    unit: str = Field(default="mm", description="Unit (mm for length, deg for angle)")
    cdr_reference: str | None = Field(default=None, description="CDR dimension ID, e.g. DIM_001")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Confidence in [0.0, 1.0]")
    status: str = Field(default="observed", description="Provenance status")

    model_config = {"extra": "forbid"}
