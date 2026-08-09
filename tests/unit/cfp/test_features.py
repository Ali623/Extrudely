"""Tests for CFP feature models — ExtrudeFeature schema validation."""
import pytest
from pydantic import ValidationError

from extrudely.cfp.features import ExtrudeFeature


class TestExtrudeFeature:
    def test_valid_extrude_minimal(self):
        """ExtrudeFeature with only required fields."""
        f = ExtrudeFeature(feature_id="F001", sketch_id="SK001", distance=10.0)
        assert f.feature_id == "F001"
        assert f.operation == "EXTRUDE"
        assert f.sketch_id == "SK001"
        assert f.distance == 10.0
        assert f.direction == [0, 0, 1]
        assert f.mode == "add"
        assert f.symmetric is False

    def test_valid_extrude_all_fields(self):
        """ExtrudeFeature with all fields explicitly set."""
        f = ExtrudeFeature(
            feature_id="F002",
            operation="EXTRUDE",
            sketch_id="SK002",
            direction=[1, 0, 0],
            distance="$part_height",
            mode="new_body",
            symmetric=True,
        )
        assert f.distance == "$part_height"
        assert f.mode == "new_body"
        assert f.symmetric is True

    def test_defaults_apply(self):
        """Non-required fields get correct defaults."""
        f = ExtrudeFeature(feature_id="F001", sketch_id="SK001", distance=5.0)
        assert f.direction == [0, 0, 1]
        assert f.mode == "add"
        assert f.symmetric is False

    def test_rejects_invalid_operation(self):
        """Operation must be EXTRUDE (Literal type)."""
        with pytest.raises(ValidationError):
            ExtrudeFeature(feature_id="F001", operation="BOGUS", sketch_id="SK001", distance=10)

    def test_rejects_invalid_mode(self):
        """Mode must be 'add' or 'new_body'."""
        with pytest.raises(ValidationError):
            ExtrudeFeature(feature_id="F001", sketch_id="SK001", distance=10, mode="subtract")

    def test_rejects_missing_feature_id(self):
        """feature_id is required."""
        with pytest.raises(ValidationError):
            ExtrudeFeature(sketch_id="SK001", distance=10)

    def test_rejects_missing_sketch_id(self):
        """sketch_id is required."""
        with pytest.raises(ValidationError):
            ExtrudeFeature(feature_id="F001", distance=10)

    def test_rejects_extra_fields(self):
        """Extra fields forbidden per model_config."""
        with pytest.raises(ValidationError):
            ExtrudeFeature(feature_id="F001", sketch_id="SK001", distance=10, extra_field=42)

    def test_rejects_nan_direction(self):
        """Direction with NaN values rejected at schema level."""
        with pytest.raises(ValidationError):
            ExtrudeFeature(feature_id="F001", sketch_id="SK001", distance=10,
                           direction=[0.0, 0.0, float("nan")])

    def test_rejects_inf_direction(self):
        """Direction with Inf values rejected at schema level."""
        with pytest.raises(ValidationError):
            ExtrudeFeature(feature_id="F001", sketch_id="SK001", distance=10,
                           direction=[0.0, float("inf"), 0.0])

    def test_rejects_empty_dollar_ref(self):
        """Distance '$' (empty param name) rejected at schema level."""
        with pytest.raises(ValidationError):
            ExtrudeFeature(feature_id="F001", sketch_id="SK001", distance="$")

    def test_rejects_empty_distance_string(self):
        """Empty distance string rejected at schema level."""
        with pytest.raises(ValidationError):
            ExtrudeFeature(feature_id="F001", sketch_id="SK001", distance="  ")


class TestCutExtrudeFeature:
    def test_valid_cut_extrude_minimal(self):
        """CutExtrudeFeature with only required fields."""
        from extrudely.cfp.features import CutExtrudeFeature
        f = CutExtrudeFeature(feature_id="F002", sketch_id="SK002", target="F001", depth=10.0)
        assert f.feature_id == "F002"
        assert f.operation == "CUT_EXTRUDE"
        assert f.target == "F001"
        assert f.depth == 10.0
        assert f.direction == [0, 0, -1]
        assert f.termination == "blind"

    def test_valid_cut_extrude_all_fields(self):
        """CutExtrudeFeature with all fields explicitly set."""
        from extrudely.cfp.features import CutExtrudeFeature
        f = CutExtrudeFeature(
            feature_id="F003",
            sketch_id="SK003",
            target="F001",
            direction=[0, 0, 1],
            depth="$pocket_depth",
            termination="through_all",
        )
        assert f.depth == "$pocket_depth"
        assert f.termination == "through_all"
        assert f.direction == [0, 0, 1]

    def test_defaults_apply(self):
        """Non-required fields get correct defaults."""
        from extrudely.cfp.features import CutExtrudeFeature
        f = CutExtrudeFeature(feature_id="F002", sketch_id="SK002", target="F001", depth=5.0)
        assert f.direction == [0, 0, -1]
        assert f.termination == "blind"

    def test_rejects_invalid_termination(self):
        """Termination must be 'blind' or 'through_all'."""
        from extrudely.cfp.features import CutExtrudeFeature
        with pytest.raises(ValidationError):
            CutExtrudeFeature(feature_id="F002", sketch_id="SK002", target="F001", depth=10,
                              termination="up_to_face")

    def test_rejects_missing_target(self):
        """target is required."""
        from extrudely.cfp.features import CutExtrudeFeature
        with pytest.raises(ValidationError):
            CutExtrudeFeature(feature_id="F002", sketch_id="SK002", depth=10)

    def test_rejects_nan_direction(self):
        """Direction with NaN values rejected at schema level."""
        from extrudely.cfp.features import CutExtrudeFeature
        with pytest.raises(ValidationError):
            CutExtrudeFeature(feature_id="F002", sketch_id="SK002", target="F001", depth=10,
                              direction=[0.0, 0.0, float("nan")])

    def test_rejects_extra_fields(self):
        """Extra fields forbidden per model_config."""
        from extrudely.cfp.features import CutExtrudeFeature
        with pytest.raises(ValidationError):
            CutExtrudeFeature(feature_id="F002", sketch_id="SK002", target="F001", depth=10,
                              extra_field=42)
