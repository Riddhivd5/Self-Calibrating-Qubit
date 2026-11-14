"""closed_loop_report.py -- the closed-loop LER table and figure, built from ler_comparison.py outputs.

Usage (repo root): python closed_loop_report.py results/closed_loop
Expects sub-folders controlled/, fitted/ and real/ (and, if present, combined/), each holding ler_summary.md and ler_windows.csv from ler_comparison.py.
Writes closed_loop_table.md, closed_loop_figure.png and closed_loop_figure.pdf into the folder given.
Table numbers are copied from the ler_summary.md files (nothing is recomputed); the figure plots ler_windows.csv with no smoothing:
(a) LER per window pooled over runs; (b) cumulative logical errors of each arm minus the oracle arm, summed over runs.
"""
import csv
import os
import re
import sys

import numpy as np

ARMS = [("frozen", "Frozen"), ("periodic_24h", "Periodic recalibration, 24 h"), ("oracle", "Oracle (labelled, every window)"),
        ("em_pi_fast", "Adaptive, same window"), ("em_pi_fast_lag", "Adaptive, online"), ("gated_v5_lag", "Gated by alarm, online")]
# fixed colour per arm (validated categorical order), plus a line style so identity never rests on colour alone
STYLE = {"frozen": ("#2a78d6", "-"), "periodic_24h": ("#eb6834", (0, (5, 2))), "oracle": ("#1baf7a", (0, (1, 1.2))),
         "em_pi_fast": ("#eda100", (0, (3, 1, 1, 1))), "em_pi_fast_lag": ("#e87ba4", "-")}
NAMES = {"step_q1": "Step, 1 sigma (controlled)", "slow_q1": "Slow ramp to 1 sigma (controlled)",
         "physical_quiet_q1": "Physical error ramped x3, no readout drift", "step_physical_q1": "Step, 1 sigma, plus physical error ramped x3", "refit_q0": "Fitted profile q0",
         "refit_q1": "Fitted profile q1", "refit_q2": "Fitted profile q2", "real_q0": "Real replay q0", "real_q1": "Real replay q1",
         "real_q2": "Real replay q2"}


def parse(path):
    out = {}
    for blk in open(path).read().split("### ")[1:]:
        name = blk.split("\n")[0].strip()
        arms = {}
        for l in blk.split("\n"):
            if l.startswith("| ") and not l.startswith("| arm") and not l.startswith("|---"):
                c = [x.strip() for x in l.strip("|").split("|")]
                arms[c[0]] = dict(ler=c[1], resample=c[2], shots=c[3], rec=c[5])
        head = re.search(r"(\d+) run\(s\); (\d+) windows per run, (\d+) shots per window", blk)
        gap = re.search(r"frozen-vs-oracle LER gap: ([\d.]+) percentage points(.*)", blk)
        out[name] = dict(arms=arms, runs=int(head.group(1)), windows=int(head.group(2)), shots=int(head.group(3)),
                         gap=float(gap.group(1)), resolvable="not distinguishable" not in gap.group(2))
    return out


def pct(cell):
    """'0.00888 [0.00869, 0.00908]' -> '0.888 [0.869, 0.908]' (percent)"""
    v = [100 * float(x) for x in re.findall(r"[\d.]+", cell)]
    return f"{v[0]:.3f} [{v[1]:.3f}, {v[2]:.3f}]"


def series(path, scenario, arm):
    t, k, n = {}, {}, {}
    for r in csv.DictReader(open(path)):
        if r["scenario"] == scenario and r["arm"] == arm:
            s = int(r["step"])
            t[s] = float(r["t"])
            k[s] = k.get(s, 0) + int(r["errors"])
            n[s] = n.get(s, 0) + int(r["shots"])
    idx = sorted(t)
    return np.array([t[i] for i in idx]), np.array([k[i] for i in idx]), np.array([n[i] for i in idx])


