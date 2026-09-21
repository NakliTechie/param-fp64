#!/usr/bin/env python3
"""param-fp64 harness. stdlib only.

  bench.py build            compile kernels with the pinned flag set
  bench.py run [--quick]    run all measured cells, write results/raw/*.json and merge into results/results.csv
  bench.py check            schema + citation check over results/results.csv (exit 1 on any violation)
  bench.py table            render RESULT.md from results/results.csv
"""
import csv, json, os, platform, re, subprocess, sys, time
from pathlib import Path
from statistics import median

ROOT = Path(__file__).resolve().parent
KERNELS, BUILD, RESULTS, RAW = ROOT / "kernels", ROOT / "build", ROOT / "results", ROOT / "results" / "raw"
CSV, PUBLISHED = RESULTS / "results.csv", RESULTS / "published.csv"
SOURCES, RESULT_MD = ROOT / "SOURCES.md", ROOT / "RESULT.md"
FLAGS = ["-O2", "-std=c99", "-fno-fast-math"]
CC = os.environ.get("CC", "cc")
RUNS = 5
MIN_S = 1.0
IDLE_S = 60
LOAD_MAX = 4.0  # 1-min load average ceiling; our own 10-process throughput cell lifts it for minutes, so the real guard is busy_procs

COLUMNS = ["workload", "machine", "cores", "mode", "precision", "mflops", "source",
           "compiler", "flags", "runs", "thermal", "citation"]
WORKLOADS = {  # id -> (binary, args)
    "ll7": ("ll7", []),
    "ll7f32": ("ll7f32", []),
    "linpack100": ("linpack", ["100"]),
    "linpack1000": ("linpack", ["1000"]),
}


def sh(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, check=True, **kw).stdout.strip()


def compiler_id():
    return sh([CC, "--version"]).splitlines()[0]


def machine_id():
    """Map this host to a machine id in the table; unknown hosts get a descriptive id."""
    if platform.system() == "Darwin":
        brand = sh(["sysctl", "-n", "machdep.cpu.brand_string"])
        slug = brand.lower().replace("apple ", "").replace(" ", "")
        return slug  # e.g. m4pro, m4max
    return re.sub(r"[^a-z0-9]+", "", platform.processor().lower()) or "unknown"


def perf_cores():
    if platform.system() == "Darwin":
        out = sh(["sysctl", "-n", "hw.perflevel0.logicalcpu"])
        return int(out)
    return os.cpu_count() or 1


def thermal_state():
    if platform.system() == "Darwin":
        try:
            out = sh(["pmset", "-g", "therm"])
            m = re.search(r"CPU_Speed_Limit\s*=\s*(\d+)", out)
            if m:
                return f"speedlimit={m.group(1)}"
            return "no-thermal-warning-recorded" if "No thermal warning" in out else "speedlimit=?"
        except Exception:
            return "speedlimit=?"
    return "?"


def build():
    BUILD.mkdir(exist_ok=True)
    for src, out, extra in (("ll7.c", "ll7", []), ("ll7.c", "ll7f32", ["-DSINGLE"]), ("linpack.c", "linpack", ["-lm"])):
        cmd = [CC, *FLAGS, *extra, "-o", str(BUILD / out), str(KERNELS / src)]
        print(" ".join(cmd))
        subprocess.run(cmd, check=True)
    (BUILD / "flags.txt").write_text(" ".join(FLAGS) + "\n" + compiler_id() + "\n")


def run_once(wid, min_s=MIN_S):
    binary, args = WORKLOADS[wid]
    out = sh([str(BUILD / binary), *args, str(min_s)])
    return json.loads(out)


def run_parallel(wid, nproc, min_s=MIN_S):
    binary, args = WORKLOADS[wid]
    procs = [subprocess.Popen([str(BUILD / binary), *args, str(min_s * 2)],
                              stdout=subprocess.PIPE, text=True) for _ in range(nproc)]
    outs = [json.loads(p.communicate()[0]) for p in procs]
    return {"per_process": outs, "mflops": sum(o["mflops"] for o in outs)}


def busy_procs():
    """Other processes using >40% CPU. Our own kernels are excluded by path."""
    return [l for l in sh(["ps", "-Ao", "%cpu,comm"]).splitlines()[1:]
            if float(l.split()[0]) > 40 and "bench.py" not in l and str(BUILD) not in l]


