# Extrudely POC 1
## Benchmark and Evaluation Plan v0.1

### 1. Purpose

The benchmark plan must answer two different questions:

1. **Can Extrudely compete fairly with Ortho2CAD on the same raster drawing-to-CAD task?**
2. **Does the broader Extrudely architecture provide useful engineering advantages when vector information, dimensions, validation, and real-world drawings are available?**

These questions must never be mixed into one headline score.

The evaluation will therefore contain two primary tracks:

```text
TRACK A
Research Benchmark
Fair comparison with Ortho2CAD

TRACK B
Engineering Benchmark
Evaluation of full Extrudely capabilities
```

A third external benchmark track may be added using newer public CAD benchmarks where appropriate.

---

# 2. Benchmark Philosophy

Extrudely should not claim improvement over Ortho2CAD by giving itself richer input.

A fair comparison requires:

```text
same test drawing
same raster information
same ground-truth CAD
same evaluation method
no vector information
no user correction
no hidden metadata
```

The full Extrudely product mode can then be evaluated separately.

---

# 3. Benchmark Track A: Ortho2CAD-Compatible Evaluation

The official comparison pipeline will be:

```text
                 SAME RASTER DRAWING
                         │
             ┌───────────┴───────────┐
             │                       │
             ▼                       ▼
        Ortho2CAD              Extrudely Raster
             │                       │
             ▼                       ▼
         CadQuery                  CFP
             │                       │
             │                       ▼
             │                 CadQuery Compiler
             │                       │
             ▼                       ▼
            STEP                    STEP
             │                       │
             └───────────┬───────────┘
                         ▼
                  SAME EVALUATOR
```

Ortho2CAD directly converts rasterized orthographic drawings into CadQuery. Its authors evaluate using executable CAD validity and 3D IoU against ground-truth STEP geometry.

---

# 4. Ortho2CAD Input Conditions

For the direct benchmark, Extrudely receives only:

- PNG raster drawing
- orthographic drawing information visible in the image
- the same instruction context allowed by the baseline

Ortho2CAD's generated drawings contain:

- front view
- top view
- right view
- first-angle projection
- visible edges
- dashed hidden edges
- three bounding-box dimensions

The authors note that these dimensions do not fully dimension every feature.

Extrudely must not access the original vector geometry during this benchmark.

---

# 5. Benchmark Dataset A1: DeepCAD / GenCAD-Code

This will be the **primary benchmark**.

Ortho2CAD uses DeepCAD-derived orthographic drawings paired with GenCAD-Code CadQuery programs for supervised fine-tuning. The paper reports:

```text
Training:   147,289
Test:         7,355
Final evaluation subset: 100
```

and uses the same fixed 100-example evaluation subset as CAD-Coder.

The Ortho2CAD repository includes the 100-example test data under its `inference` folder, which makes exact replication practical.

### Important reproducibility note

The Ortho2CAD paper currently lists a validation count of 9,027, while the current GenCAD-Code Hugging Face metadata reports 8,204 validation examples.

Therefore:

> The actual files and split identifiers used by the Ortho2CAD repository must be treated as the authoritative reproduction source before training begins.

We should not silently reconstruct the split from dataset counts.

---

# 6. Benchmark Dataset A2: Fusion 360 Reconstruction

This will be the **secondary transfer/generalization benchmark**.

The Fusion 360 Reconstruction dataset contains human CAD construction sequences based primarily on sketch and extrusion operations. The original dataset contains 8,625 designs.

Ortho2CAD uses:

```text
Training: 6,900
Test:     1,725

Final evaluation subset: 100
```

and its repository also includes the corresponding 100-example inference set.

This benchmark is particularly important because it measures distribution transfer rather than only performance on DeepCAD-style geometry.

---

# 7. Baselines

The benchmark should contain several levels of comparison.

### Baseline B0: Published Ortho2CAD

Use the reported Ortho2CAD results as the published reference.

### Baseline B1: Reproduced Ortho2CAD

Run the public Ortho2CAD implementation locally.

This is preferable to relying only on reported paper values.

### Baseline B2: Base Open-Source VLM

Example:

```text
Qwen3-VL-8B-Instruct
```

without Extrudely-specific training.

### Baseline B3: Direct VLM-to-CadQuery

Same main VLM as Extrudely but without:

```text
CDR
CFP
deterministic compiler
```

This is extremely important.

It isolates whether our architecture provides value beyond changing the model.

### Baseline B4: Proprietary VLM

A strong current proprietary multimodal model may be evaluated as an external zero-shot reference.

It is not part of the production system.

---

