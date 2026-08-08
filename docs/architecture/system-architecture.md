# Extrudely POC 1
## System Architecture v0.1

### 1. Architecture Goal

Extrudely should reconstruct parametric 3D CAD models from raster and vector engineering drawings while remaining:

- benchmarkable against Ortho2CAD
- geometrically explainable
- editable
- robust to uncertainty
- deployable on-premise
- extensible to more complex engineering drawings later

The architecture deliberately avoids relying on a single end-to-end `drawing → Python code` model.

Ortho2CAD demonstrates that a VLM can directly translate rasterized orthographic drawings into editable CadQuery and improve reconstruction using supervised fine-tuning and geometry-grounded reinforcement learning. Extrudely will retain the strengths of this approach while introducing explicit drawing understanding, raster/vector fusion, structured CAD planning, and iterative validation.

---

# 2. High-Level Architecture

```text
                         ENGINEERING DRAWING
                                │
                         INPUT ORCHESTRATOR
                                │
                 ┌──────────────┴──────────────┐
                 │                             │
                 ▼                             ▼
          RASTER PIPELINE                VECTOR PIPELINE
     PNG / JPEG / Scan / PDF          DXF / SVG / Vector PDF
                 │                             │
                 ▼                             ▼
       Visual Geometry Parser         Exact Geometry Parser
       Annotation Parser              Text / Layer Parser
       View Detector                  View Reconstruction
                 │                             │
                 └──────────────┬──────────────┘
                                ▼
                COMMON DRAWING REPRESENTATION
                         [CDR / Drawing IR]
                                │
                                ▼
                   CROSS-VIEW GEOMETRY ENGINE
                                │
                                ▼
                      3D FEATURE REASONER
                                │
                                ▼
                       CAD FEATURE PLAN
                             [CFP]
                                │
                                ▼
                  DETERMINISTIC CAD COMPILER
                                │
                                ▼
                         CADQUERY CODE
                                │
                                ▼
                     CADQUERY / OPENCASCADE
                                │
                      ┌─────────┴─────────┐
                      ▼                   ▼
                    STEP              B-Rep / Mesh
                      │                   │
                      └─────────┬─────────┘
                                ▼
                       VALIDATION ENGINE
                                │
             ┌──────────────────┼──────────────────┐
             ▼                  ▼                  ▼
       Projection Check   Dimension Check    Geometry Check
             │                  │                  │
             └──────────────────┼──────────────────┘
                                ▼
                         VALIDATION SCORE
                                │
                   ┌────────────┴────────────┐
                   │                         │
                PASSED                    FAILED
                   │                         │
                   ▼                         ▼
                OUTPUT              CORRECTION AGENT
                                             │
                                             ▼
                                    MODIFY FEATURE PLAN
                                             │
                                             └──────→ Recompile
```

---

# 3. Architectural Principle

Extrudely should separate four fundamentally different problems:

### Layer A
**What is present in the drawing?**

### Layer B
**What 3D geometry does that drawing imply?**

### Layer C
**What CAD operations should construct that geometry?**

### Layer D
**Does the generated CAD actually agree with the drawing?**

Mixing all four into one VLM prompt makes debugging, benchmarking, correction, and engineering validation difficult.

---

# 4. Module 1: Input Orchestrator

The Input Orchestrator receives:

- PNG
- JPEG
- PDF
- DXF
- SVG

Its first task is to classify the input.

```text
PDF
 │
 ├── Contains usable vector objects?
 │        │
 │        ├── YES → Vector + Raster Hybrid
 │        │
 │        └── NO  → Raster Pipeline
 │
 └── Render preview for visual interpretation
```

For DXF and SVG, both a structured vector representation and a raster preview should be generated.

This is important because the VLM may understand layout or semantic relationships visually even when exact geometry is available structurally.

---

# 5. Module 2: Raster Preprocessing

Raster preprocessing converts drawings into a standardized representation before AI interpretation.

Tasks include:

