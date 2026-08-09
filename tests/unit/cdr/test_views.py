"""Tests for DrawingView and SectionView models."""

import pytest

from extrudely.cdr.models import DrawingView, SectionView


class TestDrawingView:
    def test_front_view(self):
        view = DrawingView.model_validate({
            "view_id": "VIEW_FRONT",
            "view_type": "front",
            "confidence": 0.98,
            "projection_system": "first_angle",
            "bounding_box": [0.10, 0.15, 0.48, 0.61],
            "coordinate_frame": {"u_axis": "X", "v_axis": "Z"},
        })
        assert view.view_id == "VIEW_FRONT"
        assert view.view_type.value == "front"
        assert view.confidence == 0.98

    def test_minimal_view(self):
        view = DrawingView.model_validate({
            "view_id": "VIEW_UNKNOWN",
            "view_type": "unknown",
            "confidence": 0.5,
        })
        assert view.projection_system is None
        assert view.bounding_box is None
        assert view.coordinate_frame is None

    def test_all_view_types(self):
        for vt in ["front", "top", "left", "right", "section", "unknown"]:
            view = DrawingView.model_validate({
                "view_id": f"VIEW_{vt.upper()}",
                "view_type": vt,
                "confidence": 1.0,
            })
            assert view.view_type.value == vt

    def test_rejects_invalid_view_type(self):
        with pytest.raises(ValueError):
            DrawingView.model_validate({
                "view_id": "VIEW_BAD",
                "view_type": "isometric",
                "confidence": 0.5,
            })

    def test_round_trip(self):
        data = {
            "view_id": "VIEW_TOP",
            "view_type": "top",
            "confidence": 0.99,
            "projection_system": "first_angle",
            "bounding_box": [0.0, 0.0, 0.5, 0.5],
            "coordinate_frame": {"u_axis": "X", "v_axis": "Y"},
        }
        view = DrawingView.model_validate(data)
        assert view.model_dump() == data


class TestSectionView:
    def test_section_view_extends_drawing_view(self):
        sv = SectionView.model_validate({
            "view_id": "VIEW_SECTION_AA",
            "view_type": "section",
            "section_label": "A-A",
            "section_type": "full",
            "confidence": 0.91,
        })
        assert sv.section_label == "A-A"
        assert sv.section_type == "full"
        assert sv.view_type.value == "section"

    def test_section_view_with_frame(self):
        sv = SectionView.model_validate({
            "view_id": "VIEW_SECTION_BB",
            "view_type": "section",
            "section_label": "B-B",
            "section_type": "full",
            "confidence": 0.85,
            "coordinate_frame": {"u_axis": "Y", "v_axis": "Z"},
        })
        assert sv.coordinate_frame.u_axis == "Y"
