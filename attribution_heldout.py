"""
attribution_heldout.py -- can the syndrome features tell READOUT drift from PHYSICAL drift once an alarm has fired?

A harder version of attribution_roc_experiment.py / attribution_stress_test.py (October), which trained and tested on the same
drift magnitudes and the same single physical-noise mix, with symmetric readout flips. Here:
  * readout errors are state-dependent, as in adaptive_boundary_v5.Hardware: the true measurement outcome is flipped with
    probability e0 (prepared-0 read as 1) or e1 (1 read as 0); the healthy baseline is already asymmetric (e0 1.0%, e1 2.0%);
  * three kinds of readout drift: "symmetric" (both errors scale), "shift" (e0 rises, e1 halves: the boundary is displaced
    towards the |0> cloud) and "decay" (only e1 rises: more |1> read as |0>);
  * six kinds of physical drift: "both" (data + gate depolarising, the October model), "data", "gate", "t1" (Pauli-twirled
    amplitude damping on the data qubits: X/Y-biased), "dephasing" (Z only on the data qubits) and "reset" (ancilla and data
    reset flips: a physical state-preparation error that acts on the measured qubit itself);
  * every condition is tuned to a target RISE IN FIRE RATE, so the two classes are matched in fire rate at each level and the
    fire rate alone cannot separate them;
  * the classifier is trained on some kinds and levels and tested on OTHER levels, and on kinds it has never seen;
  * a label-shuffle null, a feature ablation, classification accuracy, and bootstrap intervals over test windows.
Positive class = readout drift. Features (drift_framework.features): fire rate, round-to-round correlation, per-ancilla
asymmetry. Classifier: logistic regression on standardised features, as in October.

Usage (repo root): python attribution_heldout.py --out-dir results/<new folder>
"""
import argparse
import csv
import json
import os
import sys
import time

import numpy as np
import stim
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, roc_curve
from sklearn.preprocessing import StandardScaler

from drift_framework import Layout, features

E0, E1 = 0.010, 0.020          # healthy readout errors: 0 read as 1, 1 read as 0
READOUT = ("symmetric", "shift", "decay")
PHYSICAL = ("both", "data", "gate", "t1", "dephasing", "reset")
TRAIN_KINDS = ("symmetric", "shift", "both")           # the classifier never sees the other kinds
FEATS = ("fire rate", "correlation", "asymmetry")
SETS = (("fire rate only", [0]), ("correlation only", [1]), ("asymmetry only", [2]), ("correlation + asymmetry", [1, 2]), ("all three", [0, 1, 2]))


def circuit(d, p_phys, kind="both", x=1.0):
    """Physical drift of a given kind and size x (x = multiplier for both/data/gate, probability for t1/dephasing/reset)."""
    pd = p_phys * (x if kind in ("both", "data") else 1.0)
    pg = p_phys * (x if kind in ("both", "gate") else 1.0)
    c = stim.Circuit.generated("surface_code:rotated_memory_z", distance=d, rounds=d, before_round_data_depolarization=pd,
                               after_clifford_depolarization=pg, after_reset_flip_probability=(x if kind == "reset" else 0.0))
    if kind in ("t1", "dephasing") and x > 0:
        ch = [x / 4, x / 4, (2 - x - 2 * np.sqrt(1 - x)) / 4] if kind == "t1" else [0.0, 0.0, x]
        c = _extra_data_channel(c, ch)
    return c


def _extra_data_channel(circ, ch):
    out = stim.Circuit()
    for inst in circ:
        if isinstance(inst, stim.CircuitRepeatBlock):
            out.append(stim.CircuitRepeatBlock(inst.repeat_count, _extra_data_channel(inst.body_copy(), ch)))
            continue
        out.append(inst)
        if inst.name == "DEPOLARIZE1":      # the per-round data-qubit noise location
            out.append("PAULI_CHANNEL_1", [t.value for t in inst.targets_copy()], ch)
    return out


def readout_errors(kind, x):
    if kind == "symmetric":
        return E0 * x, E1 * x
    if kind == "shift":
        return E0 + x, E1 * 0.5
    if kind == "decay":
        return E0, E1 + x
    return E0, E1


RANGE = {"symmetric": (1.0, 12.0), "shift": (0.0, 0.3), "decay": (0.0, 0.5), "both": (1.0, 16.0), "data": (1.0, 80.0), "gate": (1.0, 20.0),
         "t1": (0.0, 0.5), "dephasing": (0.0, 0.4), "reset": (0.0, 0.3)}