- resolution normalization
- grayscale conversion where appropriate
- deskewing
- scan rotation correction
- moderate denoising
- contrast normalization
- line preservation
- page boundary detection
- drawing-region extraction

The original image must always be retained.

Preprocessing should never permanently replace the original because thin engineering lines may disappear during aggressive cleanup.

The original and processed images should both remain available to downstream models.

---

# 6. Module 3: Drawing Layout Detection

The system identifies regions such as:

```text
FRONT VIEW

TOP VIEW

SIDE VIEW

SECTION VIEW

TITLE BLOCK

NOTES

DIMENSION REGIONS
```

For clean drawings, geometric layout rules may already identify views.

For scanned or complicated drawings, a trained detector can assist.

Recent engineering-drawing research supports a modular architecture of this kind. Hybrid systems using oriented-object detection followed by specialized document/VLM parsing have shown strong structured extraction performance on dimensions, threads, title blocks, and other engineering annotations.

A candidate POC implementation could use:

```text
YOLO-style detector
        +
orientation-aware annotation detection
        +
specialized parser / VLM
```

rather than sending the complete drawing directly to OCR.

---

# 7. Module 4: Raster Geometry Parser

This module extracts geometric evidence from raster views.

Detected primitives can include:

- straight lines
- arcs
- circles
- centerlines
- hidden lines
- contour boundaries
- symmetry axes

Each primitive receives:

```text
primitive ID

view ID

geometry

line type

pixel coordinates

normalized coordinates

confidence

source region
```

Exact dimensions should not be inferred purely from pixel scale when an explicit dimension exists.

---

# 8. Module 5: Engineering Annotation Parser

This component interprets:

- linear dimensions
- diameters
- radii
- angles
- depths
- hole callouts
- counterbore notation
- countersink notation
- simple thread callouts
- tolerances
- units
- title-block values

Example:

```text
Drawing text:
4X Ø8 THRU

Parsed representation:

type        = hole
quantity    = 4
diameter    = 8
termination = through
unit        = mm
confidence  = 0.97
```

Another example:

```text
M10 × 1.5

type          = metric_thread
nominal       = 10
pitch         = 1.5
geometry_mode = simplified
```

The system should preserve the original text along with the structured interpretation.

---

# 9. Module 6: Vector Geometry Parser

Vector inputs should not be treated as images when exact geometry is available.

Drawing2CAD provides useful evidence for this design direction because it retains vector primitives and maps them toward parametric CAD operations rather than discarding geometric precision through rasterization.

### DXF parser

Extract:

- LINE
- ARC
- CIRCLE
- POLYLINE
- SPLINE where manageable
- TEXT
- MTEXT
- DIMENSION
- layer information
- line style
- coordinates
- blocks where relevant

### SVG parser

Extract:

- line
- polyline
- polygon
- circle
- ellipse
- path
- text
- transformation matrices

### Vector PDF parser

Attempt extraction of:

- line segments
- curves
- text
- coordinates
- font information
- line styles

A raster rendering should still be produced for semantic interpretation.

---

# 10. Module 7: Common Drawing Representation

This is the most important interface in the architecture.

All input modalities must eventually produce the same **Common Drawing Representation**, abbreviated **CDR**.

The CDR should contain observed engineering evidence, not final CAD code.

Conceptually:

```text
DrawingDocument
│
├── Metadata
│
├── Views
│   ├── Front
│   ├── Top
│   ├── Side
│   └── Section
│
├── Primitives
│
├── Annotations
│
├── Constraints
│
├── CrossViewLinks
│
├── Provenance
│
└── Uncertainties
```

---

# 11. CDR Metadata

```text
document_id

part_name

part_number

language

units

scale

projection_type

material

input_type

source_files
```

Every automatically extracted field receives:

```text
value

confidence

source

evidence
```

Example:

```text
units:
    value: mm
    confidence: 0.99
    source: title_block
```

---

# 12. CDR Views

Every view becomes an independent structured object.

Example:

```text
View:
    id: V1
    type: front
    bounding_region: [...]
    orientation: front
    projection: first_angle
    confidence: 0.97
```

