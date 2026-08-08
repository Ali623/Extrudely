# Extrudely POC 1
## CAD Feature Plan Specification v0.1

### 1. Purpose

The **CAD Feature Plan**, abbreviated **CFP**, defines how the geometry described by the Common Drawing Representation should be constructed as an editable parametric CAD model.

The separation is:

```text
CDR
=
What does the drawing describe?

CFP
=
How should that geometry be constructed?

CadQuery
=
Executable implementation of that construction plan
```

The CFP should therefore contain **structured CAD operations**, not arbitrary Python code.

---

# 2. Overall Flow

```text
Common Drawing Representation
            │
            ▼
      3D Feature Reasoner
            │
            ▼
     CAD Feature Plan
            │
            ▼
    Plan Validation
            │
            ▼
 Deterministic Compiler
            │
            ▼
      CadQuery Code
            │
            ▼
        STEP / B-Rep
```

If validation detects an error:

```text
Validation Error
      │
      ▼
Correction Agent
      │
      ▼
Modify CFP
      │
      ▼
Recompile
```

The system should preferably correct the **feature plan**, not generated Python directly.

---

# 3. Top-Level CFP Structure

```text
CADFeaturePlan
│
├── plan_metadata
├── part_reference
├── coordinate_system
├── parameters
├── sketches
├── features
├── dependencies
├── assumptions
├── uncertainties
├── validation_targets
└── revision_history
```

A simplified JSON structure:

```json
{
  "plan_id": "CFP_001",
  "version": "0.1",
  "document_id": "DOC_001",
  "status": "candidate",
  "parameters": {},
  "sketches": [],
  "features": [],
  "assumptions": [],
  "validation_targets": []
}
```

---

# 4. Plan Status

Allowed states:

```text
candidate
validated
requires_review
failed
user_confirmed
final
```

Example:

```json
{
  "status": "validated"
}
```

means that the generated CAD has passed the currently configured validation thresholds.

---

# 5. Global Coordinate System

Extrudely should use one normalized 3D coordinate convention.

Recommended:

```text
X = width
Y = depth
Z = height
```

The generated part should preferably have its main reference geometry positioned predictably around the origin.

Example:

```text
XY plane → common base sketch plane

Z → primary extrusion direction
```

This does not mean every part must start from the XY plane. Revolved and side-driven parts may use other planes.

---

# 6. Global Parameter Table

Dimensions should be named rather than copied repeatedly into feature definitions.

Example:

```json
{
  "parameters": {
    "part_width": {
      "value": 100.0,
      "unit": "mm",
      "source_dimension": "DIM_001"
    },
    "part_depth": {
      "value": 60.0,
      "unit": "mm",
      "source_dimension": "DIM_002"
    },
    "part_height": {
      "value": 20.0,
      "unit": "mm",
      "source_dimension": "DIM_003"
    },
    "hole_diameter": {
      "value": 8.0,
      "unit": "mm",
      "source_dimension": "DIM_008"
    }
  }
}
```

Then a feature can reference:

```text
$hole_diameter
```

rather than hard-coding:

```text
8.0
```

This improves editability.

---

# 7. Parameter Provenance

Every important parameter should retain:

```text
value

unit

CDR source

confidence

status
```

Example:

```json
{
  "value": 8.0,
  "unit": "mm",
  "cdr_reference": "DIM_008",
  "confidence": 0.98,
  "status": "observed"
}
```

An inferred value might instead use:

```json
{
  "status": "inferred",
  "confidence": 0.78
}
```

---

# 8. Feature Sequence

Features must be ordered.

Example:

```text
F001 Base Extrusion
      ↓
F002 Pocket
      ↓
F003 Hole
      ↓
F004 Linear Pattern
      ↓
F005 Chamfer
      ↓
F006 Fillet
```

Every feature should explicitly declare its dependencies.

---

# 9. Base Feature Object

Every CAD feature should share:

```json
{
  "feature_id": "F003",
  "operation": "HOLE",
  "name": "Mounting Hole",
  "enabled": true,
  "depends_on": ["F001"],
  "confidence": 0.97,
  "cdr_evidence": ["HYP_004", "DIM_008"],
  "parameters": {},
  "validation_targets": []
}
```

---

# 10. Initial POC Operation Vocabulary

POC 1 should use a controlled operation set.

```text
SKETCH

EXTRUDE

CUT_EXTRUDE

HOLE

COUNTERBORE

COUNTERSINK

REVOLVE

REVOLVE_CUT

LINEAR_PATTERN

CIRCULAR_PATTERN

MIRROR

CHAMFER

FILLET
```

This should be sufficient for the intermediate-complexity scope we selected.

---

# 11. Why Use a Closed Vocabulary

Without a controlled operation vocabulary:

```text
AI may invent arbitrary CAD procedures.
```

With a closed vocabulary:

```text
AI chooses among supported engineering operations.
```

Benefits:

- deterministic compilation
- easier validation
- easier training
- easier debugging
- easier feature-level evaluation
- better security
- simpler user correction

---

# 12. Sketch Object

A sketch defines the 2D geometry required by a feature.

Example:

```json
{
  "sketch_id": "SK001",
  "plane": "XY",
  "origin": [0, 0, 0],
  "geometry": [],
  "constraints": [],
  "cdr_references": ["PROFILE_001"]
}
```

---

# 13. Sketch Planes

Supported initial planes:

```text
XY
XZ
YZ
```

Additionally, later features may define sketches on:

```text
planar faces
offset planes
```

For POC 1, we should avoid complex arbitrary construction-plane logic unless required.

---

# 14. Sketch Primitive Vocabulary

Inside a sketch:

```text
LINE

ARC

CIRCLE

RECTANGLE

POLYLINE
```

Potential later extension:

```text
ELLIPSE
SPLINE
```

Splines should remain outside the main POC geometry target.

---

# 15. Rectangle Sketch Example

```json
{
  "sketch_id": "SK001",
  "plane": "XY",
  "geometry": [
    {
      "type": "RECTANGLE",
      "width": "$part_width",
      "height": "$part_depth",
      "center": [0, 0]
    }
  ]
}
```

---

# 16. Custom Profile Example

```json
{
  "geometry": [
    {
      "type": "LINE",
      "start": [0, 0],
      "end": [40, 0]
    },
    {
      "type": "LINE",
      "start": [40, 0],
      "end": [40, 20]
    },
    {
      "type": "ARC",
      "center": [30, 20],
      "radius": 10,
      "start_angle": 0,
      "end_angle": 180
    }
  ]
}
```

The compiler should verify that required profiles are closed before using them for solid operations.

---

# 17. Sketch Constraints

Supported constraints may include:

```text
horizontal
vertical
parallel
perpendicular
coincident
concentric
equal
symmetric
tangent
distance
radius
diameter
```

For POC 1, these constraints mainly help preserve design intent and validate geometry.

---

# 18. EXTRUDE Feature

Example:

```json
{
  "feature_id": "F001",
  "operation": "EXTRUDE",
  "sketch_id": "SK001",
  "direction": [0, 0, 1],
  "distance": "$part_height",
  "mode": "add",
  "symmetric": false
}
```

Possible modes:

```text
add
new_body
```

POC 1 should normally operate with a single body.

---

# 19. CUT_EXTRUDE Feature

```json
{
  "feature_id": "F002",
  "operation": "CUT_EXTRUDE",
  "sketch_id": "SK002",
  "target": "F001",
  "direction": [0, 0, -1],
  "depth": 10.0,
  "termination": "blind"
}
```

Supported termination types:

```text
blind
through_all
up_to_face
```

For POC 1, `blind` and `through_all` are the most important.

---

# 20. Pocket Representation

A pocket does not necessarily need its own operation.

Instead:

```text
SKETCH
+
CUT_EXTRUDE
```

can represent:

