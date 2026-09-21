# PARAM strand — three artifacts


## Decision: port t4 to WASM

Locked. The simulator runs a real T800 instruction set, not a bespoke occam-subset interpreter. Basis: `pahihu/t4` — C, emulates T414/T800, passes the T800 FPU validation suite, already builds the D7205A occam 2 toolset on macOS and Linux — compiled with Emscripten.

**What this buys**

|  | Gain |
| --- | --- |
| Compiler | None to write. The period occam toolset runs *inside* the emulator — the authentic 1991 toolchain, not our approximation of one |
| Authority | The artifact runs real transputer binaries. "Close enough" stops being something anyone can say |
| Validation | TVS1 / TVS1F and the FPU tests are the machine-checkable termination condition, free, upstream |
| Scope | Instruction semantics, scheduler, FPU — all inherited. We build the fabric and the surface, not the CPU |

**What it costs**

1. **t4 emulates one transputer.** PARAM is 64 wired in a reconfigurable topology. The link engine exists but points at host networking; it gets replaced with an in-process fabric. This is the real work and it is not small.
2. **Not a single-file tool any more.** A WASM blob plus a toolset image breaks the default shape. Deliberate departure, reason recorded here — Build Doctrine rung 1 — justified because the browser genuinely cannot run period occam otherwise.
3. **Cold-load budget gets hard.** WASM plus toolset image is megabytes. Rule 2 (≤5 s) holds only if demo traces ship precomputed and the emulator loads lazily behind them.
4. **Licensing is unresolved.** See the last section. This is the one thing that can kill the approach outright.
5. **Cycle accuracy is an upstream non-goal.** Fine — we were never selling cycle accuracy. Say so in the copy rather than implying otherwise.

**What it forecloses:** the weekend version. This is weeks, not days. Accepted, because artifact 3 is the one that gets read and it does not block on this one.

## Shared spine

Three artifacts, three repos, three deploys. They cite each other; they do not share a codebase. Anything that would force a shared data layer is the signal we have drifted into Product tier — see the last section.

**The FP64 rule.** Every performance number in every artifact is FP64, measured, named to a machine. The Cray X-MP's 200 MFLOPS per CPU was all 64-bit; the M4 Pro's 8.6 TFLOPS is FP32 GPU and Metal has no FP64 at all. Mixing them is the cheat that kills the piece with the first competent reader. Where only an FP32 figure exists, it is labelled FP32 in the same visual unit as the number — not in a footnote.

**Source discipline.** The historical record here is thin and partisan. Three tiers, marked in the artifact itself:

| Tier | Example | Treatment |
| --- | --- | --- |
| Primary, verifiable | Inmos TN06 Livermore Loop 7 figures; X-MP brochure peak of 200 MFLOPS/CPU and 800+ for the X-MP/48 | Stated plainly |
| Secondary, consistent | 64-node PARAM 8000 delivered Aug 1991; 256-node 1 GFLOPS theoretical, 100–200 MFLOPS sustained; exports to Germany, UK, Russia | Stated with source named |
| Contested or self-reported | "28× the Cray for the same $10M"; "second only to a US machine at Zurich 1990" | Attributed to whoever claimed it, never laundered into our own voice |

The third tier is where this subject goes wrong. Both of those claims are repeated everywhere and originate with C-DAC or its boosters. Quote them as claims — they are interesting *as* claims — and never put them in a table cell.

**Tier.** All three are Tool tier. One doc each (this one covers all three during planning; each artifact gets its own handoff when its build opens). No role matrix — single actor throughout. Forward pass once at ship, rubric pass once at ship.

**How they cite each other.** Artifact 1 produces the numbers. Artifact 2 embeds as the interactive proof. Artifact 3 is the argument and links both. Build order: 1 → 3 → 2, because 3 is the one that gets read and 2 is the one that can slip.

## Artifact 1 — the FP64 benchmark

**Vision.** A single reproducible table: four period-relevant workloads, run on today's hardware, set against published 1987–1991 figures for the machines that mattered. It exists so artifacts 2 and 3 can cite a number instead of a vibe. Deliverable is a repo, a CSV, and a one-page result — not a site.

**Workloads.** Chosen because period numbers exist and can be re-run unmodified:

| Workload | Why | Period anchor |
| --- | --- | --- |
| Livermore Loop 7 | Inmos published a direct comparison table for it | T800-30 at 2.25 MFLOPS, T800-20 at 1.5, T414-20 at 0.09, VAX 11/780 with FPA at 0.54 |
| LINPACK 100×100 and 1000×1000 | What everyone will ask for; both eras reported it | X-MP and PARAM-era figures both in the literature |
| Shallow-water / barotropic kernel | Stands in for what NCMRWF actually bought the X-MP/14 to run | Reconstructed from period model descriptions; mark as reconstructed |
| Marmousi migration | 1988 synthetic, openly available, exactly the ONGC-class problem | Published timings from several eras |