The CDR should not assume that all drawings have exactly three views because the POC supports two or three.

---

# 13. CDR Geometric Primitives

Example:

```text
Primitive:
    id: P102
    view: front
    type: circle
    center: [44.2, 31.7]
    radius: 7.9
    line_type: visible
    confidence: 0.94
    source: raster
```

For vector geometry:

```text
Primitive:
    id: P103
    view: front
    type: circle
    center: [45.0, 32.0]
    radius: 8.0
    line_type: visible
    confidence: 1.00
    source: dxf
```

The raw observations remain separate even when they appear to represent the same geometry.

The fusion engine decides whether they should be merged.

---

# 14. CDR Dimensions

Dimensions should explicitly reference geometry whenever possible.

Example:

```text
Dimension:
    id: D14
    type: diameter
    nominal: 16.0
    unit: mm

    tolerance:
        plus: 0.1
        minus: 0.1

    references:
        - P103

    confidence: 0.98
    source: annotation
```

This is much more useful than storing `"Ø16 ±0.1"` as plain text.

---

# 15. Evidence Provenance

Every important value should carry provenance.

Example:

```text
value: 16.0 mm

evidence:
    - OCR annotation Ø16
    - DXF circle radius 8.0
    - top-view correspondence
```

This enables conflict resolution.

If another source suggests:

```text
radius = 8.3
```

the system knows exactly which pieces of evidence disagree.

---

# 16. Conflict Resolver

The system should not have a universal rule such as:

```text
DXF always wins
```

or:

```text
OCR always wins
```

Instead it produces a weighted decision.

Example:

```text
Explicit dimension     0.99
DXF geometry           0.96
Cross-view consistency 0.95
Raster measurement     0.71
```

Result:

```text
hole diameter = 16 mm
confidence = 0.98
```

When evidence remains genuinely contradictory:

```text
status = REVIEW_REQUIRED
```

---

# 17. Cross-View Geometry Engine

This module establishes correspondence between views.

For example:

```text
Front view circle P31
        ↕
Top view hidden edges P92/P93
        ↕
Side view hidden edges P141/P142
```

may jointly represent:

```text
one cylindrical through-hole
```

The engine should reason using:

- projection alignment
- shared dimensions
- center alignment
- symmetry
- repeated spacing
- visible/hidden line relationships
- section-view evidence

This stage transforms independent 2D observations into coherent multi-view geometry.

---

# 18. Constraint Graph

A graph representation should store engineering relationships.

Nodes can represent:

```text
lines
circles
profiles
dimensions
features
```

Edges can represent:

```text
parallel

perpendicular

coincident

concentric

symmetric

equal

aligned

pattern_member

same_feature_across_view
```

The graph should allow deterministic geometry rules to complement VLM reasoning.

---

# 19. Module 8: 3D Feature Reasoner

The Feature Reasoner receives:

```text
CDR
+
constraint graph
+
drawing preview
```

and determines likely 3D features.

Example:

```text
Observed:

Front → rectangle
Top → rectangle
Side → rectangle
Dimensions → 100 × 60 × 20

Inference:

BASE_PRISM
width     = 100
height    = 60
thickness = 20
```

Another example:

```text
Top → four Ø8 circles
Front → hidden vertical pairs
Spacing → symmetric

Inference:

HOLE_PATTERN
count      = 4
diameter   = 8
termination = THROUGH
```

---

# 20. Recommended AI Responsibility

The VLM should primarily perform:

- semantic drawing interpretation
- ambiguous feature reasoning
- cross-view interpretation
- feature hypothesis generation
- candidate ranking assistance
- correction reasoning

The VLM should **not** be responsible for every exact coordinate calculation.

Exact geometry should use deterministic geometry whenever possible.

This leads to:

```text
AI decides WHAT the feature is.

Geometry engine determines WHERE it is.

CAD compiler determines HOW to construct it.
```

---

# 21. Main Open-Source Reasoning Model

The first strong candidate remains:

**Qwen3-VL-8B-Instruct**

