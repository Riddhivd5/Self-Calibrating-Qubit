"""
adaptive_boundary_v2.py   (Step 1b: fixes for the 80% target; does not modify adaptive_boundary.py)

Fix 1  imbalance : the unlabelled stream is mostly |0> in real QEC. The fraction of |1> (pi) is estimated
                   ONCE from the discriminator's own decisions at t=0 (no labels), then used to correct
                   the running average ("moment+pi") or as the prior of a soft 2-cluster fit ("EM+pi").
Fix 2  detector  : the update step size depends on the syndrome detector. Quiet -> small steps,
                   alarm -> big steps. The detector is modelled from the Stim results: it alarms when the
                   detector fire rate (a function of the readout error the deployed boundary is causing,
                   taken from a Stim lookup table) is 30% above its healthy level, the same rule as
                   real_drift_detector.py. It is not re-simulated in Stim at every step.
Honest testing   : the two step sizes are CHOSEN on profile q0 with seeds 0-4, then every number that is
                   reported comes from seeds 100+ and includes profiles q1 and q2 that were never used for
                   choosing.

recovery = (mean p_frozen - mean p_method) / (mean p_frozen - mean p_oracle), per run. Only "periodic" and
"oracle" ever use labels to adapt; true labels are otherwise used only to MEASURE error.

Needs iq_generator.py, adaptive_boundary.py, drift_framework.py in the same folder.
Usage: python adaptive_boundary_v2.py            (about 5 minutes)
Outputs: adaptive_boundary_v2.csv, adaptive_boundary_v2.png, fire_table.npy (cache)
"""
import argparse
import csv
import os

import numpy as np

from adaptive_boundary import classify, misassign
from iq_generator import DriftParams, IQDriftGenerator

P_PHYS, D, ALARM_RISE = 0.001, 5, 0.30
P1S = (0.5, 0.1)
ETA_FIXED = 0.3     # step size of the fixed-step variants (same as v1)
PERIOD = 24.0
METHODS = ("frozen", "periodic", "moment (v1)", "two-means (v1)", "moment+pi", "EM+pi",
           "moment+pi gated", "EM+pi gated", "oracle")


# ---------------------------------------------------------------- detector model
def fire_table(cache="fire_table.npy"):
    if os.path.exists(cache):
        return np.load(cache)
    from drift_framework import build_circuit, sample_window
    grid = np.array([0.0002, 0.0005, 0.001, 0.002, 0.004, 0.007, 0.01, 0.015, 0.02, 0.03,
                     0.045, 0.06, 0.08, 0.12, 0.2, 0.3, 0.5])
    fr = [sample_window(build_circuit(D, p_readout=p, p_phys=P_PHYS), 20000, seed=7)[0].mean() for p in grid]
    arr = np.vstack([grid, fr]); np.save(cache, arr); return arr


# ---------------------------------------------------------------- data (generated once, replayed for every method)
def make_data(profile, strength, seed, hours=168.0, step=4.0, n_unl=1500, n_eval=3000, n_cal=2000):
    gen = IQDriftGenerator(DriftParams(drift_profile=profile, stochastic_drift_strength=strength, rng_seed=seed))
    iq, st = gen.generate_shots(n_shots=20000, t_hours=0)
    f0, f1 = iq[st == 0].mean(), iq[st == 1].mean()
    sig2 = 0.5 * np.mean(np.r_[np.abs(iq[st == 0] - f0) ** 2, np.abs(iq[st == 1] - f1) ** 2])
    times = np.arange(0, hours + 1e-9, step)
    steps = []
    for t in times:
        steps.append(dict(t=t,
                          unl={p1: gen.generate_shots(n_shots=n_unl, t_hours=t, p_state1=p1) for p1 in P1S},
                          ev=gen.generate_shots(n_shots=n_eval, t_hours=t, p_state1=0.5),
                          cal=gen.generate_shots(n_shots=n_cal, t_hours=t)))
    return dict(f0=f0, f1=f1, sig2=sig2, steps=steps)