**Machines in the table:** Cray X-MP/14 (published peak, no re-run possible), PARAM 8000 64-node (published, plus emulated once artifact 2 exists), M4 Pro one P-core, M4 Pro ten P-cores, M4 Max Studio. The Spark units are out of scope — different memory model, muddies the comparison, and nobody in 1991 had a coherent analogue.

**Roadmap**

- **v1.0** — Livermore 7 and LINPACK only, on M4 Pro and M4 Max, against published period figures. Ships the CSV, the harness, and the sourcing table. This is enough for artifact 3.
- **v1.1** — shallow-water and Marmousi added. Slower, more judgment calls, more caveats.
- **v1.2** — PARAM 8000 column filled by emulation rather than citation, once artifact 2 can run 64 nodes.

**Handoff notes**

- Harness in Python, kernels in C compiled with the same flags across runs; flags recorded in the CSV alongside every result. A benchmark whose compiler flags are not in the output is not a benchmark.
- Pin CPU governor state, run counts, and thermal conditions. On a laptop, sustained versus burst is a real 20–30% and someone will check.
- Every cell in the output carries a `source` column: `measured`, `published`, or `reconstructed`. No cell without one.
- **Termination condition:** harness re-run on a clean checkout reproduces every measured cell within 5%, and every published cell resolves to a citation in `SOURCES.md`. Not a self-report.

## Artifact 2 — the browser transputer

**Vision.** Open a tab, get a working 64-node PARAM 8000: real T800 instruction set, period occam toolchain, a topology you can rewire, and the message traffic visible as it happens. The point is not speed — it is that a person can *see* CSP running on the machine that was built because a Cray was refused.

**Unity sentence.** *An instrument panel for a machine that no longer exists — dense, honest, every channel visible.* Direction: **Dense** (Berkeley Graphics). Nodes, links, channel states, a cycle counter and a trace pane all live at once; this is a workbench, not a reading surface.

### Architecture

```
UI (vanilla JS, no build step)
  │
  ├── fabric.js ── virtual-time scheduler + link router
  │                 owns the topology graph; owns the clock
  │
  └── N × Worker
        └── t4.wasm (one emulated T800 per instance)
              links 0–3 → postMessage → fabric router
```

Four calls that decide everything:

1. **One emulated transputer per Worker, links routed in JS.** t4 already models four links per node; the port replaces its host-networking backend with a message port. Cleanest seam, matches the hardware's own abstraction, and keeps the WASM untouched apart from that one backend.
2. **Virtual time, not wall-clock.** The fabric owns a cycle counter; Workers run in bounded quanta and report back. Non-negotiable: real-time 64-node on \~10 browser cores is marginal at best, and virtual time additionally makes every run deterministic and therefore reproducible, traceable, and precomputable. Determinism is worth more here than fidelity to 20 MHz.
3. **Topology is data.** A JSON graph of node → link → node, with the period configurations (ring, mesh, hypercube, the reconfigurable crossbar PARAM actually used) as presets. Rewiring is editing the graph, not touching the emulator.
4. **Toolset runs inside.** occam source goes into the emulated D7205A toolset, which emits a real transputer binary, which the fabric loads. Slow, authentic, and it means we ship no compiler of our own.

### Roadmap

- **v1.0 — one node.** t4 in WASM, one Worker, the occam toolset running inside it, a console. Ship a precomputed Livermore 7 trace so the 5 s bar holds while WASM streams in behind it. The hard part of the port is over at this milestone.
- **v1.1 — the fabric.** Link backend swapped, virtual-time scheduler, 2 to 64 nodes, topology presets, the visible channel traffic. This is the artifact people will link to.
- **v1.2 — the workloads.** The period demo set, precomputed traces for each, and the emulated PARAM column feeding back into artifact 1.
- **Deferred, documented:** cycle accuracy, T9000, the graphics instructions, anything above 64 nodes.

### Handoff notes

