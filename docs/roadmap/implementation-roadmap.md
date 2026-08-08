# Extrudely POC 1
## Implementation Roadmap v0.1

### 1. Development Strategy

The project should be developed as a sequence of working vertical slices.

The rule is:

```text
Benchmark first
      ↓
Minimal CAD reconstruction
      ↓
Structured CDR
      ↓
Structured CFP
      ↓
Validation
      ↓
Self-correction
      ↓
Vector support
      ↓
Hybrid support
      ↓
Advanced POC features
      ↓
Real-company evaluation
      ↓
Demo application
```

At every major milestone, Extrudely should remain executable and benchmarkable.

---

# 2. Phase 0: Repository and Reproducibility Foundation

## Objective

Create the project foundation before implementing AI components.

### Repository structure

```text
extrudely/
│
├── apps/
│   └── web/
│
├── src/
│   └── extrudely/
│       │
│       ├── input/
│       ├── raster/
│       ├── vector/
│       ├── cdr/
│       ├── reasoning/
│       ├── cfp/
│       ├── compiler/
│       ├── cad/
│       ├── validation/
│       ├── correction/
│       ├── benchmark/
│       └── common/
│
├── configs/
│
├── datasets/
│   ├── raw/
│   ├── processed/
│   └── splits/
│
├── experiments/
│
├── tests/
│   ├── unit/
│   ├── integration/
│   └── benchmark/
│
├── scripts/
│
├── docker/
│
├── docs/
│
└── README.md
```

---

# 3. Core Development Environments

Initially maintain separate environments for:

### AI

```text
PyTorch
Transformers
Qwen-VL
PEFT
```

### CAD

```text
CadQuery
OCP/OpenCascade
STEP
```

### Geometry/Data

```text
OpenCV
NumPy
Shapely
ezdxf
Pydantic
```

### Application

```text
FastAPI
frontend
3D viewer
```

Containerization should be introduced early enough to guarantee reproducibility.

CadQuery remains a suitable CAD layer because it provides parametric Python modeling on OpenCascade/OCP and supports high-quality STEP output.

---

# 4. Phase 1: Reproduce Ortho2CAD Benchmark

## Objective

Before developing Extrudely:

> **Run Ortho2CAD ourselves and reproduce its evaluation pipeline.**

The public Ortho2CAD repository currently contains:

```text
inference/
orthographic_drawing_generation/
src/
```

and includes 100 test examples for both evaluated datasets. It also separates VLM training/inference, CAD IoU evaluation, and orthographic drawing generation into dedicated environments.

---

# 5. Phase 1 Tasks

### 1. Clone and freeze Ortho2CAD

Record:

```text
commit hash
dependencies
model weights
dataset version
evaluation configuration
```

### 2. Download benchmark data

Obtain:

```text
DeepCAD / GenCAD-Code orthographic data

Fusion 360 reconstruction data

100-example DeepCAD test set

100-example Fusion 360 test set
```

### 3. Run provided inference

### 4. Generate predicted CadQuery/CAD

### 5. Execute official IoU evaluation

### 6. Store results per sample

```text
sample_id
valid
IoU
runtime
generated code
STEP
```

---

# 6. Phase 1 Acceptance Gate

Phase 1 passes when we can execute:

```text
python benchmark_orthocad.py
```

and obtain a reproducible table such as:

| Sample | Valid | IoU |
|---|---:|---:|
| 001 | ✓ | ... |
| 002 | ✓ | ... |
| ... | ... | ... |

plus:

```text
Mean IoU
Median IoU
Valid CAD rate
```

Only after this works do we begin claiming comparisons against Ortho2CAD.

---

# 7. Phase 2: Extrudely Minimal Vertical Slice

## Objective

Build the smallest possible Extrudely pipeline.

Initially support only:

```text
Raster PNG
+
3 views
+
simple extrusion geometry
+
simple holes
```

Pipeline:

```text
PNG
 ↓
VLM
 ↓
minimal CDR
 ↓
minimal CFP
 ↓
CadQuery compiler
 ↓
STEP
```

No sophisticated OCR.

No DXF.

No correction loop.

No UI.

---

# 8. Minimal CDR v0

Implement only:

```text
Document
Metadata
Views
Profiles
Lines
Circles
Dimensions
Evidence
Confidence
```

Use Pydantic models.

Example:

```text
cdr/models.py
```

with classes such as:

```text
DrawingDocument

DrawingView

Primitive

Dimension

Evidence
```

---

# 9. Minimal CFP v0

Support:

```text
SKETCH
EXTRUDE
CUT_EXTRUDE
HOLE
```

This deliberately overlaps strongly with the simpler geometry represented in Ortho2CAD-style datasets.

---

# 10. Minimal Deterministic Compiler

Implement:

```text
CFP
 ↓
CadQuery
```

without an LLM.

Example mappings:

```text
SKETCH rectangle
       ↓
Workplane rectangle

EXTRUDE
       ↓
extrude()

HOLE
       ↓
hole()

CUT_EXTRUDE
       ↓
cutBlind()/cutThruAll()
```

The compiler must be completely deterministic.

---

# 11. Compiler Unit Tests

Create manually defined CFP examples:

```text
plate

plate + hole

plate + four holes

block + pocket

stepped block
```

For each:

```text
CFP
 ↓
compiler
 ↓
CadQuery
 ↓
STEP
```

Verify:

```text
valid solid
correct dimensions
repeatable result
```

The compiler should be almost perfectly reliable before AI-generated CFPs are introduced.

---

# 12. Phase 2 Acceptance Gate

At least:

```text
20 manually created CFP test parts
```

should compile successfully.

Target:

```text
100% valid CadQuery
100% valid STEP
```

for valid CFP inputs.

If the compiler itself is unreliable, AI evaluation becomes meaningless.

---

# 13. Phase 3: Raster Drawing Understanding

## Objective

Replace manually defined CFP inputs with information extracted from drawings.

Pipeline:

```text
Raster drawing
      ↓
View detection
      ↓
Geometry / annotation understanding
      ↓
CDR
```

---

# 14. Phase 3A: View Detection

Detect:

```text
front
top
right/left
simple section
title block
```

Start with benchmark drawings because their layout is standardized.

Initially use:

```text
geometry/layout heuristics
+
VLM classification
```

before training a dedicated detector.

---

# 15. Phase 3B: Primitive Extraction

Implement raster extraction for:

```text
straight lines
circles
arcs
visible contours
hidden lines
centerlines
```

Use deterministic computer vision where useful.

Do not make the VLM estimate every pixel coordinate.

---

# 16. Phase 3C: Dimension Extraction

Extract:

```text
overall dimensions
diameters
radii
depths
linear dimensions
```

Store:

```text
raw annotation

normalized value

unit

geometry reference

confidence

evidence region
```

For the first benchmark, priority goes to the dimension types actually present in Ortho2CAD drawings.

---

# 17. Phase 3D: CDR Debug Viewer

Before building the final web app, create a simple internal visualization tool.

Example:

```text
Original Drawing

+
Detected Front View

+
Detected Top View

+
Detected Circles

+
Detected Dimensions

+
Confidence labels
```

This will save a huge amount of debugging time.

---

# 18. Phase 3 Acceptance Gate

Create a manually inspected set of approximately:

```text
50 benchmark drawings
```

and evaluate:

```text
view detection accuracy

dimension extraction accuracy

circle detection accuracy

main profile accuracy

hidden-line classification
```

Do not proceed purely based on visual impressions.

---

# 19. Phase 4: CDR → CFP Reasoning

## Objective

Introduce the main AI reasoning component.

Input:

```text
drawing image
+
CDR
```

Output:

```text
structured CFP
```

not Python.

---

# 20. Main Model Experiment

Start with an 8B-class multimodal model.

A strong initial candidate remains:

```text
Qwen3-VL-8B-Instruct
```

which is also the base family used by Ortho2CAD. This keeps architecture comparison more meaningful. The current Qwen3-VL ecosystem includes 8B models and multimodal variants built on the same foundation.

Do not lock the model permanently before testing alternatives.

---

# 21. Structured Output

The model must produce schema-constrained CFP output.

Example:

```json
{
  "features": [
    {
      "operation": "EXTRUDE",
      "sketch_id": "SK01",
      "distance": 20
    },
    {
      "operation": "HOLE",
      "diameter": 8,
      "termination": "through_all"
    }
  ]
}
```

Then validate through Pydantic.

Invalid outputs are rejected before CAD execution.

---

# 22. First Core Experiment

Run:

```text
100 Ortho2CAD DeepCAD test drawings
```

through:

```text
Extrudely Raster
```

Measure:

```text
Valid CFP
Valid CadQuery
Valid STEP
3D IoU
```

