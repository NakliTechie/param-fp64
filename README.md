# param-fp64

> FP64 benchmark: four period workloads on today's hardware, set against published 1987–1991 figures for the Cray X-MP and PARAM 8000.

Artifact 1 of the PARAM strand. It exists so the other two artifacts — the browser transputer and the export-control piece — can cite a number instead of a vibe. Deliverable is this repo, a CSV, and a one-page result. Not a site.

Full strand handoff, including the other two artifacts and the shared rules (FP64-only, three-tier sourcing): [HANDOFF.md](HANDOFF.md). This repo builds §Artifact 1.

## Rules that bind every cell

- Every number is FP64, measured, named to a machine. FP32-only figures carry the label in the same cell.
- Every cell carries `source`: `measured` · `published` · `reconstructed`.
- Compiler flags, run counts, and thermal state ship in the CSV next to the result.
- Contested or self-reported claims are attributed to the claimant and never appear in a table cell.

## Roadmap

- v1.0 — Livermore Loop 7 and LINPACK (100×100, 1000×1000) on M4 Pro and M4 Max, against published period figures. CSV + harness + `SOURCES.md`.
- v1.1 — shallow-water kernel and Marmousi migration.
- v1.2 — PARAM 8000 column by emulation, once the browser transputer runs 64 nodes. Stays a file copied between repos, never a dependency.

Termination condition: a clean-checkout re-run reproduces every measured cell within 5%, and every published cell resolves to a citation in `SOURCES.md`.