- rectangular pocket
- circular pocket
- slot
- custom profile cut

This keeps the operation vocabulary smaller.

---

# 21. HOLE Feature

Example:

```json
{
  "feature_id": "F003",
  "operation": "HOLE",
  "support_face": "FACE_TOP",
  "locations": [
    [-30, -15],
    [30, -15],
    [-30, 15],
    [30, 15]
  ],
  "diameter": "$hole_diameter",
  "termination": "through_all"
}
```

---

# 22. Blind Hole

```json
{
  "operation": "HOLE",
  "diameter": 10,
  "termination": "blind",
  "depth": 15
}
```

---

# 23. Counterbore

```json
{
  "feature_id": "F004",
  "operation": "COUNTERBORE",
  "location": [25, 20],
  "hole_diameter": 8,
  "counterbore_diameter": 14,
  "counterbore_depth": 5,
  "termination": "through_all"
}
```

---

# 24. Countersink

```json
{
  "operation": "COUNTERSINK",
  "location": [25, 20],
  "hole_diameter": 8,
  "countersink_diameter": 16,
  "angle": 90,
  "termination": "through_all"
}
```

---

# 25. Simplified Thread Metadata

For threaded holes:

```json
{
  "operation": "HOLE",
  "diameter": 8.5,
  "thread": {
    "designation": "M10x1.5",
    "standard": "metric",
    "nominal_diameter": 10,
    "pitch": 1.5,
    "geometry_mode": "metadata"
  }
}
```

Actual helical geometry is not required.

---

# 26. REVOLVE Feature

Example:

```json
{
  "feature_id": "F001",
  "operation": "REVOLVE",
  "sketch_id": "SK001",
  "axis": {
    "start": [0, 0],
    "end": [0, 100]
  },
  "angle": 360
}
```

This should support:

- shafts
- stepped shafts
- flanges
- simple turned parts

---

# 27. REVOLVE_CUT

For grooves or rotational cuts:

```json
{
  "operation": "REVOLVE_CUT",
  "sketch_id": "SK004",
  "axis_reference": "AXIS_MAIN",
  "angle": 360
}
```

---

# 28. LINEAR_PATTERN

Instead of modeling repeated holes independently:

```json
{
  "feature_id": "F005",
  "operation": "LINEAR_PATTERN",
  "source_feature": "F003",
  "direction": [1, 0, 0],
  "count": 4,
  "spacing": 20
}
```

Optional second direction:

```json
{
  "direction_2": [0, 1, 0],
  "count_2": 2,
  "spacing_2": 30
}
```

---

# 29. CIRCULAR_PATTERN

```json
{
  "operation": "CIRCULAR_PATTERN",
  "source_feature": "F003",
  "axis": "AXIS_Z",
  "count": 6,
  "angle": 360
}
```

Useful for:

- flange holes
- bolt circles
- radial patterns

---

# 30. MIRROR

```json
{
  "operation": "MIRROR",
  "source_features": ["F004"],
  "mirror_plane": "YZ"
}
```

The feature history should preserve symmetry rather than duplicating features unnecessarily.

---

# 31. CHAMFER

```json
{
  "operation": "CHAMFER",
  "edge_selection": {
    "strategy": "feature_relative",
    "references": ["F001"]
  },
  "distance": 2.0
}
```

---

# 32. FILLET

```json
{
  "operation": "FILLET",
  "edge_selection": {
    "strategy": "feature_relative",
    "references": ["F001"]
  },
  "radius": 3.0
}
```

---

# 33. Important Edge-Selection Problem

Fillets and chamfers are challenging because raw CAD edge indices are unstable.

Avoid:

```text
edge 17
```

whenever possible.

Instead use semantic selectors such as:

```text
all vertical outer edges

top perimeter edges

edges created by Feature F003

edges adjacent to FACE_TOP
```

The compiler can translate these into CadQuery selectors.

---

# 34. Semantic Geometry References

Features should refer to semantic entities.

Examples:

