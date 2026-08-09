"""Tests for sketch compiler — CF Sketch -> CadQuery code generation."""
import pytest

from extrudely.cfp.sketch import Sketch
from extrudely.compiler.errors import CompilerError
from extrudely.compiler.sketch_compiler import compile_sketch


def _mk_sketch(sketch_id="SK001", plane="XY", geometry=None, closed=False):
    return Sketch.model_validate({
        "sketch_id": sketch_id, "plane": plane, "geometry": geometry or [], "closed": closed,
    })

class TestLinePrimitive:
    def test_single_line(self):
        s = _mk_sketch(geometry=[{"type": "LINE", "id": "L1", "start": [0, 0], "end": [100, 0]}])
        code = compile_sketch(s)
        assert "Workplane" in code
        assert "moveTo(0.0, 0.0)" in code
        assert "lineTo(100.0, 0.0)" in code

    def test_two_lines(self):
        s = _mk_sketch(geometry=[
            {"type": "LINE", "id": "L1", "start": [0, 0], "end": [100, 0]},
            {"type": "LINE", "id": "L2", "start": [100, 0], "end": [100, 60]},
        ], closed=True)
        code = compile_sketch(s)
        assert "close()" in code

class TestCirclePrimitive:
    def test_circle(self):
        s = _mk_sketch(geometry=[{"type": "CIRCLE", "id": "C1", "center": [50, 50], "radius": 20}])
        code = compile_sketch(s)
        assert "circle(20" in code

class TestRectanglePrimitive:
    def test_rectangle(self):
        s = _mk_sketch(geometry=[{"type": "RECTANGLE", "id": "R1", "width": 100, "height": 60, "center": [50, 30]}])
        code = compile_sketch(s)
        assert "rect(100.0, 60.0)" in code

class TestArcPrimitive:
    def test_arc(self):
        s = _mk_sketch(geometry=[{
            "type": "ARC", "id": "A1",
            "center": [50, 0], "radius": 25,
            "start_angle": 0, "end_angle": 180,
        }])
        code = compile_sketch(s)
        assert "threePointArc" in code

class TestPolylinePrimitive:
    def test_polyline(self):
        s = _mk_sketch(geometry=[{
            "type": "POLYLINE", "id": "P1",
            "points": [[0, 0], [10, 0], [10, 10], [0, 10]],
        }], closed=True)
        code = compile_sketch(s)
        assert "moveTo(0.0, 0.0)" in code
        assert "close()" in code

class TestDeterministic:
    def test_same_input_same_output(self):
        s = _mk_sketch(geometry=[{"type": "LINE", "id": "L1", "start": [0, 0], "end": [100, 0]}])
        code1 = compile_sketch(s)
        code2 = compile_sketch(s)
        assert code1 == code2

    def test_different_input_different_output(self):
        s1 = _mk_sketch(sketch_id="SK001", geometry=[{"type": "LINE", "id": "L1", "start": [0, 0], "end": [10, 0]}])
        s2 = _mk_sketch(sketch_id="SK002", geometry=[{"type": "LINE", "id": "L1", "start": [0, 0], "end": [20, 0]}])
        assert compile_sketch(s1) != compile_sketch(s2)

class TestPlanes:
    def test_xy_plane(self):
        s = _mk_sketch(plane="XY", geometry=[{"type": "CIRCLE", "id": "C1", "center": [0, 0], "radius": 10}])
        code = compile_sketch(s)
        assert 'Workplane("XY")' in code

    def test_xz_plane(self):
        s = _mk_sketch(plane="XZ", geometry=[{"type": "CIRCLE", "id": "C1", "center": [0, 0], "radius": 10}])
        code = compile_sketch(s)
        assert 'Workplane("XZ")' in code

    def test_yz_plane(self):
        s = _mk_sketch(plane="YZ", geometry=[{"type": "CIRCLE", "id": "C1", "center": [0, 0], "radius": 10}])
        code = compile_sketch(s)
        assert 'Workplane("YZ")' in code

class TestErrors:
    def test_unsupported_plane(self):
        s = _mk_sketch(geometry=[{"type": "CIRCLE", "id": "C1", "center": [0, 0], "radius": 10}])
        object.__setattr__(s, "plane", "BOGUS")
        with pytest.raises(CompilerError) as exc:
            compile_sketch(s)
        assert "unsupported_plane" in str(exc.value)

    def test_empty_geometry(self):
        s = _mk_sketch()
        with pytest.raises(CompilerError) as exc:
            compile_sketch(s)
        assert "empty_geometry" in str(exc.value)

    def test_unknown_type(self):
        s = _mk_sketch(geometry=[{"type": "CIRCLE", "id": "C1", "center": [0, 0], "radius": 10}])
        s.geometry[0].type = "BOGUS"
        with pytest.raises(CompilerError) as exc:
            compile_sketch(s)
        assert "unknown_primitive" in str(exc.value)

class TestFullSketch:
    def test_complex_sketch(self):
        s = _mk_sketch(geometry=[
            {"type": "LINE", "id": "L1", "start": [0, 0], "end": [100, 0]},
            {"type": "LINE", "id": "L2", "start": [100, 0], "end": [100, 60]},
            {"type": "LINE", "id": "L3", "start": [100, 60], "end": [0, 60]},
            {"type": "LINE", "id": "L4", "start": [0, 60], "end": [0, 0]},
        ], closed=True)
        code = compile_sketch(s)
        assert "Workplane" in code
        assert "close()" in code
        assert code.count("lineTo") == 4

class TestSyntaxValidity:
    def test_output_is_valid_python(self):
        s = _mk_sketch(geometry=[
            {"type": "RECTANGLE", "id": "R1", "width": 100, "height": 60, "center": [50, 30]},
        ])
        code = compile_sketch(s)
        compile(code, "<test>", "exec")
