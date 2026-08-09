"""Tests for extrude compiler — ExtrudeFeature + Sketch -> CadQuery code."""
import pytest

from extrudely.cfp.features import ExtrudeFeature
from extrudely.cfp.parameters import Parameter
from extrudely.cfp.sketch import Sketch
from extrudely.compiler.errors import CompilerError
from extrudely.compiler.extrude_compiler import compile_extrude


def _mk_sketch(sketch_id="SK001", plane="XY", geometry=None, closed=True):
    return Sketch.model_validate({
        "sketch_id": sketch_id, "plane": plane, "geometry": geometry or [], "closed": closed,
    })

def _mk_feature(feature_id="F001", sketch_id="SK001", distance=10.0, **kwargs):
    return ExtrudeFeature(feature_id=feature_id, sketch_id=sketch_id, distance=distance, **kwargs)

def _mk_param(name, value):
    return Parameter(value=value, cdr_reference=f"DIM_{name}")


class TestBasicExtrude:
    def test_rectangle_extrude(self):
        """Rectangular plate: RECTANGLE sketch + EXTRUDE feature."""
        sk = _mk_sketch(geometry=[
            {"type": "RECTANGLE", "id": "R1", "width": 100, "height": 60, "center": [50, 30]},
        ])
        feat = _mk_feature(distance=10.0)
        code = compile_extrude(feat, sk)
        assert "Workplane" in code
        assert "rect(100.0, 60.0)" in code
        assert "extrude(10.000000)" in code
        assert "# F001: EXTRUDE" in code

    def test_circle_extrude_new_body(self):
        """Circle sketch + EXTRUDE new_body mode."""
        sk = _mk_sketch(geometry=[
            {"type": "CIRCLE", "id": "C1", "center": [0, 0], "radius": 20},
        ])
        feat = _mk_feature(mode="new_body", distance=30)
        code = compile_extrude(feat, sk)
        assert "circle(20" in code
        assert "extrude(30.000000)" in code
        assert "new_body" in code  # should appear in comment

    def test_symmetric_extrude(self):
        """Symmetric extrude uses both=True with half distance."""
        sk = _mk_sketch(geometry=[
            {"type": "RECTANGLE", "id": "R1", "width": 50, "height": 50, "center": [25, 25]},
        ])
        feat = _mk_feature(distance=10.0, symmetric=True)
        code = compile_extrude(feat, sk)
        assert "extrude(5.000000, both=True)" in code
        assert "half=5.000000" in code


class TestParamResolution:
    def test_resolves_param_reference(self):
        """Distance as $param_name is resolved from parameters dict."""
        sk = _mk_sketch(geometry=[
            {"type": "RECTANGLE", "id": "R1", "width": 100, "height": 60, "center": [50, 30]},
        ])
        feat = _mk_feature(distance="$part_height")
        params = {"part_height": _mk_param("part_height", 15.0)}
        code = compile_extrude(feat, sk, parameters=params)
        assert "extrude(15.000000)" in code

    def test_unresolved_param_raises(self):
        """Missing parameter raises CompilerError."""
        sk = _mk_sketch(geometry=[
            {"type": "RECTANGLE", "id": "R1", "width": 100, "height": 60, "center": [50, 30]},
        ])
        feat = _mk_feature(distance="$unknown_param")
        with pytest.raises(CompilerError) as exc:
            compile_extrude(feat, sk, parameters={})
        assert "unresolved_parameter" in str(exc.value)
        assert "unknown_param" in str(exc.value)

    def test_param_with_zero_value_raises(self):
        """Parameter resolved to zero distance triggers invalid_distance error."""
        sk = _mk_sketch(geometry=[
            {"type": "RECTANGLE", "id": "R1", "width": 100, "height": 60, "center": [50, 30]},
        ])
        feat = _mk_feature(distance="$zero_param")
        params = {"zero_param": Parameter(value=0.0, cdr_reference="DIM_X")}
        with pytest.raises(CompilerError) as exc:
            compile_extrude(feat, sk, parameters=params)
        assert "invalid_distance" in str(exc.value)


class TestDeterministic:
    def test_same_input_same_output(self):
        sk = _mk_sketch(geometry=[
            {"type": "RECTANGLE", "id": "R1", "width": 100, "height": 60, "center": [50, 30]},
        ])
        feat = _mk_feature(distance=10.0)
        c1 = compile_extrude(feat, sk)
        c2 = compile_extrude(feat, sk)
        assert c1 == c2

    def test_different_distance_different_output(self):
        sk = _mk_sketch(geometry=[
            {"type": "RECTANGLE", "id": "R1", "width": 100, "height": 60, "center": [50, 30]},
        ])
        f1 = _mk_feature(distance=10.0)
        f2 = _mk_feature(distance=20.0)
        assert compile_extrude(f1, sk) != compile_extrude(f2, sk)

    def test_different_symmetric_different_output(self):
        """Symmetric flag changes output (both=True vs regular)."""
        sk = _mk_sketch(geometry=[
            {"type": "RECTANGLE", "id": "R1", "width": 50, "height": 50, "center": [25, 25]},
        ])
        f1 = _mk_feature(distance=10.0, symmetric=False)
        f2 = _mk_feature(distance=10.0, symmetric=True)
        assert compile_extrude(f1, sk) != compile_extrude(f2, sk)

    def test_different_mode_different_comment(self):
        """Mode appears in comment, so different mode → different output."""
        sk = _mk_sketch(geometry=[
            {"type": "RECTANGLE", "id": "R1", "width": 50, "height": 50, "center": [25, 25]},
        ])
        f1 = _mk_feature(distance=10.0, mode="add")
        f2 = _mk_feature(distance=10.0, mode="new_body")
        assert compile_extrude(f1, sk) != compile_extrude(f2, sk)