At this point we obtain the first genuine:

```text
Ortho2CAD
vs
Extrudely
```

comparison.

---

# 23. Phase 5: Self-Validation

## Objective

Make the generated CAD evaluate itself against the drawing.

Pipeline:

```text
STEP
 ↓
orthographic rendering
 ↓
front/top/side projections
 ↓
comparison against source
```

Implement:

```text
silhouette comparison

edge comparison

dimension comparison

feature presence comparison
```

---

# 24. Validation v1

Start with:

### CAD validity

```text
B-Rep valid?
solid exists?
```

### Bounding dimensions

```text
width
height
depth
```

### Projection similarity

```text
front silhouette IoU
top silhouette IoU
side silhouette IoU
```

### Explicit dimensions

```text
expected
vs
measured CAD
```

---

# 25. Validation Acceptance

Validator results must be structured.

Example:

```json
{
  "feature_id": "F04",
  "type": "dimension_mismatch",
  "expected": 8.0,
  "observed": 10.0,
  "severity": "critical"
}
```

Not:

```text
The CAD looks a bit incorrect.
```

---

# 26. Phase 6: Self-Correction

## Objective

Use validation failures to modify the CFP.

Pipeline:

```text
CFP v1
 ↓
CAD
 ↓
Validation
 ↓
Errors
 ↓
Correction Agent
 ↓
CFP v2
```

Limit initially to:

```text
maximum 2 correction iterations
```

Then experimentally evaluate whether a third iteration provides enough improvement to justify runtime.

---

# 27. Correction Experiments

Measure:

```text
IoU before correction

IoU after correction

dimension error before

dimension error after

% improved

% unchanged

% degraded
```

Self-correction remains enabled only if it measurably improves results.

---

# 28. Phase 6 Acceptance Gate

Target:

```text
majority of corrected samples improve

very low degradation rate

runtime remains practical
```

We should not keep a correction loop merely because it looks technically impressive.

---

# 29. Phase 7: Vector Pipeline

## Objective

Add:

```text
DXF
SVG
vector PDF
```

without changing the downstream CDR/CFP architecture.

---

# 30. DXF Parser

Recommended initial implementation:

```text
ezdxf
```

Extract:

```text
LINE
ARC
CIRCLE
LWPOLYLINE
TEXT
MTEXT
DIMENSION
layers
line styles
blocks where necessary
```

Normalize everything into CDR entities.

---

# 31. SVG Parser

Extract:

```text
line
polyline
polygon
circle
ellipse
path
text
transforms
```

Convert to the same CDR primitives used by DXF and raster.

---

# 32. PDF Router

For every PDF:

```text
PDF
 ↓
inspect objects
 ↓
vector content available?
```

If yes:

```text
vector parser
+
render raster preview
```

If no:

```text
raster pipeline
```

This automatically produces:

```text
PDF_VECTOR
PDF_RASTER
PDF_HYBRID
```

---

# 33. Vector Acceptance Test

Take a CAD part and export:

```text
PNG
DXF
SVG
PDF
```

All four should produce geometrically compatible CDR objects.

Test:

```text
same circle diameter

same view alignment

same overall dimensions

same feature interpretation
```

---

# 34. Phase 8: Raster + Vector Fusion

## Objective

Create the full Extrudely architecture.

```text
Raster evidence
       +
Vector evidence
       +
Annotations
       ↓
Evidence Fusion
       ↓
Resolved CDR
```

Example:

```text
OCR:
Ø16

DXF:
radius = 8.0

Raster:
radius ≈ 8.2
```

Resolved:

```text
diameter = 16 mm
confidence = high
```

---

# 35. Conflict Resolver

Implement evidence ranking based on:

```text
explicit dimensions

vector geometry

cross-view consistency

OCR confidence

raster measurements

drawing scale
```

Never silently discard conflicting values.

Create:

```text
Conflict object
```

when disagreement remains meaningful.

---

# 36. Hybrid Ablation

Run identical parts through:

```text
Raster only

Vector only

Raster + Vector
```

Measure:

```text
IoU

dimension accuracy

feature accuracy

runtime
```

This gives us direct evidence of whether hybrid processing is worthwhile.

---

# 37. Phase 9: Intermediate CAD Features

Once the core pipeline is stable, expand the CFP/compiler.

Add in this order:

### 9A

```text
COUNTERBORE
COUNTERSINK
```

### 9B

