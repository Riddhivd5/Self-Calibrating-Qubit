"""
detector_scoring.py -- false positives, false negatives and detection delay of the v5 fire-rate alarm, with the truth
defined by what was injected (not by the alarm's own input), under readout-only, physical-only and combined drift, and for
several window sizes.

The alarm is adaptive_boundary_v5.ControllerV5, unchanged: reference = K_REF windows recorded right after calibration, alarm when
the fire-rate z-score exceeds ZTHR and the relative rise exceeds REL_RISE. Thresholds are NOT retuned per window size or per case.
The decision boundary is frozen at its calibration value throughout (the detector is scored on its own, without adaptation).

Part A, controlled states (iq_generator_controlled.py; noise and decay tail of the chosen qubit's refit profile, no other drift):
  each seed is a fresh calibration and a fresh reference; then, for every case, a stream of windows at a fixed state.
    healthy          : nothing changed                                  -> every alarm is a false positive
    readout s sigma  : both clouds displaced by s cloud sigma           -> every silent window is a false negative
    physical x f     : readout unchanged, physical error rate times f   -> the alarm fires although the readout did not drift
    combined         : both at once
  Detection delay for a step: windows until the first alarm in the stream that starts at the step (window 1 is the first window
  after the step); the alarm decides at the end of a window, so delay in shots = windows x window size.
Part B, trajectories at the v5 window size: fitted profiles (refit on the 149 real snapshots, events on) and the real IBM
  snapshots. Every window is scored, including the in-between ones: alarm probability is reported against the window's true
  rise in readout error (actual flip rate minus the flip rate of the reference windows, in percentage points; the fire rate
  responds to the absolute rise, so a ratio would not be comparable between qubits), and for the fitted profiles also by whether
  a generator event was active. Real data: the reference windows can only draw on the first snapshot's held-out IQ points
  (500 per state), so the real reference is noisier than it would be on a device.

Usage (repo root): python detector_scoring.py --out-dir results/<new folder>
"""
import argparse
import csv
import json
import os
import sys
import time

import numpy as np

import adaptive_boundary_v5 as v5
import ler_comparison as lc
from iq_generator_controlled import make_controlled
from iq_generator_refit import make_generator

BINS = [(-1e9, 0.25), (0.25, 0.5), (0.5, 0.75), (0.75, 1.0), (1.0, 2.0), (2.0, 1e9)]  # rise in readout error, percentage points


def wilson(k, n, z=1.96):
    if n == 0:
        return float("nan"), float("nan")
    return lc.wilson(k, n, z)


def state_pools(q, seed, shift, n_pool):
    g = make_controlled(q, seed=seed, kind="step", shift_sigma=shift, t_on=0.0)
    return g.generate_shots(n_shots=n_pool, t_hours=1.0, p_state1=0.0)[0], g.generate_shots(n_shots=n_pool, t_hours=1.0, p_state1=1.0)[0]


def stream(hw, pools, c0, c1, n, seed):
    """n consecutive windows at a fixed state: (alarm inputs, true flip rate)."""
    smp, rng = hw.sampler(seed), np.random.default_rng(seed)
    fire, flip = [], []
    for _ in range(n):
        fire.append(hw.features(hw.syndromes(smp, pools[0], pools[1], c0, c1, rng))[0])
        flip.append(hw.last_flip_rate)
    return np.array(fire), np.array(flip)


