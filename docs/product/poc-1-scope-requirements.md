# Extrudely POC 1
## 2D Engineering Drawing to Parametric 3D CAD

### 1. POC Objective

Extrudely POC 1 will develop and evaluate an AI-assisted system that reconstructs editable parametric 3D CAD models from 2D mechanical engineering drawings.

The system will accept both raster and vector engineering drawings, extract their geometric and dimensional information, infer a reasonable CAD feature sequence, generate executable CadQuery code, export the resulting model as STEP geometry, and automatically validate the reconstructed model against the source drawing.

A dedicated raster-only benchmark mode will allow direct comparison with Ortho2CAD using equivalent inputs and evaluation conditions. Ortho2CAD provides the principal published baseline because it reconstructs CadQuery models from rasterized orthographic drawings and evaluates generated geometry using CAD validity and 3D IoU.

---

## 2. Primary Research Question

**Can a multimodal, geometry-aware reconstruction pipeline generate editable parametric CAD models from 2D engineering drawings with accuracy comparable to or better than direct vision-language-model-based approaches such as Ortho2CAD?**

Secondary questions include:

- Does explicit drawing understanding improve CAD reconstruction?
- Does access to vector geometry improve dimensional and feature accuracy?
- Does combining raster and vector information outperform either modality alone?
- Can iterative geometric validation improve reconstruction accuracy?
- How well does the approach transfer from public benchmark datasets to real engineering drawings?

---

# 3. Supported Inputs

POC 1 will support:

### Raster inputs
- PNG
- JPEG
- rasterized PDF
- moderately noisy scanned drawings

### Vector inputs
- DXF
- SVG
- vector PDF

DWG is excluded from POC 1 because of additional proprietary-format handling complexity.

The system should automatically determine whether a PDF contains useful vector information or should be processed as a raster document.

---

# 4. Drawing Scope

Each input represents:

- one mechanical part
- one drawing sheet
- two or three standard orthographic views

Supported views include primarily:

- front
- top
- left/right side

The system will support:

- first-angle projection
- third-angle projection

Projection type should be detected automatically from the drawing layout, projection symbol, or title-block information.

A simple section view may also be used when necessary for interpreting internal geometry.

Multiple parts per drawing and multi-sheet part drawings are outside POC 1.

---

# 5. Supported Part Complexity

POC 1 targets **intermediate mechanical part complexity**.

Supported geometric features include:

### Base geometry
- rectangular and polygonal profiles
- circular profiles
- simple compound sketches
- additive extrusions
- subtractive extrusions
- pockets
- slots
- through holes
- blind holes

### Hole features
- standard circular holes
- counterbores
- countersinks
- hole depth
- through-hole identification

### Repeated features
- linear patterns
- circular patterns
- equally spaced holes
- mirrored features
- symmetric geometry

### Edge features
- simple fillets
- simple chamfers

### Revolved geometry
- shafts
- stepped shafts
- cylindrical bodies
- flanges
- simple grooves
- other simple turned profiles

### Threads
The system should recognize simple thread callouts including examples such as:

- M8
- M10 × 1.5
- UNC
- UNF

Full helical thread geometry is not required. Threads may be represented using simplified geometry and structured metadata.

---

# 6. Dimensional Understanding

Standard engineering dimensions will be interpreted as geometric constraints.

Supported information includes:

- length
- width
- height
- diameter
- radius
- hole diameter
- hole depth
- pocket dimensions
- spacing
- feature locations
- angles where required

Drawings are expected to be **mostly dimensionally complete**.

When a dimension is missing, the system may infer it when there is sufficient geometric and cross-view evidence.

Critical inferred values must receive a confidence score.

---

# 7. Tolerances

POC 1 will recognize basic dimensional tolerances where available.

The nominal dimension will be used for geometry generation.

Tolerance information should be preserved separately as metadata.

POC 1 will not perform:

- tolerance-stack analysis
- manufacturing tolerance optimization
- complete GD&T interpretation
- datum-reference reasoning

These remain future extensions.

---

# 8. Title Block Understanding

Basic title-block extraction is included.

The system should attempt to identify:

- part name
- part number
- drawing scale
- measurement units
- projection convention
- material

Full document-management information such as approval workflows, revision history, release status, and signatures is outside the POC.

---

# 9. Language and Units

Supported drawing languages:

- English
- German

Supported measurement systems:

- millimeters
- inches

Unit detection should preferably occur automatically using dimension annotations and title-block information.

---

# 10. Shared Drawing Representation

Raster and vector inputs should converge into a common structured representation before CAD generation.

Conceptually:

```text
Raster Drawing ──→ Vision Parser ───┐
                                    │
                                    ▼
                         Structured Drawing Model
                                    │
                                    ▼
                              CAD Reasoning
                                    │
                                    ▼
Vector Drawing ──→ Vector Parser ──┘
```

