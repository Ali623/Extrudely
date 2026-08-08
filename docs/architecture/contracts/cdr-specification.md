# Extrudely POC 1
## Common Drawing Representation Specification v0.1

### 1. Purpose

The **Common Drawing Representation**, abbreviated **CDR**, is the structured intermediate format between drawing parsing and 3D CAD reasoning.

Its purpose is to make all supported input formats look the same to downstream components.

```text
PNG / JPEG ──→ Raster Parser ──┐
                               │
PDF Scan ────→ Raster Parser ──┤
                               │
DXF ─────────→ Vector Parser ──┤
                               ├──→ CDR ──→ 3D Reasoning
SVG ─────────→ Vector Parser ──┤
                               │
Vector PDF ──→ Vector Parser ──┘
```

The CAD reasoning system should not need to know whether a circle originally came from a DXF entity, computer vision, OCR-assisted interpretation, or user correction.

That information remains available through provenance metadata.

---

# 2. Core Design Principle

The CDR must clearly distinguish between:

### Observed information

Directly obtained from the drawing.

Examples:

```text
A circle exists here.

The annotation says Ø16.

This line is dashed.

The title block says mm.
```

### Inferred information

Derived through reasoning.

Examples:

```text
These three projected entities represent one hole.

The hole is through the entire part.

These four circles form a rectangular pattern.

This profile should become an extrusion.
```

These should never be silently mixed.

The CDR stores primarily **drawing evidence and geometric interpretation**.

The later **CAD Feature Plan** stores the proposed 3D construction strategy.

---

# 3. Top-Level CDR

The top-level structure is:

```text
DrawingDocument
│
├── document
├── metadata
├── sheets
├── views
├── primitives
├── annotations
├── dimensions
├── constraints
├── cross_view_links
├── feature_hypotheses
├── conflicts
├── uncertainties
├── provenance
└── corrections
```

For POC 1:

```text
sheets = exactly 1
parts  = exactly 1
```

The schema should nevertheless avoid assumptions that would prevent later extension.

---

# 4. Document Object

```json
{
  "document_id": "DOC_000123",
  "schema_version": "0.1",
  "created_at": "...",
  "input_type": "DXF",
  "source_files": [],
  "processing_mode": "hybrid",
  "benchmark_mode": false
}
```

### `input_type`

Allowed values:

```text
PNG
JPEG
PDF_RASTER
PDF_VECTOR
PDF_HYBRID
DXF
SVG
```

### `processing_mode`

```text
raster
vector
hybrid
```

### `benchmark_mode`

When:

```text
true
```

the pipeline must enforce Ortho2CAD-compatible restrictions.

---

# 5. Source File Object

Every uploaded file is registered.

```json
{
  "source_id": "SRC_001",
  "filename": "part_123.pdf",
  "mime_type": "application/pdf",
  "sha256": "...",
  "page_count": 1
}
```

Hashes help guarantee experiment reproducibility.

---

# 6. Drawing Metadata

```json
{
  "part_name": "Mounting Bracket",
  "part_number": "BR-1042",
  "material": "EN AW-6061",
  "language": "en",
  "units": "mm",
  "scale": "1:2",
  "projection_system": "first_angle"
}
```

Each value must include confidence and provenance.

Therefore internally:

```json
{
  "units": {
    "value": "mm",
    "confidence": 0.99,
    "status": "confirmed",
    "evidence_ids": ["EVID_014"]
  }
}
```

---

# 7. Standard Field Wrapper

Important extracted values should use a common structure:

```json
{
  "value": 16.0,
  "confidence": 0.97,
  "status": "observed",
  "evidence_ids": ["EVID_101", "EVID_102"]
}
```

Possible status values:

```text
observed
inferred
user_confirmed
user_corrected
conflicted
unknown
```

This pattern should be reused throughout the CDR.

---

# 8. Confidence Scale

Use normalized confidence:

```text
0.00 to 1.00
```

Suggested interpretation:

| Confidence | Interpretation |
|---:|---|
| 0.95–1.00 | Very strong evidence |
| 0.85–0.95 | High confidence |
| 0.70–0.85 | Reasonable but should be checked |
| 0.50–0.70 | Ambiguous |
| <0.50 | Do not automatically trust |

