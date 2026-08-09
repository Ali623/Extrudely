"""CDR confidence field wrapper — reusable Pydantic generic for all uncertain values.

Per AD-5: Every inferred value carries confidence and provenance.
Per AD-6: Unknown values serialize as value=null, confidence=0.0, status=unknown.
"""

from typing import Generic, TypeVar

from pydantic import BaseModel, Field

from extrudely.cdr.enums import StatusEnum

T = TypeVar("T")


class ConfidenceValue(BaseModel, Generic[T]):
    """Standard field wrapper for all CDR values that carry confidence and provenance.

    Generic over T so that ConfidenceValue[str] and ConfidenceValue[float] carry
    different type safety.
    """

    value: T | None = Field(
        default=None,
        description="The field value. None when status is unknown.",
    )
    confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Confidence in [0.0, 1.0]. 0.0 means no confidence / unknown.",
    )
    status: StatusEnum = Field(
        default=StatusEnum.UNKNOWN,
        description="Provenance status of this value.",
    )
    evidence_ids: list[str] = Field(
        default_factory=list,
        description="References to Evidence objects supporting this value.",
    )

    model_config = {"extra": "forbid"}
