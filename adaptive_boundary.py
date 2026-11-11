"""
adaptive_boundary.py   (Step 1: boundary re-centring in Python, readout level only)

Compares, on drifting IQ data from iq_generator.py, how often the 0/1 discriminator is wrong
(misassignment p) for:

  frozen        boundary fixed at t = 0                                     (no adaptation)
  periodic      re-calibrated with LABELLED shots every --period hours      (costs downtime)
  moment        label-free: boundary midpoint follows the running mean of the unlabelled IQ dots
                (keeps the t=0 orientation and separation; assumes roughly balanced 0/1 stream)
  two-means     label-free: each cloud centroid follows its own running mean, using the
                discriminator's own decisions as labels (also follows rotation and gain)
  oracle        re-calibrated with labels at EVERY step (best possible, used as the floor)

Only the "periodic" and "oracle" methods ever see true labels. "moment" and "two-means" see only
unlabelled dots. True labels are used only to MEASURE every method on fresh dots.

recovery = (mean p_frozen - mean p_method) / (mean p_frozen - mean p_oracle)
1.0 = as good as perfect recalibration, 0.0 = no better than frozen, negative = worse than frozen.

Needs iq_generator.py in the same folder:   git checkout iq-generator -- iq_generator.py
Usage:  python adaptive_boundary.py
        python adaptive_boundary.py --profiles q0 --strengths 4 --p-state1 0.5 0.1 --seeds 5
Outputs: adaptive_boundary.csv, adaptive_boundary.png
"""
import argparse
import csv

import numpy as np

from iq_generator import DriftParams, IQDriftGenerator

ETA = 0.3  # how far each batch pulls the boundary (fixed in advance, NOT tuned on the results)


def classify(iq, c0, c1):
    return (np.abs(iq - c1) < np.abs(iq - c0)).astype(int)


def misassign(iq, st, c0, c1):
    pred = classify(iq, c0, c1)
    return 0.5 * (np.mean(pred[st == 1] == 0) + np.mean(pred[st == 0] == 1))


def calibrate(gen, t, n):
    iq, st = gen.generate_shots(n_shots=n, t_hours=t)
    return iq[st == 0].mean(), iq[st == 1].mean()


def run(profile, strength, p1, hours, step, period, n_unlab, n_eval, n_cal, seed, eta=ETA):
    gen = IQDriftGenerator(DriftParams(drift_profile=profile, stochastic_drift_strength=strength, rng_seed=seed))
    f0, f1 = calibrate(gen, 0, 20000)                 # frozen discriminator
    w0 = f1 - f0                                       # t=0 orientation and separation
    mom_mid = (f0 + f1) / 2                            # moment method state
    tm0, tm1 = f0, f1                                  # two-means state
    pc0, pc1 = f0, f1                                  # periodic state
    times = np.arange(0, hours + 1e-9, step)
    res = {k: [] for k in ("frozen", "periodic", "moment", "two-means", "oracle")}
    last_cal = 0.0
    for t in times:
        # unlabelled stream the adaptive methods get to see (natural 0/1 mix p1)
        iq_u, _ = gen.generate_shots(n_shots=n_unlab, t_hours=t, p_state1=p1)
        # moment: move the midpoint toward the running mean of the stream
        mom_mid = (1 - eta) * mom_mid + eta * iq_u.mean()
        m0, m1 = mom_mid - w0 / 2, mom_mid + w0 / 2
        # two-means: assign with own decisions, pull each centroid toward its members' mean
        lab = classify(iq_u, tm0, tm1)
        if (lab == 0).sum() > 10: tm0 = (1 - eta) * tm0 + eta * iq_u[lab == 0].mean()
        if (lab == 1).sum() > 10: tm1 = (1 - eta) * tm1 + eta * iq_u[lab == 1].mean()
        # periodic labelled recalibration
        if t - last_cal >= period - 1e-9:
            pc0, pc1 = calibrate(gen, t, n_cal); last_cal = t
        # oracle
        o0, o1 = calibrate(gen, t, n_cal)
        # measure everything on fresh labelled dots (balanced, so numbers are comparable across p1)
        iq_e, st_e = gen.generate_shots(n_shots=n_eval, t_hours=t, p_state1=0.5)
        for k, (a, b) in {"frozen": (f0, f1), "periodic": (pc0, pc1), "moment": (m0, m1),
                          "two-means": (tm0, tm1), "oracle": (o0, o1)}.items():
            res[k].append(misassign(iq_e, st_e, a, b))
    return times, {k: np.array(v) for k, v in res.items()}


