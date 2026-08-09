# Extrudely

Reconstruct editable parametric 3D CAD models from 2D mechanical engineering drawings.

**Status:** POC 1 — Project Foundation

## Quickstart

```bash
# Install dependencies
uv sync

# Run tests
uv run pytest

# Lint
uv run ruff check .
```

## Architecture

The pipeline transforms engineering drawings through four layers:

```
Input → Drawing Understanding (CDR) → 3D Reasoning (CFP) → CadQuery Compiler → STEP → Validation → Correction
```

- **Layer A** — Drawing understanding: raster and vector parsers → Common Drawing Representation (CDR)
- **Layer B** — 3D geometry: cross-view reasoning → 3D feature hypotheses
- **Layer C** — CAD construction: CAD Feature Plan (CFP) → deterministic CadQuery compilation
- **Layer D** — Validation: 5-stage validator → correction loop

See [System Architecture](docs/architecture/system-architecture.md) and [Architecture Spine](_bmad-output/planning-artifacts/architecture/ARCHITECTURE-SPINE.md) for details.

## Docs

- [PRD](_bmad-output/planning-artifacts/prd.md)
- [Epics](_bmad-output/planning-artifacts/epics.md)
- [CDR Specification](docs/architecture/contracts/cdr-specification.md)
- [CFP Specification](docs/architecture/contracts/cfp-specification.md)
- [Implementation Roadmap](docs/roadmap/implementation-roadmap.md)
