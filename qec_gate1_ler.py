"""
qec_gate1_ler.py  --  Gate 1, stream B: logical error rate under readout drift, done the way the reviewers asked.

Replaces qec_gate1_drift.py and qec_gate1_real_drift.py (kept for history). Differences:
  * every window reports its shot count and a 95% Wilson confidence interval (default 20000 shots/window)
  * a no-drift CONTROL series (same windows, constant readout error) shows how much LER moves by chance alone
  * drift is tested, not eyeballed: first-vs-last two-proportion z-test and a Cochran-Armitage trend test,
    for the drift series and for the control
  * one window per real snapshot, in chronological order with hours since the first snapshot, no interpolation
    across shots; the snapshot schedule is printed
  * real drift is replayed two ways: (a) IBM-reported readout error, (b) misassignment of a boundary frozen on the
    first snapshot, measured on the real IQ points
  * a fixed baseline decoder built at the healthy design point is used for every window (the decoder does not
    know about drift), instead of rebuilding the decoder from each shot's own error rate
  * physical error is held constant, so changes in LER come from readout drift only

Usage (repo root, needs drift_framework.py and real_drift_detector.py, data/ folder for the real replay):
    python qec_gate1_ler.py                       # simulated + real, d=3 and d=5
    python qec_gate1_ler.py --skip-real --shots 5000
Outputs: gate1_ler_simulated.png, gate1_ler_real.png, gate1_ler_results.csv, gate1_ler_summary.md
"""
import argparse
import csv
import datetime as dt
import os

import numpy as np
import pymatching
from scipy.stats import norm

from drift_framework import build_circuit, sample_window


def wilson(k, n, z=1.96):
    p = k / n
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return max(0.0, c - h), min(1.0, c + h)


def two_prop_p(k1, n1, k2, n2):
    p = (k1 + k2) / (n1 + n2)
    se = np.sqrt(p * (1 - p) * (1 / n1 + 1 / n2))
    return 2 * norm.sf(abs((k2 / n2 - k1 / n1) / se)) if se > 0 else 1.0


def trend_p(k, n):
    """Cochran-Armitage trend test across ordered windows (two-sided p-value, sign of the trend)."""
    k, n = np.asarray(k, float), np.asarray(n, float)
    w = np.arange(len(k), dtype=float)
    N, pbar = n.sum(), k.sum() / n.sum()
    num = np.sum(w * (k - n * pbar))
    var = pbar * (1 - pbar) * (np.sum(n * w * w) - np.sum(n * w) ** 2 / N)
    z = num / np.sqrt(var) if var > 0 else 0.0
    return 2 * norm.sf(abs(z)), float(np.sign(z))


class Runner:
    """Builds the fixed baseline decoder once and measures LER of any (readout p, physical p) window."""

    def __init__(self, d, p_design, p_phys, shots):
        self.d, self.p_phys, self.shots, self.cache = d, p_phys, shots, {}
        design = build_circuit(d, p_readout=p_design, p_phys=p_phys)
        self.matcher = pymatching.Matching.from_detector_error_model(
            design.detector_error_model(decompose_errors=True))

    def window(self, p, seed):
        key = round(max(p, 1e-4), 4)
        if key not in self.cache:
            self.cache[key] = build_circuit(self.d, p_readout=key, p_phys=self.p_phys)
        det, obs = sample_window(self.cache[key], self.shots, seed=seed)
        pred = np.asarray(self.matcher.decode_batch(det)).reshape(-1)
        k = int(np.sum(pred != np.asarray(obs).reshape(-1)))
        return k, self.shots, float(det.mean())


def series(runner, ps, seed0):
    out = []
    for i, p in enumerate(ps):
        k, n, fire = runner.window(p, seed0 + i)
        lo, hi = wilson(k, n)
        out.append(dict(p=float(p), k=k, n=n, ler=k / n, lo=lo, hi=hi, fire=fire))
    return out


