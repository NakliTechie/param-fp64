# SPEC — param-fp64 v1.0

Tier: **Tool**. Direction: n/a (no UI; the surface is a CSV and one Markdown table).
Status: draft 0.1, 2026-09-21. Governs v1.0 only; v1.1/v1.2 in [HANDOFF.md](HANDOFF.md) §Artifact 1.

## §0 Agent contract

*Owed. Filled by the DRIVER pass once this draft settles.* Until then the contract is the CLI in §4: every capability is a `make` target or a `bench.py` subcommand; there is no other door.

## §1 Purpose

One reproducible table. Four period workloads (two in v1.0), run FP64 on today's hardware, set against published 1987–1991 figures for the Cray X-MP and PARAM 8000. Artifacts 2 and 3 cite this table. Nothing here is a site.

## §2 The three rules (from the strand handoff, restated as checkable conditions)

1. **FP64 only.** Every kernel computes in `double`. A cell whose only available period figure is not FP64 carries `precision` ≠ `fp64` in the CSV and the table renders the precision inside the same cell as the number.
2. **`source` on every cell.** One of `measured` · `published` · `reconstructed`. A row without it fails the schema check.
3. **Flags travel with the number.** `compiler`, `flags`, `runs`, `thermal` are columns, not a footnote.

Contested claims (28× the Cray; Zurich 1990) live in `SOURCES.md` §Attributed and nowhere else.

## §3 Workloads (v1.0)

| id | Kernel | Reference source | Notes |
|---|---|---|---|
| `ll7` | Livermore Loop 7 (equation of state fragment) | McMahon 1986 loop 7, `double` | The Inmos TN06 comparison table exists for exactly this loop |
| `linpack100` | LINPACK 100×100, `dgefa`/`dgesl` | Dongarra reference C translation, no BLAS substitution | The "everyone will ask" number |
| `linpack1000` | LINPACK 1000×1000 | Same code, n=1000 | Period figures exist for both eras |

Kernels are C, unmodified reference loops. No hand vectorisation, no Accelerate/BLAS. The comparison is compiler-on-reference-source, same as the period figures were.

## §4 Harness

- `bench.py` (Python 3.12, stdlib only): `build`, `run`, `check`, `table`.
- `make` wraps `bench.py`; `make all` = build → run → check → table.
- Flag set, fixed for every run: `-O2 -std=c99 -fno-fast-math` (no `-ffast-math`, ever: it breaks the FP64 claim). Recorded verbatim in the CSV.
- Runs: 5 per cell, report median; all 5 raw values kept in `results/raw/`.
- Thermal: `thermal` column = `cold` (first run after ≥60 s idle) or `sustained` (5 back-to-back). Both are reported for the 10-core cell because the delta on a laptop is real.
- Core pinning on macOS: QoS `user-interactive` via `taskpolicy -c utility` inversion is unreliable; v1.0 records `cores` as requested threads and notes the OS scheduler in `SOURCES.md`. Multi-core cell uses independent processes, not threads, so the number is "10 copies of the kernel" — labelled as such (`cores=10, mode=throughput`).

## §5 Machines

| machine id | What | How the cell is filled |
|---|---|---|
| `cray-xmp14` | Cray X-MP/14, 1 CPU | `published` — brochure peak 200 MFLOPS/CPU; LINPACK from the Dongarra table, edition cited |
| `param8000-64` | PARAM 8000, 64 × T800-20 | `published` — secondary, source named; v1.2 adds `measured (emulated)` |
| `t800-20` | Single T800-20 | `published` — Inmos TN06, LL7 = 1.5 MFLOPS |
| `m4pro-1p` | Apple M4 Pro, 1 P-core | `measured` — this laptop: 10P+4E, 24 GB, clang 21.0.0 |
| `m4pro-10p` | Apple M4 Pro, 10 P-cores, throughput mode | `measured` |
| `m4max-studio` | Apple M4 Max Studio | `measured` — owed, machine access open |

Spark units: out of scope (handoff).

## §6 CSV schema — `results/results.csv`

```
workload,machine,cores,mode,precision,mflops,source,compiler,flags,runs,thermal,citation
ll7,m4pro-1p,1,single,fp64,<n>,measured,"Apple clang 21.0.0","-O2 -std=c99 -fno-fast-math",5,cold,
ll7,t800-20,1,single,fp64,1.5,published,,,,,TN06
```

`citation` is a key into `SOURCES.md`. `check` fails on: missing `source`, `measured` row without `compiler`+`flags`+`runs`, `published` row without a resolving `citation`, `precision` other than `fp64` without the value being rendered with its label in `table`.

## §7 Termination condition (v1.0)

- `git clone` fresh → `make all` → every `measured` cell within 5% of the committed CSV on the same machine id.
- Every `published` cell's `citation` resolves to an entry in `SOURCES.md` with a URL or a document identifier.
- `make check` exit 0 is the verifier's word. Nothing else counts.

## §8 Out of scope for v1.0

Shallow-water, Marmousi, emulated PARAM column, any GPU number, any FP32 number from the M-series (Metal has no FP64; the 8.6 TFLOPS figure is FP32 and does not enter this table).
