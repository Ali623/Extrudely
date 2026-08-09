"""Deterministic compiler: CFP Sketch -> CadQuery 2D sketch code strings.

Per AD-3: Stateless and deterministic. Same Sketch input always produces
byte-identical CadQuery output.
"""
import math

from extrudely.cfp.enums import SketchPlaneEnum
from extrudely.cfp.sketch import Sketch
from extrudely.compiler.errors import CompilerError

_PLANE_MAP = {
    SketchPlaneEnum.XY: "XY",
    SketchPlaneEnum.XZ: "XZ",
    SketchPlaneEnum.YZ: "YZ",
}

# Primitives that produce already-closed wires — close() is not needed and would crash
_SELF_CLOSING_PRIMITIVES = frozenset({"RECTANGLE", "CIRCLE"})


def compile_sketch(sketch: Sketch) -> str:
    if sketch.plane not in _PLANE_MAP:
        raise CompilerError(
            "unsupported_plane",
            sketch.sketch_id,
            f"Unsupported sketch plane: {getattr(sketch.plane, 'value', sketch.plane)}",
        )
    if not sketch.geometry:
        raise CompilerError(
            "empty_geometry",
            sketch.sketch_id,
            "Sketch has no geometry primitives",
        )
    plane = _PLANE_MAP[sketch.plane]
    lines = [f"# Sketch {sketch.sketch_id} on {plane}"]
    lines.append(f'result = cq.Workplane("{plane}")')
    for i, prim in enumerate(sketch.geometry):
        pid = prim.id or f"_{i}"
        lines.append(f"# {pid}: {prim.type}")
        if prim.type == "LINE":
            lines.extend(_compile_line(prim, i == 0))
        elif prim.type == "ARC":
            lines.extend(_compile_arc(prim))
        elif prim.type == "CIRCLE":
            lines.extend(_compile_circle(prim))
        elif prim.type == "RECTANGLE":
            lines.extend(_compile_rectangle(prim))
        elif prim.type == "POLYLINE":
            lines.extend(_compile_polyline(prim))
        else:
            raise CompilerError(
                "unknown_primitive",
                sketch.sketch_id,
                f"Unknown primitive type: {getattr(prim, 'type', 'unknown')}",
            )
    if sketch.closed and _needs_close(sketch.geometry):
        lines.append("result = result.close()")
    return "\n".join(lines) + "\n"

def _compile_line(prim, is_first):
    sx, sy = prim.start[0], prim.start[1]
    ex, ey = prim.end[0], prim.end[1]
    out = []
    if is_first:
        out.append(f"result = result.moveTo({sx}, {sy})")
    out.append(f"result = result.lineTo({ex}, {ey})")
    return out

def _compile_arc(prim):
    cx, cy = prim.center[0], prim.center[1]
    mid_angle = (prim.start_angle + prim.end_angle) / 2
    mx = cx + prim.radius * math.cos(math.radians(mid_angle))
    my = cy + prim.radius * math.sin(math.radians(mid_angle))
    ex = cx + prim.radius * math.cos(math.radians(prim.end_angle))
    ey = cy + prim.radius * math.sin(math.radians(prim.end_angle))
    sx = cx + prim.radius * math.cos(math.radians(prim.start_angle))
    sy = cy + prim.radius * math.sin(math.radians(prim.start_angle))
    return [
        f"result = result.moveTo({sx:.6f}, {sy:.6f})",
        f"result = result.threePointArc(({mx:.6f}, {my:.6f}), ({ex:.6f}, {ey:.6f}))",
    ]

def _compile_circle(prim):
    cx, cy = prim.center[0], prim.center[1]
    return [
        f"result = result.moveTo({cx + prim.radius}, {cy})",
        f"result = result.circle({prim.radius})",
    ]

def _compile_rectangle(prim):
    cx, cy = prim.center[0], prim.center[1]
    return [
        f"result = result.moveTo({cx - prim.width / 2}, {cy - prim.height / 2})",
        f"result = result.rect({prim.width}, {prim.height})",
    ]

def _compile_polyline(prim):
    out = []
    for i, pt in enumerate(prim.points):
        x, y = pt[0], pt[1]
        if i == 0:
            out.append(f"result = result.moveTo({x}, {y})")
        else:
            out.append(f"result = result.lineTo({x}, {y})")
    return out


def _needs_close(geometry: list) -> bool:
    """Only open-chain primitives need explicit close().

    RECTANGLE and CIRCLE produce already-closed wires in CadQuery;
    calling close() on them would raise an error.
    """
    if not geometry:
        return False
    return any(
        getattr(p, "type", None) not in _SELF_CLOSING_PRIMITIVES
        for p in geometry
    )