```text
FACE_TOP

FACE_BOTTOM

FACE_FRONT

AXIS_MAIN

BASE_BODY

PROFILE_OUTER

HOLE_PATTERN_1
```

rather than transient OpenCascade IDs.

This will make regeneration substantially more robust.

---

# 35. Dependency Graph

Each feature creates a dependency node.

Example:

```text
F001 Base Extrusion
 │
 ├── F002 Pocket
 │
 ├── F003 Hole
 │    └── F004 Circular Pattern
 │
 └── F005 Chamfer
      └── F006 Fillet
```

A feature cannot execute unless its dependencies are valid.

---

# 36. Feature Dependencies

Example:

```json
{
  "feature_id": "F006",
  "depends_on": [
    "F001",
    "F005"
  ]
}
```

This helps identify exactly which downstream operations must be regenerated after a correction.

---

# 37. Assumptions

When the drawing does not explicitly define something but the system proceeds, the assumption must be recorded.

Example:

```json
{
  "assumption_id": "ASM_001",
  "description": "Pocket is centered on the vertical symmetry axis.",
  "confidence": 0.81,
  "cdr_evidence": ["SYM_001"],
  "affects_features": ["F002"]
}
```

---

# 38. Critical vs Non-Critical Assumptions

Assumptions should have severity:

```text
low
medium
critical
```

Example:

```text
Assuming a fillet is R3 instead of R2
→ medium

Assuming a blind hole is through
→ critical
```

Critical low-confidence assumptions should trigger review.

---

# 39. CFP Uncertainty

Example:

```json
{
  "uncertainty_id": "CFP_UNC_01",
  "feature_id": "F003",
  "property": "termination",
  "candidates": [
    {
      "value": "through_all",
      "confidence": 0.61
    },
    {
      "value": "blind",
      "confidence": 0.39
    }
  ]
}
```

This may trigger multiple CAD candidates.

---

# 40. Candidate Feature Plans

For ambiguous drawings:

```text
CFP Candidate A
Hole = THROUGH

CFP Candidate B
Hole = BLIND 20 mm
```

Each candidate is compiled and validated independently.

---

# 41. Candidate Ranking

Candidate ranking should use:

```text
drawing agreement

dimension agreement

cross-view consistency

feature consistency

CAD validity

projection similarity
```

not only VLM confidence.

Conceptually:

```text
Candidate Score
=
Geometry Validation
+
Dimension Validation
+
Projection Consistency
+
Feature Consistency
```

Exact weights should be calibrated experimentally.

---

# 42. Validation Targets Inside the CFP

Each feature can define what should be checked after generation.

Example:

```json
{
  "feature_id": "F003",
  "validation_targets": [
    {
      "type": "diameter",
      "expected": 8.0,
      "unit": "mm"
    },
    {
      "type": "count",
      "expected": 4
    },
    {
      "type": "termination",
      "expected": "through_all"
    }
  ]
}
```

---

# 43. Dimensional Validation Target

```json
{
  "type": "dimension",
  "name": "overall_width",
  "expected": 100.0,
  "absolute_tolerance": 0.5,
  "relative_tolerance": 0.01
}
```

The final threshold values remain configurable.

---

# 44. Projection Validation Target

A feature may reference which source view should show it.

Example:

```json
{
  "type": "projection_presence",
  "view": "TOP",
  "expected_geometry": "circle"
}
```

This allows the validation system to ask:

```text
Does F003 produce the expected circle in the top projection?
```

---

# 45. Compiler Contract

The deterministic compiler receives a **valid CFP** and must return:

```text
CadQuery code

execution metadata

semantic entity map
```

Example semantic map:

```text
F001 → base solid

F003 → four cylindrical cuts

F005 → selected chamfer edges
```

This map will later support validation and correction.

---

# 46. Compiler Validation Before Execution

Before producing code, check:

```text
All referenced sketches exist?

All parameters resolved?

All dependencies valid?

Sketch profiles closed?

Feature order valid?

Unsupported operation present?

Critical uncertainty unresolved?
```

