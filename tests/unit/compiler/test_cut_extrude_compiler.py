"""Tests for cut-extrude compiler — CutExtrudeFeature + Sketch -> CadQuery code."""
import pytest

from extrudely.cfp.features import CutExtrudeFeature
from extrudely.cfp.parameters import Parameter
from extrudely.cfp.sketch import Sketch
from extrudely.compiler.cut_extrude_compiler import compile_cut_extrude
from extrudely.compiler.errors import CompilerError


def _mk_sketch(sketch_id="SK002", plane="XY", geometry=None, closed=True):
    return Sketch.model_validate({
        "sketch_id": sketch_id, "plane": plane, "geometry": geometry or [], "closed": closed,
    })

def _mk_feature(feature_id="F002", sketch_id="SK002", target="F001", depth=10.0, **kwargs):
    return CutExtrudeFeature(
        feature_id=feature_id, sketch_id=sketch_id, target=target, depth=depth, **kwargs
    )

def _mk_param(name, value):
    return Parameter(value=value, cdr_reference=f"DIM_{name}")


class TestBasicCutExtrude:
    def test_blind_pocket_down(self):
        """RECTANGLE pocket 50×30mm, 10mm deep from top face."""
        sk = _mk_sketch(geometry=[
            {"type": "RECTANGLE", "id": "R1", "width": 50, "height": 30, "center": [25, 15]},
        ])
        feat = _mk_feature(depth=10.0)
        code = compile_cut_extrude(feat, sk)
        assert 'faces(">Z").workplane()' in code
        assert "cutBlind(-10.000000)" in code
        assert "# F002: CUT_EXTRUDE" in code

    def test_through_all(self):
        """Through-all cut: cutThruAll() with no depth."""
        sk = _mk_sketch(geometry=[
            {"type": "CIRCLE", "id": "C1", "center": [0, 0], "radius": 15},
        ])
        feat = _mk_feature(depth=10.0, termination="through_all")
        code = compile_cut_extrude(feat, sk)
        assert "cutThruAll()" in code
        assert "cutBlind" not in code

    def test_cut_up_from_bottom_rejected(self):
        """Direction [0,0,1] rejected — only -Z supported in Phase 1."""
        sk = _mk_sketch(geometry=[
            {"type": "RECTANGLE", "id": "R1", "width": 50, "height": 30, "center": [25, 15]},
        ])
        feat = _mk_feature(direction=[0, 0, 1], depth=8.0)
        with pytest.raises(CompilerError) as exc:
            compile_cut_extrude(feat, sk)
        assert "unsupported_direction" in str(exc.value)


class TestParamResolution:
    def test_resolves_param_reference(self):
        sk = _mk_sketch(geometry=[
            {"type": "RECTANGLE", "id": "R1", "width": 50, "height": 30, "center": [25, 15]},
        ])
        feat = _mk_feature(depth="$pocket_depth")
        params = {"pocket_depth": _mk_param("pocket_depth", 12.0)}
        code = compile_cut_extrude(feat, sk, parameters=params)
        assert "cutBlind(-12.000000)" in code

    def test_unresolved_param_raises(self):
        sk = _mk_sketch(geometry=[
            {"type": "RECTANGLE", "id": "R1", "width": 50, "height": 30, "center": [25, 15]},
        ])
        feat = _mk_feature(depth="$unknown")
        with pytest.raises(CompilerError) as exc:
            compile_cut_extrude(feat, sk, parameters={})
        assert "unresolved_parameter" in str(exc.value)


class TestDeterministic:
    def test_same_input_same_output(self):
        sk = _mk_sketch(geometry=[
            {"type": "RECTANGLE", "id": "R1", "width": 50, "height": 30, "center": [25, 15]},
        ])
        feat = _mk_feature(depth=10.0)
        assert compile_cut_extrude(feat, sk) == compile_cut_extrude(feat, sk)

    def test_different_termination_different_output(self):
        sk = _mk_sketch(geometry=[
            {"type": "RECTANGLE", "id": "R1", "width": 50, "height": 30, "center": [25, 15]},
        ])
        f1 = _mk_feature(depth=10.0, termination="blind")
        f2 = _mk_feature(depth=10.0, termination="through_all")
        assert compile_cut_extrude(f1, sk) != compile_cut_extrude(f2, sk)