# 8. Primary Benchmark Metrics

For direct comparison with Ortho2CAD, two metrics are mandatory.

## 8.1 Executable / Valid CAD Rate

Measure:

```text
number of outputs producing valid CAD
-------------------------------------
total benchmark examples
```

An output fails if:

- generated code does not parse
- runtime execution fails
- no solid is produced
- generated geometry is invalid

Ortho2CAD reports valid-code results together with geometric IoU.

---

# 9. 3D Intersection-over-Union

The primary geometric metric will be:

```text
IoU =
Volume(Prediction ∩ Ground Truth)
---------------------------------
Volume(Prediction ∪ Ground Truth)
```

For invalid models:

```text
IoU = 0
```

This matches the Ortho2CAD evaluation principle. The paper also states that predicted and target models are normalized and aligned before IoU calculation.

### Critical rule

We should use:

> **the Ortho2CAD/CAD-Coder evaluator itself wherever possible**

rather than implementing our own version and assuming the numbers are comparable.

---

# 10. Published Reference Target

The published Ortho2CAD benchmark remains our primary reference point.

For POC planning, the target should be interpreted as:

```text
Valid CAD:
approximately 100%

DeepCAD geometric accuracy:
approximately 0.79 mean 3D IoU
```

The exact reproduced value from the authors' evaluation code should be recorded before any Extrudely comparison is published.

Our internal benchmark table should ultimately contain:

| System | Valid CAD | Mean IoU |
|---|---:|---:|
| Ortho2CAD published | reference | reference |
| Ortho2CAD reproduced | measured | measured |
| Base VLM | measured | measured |
| Direct VLM → CadQuery | measured | measured |
| Extrudely Raster | measured | measured |

---

# 11. Zero-Shot Evaluation

Before any task-specific training:

```text
Pretrained VLM
      ↓
Extrudely architecture
      ↓
100-example test set
```

Measure:

- valid CAD
- IoU
- CDR correctness
- CFP correctness
- runtime

This tells us how much capability comes from architecture alone.

---

# 12. Fine-Tuned Evaluation

Then train/adapt using the official training data.

The test set remains untouched.

Evaluate:

```text
Fine-Tuned Direct VLM
vs
Fine-Tuned Extrudely
vs
Ortho2CAD
```

Where practical, training should use:

- the same underlying CAD models
- identical training/test membership
- no test-derived synthetic variants
- equivalent information access

This gives the fairest architectural comparison.

---

# 13. Train/Test Leakage Prevention

This is essential because Extrudely will create multiple modalities from the same CAD model.

Suppose:

```text
Part ABC
├── PNG
├── SVG
├── PDF
├── DXF
└── noisy PNG
```

All versions must belong to **one split only**.

Never allow:

```text
ABC.png → training

ABC.dxf → validation

ABC.pdf → test
```

That would leak the target geometry across modalities.

Therefore splitting must occur using:

```text
original CAD model ID
```

before rendering or format generation.

---

# 14. Synthetic Dataset Split

Recommended split:

```text
CAD MODEL IDS
      │
      ├── Train
      ├── Validation
      └── Test
```

Then generate modalities within each partition.

```text
TRAIN MODEL
   ├── PNG
   ├── PDF
   ├── DXF
   └── SVG

TEST MODEL
   ├── PNG
   ├── PDF
   ├── DXF
   └── SVG
```

No geometry crosses between partitions.

---

# 15. Engineering Track B

The full Extrudely evaluation will use:

```text
B1 Clean Raster

B2 Noisy Raster

B3 Vector

B4 Hybrid

B5 Real Company Drawings
```

These results must be reported separately.

---

# 16. Track B1: Clean Raster

Input:

- clean PNG/JPEG
- CAD-exported PDF raster
- clear dimensions
- two or three views

Purpose:

```text
measure normal raster performance
```

---

# 17. Track B2: Noisy Raster

Synthetic and real degradation should include controlled levels of:

- blur
- Gaussian noise
- compression
- reduced resolution
- skew
- broken thin lines
- uneven contrast

Suggested categories:

```text
Clean
Mild degradation
Moderate degradation
```

Severely damaged historical drawings remain outside POC 1.

---

# 18. Track B3: Vector

Input:

- DXF
- SVG
- vector PDF

The system may use:

- exact line coordinates
- circles
- arcs
- dimension entities
- text
- layers
- line styles

This track determines how much exact drawing geometry improves reconstruction.

---

# 19. Track B4: Hybrid

Hybrid mode receives:

```text
vector geometry
+
raster rendering
+
visual semantic reasoning
```

The hypothesis is:

> Vector geometry improves precision while raster/VLM reasoning improves semantic interpretation.

This should become the strongest Extrudely production configuration.

---

# 20. Current External Vector Benchmark Opportunity

The **ECCV 2026 CAD Challenge** currently provides:

```text
8,344 training samples
927 public test samples
```

with each training example containing:

- SVG TechDraw
- PDF TechDraw
- DXF TechDraw
- target STEP
- additional 3D renders

The public test set contains the same input modalities but hides the target STEP.

This dataset is highly relevant to Extrudely's vector pipeline.

### Important limitation

The official challenge allows both:

```text
3D render + TechDraw
```

while Extrudely's intended task is:

```text
2D engineering drawing → CAD
```

Therefore leaderboard scores are **not directly comparable** unless we also use the same official inputs.

For our project we can create:

```text
Extrudely TechDraw-Only Evaluation
```

using only:

- SVG
- PDF
- DXF

from the dataset.

This becomes an external robustness benchmark, not an Ortho2CAD benchmark.

---

# 21. CADBench as an Optional Diagnostic Benchmark

CADBench, released in May 2026, contains 18,000 evaluation samples across six benchmark families and five modalities, with metrics covering geometry, executability, and program compactness. Its authors specifically report that rankings vary considerably by metric and complexity.

CADBench does not exactly match our orthographic drawing task, so it should not replace Ortho2CAD.

However, it can later be useful for:

```text
general CAD reconstruction diagnostics

complexity analysis

program quality evaluation
```

---

# 22. Real Company Dataset

A small real-world test set is required for the product gate.

Recommended target:

```text
30–50 representative drawings
```

if enough examples are available.

The set should cover our declared POC scope.

Suggested categories:

```text
plates / brackets

machined blocks

hole patterns

counterbored parts

chamfered / filleted parts

simple shafts

flanges

simple revolved components
```

No training should occur on these exact test drawings.

---

# 23. Real Dataset Ground Truth

Each real drawing should ideally have:

```text
original engineering drawing

approved reference CAD / STEP

key dimensions

feature annotations
```

If reference CAD does not exist, a qualified engineer should create or verify ground truth.

---

# 24. Real Dataset Annotation

For evaluation, each test part should have a compact annotation record containing:

```text
overall dimensions

hole count

hole diameters

hole types

pocket count

revolved features

patterns

fillets

chamfers

important feature locations
```

This allows engineering evaluation beyond 3D IoU.

---

# 25. Dimensional Accuracy

For every dimension:

```text
Absolute Error =
|predicted - ground truth|
```

and:

```text
Relative Error =
|predicted - ground truth|
--------------------------
|ground truth|
```

Report:

```text
mean absolute error

median absolute error

mean relative error

95th percentile error

dimension pass rate
```

The actual acceptance threshold will be calibrated experimentally.

---

# 26. Dimension Pass Rule

The final rule should combine:

```text
absolute tolerance
+
relative tolerance
```

For example conceptually:

```text
PASS if

absolute error ≤ A

OR

relative error ≤ R
```

The values of `A` and `R` should not be fixed until we inspect the scale and precision of the real test drawings.

---

# 27. Feature Recognition Metrics

For each supported feature type:

```text
Precision

Recall

F1
```

Evaluate separately for:

- holes
- counterbores
- countersinks
- pockets
- patterns
- mirrors
- revolves
- chamfers
- fillets

---

# 28. Feature Parameter Accuracy

Correct feature classification is not enough.

For example:

```text
Hole detected ✓

Diameter incorrect ✗
```

Therefore evaluate:

```text
feature type correctness

feature count correctness

feature parameter correctness
```

---

# 29. Hole-Specific Metrics

Because holes are very common engineering features, report:

```text
hole count accuracy

diameter MAE

location error

depth accuracy

through/blind classification accuracy

counterbore accuracy

countersink accuracy

thread-callout recognition accuracy
```

---

# 30. Pattern Metrics

Evaluate:

```text
pattern detected?

pattern type correct?

count correct?

spacing correct?

axis/direction correct?
```

Report separately for:

```text
linear
rectangular
circular
mirror
```

---

# 31. Reprojection Metrics

After generating CAD:

```text
CAD
 ↓
front/top/side projections
```

Compare each projection with the source.

Possible metrics:

```text
silhouette IoU

edge precision

edge recall

edge F1

feature correspondence
```

The reprojection score should be reported per view.

---

# 32. 3D Geometric Metrics

When ground-truth STEP exists, evaluate:

```text
3D IoU

Chamfer Distance

bounding-box dimension error

volume error
```