If not:

```text
DO NOT COMPILE
```

and return a structured error.

---

# 47. Deterministic Compiler Principle

The AI should generate:

```text
{
  "operation": "EXTRUDE",
  "distance": 20
}
```

The compiler should generate the actual CadQuery syntax.

This means the model does not need to memorize every CadQuery API detail.

---

# 48. Example Full CFP

Consider a rectangular mounting plate with four holes and edge chamfers.

```json
{
  "plan_id": "CFP_001",

  "parameters": {
    "width": 100,
    "depth": 60,
    "height": 10,
    "hole_diameter": 8,
    "hole_offset_x": 40,
    "hole_offset_y": 20,
    "chamfer_size": 2
  },

  "sketches": [
    {
      "sketch_id": "SK001",
      "plane": "XY",
      "geometry": [
        {
          "type": "RECTANGLE",
          "width": "$width",
          "height": "$depth",
          "center": [0, 0]
        }
      ]
    }
  ],

  "features": [
    {
      "feature_id": "F001",
      "operation": "EXTRUDE",
      "sketch_id": "SK001",
      "distance": "$height"
    },

    {
      "feature_id": "F002",
      "operation": "HOLE",
      "support_face": "FACE_TOP",
      "locations": [
        ["-$hole_offset_x", "-$hole_offset_y"],
        ["$hole_offset_x", "-$hole_offset_y"],
        ["-$hole_offset_x", "$hole_offset_y"],
        ["$hole_offset_x", "$hole_offset_y"]
      ],
      "diameter": "$hole_diameter",
      "termination": "through_all"
    },

    {
      "feature_id": "F003",
      "operation": "CHAMFER",
      "edge_selection": {
        "strategy": "outer_vertical_edges"
      },
      "distance": "$chamfer_size"
    }
  ]
}
```

---

# 49. Compiled Conceptually Into CadQuery

The compiler would produce something equivalent to:

```text
Create centered rectangle

Extrude 10 mm

Select top face

Create four Ø8 through holes

Select specified outer edges

Apply 2 mm chamfer
```

The exact Python syntax remains a compiler responsibility.

---

# 50. Correction Example

Suppose validation finds:

```text
Expected hole diameter = 8 mm

Generated = 10 mm
```

The Correction Agent should locate:

```text
parameter = hole_diameter
```

and modify:

```text
10 → 8
```

Then:

```text
CFP v2
 ↓
recompile
 ↓
validate
```

No arbitrary Python repair is necessary.

---

# 51. Structural Error Example

Suppose a hole was interpreted as a pocket.

Current:

```json
{
  "operation": "CUT_EXTRUDE"
}
```

Correct interpretation:

```json
{
  "operation": "HOLE"
}
```

The correction happens at feature level.

---

# 52. Pattern Correction Example

Initial model:

```text
4 independent HOLE features
```

Detected symmetry suggests:

```text
1 HOLE
+
LINEAR_PATTERN / rectangular pattern
```

The Correction Agent may rewrite the feature structure while preserving final geometry.

This improves CAD editability.

---

# 53. Feature Plan Quality Metrics

Besides final geometric accuracy, we can evaluate CFP quality.

Potential metrics:

```text
supported-operation rate

parameter completeness

dependency validity

feature count accuracy

feature type accuracy

pattern recognition accuracy

editable-history quality

critical-assumption count
```

---

# 54. Feature Sequence Quality

Exact original CAD history is not required.

Therefore we should distinguish:

```text
geometry equivalence

feature semantic equivalence

exact modeling-history equivalence
```

POC 1 requires the first two.

It does not require exact historical equivalence.

---

# 55. Preferred Modeling Principles

When multiple construction strategies produce the same geometry, prefer:

```text
fewer unnecessary features

recognizable engineering features

explicit symmetry

explicit patterns

named dimensions

simple sketches

stable references
```

For example:

```text
four separate identical holes
```

