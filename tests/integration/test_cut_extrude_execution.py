"""Integration tests: compile_cut_extrude -> CadQuery execution -> STEP export.

Per AD-12: Every CFP operation requires CadQuery execution + STEP validity tests.
These tests require cadquery installed; skipped otherwise.
"""
import os
import tempfile

import pytest

cadquery = pytest.importorskip("cadquery")

# E402: imports must be after importorskip to handle missing cadquery gracefully
from extrudely.cfp.features import CutExtrudeFeature, ExtrudeFeature  # noqa: E402
from extrudely.cfp.sketch import Sketch  # noqa: E402
from extrudely.compiler.cut_extrude_compiler import compile_cut_extrude  # noqa: E402
from extrudely.compiler.extrude_compiler import compile_extrude  # noqa: E402


def _mk_sketch(sketch_id="SK001", plane="XY", geometry=None, closed=True):
    return Sketch.model_validate({
        "sketch_id": sketch_id, "plane": plane, "geometry": geometry or [], "closed": closed,
    })


_preamble = "import cadquery as cq\n"


def _exec_code(code: str) -> object:
    """Execute generated code and return the result object."""
    ns = {}
    exec(_preamble + code, ns)
    return ns.get("result")


@pytest.mark.integration
@pytest.mark.slow
class TestCutExtrudeExecution:
    """Execute generated CadQuery code with both EXTRUDE + CUT_EXTRUDE."""

    def test_block_with_blind_rectangular_pocket(self):
        """EXTRUDE 100×60×20 block + CUT_EXTRUDE 50×30 blind pocket 10mm deep."""
        # F001: base block
        sk1 = _mk_sketch(sketch_id="SK001", geometry=[
            {"type": "RECTANGLE", "id": "R1", "width": 100, "height": 60, "center": [50, 30]},
        ])
        feat1 = ExtrudeFeature(feature_id="F001", sketch_id="SK001", distance=20.0)
        code1 = compile_extrude(feat1, sk1)

        # F002: blind pocket from top
        sk2 = _mk_sketch(sketch_id="SK002", geometry=[
            {"type": "RECTANGLE", "id": "R2", "width": 50, "height": 30, "center": [25, 15]},
        ])
        feat2 = CutExtrudeFeature(feature_id="F002", sketch_id="SK002", target="F001", depth=10.0)
        code2 = compile_cut_extrude(feat2, sk2)

        full_code = code1 + code2
        result = _exec_code(full_code)

        assert result is not None, "Generated code must produce a 'result' variable"
        assert result.val().isValid(), "Result must be a valid solid"

        bb = result.val().BoundingBox()
        assert bb.xmax - bb.xmin == pytest.approx(100.0, abs=0.1)
        assert bb.ymax - bb.ymin == pytest.approx(60.0, abs=0.1)
        assert bb.zmax - bb.zmin == pytest.approx(20.0, abs=0.1)
        # Volume should be block minus pocket: 100*60*20 - 50*30*10 = 105000
        assert result.val().Volume() == pytest.approx(105000.0, rel=0.001)

    def test_block_with_through_cut(self):
        """EXTRUDE block + CUT_EXTRUDE through_all circular hole."""
        sk1 = _mk_sketch(sketch_id="SK001", geometry=[
            {"type": "RECTANGLE", "id": "R1", "width": 100, "height": 60, "center": [50, 30]},
        ])
        feat1 = ExtrudeFeature(feature_id="F001", sketch_id="SK001", distance=20.0)
        code1 = compile_extrude(feat1, sk1)

        sk2 = _mk_sketch(sketch_id="SK002", geometry=[
            {"type": "CIRCLE", "id": "C1", "center": [50, 30], "radius": 15},
        ])
        feat2 = CutExtrudeFeature(
            feature_id="F002", sketch_id="SK002", target="F001",
            depth=10.0, termination="through_all",
        )
        code2 = compile_cut_extrude(feat2, sk2)

        full_code = code1 + code2
        result = _exec_code(full_code)

        assert result is not None
        assert result.val().isValid()

        bb = result.val().BoundingBox()
        assert bb.xmax - bb.xmin == pytest.approx(100.0, abs=0.1)
        assert bb.ymax - bb.ymin == pytest.approx(60.0, abs=0.1)
        assert bb.zmax - bb.zmin == pytest.approx(20.0, abs=0.1)

@pytest.mark.integration
@pytest.mark.slow
class TestCutExtrudeStepExport:
    """Verify STEP export from generated CadQuery code with cut features."""

    def test_export_step_with_pocket(self):
        """EXTRUDE + CUT_EXTRUDE → valid STEP export."""
        sk1 = _mk_sketch(sketch_id="SK001", geometry=[
            {"type": "RECTANGLE", "id": "R1", "width": 100, "height": 60, "center": [50, 30]},
        ])
        feat1 = ExtrudeFeature(feature_id="F001", sketch_id="SK001", distance=20.0)
        code1 = compile_extrude(feat1, sk1)

        sk2 = _mk_sketch(sketch_id="SK002", geometry=[
            {"type": "RECTANGLE", "id": "R2", "width": 50, "height": 30, "center": [25, 15]},
        ])
        feat2 = CutExtrudeFeature(feature_id="F002", sketch_id="SK002", target="F001", depth=10.0)
        code2 = compile_cut_extrude(feat2, sk2)

        result = _exec_code(code1 + code2)
        assert result is not None

        with tempfile.TemporaryDirectory() as tmpdir:
            step_path = os.path.join(tmpdir, "test_pocket.step")
            cadquery.exporters.export(result.val(), step_path)

            assert os.path.isfile(step_path), "STEP file must exist"
            assert os.path.getsize(step_path) > 0, "STEP file must be non-empty"

            imported = cadquery.importers.importStep(step_path)
            assert imported is not None
            assert imported.val().isValid()

            orig_vol = result.val().Volume()
            imported_vol = imported.val().Volume()
            assert imported_vol == pytest.approx(orig_vol, rel=0.001)