def load_ok(quick):
    """A benchmark taken on a busy machine is not a benchmark. Refuse unless quiet."""
    load1 = os.getloadavg()[0]
    busy = busy_procs()
    print(f"load1={load1:.2f} busy_procs={len(busy)}")
    if quick:
        return True
    if load1 > 2.0 or busy:
        for b in busy:
            print("  busy:", b.strip()[:100])
        print("machine not quiet; refusing full run (use --quick to override for a smoke test)")
        return False
    return True


def run(quick=False):
    if not (BUILD / "ll7").exists():
        build()
    if not load_ok(quick):
        sys.exit(3)
    mid, comp, flags = machine_id(), compiler_id(), " ".join(FLAGS)
    ncores = perf_cores()
    idle = 5 if quick else IDLE_S
    runs = 2 if quick else RUNS
    RAW.mkdir(parents=True, exist_ok=True)
    rows = []
    for wid in WORKLOADS:
        # cold: idle first, then a single run
        print(f"[{wid}] idling {idle}s for cold cell", flush=True)
        time.sleep(idle)
        others = busy_procs()
        if not quick and (os.getloadavg()[0] > LOAD_MAX or others):
            print(f"[{wid}] load1={os.getloadavg()[0]:.2f} busy={len(others)}; aborting run, nothing written", flush=True)
            sys.exit(3)
        therm = thermal_state()
        cold = run_once(wid)
        # sustained: back-to-back runs, median
        sus = [run_once(wid) for _ in range(runs)]
        sus_m = median(o["mflops"] for o in sus)
        # throughput: ncores independent processes at once
        par = run_parallel(wid, ncores)
        raw = {"workload": wid, "machine": mid, "compiler": comp, "flags": flags,
               "load1_before": os.getloadavg()[0], "busy_before": len(others),
               "thermal_before": therm, "cold": cold, "sustained": sus, "throughput": par,
               "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S")}
        raw["load1_after"] = os.getloadavg()[0]
        (RAW / f"{mid}-{wid}.json").write_text(json.dumps(raw, indent=1))
        base = dict(workload=wid, precision=cold.get("precision", "fp64"), source="measured", compiler=comp,
                    flags=flags, citation="")
        rows.append({**base, "machine": f"{mid}-1p", "cores": 1, "mode": "single",
                     "mflops": f"{cold['mflops']:.1f}", "runs": 1, "thermal": f"cold;{therm}"})
        rows.append({**base, "machine": f"{mid}-1p", "cores": 1, "mode": "single",
                     "mflops": f"{sus_m:.1f}", "runs": runs, "thermal": "sustained"})
        rows.append({**base, "machine": f"{mid}-{ncores}p", "cores": ncores, "mode": "throughput",
                     "mflops": f"{par['mflops']:.1f}", "runs": 1, "thermal": "sustained"})
        print(f"[{wid}] cold {cold['mflops']:.0f}  sustained {sus_m:.0f}  x{ncores} {par['mflops']:.0f} MFLOPS", flush=True)
    merge_rows(rows, mid)


def read_csv():
    if not CSV.exists():
        return []
    with CSV.open() as f:
        return list(csv.DictReader(f))


def write_csv(rows):
    RESULTS.mkdir(exist_ok=True)
    with CSV.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in COLUMNS})


def merge_rows(new, mid):
    """results.csv = results/published.csv (hand-maintained, cited) + measured rows.
    This machine's previous measured rows are replaced; other machines' are kept."""
    with PUBLISHED.open() as f:
        pub = list(csv.DictReader(f))
    keep = [r for r in read_csv() if r["source"] == "measured" and not r["machine"].startswith(mid + "-")]
    write_csv(pub + keep + new)
    print(f"wrote {CSV} ({len(keep) + len(new)} rows)")