def recovery(res, k):
    den = res["frozen"].mean() - res["oracle"].mean()
    return np.nan if den < 1e-3 else (res["frozen"].mean() - res[k].mean()) / den


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--profiles", nargs="+", default=["q0", "q1", "q2"])
    ap.add_argument("--strengths", nargs="+", type=float, default=[1.0, 4.0])
    ap.add_argument("--p-state1", nargs="+", type=float, default=[0.5, 0.1], help="fraction of |1> in the unlabelled stream")
    ap.add_argument("--hours", type=float, default=168.0)
    ap.add_argument("--step", type=float, default=4.0)
    ap.add_argument("--period", type=float, default=24.0, help="periodic recalibration interval (hours)")
    ap.add_argument("--seeds", type=int, default=3)
    ap.add_argument("--n-unlab", type=int, default=1500)
    ap.add_argument("--n-eval", type=int, default=3000)
    ap.add_argument("--n-cal", type=int, default=2000)
    a = ap.parse_args()

    methods = ("frozen", "periodic", "moment", "two-means", "oracle")
    print(f"{'profile':6s} {'str':>4s} {'p(|1>)':>6s} | mean misassign %  frozen  periodic  moment  2-means  oracle | recovery  periodic  moment  2-means")
    rows, example = [], None
    for prof in a.profiles:
        for s in a.strengths:
            for p1 in a.p_state1:
                R = []
                for seed in range(a.seeds):
                    t, r = run(prof, s, p1, a.hours, a.step, a.period, a.n_unlab, a.n_eval, a.n_cal, seed=100 + seed)
                    R.append(r)
                    gap = r["frozen"].mean() - r["oracle"].mean()
                    if p1 == 0.5 and seed == 0 and (example is None or gap > example[5]):
                        example = (t, r, prof, s, p1, gap)   # plot the balanced case with the most drift
                mean = {k: np.mean([x[k].mean() for x in R]) * 100 for k in methods}
                rec = {k: np.nanmean([recovery(x, k) for x in R]) for k in ("periodic", "moment", "two-means")}
                recsd = {k: np.nanstd([recovery(x, k) for x in R]) for k in ("periodic", "moment", "two-means")}
                print(f"{prof:6s} {s:4.1f} {p1:6.2f} | {'':16s}{mean['frozen']:6.2f} {mean['periodic']:8.2f} {mean['moment']:7.2f} {mean['two-means']:8.2f} {mean['oracle']:7.2f} |"
                      f"          {rec['periodic']:7.2f} {rec['moment']:7.2f} {rec['two-means']:8.2f}   (+/- {recsd['two-means']:.2f})")
                rows.append((prof, s, p1, *[mean[k] for k in methods], *[rec[k] for k in ("periodic", "moment", "two-means")]))
    with open("adaptive_boundary.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["profile", "strength", "p_state1", *[f"misassign_pct_{k}" for k in methods], "recovery_periodic", "recovery_moment", "recovery_two_means"])
        w.writerows(rows)

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    t, r, prof, s, p1, _ = example
    plt.figure(figsize=(9, 4.2))
    for k in methods:
        plt.plot(t, r[k] * 100, label=k, lw=2 if k in ("frozen", "two-means") else 1.2, ls="--" if k == "oracle" else "-")
    plt.xlabel("hours"); plt.ylabel("misassignment (%)"); plt.legend(fontsize=8)
    plt.title(f"{prof}, drift strength {s:g}, unlabelled stream {p1:.0%} |1>"); plt.tight_layout(); plt.savefig("adaptive_boundary.png", dpi=150)
    print("\nwrote adaptive_boundary.csv and adaptive_boundary.png")


if __name__ == "__main__":
    main()