This is especially useful because Ortho2CAD itself uses the Qwen3-VL family for raster-to-CadQuery reconstruction, giving us a meaningful architectural comparison rather than simply comparing different model scales.

An 8B-class model also fits our objective of a workstation-friendly deployment more realistically than a very large VLM.

The exact model is **not locked yet** and should be selected after a small evaluation.

---

# 22. Module 9: CAD Feature Plan

The Feature Reasoner should not directly generate Python.

Instead it creates a structured **CAD Feature Plan**, abbreviated **CFP**.

Example:

```text
Part
│
├── Feature 1
│   type: extrusion
│   sketch_plane: XY
│   profile: rectangle
│   width: 100
│   height: 60
│   distance: 20
│
├── Feature 2
│   type: hole_pattern
│   face: top
│   diameter: 8
│   termination: through
│   pattern: rectangular
│   count: 4
│
├── Feature 3
│   type: chamfer
│   distance: 2
│
└── Feature 4
    type: fillet
    radius: 3
```

Each feature must contain:

```text
feature_id

operation

parameters

dependencies

geometry references

evidence references

confidence
```

---

# 23. Why the Feature Plan Matters

Without a Feature Plan:

```text
Drawing
   ↓
AI
   ↓
arbitrary Python
```

A failure may be difficult to interpret.

With the Feature Plan:

```text
Drawing
   ↓
CDR
   ↓
Feature Plan
   ↓
Compiler
   ↓
CadQuery
```

we can identify:

```text
Feature 4 = incorrect hole depth
```

and change only:

```text
Feature 4.depth
```

before regenerating the model.

This is essential for targeted corrections and engineering explainability.

---

# 24. Supported Feature Plan Operations

POC 1 should initially define a closed vocabulary:

```text
SKETCH

EXTRUDE

CUT_EXTRUDE

HOLE

COUNTERBORE

COUNTERSINK

REVOLVE

LINEAR_PATTERN

CIRCULAR_PATTERN

MIRROR

CHAMFER

FILLET
```

Slots and pockets can initially be expressed using:

```text
SKETCH + CUT_EXTRUDE
```

rather than requiring dedicated operation types.

---

# 25. Module 10: Deterministic CadQuery Compiler

The Feature Plan should be compiled into CadQuery using deterministic templates/functions.

For example:

```text
Feature Plan:

operation = hole
diameter = 10
depth = through
```

becomes a known CadQuery construction.

This is preferable to asking an LLM to rewrite arbitrary Python every time.

CadQuery is well suited to this role because it provides scripted parametric modeling on top of OpenCascade/OCP and supports STEP export. Its current documentation also provides direct DXF and STEP import capabilities.

---

# 26. Why We Still Keep CadQuery Code

Although generation becomes structured, the final code remains:

```text
human-readable

editable

versionable

executable

portable

inspectable
```

Therefore our output requirements remain unchanged:

```text
model.py
model.step
```

---

# 27. Module 11: Secure CAD Execution

Generated CadQuery should execute inside a controlled environment.

Execution produces:

```text
success / failure

B-Rep

STEP

mesh

bounding box

volume

faces

edges
```

The runtime should enforce:

- execution timeout
- restricted file system
- limited imports
- controlled memory
- known CadQuery environment

This prevents malformed generated code from disrupting the POC service.

---

# 28. Validation Stage 1: CAD Validity

Before geometric accuracy is considered, verify:

```text
Did the CadQuery compile?

Did execution complete?

Was a solid generated?

Is the B-Rep valid?

Is the model non-empty?
```

These contribute to:

```text
Valid CadQuery Rate

Valid CAD Rate
```

which are required for Ortho2CAD comparison.

---

# 29. Validation Stage 2: Reprojection

The reconstructed CAD is rendered back into:

```text
front

top

side
```

using the projection convention detected from the original drawing.

Then compare:

```text
SOURCE FRONT ↔ GENERATED FRONT

SOURCE TOP   ↔ GENERATED TOP

SOURCE SIDE  ↔ GENERATED SIDE
```