```text
LINEAR_PATTERN
CIRCULAR_PATTERN
MIRROR
```

### 9C

```text
REVOLVE
REVOLVE_CUT
```

### 9D

```text
CHAMFER
FILLET
```

This order is intentional.

Fillets/chamfers should come last because stable semantic edge selection is more difficult.

---

# 38. Phase 10: Drawing Robustness

Add controlled synthetic degradation.

Generate:

```text
clean
mild
moderate
```

versions using:

```text
blur

noise

JPEG compression

skew

reduced resolution

broken lines

contrast variation
```

Measure degradation curves rather than one noisy score.

---

# 39. Phase 11: Engineering Annotation Extensions

Add:

```text
counterbore symbols

countersink symbols

simple thread callouts

basic tolerances

English/German annotations

title-block extraction
```

Threads remain:

```text
metadata / simplified geometry
```

not explicit helical geometry.

---

# 40. Phase 12: Two-View Reconstruction

The benchmark path initially uses three views.

Once stable, evaluate:

```text
3 views
vs
2 views
```

For two-view inputs:

```text
detect missing information

increase uncertainty appropriately

generate multiple candidates when justified
```

The system should not pretend that genuinely ambiguous geometry is certain.

---

# 41. Phase 13: Simple Section Views

Add recognition of:

```text
SECTION A-A
```

and basic full sections.

Use sections primarily to resolve:

```text
internal steps

blind holes

counterbores

internal cavities
```

Advanced offset/broken sections remain outside POC 1.

---

# 42. Phase 14: Synthetic Multimodal Dataset

Create a generation pipeline:

```text
Ground Truth STEP
       │
       ├── PNG
       ├── noisy PNG
       ├── DXF
       ├── SVG
       └── PDF
```

Store:

```text
model ID

drawing modalities

ground-truth CDR where possible

ground-truth CFP where available

STEP
```

Split by CAD model ID before generating modalities.

---

# 43. Synthetic Dataset Priorities

Do not immediately generate hundreds of thousands of examples.

Start with approximately:

```text
1,000–5,000 models
```

to validate:

```text
pipeline correctness

format consistency

training usefulness
```

Only scale after showing that synthetic data improves results.

---

# 44. Phase 15: Model Adaptation

Training sequence:

### Experiment T0

```text
Zero-shot VLM
```

### T1

```text
LoRA / PEFT on drawing → CFP
```

### T2

```text
full or stronger adaptation if justified
```

### T3

```text
geometry-aware ranking / feedback
```

Do not start by training from scratch.

The 24–48 GB GPU constraint strongly favors parameter-efficient adaptation for the first model experiments.

---

# 45. Training Target

Prefer:

```text
Drawing + CDR
      ↓
CFP
```

over:

```text
Drawing
 ↓
raw Python
```

This substantially reduces the output vocabulary and constrains the reasoning problem.

---

# 46. Phase 16: Real Company Dataset

Prepare approximately:

```text
30–50 parts
```

where possible.

Divide into:

```text
development examples

final untouched test examples
```

The final product benchmark must remain unseen during model tuning.

---

# 47. Real Drawing Categories

Try to cover:

```text
plates

brackets

machined blocks

hole patterns

counterbored components

simple shafts

flanges

revolved parts

filleted/chamfered components
```

All must remain inside the agreed POC scope.

---

# 48. Phase 17: Simple Web Application

Only after the backend works.

Main screen:

```text
┌─────────────────────────────────────────┐
│ Upload Drawing                          │
├───────────────────┬─────────────────────┤
│ Original Drawing  │ 3D CAD              │
│                   │                     │
├───────────────────┼─────────────────────┤
│ Extracted Data    │ Validation          │
│ Views             │ IoU / projection    │
│ Dimensions        │ Mismatches          │
│ Features          │ Confidence          │
├───────────────────┴─────────────────────┤
│ Correct | Regenerate | Export           │
└─────────────────────────────────────────┘
```

---

# 49. UI POC Features

Implement:

```text
upload

drawing display

CDR inspection

dimension list

feature list

confidence warnings

interactive 3D preview

projection comparison

mismatch overlay

targeted corrections

regenerate

download STEP

download CadQuery
```

No general-purpose CAD editor.

---

# 50. Phase 18: Full Benchmark Run

Freeze:

```text
code version

model version

dataset version

hardware

configuration
```

Then run:

### Research