These thresholds should remain configurable.

They are not final engineering acceptance thresholds.

---

# 9. Evidence Object

Every meaningful interpretation should point to evidence.

```json
{
  "evidence_id": "EVID_101",
  "source_id": "SRC_001",
  "source_type": "ocr",
  "page": 1,
  "view_id": "VIEW_FRONT",
  "region": [102, 220, 166, 247],
  "raw_value": "Ø16",
  "confidence": 0.98
}
```

Possible `source_type` values:

```text
raster_geometry
vector_geometry
ocr
title_block
dimension_entity
vlm
cross_view_reasoning
geometry_rule
user
```

---

# 10. Coordinate Systems

This needs to be carefully standardized.

The CDR should support three coordinate spaces.

## A. Pixel coordinates

Used for raster images.

```text
origin = top-left
x → right
y → down
```

Example:

```json
{
  "coordinate_system": "pixel",
  "x": 425,
  "y": 318
}
```

---

# 11. Normalized 2D Coordinates

Every raster primitive should also have normalized coordinates.

```text
x ∈ [0,1]
y ∈ [0,1]
```

This makes results independent of image resolution.

Example:

```json
{
  "x": 0.421,
  "y": 0.312
}
```

---

# 12. Engineering Coordinates

Whenever drawing scale or explicit vector coordinates are available:

```text
unit = mm or inch
```

Example:

```json
{
  "coordinate_system": "engineering",
  "x": 45.0,
  "y": 32.0,
  "unit": "mm"
}
```

Engineering coordinates should be preferred for CAD reconstruction when sufficiently reliable.

---

# 13. Local View Coordinate System

Each orthographic view should receive a local coordinate frame.

Example:

```text
Front View:

u → horizontal
v → vertical
```

The view object defines how:

```text
u, v
```

map conceptually to:

```text
X, Y, Z
```

in the reconstructed part.

Example:

```text
front:
u → X
v → Z

top:
u → X
v → Y

right:
u → Y
v → Z
```

Projection-system handling must adjust orientation appropriately.

---

# 14. View Object

Example:

```json
{
  "view_id": "VIEW_FRONT",
  "view_type": "front",
  "confidence": 0.98,
  "projection_system": "first_angle",
  "bounding_box": [0.10, 0.15, 0.48, 0.61],
  "coordinate_frame": {
    "u_axis": "X",
    "v_axis": "Z"
  }
}
```

Allowed POC 1 view types:

```text
front
top
left
right
section
unknown
```

---

# 15. Section View Object

Simple sections should include:

```json
{
  "view_id": "VIEW_SECTION_AA",
  "view_type": "section",
  "section_label": "A-A",
  "section_type": "full",
  "confidence": 0.91
}
```

POC 1 should not attempt advanced section types initially.

---

# 16. Primitive Base Object

All geometric primitives should share:

```json
{
  "primitive_id": "PRIM_001",
  "view_id": "VIEW_FRONT",
  "primitive_type": "line",
  "line_style": "visible",
  "confidence": 0.97,
  "source": "dxf",
  "evidence_ids": []
}
```

---

# 17. Supported Primitive Types

Initial POC vocabulary:

```text
line
circle
arc
polyline
rectangle
ellipse
centerline
construction_line
hatch_region
unknown_curve
```

Avoid introducing dozens of primitive classes unnecessarily.

---

# 18. Line Primitive

```json
{
  "primitive_id": "PRIM_001",
  "primitive_type": "line",
  "view_id": "VIEW_FRONT",
  "start": [10.0, 20.0],
  "end": [80.0, 20.0],
  "line_style": "visible",
  "confidence": 0.99
}
```

---

# 19. Line Styles

Important engineering line styles:

```text
visible
hidden
center
construction
dimension
extension
section
unknown
```

This distinction matters significantly for 3D reconstruction.

A dashed hidden line should not be treated as ordinary visible geometry.

---

# 20. Circle Primitive

```json
{
  "primitive_id": "PRIM_021",
  "primitive_type": "circle",
  "view_id": "VIEW_TOP",
  "center": [45.0, 30.0],
  "radius": 8.0,
  "line_style": "visible",
  "confidence": 0.99
}
```

---

