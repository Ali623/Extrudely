"""Deterministic compiler: CFP ExtrudeFeature + Sketch -> CadQuery extrude code.

Per AD-3: Stateless and deterministic. Same inputs always produce byte-identical output.
Per AD-13: Phase 1 operation — EXTRUDE.
"""
import math

from extrudely.cfp.features import ExtrudeFeature
from extrudely.cfp.parameters import Parameter
from extrudely.cfp.sketch import Sketch
from extrudely.compiler.errors import CompilerError
from extrudely.compiler.sketch_compiler import compile_sketch

_VALID_MODES = frozenset({"add", "new_body"})
_DEFAULT_DIRECTION = [0.0, 0.0, 1.0]


def compile_extrude(
    feature: ExtrudeFeature,
    sketch: Sketch,
    parameters: dict[str, Parameter] | None = None,
) -> str:
    """Compile a CFP ExtrudeFeature + Sketch into CadQuery Python code.

    Args:
        feature: The EXTRUDE feature definition (CFP spec §18).
        sketch: The 2D sketch to extrude.
        parameters: Optional parameter table for resolving $param references.

    Returns:
        Complete CadQuery Python code string (sketch + extrude).

    Raises:
        CompilerError: For unresolved parameters, invalid distance, bad mode,
                       zero direction vector, unclosed sketch profile, or
                       unsupported direction.
    """
    # --- pre-flight: sketch_id cross-check ---
    if feature.sketch_id != sketch.sketch_id:
        raise CompilerError(
            "sketch_id_mismatch",
            feature.feature_id,
            f"Feature references sketch '{feature.sketch_id}' "
            f"but sketch '{sketch.sketch_id}' was provided.",
        )

    # --- pre-flight: mode ---
    if feature.mode not in _VALID_MODES:
        raise CompilerError(
            "unsupported_mode",
            feature.feature_id,
            f"Unsupported extrude mode: {feature.mode!r}. Expected 'add' or 'new_body'.",
        )

    # --- pre-flight: direction ---
    dx, dy, dz = feature.direction
    if not all(math.isfinite(v) for v in feature.direction):
        raise CompilerError(
            "non_finite_direction",
            feature.feature_id,
            f"Direction vector contains non-finite values: {feature.direction}.",
        )
    if dx == 0.0 and dy == 0.0 and dz == 0.0:
        raise CompilerError(
            "zero_direction",
            feature.feature_id,
            "Extrude direction vector is [0, 0, 0] — must be non-zero.",
        )
    if feature.direction != _DEFAULT_DIRECTION:
        raise CompilerError(
            "unsupported_direction",
            feature.feature_id,
            f"Only +Z extrusion is supported in Phase 1, got {feature.direction}.",
        )

    # --- resolve distance ---
    distance = _resolve_distance(feature, parameters)

    # --- pre-flight: distance ---
    if not math.isfinite(distance):
        raise CompilerError(
            "non_finite_distance",
            feature.feature_id,
            f"Extrude distance must be finite, got {distance}.",
        )
    if distance <= 0:
        raise CompilerError(
            "invalid_distance",
            feature.feature_id,
            f"Extrude distance must be > 0, got {distance}.",
        )

    # --- pre-flight: closed profile ---
    if not sketch.closed:
        raise CompilerError(
            "unclosed_profile",
            feature.feature_id,
            f"Sketch '{sketch.sketch_id}' must be closed for extrude (closed=True).",
        )

    # --- generate sketch code ---
    sketch_code = compile_sketch(sketch)

    # --- append extrude call ---
    dir_str = f"[{dx:.6g}, {dy:.6g}, {dz:.6g}]"
    lines = sketch_code.rstrip("\n").split("\n")
    if feature.symmetric:
        half = distance / 2.0
        lines.append(
            f"# {feature.feature_id}: EXTRUDE symmetric "
            f"distance={distance:.6f} (half={half:.6f}) "
            f"direction={dir_str} mode={feature.mode}"
        )
        lines.append(f"result = result.extrude({half:.6f}, both=True)")
    else:
        lines.append(
            f"# {feature.feature_id}: EXTRUDE distance={distance:.6f} "
            f"direction={dir_str} mode={feature.mode}"
        )
        lines.append(f"result = result.extrude({distance:.6f})")

    return "\n".join(lines) + "\n"


def _resolve_distance(
    feature: ExtrudeFeature,
    parameters: dict[str, Parameter] | None,
) -> float:
    """Resolve the distance value from a numeric or $param reference.

    Returns:
        The resolved distance as a float.

    Raises:
        CompilerError: If a $param reference cannot be resolved or a literal
                       distance string cannot be parsed as a float.
    """
    raw = feature.distance
    if isinstance(raw, (int, float)):
        return float(raw)
    # $param reference
    if isinstance(raw, str) and raw.startswith("$"):
        param_name = raw[1:]  # strip '$'
        if parameters is None or param_name not in parameters:
            raise CompilerError(
                "unresolved_parameter",
                feature.feature_id,
                f"Parameter '${param_name}' not found in parameter table.",
            )
        return float(parameters[param_name].value)
    # string but not a $param — must be a parseable float literal
    if isinstance(raw, str):
        raise CompilerError(
            "invalid_distance_format",
            feature.feature_id,
            f"Distance must be a number or $param reference, got {raw!r}.",
        )
    raise CompilerError(
        "invalid_distance_type",
        feature.feature_id,
        f"Unsupported distance type: {type(raw).__name__}.",
    )