The intermediate representation should contain information such as:

- drawing views
- geometric primitives
- circles
- arcs
- line segments
- hidden geometry
- dimensions
- feature relationships
- symmetry
- patterns
- section information
- confidence values
- potential CAD features

The exact representation will be designed during the architecture phase.

---

# 11. CAD Reconstruction

The system will generate:

1. **Executable CadQuery code**
2. **STEP geometry**

The generated CAD should contain a reasonable and editable feature sequence.

Exact reconstruction of the original designer's modeling history is not required.

An acceptable reconstruction might use:

```text
Base sketch
   ↓
Extrusion
   ↓
Pocket
   ↓
Hole
   ↓
Pattern
   ↓
Chamfer
   ↓
Fillet
```

provided that the final geometry and engineering intent are correct.

---

# 12. Automatic Confidence Handling

The system will operate automatically but include confidence checks.

High-confidence features should be generated without user intervention.

When important information is uncertain, the system should:

- identify the uncertain feature
- assign a confidence score
- show the relevant evidence
- flag the issue for review

The system should not silently invent critical engineering geometry.

---

# 13. Ambiguity Resolution

POC 1 will use a hybrid ambiguity strategy.

If sufficient evidence exists, generation continues automatically.

If ambiguity could materially change the resulting CAD geometry, the system may:

- flag the feature
- temporarily block that feature
- request targeted user correction

When substantial ambiguity remains, the system may generate the **top two or three ranked CAD candidates**.

Multiple candidates should only be generated for genuinely uncertain cases.

---

# 14. Raster/Vector Conflict Resolution

Raster interpretation, explicit dimensions, and vector geometry may occasionally disagree.

The system will therefore use a confidence-based conflict resolver considering:

- explicit dimension annotations
- vector geometry
- OCR confidence
- drawing scale
- cross-view consistency
- geometric constraints
- detected feature relationships

Contradictions should be surfaced to the user rather than silently resolved when confidence is insufficient.

---

# 15. Geometric Self-Validation

POC 1 will include an iterative verification loop.

```text
Generate CAD
     ↓
Execute CadQuery
     ↓
Generate STEP/B-Rep
     ↓
Render orthographic views
     ↓
Compare with source drawing
     ↓
Detect mismatches
     ↓
Correct CAD program
     ↓
Validate again
```

The loop ends when:

- the required accuracy/confidence threshold is reached, or
- the maximum correction count is reached.

This validation mechanism is a central part of the Extrudely approach.

---

# 16. User Correction

The POC will support targeted human correction.

The user may correct information such as:

- dimension value
- feature classification
- hole interpretation
- projection interpretation
- ambiguous geometry

The CAD model can then be regenerated using the corrected information.

POC 1 is not intended to become a complete interactive CAD editor.

---

# 17. Explainability

The user interface should expose basic engineering-level explainability.

The system should show:

- detected views
- extracted dimensions
- recognized features
- inferred features
- confidence scores
- ambiguous regions
- validation mismatches

Detailed internal model reasoning does not need to be exposed.

---

# 18. User Interface

POC 1 will include a lightweight web application.

The interface should allow the user to:

1. upload a drawing
2. inspect detected views
3. inspect extracted dimensions
4. inspect recognized features
5. see confidence warnings
6. generate the CAD model
7. view the 3D result
8. review validation mismatches
9. apply targeted corrections
10. regenerate the model
11. export CadQuery code
12. export STEP geometry

---

# 19. 3D Visualization

The web interface will include an interactive 3D preview supporting:

- rotation
- zoom
- pan

Advanced CAD editing is not required.

---

# 20. Drawing-to-CAD Comparison Interface

The UI should show:

**Original drawing**

alongside:

**orthographic projections regenerated from the reconstructed CAD**

Differences should be highlighted automatically wherever practical.

This allows an engineer to quickly understand where reconstruction errors occurred.

---

# 21. Model Strategy

The main Extrudely system will use an **open-source model stack** that can be adapted or fine-tuned for engineering drawings.

Strong proprietary multimodal models may be used as external comparison baselines.

The production pipeline must not depend on proprietary APIs.

This allows reproducibility and supports deployment where engineering drawings contain confidential intellectual property.

---

# 22. Deployment Strategy

POC 1 will use a hybrid deployment design.

The core system should be capable of running:

- locally
- on-premise
- in private cloud infrastructure

External multimodal APIs remain optional.

The target hardware is approximately a **single 24–48 GB GPU** where practical.

---

# 23. Runtime Target

Target end-to-end processing time:

**less than approximately two minutes per part**

where practical.

This includes:

- drawing parsing
- CAD generation
- CAD execution
- primary validation

Additional correction iterations may extend this time.

---

# 24. Dataset Strategy

Three types of data will be used.

### A. Public benchmark datasets

