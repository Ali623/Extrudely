"""Deterministic compiler: CFP CutExtrudeFeature + Sketch -> CadQuery cut code.

Per AD-3: Stateless and deterministic. Same inputs always produce byte-identical output.
Per AD-13: Phase 1 operation — CUT_EXTRUDE.
"""
import math

from extrudely.cfp.features import CutExtrudeFeature
from extrudely.cfp.parameters import Parameter
from extrudely.cfp.sketch import Sketch
from extrudely.compiler.errors import CompilerError
from extrudely.compiler.sketch_compiler import compile_sketch

_FACE_SELECTORS = {
    (0.0, 0.0, -1.0): 'faces(">Z")',   # top face, cut down
}


def compile_cut_extrude(
    feature: CutExtrudeFeature,
    sketch: Sketch,
    parameters: dict[str, Parameter] | None = None,
) -> str:
    """Compile a CFP CutExtrudeFeature + Sketch into CadQuery Python code.

    Args:
        feature: The CUT_EXTRUDE feature definition (CFP spec §19).
        sketch: The 2D sketch for the cut profile.
        parameters: Optional parameter table for resolving $param references.

    Returns:
        Complete CadQuery Python code string for the cut operation.

    Raises:
        CompilerError: For unresolved parameters, invalid depth, bad termination,
                       unsupported direction, unclosed profile, or sketch_id mismatch.
    """
    # --- pre-flight: sketch_id cross-check ---
    if feature.sketch_id != sketch.sketch_id:
        raise CompilerError(
            "sketch_id_mismatch",
            feature.feature_id,
            f"Feature references sketch '{feature.sketch_id}' "
            f"but sketch '{sketch.sketch_id}' was provided.",
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
            "Direction vector is [0, 0, 0] — must be non-zero.",
        )
    dir_tuple = (dx, dy, dz)
    if dir_tuple not in _FACE_SELECTORS:
        raise CompilerError(
            "unsupported_direction",
            feature.feature_id,
            f"Only -Z cut direction is supported in Phase 1, got {list(dir_tuple)}.",
        )
    face_selector = _FACE_SELECTORS[dir_tuple]

    # --- resolve depth ---
    depth = _resolve_depth(feature, parameters)

    # --- pre-flight: depth ---
    if not math.isfinite(depth):
        raise CompilerError(
            "non_finite_depth",
            feature.feature_id,
            f"Cut depth must be finite, got {depth}.",
        )
    if depth <= 0:
        raise CompilerError(
            "invalid_depth",
            feature.feature_id,
            f"Cut depth must be > 0, got {depth}.",
        )

    # --- pre-flight: closed profile ---
    if not sketch.closed:
        raise CompilerError(
            "unclosed_profile",
            feature.feature_id,
            f"Sketch '{sketch.sketch_id}' must be closed for cut-extrude (closed=True).",
        )

    # --- generate sketch code ---
    sketch_code = compile_sketch(sketch)

    # --- adapt: replace Workplane line with face-selection workplane ---
    lines = sketch_code.rstrip("\n").split("\n")
    # Find the Workplane line emitted by compile_sketch and replace it
    for i, line in enumerate(lines):
        if line.startswith("result = cq.Workplane("):
            lines[i] = f"result = result.{face_selector}.workplane()"
            break

    # --- append cut operation ---
    dir_str = f"[{dx:.6g}, {dy:.6g}, {dz:.6g}]"
    if feature.termination == "through_all":
        lines.append(
            f"# {feature.feature_id}: CUT_EXTRUDE through_all "
            f"direction={dir_str} target={feature.target}"
        )
        lines.append("result = result.cutThruAll()")
    else:
        # Phase 1: only -Z direction, cutBlind(-depth) cuts into the part
        lines.append(
            f"# {feature.feature_id}: CUT_EXTRUDE depth={depth:.6f} "
            f"direction={dir_str} target={feature.target}"
        )
        lines.append(f"result = result.cutBlind({-depth:.6f})")

    return "\n".join(lines) + "\n"


def _resolve_depth(
    feature: CutExtrudeFeature,
    parameters: dict[str, Parameter] | None,
) -> float:
    """Resolve the depth value from a numeric or $param reference."""
    raw = feature.depth
    if isinstance(raw, (int, float)):
        return float(raw)
    if isinstance(raw, str) and raw.startswith("$"):
        param_name = raw[1:]
        if parameters is None or param_name not in parameters:
            raise CompilerError(
                "unresolved_parameter",
                feature.feature_id,
                f"Parameter '${param_name}' not found in parameter table.",
            )
        return float(parameters[param_name].value)
    if isinstance(raw, str):
        raise CompilerError(
            "invalid_depth_format",
            feature.feature_id,
            f"Depth must be a number or $param reference, got {raw!r}.",
        )
    raise CompilerError(
        "invalid_depth_type",
        feature.feature_id,
        f"Unsupported depth type: {type(raw).__name__}.",
    )
