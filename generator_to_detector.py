"""
generator_to_detector.py

Connects the IQ drift generator (iq_generator.py) to the syndrome detector.

    generator IQ dots --(0/1 line frozen at t=0)--> real misassignment p(t)
    p(t) --> Stim surface code --> detection events --> fire rate, round-to-round correlation
    --> alarm rule (same as real_drift_detector.py)

This replaces the made-up error numbers with the actual output of a frozen discriminator,
and lets you dial the drift up with --strength to test bigger drift than the real data shows.

Needs iq_generator.py in the same folder (on the iq-generator branch):
    git checkout iq-generator -- iq_generator.py

Usage:
    python generator_to_detector.py                       # q0,q1,q2 at strength 1 and 4
    python generator_to_detector.py --profiles q1 --strengths 4 --hours 168 --step 4

Outputs: generator_to_detector.csv and generator_to_detector.png
"""
import argparse
import csv

import numpy as np

from drift_framework import Layout, build_circuit, features, sample_window
from iq_generator import DriftParams, IQDriftGenerator

P_PHYS = 0.001      # physical error rate, held fixed: all drift here is readout drift
ZTHR = 3.0          # statistical threshold (same as real_drift_detector.py)
REL_RISE = 0.30     # practical threshold: 30% above the healthy level


def frozen_error(gen, centroid0, centroid1, t, n):
    """Run the frozen nearest-centroid discriminator on fresh dots at time t."""
    iq, states = gen.generate_shots(n_shots=n, t_hours=t)
    pred = np.where(np.abs(iq - centroid0) < np.abs(iq - centroid1), 0, 1)
    e0 = np.mean(pred[states == 0] == 1)   # prepared 0, read 1
    e1 = np.mean(pred[states == 1] == 0)   # prepared 1, read 0
    return (e0 + e1) / 2, e0, e1


def run_one(profile, strength, hours, step, shots, d, n_iq, seed):
    gen = IQDriftGenerator(DriftParams(drift_profile=profile, stochastic_drift_strength=strength, rng_seed=seed))

    # calibrate the discriminator once, at t = 0, then freeze it
    iq, st = gen.generate_shots(n_shots=20000, t_hours=0)
    c0, c1 = iq[st == 0].mean(), iq[st == 1].mean()

    times = np.arange(0, hours + 1e-9, step)
    p_t = np.array([max(frozen_error(gen, c0, c1, t, n_iq)[0], 1e-4) for t in times])

    # healthy baseline = median error over the first few time points
    p_base = float(np.median(p_t[:4]))
    c_base = build_circuit(d, p_readout=p_base, p_phys=P_PHYS)
    lay = Layout(c_base)
    ref = features(sample_window(c_base, 200000, seed=1)[0], lay, np.ones(lay.n_anc))["per_anc"]
    base = [features(sample_window(c_base, shots, seed=100 + k)[0], lay, ref) for k in range(30)]
    bf = np.array([b["fire_rate"] for b in base]); bt = np.array([b["tcorr"] for b in base])

    rows = []
    for i, (t, p) in enumerate(zip(times, p_t)):
        f = features(sample_window(build_circuit(d, p_readout=p, p_phys=P_PHYS), shots, seed=5000 + i)[0], lay, ref)
        zf = (f["fire_rate"] - bf.mean()) / bf.std(); zt = (f["tcorr"] - bt.mean()) / bt.std()
        rise = max(f["fire_rate"] / bf.mean() - 1, f["tcorr"] / bt.mean() - 1)
        rows.append((t, p, f["fire_rate"], f["tcorr"], zf, zt, bool((max(zf, zt) > ZTHR) and (rise > REL_RISE))))
    return times, p_t, p_base, rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--profiles", nargs="+", default=["q0", "q1", "q2"])
    ap.add_argument("--strengths", nargs="+", type=float, default=[1.0, 4.0])
    ap.add_argument("--hours", type=float, default=168.0)
    ap.add_argument("--step", type=float, default=4.0)
    ap.add_argument("--shots", type=int, default=3000, help="QEC shots per time point")
    ap.add_argument("--n-iq", type=int, default=4000, help="IQ shots per time point")
    ap.add_argument("--d", type=int, default=5)
    ap.add_argument("--seed", type=int, default=7)
    a = ap.parse_args()

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    combos = [(p, s) for s in a.strengths for p in a.profiles]
    fig, ax = plt.subplots(len(combos), 2, figsize=(11, 2.3 * len(combos)), squeeze=False)

    print(f"{'profile':7s} {'strength':8s} {'baseline p':10s} {'max p':8s} {'big events':10s} {'caught':7s} {'false alarms':12s} {'detection delay (h)'}")
    out = []
    for k, (prof, s) in enumerate(combos):
        times, p_t, p_base, rows = run_one(prof, s, a.hours, a.step, a.shots, a.d, a.n_iq, a.seed)
        alarm = np.array([r[6] for r in rows])
        big = p_t > 2 * p_base
        quiet = p_t < 1.25 * p_base
        # delay: first time p crosses 2x baseline -> first alarm at or after that time
        delay = "-"
        if big.any():
            t_big = times[np.argmax(big)]
            after = np.where(alarm & (times >= t_big))[0]
            delay = f"{times[after[0]] - t_big:.0f}" if len(after) else "missed"
        print(f"{prof:7s} {s:<8.1f} {p_base:<10.4f} {p_t.max():<8.4f} {int(big.sum()):<10d} {int((alarm & big).sum()):<7d} {int((alarm & quiet).sum())} of {int(quiet.sum()):<7d} {delay}")
        for r in rows:
            out.append((prof, s, *r))
        ax[k, 0].plot(times, p_t, ".-"); ax[k, 0].axhline(2 * p_base, color="r", ls="--", lw=0.8)
        ax[k, 0].set_ylabel(f"{prof} x{s:g}\nmisassign p", fontsize=8)
        ax[k, 1].plot(times, [r[2] for r in rows], ".-")
        ax[k, 1].plot(times[alarm], np.array([r[2] for r in rows])[alarm], "ro", ms=4)
        ax[k, 1].set_ylabel("fire rate (red = alarm)", fontsize=8)
    ax[-1, 0].set_xlabel("hours"); ax[-1, 1].set_xlabel("hours")
    fig.tight_layout(); fig.savefig("generator_to_detector.png", dpi=140)

    with open("generator_to_detector.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["profile", "strength", "hours", "misassign_p", "fire_rate", "tcorr", "z_fire", "z_tcorr", "alarm"])
        w.writerows(out)
    print("\nwrote generator_to_detector.csv and generator_to_detector.png")


if __name__ == "__main__":
    main()
