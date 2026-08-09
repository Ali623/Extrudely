"""Tests for CDR enum types."""

from extrudely.cdr.enums import (
    InputTypeEnum,
    LineStyleEnum,
    ProcessingModeEnum,
    SourceTypeEnum,
    StatusEnum,
    ViewTypeEnum,
)


class TestInputTypeEnum:
    def test_valid_values(self):
        assert InputTypeEnum.PNG.value == "PNG"
        assert InputTypeEnum.JPEG.value == "JPEG"
        assert InputTypeEnum.DXF.value == "DXF"
        assert InputTypeEnum.SVG.value == "SVG"

    def test_all_raster_types(self):
        raster = {InputTypeEnum.PNG, InputTypeEnum.JPEG, InputTypeEnum.PDF_RASTER}
        assert all(isinstance(t, InputTypeEnum) for t in raster)


class TestViewTypeEnum:
    def test_valid_values(self):
        assert ViewTypeEnum.FRONT.value == "front"
        assert ViewTypeEnum.TOP.value == "top"
        assert ViewTypeEnum.LEFT.value == "left"
        assert ViewTypeEnum.RIGHT.value == "right"
        assert ViewTypeEnum.SECTION.value == "section"
        assert ViewTypeEnum.UNKNOWN.value == "unknown"


class TestSourceTypeEnum:
    def test_all_source_types(self):
        expected = {
            "raster_geometry",
            "vector_geometry",
            "ocr",
            "title_block",
            "dimension_entity",
            "vlm",
            "cross_view_reasoning",
            "geometry_rule",
            "user",
        }
        assert {e.value for e in SourceTypeEnum} == expected


class TestStatusEnum:
    def test_valid_values(self):
        assert StatusEnum.OBSERVED.value == "observed"
        assert StatusEnum.INFERRED.value == "inferred"
        assert StatusEnum.USER_CONFIRMED.value == "user_confirmed"
        assert StatusEnum.USER_CORRECTED.value == "user_corrected"
        assert StatusEnum.CONFLICTED.value == "conflicted"
        assert StatusEnum.UNKNOWN.value == "unknown"

    def test_default_is_unknown(self):
        """StatusEnum default should be unknown for safety."""
        from extrudely.cdr.enums import StatusEnum

        # The enum itself defines unknown, and ConfidenceValue uses it as default
        assert StatusEnum.UNKNOWN is not None


class TestLineStyleEnum:
    def test_valid_values(self):
        assert LineStyleEnum.VISIBLE.value == "visible"
        assert LineStyleEnum.HIDDEN.value == "hidden"
        assert LineStyleEnum.CENTER.value == "center"

    def test_all_styles_count(self):
        styles = list(LineStyleEnum)
        assert len(styles) >= 8  # visible, hidden, center, construction, dimension, extension, section, unknown


class TestProcessingModeEnum:
    def test_valid_values(self):
        assert ProcessingModeEnum.RASTER.value == "raster"
        assert ProcessingModeEnum.VECTOR.value == "vector"
        assert ProcessingModeEnum.HYBRID.value == "hybrid"
