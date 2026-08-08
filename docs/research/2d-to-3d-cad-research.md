I dug through the recent work up to **August 8, 2026**. The field has moved quite a lot in the last 12 to 18 months.

The most important discovery is that a **July 2026 paper is almost exactly the POC we are discussing**: orthographic 2D engineering drawings → editable parametric CAD → STEP.

## 1. Research closest to our problem

| Work | Date | Input | Output | Relevance |
|---|---:|---|---|---|
| **Ortho2CAD** | Jul 2026 | Front, top, right raster drawings | CadQuery code → STEP | ⭐⭐⭐⭐⭐ Exact problem |
| **Drawing2CAD** | 2025 | Vector engineering drawings | Parametric CAD sequence | ⭐⭐⭐⭐⭐ Exact problem for DXF/SVG |
| **RL CAD Reconstruction from Orthographic Drawings** | 2025 | Parsed orthographic drawings | Editable CAD feature sequence | ⭐⭐⭐⭐ |
| **CAD2Program** | 2025 | Raster CAD drawing | Parametric CAD program | ⭐⭐⭐⭐ |
| **Multi-View 2D Projection → CAD** | 2026 | Six orthographic views | Siemens NX parametric model | ⭐⭐⭐⭐ |
| **Traditional Orthographic Reconstruction** | 2023 | SVG orthographic views | STEP | ⭐⭐⭐ Useful deterministic baseline |

### Ortho2CAD is the one we should study first

