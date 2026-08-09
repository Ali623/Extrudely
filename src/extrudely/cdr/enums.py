"""CDR enum types — input, view, source, status, line style, and processing mode enums."""

from enum import StrEnum


class InputTypeEnum(StrEnum):
    """Supported drawing input formats."""

    PNG = "PNG"
    JPEG = "JPEG"
    PDF_RASTER = "PDF_RASTER"
    PDF_VECTOR = "PDF_VECTOR"
    PDF_HYBRID = "PDF_HYBRID"
    DXF = "DXF"
    SVG = "SVG"


class ProcessingModeEnum(StrEnum):
    """Pipeline processing mode."""

    RASTER = "raster"
    VECTOR = "vector"
    HYBRID = "hybrid"


class ViewTypeEnum(StrEnum):
    """Orthographic view types supported in POC 1."""

    FRONT = "front"
    TOP = "top"
    LEFT = "left"
    RIGHT = "right"
    SECTION = "section"
    UNKNOWN = "unknown"


class SourceTypeEnum(StrEnum):
    """Evidence source types for provenance tracking."""

    RASTER_GEOMETRY = "raster_geometry"
    VECTOR_GEOMETRY = "vector_geometry"
    OCR = "ocr"
    TITLE_BLOCK = "title_block"
    DIMENSION_ENTITY = "dimension_entity"
    VLM = "vlm"
    CROSS_VIEW_REASONING = "cross_view_reasoning"
    GEOMETRY_RULE = "geometry_rule"
    USER = "user"


class StatusEnum(StrEnum):
    """Field value status — distinguishes observed from inferred from user-corrected."""

    OBSERVED = "observed"
    INFERRED = "inferred"
    USER_CONFIRMED = "user_confirmed"
    USER_CORRECTED = "user_corrected"
    CONFLICTED = "conflicted"
    UNKNOWN = "unknown"


class LineStyleEnum(StrEnum):
    """Engineering line style for geometric primitives."""

    VISIBLE = "visible"
    HIDDEN = "hidden"
    CENTER = "center"
    CONSTRUCTION = "construction"
    DIMENSION = "dimension"
    EXTENSION = "extension"
    SECTION = "section"
    UNKNOWN = "unknown"