Comparison should include:

- outer silhouette
- internal visible edges
- holes
- hidden geometry where practical
- feature locations

---

# 30. Validation Stage 3: Dimensional Validation

Because the CDR stores explicit dimensions, we can test the generated CAD directly.

Example:

```text
Drawing:

hole diameter = 16 mm

Generated CAD:

hole diameter = 15.92 mm

Absolute error = 0.08 mm

Relative error = 0.5%
```

This is more meaningful for engineering use than image similarity alone.

---

# 31. Validation Stage 4: Feature Validation

The system verifies that expected features exist.

Example:

```text
Expected:

4 × Ø8 THROUGH
2 mm chamfer
R3 fillet

Generated:

4 × Ø8 THROUGH  ✓
2 mm chamfer    ✓
R3 fillet       ✗
```

This creates feature-level error reporting.

---

# 32. Validation Stage 5: 3D Geometry Metrics

When ground-truth CAD is available, as in benchmark datasets, evaluate:

```text
3D IoU

Chamfer Distance

bounding-box difference

volume difference
```

The exact Ortho2CAD-compatible IoU implementation should be reproduced for the official benchmark rather than replaced with our own interpretation.

---

# 33. Validation Report

All validators produce one structured report.

Example:

```text
CAD valid                   PASS

Front silhouette            0.96

Top silhouette              0.93

Side silhouette             0.97

Dimension score             0.99

Feature score               0.88

3D IoU                      0.84

Detected mismatch:
    fillet radius incorrect

Recommended correction:
    Feature F7
```

---

# 34. Module 12: Correction Agent

The Correction Agent receives:

```text
CDR

CAD Feature Plan

Validation Report

rendered comparisons
```

It does **not** primarily edit Python.

Instead:

```text
Original:

F7:
    operation = fillet
    radius = 5

Correction:

F7:
    operation = fillet
    radius = 3
```

The compiler then regenerates the complete CadQuery program.

---

# 35. Iterative Validation Loop

```text
CAD Feature Plan v1
        │
        ▼
      CAD v1
        │
        ▼
    Validation
        │
        ▼
    score = 0.74
        │
        ▼
    Correction
        │
        ▼
CAD Feature Plan v2
        │
        ▼
      CAD v2
        │
        ▼
    Validation
        │
        ▼
    score = 0.91
```

The loop stops when:

```text
quality threshold reached

OR

maximum iteration count reached
```

A small limit such as two or three correction iterations is a reasonable initial engineering target, but this value remains to be experimentally calibrated against the two-minute runtime objective.

---

# 36. Candidate Generation

When confidence is high:

```text
1 CAD Feature Plan
```

When confidence is low:

```text
Candidate A
Candidate B
Candidate C
```

Each candidate goes through the same compiler and validator.

Ranking should primarily use measurable geometry rather than model self-confidence alone.

Example:

```text
Candidate A   validation 0.94

Candidate B   validation 0.86

Candidate C   validation 0.69
```

Candidate A becomes the default result.

---

# 37. Human Correction Path

The user should be able to modify structured information.

Example:

```text
Detected:
Ø18

User:
No, Ø16

CDR updated:
D12.nominal = 16
```

Only downstream stages need rerunning.

Similarly:

```text
Detected:
blind hole

User:
through hole

Feature Plan updated
        ↓
CadQuery regenerated
```

This avoids reprocessing the entire document unnecessarily.

---

# 38. Web Application Architecture

```text
                    WEB FRONTEND
                         │
              ┌──────────┼──────────┐
              │          │          │
           Drawing       3D      Validation
            Viewer      Viewer      Panel
              │          │          │
              └──────────┼──────────┘
                         │
                         ▼
                     REST API
                         │
                         ▼
                  PIPELINE SERVICE
                         │
       ┌─────────────────┼─────────────────┐
       ▼                 ▼                 ▼
   Parsing           AI Reasoning      CAD Service
   Service             Service          Service
                                             │
                                             ▼
                                       Validator
```

For the POC, these do not need to be physically separate microservices.