# 21. Arc Primitive

```json
{
  "primitive_id": "PRIM_030",
  "primitive_type": "arc",
  "view_id": "VIEW_FRONT",
  "center": [20.0, 20.0],
  "radius": 5.0,
  "start_angle": 0,
  "end_angle": 90
}
```

Angles should use one consistent convention.

Recommended:

```text
degrees
counterclockwise
```

---

# 22. Profile Object

Connected primitives may form a profile.

```json
{
  "profile_id": "PROFILE_001",
  "view_id": "VIEW_FRONT",
  "primitive_ids": [
    "PRIM_001",
    "PRIM_002",
    "PRIM_003",
    "PRIM_004"
  ],
  "closed": true,
  "confidence": 0.97
}
```

Profiles become particularly important for extrusion and revolve reasoning.

---

# 23. Annotation Object

Raw annotations should be preserved separately from their interpretation.

```json
{
  "annotation_id": "ANN_001",
  "view_id": "VIEW_TOP",
  "raw_text": "4X Ø8 THRU",
  "normalized_text": "4X Ø8 THRU",
  "language": "en",
  "confidence": 0.97
}
```

---

# 24. Dimension Object

Dimensions should not remain plain text.

Example:

```json
{
  "dimension_id": "DIM_001",
  "dimension_type": "diameter",
  "nominal_value": 8.0,
  "unit": "mm",
  "quantity": 4,
  "termination": "through",
  "references": ["PRIM_021"],
  "confidence": 0.98
}
```

---

# 25. Supported Dimension Types

Initial vocabulary:

```text
linear
horizontal
vertical
diameter
radius
angle
depth
spacing
coordinate
unknown
```

---

# 26. Tolerance Object

```json
{
  "tolerance": {
    "type": "bilateral",
    "upper": 0.05,
    "lower": -0.05,
    "unit": "mm"
  }
}
```

Other possible types:

```text
bilateral
unilateral
limit
fit_designation
none
```

POC 1 stores these but does not perform tolerance-stack analysis.

---

# 27. Thread Annotation

Example:

```json
{
  "annotation_id": "ANN_THREAD_01",
  "annotation_type": "thread",
  "standard": "metric",
  "nominal_diameter": 10,
  "pitch": 1.5,
  "designation": "M10x1.5",
  "geometry_mode": "simplified"
}
```

Possible standards:

```text
metric
UNC
UNF
unknown
```

---

# 28. Hole Specification

Hole information should have a dedicated semantic representation.

```json
{
  "hole_spec_id": "HOLE_01",
  "diameter": 8.0,
  "quantity": 4,
  "termination": "through",
  "depth": null,
  "counterbore": null,
  "countersink": null,
  "thread": null
}
```

Counterbore example:

```json
{
  "counterbore": {
    "diameter": 14.0,
    "depth": 5.0
  }
}
```

---

# 29. Constraint Object

Constraints represent geometric relationships.

```json
{
  "constraint_id": "CONST_001",
  "constraint_type": "concentric",
  "entities": [
    "PRIM_021",
    "PRIM_022"
  ],
  "confidence": 0.99
}
```

---

# 30. Supported Constraint Types

POC 1:

```text
parallel
perpendicular
horizontal
vertical
coincident
concentric
tangent
equal
symmetric
aligned
equal_spacing
same_radius
same_diameter
```

---

# 31. Symmetry Object

Example:

```json
{
  "symmetry_id": "SYM_01",
  "view_id": "VIEW_TOP",
  "axis": {
    "type": "vertical",
    "position": 50.0
  },
  "entity_groups": [
    ["PRIM_021", "PRIM_022"]
  ],
  "confidence": 0.95
}
```

---

# 32. Pattern Hypothesis

Repeated features can be represented before full 3D CAD reasoning.

Example:

```json
{
  "pattern_id": "PAT_01",
  "pattern_type": "rectangular",
  "member_entities": [
    "PRIM_021",
    "PRIM_022",
    "PRIM_023",
    "PRIM_024"
  ],
  "count": 4,
  "spacing_x": 60.0,
  "spacing_y": 30.0,
  "confidence": 0.94
}
```

Other POC 1 types:

```text
linear
rectangular
circular
mirror
```

---