- **Browser floor:** WASM + Workers + SharedArrayBuffer if the scheduler needs it, which means COOP/COEP headers and therefore a real static host. Check this before writing code — it constrains deployment.
- **Stand-in seam:** a `FakeEmulator` that satisfies the fabric's interface with scripted link traffic, so the fabric, the topology editor and the whole surface can be built and critiqued before the Emscripten port lands. Standard pattern; use it here, the port will take longer than expected.
- **Persistence:** occam source and topology graphs to the user's own folder via File System Access, IndexedDB mirror. No server, no account. Nothing about this tool needs one.
- **Agent face:** `load`, `compile`, `setTopology`, `step`, `runUntil`, `readChannel`, `dumpTrace`. The verifier drives this, not the DOM.
- **Termination condition per milestone:** v1.0 — TVS1F and the T800 FPU tests pass in-browser, same vectors upstream uses. v1.1 — a known occam program produces bit-identical output across 64 nodes on three topologies, and two runs of the same seed produce identical traces. Determinism is the gate.
- **Do not:** reimplement any part of the instruction set in JS; add a wall-clock mode; ship without the precomputed traces; let the topology editor write into emulator memory directly.

## Artifact 3 — the export-control piece

**Thesis.** Every performance threshold ever written into an export-control regime has been overtaken by consumer hardware, and the interval between the line being drawn and the line being crossed keeps shrinking. India appears on the receiving end of that chart twice, 35 years apart.

**The chart.** One axis, FP64-equivalent, log scale, 1987 to 2026. Two series:

- The **control threshold** in force that year — the composite-performance metrics of the COCOM and post-COCOM regimes through the 1990s, then the 2022 performance thresholds and each subsequent revision.
- The **consumer shelf** that year — what an individual could buy without permission.

The story is the crossings, and the shrinking gap between them. Annotate two points: 1987, where the denial of an X-MP/14 to India sat above the line, and the present, where the same argument is being made about accelerators.

**The honest complication, stated up front rather than buried.** The metrics are not commensurable. 1990s regimes counted composite theoretical performance on general-purpose 64-bit arithmetic; current thresholds are built around low-precision throughput and interconnect bandwidth for training runs. A single line through both is a rhetorical device, not a measurement. Say that in the piece, draw it anyway, and show the FP64 series as the one continuous thing underneath. A reader who catches the incommensurability before you admit it stops trusting the rest.

**What makes it worth reading rather than another explainer:** the PARAM outcome. Denial produced a domestic alternative at a fraction of the price that then *exported to the countries running the control regime*. That is the uncomfortable fact for both sides of the current argument, and almost nobody writing about GPU controls has it to hand.

**Roadmap**

- **v1.0** — the piece plus a static chart. Publishable on its own, cites artifact 1, links artifact 2 when it lands.
- **v1.1** — the chart made interactive, same repo, no new architecture.

**Sourcing.** Threshold values come from primary regulatory text — the regulations themselves and the Federal Register notices, not secondary summaries, which get the numbers wrong constantly. Budget real time for this; it is the slowest part of the whole strand and the part most likely to be checked.

## Open questions and escalations

**1. Licensing — resolve before any Emscripten work.** Two separate questions, and the second is the dangerous one.

- *t4 itself* — check the repo's licence. If it is permissive, the port is clean. If it is absent or restrictive, contact the author; this is a small, friendly corner of the internet and an email will probably settle it.
- *The D7205A occam toolset* — INMOS software, rights now sitting somewhere in the ST Microelectronics lineage. It is archived and circulated freely at transputer.net, but *circulated* is not *licensed*, and shipping it inside a public artifact is a different act from a hobbyist downloading it. Options in preference order: confirm a release or abandonment of rights; ship the tool without the toolset and have users supply their own image; or fall back to a modern occam-π compiler targeting transputer bytecode, which costs the authenticity that motivated the whole WASM decision.

This is a genuine fork. v1.0 should not start until it is answered.

**2. Naming.** Needs a check against NAMES.md before anything is created. Wants to be English, short, verb-able. `Loom` is the obvious fit — weaving, links, a machine that runs threads — if it is free. Fallbacks: `Lattice`, `Farm` (period-correct: a transputer farm was the term of art), `Occam` itself if we want to be literal.

**3. The tier boundary.** Three artifacts sharing a numbers CSV is fine. The moment artifact 1's harness becomes a service artifact 2 calls, or the three want one deploy, it has become a Product and needs re-tiering explicitly. Watch for it at v1.2 of artifact 2, where the emulated PARAM column wants to flow back into artifact 1 — that is the exact seam where the drift would start. Keep it a file copied between repos, not a dependency.

**4. Scope risk worth naming now.** Artifact 2 is the one that can consume the whole strand. It is also the least necessary — 1 and 3 stand alone and make the argument without it. If the port stalls, ship 1 and 3, publish, and let 2 arrive late.

**Immediate next step:** the licence check on both items in §1. Everything else waits on it.
