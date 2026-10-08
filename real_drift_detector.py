"""
real_drift_detector.py

Gate 2 check: does the syndrome-based detector react to REAL IBM readout drift,
and does it react when IBM's reported readout errors change?

Pipeline, per snapshot in data/:
    real IQ points --(frozen 0/1 boundary from first snapshot)--> readout error p
    p --> Stim surface code (drift_framework.build_circuit) --> detection events
    detection events --> fire rate, round-to-round correlation (drift_framework.features)

Usage (from the repo root):
    python real_drift_detector.py                 # defaults: d=5, 4000 shots per snapshot
    python real_drift_detector.py --d 3 --shots 2000

Outputs:
    real_drift_detector.csv   one row per snapshot
    real_drift_detector.png   fire rate and correlation over time, recalibration times marked

Requires: stim, numpy, matplotlib   (drift_framework.py must be in the same folder)
"""
import argparse
import glob
import json
import os

import numpy as np

from drift_framework import Layout, build_circuit, features, sample_window

QUBITS = (0, 1, 2)
N_BASE = 10     # snapshots 1..N_BASE define the healthy readout-error level
P_PHYS = 0.001  # physical error rate, held fixed: all drift here is readout drift


def load_snapshots(data_dir):
    snaps = []
    for f in sorted(glob.glob(os.path.join(data_dir, "iq_*.npz"))):
        mf = f.replace("iq_", "metadata_").replace(".npz", ".json")
        if not os.path.exists(mf):
            continue
        meta = json.load(open(mf))
        cal = meta["calibration"]
        ibm_ro = tuple(cal[f"q{q}"]["readout_error"] for q in QUBITS)
        snaps.append((meta["timestamp_utc"], ibm_ro, np.load(f)))
    snaps.sort(key=lambda s: s[0])
    return snaps


def frozen_boundary_error(iq0, iq1, c0, c1):
    """Misassignment of a boundary frozen at (c0, c1): perpendicular bisector of the two centroids."""
    w, mid = c1 - c0, (c0 + c1) / 2
    cls = lambda z: (((z - mid) * np.conj(w)).real > 0)
    e0 = cls(iq0).mean()           # prepared 0, read 1
    e1 = 1.0 - cls(iq1).mean()     # prepared 1, read 0
    return e0, e1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", default="data")
    ap.add_argument("--d", type=int, default=5)
    ap.add_argument("--shots", type=int, default=4000)
    ap.add_argument("--zthr", type=float, default=3.0, help="alarm threshold in baseline standard deviations")
    args = ap.parse_args()

    snaps = load_snapshots(args.data_dir)
    print(f"{len(snaps)} snapshots from {snaps[0][0]} to {snaps[-1][0]}")

    # 1) frozen boundary per qubit, calibrated on the first snapshot
    first = snaps[0][2]
    cent = {q: (first[f"q{q}_state0"].mean(), first[f"q{q}_state1"].mean()) for q in QUBITS}

    # 2) real readout error per snapshot (mean over q0..q2 of the two-state average)
    p_ro, recal = [], []
    prev_cal = None
    for ts, cal, d in snaps:  # cal = IBM-reported readout errors (q0,q1,q2) at that snapshot
        errs = []
        for q in QUBITS:
            e0, e1 = frozen_boundary_error(d[f"q{q}_state0"], d[f"q{q}_state1"], *cent[q])
            errs.append((e0 + e1) / 2)
        p_ro.append(max(float(np.mean(errs)), 1e-4))
        recal.append(prev_cal is not None and cal != prev_cal)
        prev_cal = cal
    p_ro, recal = np.array(p_ro), np.array(recal)

    # 3) healthy baseline: many windows at the starting error, to get a noise level
    p_base = float(np.median(p_ro[1:N_BASE + 1]))
    print(f"healthy baseline readout error (median of snapshots 1..{N_BASE}): {p_base:.4f}")
    c_base = build_circuit(args.d, p_readout=p_base, p_phys=P_PHYS)
    lay = Layout(c_base)
    ref = features(sample_window(c_base, 200000, seed=1)[0], lay, np.ones(lay.n_anc))["per_anc"]
    base = [features(sample_window(c_base, args.shots, seed=100 + k)[0], lay, ref) for k in range(30)]
    bf, bt = np.array([b["fire_rate"] for b in base]), np.array([b["tcorr"] for b in base])

    # 4) replay every real snapshot
    rows = []
    for i, ((ts, cal, _), p) in enumerate(zip(snaps, p_ro)):
        c = build_circuit(args.d, p_readout=p, p_phys=P_PHYS)
        f = features(sample_window(c, args.shots, seed=5000 + i)[0], lay, ref)
        rows.append((ts, cal, p, f["fire_rate"], f["tcorr"], f["asym"],
                     (f["fire_rate"] - bf.mean()) / bf.std(), (f["tcorr"] - bt.mean()) / bt.std()))

    import csv
    with open("real_drift_detector.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["timestamp_utc", "ibm_readout_error_q0_q1_q2", "readout_error", "fire_rate", "tcorr", "asym",
                    "z_fire", "z_tcorr", "recal_event"])
        for r, rc in zip(rows, recal):
            w.writerow([*r, int(rc)])

    z_fire = np.array([r[6] for r in rows])
    z_tc = np.array([r[7] for r in rows])
    alarm = (z_fire > args.zthr) | (z_tc > args.zthr)

    print(f"\nbaseline noise: fire rate {bf.mean():.4f} +/- {bf.std():.4f}, tcorr {bt.mean():.5f} +/- {bt.std():.5f}")
    print(f"snapshots with alarm (z > {args.zthr}): {alarm.sum()} of {len(alarm)}")
    print(f"snapshots where IBM-reported readout error changed: {recal.sum()}")
    if recal.any():
        print(f"  mean |change in readout error| when IBM numbers changed : "
              f"{np.mean(np.abs(np.diff(p_ro, prepend=p_ro[0]))[recal]):.4f}")
        print(f"  mean |change in readout error| when they did not      : "
              f"{np.mean(np.abs(np.diff(p_ro, prepend=p_ro[0]))[~recal]):.4f}")
        print(f"  alarms when IBM numbers changed: {(alarm & recal).sum()} of {recal.sum()}")
    big = p_ro > 2 * p_base
    print(f"\nbig drift events (readout error > 2x healthy baseline): {big.sum()}  ->  alarms on them: {(alarm & big).sum()} of {big.sum()}")
    print("\nlargest readout-error snapshots:")
    for i in np.argsort(p_ro)[::-1][:5]:
        print(f"  {rows[i][0][:19]}  p={p_ro[i]:.4f}  z_fire={z_fire[i]:+.1f}  z_tcorr={z_tc[i]:+.1f}  alarm={bool(alarm[i])}")

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    t = np.arange(len(rows))
    fig, ax = plt.subplots(3, 1, figsize=(10, 7), sharex=True)
    for a, y, lab in ((ax[0], p_ro, "real readout error (frozen boundary)"),
                      (ax[1], [r[3] for r in rows], "detector fire rate"),
                      (ax[2], [r[4] for r in rows], "round-to-round correlation")):
        a.plot(t, y, ".-")
        a.set_ylabel(lab, fontsize=8)
        for k in np.where(recal)[0]:
            a.axvline(k, color="r", alpha=0.15)
    ax[2].set_xlabel("snapshot index (red lines = IBM-reported readout error changed)")
    fig.tight_layout()
    fig.savefig("real_drift_detector.png", dpi=150)
    print("\nwrote real_drift_detector.csv and real_drift_detector.png")


if __name__ == "__main__":
    main()