def main():
    root = sys.argv[1] if len(sys.argv) > 1 else "results/closed_loop"
    S = {}
    for sub in ("controlled", "combined", "fitted", "real"):
        p = os.path.join(root, sub, "ler_summary.md")
        if os.path.exists(p):
            S.update(parse(p))
    L = ["# Closed-loop logical error rate: frozen, periodically recalibrated, oracle and adaptive decision boundaries", "",
         "d = 5 rotated surface code, physical error 0.001, fixed PyMatching decoder built at the calibration-time readout error. "
         "LER in percent, pooled over runs, with the 95% interval from resampling (runs for simulated drift; window blocks for the real "
         "replay, which is one 15.6-day trajectory re-sampled, so its interval covers sampling noise only). Recovery = share of the "
         "frozen-to-oracle LER gap that an arm removes, with a 95% bootstrap interval over runs (for the real replay the runs are "
         "re-samplings of the same trajectory, so that interval is narrow and covers sampling noise only); it is not reported when the gap "
         "is not distinguishable from zero. 'Same window' scores a boundary on the window it was just tuned on (offline re-assignment); "
         "'online' scores each window at the boundary from before that window's data. Source: ler_summary.md in controlled/, fitted/, real/.", "",
         "| scenario | runs x windows x shots | frozen | periodic 24 h | oracle | adaptive, same window | adaptive, online | gated, online | "
         "recovery: same window | recovery: online | recovery: gated online | recovery: periodic 24 h |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for sc, nice in NAMES.items():
        if sc not in S:
            continue
        s = S[sc]
        a = s["arms"]
        r = lambda m: a[m]["rec"] if s["resolvable"] else "-"
        cell = lambda m: re.sub(r"^([\d.]+) .*", lambda q: f"{100*float(q.group(1)):.3f}", a[m]["ler"]) + " " + \
            "[" + ", ".join(f"{100*float(x):.3f}" for x in re.findall(r"[\d.]+", a[m]["resample"])) + "]"
        L.append(f"| {nice} | {s['runs']} x {s['windows']} x {s['shots']} | " + " | ".join(cell(m) for m in
                 ("frozen", "periodic_24h", "oracle", "em_pi_fast", "em_pi_fast_lag", "gated_v5_lag"))
                 + f" | {r('em_pi_fast')} | {r('em_pi_fast_lag')} | {r('gated_v5_lag')} | {r('periodic_24h')} |")
    L.append("")
    open(os.path.join(root, "closed_loop_table.md"), "w").write("\n".join(L) + "\n")
    print("\n".join(L))

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.size": 8, "axes.spines.top": False, "axes.spines.right": False, "axes.linewidth": 0.6,
                         "pdf.fonttype": 42, "font.family": "DejaVu Sans"})
    fig, ax = plt.subplots(1, 2, figsize=(7.16, 2.55))
    label = dict(ARMS)
    # (a) simulated step: LER over time, pooled over runs at each window
    path, sc = os.path.join(root, "controlled", "ler_windows.csv"), "step_q1"
    if sc in S and os.path.exists(path):
        for m in ("frozen", "periodic_24h", "oracle", "em_pi_fast", "em_pi_fast_lag"):
            t, k, n = series(path, sc, m)
            col, ls = STYLE[m]
            ax[0].plot(t, 100 * np.maximum(k, 0.5) / n, color=col, ls=ls, lw=1.3, label=label[m])
        ax[0].set_yscale("log")
        ax[0].set_ylabel("Logical error rate (%), log scale")
        ax[0].set_title(f"(a) Simulated 1 sigma step at 56 h, {S[sc]['runs']} runs pooled", fontsize=8, loc="left")
        ax[0].legend(fontsize=6.5, frameon=False, loc="center right", bbox_to_anchor=(1.0, 0.56), handlelength=2.6)
        ax[0].text(0.99, 0.02, f"{S[sc]['runs'] * S[sc]['shots']:,} QEC shots per point", transform=ax[0].transAxes, ha="right", va="bottom",
                   fontsize=6.5, color="#5a5952")
    # (b) real replay: cumulative logical errors in excess of the oracle arm (the per-window traces overlap too closely to read)
    path, sc = os.path.join(root, "real", "ler_windows.csv"), "real_q1"
    if sc in S and os.path.exists(path):
        t, ko, n = series(path, sc, "oracle")
        for m in ("frozen", "periodic_24h", "em_pi_fast", "em_pi_fast_lag"):
            _, k, _ = series(path, sc, m)
            col, ls = STYLE[m]
            y = np.cumsum(k - ko)
            ax[1].plot(t, y, color=col, ls=ls, lw=1.3, label=label[m])
            ax[1].annotate(f"{y[-1]:+,.0f}", (t[-1], y[-1]), xytext=(3, 5 if m == "em_pi_fast" else 0), textcoords="offset points", fontsize=6.5,
                           va="center", color="#33322e")
        ax[1].axhline(0, color="#1baf7a", ls=(0, (1, 1.2)), lw=1.0)
        ax[1].annotate("Oracle = 0", (t[-1], 0), xytext=(3, -6), textcoords="offset points", fontsize=6.5, va="center", color="#33322e")
        ax[1].set_ylabel("Cumulative logical errors above oracle")
        ax[1].set_title(f"(b) Real q1 drift replayed ({int(n.sum()) / 1e6:.2f} M shots per arm)", fontsize=8, loc="left")
        ax[1].legend(fontsize=6.5, frameon=False, loc="upper left", handlelength=2.6)
        ax[1].set_xlim(t[0], t[-1] * 1.13)
        ax[1].set_ylim(bottom=-450)
    for axi in ax:
        axi.set_xlabel("Time since calibration (h)")
        axi.grid(axis="y", color="#d9d8d2", lw=0.4)
        axi.tick_params(width=0.6, length=3)
    fig.tight_layout(pad=0.4, w_pad=1.2)
    for ext in ("png", "pdf"):
        fig.savefig(os.path.join(root, f"closed_loop_figure.{ext}"), dpi=300)
    print(f"wrote closed_loop_table.md and closed_loop_figure.png/.pdf in {root}")


if __name__ == "__main__":
    main()