class TestErrors:
    def test_unsupported_x_direction_raises(self):
        sk = _mk_sketch(geometry=[
            {"type": "CIRCLE", "id": "C1", "center": [0, 0], "radius": 10},
        ])
        feat = _mk_feature(direction=[1.0, 0.0, 0.0], depth=10)
        with pytest.raises(CompilerError) as exc:
            compile_cut_extrude(feat, sk)
        assert "unsupported_direction" in str(exc.value)

    def test_zero_direction_raises(self):
        sk = _mk_sketch(geometry=[
            {"type": "CIRCLE", "id": "C1", "center": [0, 0], "radius": 10},
        ])
        feat = _mk_feature(direction=[0.0, 0.0, 0.0], depth=10)
        with pytest.raises(CompilerError) as exc:
            compile_cut_extrude(feat, sk)
        assert "zero_direction" in str(exc.value)

    def test_nan_direction_raises(self):
        sk = _mk_sketch(geometry=[
            {"type": "CIRCLE", "id": "C1", "center": [0, 0], "radius": 10},
        ])
        feat = _mk_feature(depth=10)
        object.__setattr__(feat, "direction", [0.0, 0.0, float("nan")])
        with pytest.raises(CompilerError) as exc:
            compile_cut_extrude(feat, sk)
        assert "non_finite_direction" in str(exc.value)

    def test_zero_depth_raises(self):
        sk = _mk_sketch(geometry=[
            {"type": "RECTANGLE", "id": "R1", "width": 50, "height": 30, "center": [25, 15]},
        ])
        feat = _mk_feature(depth=0.0)
        with pytest.raises(CompilerError) as exc:
            compile_cut_extrude(feat, sk)
        assert "invalid_depth" in str(exc.value)

    def test_nan_depth_raises(self):
        sk = _mk_sketch(geometry=[
            {"type": "CIRCLE", "id": "C1", "center": [0, 0], "radius": 10},
        ])
        feat = _mk_feature(depth=float("nan"))
        with pytest.raises(CompilerError) as exc:
            compile_cut_extrude(feat, sk)
        assert "non_finite_depth" in str(exc.value)

    def test_unclosed_profile_raises(self):
        sk = _mk_sketch(closed=False, geometry=[
            {"type": "LINE", "id": "L1", "start": [0, 0], "end": [50, 0]},
        ])
        feat = _mk_feature(depth=10)
        with pytest.raises(CompilerError) as exc:
            compile_cut_extrude(feat, sk)
        assert "unclosed_profile" in str(exc.value)

    def test_sketch_id_mismatch_raises(self):
        sk = _mk_sketch(sketch_id="SK999", geometry=[
            {"type": "CIRCLE", "id": "C1", "center": [0, 0], "radius": 10},
        ])
        feat = _mk_feature(sketch_id="SK002", depth=10)
        with pytest.raises(CompilerError) as exc:
            compile_cut_extrude(feat, sk)
        assert "sketch_id_mismatch" in str(exc.value)


class TestSyntaxValidity:
    def test_blind_output_is_valid_python(self):
        sk = _mk_sketch(geometry=[
            {"type": "RECTANGLE", "id": "R1", "width": 50, "height": 30, "center": [25, 15]},
        ])
        feat = _mk_feature(depth=10.0)
        compile(compile_cut_extrude(feat, sk), "<test>", "exec")

    def test_through_all_output_is_valid_python(self):
        sk = _mk_sketch(geometry=[
            {"type": "RECTANGLE", "id": "R1", "width": 50, "height": 30, "center": [25, 15]},
        ])
        feat = _mk_feature(depth=10.0, termination="through_all")
        compile(compile_cut_extrude(feat, sk), "<test>", "exec")