# ---------------------------------------------------------------- the methods
def em_step(iq, c0, c1, pi, sig2):
    """One soft 2-cluster update with fixed prior pi for |1>."""
    l1 = np.log(pi) - np.abs(iq - c1) ** 2 / (2 * sig2)
    l0 = np.log(1 - pi) - np.abs(iq - c0) ** 2 / (2 * sig2)
    r = 1.0 / (1.0 + np.exp(np.clip(l0 - l1, -50, 50)))
    n1, n0 = r.sum(), (1 - r).sum()
    n0c = (1 - r) @ iq / n0 if n0 > 10 else c0
    n1c = r @ iq / n1 if n1 > 10 else c1
    return n0c, n1c


def simulate(data, p1, fire, eta_q, eta_a):
    f0, f1, sig2 = data["f0"], data["f1"], data["sig2"]
    w0 = f1 - f0
    u0 = data["steps"][0]["unl"][p1][0]
    pi = float(np.clip(classify(u0, f0, f1).mean(), 0.02, 0.98))        # label-free estimate
    st0 = data["steps"][0]["unl"][p1]
    p_ref = max(np.mean(classify(st0[0], f0, f1) != st0[1]), 1e-3)
    fire_thr = (1 + ALARM_RISE) * np.interp(p_ref, fire[0], fire[1])

    S = {m: [f0, f1] for m in METHODS}
    mid = (f0 + f1) / 2
    out = {m: [] for m in METHODS}
    last_cal = 0.0
    for sd in data["steps"]:
        t = sd["t"]; iq, stt = sd["unl"][p1]; eiq, est = sd["ev"]; ciq, cst = sd["cal"]

        def detector_alarm(c0, c1):
            p_cur = np.mean(classify(iq, c0, c1) != stt)     # error the deployed boundary is causing in the stream
            return np.interp(p_cur, fire[0], fire[1]) > fire_thr

        # v1 methods (balanced assumption / hard assignment), fixed step
        mid = (1 - ETA_FIXED) * mid + ETA_FIXED * iq.mean()
        S["moment (v1)"] = [mid - w0 / 2, mid + w0 / 2]
        c0, c1 = S["two-means (v1)"]; lab = classify(iq, c0, c1)
        if (lab == 0).sum() > 10: c0 = (1 - ETA_FIXED) * c0 + ETA_FIXED * iq[lab == 0].mean()
        if (lab == 1).sum() > 10: c1 = (1 - ETA_FIXED) * c1 + ETA_FIXED * iq[lab == 1].mean()
        S["two-means (v1)"] = [c0, c1]

        # fix 1: pi-corrected, fixed step; fix 1+2: pi-corrected, detector-controlled step
        for name, gated in (("moment+pi", False), ("moment+pi gated", True)):
            c0, c1 = S[name]
            eta = (eta_a if detector_alarm(c0, c1) else eta_q) if gated else ETA_FIXED
            c0 = (1 - eta) * c0 + eta * (iq.mean() - pi * w0)
            S[name] = [c0, c0 + w0]
        for name, gated in (("EM+pi", False), ("EM+pi gated", True)):
            c0, c1 = S[name]
            eta = (eta_a if detector_alarm(c0, c1) else eta_q) if gated else ETA_FIXED
            n0, n1 = em_step(iq, c0, c1, pi, sig2)
            S[name] = [(1 - eta) * c0 + eta * n0, (1 - eta) * c1 + eta * n1]

        # labelled baselines
        o0, o1 = ciq[cst == 0].mean(), ciq[cst == 1].mean()
        if t - last_cal >= PERIOD - 1e-9:
            S["periodic"] = [o0, o1]; last_cal = t
        S["oracle"] = [o0, o1]

        for m in METHODS:                     # measure on fresh balanced labelled dots
            out[m].append(misassign(eiq, est, *S[m]))
    return {m: np.array(v) for m, v in out.items()}