def part_a(a, hws, rows, L):
    cases = [("healthy", 0.0, 1.0)]
    cases += [(f"readout {s:g} sigma", s, 1.0) for s in a.shifts]
    cases += [(f"physical x{f:g}", 0.0, f) for f in a.phys]
    cases += [(f"combined {s:g} sigma, x{f:g}", s, f) for s, f in ((0.5, 1.5), (1.0, 2.0))]
    res = {}
    for k in range(a.seeds):
        seed = a.seed0 + k
        cal = make_controlled(a.qubit, seed=seed, kind="step", shift_sigma=0.0)
        iq, st = cal.generate_shots(n_shots=20000, t_hours=0)
        c0, c1 = iq[st == 0].mean(), iq[st == 1].mean()
        pools = {s: state_pools(a.qubit, seed + 10_000 * (i + 1), s, a.n_pool) for i, s in enumerate(sorted({c[1] for c in cases}))}
        ref_pool = state_pools(a.qubit, seed + 900_000, 0.0, a.n_pool)   # reference and healthy test use independent IQ draws
        for win in a.windows:
            v5.WIN = win
            hw0 = hws(v5.P_PHYS)
            rf, rflip = stream(hw0, ref_pool, c0, c1, v5.K_REF, 40_000 + seed)
            ctrl = v5.ControllerV5(rf)
            for ci, (name, s, f) in enumerate(cases):
                hw = hws(v5.P_PHYS * f)
                fire, flip = stream(hw, pools[s], c0, c1, a.stream, 50_000 + 1000 * seed + 37 * ci + win)
                al = np.array([ctrl.alarm(x, 0.0) for x in fire])
                first = int(np.argmax(al)) + 1 if al.any() else 0
                res.setdefault((name, win), []).append(dict(al=al, flip=flip.mean(), ref=rflip.mean(), first=first,
                                                            rise=fire.mean() / ctrl.m - 1))
        print(f"  part A seed {k + 1}/{a.seeds} done", flush=True)
    L.append("## Part A: controlled states")
    L.append(f"{a.seeds} independent calibrations (seeds {a.seed0}-{a.seed0 + a.seeds - 1}), {a.stream} consecutive windows per case, qubit {a.qubit}, "
             f"d={v5.D}, physical error {v5.P_PHYS}. One shot = {v5.D} syndrome rounds. Intervals: 95% Wilson over all windows, and in "
             "brackets the range of the per-calibration alarm fraction (10th-90th percentile), because windows that share a reference are not independent.")
    L.append("")
    for win in a.windows:
        L.append(f"### Window = {win} shots ({win * v5.D} syndrome rounds)")
        L.append("")
        L.append("| case | readout error (x healthy) | fire-rate rise | windows | alarm fraction [95% CI] (10th-90th pct over calibrations) | reads as | "
                 "first alarm: median / 90th pct window | median delay in shots (syndrome rounds) | streams never alarmed |")
        L.append("|---|---|---|---|---|---|---|---|---|")
        for name, s, f in cases:
            R = res[(name, win)]
            al = np.concatenate([r["al"] for r in R])
            k, n = int(al.sum()), len(al)
            lo, hi = wilson(k, n)
            per = np.array([r["al"].mean() for r in R])
            ratio = np.mean([r["flip"] for r in R]) / np.mean([r["ref"] for r in R])
            firsts = np.array([r["first"] for r in R])
            hit = firsts[firsts > 0]
            kind = "false-positive rate" if name == "healthy" else ("alarm without readout drift" if s == 0 else "detection rate (1 - false-negative rate)")
            if name == "healthy" or not len(hit):
                d1 = d2 = "-"
            else:
                d1 = f"{np.median(hit):.0f} / {np.percentile(hit, 90):.0f}"
                d2 = f"{np.median(hit) * win:.0f} ({np.median(hit) * win * v5.D:.0f})"
            L.append(f"| {name} | {np.mean([r['flip'] for r in R]):.4f} ({ratio:.2f}x) | {100 * np.mean([r['rise'] for r in R]):+.1f}% | {n} | "
                     f"{k / n:.3f} [{lo:.3f}, {hi:.3f}] ({np.percentile(per, 10):.2f}-{np.percentile(per, 90):.2f}) | {kind} | {d1} | {d2} | "
                     f"{int((firsts == 0).sum())}/{len(firsts)} |")
            rows.append(dict(part="A", source=name, window=win, group="all", n_windows=n, alarms=k, alarm_fraction=k / n, ci_lo=lo, ci_hi=hi,
                             readout_error=np.mean([r["flip"] for r in R]), error_ratio=ratio, fire_rise=np.mean([r["rise"] for r in R]),
                             median_first_alarm_window=(np.median(hit) if len(hit) else ""), never_alarmed=int((firsts == 0).sum()),
                             streams=len(firsts)))
        L.append("")