class TestErrors:
    def test_zero_distance_raises(self):
        sk = _mk_sketch(geometry=[
            {"type": "RECTANGLE", "id": "R1", "width": 100, "height": 60, "center": [50, 30]},
        ])
        feat = _mk_feature(distance=0.0)
        with pytest.raises(CompilerError) as exc:
            compile_extrude(feat, sk)
        assert "invalid_distance" in str(exc.value)

    def test_negative_distance_raises(self):
        sk = _mk_sketch(geometry=[
            {"type": "RECTANGLE", "id": "R1", "width": 100, "height": 60, "center": [50, 30]},
        ])
        feat = _mk_feature(distance=-5)
        with pytest.raises(CompilerError) as exc:
            compile_extrude(feat, sk)
        assert "invalid_distance" in str(exc.value)

    def test_nan_distance_raises(self):
        sk = _mk_sketch(geometry=[
            {"type": "CIRCLE", "id": "C1", "center": [0, 0], "radius": 10},
        ])
        feat = _mk_feature(distance=float("nan"))
        with pytest.raises(CompilerError) as exc:
            compile_extrude(feat, sk)
        assert "non_finite_distance" in str(exc.value)

    def test_inf_distance_raises(self):
        sk = _mk_sketch(geometry=[
            {"type": "CIRCLE", "id": "C1", "center": [0, 0], "radius": 10},
        ])
        feat = _mk_feature(distance=float("inf"))
        with pytest.raises(CompilerError) as exc:
            compile_extrude(feat, sk)
        assert "non_finite_distance" in str(exc.value)

    def test_zero_direction_raises(self):
        sk = _mk_sketch(geometry=[
            {"type": "CIRCLE", "id": "C1", "center": [0, 0], "radius": 10},
        ])
        feat = _mk_feature(direction=[0.0, 0.0, 0.0], distance=10)
        with pytest.raises(CompilerError) as exc:
            compile_extrude(feat, sk)
        assert "zero_direction" in str(exc.value)

    def test_nan_direction_raises(self):
        """NaN direction rejected at schema level; compiler guards for misuse."""
        sk = _mk_sketch(geometry=[
            {"type": "CIRCLE", "id": "C1", "center": [0, 0], "radius": 10},
        ])
        feat = _mk_feature(distance=10)
        object.__setattr__(feat, "direction", [0.0, 0.0, float("nan")])
        with pytest.raises(CompilerError) as exc:
            compile_extrude(feat, sk)
        assert "non_finite_direction" in str(exc.value)

    def test_unsupported_direction_raises(self):
        """Only +Z extrusion is supported in Phase 1."""
        sk = _mk_sketch(geometry=[
            {"type": "CIRCLE", "id": "C1", "center": [0, 0], "radius": 10},
        ])
        feat = _mk_feature(direction=[1.0, 0.0, 0.0], distance=10)
        with pytest.raises(CompilerError) as exc:
            compile_extrude(feat, sk)
        assert "unsupported_direction" in str(exc.value)

    def test_bad_literal_distance_string_raises(self):
        """Non-numeric, non-$param string raises CompilerError."""
        sk = _mk_sketch(geometry=[
            {"type": "CIRCLE", "id": "C1", "center": [0, 0], "radius": 10},
        ])
        feat = _mk_feature(distance="not_a_number")
        with pytest.raises(CompilerError) as exc:
            compile_extrude(feat, sk)
        assert "invalid_distance_format" in str(exc.value)

    def test_unclosed_profile_raises(self):
        """Sketch without closed=True raises CompilerError."""
        sk = _mk_sketch(closed=False, geometry=[
            {"type": "LINE", "id": "L1", "start": [0, 0], "end": [100, 0]},
        ])
        feat = _mk_feature(distance=10)
        with pytest.raises(CompilerError) as exc:
            compile_extrude(feat, sk)
        assert "unclosed_profile" in str(exc.value)

    def test_sketch_id_mismatch_raises(self):
        """Feature referencing different sketch_id than the one passed raises."""
        sk = _mk_sketch(sketch_id="SK002", geometry=[
            {"type": "CIRCLE", "id": "C1", "center": [0, 0], "radius": 10},
        ])
        feat = _mk_feature(sketch_id="SK001", distance=10)
        with pytest.raises(CompilerError) as exc:
            compile_extrude(feat, sk)
        assert "sketch_id_mismatch" in str(exc.value)

    def test_unsupported_mode_raises(self):
        """Mode can't be anything outside add/new_body (enforced by Pydantic),
        but we test the compiler's own guard for programmatic misuse."""
        sk = _mk_sketch(geometry=[
            {"type": "CIRCLE", "id": "C1", "center": [0, 0], "radius": 10},
        ])
        feat = _mk_feature(distance=10)
        object.__setattr__(feat, "mode", "subtract")
        with pytest.raises(CompilerError) as exc:
            compile_extrude(feat, sk)
        assert "unsupported_mode" in str(exc.value)


class TestSyntaxValidity:
    def test_output_is_valid_python(self):
        sk = _mk_sketch(geometry=[
            {"type": "RECTANGLE", "id": "R1", "width": 100, "height": 60, "center": [50, 30]},
        ])
        feat = _mk_feature(distance=10.0)
        code = compile_extrude(feat, sk)
        compile(code, "<test>", "exec")

    def test_with_param_is_valid_python(self):
        sk = _mk_sketch(geometry=[
            {"type": "RECTANGLE", "id": "R1", "width": 100, "height": 60, "center": [50, 30]},
        ])
        feat = _mk_feature(distance="$height")
        params = {"height": _mk_param("height", 12.0)}
        code = compile_extrude(feat, sk, parameters=params)
        compile(code, "<test>", "exec")