# 33. Cross-View Link Object

This is crucial.

Example:

```json
{
  "link_id": "CVL_001",
  "link_type": "same_feature",
  "entities": [
    {
      "view_id": "VIEW_TOP",
      "primitive_ids": ["PRIM_021"]
    },
    {
      "view_id": "VIEW_FRONT",
      "primitive_ids": ["PRIM_055", "PRIM_056"]
    }
  ],
  "feature_hypothesis": "through_hole",
  "confidence": 0.92
}
```

This says:

```text
top-view circle
+
front-view hidden edges
=
probably the same 3D feature
```

---

# 34. Cross-View Relation Types

Initial vocabulary:

```text
same_edge
same_face
same_feature
projected_correspondence
shared_center
shared_boundary
shared_axis
unknown
```

---

# 35. 3D Geometric Hypothesis

The CDR may contain preliminary 3D interpretations, but not CAD operations.

Example:

```json
{
  "hypothesis_id": "HYP_001",
  "hypothesis_type": "cylindrical_void",
  "source_entities": [
    "PRIM_021",
    "PRIM_055",
    "PRIM_056"
  ],
  "diameter": 8.0,
  "axis": "Z",
  "confidence": 0.94
}
```

Notice that this does **not** say:

```text
CadQuery.hole()
```

That belongs later in the CAD Feature Plan.

---

# 36. Feature Hypothesis Vocabulary

Potential POC 1 hypotheses:

```text
prismatic_volume
cylindrical_volume
cylindrical_void
pocket
slot
counterbore
countersink
revolved_volume
revolved_cut
edge_fillet
edge_chamfer
linear_pattern
circular_pattern
mirror
```

These represent engineering interpretation, not implementation.

---

# 37. Conflict Object

Conflicting evidence must be explicit.

Example:

```json
{
  "conflict_id": "CONFLICT_001",
  "property": "PRIM_021.diameter",
  "candidates": [
    {
      "value": 16.0,
      "source": "dimension_annotation",
      "confidence": 0.99
    },
    {
      "value": 16.6,
      "source": "raster_geometry",
      "confidence": 0.73
    }
  ],
  "resolution": {
    "value": 16.0,
    "method": "weighted_evidence",
    "confidence": 0.98
  }
}
```

---

# 38. Unresolved Conflict

If evidence remains too close:

```json
{
  "resolution": null,
  "status": "review_required"
}
```

This should propagate downstream.

The CAD Reasoner must know that the affected feature is uncertain.

---

# 39. Uncertainty Object

Uncertainty is different from conflict.

A conflict means:

```text
two sources disagree
```

Uncertainty means:

```text
insufficient evidence exists
```

Example:

```json
{
  "uncertainty_id": "UNC_001",
  "property": "hole_depth",
  "reason": "no depth annotation and hidden lines are inconclusive",
  "confidence": 0.44,
  "requires_review": true
}
```

---

# 40. Unknown Values

Never invent values to satisfy the schema.

Use:

```json
{
  "value": null,
  "confidence": 0.0,
  "status": "unknown"
}
```

This is much safer than forcing a guessed dimension into the CAD pipeline.

---

# 41. User Correction Object

Every correction should be recorded rather than overwriting history.

```json
{
  "correction_id": "CORR_001",
  "target": "DIM_001.nominal_value",
  "old_value": 18.0,
  "new_value": 16.0,
  "source": "user",
  "timestamp": "..."
}
```

The current value becomes:

```text
16.0
```

but the history remains auditable.

---

# 42. User Confirmation

A user may also confirm an existing interpretation.

```json
{
  "correction_id": "CORR_002",
  "target": "HYP_004",
  "action": "confirm"
}
```

This should raise the downstream trust level.

---

# 43. Provenance Chain

A final parameter should be traceable back through the pipeline.

Example:

```text
CAD hole diameter = 16 mm
        │
        ▼
Feature Plan parameter
        │
        ▼
CDR Dimension DIM_001
        │
        ├── OCR: Ø16
        │
        ├── DXF circle: radius 8
        │
        └── cross-view geometry consistent
```

This gives us true engineering explainability.

---

# 44. Raster/Vector Fusion

Suppose raster parsing detects:

```text
circle center = (45.3, 31.9)
radius = 8.2
confidence = 0.78
```

DXF gives:

```text
circle center = (45.0, 32.0)
radius = 8.0
confidence = 1.00
```

and the annotation says:

```text
Ø16
confidence = 0.98
```

The CDR should preserve all three observations.

Then create a resolved entity:

```json
{
  "center": [45.0, 32.0],
  "radius": 8.0,
  "confidence": 0.99,
  "evidence_ids": [
    "DXF_CIRCLE_21",
    "OCR_DIM_11",
    "RASTER_CIRCLE_42"
  ]
}
```

---

# 45. Important Rule for Explicit Dimensions

Scaled drawing geometry must not automatically override explicit engineering dimensions.

For example:

```text
Drawing scale = 1:2

Measured image diameter ≈ 15.7 mm

Explicit annotation = Ø16
```

The resulting intended geometry should normally be:

```text
16 mm
```

provided that no stronger contradictory evidence exists.

---

# 46. Geometry Normalization

Vector geometry from different formats should be normalized.

Example input units:

```text
DXF = inches

title block = mm
```

The CDR should convert engineering coordinates to the document's resolved working unit.

Internally we should probably use:

```text
millimeters
```

as the canonical unit.

Original unit values remain stored in provenance.

---

# 47. Recommended Canonical Unit

Internally:

```text
length = millimeters
angle  = degrees
```

For inch drawings:

```text
0.5 inch
```

becomes internally:

```text
12.7 mm
```

while display metadata retains:

```text
original unit = inch
```

This simplifies geometry operations considerably.

---

# 48. Bounding Boxes

Every view and annotation should have a bounding region.

Normalized example:

```json
{
  "x_min": 0.12,
  "y_min": 0.21,
  "x_max": 0.44,
  "y_max": 0.56
}
```

This supports UI highlighting.

When the engineer clicks:

```text
Hole Ø16
```

the UI can highlight the exact source annotation.

---

# 49. CDR and UI Relationship

The UI should consume the CDR directly.

Example:

```text
Detected Features

✓ Ø16 through hole          98%
✓ 4-hole rectangular array 94%
⚠ R5 edge fillet           71%
```

Clicking a result can reveal:

```text
source annotation

relevant drawing region

vector geometry

cross-view evidence
```

---

# 50. CDR Validation

Before the CAD reasoning stage begins, the CDR itself should be validated.

Checks include:

```text
units resolved?

projection resolved?

at least 2 usable views?

view orientations known?

main profiles closed?

dimension references valid?

cross-view links valid?

critical conflicts unresolved?
```

---

# 51. CDR Quality Score

The CDR can receive an overall readiness score.

Example:

```text
Metadata completeness        0.97
View detection               0.98
Geometry extraction          0.92
Dimension extraction         0.96
Cross-view consistency       0.88
Unresolved ambiguity         0.08

CDR readiness                0.93
```

This score should help decide whether automatic CAD generation is safe.

---

# 52. CAD Generation Gate

Possible policy:

```text
CDR readiness ≥ 0.85
    → automatic generation

0.65–0.85
    → generate with warnings

< 0.65
    → request targeted review
```

These numbers are placeholders and should be calibrated experimentally.

---

# 53. CDR Benchmark Mode

When benchmarking against Ortho2CAD:

```text
vector evidence = disabled
user corrections = disabled
external metadata = disabled
ground-truth CAD = unavailable during inference
```

The CDR is generated entirely from the permitted benchmark raster input.

This preserves fair comparison.

---

# 54. CDR Hybrid Mode

Normal Extrudely operation allows:

```text
raster evidence
+
vector evidence
+
annotation evidence
+
cross-view reasoning
```

This becomes the strongest production configuration.

---

# 55. Proposed Serialization

Recommended format:

```text
JSON
```

with schema validation through:

```text
Pydantic
```

Reasons:

- easy debugging
- human readable
- model friendly
- API friendly
- versionable
- easy experiment storage
- straightforward Python integration

---

# 56. Simplified Complete Example

A very simplified CDR might look like:

```json
{
  "document": {
    "document_id": "DOC_001",
    "schema_version": "0.1",
    "input_type": "DXF"
  },

  "metadata": {
    "units": "mm",
    "projection_system": "first_angle",
    "language": "en"
  },

  "views": [
    {
      "view_id": "FRONT",
      "view_type": "front"
    },
    {
      "view_id": "TOP",
      "view_type": "top"
    }
  ],

  "primitives": [
    {
      "primitive_id": "C1",
      "view_id": "TOP",
      "primitive_type": "circle",
      "center": [50, 30],
      "radius": 8
    }
  ],

  "dimensions": [
    {
      "dimension_id": "D1",
      "dimension_type": "diameter",
      "nominal_value": 16,
      "unit": "mm",
      "references": ["C1"]
    }
  ],

  "cross_view_links": [
    {
      "link_id": "L1",
      "link_type": "same_feature",
      "feature_hypothesis": "through_hole"
    }
  ],

  "feature_hypotheses": [
    {
      "hypothesis_id": "H1",
      "hypothesis_type": "cylindrical_void",
      "diameter": 16,
      "confidence": 0.96
    }
  ]
}
```

The downstream CAD reasoner can turn this into:

```text
HOLE
diameter = 16
termination = THROUGH
```

inside the CAD Feature Plan.

---

# 57. What Must Not Be Stored in the CDR

The CDR should not contain arbitrary generated code such as:

```python
cq.Workplane("XY").box(...).faces(">Z").hole(...)
```

It also should not prematurely decide:

```text
Extrude Feature #3
```

unless we intentionally classify that as a feature hypothesis.

The construction sequence belongs in the **CAD Feature Plan**.

---

# 58. CDR vs CAD Feature Plan

The separation should remain:

```text
CDR
=
What does the drawing tell us?
```

versus:

```text
CAD Feature Plan
=
How should we construct the part?
```

Example:

```text
CDR:

closed rectangular profile
100 × 60
depth evidence = 20
```

then:

```text
CAD Feature Plan:

SKETCH rectangle 100 × 60
EXTRUDE 20
```

This distinction is one of the most important architecture decisions in Extrudely.

---

# 59. Proposed CDR Pipeline

```text
                   RAW DRAWING
                        │
                        ▼
               MODALITY-SPECIFIC PARSING
                        │
                        ▼
                 RAW OBSERVATIONS
                        │
                        ▼
                 NORMALIZATION
                        │
                        ▼
                 EVIDENCE FUSION
                        │
                        ▼
               CROSS-VIEW MATCHING
                        │
                        ▼
              GEOMETRIC CONSTRAINTS
                        │
                        ▼
               FEATURE HYPOTHESES
                        │
                        ▼
                       CDR
                        │
                        ▼
                READINESS CHECK
                        │
                        ▼
                CAD FEATURE PLAN
```

---

# 60. Initial CDR Implementation Priority

The first implementation should not attempt every field immediately.

### Phase CDR-1

Implement:

```text
document

metadata

views

lines

circles

arcs

profiles

dimensions

evidence

confidence
```

### Phase CDR-2

Add:

```text
constraints

cross-view links

hole specifications

symmetry

patterns
```

### Phase CDR-3

Add:

```text
feature hypotheses

conflicts

uncertainties

user corrections
```

### Phase CDR-4

Add:

```text
tolerances

simple threads

section-view relationships
```

This gives us a practical development order without weakening the final architecture.

---

# 61. CDR Success Criteria

The CDR is successful if:

1. raster and vector parsers can generate the same schema
2. source evidence remains traceable
3. dimensions can reference actual geometry
4. view correspondences can be represented explicitly
5. conflicts are not silently discarded
6. uncertainty can propagate downstream
7. user corrections can modify structured values
8. the CAD Reasoner does not require source-format-specific logic
9. the UI can explain where important values came from
10. benchmark mode can disable privileged vector information

---

# 62. Key Architecture Decision

The recommended representation therefore becomes:

```text
Raw Drawing
    ↓
Observed Evidence
    ↓
Common Drawing Representation
    ↓
3D Geometric Interpretation
    ↓
CAD Feature Plan
    ↓
CadQuery Compiler
```

rather than:

```text
Drawing
    ↓
VLM
    ↓
Python
```

This gives Extrudely a structured and testable foundation while preserving the ability to compare the raster-only configuration directly against Ortho2CAD.