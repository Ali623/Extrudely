"""Integration test for CFP module imports."""
def test_all_public_types_importable():
    pass

def test_cfp_and_cdr_modules_import_independently():
    from extrudely.cdr import DrawingDocument
    from extrudely.cfp import CADFeaturePlan
    assert DrawingDocument is not None
    assert CADFeaturePlan is not None