def summarise(label, drift, ctrl, hrs=None):
    kd, nd = [r["k"] for r in drift], [r["n"] for r in drift]
    kc, nc = [r["k"] for r in ctrl], [r["n"] for r in ctrl]
    pd_, sd = trend_p(kd, nd)
    pc_, sc = trend_p(kc, nc)
    fl = two_prop_p(kd[0], nd[0], kd[-1], nd[-1])
    fc = two_prop_p(kc[0], nc[0], kc[-1], nc[-1])
    cpool = sum(kc) / sum(nc)
    clo, chi = wilson(sum(kc), sum(nc))
    above = sum(r["lo"] > chi for r in drift)
    if hrs is not None:  # real drift is spiky, not monotonic: report peak window instead of trend tests
        ip = int(np.argmax([r["ler"] for r in drift]))
        pk = drift[ip]
        return [f"- {label} ({nd[0]} shots per window): control pooled LER {cpool:.4f} [{clo:.4f}, {chi:.4f}]; "
                f"windows whose CI lies entirely above the control CI: {above} of {len(drift)}; "
                f"peak window at {hrs[ip]:.0f} h: LER {pk['ler']:.4f} [{pk['lo']:.4f}, {pk['hi']:.4f}] "
                f"(readout error {pk['p']:.4f}), {pk['ler'] / cpool:.1f}x the control; "
                f"control windows above the control CI: {sum(r['lo'] > chi for r in ctrl)} of {len(ctrl)}"]
    return [f"- {label}: LER first {drift[0]['ler']:.4f} [{drift[0]['lo']:.4f}, {drift[0]['hi']:.4f}] -> last "
            f"{drift[-1]['ler']:.4f} [{drift[-1]['lo']:.4f}, {drift[-1]['hi']:.4f}] "
            f"({nd[0]} shots per window); first-vs-last p = {fl:.2g}; trend p = {pd_:.2g} "
            f"({'rising' if sd > 0 else 'falling'})",
            f"  control (constant readout error): pooled LER {cpool:.4f} [{clo:.4f}, {chi:.4f}]; first-vs-last "
            f"p = {fc:.2g}; trend p = {pc_:.2g}; drift windows whose CI lies entirely above the control CI: "
            f"{above} of {len(drift)}"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--d", nargs="+", type=int, default=[3, 5])
    ap.add_argument("--shots", type=int, default=20000, help="QEC shots per window")
    ap.add_argument("--windows", type=int, default=10)
    ap.add_argument("--p0", type=float, default=0.01, help="simulated drift: starting readout error")
    ap.add_argument("--p1", type=float, default=0.025, help="simulated drift: final readout error")
    ap.add_argument("--pphys", type=float, default=0.001, help="physical error rate, held fixed")
    ap.add_argument("--data-dir", default="data")
    ap.add_argument("--skip-real", action="store_true")
    ap.add_argument("--out-dir", default=".")
    a = ap.parse_args()
    os.makedirs(a.out_dir, exist_ok=True)
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    md = [f"# Gate 1 LER under readout drift (physical error fixed at {a.pphys}, {a.shots} shots/window, "
          f"95% Wilson CIs, fixed baseline decoder)\n"]
    rows = []

    # ---------------------------------------------------------------- A. simulated drift
    md.append(f"## Simulated drift: readout error {a.p0:.1%} -> {a.p1:.1%} over {a.windows} windows\n")
    ps = np.linspace(a.p0, a.p1, a.windows)
    fig, ax = plt.subplots(1, len(a.d), figsize=(5.5 * len(a.d), 4), squeeze=False)
    for j, d in enumerate(a.d):
        r = Runner(d, a.p0, a.pphys, a.shots)
        drift = series(r, ps, 1000)
        ctrl = series(r, np.full(a.windows, a.p0), 500000)
        md += summarise(f"d={d}", drift, ctrl) + [""]
        for nm, s in (("drift", drift), ("control", ctrl)):
            for i, x in enumerate(s):
                rows.append(dict(part="simulated", d=d, series=nm, window=i, time_h="", **x))
        x = np.arange(1, a.windows + 1)
        for nm, s, c in (("drift", drift, "C0"), ("control (no drift)", ctrl, "C7")):
            ax[0, j].errorbar(x, [y["ler"] * 100 for y in s],
                              yerr=[[max(0.0, y["ler"] - y["lo"]) * 100 for y in s], [max(0.0, y["hi"] - y["ler"]) * 100 for y in s]],
                              marker="o", ms=4, capsize=2, label=nm, color=c)
        ax[0, j].set_title(f"d={d}, {a.shots} shots/window, 95% CI")
        ax[0, j].set_xlabel("window")
        ax[0, j].set_ylabel("logical error rate (%)")
        ax[0, j].legend(fontsize=8)
        ax[0, j].grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(os.path.join(a.out_dir, "gate1_ler_simulated.png"), dpi=150)
    plt.close(fig)

    # ---------------------------------------------------------------- B. real drift replay
    if not a.skip_real:
        from real_drift_detector import QUBITS, frozen_boundary_error, load_snapshots
        snaps = load_snapshots(a.data_dir)
        t = np.array([dt.datetime.fromisoformat(s[0].replace("Z", "+00:00")).timestamp() for s in snaps])
        hrs = (t - t[0]) / 3600
        gaps = np.diff(hrs)
        md.append(f"## Real IBM drift replay: {len(snaps)} snapshots, {snaps[0][0][:19]} to {snaps[-1][0][:19]} "
                  f"({hrs[-1]:.0f} h)\n")
        md.append(f"Acquisition schedule: gaps between consecutive snapshots, median {np.median(gaps):.2f} h, "
                  f"min {gaps.min():.2f} h, max {gaps.max():.2f} h; {int((gaps < 1.0).sum())} gaps shorter than 1 h. "
                  f"One QEC window per snapshot, no interpolation.\n")
        ibm = np.array([float(np.mean(s[1])) for s in snaps])
        first = snaps[0][2]
        cent = {q: (first[f"q{q}_state0"].mean(), first[f"q{q}_state1"].mean()) for q in QUBITS}
        iq = np.array([np.mean([np.mean(frozen_boundary_error(s[2][f"q{q}_state0"], s[2][f"q{q}_state1"], *cent[q]))
                                for q in QUBITS]) for s in snaps])
        md.append(f"Readout error per snapshot: IBM-reported mean {ibm.min():.4f} to {ibm.max():.4f}; "
                  f"frozen-boundary misassignment on real IQ {iq.min():.4f} to {iq.max():.4f} "
                  f"(IQ points per state per snapshot: {len(first['q0_state0'])}).\n")
        fig, ax = plt.subplots(len(a.d), 2, figsize=(11, 3.6 * len(a.d)), squeeze=False)
        for j, d in enumerate(a.d):
            for c, (nm, p) in enumerate((("IBM-reported readout error", ibm), ("frozen-boundary error on real IQ", iq))):
                base = float(np.median(p[: max(3, len(p) // 10)]))
                r = Runner(d, base, a.pphys, a.shots)
                drift = series(r, np.maximum(p, 1e-4), 2000)
                ctrl = series(r, np.full(len(p), base), 700000)
                md += summarise(f"d={d}, {nm}", drift, ctrl, hrs)
                corr = np.corrcoef(p, [x["ler"] for x in drift])[0, 1]
                md += [f"  correlation between readout error and window LER: {corr:+.2f}", ""]
                for nm2, s in (("drift", drift), ("control", ctrl)):
                    for i, x in enumerate(s):
                        rows.append(dict(part=f"real_{'ibm' if c == 0 else 'iq'}", d=d, series=nm2, window=i,
                                         time_h=f"{hrs[i]:.2f}", **x))
                for nm2, s, col in (("real drift", drift, "C0"), ("control (no drift)", ctrl, "C7")):
                    ax[j, c].errorbar(hrs, [y["ler"] * 100 for y in s],
                                      yerr=[[max(0.0, y["ler"] - y["lo"]) * 100 for y in s],
                                            [max(0.0, y["hi"] - y["ler"]) * 100 for y in s]],
                                      marker="o", ms=3, lw=0.8, capsize=1.5, label=nm2, color=col)
                ax[j, c].set_title(f"d={d}, {nm}", fontsize=9)
                ax[j, c].set_xlabel("hours since first snapshot")
                ax[j, c].set_ylabel("LER (%), 95% CI")
                ax[j, c].legend(fontsize=7)
                ax[j, c].grid(alpha=0.3)
        fig.tight_layout()
        fig.savefig(os.path.join(a.out_dir, "gate1_ler_real.png"), dpi=150)
        plt.close(fig)

    with open(os.path.join(a.out_dir, "gate1_ler_results.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["part", "d", "series", "window", "time_h", "p", "n", "k", "ler", "lo",
                                           "hi", "fire"])
        w.writeheader()
        for r in rows:
            w.writerow({k: r[k] for k in w.fieldnames})
    text = "\n".join(md) + "\n"
    open(os.path.join(a.out_dir, "gate1_ler_summary.md"), "w").write(text)
    print(text)


if __name__ == "__main__":
    main()