def trajectory(data, hw, seed):
    """v5 alarm on the frozen boundary along a trajectory; returns alarm, true flip rate, reference flip rate."""
    smp, rng, s0 = hw.sampler(40_000 + seed), np.random.default_rng(40_000 + seed), data["steps"][0]
    rf, rflip = [], []
    for _ in range(v5.K_REF):
        rf.append(hw.features(hw.syndromes(smp, s0["pool0"], s0["pool1"], data["f0"], data["f1"], rng))[0])
        rflip.append(hw.last_flip_rate)
    ctrl = v5.ControllerV5(np.array(rf))
    smp, rng = hw.sampler(30_000 + seed), np.random.default_rng(seed)
    al, fl = [], []
    for sd in data["steps"]:
        al.append(ctrl.alarm(*hw.features(hw.syndromes(smp, sd["pool0"], sd["pool1"], data["f0"], data["f1"], rng))))
        fl.append(hw.last_flip_rate)
    return np.array(al), np.array(fl), float(np.mean(rflip))


def binned(L, rows, source, al, rise, extra=None):
    L.append("| true rise in readout error over the reference (percentage points) | windows | alarm fraction [95% CI] |")
    L.append("|---|---|---|")
    for lo_, hi_ in BINS:
        m = (rise >= lo_) & (rise < hi_)
        k, n = int(al[m].sum()), int(m.sum())
        lo, hi = wilson(k, n)
        lab = f"under {hi_:g}" if lo_ < -1e8 else (f"{lo_:g} to {hi_:g}" if hi_ < 1e8 else f"over {lo_:g}")
        L.append(f"| {lab} | {n} | " + (f"{k / n:.3f} [{lo:.3f}, {hi:.3f}] |" if n else "- |"))
        rows.append(dict(part="B", source=source, window=v5.WIN, group=f"rise {lab} pp", n_windows=n, alarms=k,
                         alarm_fraction=(k / n if n else ""), ci_lo=lo, ci_hi=hi))
    for lab, m in (extra or []):
        k, n = int(al[m].sum()), int(m.sum())
        lo, hi = wilson(k, n)
        L.append(f"| {lab} | {n} | " + (f"{k / n:.3f} [{lo:.3f}, {hi:.3f}] |" if n else "- |"))
        rows.append(dict(part="B", source=source, window=v5.WIN, group=lab, n_windows=n, alarms=k, alarm_fraction=(k / n if n else ""),
                         ci_lo=lo, ci_hi=hi))
    L.append("")