IoU remains the official Ortho2CAD comparison metric.

Other metrics provide additional diagnostic information.

---

# 33. B-Rep-Level Evaluation

For later engineering evaluation, include where practical:

```text
face count difference

edge count difference

vertex count difference

surface correspondence
```

The current ECCV 2026 CAD Challenge evaluator demonstrates a useful B-Rep-oriented evaluation design with:

- surface F1
- edge F1
- vertex F1
- topology F1
- valid STEP ratio

which may provide useful inspiration for Extrudely's extended evaluator.

---

# 34. CFP Quality Metrics

Because Extrudely produces a structured CAD Feature Plan, evaluate:

```text
feature-type accuracy

feature parameter accuracy

dependency validity

unsupported-operation rate

feature sequence validity

pattern abstraction quality
```

Exact original construction history is not required.

---

# 35. Editability Metric

A generated part should not only look correct.

Measure:

```text
Can dimensions be changed?

Can hole diameter be edited?

Can pattern count be modified?

Can the model regenerate successfully?
```

A simple **Parametric Edit Success Rate** can be defined:

```text
successful parameter edits
--------------------------
attempted parameter edits
```

This directly measures usefulness of the CFP + CadQuery representation.

---

# 36. Self-Correction Metrics

Run every applicable sample:

```text
before correction
vs
after correction
```

Report:

```text
Initial IoU

Final IoU

IoU improvement

Initial dimension error

Final dimension error

Correction success rate

Number of iterations
```

---

# 37. Correction Efficiency

Define:

```text
Correction Gain
=
Final Score - Initial Score
```

Also report:

```text
% improved

% unchanged

% degraded
```

A correction loop that sometimes makes good models worse must be detectable.

---

# 38. Confidence Evaluation

Because Extrudely exposes confidence scores, confidence itself should be evaluated.

Questions:

```text
When confidence = 95%, is the system actually correct about 95% of the time?

Are low-confidence predictions genuinely more error-prone?
```

Useful metrics include:

```text
Expected Calibration Error

Brier score

accuracy by confidence bucket
```

This is important for trustworthy human review.

---

# 39. Human Review Rate

Track:

```text
percentage automatically accepted

percentage requiring warning

percentage requiring user correction

percentage completely rejected
```

A practical system should not achieve accuracy simply by flagging every example for manual review.

---

# 40. Runtime Metrics

The POC target is approximately:

```text
< 2 minutes per part
```

where practical.

Report runtime by stage:

```text
preprocessing

drawing parsing

CDR construction

feature reasoning

CFP generation

CadQuery compilation

CAD execution

validation

correction
```

---

# 41. Hardware Metrics

The main deployment goal is a single:

```text
24–48 GB GPU
```

Therefore record:

```text
peak GPU memory

peak system RAM

model size

inference runtime
```

The benchmark report should always state hardware.

---

# 42. Input-Type Evaluation Matrix

Final engineering results should look like:

| Metric | Clean Raster | Noisy Raster | DXF | SVG | Vector PDF | Hybrid |
|---|---:|---:|---:|---:|---:|---:|
| Valid CAD | | | | | | |
| 3D IoU | | | | | | |
| Dimension error | | | | | | |
| Feature F1 | | | | | | |
| Runtime | | | | | | |

No single average should hide modality weaknesses.

---

# 43. Drawing-Quality Evaluation

Raster performance should additionally be reported by:

```text
Clean

Mild degradation

Moderate degradation
```

This reveals robustness deterioration.

---

# 44. View-Count Evaluation

Because POC 1 supports two or three views:

```text
2 views

3 views
```

should be evaluated separately.

This tells us how much missing-view information affects reconstruction.

---

# 45. Feature-Complexity Evaluation

Group parts by approximate complexity.

### Level 1

```text
extrude
cut
simple holes
```

### Level 2

```text
patterns
counterbores
countersinks
```

### Level 3

```text
revolve
chamfer
fillet
multiple interacting features
```

Report performance separately.

---

# 46. Main Ablation Study

The most important ablation is:

```text
A0 Direct VLM → CadQuery

A1 Raster → CDR → CFP → CadQuery

A2 A1 + Self-Validation

A3 A2 + Self-Correction

A4 Vector → CDR → CFP

A5 Raster + Vector → CDR → CFP
```

This tells us which architectural components actually contribute value.

---

# 47. Additional Ablations

Evaluate:

```text
with dimensions
vs
without dimensions
```

```text
with cross-view matching
vs
without cross-view matching
```

```text
with pattern abstraction
vs
independent repeated features
```

```text
deterministic compiler
vs
VLM-generated CadQuery
```