**Ortho2CAD: 3D CAD Generation from Orthographic Drawings Using Vision Language Models**, published July 9, 2026, takes three standard engineering views, front, top and right, and generates executable **CadQuery Python code**. The code can then be exported as an editable STEP model. ([arxiv.org](https://arxiv.org/html/2607.08891))

Its architecture is especially interesting:

**Orthographic drawing → Qwen3-VL → CadQuery program → execute CAD → compare geometry → RL improvement**

They use **Qwen3-VL-8B-Instruct**, supervised fine-tuning first, followed by geometry-grounded reinforcement learning. ([arxiv.org](https://arxiv.org/html/2607.08891))

Their DeepCAD-derived training split contains about **147,289 training examples**, with additional validation and test data. Their orthographic dataset contains more than **150,000 drawing samples**. ([arxiv.org](https://arxiv.org/html/2607.08891))

On their DeepCAD test subset, Ortho2CAD achieved:

- **100% executable/valid CAD**
- mean IoU around **0.792**
- better geometry similarity than their reported CAD-Coder baseline

After RL on Fusion 360 reconstruction data, they report 100% valid programs and IoU around 0.56 on that harder dataset. ([arxiv.org](https://arxiv.org/html/2607.08891))

Even better for us, the **code and dataset are public**.

[Ortho2CAD GitHub repository](https://github.com/AdityaJoglekar/Ortho2CAD)  
[Ortho2CAD dataset on Hugging Face](https://huggingface.co/datasets/AdityaJoglekar/Ortho2CAD_Orthographic_Drawings/tree/main)

There is one big warning. Their current system mainly handles **sketch + extrusion operations**. The drawing generator also supplies only a few key overall dimensions, rather than all feature dimensions, tolerances and GD&T information. The authors explicitly identify richer CAD operations and more complex geometry as future work. ([arxiv.org](https://arxiv.org/html/2607.08891))

That gap is probably where our POC can become interesting.

---

## 2. Drawing2CAD is the second paper I would study

**Drawing2CAD**, ACM Multimedia 2025, attacks almost the same problem but starts from **vector engineering drawings** rather than raster images. ([arxiv.org](https://arxiv.org/abs/2508.18733?utm_source=chatgpt.com))

Conceptually:

**SVG/vector drawing → Transformer → CAD commands + parameters → parametric model**

They introduced **CAD-VGDrawing**, containing more than 150k paired engineering drawings and corresponding parametric CAD models.

A particularly important finding is that retaining actual vector geometry gives the model more useful geometric information than simply rasterizing the drawing.

This matters for us because a real industrial POC could receive:

- PDF
- DXF
- DWG
- SVG
- scanned drawings
- screenshots

We probably should **not treat all of them as images**.

For DXF/SVG/PDF containing vectors, extracting actual lines, arcs, circles and coordinates could give us much higher dimensional accuracy.

[Drawing2CAD code repository](https://github.com/lllssc/Drawing2CAD?utm_source=chatgpt.com)

There is also a 2026 follow-up called **SwiftCAD**, which simplifies the Drawing2CAD architecture with a shared decoder and aims for similar performance with lower computational cost. ([openreview.net](https://openreview.net/forum?noteId=PuNjZkP5z1&utm_source=chatgpt.com))

---

# 3. Latest AI models worth considering

For our POC, I would separate **complete CAD-generation models** from general VLMs.

| Model | Year | Input | Generates | How useful for us |
|---|---:|---|---|---|
| **Ortho2CAD / Qwen3-VL-8B** | 2026 | Orthographic drawing | CadQuery | ⭐⭐⭐⭐⭐ |
| **CAD-Coder** | 2025 | Image | CadQuery Python | ⭐⭐⭐⭐⭐ |
| **cadrille** | 2026 | Image / text / point cloud | Executable CAD code | ⭐⭐⭐⭐ |
| **Drawing2CAD** | 2025 | Vector drawings | CAD command sequence | ⭐⭐⭐⭐⭐ |
| **Img2CADSeq** | 2026 | Single image | B-Rep / STEP | ⭐⭐⭐⭐ |
| **CAD-Recode** | 2025 | Point cloud | CadQuery Python | ⭐⭐⭐ |
| **CADFit** | 2026 | Mesh / geometry | Parametric CAD program | ⭐⭐⭐⭐ |
| **BrepGaussian** | 2026 | Multi-view images | B-Rep geometry | ⭐⭐⭐ |

### CAD-Coder

This is probably our most important baseline after Ortho2CAD.

CAD-Coder generates executable **CadQuery Python programs from images** and was trained using the **GenCAD-Code** dataset containing more than **163k image/CadQuery pairs**. ([arxiv.org](https://arxiv.org/abs/2505.14646?utm_source=chatgpt.com))

The model is around 13B parameters and is publicly available.

[CAD-Coder GitHub](https://github.com/anniedoris/CAD-Coder?utm_source=chatgpt.com)

The advantage of this family of approaches is huge for an engineering POC:

```text id="rc9fn2"
AI output
    ↓
Python / CadQuery
    ↓
OpenCascade geometry
    ↓
STEP
    ↓
SolidWorks / NX / CATIA / FreeCAD / etc.
```

Instead of asking the model to hallucinate a mesh, it creates a **program describing how the part is constructed**.

---

### cadrille

**cadrille**, accepted at ICLR 2026, goes even further. It accepts multiple modalities including images, point clouds and text, and produces executable Python CAD programs. It combines supervised learning with online reinforcement learning. ([iclr.cc](https://iclr.cc/virtual/2026/poster/10006759?utm_source=chatgpt.com))

This is interesting if later we want something like:

> engineering drawing + textual notes + partial 3D geometry → CAD

rather than drawing alone.

[cadrille GitHub](https://github.com/col14m/cadrille?utm_source=chatgpt.com)

---

### Img2CADSeq

**Img2CADSeq**, SIGGRAPH 2026, reconstructs CAD from an image using an intermediate geometric representation and ultimately produces B-Rep / STEP-compatible geometry. ([arxiv.org](https://arxiv.org/abs/2605.13293?utm_source=chatgpt.com))

Its value for us is less about orthographic drawing understanding and more about **complex 3D geometry reconstruction**.

---

### CADFit

**CADFit**, May 2026, is particularly interesting because it supports a richer modelling vocabulary such as:

- extrusion
- revolution
- fillet
- chamfer

rather than limiting everything to extrusions. ([arxiv.org](https://arxiv.org/abs/2605.01171?utm_source=chatgpt.com))

I would keep this paper in mind when we get to the question of **how to reconstruct realistic manufacturing parts**.

---

# 4. Datasets that matter

Here is the dataset landscape I would currently use.

| Dataset | Approx. scale | Contains | Value for our POC |
|---|---:|---|---|
| **Ortho2CAD Orthographic Drawings** | >150k | 3-view drawings + CAD | ⭐⭐⭐⭐⭐ |
| **CAD-VGDrawing** | >150k | Vector engineering drawings + CAD | ⭐⭐⭐⭐⭐ |
| **GenCAD-Code** | >163k | Rendered CAD images + CadQuery | ⭐⭐⭐⭐⭐ |
| **OrthoCAD-322K** | 322k | Orthographic/isometric views + CAD | ⭐⭐⭐⭐ |
| **DeepCAD** | 178k+ | CAD construction sequences | ⭐⭐⭐⭐⭐ |
| **Fusion 360 Gallery** | 8.6k reconstruction sequences | Real CAD modelling histories | ⭐⭐⭐⭐ |
| **SketchGraphs** | 15M sketches | Sketch geometry + constraints | ⭐⭐⭐⭐ |
| **CAD-220K** | 220k | B-Rep CAD models | ⭐⭐⭐ |
| **PrintCAD** | 2k physical parts | Real photographs + CAD | ⭐⭐⭐ |
| **TriView-CAD** | 2026 dataset | Three-view consistency data | ⭐⭐⭐ |

### OrthoCAD-322K

This is a newer and quite interesting dataset containing approximately **322,000 CAD models with standardized orthographic and isometric representations**, including DXF and raster representations. ([sciencedirect.com](https://www.sciencedirect.com/science/article/pii/S0097849325001980?utm_source=chatgpt.com))

It was designed mainly for CAD retrieval rather than reconstruction, but it could be extremely useful for:

**drawing encoder pretraining → shape retrieval → CAD reconstruction**

For example, before asking AI to create something from scratch, retrieve the five most geometrically similar CAD parts from a 300k library.

That could make the generation task significantly easier.

---

### SketchGraphs

SketchGraphs is older but still extremely relevant because it contains about **15 million CAD sketches with geometric constraints**. ([github.com](https://github.com/PrincetonLIPS/SketchGraphs?utm_source=chatgpt.com))

It teaches relationships like:

```text id="7ix1pw"
parallel
perpendicular
coincident
tangent
equal
horizontal
vertical
radius
distance
```

These are exactly the relationships we eventually need if the goal is a **real parametric CAD model**, rather than a visually similar 3D object.

---

### Fusion 360 Gallery

Autodesk's Fusion 360 reconstruction dataset contains around **8,625 sketch-and-extrude construction sequences** generated from real CAD modelling workflows. ([github.com](https://github.com/AutodeskAILab/Fusion360GalleryDataset?utm_source=chatgpt.com))

It is relatively small compared with synthetic datasets, but potentially more valuable because it contains actual modelling histories.

---

# 5. There is another important research area: understanding the drawing itself

Most CAD-generation papers simplify the input drawings considerably.

Actual company drawings may contain:

```text id="sjurzw"
┌──────────────────────────────┐
│ FRONT VIEW       ⌀20 H7      │
│                              │
│     ┌──────┐                 │
│     │      │   45 ±0.05      │
│     └──────┘                 │
│                              │
│ SECTION A-A                  │
│                              │
│ Ra 1.6       M10 × 1.5       │
│                              │
│ MATERIAL: EN AW-6061         │
│ SCALE 1:2                    │
└──────────────────────────────┘
```

This introduces a completely different AI problem:

**drawing understanding.**

Recent 2025 work has combined **YOLOv11-OBB** with models such as **Donut and Florence-2** to identify drawing regions, dimensions, symbols, text and GD&T annotations. One dataset in this research contained 1,367 annotated mechanical drawings across nine information categories. Another multi-stage approach used approximately 1,000 layout-labelled drawings plus 1,406 annotation-level examples. ([arxiv.org](https://arxiv.org/abs/2506.17374?utm_source=chatgpt.com))

A 2026 survey of engineering-document intelligence also concludes that robust geometric reasoning and standardized multi-format engineering-drawing benchmarks remain open problems. ([researchgate.net](https://www.researchgate.net/publication/408207060_Vision_foundation_models_for_engineering_document_intelligence_and_manufacturing_inspection_a_survey?utm_source=chatgpt.com))

This is important because **2D → 3D alone is not enough**.

The system must understand what `Ø20`, `R5`, `M8`, hidden lines, sections, tolerances and view relationships actually mean.

---

# 6. One 2026 technique I find especially interesting

MIT researchers published **GIFT: Bootstrapping Image-to-CAD Program Synthesis via Geometric Feedback** in March 2026. ([arxiv.org](https://arxiv.org/abs/2603.27448?utm_source=chatgpt.com))

Instead of simply training the model once, the system:

```text id="ytpk7f"
Generate CAD
      ↓
Render resulting CAD
      ↓
Compare against target
      ↓
Identify geometry errors
      ↓
Generate harder training examples
      ↓
Train again
```

They report a roughly **12% improvement in mean IoU** over their supervised baseline while reducing inference compute substantially. ([arxiv.org](https://arxiv.org/abs/2603.27448?utm_source=chatgpt.com))

I think this principle is extremely relevant to Extrudely.

CAD has a major advantage over normal image generation: **we can mathematically check whether the answer is correct**.

---

# 7. What is actually solved, and what is not

The recent papers make the POC much more feasible than it would have been two years ago.

But the problem is **not solved** in the industrial sense.

Current systems are increasingly good at:

**clean drawing → relatively simple 3D part → executable CAD**

They are still weak when drawings contain combinations of:

- many views
- section views
- detail views
- auxiliary views
- large numbers of dimensions
- GD&T
- threads
- holes and hole patterns
- fillets and chamfers
- revolves
- sweeps
- lofts
- complex pockets
- thin-wall geometry
- datum references
- conflicting or missing dimensions
- old scanned drawings
- handwritten modifications
- unusual drawing standards

Ortho2CAD itself acknowledges the limitation around richer modelling operations and complicated geometry. ([arxiv.org](https://arxiv.org/html/2607.08891))

And that is actually good news for us because there is still plenty of room for a useful engineering system.

# 8. My main conclusion before we brainstorm

I **would not build Extrudely as one giant "image → STEP" neural network**.

The strongest recent work points toward something closer to:

```text id="li548w"
                        2D ENGINEERING DRAWING
                                  │
                ┌─────────────────┴─────────────────┐
                │                                   │
             VECTOR                              RASTER
         PDF / DXF / SVG                      Scan / Image
                │                                   │
        Geometry Parser                     Vision / VLM
                └─────────────────┬─────────────────┘
                                  ↓
                       Drawing Understanding
                  views + dimensions + topology
                                  ↓
                        CAD reasoning model
                                  ↓
                     Parametric CAD program
                           CadQuery
                                  ↓
                          OpenCascade
                                  ↓
                              STEP
                                  ↓
                      Render views again
                                  ↓
                 Compare with original drawing
                                  ↓
                         AI self-correction
```

That is already a much clearer research direction than simply starting with a generic vision model.

For our next brainstorming step, I would therefore treat **Ortho2CAD as the baseline we need to understand and improve**, **Drawing2CAD as the vector-input route**, **CAD-Coder as a second generation baseline**, and drawing/GD&T parsing as the missing industrial layer. ([arxiv.org](https://arxiv.org/html/2607.08891))

When we brainstorm, the most useful next question is not just *“which model should we use?”* It is **what exact level of engineering drawing do we want the first Extrudely POC to solve?** Once we define that boundary, we can design something feasible rather than attempting the entire 2D-to-CAD problem at once.

genui{"suggest_automation":{"label":"Watch for new 2D-to-CAD papers and datasets"}}