def part_b(a, hws, rows, L):
    v5.WIN = a.traj_window
    hw0 = hws(v5.P_PHYS)
    L.append(f"## Part B: trajectories, window = {v5.WIN} shots, every window scored")
    L.append("")
    L.append("Reference readout error per trajectory is the mean flip rate of its own reference windows. On real data those windows draw on the "
             "first snapshot's 500 held-out IQ points per state, so the real reference carries visible sampling noise.")
    L.append("")
    for q in ("q0", "q1", "q2"):
        AL, RT, EV, REF = [], [], [], []
        for k in range(a.traj_seeds):
            seed = a.seed0 + 500 + k
            data = lc.make_data_from(lambda: make_generator(q, seed=seed, events=True), seed, hours=a.refit_hours, step=a.refit_step)
            g = make_generator(q, seed=seed, events=True)
            ev = np.array([bool(getattr(g, "active_events", lambda t: [])(sd["t"])) for sd in data["steps"]])
            al, fl, ref = trajectory(data, hw0, seed)
            REF.append(ref)
            AL.append(al); RT.append(100 * (fl - ref)); EV.append(ev)
        al, rt, ev = np.concatenate(AL), np.concatenate(RT), np.concatenate(EV)
        L.append(f"### Fitted profile {q} ({a.traj_seeds} trajectories of {a.refit_hours:g} h at {a.refit_step:g} h steps, events on; {len(al)} windows, "
                 f"{int(ev.sum())} with a generator event active; reference readout error "
                 f"{100 * np.mean(REF):.2f}%, alarms on {int(al.sum())} windows)")
        L.append("")
        binned(L, rows, f"fitted {q}", al, rt, [("generator event active", ev), ("no event active", ~ev)])
        print(f"  part B fitted {q} done", flush=True)
    for q in (0, 1, 2):
        AL, RT, REF = [], [], []
        for rep in range(a.real_reps):
            data = lc.make_real_data(q, a.data_dir, rep)
            al, fl, ref = trajectory(data, hw0, 700 + rep)
            REF.append(ref)
            AL.append(al); RT.append(100 * (fl - ref))
        al, rt = np.concatenate(AL), np.concatenate(RT)
        L.append(f"### Real IBM snapshots q{q} ({len(AL[0])} snapshots x {a.real_reps} repetitions = {len(al)} windows; repetitions re-draw the QEC "
                 "shots over the SAME 15.6-day trajectory, so the intervals describe sampling noise only, not other devices or periods; "
                 f"reference readout error {100 * np.mean(REF):.2f}%, alarms on {int(al.sum())} windows)")
        L.append("")
        binned(L, rows, f"real q{q}", al, rt)
        print(f"  part B real q{q} done", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default=".")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--data-dir", default="data")
    ap.add_argument("--qubit", default="q1")
    ap.add_argument("--seeds", type=int, default=20, help="part A: independent calibrations")
    ap.add_argument("--seed0", type=int, default=300)
    ap.add_argument("--stream", type=int, default=40, help="part A: consecutive windows per case")
    ap.add_argument("--windows", nargs="+", type=int, default=[250, 500, 1000, 1500])
    ap.add_argument("--shifts", nargs="+", type=float, default=[0.1, 0.15, 0.25, 0.35, 0.5, 1.0])
    ap.add_argument("--phys", nargs="+", type=float, default=[1.5, 2.0, 3.0])
    ap.add_argument("--n-pool", type=int, default=40000)
    ap.add_argument("--traj-window", type=int, default=1500)
    ap.add_argument("--traj-seeds", type=int, default=8)
    ap.add_argument("--real-reps", type=int, default=8)
    ap.add_argument("--refit-hours", type=float, default=336.0)
    ap.add_argument("--refit-step", type=float, default=2.0)
    ap.add_argument("--d", type=int, default=5)
    ap.add_argument("--pphys", type=float, default=0.001)
    ap.add_argument("--skip-b", action="store_true")
    a = ap.parse_args()
    v5.D, v5.P_PHYS = a.d, a.pphys
    os.makedirs(a.out_dir, exist_ok=True)
    outs = [os.path.join(a.out_dir, f) for f in ("detector_scoring.md", "detector_scoring.csv", "detector_scoring_config.json")]
    if any(os.path.exists(f) for f in outs) and not a.force:
        sys.exit(f"outputs exist in {a.out_dir}; use a new --out-dir or --force")
    import pymatching
    import stim
    json.dump(dict(args=vars(a), cmd=" ".join(sys.argv), time=time.strftime("%Y-%m-%d %H:%M:%S"), numpy=np.__version__,
                   stim=stim.__version__, pymatching=pymatching.__version__), open(outs[2], "w"), indent=1)
    cache = {}
    hws = lambda pp: cache.setdefault(round(pp, 6), lc.HW(pp))
    rows = []
    L = ["# Detector scoring: v5 fire-rate alarm, truth defined by the injected drift", "",
         f"Alarm: z-score > {v5.ZTHR} and relative rise > {v5.REL_RISE} against {v5.K_REF} reference windows recorded right after calibration "
         "(adaptive_boundary_v5.ControllerV5, unchanged; thresholds not retuned per window size or case). Frozen boundary throughout.", ""]
    part_a(a, hws, rows, L)
    if not a.skip_b:
        part_b(a, hws, rows, L)
    open(outs[0], "w").write("\n".join(L) + "\n")
    keys = []
    for r in rows:
        keys += [k for k in r if k not in keys]
    with open(outs[1], "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=keys)
        w.writeheader(); w.writerows(rows)
    print("\n".join(L))
    print(f"\nwrote {outs[0]} and {outs[1]}")


if __name__ == "__main__":
    main()