```text
zero-shot
vs
fine-tuned
```

---

# 48. Model Comparison

Using the same Extrudely architecture, compare a small number of candidate reasoning models.

For example:

```text
Model A

Model B

Model C
```

Keep:

- parser
- CDR
- CFP
- compiler
- validation

fixed.

This prevents architecture and model improvements from being confounded.

---

# 49. Statistical Reporting

Because the Ortho2CAD final benchmark uses only 100 examples, a difference in mean IoU alone may be misleading.

Therefore report:

```text
mean

median

standard deviation

95% confidence interval
```

for major continuous metrics.

Use paired evaluation because both systems process the same drawings.

Recommended statistical tools:

### IoU / dimensional error

```text
paired bootstrap confidence interval
```

and optionally:

```text
Wilcoxon signed-rank test
```

### Valid/invalid CAD

```text
McNemar test
```

This provides stronger evidence than comparing two means alone.

---

# 50. Failure Categories

Every failed reconstruction should receive a failure label.

Suggested taxonomy:

```text
view detection failure

OCR/dimension failure

primitive extraction failure

cross-view association failure

feature classification failure

feature parameter failure

CFP planning failure

CadQuery compilation failure

CAD execution failure

validation failure

correction failure
```

This is essential for understanding where development effort should go.

---

# 51. Benchmark Audit Trail

For every example save:

```text
input

model version

parser version

CDR

CFP

CadQuery

STEP

IoU

dimension metrics

feature metrics

runtime

confidence

validation iterations

failure type
```

This makes every aggregate score traceable back to individual parts.

---

# 52. Research Success Gate

The research gate contains three levels.

### Minimum credible result

Extrudely runs successfully on the identical Ortho2CAD benchmark and achieves performance reasonably close to the reproduced baseline.

### Target result

Extrudely matches or exceeds Ortho2CAD geometric accuracy while maintaining near-perfect CAD validity.

### Stretch result

Extrudely exceeds Ortho2CAD while also demonstrating:

```text
better dimensional accuracy

better feature interpretability

successful self-correction
```

The reproduced Ortho2CAD implementation, not only the paper number, should ultimately define the exact target.

---

# 53. Product Success Gate

On the held-out company dataset, the system must show acceptable performance in:

```text
CAD validity

overall geometry

critical dimensions

supported feature reconstruction

editability

confidence reporting
```

Final numerical thresholds should be locked only after:

1. the real dataset is selected
2. drawing quality is assessed
3. engineering tolerance expectations are agreed

---

# 54. Runtime Gate

Target:

```text
normal high-confidence reconstruction
≈ under 2 minutes
```

on the selected workstation-class hardware.

Correction cases may take longer but should report their additional cost separately.

---

# 55. Hardware Gate

The primary open-source production configuration should be runnable using approximately:

```text
one 24–48 GB GPU
```

where practical.

Configurations requiring substantially larger infrastructure may still be tested as research baselines but should not become the default POC deployment.

---

# 56. Final Dual Success Rule

Extrudely POC 1 passes only when:

```text
RESEARCH GATE
      +
PRODUCT GATE
      =
POC SUCCESS
```

A strong synthetic benchmark result alone is insufficient.

A convincing visual demo without reproducible benchmark evidence is also insufficient.

---

# 57. Recommended Benchmark Execution Order

The development team should execute evaluation in this order:

```text
1. Reproduce Ortho2CAD evaluator

2. Reproduce Ortho2CAD baseline

3. Evaluate base VLM zero-shot

4. Evaluate direct VLM → CadQuery

5. Evaluate CDR + CFP raster pipeline

6. Add self-validation

7. Add self-correction

8. Add vector mode

9. Add hybrid mode

10. Evaluate synthetic noisy drawings

11. Evaluate ECCV TechDraw-only subset

12. Evaluate held-out company drawings
```

This sequence ensures we always know which change produced an improvement.

---

# 58. Final Benchmark Structure

The final benchmark report should contain four clearly labeled sections:

## A. Published Baseline Reproduction

```text
Ortho2CAD
CAD-Coder / relevant baselines
```

## B. Fair Raster Comparison

```text
Direct VLM
Extrudely Raster
Extrudely Raster + validation
Extrudely Raster + correction
```

## C. Extrudely Extended Evaluation

```text
Vector
Hybrid
Noisy raster
2-view
3-view
feature complexity
```

## D. Real Engineering Evaluation

```text
company drawings
dimensional correctness
feature correctness
editability
review requirement
runtime
```

This gives Extrudely both a defensible research benchmark and a realistic engineering validation framework.