They can initially exist as clean Python modules behind one backend.

---

# 39. UI Main Screen

The desired workflow is:

```text
┌────────────────────────────────────────────────────┐
│ Upload Drawing                                     │
├──────────────────────┬─────────────────────────────┤
│                      │                             │
│ Original 2D Drawing  │        3D CAD Preview       │
│                      │                             │
├──────────────────────┼─────────────────────────────┤
│ Detected information │ Validation                  │
│                      │                             │
│ Dimensions            │ Front:  ✓                  │
│ Features              │ Top:    ⚠                  │
│ Confidence            │ Side:   ✓                  │
│ Warnings              │                             │
├──────────────────────┴─────────────────────────────┤
│ [Correct] [Regenerate] [Export STEP] [View Code]  │
└────────────────────────────────────────────────────┘
```

---

# 40. Mismatch Visualization

When validation finds a difference, the UI should support something conceptually similar to:

```text
ORIGINAL VIEW

vs

GENERATED CAD PROJECTION

vs

DIFFERENCE OVERLAY
```

Typical highlighted issues:

```text
missing hole

incorrect diameter

wrong pocket depth

incorrect outline

misaligned feature

missing fillet
```

---

# 41. Experiment Tracking

Every run receives a unique experiment ID.

Store:

```text
input

input hash

preprocessing settings

model version

model configuration

CDR

Feature Plan

generated code

STEP

validation results

iteration history

user corrections

runtime

final status
```

This gives us reproducible benchmark experiments.

---

# 42. Benchmark Architecture

A dedicated benchmark switch should exist.

```text
mode = ORTHO2CAD_BENCHMARK
```

When enabled:

```text
Raster input only              ENABLED

Vector parser                  DISABLED

DXF metadata                   DISABLED

SVG metadata                   DISABLED

Additional company metadata    DISABLED

Human correction               DISABLED

Ground truth during inference  DISABLED
```

The system receives only information available in the benchmark drawing.

This prevents accidental leakage and preserves fair comparison.

---

# 43. Ortho2CAD Benchmark Flow

```text
SAME TEST PNG
      │
      ├──────────────→ Ortho2CAD
      │                    │
      │                    ▼
      │                   CAD
      │                    │
      │
      └──────────────→ Extrudely Raster
                           │
                           ▼
                          CAD
                           │
             ┌─────────────┴─────────────┐
             ▼                           ▼
          Validity                    3D IoU
```

This is our apples-to-apples research track.

---

# 44. Full Extrudely Evaluation

Separate from the Ortho2CAD benchmark:

```text
Extrudely Raster

Extrudely Noisy Raster

Extrudely Vector

Extrudely Hybrid
```

This allows us to measure the value of each architectural component.

---

# 45. Recommended Ablation Experiments

The architecture naturally supports comparisons such as:

```text
Direct VLM → CadQuery

vs

Raster → CDR → Feature Plan → CadQuery


Raster CDR

vs

Vector CDR


Raster only

vs

Vector only

vs

Hybrid


No self-correction

vs

Self-correction


VLM-generated Python

vs

Structured Feature Plan + deterministic compiler
```

These experiments will tell us whether each new component actually improves performance.

---

# 46. Initial Technology Candidates

These are implementation candidates, not locked decisions.

| Layer | Initial Candidate |
|---|---|
| Backend | Python |
| API | FastAPI |
| Raster processing | OpenCV |
| Detection | YOLO family / equivalent |
| Engineering annotation parser | specialized VLM/document model |
| Main VLM | Qwen3-VL-8B class |
| DXF parsing | ezdxf / CadQuery-compatible tooling |
| SVG parsing | Python SVG geometry parser |
| PDF parsing | vector extraction + raster rendering |
| Schema | Pydantic / JSON |
| Constraint graph | NetworkX/custom geometry graph |
| 2D geometry | Shapely/custom analytic geometry |
| CAD | CadQuery |
| Kernel | OpenCascade/OCP |
| 3D processing | OpenCascade + mesh tooling |
| Experiment data | PostgreSQL/files/object store |
| 3D browser viewer | Three.js-compatible viewer |
| Containerization | Docker |