def check():
    rows = read_csv()
    cites = set(re.findall(r"^### `([^`]+)`", SOURCES.read_text(), re.M)) if SOURCES.exists() else set()
    errs = []
    for i, r in enumerate(rows, 2):
        where = f"results.csv:{i} [{r.get('workload')},{r.get('machine')}]"
        if r.get("source") not in ("measured", "published", "reconstructed"):
            errs.append(f"{where}: source must be measured|published|reconstructed, got {r.get('source')!r}")
        if r.get("source") == "measured" and not (r.get("compiler") and r.get("flags") and r.get("runs")):
            errs.append(f"{where}: measured row missing compiler/flags/runs")
        if r.get("source") in ("published", "reconstructed"):
            if not r.get("citation"):
                errs.append(f"{where}: {r['source']} row has no citation")
            elif r["citation"] not in cites:
                errs.append(f"{where}: citation {r['citation']!r} does not resolve in SOURCES.md")
        if not r.get("precision"):
            errs.append(f"{where}: precision missing")
        try:
            float(r.get("mflops", ""))
        except ValueError:
            errs.append(f"{where}: mflops not numeric")
    for r in rows:
        if r.get("source") == "measured":
            mid = r["machine"].rsplit("-", 1)[0]
            rawf = RAW / f"{mid}-{r['workload']}.json"
            if not rawf.exists():
                errs.append(f"measured cell {r['workload']}/{r['machine']} has no raw file {rawf.name}")
                continue
            d = json.loads(rawf.read_text())
            worst = max(d.get("load1_before", 99), d.get("load1_after", 99))
            if worst > LOAD_MAX or d.get("busy_before", 1):
                errs.append(f"measured cell {r['workload']}/{r['machine']}: load {worst:.2f} (max {LOAD_MAX}) or other busy processes ({d.get('busy_before')}) during the run ({rawf.name})")
    for e in errs:
        print("FAIL", e)
    print(f"check: {len(rows)} rows, {len(errs)} violations")
    return 1 if errs else 0


def fmt_cell(r):
    v = float(r["mflops"])
    s = f"{v:,.0f}" if v >= 10 else f"{v:.2f}"
    if r["precision"] != "fp64":
        s += f" ({r['precision']})"
    tag = {"measured": "", "published": " ᵖ", "reconstructed": " ʳ"}[r["source"]]
    return s + tag


def table():
    rows = read_csv()
    if check():
        print("table: refusing to render; fix check violations first")
        return 1
    machines = []
    for r in rows:
        key = (r["machine"], r["mode"], r["thermal"].split(";")[0])
        if key not in machines:
            machines.append(key)
    order = ["ll7", "ll7f32", "linpack100", "linpack1000", "peak", "sustained"]
    workloads = sorted(dict.fromkeys(r["workload"] for r in rows), key=lambda w: order.index(w) if w in order else 99)
    lines = ["# RESULT — FP64 MFLOPS, then and now", "",
             "Generated by `bench.py table` from `results/results.csv`. Every cell is FP64 unless labelled otherwise.",
             "ᵖ published (citation in SOURCES.md) · ʳ reconstructed · unmarked = measured here.", ""]
    hdr = "| machine | mode | thermal | " + " | ".join(workloads) + " |"
    lines += [hdr, "|" + "---|" * (3 + len(workloads))]
    for m, mode, th in machines:
        cells = []
        for w in workloads:
            hit = [r for r in rows if r["machine"] == m and r["mode"] == mode and r["thermal"].split(";")[0] == th and r["workload"] == w]
            cells.append(fmt_cell(hit[0]) if hit else "—")
        lines.append(f"| `{m}` | {mode} | {th} | " + " | ".join(cells) + " |")
    meas = [r for r in rows if r["source"] == "measured"]
    if meas:
        lines += ["", "## Measured-cell conditions", ""]
        for comp, flags in dict.fromkeys((r["compiler"], r["flags"]) for r in meas):
            lines.append(f"- `{comp}` · flags `{flags}` · runs per sustained cell: {max(int(r['runs']) for r in meas)} (median reported)")
        therms = sorted({r["thermal"] for r in meas if r["thermal"].startswith("cold")})
        if therms:
            lines.append(f"- cold-cell thermal state (`pmset -g therm`): {', '.join(t.split(';',1)[1] for t in therms)}")
    RESULT_MD.write_text("\n".join(lines) + "\n")
    print(f"wrote {RESULT_MD}")
    return 0


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "help"
    if cmd == "build":
        build()
    elif cmd == "run":
        run(quick="--quick" in sys.argv)
    elif cmd == "check":
        sys.exit(check())
    elif cmd == "table":
        sys.exit(table())
    else:
        print(__doc__)