is less desirable than:

```text
one hole + pattern
```

when the drawing clearly describes a pattern.

---

# 56. Self-Correction Interface

The validator should return errors in CFP terms.

Example:

```json
{
  "error_type": "dimension_mismatch",
  "feature_id": "F003",
  "parameter": "diameter",
  "expected": 8.0,
  "observed": 10.0
}
```

rather than:

```text
Rendered model looks wrong.
```

This dramatically simplifies correction.

---

# 57. User Correction Interface

The UI should also modify CFP/CDR fields.

Example:

```text
Detected Feature:
4 × Ø8 through holes

User changes:
Ø8 → Ø10
```

Then:

```text
CDR updated
 ↓
CFP parameter updated
 ↓
CAD recompiled
```

---

# 58. CFP Revision History

Every generated revision should be retained.

Example:

```text
CFP v1
AI initial generation

CFP v2
automatic validation correction

CFP v3
user corrected hole diameter

CFP v4
final validated model
```

---

# 59. Revision Object

```json
{
  "revision": 3,
  "trigger": "user_correction",
  "changes": [
    {
      "path": "parameters.hole_diameter",
      "old_value": 8,
      "new_value": 10
    }
  ]
}
```

---

# 60. Benchmark Mode

During the Ortho2CAD benchmark:

```text
CFP generation may use only
information extracted from the raster benchmark input.
```

Disabled:

```text
vector-derived geometry

human correction

ground-truth feature history

ground-truth CAD during inference
```

The resulting CadQuery/STEP is then evaluated against the same ground truth.

---

# 61. Direct Baseline vs Structured Extrudely

A very important experiment will be:

```text
A:
Raster → VLM → CadQuery

B:
Raster → CDR → CFP → Compiler → CadQuery
```

This isolates the value of the structured architecture.

---

# 62. Hybrid Benchmark

A separate Extrudely experiment can use:

```text
Raster
+
DXF/vector geometry
      ↓
     CDR
      ↓
     CFP
```

This should not be presented as a direct Ortho2CAD comparison, but as the enhanced industrial mode.

---

# 63. Initial CFP Implementation Priority

### CFP Phase 1

Implement:

```text
SKETCH
EXTRUDE
CUT_EXTRUDE
HOLE
```

This gives us direct coverage of much of the Ortho2CAD-style geometry.

### CFP Phase 2

Add:

```text
COUNTERBORE
COUNTERSINK
LINEAR_PATTERN
CIRCULAR_PATTERN
MIRROR
```

### CFP Phase 3

Add:

```text
REVOLVE
REVOLVE_CUT
CHAMFER
FILLET
```

This reaches our complete POC 1 intermediate geometry scope.

---

# 64. Why This Development Order Matters

If we try to implement every supported feature immediately, debugging becomes difficult.

Instead:

```text
Simple benchmark geometry
        ↓
stable CDR
        ↓
stable CFP
        ↓
stable compiler
        ↓
advanced feature support
```

This keeps the benchmark path working while complexity is added incrementally.

---

# 65. CFP Success Criteria

The CAD Feature Plan is successful if:

1. every generated feature belongs to the supported vocabulary
2. every dimensional parameter is traceable
3. dependencies are explicit
4. uncertainty is preserved
5. the plan can be deterministically compiled
6. the same plan produces reproducible CAD
7. validation errors can identify affected features
8. targeted corrections do not require arbitrary Python editing
9. feature history remains reasonably engineering-friendly
10. benchmark mode remains free of privileged information

---

# 66. Final Data Architecture

Extrudely should therefore have three distinct representations:

```text
1. CDR
   What does the drawing contain?

             ↓

2. CFP
   How should the part be modeled?

             ↓

3. CadQuery
   How is that plan executed?
```

And the feedback path is:

```text
CAD Validation
      ↓
Feature-Level Error
      ↓
CFP Correction
      ↓
Recompile
```

This should become one of the central technical principles of Extrudely POC 1.