class Source:
    """One drift condition: a circuit plus state-dependent readout errors."""

    def __init__(self, d, p_phys, kind, x, seed):
        self.kind, self.x = kind, x
        self.circ = circuit(d, p_phys, kind, x) if kind in PHYSICAL else circuit(d, p_phys)
        self.e0, self.e1 = readout_errors(kind, x)
        self.smp = self.circ.compile_sampler(seed=seed)
        self.m2d = self.circ.compile_m2d_converter()
        self.rng = np.random.default_rng(seed + 1)

    def window(self, n):
        out = self.smp.sample(n)
        u = self.rng.random(out.shape)
        flip = np.where(out, u < self.e1, u < self.e0)
        return self.m2d.convert(measurements=out ^ flip, separate_observables=False)


def tune(d, p_phys, kind, target, shots, iters):
    """Bisection on the drift size so that the mean fire rate equals `target`."""
    lo, hi = RANGE[kind]
    f_hi = Source(d, p_phys, kind, hi, 7).window(shots).mean()
    if f_hi < target:
        raise RuntimeError(f"{kind}: range too small for fire rate {target:.4f} (max {f_hi:.4f})")
    for _ in range(iters):
        mid = (lo + hi) / 2
        if Source(d, p_phys, kind, mid, 7).window(shots).mean() < target:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def collect(d, p_phys, lay, ref, sizes, levels, win, n_win, seed0):
    """{(kind, level): feature array (n_win, 3)}"""
    X = {}
    for ki, kind in enumerate(READOUT + PHYSICAL):
        for li, lev in enumerate(levels):
            src = Source(d, p_phys, kind, sizes[(kind, lev)], seed0 + 1000 * ki + 10 * li)
            rows = []
            for _ in range(n_win):
                f = features(src.window(win), lay, ref)
                rows.append([f["fire_rate"], f["tcorr"], f["asym"]])
            X[(kind, lev)] = np.array(rows)
    return X


def stack(X, kinds, levels):
    xs, ys = [], []
    for (k, l), v in X.items():
        if k in kinds and l in levels:
            xs.append(v)
            ys.append(np.full(len(v), int(k in READOUT)))
    return np.concatenate(xs), np.concatenate(ys)


def fit(Xa, ya, cols):
    sc = StandardScaler().fit(Xa[:, cols])
    lr = LogisticRegression(max_iter=1000).fit(sc.transform(Xa[:, cols]), ya)
    return lambda X: lr.predict_proba(sc.transform(X[:, cols]))[:, 1]


