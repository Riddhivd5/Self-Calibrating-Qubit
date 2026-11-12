"""Checks on the real IBM snapshots that need no QEC simulation (run from the repo root; needs data/ and real_drift_detector.py).

1. Acquisition timing: snapshot timestamp (taken when collect_data.py starts, before the job is queued) against
   calibration.last_update (job.properties(), i.e. the backend calibration at the time the job ran).
2. Whether readout-error events and centroid jumps line up with IBM calibration changes (per-qubit reported readout_error
   changing between consecutive snapshots is used as the recalibration marker; last_update changes far more often).
3. Whether each qubit's flagged events exceed shot noise (2000 labelled IQ points per snapshot), and how the event count
   depends on the event threshold.

Usage: python real_event_checks.py [--data-dir data] [--out-dir results/<new folder>]
"""
import argparse
import datetime as dt
import json
import os
import sys

import numpy as np
from scipy import stats

sys.path.insert(0, ".")
from real_drift_detector import QUBITS, frozen_boundary_error, load_snapshots

N_BASE = 10  # same baseline snapshots as real_per_qubit.py (snapshots 1..10; boundary frozen at snapshot 0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", default="data")
    ap.add_argument("--out-dir", default=".")
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    os.makedirs(a.out_dir, exist_ok=True)
    out_path = os.path.join(a.out_dir, "real_event_checks.txt")
    csv_path = os.path.join(a.out_dir, "real_event_checks.csv")
    if (os.path.exists(out_path) or os.path.exists(csv_path)) and not a.force:
        sys.exit(f"{out_path} or {csv_path} exists; use a new --out-dir or --force")
    lines = []

    def P(s=""):
        print(s)
        lines.append(s)

    snaps = load_snapshots(a.data_dir)
    n = len(snaps)
    metas = [json.load(open(os.path.join(a.data_dir, "metadata_" + s[0][:19].replace("T", "_").replace(":", "-") + ".json")))
             for s in snaps]
    assert all(m["timestamp_utc"] == s[0] for m, s in zip(metas, snaps))
    T = np.array([dt.datetime.fromisoformat(s[0]).timestamp() for s in snaps])
    L = np.array([dt.datetime.fromisoformat(m["calibration"]["last_update"]).timestamp() for m in metas])
    hrs = (T - T[0]) / 3600
    gaps = np.diff(T) / 3600

    P(f"# Real-snapshot checks ({n} snapshots, backend {metas[0]['backend']}, {metas[0]['shots_per_circuit']} shots per state per qubit)")
    P()
    P("## 1. Acquisition timing")
    P(f"- First {snaps[0][0][:19]} UTC, last {snaps[-1][0][:19]} UTC, span {hrs[-1]:.1f} h ({hrs[-1]/24:.1f} d).")
    P(f"- Gaps between consecutive snapshot timestamps: median {np.median(gaps):.2f} h, min {gaps.min():.2f} h, max {gaps.max():.2f} h; "
      f"{(gaps < 1).sum()} gaps under 1 h, {(gaps > 6).sum()} over 6 h.")
    for lo, hi in ((0, 1), (1, 2), (2, 3), (3, 5), (5, 9), (9, 99)):
        P(f"  - gap {lo}-{hi if hi < 99 else '...'} h: {((gaps >= lo) & (gaps < hi)).sum()}")
    lag = (T - L) / 3600
    tz = sorted({m["calibration"]["last_update"][-6:] for m in metas})
    P(f"- last_update carries UTC offset(s) {tz}; parsed with the offset, snapshot minus last_update is median {np.median(lag):.2f} h "
      f"(5th-95th percentile {np.percentile(lag, 5):.2f} to {np.percentile(lag, 95):.2f} h).")
    neg = np.where(lag < 0)[0]
    P(f"- last_update is LATER than the snapshot timestamp in {len(neg)} snapshots (by {', '.join(f'{-lag[i]:.2f}' for i in neg)} h).")
    P("  The snapshot timestamp is taken when the collection script starts; last_update comes from job.properties() and so is")
    P("  no later than the moment the job ran. These jobs therefore ran at least that long after their timestamp (queueing).")
    for i in neg:
        nxt = f"{gaps[i]:.2f} h" if i < n - 1 else "-"
        P(f"  - snapshot {i} ({snaps[i][0][:16]}): ran >= {-lag[i]:.2f} h late; gap to the next snapshot timestamp {nxt}")
    Tc = np.maximum(T, L)  # lower bound on the true acquisition time
    order_ok = bool(np.all(np.diff(Tc) > 0))
    gc = np.diff(Tc) / 3600
    P(f"- Using max(timestamp, last_update) as a lower bound on the acquisition time: order preserved {order_ok}; gaps median "
      f"{np.median(gc):.2f} h, min {gc.min():.2f} h, max {gc.max():.2f} h; span {(Tc[-1]-Tc[0])/3600:.1f} h.")
    lu_ch = np.r_[False, np.diff(L) != 0]
    P(f"- last_update changes at {lu_ch.sum()} of {n-1} steps, so it cannot mark recalibrations of a given qubit's readout.")

    P()
    P("## 2. Do events and centroid jumps line up with IBM calibration changes?")
    rows = []
    for qi, q in enumerate(QUBITS):
        ibm = np.array([s[1][qi] for s in snaps])
        ro_ch = np.r_[False, np.diff(ibm) != 0]
        z0 = [s[2][f"q{q}_state0"] for s in snaps]
        z1 = [s[2][f"q{q}_state1"] for s in snaps]
        c0 = np.array([z.mean() for z in z0])
        c1 = np.array([z.mean() for z in z1])

        def sig(z):
            r = z - z.mean()
            return np.sqrt(0.5 * np.mean(r.real ** 2 + r.imag ** 2))
        s0 = 0.5 * (sig(z0[0]) + sig(z1[0]))
        e = np.array([frozen_boundary_error(z0[i], z1[i], c0[0], c1[0]) for i in range(n)])  # frozen at snapshot 0
        eo = np.array([frozen_boundary_error(z0[i], z1[i], c0[i], c1[i]) for i in range(n)])  # own centroids (re-centred)
        k = np.rint(e.sum(1) * 1000).astype(int)   # misassigned points out of 2000
        ko = np.rint(eo.sum(1) * 1000).astype(int)
        p = np.maximum(k / 2000, 1e-4)
        pb = float(np.median(p[1:N_BASE + 1]))
        base = max(pb, 0.005)
        scored = np.arange(n) > N_BASE
        ev = (p > 2 * base) & scored
        jump = np.r_[0, np.maximum(abs(np.diff(c0)), abs(np.diff(c1))) / s0]  # centroid move since previous snapshot, in sigma
        shift = np.maximum(abs(c0 - c0[0]), abs(c1 - c1[0])) / s0
        sep = abs(c1 - c0)
        gain = sep / sep[0]
        rot = np.degrees(np.angle((c1 - c0) / (c1[0] - c0[0])))
        # shot-to-shot standard error of a centroid difference between two snapshots, in sigma: sqrt(2/1000)
        P(f"### q{q}")
        P(f"- IBM-reported readout_error changes at {ro_ch.sum()} of {n-1} steps (used as this qubit's recalibration marker).")
        on = [i for i in np.where(ev)[0] if not ev[i - 1]]
        P(f"- Events (frozen-boundary error > {2*base:.4f}): {ev.sum()} snapshots in {len(on)} onsets. Onsets at a step where the reported "
          f"readout_error changed: {int(ro_ch[on].sum())} of {len(on)} (chance rate {ro_ch[1:].mean():.2f}).")
        a_, b_ = jump[1:][ro_ch[1:]], jump[1:][~ro_ch[1:]]
        mw = stats.mannwhitneyu(a_, b_, alternative="greater")
        P(f"- Centroid jump between consecutive snapshots (cloud sigma; shot-noise scale ~0.045): median {np.median(a_):.3f} at "
          f"calibration changes vs {np.median(b_):.3f} elsewhere; one-sided Mann-Whitney p = {mw.pvalue:.2g}.")
        cc, jj = ro_ch[1:], jump[1:]
        P(f"  Confound: steps with a calibration change follow longer gaps (median {np.median(gaps[cc]):.2f} h vs {np.median(gaps[~cc]):.2f} h) and "
          f"jumps grow with gap (rank correlation {stats.spearmanr(jj, gaps).statistic:+.2f}).")
        bins = np.digitize(gaps, np.quantile(gaps, [0.25, 0.5, 0.75]))
        rk, rng, cnt, NP = stats.rankdata(jj), np.random.default_rng(0), 0, 20000
        for _ in range(NP):
            cp = cc.copy()
            for b in range(4):
                m = np.where(bins == b)[0]
                cp[m] = rng.permutation(cc[m])
            cnt += rk[cp].mean() >= rk[cc].mean()
        P(f"  Permutation test with calibration-change labels shuffled within gap-length quartiles: p = {(cnt+1)/(NP+1):.4f}. "
          f"Jumps over 0.5 sigma: {(jj > 0.5).sum()}, of which at a calibration change: {((jj > 0.5) & cc).sum()}.")
        de = abs(np.diff(p))
        mw2 = stats.mannwhitneyu(de[ro_ch[1:]], de[~ro_ch[1:]], alternative="greater")
        P(f"- |change in frozen-boundary error| at calibration changes vs elsewhere: median {np.median(de[ro_ch[1:]]):.4f} vs "
          f"{np.median(de[~ro_ch[1:]]):.4f}; p = {mw2.pvalue:.2g}.")
        big = np.argsort(jump)[::-1][:5]
        P(f"- Five largest centroid jumps: " + "; ".join(f"{jump[i]:.2f} sigma at {hrs[i]:.1f} h (IBM value changed: {'yes' if ro_ch[i] else 'no'})" for i in big))
        rho = stats.spearmanr(ibm, p)
        P(f"- Rank correlation of IBM-reported readout_error with frozen-boundary error: {rho.statistic:+.2f} (p = {rho.pvalue:.1e}).")

        P(f"- Shot noise. Baseline error {pb:.4f} = {pb*2000:.0f} of 2000 points; event threshold {2*base:.4f} = more than {2*base*2000:.0f} of 2000.")
        ns = int(scored.sum())
        for label, rate in (("baseline rate", pb), ("mean rate of scored snapshots", float(p[scored].mean())),
                            ("median rate of scored snapshots", float(np.median(p[scored])))):
            tail = stats.binom.sf(np.floor(2 * base * 2000 + 1e-9), 2000, rate)
            P(f"  - if the true error were constant at the {label} ({rate:.4f}): P(one snapshot crosses) = {tail:.2e}, "
              f"expected crossings in {ns} scored snapshots = {ns*tail:.3f}; observed {ev.sum()}.")
        kk = k[scored]
        disp = kk.var(ddof=1) / (kk.mean() * (1 - kk.mean() / 2000))
        chi = (ns - 1) * disp
        P(f"  - dispersion of the per-snapshot error count (variance / binomial variance): {disp:.2f}; chi-square p = "
          f"{stats.chi2.sf(chi, ns-1):.1e} (1.0 would be pure shot noise around a constant rate).")
        kq = kk[~ev[scored]]
        dq = kq.var(ddof=1) / (kq.mean() * (1 - kq.mean() / 2000))
        P(f"  - same with the event snapshots removed: {dq:.2f} (p = {stats.chi2.sf((len(kq)-1)*dq, len(kq)-1):.1e}).")
        P(f"  - threshold sensitivity (events / onsets): " + ", ".join(
            f"{f}x: {int(((p > f*base) & scored).sum())}/{sum(1 for i in np.where((p > f*base) & scored)[0] if not ((p > f*base) & scored)[i-1])}"
            for f in (1.5, 2.0, 2.5, 3.0, 4.0)))
        tie = np.where(scored & (k == int(round(2 * base * 2000))))[0]
        if len(tie):
            P(f"  - {len(tie)} scored snapshot(s) sit exactly on the threshold ({int(round(2*base*2000))} of 2000, at "
              f"{', '.join(f'{hrs[i]:.1f} h' for i in tie)}); real_per_qubit.py counts such a tie as an event through floating-point rounding, this script does not.")
        if ev.sum():
            P("  - per event snapshot: hour, frozen-boundary errors/2000 (binomial p vs baseline, Bonferroni over scored), "
              "re-centred errors/2000, e0/e1 per 1000, centroid shift (sigma), gain, rotation (deg)")
            for i in np.where(ev)[0]:
                pv = min(1.0, stats.binom.sf(k[i] - 1, 2000, pb) * ns)
                P(f"    - {hrs[i]:6.1f} h: {k[i]:3d} (p_adj {pv:.1e}), re-centred {ko[i]:3d}, e0/e1 {e[i,0]*1000:.0f}/{e[i,1]*1000:.0f}, "
                  f"shift {shift[i]:.2f}, gain {gain[i]:.3f}, rot {rot[i]:+.2f}")
        P(f"  - re-centred (own-centroid) error: median {np.median(ko[scored])/2000:.4f}; in event snapshots median "
          f"{(np.median(ko[ev])/2000 if ev.sum() else float('nan')):.4f}. Frozen minus re-centred, summed over event snapshots: "
          f"{int((k[ev]-ko[ev]).sum())} of {int(k[ev].sum())} misassigned points are removed by re-centring.")
        P(f"- Centroid shift from snapshot 0 (cloud sigma): median {np.median(shift):.2f}, max {shift.max():.2f}; gain range "
          f"{gain.min():.3f} to {gain.max():.3f}; rotation range {rot.min():+.2f} to {rot.max():+.2f} deg.")
        P()
        for i in range(n):
            rows.append((q, i, snaps[i][0], f"{hrs[i]:.3f}", f"{lag[i]:.3f}", int(lu_ch[i]), int(ro_ch[i]), f"{ibm[i]:.6f}", k[i], ko[i],
                         int(round(e[i, 0] * 1000)), int(round(e[i, 1] * 1000)), f"{shift[i]:.4f}", f"{jump[i]:.4f}", f"{gain[i]:.4f}",
                         f"{rot[i]:.3f}", int(ev[i]), int(scored[i])))

    open(out_path, "w").write("\n".join(lines) + "\n")
    with open(csv_path, "w") as f:
        f.write("qubit,snapshot,timestamp_utc,hours,timestamp_minus_last_update_h,last_update_changed,ibm_readout_error_changed,"
                "ibm_readout_error,frozen_errors_of_2000,recentred_errors_of_2000,e0_per_1000,e1_per_1000,centroid_shift_sigma,"
                "centroid_jump_sigma,gain,rotation_deg,event,scored\n")
        for r in rows:
            f.write(",".join(str(x) for x in r) + "\n")
    print(f"\nwrote {out_path} and {csv_path}")


if __name__ == "__main__":
    main()