def recovery(r, m):
    den = r["frozen"].mean() - r["oracle"].mean()
    return np.nan if den < 0.002 else (r["frozen"].mean() - r[m].mean()) / den


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tune-seeds", type=int, default=5)
    ap.add_argument("--test-seeds", type=int, default=8)
    ap.add_argument("--strengths", nargs="+", type=float, default=[1.0, 4.0])
    a = ap.parse_args()
    fire = fire_table()

    # ---- choose the two step sizes on q0, seeds 0..4 only
    print("choosing step sizes on q0 with tuning seeds (never reported below)...")
    tune = [(s, make_data("q0", s, seed)) for s in a.strengths for seed in range(a.tune_seeds)]
    best = None
    for eq in (0.05, 0.1, 0.2, 0.3):
        for ea in (0.5, 0.7, 0.9):
            rec = [recovery(simulate(d, p1, fire, eq, ea), m) for _, d in tune for p1 in P1S
                   for m in ("moment+pi gated", "EM+pi gated")]
            score = np.nanmedian(rec)
            if best is None or score > best[0]: best = (score, eq, ea)
    print(f"  chosen: eta_quiet={best[1]}, eta_alarm={best[2]}   (tuning-set median recovery {best[0]:.2f})")
    eq, ea = best[1], best[2]

    # ---- held-out test: new seeds (100+), all three profiles
    rows = []
    hdr = f"{'profile':6s} {'str':>3s} {'p(|1>)':>6s} {'gap pp':>6s} |" + "".join(f"{m[:11]:>12s}" for m in METHODS[1:-1])
    print("\nMEDIAN RECOVERY over held-out seeds  (1.0 = as good as oracle, negative = worse than frozen)\n" + hdr)
    example = {}
    for prof in ("q0", "q1", "q2"):
        for s in a.strengths:
            data = [make_data(prof, s, 100 + k) for k in range(a.test_seeds)]
            for p1 in P1S:
                R = [simulate(d, p1, fire, eq, ea) for d in data]
                gap = np.mean([(r["frozen"].mean() - r["oracle"].mean()) * 100 for r in R])
                line = f"{prof:6s} {s:3.0f} {p1:6.2f} {gap:6.2f} |"
                for m in METHODS[1:-1]:
                    rec = np.array([recovery(r, m) for r in R])
                    med = np.nanmedian(rec) if np.isfinite(rec).any() else np.nan
                    fin = np.isfinite(rec)                       # runs with no drift to recover are skipped, not counted as failures
                    frac = np.mean(rec[fin] >= 0.8) if fin.any() else np.nan
                    rows.append((prof, s, p1, gap, m, med, frac, int(fin.sum())))
                    line += f"{med:12.2f}" if np.isfinite(med) else f"{'n/a':>12s}"
                print(line)
                if (prof, s, p1) in (("q1", 4.0, 0.5), ("q1", 4.0, 0.1)):
                    example[p1] = (data[0]["steps"], R[0])
    print("\nFRACTION OF HELD-OUT RUNS WITH RECOVERY >= 0.8   (n/a = no drift to recover)")
    print(f"{'profile':6s} {'str':>3s} {'p(|1>)':>6s} {'runs':>4s} |" + "".join(f"{m[:11]:>12s}" for m in METHODS[1:-1]))
    for prof in ("q0", "q1", "q2"):
        for s in a.strengths:
            for p1 in P1S:
                sel = [r for r in rows if r[0] == prof and r[1] == s and r[2] == p1]
                print(f"{prof:6s} {s:3.0f} {p1:6.2f} {sel[0][7]:4d} |" + "".join(
                    (f"{r[6]:12.2f}" if np.isfinite(r[6]) else f"{'n/a':>12s}") for r in sel))

    with open("adaptive_boundary_v2.csv", "w", newline="") as fh:
        w = csv.writer(fh); w.writerow(["profile", "strength", "p_state1", "frozen_minus_oracle_pp", "method",
                                        "median_recovery", "fraction_runs_ge_0.8", "n_runs_with_drift", "eta_quiet", "eta_alarm"])
        for r in rows: w.writerow([*r, eq, ea])

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1, 2, figsize=(12, 4.2), sharey=True)
    for k, p1 in enumerate(P1S):
        steps, r = example[p1]; t = [x["t"] for x in steps]
        for m, kw in (("frozen", dict(lw=2)), ("periodic", dict(lw=1)), ("moment (v1)", dict(lw=1)),
                      ("EM+pi gated", dict(lw=2.2)), ("moment+pi gated", dict(lw=1.4)), ("oracle", dict(ls="--", lw=1.2))):
            ax[k].plot(t, r[m] * 100, label=m, **kw)
        ax[k].set_title(f"q1, drift x4, stream {p1:.0%} |1>  (held-out seed)"); ax[k].set_xlabel("hours")
    ax[0].set_ylabel("misassignment (%)"); ax[0].legend(fontsize=8)
    fig.tight_layout(); fig.savefig("adaptive_boundary_v2.png", dpi=150)
    print("\nwrote adaptive_boundary_v2.csv and adaptive_boundary_v2.png")


if __name__ == "__main__":
    main()