def auc_ci(y, s, rng, boot):
    a = roc_auc_score(y, s)
    i1, i0 = np.where(y == 1)[0], np.where(y == 0)[0]
    bs = []
    for _ in range(boot):
        ix = np.r_[rng.choice(i1, len(i1)), rng.choice(i0, len(i0))]
        bs.append(roc_auc_score(y[ix], s[ix]))
    return a, np.percentile(bs, 2.5), np.percentile(bs, 97.5)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default=".")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--d", type=int, default=5)
    ap.add_argument("--pphys", type=float, default=0.001)
    ap.add_argument("--windows", nargs="+", type=int, default=[250, 1500])
    ap.add_argument("--train-levels", nargs="+", type=float, default=[0.4, 1.0, 2.0], help="fire-rate rise used for training")
    ap.add_argument("--test-levels", nargs="+", type=float, default=[0.3, 0.6, 1.5, 2.5], help="held-out fire-rate rise used for testing")
    ap.add_argument("--n-win", type=int, default=150, help="windows per condition, for each of train and test")
    ap.add_argument("--tune-shots", type=int, default=60000)
    ap.add_argument("--tune-iters", type=int, default=13)
    ap.add_argument("--boot", type=int, default=1000)
    ap.add_argument("--null", type=int, default=200, help="label shuffles for the null")
    a = ap.parse_args()
    os.makedirs(a.out_dir, exist_ok=True)
    outs = [os.path.join(a.out_dir, f) for f in ("attribution_heldout.md", "attribution_heldout.csv", "attribution_heldout_config.json",
                                                 "attribution_heldout_roc.png")]
    if any(os.path.exists(f) for f in outs) and not a.force:
        sys.exit(f"outputs exist in {a.out_dir}; use a new --out-dir or --force")
    import sklearn
    json.dump(dict(args=vars(a), cmd=" ".join(sys.argv), time=time.strftime("%Y-%m-%d %H:%M:%S"), numpy=np.__version__, stim=stim.__version__,
                   sklearn=sklearn.__version__), open(outs[2], "w"), indent=1)
    rng = np.random.default_rng(0)
    d, pp = a.d, a.pphys
    healthy = Source(d, pp, "healthy", 0.0, 1)
    lay = Layout(healthy.circ)
    ref = features(healthy.window(200000), lay, np.ones(lay.n_anc))["per_anc"]
    f0 = healthy.window(200000).mean()
    levels = sorted(set(a.train_levels) | set(a.test_levels))
    sizes = {}
    for kind in READOUT + PHYSICAL:
        for lev in levels:
            sizes[(kind, lev)] = tune(d, pp, kind, f0 * (1 + lev), a.tune_shots, a.tune_iters)
        print(f"  tuned {kind}: " + ", ".join(f"+{100*l:.0f}% -> {sizes[(kind, l)]:.4g}" for l in levels), flush=True)

    L = ["# Attribution with held-out drift sizes and kinds: readout drift (positive) vs physical drift", "",
         f"d={d}, physical error {pp}, healthy readout errors e0={E0}, e1={E1} (state-dependent), healthy fire rate {f0:.5f}. "
         f"Each condition is tuned to a fire-rate rise; training levels {', '.join(f'+{100*l:.0f}%' for l in a.train_levels)}, held-out test levels "
         f"{', '.join(f'+{100*l:.0f}%' for l in a.test_levels)}. Trained on kinds {', '.join(TRAIN_KINDS)} only; {a.n_win} windows per condition. "
         f"AUC intervals: 95% bootstrap over test windows ({a.boot} resamples). The v5 alarm needs a +30% rise, so +30% is the smallest drift it flags.", "",
         "Drift size that gives each fire-rate rise (multiplier for symmetric/both/data/gate, added probability otherwise):", "",
         "| kind | " + " | ".join(f"+{100*l:.0f}%" for l in levels) + " |", "|---|" + "---|" * len(levels)]
    for kind in READOUT + PHYSICAL:
        L.append(f"| {kind} | " + " | ".join(f"{sizes[(kind, l)]:.4g}" for l in levels) + " |")
    L.append("")
    rows = []
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, len(a.windows), figsize=(5.2 * len(a.windows), 4.6), sharey=True)
    axes = np.atleast_1d(axes)
    for wi, win in enumerate(a.windows):
        Xtr = collect(d, pp, lay, ref, sizes, a.train_levels, win, a.n_win, 10_000 + win)
        Xte = collect(d, pp, lay, ref, sizes, a.test_levels, win, a.n_win, 5_000_000 + win)
        Xa, ya = stack(Xtr, TRAIN_KINDS, a.train_levels)
        L.append(f"## Window = {win} shots ({win * d} syndrome rounds)")
        L.append("")
        # ---- 1. feature ablation on held-out conditions pooled, with and without the reset-error kind
        models = {name: fit(Xa, ya, cols) for name, cols in SETS}
        for pool_name, phys in (("all held-out conditions pooled", PHYSICAL),
                                ("held-out conditions pooled, WITHOUT the reset-error kind", tuple(p for p in PHYSICAL if p != "reset"))):
            Xb, yb = stack(Xte, READOUT + phys, a.test_levels)
            L.append(f"### Feature ablation, {pool_name} ({int(yb.sum())} readout and {int((1-yb).sum())} physical test windows)")
            L.append("")
            L.append("| features | AUC [95% CI] | accuracy at 0.5 | chance band: AUC with shuffled TEST labels (2.5th-97.5th pct) | "
                     "AUC after training on shuffled labels: median (2.5th-97.5th pct) |")
            L.append("|---|---|---|---|---|")
            for name, cols in SETS:
                s = models[name](Xb)
                auc, lo, hi = auc_ci(yb, s, rng, a.boot)
                acc = float(np.mean((s > 0.5) == yb))
                ch = np.percentile([roc_auc_score(rng.permutation(yb), s) for _ in range(a.boot)], [2.5, 97.5])
                nq = np.percentile([roc_auc_score(yb, fit(Xa, rng.permutation(ya), cols)(Xb)) for _ in range(a.null)], [2.5, 50, 97.5])
                L.append(f"| {name} | {auc:.3f} [{lo:.3f}, {hi:.3f}] | {acc:.3f} | {ch[0]:.3f}-{ch[1]:.3f} | {nq[1]:.3f} ({nq[0]:.3f}-{nq[2]:.3f}) |")
                rows.append(dict(window=win, table="ablation", features=name, readout="all", physical="all" if "reset" in phys else "all but reset",
                                 level="all held-out", auc=auc, ci_lo=lo, ci_hi=hi, accuracy=acc, chance_lo=ch[0], chance_hi=ch[1],
                                 null_median=nq[1], null_lo=nq[0], null_hi=nq[2], n_pos=int(yb.sum()), n_neg=int((1 - yb).sum())))
                if name == "all three":
                    fpr, tpr, _ = roc_curve(yb, s)
                    axes[wi].plot(fpr, tpr, lw=2, label=("all kinds" if "reset" in phys else "all but reset") + f", all three (AUC {auc:.2f})")
            L.append("")
        L.append("Two nulls. Shuffling the TEST labels gives the band a classifier with no information reaches on a test set of this size. "
                 "Training on shuffled labels shows what the fitted model does without label information; with one or two features it still "
                 "outputs a monotone function of a real feature, so it lands on either the real AUC or one minus it, and the median is the informative number.")
        L.append("")
        m = models["all three"]
        # ---- 2. readout kind x physical kind
        L.append("### AUC by kind, all three features, held-out levels pooled (kinds marked * were never seen in training)")
        L.append("")
        star = lambda k: k + ("" if k in TRAIN_KINDS else " *")
        L.append("| physical \\ readout | " + " | ".join(star(r) for r in READOUT) + " |")
        L.append("|---|" + "---|" * len(READOUT))
        for p in PHYSICAL:
            cells = []
            for r in READOUT:
                X2, y2 = stack(Xte, (r, p), a.test_levels)
                s = m(X2)
                auc, lo, hi = auc_ci(y2, s, rng, a.boot)
                cells.append(f"{auc:.3f} [{lo:.3f}, {hi:.3f}]")
                rows.append(dict(window=win, table="by kind", features="all three", readout=r, physical=p, level="all held-out", auc=auc, ci_lo=lo,
                                 ci_hi=hi, accuracy=float(np.mean((s > 0.5) == y2)), n_pos=int(y2.sum()), n_neg=int((1 - y2).sum())))
            L.append(f"| {star(p)} | " + " | ".join(cells) + " |")
            X2, y2 = stack(Xte, READOUT + (p,), a.test_levels)
            fpr, tpr, _ = roc_curve(y2, m(X2))
            axes[wi].plot(fpr, tpr, lw=1, label=f"vs {p} (AUC {roc_auc_score(y2, m(X2)):.2f})")
        L.append("")
        # ---- 3. by held-out level
        L.append("### AUC by held-out level, all three features, all kinds pooled")
        L.append("")
        L.append("| fire-rate rise | AUC [95% CI] | accuracy at 0.5 |")
        L.append("|---|---|---|")
        for lev in a.test_levels:
            X2, y2 = stack(Xte, READOUT + PHYSICAL, (lev,))
            s = m(X2)
            auc, lo, hi = auc_ci(y2, s, rng, a.boot)
            L.append(f"| +{100*lev:.0f}% | {auc:.3f} [{lo:.3f}, {hi:.3f}] | {np.mean((s > 0.5) == y2):.3f} |")
            rows.append(dict(window=win, table="by level", features="all three", readout="all", physical="all", level=f"+{100*lev:.0f}%", auc=auc,
                             ci_lo=lo, ci_hi=hi, accuracy=float(np.mean((s > 0.5) == y2)), n_pos=int(y2.sum()), n_neg=int((1 - y2).sum())))
        L.append("")
        # ---- 4. feature means, to show what the classifier uses
        L.append("### Mean feature values on the held-out test windows (correlation and asymmetry as multiples of the healthy value)")
        L.append("")
        h = np.array([[f["fire_rate"], f["tcorr"], f["asym"]] for f in (features(healthy.window(win), lay, ref) for _ in range(60))]).mean(0)
        L.append("| kind | fire-rate rise | correlation / healthy | asymmetry / healthy |")
        L.append("|---|---|---|---|")
        for k in READOUT + PHYSICAL:
            v = np.concatenate([Xte[(k, l)] for l in a.test_levels]).mean(0)
            L.append(f"| {k} | {100*(v[0]/h[0]-1):+.0f}% | {v[1]/h[1]:.2f} | {v[2]/h[2]:.2f} |")
        L.append("")
        axes[wi].plot([0, 1], [0, 1], "k--", lw=0.8)
        axes[wi].set_title(f"{win}-shot windows, held-out levels")
        axes[wi].set_xlabel("false positive rate")
        axes[wi].legend(fontsize=7, loc="lower right")
        print(f"  window {win} done", flush=True)
    axes[0].set_ylabel("true positive rate (positive = readout drift)")
    fig.tight_layout()
    fig.savefig(outs[3], dpi=150)
    open(outs[0], "w").write("\n".join(L) + "\n")
    keys = []
    for r in rows:
        keys += [k for k in r if k not in keys]
    with open(outs[1], "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=keys)
        w.writeheader(); w.writerows(rows)
    print("\n".join(L))
    print(f"\nwrote {outs[0]}")


if __name__ == "__main__":
    main()