CadQuery's current documented toolchain supports parametric Python modeling, DXF import, and STEP export on top of OpenCascade/OCP, which makes it a strong fit for the planned compiler and CAD execution layer.

---

# 47. Proposed Model Strategy

Rather than using one large model for everything:

```text
SPECIALIZED PERCEPTION
        +
GENERAL VLM REASONING
        +
DETERMINISTIC GEOMETRY
        +
DETERMINISTIC CAD COMPILER
```

This keeps the AI concentrated on tasks where semantic reasoning is valuable.

A possible configuration is:

```text
Lightweight detector
    → layout / annotation localization

Specialized OCR/VLM
    → dimensions / text / symbols

Qwen3-VL-class model
    → multi-view reasoning / feature planning

Geometry engine
    → coordinates / constraints

CadQuery compiler
    → exact CAD construction
```

This modular approach is also supported by recent engineering-document research, where specialized localization plus structured VLM parsing performed better than treating the document as generic OCR.

---

# 48. Proposed Training Strategy

Training can happen progressively.

### Stage 1: Zero-shot prototype

Use pretrained models and deterministic vector parsing.

Goal:

```text
prove end-to-end architecture
```

### Stage 2: Annotation adaptation

Fine-tune specialized perception modules on:

```text
dimensions

holes

threads

views

title blocks
```

### Stage 3: CAD reasoning adaptation

Train:

```text
Drawing / CDR
      ↓
CAD Feature Plan
```

using synthetic paired data.

### Stage 4: Geometric feedback adaptation

Use validation results as training or ranking signals.

This is where techniques related to geometry-grounded feedback can eventually be introduced.

---

# 49. Target Inference Architecture

The production path should eventually look approximately like:

```text
                    INPUT
                      │
                      ▼
                  PARSING
                      │
                     CDR
                      │
                      ▼
               FEATURE REASONER
                      │
                     CFP
                      │
                      ▼
                 CAD COMPILER
                      │
                   CadQuery
                      │
                      ▼
                  VALIDATION
                      │
          ┌───────────┴───────────┐
          │                       │
        PASS                    CORRECT
          │                       │
          ▼                       │
        OUTPUT ◄──────────────────┘
```

---

# 50. Main Architectural Differentiation

The conceptual difference is:

### Ortho2CAD-style approach

```text
Raster Drawing
      ↓
     VLM
      ↓
CadQuery Program
      ↓
     CAD
```

Ortho2CAD shows this direct raster-to-CadQuery paradigm can work strongly when combined with task-specific SFT and geometry-grounded RL.

### Extrudely approach

```text
Raster / Vector Drawing
          ↓
   Structured Evidence
          ↓
 Cross-View Geometry
          ↓
    CAD Feature Plan
          ↓
 Deterministic Compiler
          ↓
      Parametric CAD
          ↓
 Geometric Verification
          ↓
      Self-Correction
```

The hypothesis is that this additional structure will provide:

```text
better dimensional fidelity

better vector utilization

better interpretability

better correction

better industrial robustness

better human review

while maintaining competitive benchmark accuracy
```

---

# 51. Architecture Boundary

POC 1 ends at:

```text
Drawing
   ↓
Understanding
   ↓
Feature Plan
   ↓
CadQuery
   ↓
STEP
   ↓
Validation
   ↓
Engineer-reviewed result
```

It does not attempt to become:

```text
a full CAD editor

a PLM system

a manufacturing planning system

a complete GD&T engine
```

---

# 52. Architecture Decision to Lock Next

The next design artifact should be the **Common Drawing Representation schema**.

This deserves its own specification because every major module depends on it:

```text
Raster Parser ──┐
                │
Vector Parser ──┼──→ CDR ──→ Geometry Reasoning
                │
User Correction ┘
```

Once the CDR schema is stable, we can independently develop the raster parser, vector parser, reasoning model, benchmark adapter, and UI without tightly coupling them.