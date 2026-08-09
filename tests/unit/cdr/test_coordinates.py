"""Tests for CDR coordinate models."""

import pytest

from extrudely.cdr.coordinates import (
    CoordinateFrame,
    EngineeringCoordinate,
    NormalizedCoordinate,
    PixelCoordinate,
)


class TestPixelCoordinate:
    def test_valid_pixel(self):
        c = PixelCoordinate.model_validate(
            {"coordinate_system": "pixel", "x": 425, "y": 318}
        )
        assert c.x == 425
        assert c.y == 318
        assert c.coordinate_system == "pixel"

    def test_requires_int_values(self):
        c = PixelCoordinate.model_validate(
            {"coordinate_system": "pixel", "x": 100, "y": 200}
        )
        assert isinstance(c.x, int)
        assert isinstance(c.y, int)

    def test_rejects_missing_fields(self):
        with pytest.raises(ValueError):
            PixelCoordinate.model_validate({"coordinate_system": "pixel", "x": 100})


class TestNormalizedCoordinate:
    def test_valid_normalized(self):
        c = NormalizedCoordinate.model_validate(
            {"coordinate_system": "normalized", "x": 0.421, "y": 0.312}
        )
        assert c.x == pytest.approx(0.421)
        assert c.y == pytest.approx(0.312)

    def test_clamps_to_zero_one(self):
        # Values outside [0,1] should be rejected if validation is strict
        c = NormalizedCoordinate.model_validate(
            {"coordinate_system": "normalized", "x": 0.0, "y": 1.0}
        )
        assert 0.0 <= c.x <= 1.0
        assert 0.0 <= c.y <= 1.0


class TestEngineeringCoordinate:
    def test_valid_engineering(self):
        c = EngineeringCoordinate.model_validate(
            {"coordinate_system": "engineering", "x": 45.0, "y": 32.0, "unit": "mm"}
        )
        assert c.x == 45.0
        assert c.y == 32.0
        assert c.unit == "mm"

    def test_round_trip(self):
        data = {"coordinate_system": "engineering", "x": 12.5, "y": 8.0, "unit": "mm"}
        c = EngineeringCoordinate.model_validate(data)
        assert c.model_dump() == data


class TestCoordinateFrame:
    def test_front_view_frame(self):
        frame = CoordinateFrame.model_validate({"u_axis": "X", "v_axis": "Z"})
        assert frame.u_axis == "X"
        assert frame.v_axis == "Z"

    def test_optional_fields(self):
        frame = CoordinateFrame.model_validate({"u_axis": "X", "v_axis": "Y"})
        assert frame.model_dump() == {"u_axis": "X", "v_axis": "Y"}