```text
Ortho2CAD reproduced

Direct VLM

Extrudely Raster

Extrudely Raster + validation

Extrudely Raster + correction
```

### Engineering

```text
Clean Raster

Noisy Raster

DXF

SVG

Vector PDF

Hybrid

Real company drawings
```

---

# 51. Phase 19: Final POC Decision

Produce a final decision table:

| Requirement | Target | Result | Pass |
|---|---:|---:|---:|
| Valid CAD | defined benchmark | | |
| Ortho2CAD comparison | competitive | | |
| Dimensional accuracy | agreed threshold | | |
| Feature accuracy | agreed threshold | | |
| Real drawing reconstruction | agreed threshold | | |
| Runtime | ~<2 min | | |
| GPU | 24–48 GB | | |
| Parametric editability | required | | |

Only then decide:

```text
POC successful

POC requires iteration

or

architecture needs revision
```

---

# 52. Recommended Milestones

## M0
**Benchmark Ready**

Ortho2CAD reproduced locally.

## M1
**CAD Compiler Ready**

Manual CFP → valid CadQuery → STEP.

## M2
**Raster MVP**

Raster → CDR → CFP → STEP.

## M3
**Benchmarkable Extrudely**

Run exact Ortho2CAD 100-sample test.

## M4
**Validated Extrudely**

Automatic reprojection and dimensional validation.

## M5
**Self-Correcting Extrudely**

CFP correction loop operational.

## M6
**Vector Extrudely**

DXF/SVG/PDF → CDR → CAD.

## M7
**Hybrid Extrudely**

Raster + vector evidence fusion.

## M8
**Intermediate Features**

Patterns, revolves, counterbores, countersinks, fillets, chamfers.

## M9
**Industrial Robustness**

Noisy scans, English/German, title blocks, simple sections.

## M10
**Real-World Validation**

Held-out company drawings evaluated.

## M11
**POC Demo**

Web interface and final benchmark report.

---

# 53. What We Should Code First

The first actual development sequence should be:

```text
1. Set up Extrudely repository

2. Clone/freeze Ortho2CAD

3. Run its 100-example DeepCAD benchmark

4. Extract/reuse its CAD IoU evaluator

5. Implement Pydantic CDR models

6. Implement Pydantic CFP models

7. Implement CFP → CadQuery compiler

8. Create 10–20 manual CFP test models

9. Generate STEP and validate geometry

10. Only then connect the VLM
```

This order is important.

The first AI code should **not** be written until:

```text
CFP → CAD → STEP → evaluation
```

works reliably without AI.

---

# 54. First Technical Prototype

The first Extrudely part should be deliberately simple:

```text
rectangular plate

overall dimensions

4 through holes
```

Input:

```text
three-view raster drawing
```

Expected CDR:

```text
base profile

width

height

thickness

four circles

hole diameter

hole locations
```

Expected CFP:

```text
SKETCH rectangle

EXTRUDE

HOLE

PATTERN
```

Expected output:

```text
model.py

model.step
```

Validation:

```text
bounding dimensions

hole diameter

hole locations

front/top/side reprojection
```

If we can make this work end-to-end with traceability, we have the core Extrudely architecture.

---

# 55. Second Technical Prototype

Use:

```text
machined block

pocket

through holes

counterbore
```

This tests:

```text
CUT_EXTRUDE

HOLE

COUNTERBORE

cross-view reasoning
```

---

# 56. Third Technical Prototype

Use:

```text
stepped shaft / flange
```

This tests:

```text
REVOLVE

REVOLVE_CUT

CIRCULAR_PATTERN

simple chamfer
```

At this point we have covered most of the POC geometry families.

---

# 57. Development Principle

At every stage:

```text
Do not add another AI model
until we know why the current stage fails.
```

Failures should first be classified as:

```text
perception problem

CDR problem

reasoning problem

CFP problem

compiler problem

validation problem
```

Only then should we decide whether the solution needs:

```text
better rules

better geometry processing

better training data

or a better AI model
```

This prevents the project from becoming an uncontrolled collection of VLM prompts.

---

# 58. Immediate Starting Point

The first implementation sprint should therefore focus entirely on:

```text
Ortho2CAD reproduction
        +
CDR/CFP Python schemas
        +
deterministic CadQuery compiler
        +
manual test parts
```

No frontend.

No DXF yet.

No model fine-tuning yet.

No self-correction yet.

When those foundations pass, we connect the first raster/VLM path.