Used for reproducibility and comparison against existing research.

Relevant sources include:

- Ortho2CAD data
- DeepCAD-derived data
- Fusion 360 reconstruction data
- other compatible public CAD datasets

### B. Synthetic multimodal dataset

CAD models will be rendered/exported into several corresponding formats:

```text
Ground-truth CAD
       │
       ├── PNG
       ├── SVG
       ├── DXF
       └── PDF
```

These provide multiple input modalities linked to exactly the same ground-truth model.

Synthetic degradation may also generate:

- blur
- scan noise
- skew
- reduced resolution
- broken lines

### C. Real company test set

A small set of representative real engineering drawings will be used to determine whether the system transfers beyond synthetic/public benchmark data.

---

# 25. Ortho2CAD Benchmark Track

A dedicated raster-only mode will provide direct benchmarking against Ortho2CAD.

The comparison must use:

- equivalent raster input
- equivalent test examples
- no vector information during inference
- no additional hidden CAD information
- identical or reproduced evaluation procedures wherever possible

The primary published Ortho2CAD evaluation uses executable CAD validity and 3D IoU, making these mandatory metrics for the benchmark track.

Two evaluations should be reported:

### Zero-shot evaluation
Evaluate the base Extrudely approach before benchmark-specific fine-tuning.

### Fine-tuned evaluation
Train or adapt using equivalent public training/test splits where feasible and compare under similar conditions.

---

# 26. Extrudely Evaluation Tracks

Performance will be evaluated separately for:

### Raster
Clean PNG/JPEG engineering drawings.

### Noisy raster
Moderately degraded scanned drawings.

### Vector
DXF/SVG/vector PDF.

### Hybrid
Cases where both geometric/vector and rendered/visual information are used.

Results should not be hidden inside one combined average.

---

# 27. Core Metrics

### Benchmark metrics

- valid CadQuery execution rate
- valid B-Rep/solid rate
- 3D IoU

### Geometric metrics

- dimensional absolute error
- dimensional relative error
- bounding-box accuracy
- geometric similarity
- projection consistency

### Feature metrics

- feature detection accuracy
- hole accuracy
- pocket accuracy
- pattern accuracy
- revolve accuracy
- chamfer/fillet accuracy

### System metrics

- generation success rate
- validation success rate
- self-correction improvement
- number of correction iterations
- inference time

---

# 28. Dimensional Acceptance

Dimensional validation should combine:

- absolute error
- relative error

rather than relying on one universal threshold.

The actual allowable thresholds will be calibrated during experimentation based on part scale, drawing quality, and benchmark characteristics.

---

# 29. Auditability and Experiment Tracking

Every reconstruction should maintain a complete experiment trail containing:

- original input
- preprocessing configuration
- extracted drawing information
- intermediate representation
- model/version used
- prompt/configuration where applicable
- generated CadQuery
- CAD execution result
- validation metrics
- detected discrepancies
- correction iterations
- user corrections
- final CadQuery
- final STEP

This is required for reproducibility, debugging, benchmarking, and future industrial validation.

---

# 30. Explicitly Out of Scope

POC 1 will not attempt to fully solve:

- assemblies
- multiple parts per drawing
- multi-sheet drawings
- complex sheet metal
- complex lofts
- advanced sweeps
- organic/freeform surfaces
- advanced spline-heavy parts
- full thread geometry
- complex gears
- complete GD&T reasoning
- datum-chain reasoning
- tolerance-stack analysis
- full manufacturing process planning
- BOM extraction
- complete revision-management workflows
- heavily degraded historical drawings
- handwritten engineering modifications
- full interactive CAD editing

---

# 31. POC Deliverables

POC 1 will produce both a **research prototype** and a **usable demonstration application**.

The expected deliverables are:

1. raster drawing parser
2. vector drawing parser
3. common structured drawing representation
4. CAD reasoning pipeline
5. CadQuery generator
6. STEP exporter
7. automatic validation and correction pipeline
8. confidence and ambiguity system
9. simple web application
10. interactive 3D preview
11. 2D-vs-generated-projection comparison
12. benchmark implementation
13. benchmark results against Ortho2CAD
14. synthetic dataset generation pipeline
15. real-company evaluation results
16. complete experiment tracking

---

# 32. POC Success Gate

POC 1 uses a **dual success criterion**.

## Research Gate

The system must demonstrate credible performance against Ortho2CAD using an equivalent raster-only benchmark setup.

Performance should be assessed using at least:

- valid CAD generation
- 3D IoU
- zero-shot performance
- comparable fine-tuned performance

## Product Gate

The system must successfully reconstruct a representative subset of real engineering drawings with acceptable:

- geometry
- dimensions
- features
- editability
- confidence reporting

### Final rule

**Extrudely POC 1 is considered successful only when both the research gate and the real-world product gate are satisfied.**