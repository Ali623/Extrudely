"""Integration tests: compile_extrude -> CadQuery execution -> STEP export.

Per AD-12: Every CFP operation requires CadQuery execution + STEP validity tests.
These tests require cadquery installed; skipped otherwise.
"""
import os
import tempfile

import pytest

cadquery = pytest.importorskip("cadquery")

# E402: imports must be after importorskip to handle missing cadquery gracefully
from extrudely.cfp.features import ExtrudeFeature  # noqa: E402
from extrudely.cfp.sketch import Sketch  # noqa: E402
from extrudely.compiler.extrude_compiler import compile_extrude  # noqa: E402


def _mk_sketch(sketch_id="SK001", plane="XY", geometry=None, closed=False):
    return Sketch.model_validate({
        "sketch_id": sketch_id, "plane": plane, "geometry": geometry or [], "closed": closed,
    })


@pytest.mark.integration
@pytest.mark.slow
class TestExtrudeExecution:
    """Execute generated CadQuery code and verify solid output."""

    def test_rectangular_plate_executes(self):
        """RECTANGLE 100×60mm + EXTRUDE 10mm -> valid solid with correct bounds."""
        sk = _mk_sketch(geometry=[
            {"type": "RECTANGLE", "id": "R1", "width": 100, "height": 60, "center": [50, 30]},
        ], closed=True)
        feat = ExtrudeFeature(feature_id="F001", sketch_id="SK001", distance=10.0)
        code = compile_extrude(feat, sk)

        # Execute generated code
        ns = {}
        exec(code, {"cadquery": cadquery, "cq": cadquery}, ns)
        result = ns.get("result")

        assert result is not None, "Generated code must produce a 'result' variable"
        assert result.val().isValid(), "Result must be a valid solid"

        # Check bounding box: width 100, height 60, depth 10 (Z extrusion)
        bb = result.val().BoundingBox()
        assert bb.xmax - bb.xmin == pytest.approx(100.0, abs=0.1)
        assert bb.ymax - bb.ymin == pytest.approx(60.0, abs=0.1)
        assert bb.zmax - bb.zmin == pytest.approx(10.0, abs=0.1)

    def test_multi_primitive_sketch_executes(self):
        """Custom profile (4 lines) + EXTRUDE -> valid solid."""
        sk = _mk_sketch(geometry=[
            {"type": "LINE", "id": "L1", "start": [0, 0], "end": [40, 0]},
            {"type": "LINE", "id": "L2", "start": [40, 0], "end": [40, 20]},
            {"type": "LINE", "id": "L3", "start": [40, 20], "end": [0, 20]},
            {"type": "LINE", "id": "L4", "start": [0, 20], "end": [0, 0]},
        ], closed=True)
        feat = ExtrudeFeature(feature_id="F001", sketch_id="SK001", distance=15.0)
        code = compile_extrude(feat, sk)

        ns = {}
        exec(code, {"cadquery": cadquery, "cq": cadquery}, ns)
        result = ns.get("result")

        assert result is not None
        assert result.val().isValid()

        bb = result.val().BoundingBox()
        assert bb.xmax - bb.xmin == pytest.approx(40.0, abs=0.1)
        assert bb.ymax - bb.ymin == pytest.approx(20.0, abs=0.1)
        assert bb.zmax - bb.zmin == pytest.approx(15.0, abs=0.1)

    def test_circle_extrude_executes(self):
        """CIRCLE Ø40 + EXTRUDE 30mm -> valid cylindrical solid."""
        sk = _mk_sketch(geometry=[
            {"type": "CIRCLE", "id": "C1", "center": [0, 0], "radius": 20},
        ])
        feat = ExtrudeFeature(feature_id="F001", sketch_id="SK001", distance=30.0)
        code = compile_extrude(feat, sk)

        ns = {}
        exec(code, {"cadquery": cadquery, "cq": cadquery}, ns)
        result = ns.get("result")

        assert result is not None
        assert result.val().isValid()

        bb = result.val().BoundingBox()
        assert bb.xmax - bb.xmin == pytest.approx(40.0, abs=0.1)  # diameter 40
        assert bb.ymax - bb.ymin == pytest.approx(40.0, abs=0.1)
        assert bb.zmax - bb.zmin == pytest.approx(30.0, abs=0.1)

    def test_symmetric_extrude_executes(self):
        """Symmetric extrude: 5mm each side → total 10mm depth."""
        sk = _mk_sketch(geometry=[
            {"type": "RECTANGLE", "id": "R1", "width": 50, "height": 50, "center": [25, 25]},
        ], closed=True)
        feat = ExtrudeFeature(feature_id="F001", sketch_id="SK001", distance=10.0, symmetric=True)
        code = compile_extrude(feat, sk)

        ns = {}
        exec(code, {"cadquery": cadquery, "cq": cadquery}, ns)
        result = ns.get("result")

        assert result is not None
        assert result.val().isValid()

        bb = result.val().BoundingBox()
        # Symmetric: 5mm above XY, 5mm below XY
        assert bb.zmin == pytest.approx(-5.0, abs=0.1)
        assert bb.zmax == pytest.approx(5.0, abs=0.1)
        assert bb.zmax - bb.zmin == pytest.approx(10.0, abs=0.1)


@pytest.mark.integration
@pytest.mark.slow
class TestStepExport:
    """Verify STEP export from generated CadQuery code."""

    def test_export_step_valid(self):
        """Generated solid exports to valid, non-empty STEP file."""
        sk = _mk_sketch(geometry=[
            {"type": "RECTANGLE", "id": "R1", "width": 100, "height": 60, "center": [50, 30]},
        ], closed=True)
        feat = ExtrudeFeature(feature_id="F001", sketch_id="SK001", distance=10.0)
        code = compile_extrude(feat, sk)

        ns = {}
        exec(code, {"cadquery": cadquery, "cq": cadquery}, ns)
        result = ns.get("result")
        assert result is not None

        with tempfile.TemporaryDirectory() as tmpdir:
            step_path = os.path.join(tmpdir, "test.step")
            cadquery.exporters.export(result.val(), step_path)

            assert os.path.isfile(step_path), "STEP file must exist"
            assert os.path.getsize(step_path) > 0, "STEP file must be non-empty"

            # Re-import and verify it's still a valid solid
            imported = cadquery.importers.importStep(step_path)
            assert imported is not None
            assert imported.val().isValid()

            # Volume should match (±0.1%)
            orig_vol = result.val().Volume()
            imported_vol = imported.val().Volume()
            assert imported_vol == pytest.approx(orig_vol, rel=0.001)
