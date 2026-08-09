"""Integration test for CDR module imports and re-exports."""



def test_all_public_types_importable():
    """Verify that every public type is importable from extrudely.cdr."""
    from extrudely.cdr import (  # noqa: F401
        ConfidenceValue,
        CoordinateFrame,
        DrawingDocument,
        DrawingMetadata,
        DrawingView,
        EngineeringCoordinate,
        Evidence,
        InputTypeEnum,
        LineStyleEnum,
        NormalizedCoordinate,
        PixelCoordinate,
        ProcessingModeEnum,
        SectionView,
        SourceFile,
        SourceTypeEnum,
        StatusEnum,
        ViewTypeEnum,
    )
    # If we get here without ImportError, the test passes


def test_convenience_imports():
    """Common import paths work."""
    from extrudely.cdr import ConfidenceValue, DrawingDocument, Evidence  # noqa: F401


def test_package_is_cdr():
    import extrudely.cdr as cdr
    assert cdr.__name__ == "extrudely.cdr"
