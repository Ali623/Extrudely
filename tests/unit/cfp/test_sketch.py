"""Tests for CFP Sketch models."""
import pytest

from extrudely.cfp.enums import ConstraintTypeEnum, SketchPlaneEnum
from extrudely.cfp.sketch import (
    ArcPrimitive,
    CirclePrimitive,
    LinePrimitive,
    PolylinePrimitive,
    RectanglePrimitive,
    Sketch,
    SketchConstraint,
)


class TestLinePrimitive:
    def test_valid_line(self):
        line_prim = LinePrimitive.model_validate({"id": "L1", "start": [0, 0], "end": [100, 0]})
        assert line_prim.type == "LINE"
        assert line_prim.start == [0, 0]

    def test_rejects_missing_end(self):
        with pytest.raises(ValueError):
            LinePrimitive.model_validate({"id": "L1", "start": [0, 0]})

class TestArcPrimitive:
    def test_valid_arc(self):
        a = ArcPrimitive.model_validate({
            "id": "A1","center":[50,0],"radius":25.0,"start_angle":0,"end_angle":180
        })
        assert a.type == "ARC"
        assert a.radius == 25.0

class TestCirclePrimitive:
    def test_valid_circle(self):
        c = CirclePrimitive.model_validate({"id": "C1", "center": [50, 50], "radius": 20.0})
        assert c.type == "CIRCLE"

class TestRectanglePrimitive:
    def test_valid_rectangle(self):
        r = RectanglePrimitive.model_validate({"id": "R1", "width": 100, "height": 60, "center": [50, 30]})
        assert r.type == "RECTANGLE"
        assert r.width == 100

class TestPolylinePrimitive:
    def test_valid_polyline(self):
        p = PolylinePrimitive.model_validate({"id": "P1", "points": [[0, 0], [10, 0], [10, 10]]})
        assert p.type == "POLYLINE"
        assert len(p.points) == 3

    def test_rejects_single_point(self):
        with pytest.raises(ValueError):
            PolylinePrimitive.model_validate({"id": "P1", "points": [[0, 0]]})

class TestSketchConstraint:
    def test_horizontal_constraint(self):
        c = SketchConstraint.model_validate({
            "constraint_id": "C001", "constraint_type": "horizontal", "entities": ["L1"],
        })
        assert c.constraint_type == ConstraintTypeEnum.HORIZONTAL

    def test_distance_constraint_with_value(self):
        c = SketchConstraint.model_validate({
            "constraint_id": "C002", "constraint_type": "distance", "entities": ["L1", "L2"], "value": 50.0,
        })
        assert c.value == 50.0

class TestSketch:
    def test_minimal_sketch(self):
        s = Sketch.model_validate({"sketch_id": "SK001", "plane": "XY"})
        assert s.sketch_id == "SK001"
        assert s.geometry == []
        assert s.constraints == []

    def test_sketch_with_geometry(self):
        s = Sketch.model_validate({
            "sketch_id": "SK001",
            "plane": "XY",
            "origin": [0, 0, 0],
            "geometry": [
                {"type": "LINE", "id": "L1", "start": [0, 0], "end": [100, 0]},
                {"type": "CIRCLE", "id": "C1", "center": [50, 50], "radius": 20},
            ],
            "closed": True,
        })
        assert len(s.geometry) == 2
        assert s.geometry[0].type == "LINE"
        assert s.geometry[1].type == "CIRCLE"

    def test_full_sketch(self):
        s = Sketch.model_validate({
            "sketch_id": "SK002",
            "plane": "XZ",
            "origin": [0, 0, 10],
            "geometry": [
                {"type": "RECTANGLE", "id": "R1", "width": 100, "height": 60, "center": [50, 30]},
            ],
            "constraints": [
                {"constraint_id": "C001", "constraint_type": "horizontal", "entities": ["R1"]},
            ],
            "cdr_references": ["PROFILE_001"],
            "closed": True,
        })
        assert s.plane == SketchPlaneEnum.XZ
        assert len(s.constraints) == 1

    def test_wrong_discriminator_rejected(self):
        with pytest.raises(ValueError):
            Sketch.model_validate({
                "sketch_id": "SK003",
                "plane": "XY",
                "geometry": [{"type": "BOGUS", "id": "X1"}],
            })
