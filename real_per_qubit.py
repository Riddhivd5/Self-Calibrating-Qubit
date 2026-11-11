"""Per-qubit real-drift detector validation on all IBM snapshots (run from the repo root; needs data/, drift_framework.py,
real_drift_detector.py). Same detector as real_drift_detector.py (fire-rate z-score > 3 AND rise > 30%), but one qubit at a time."""
import datetime as dt
import json
import glob
import sys

import numpy as np

sys.path.insert(0, ".")
from drift_framework import Layout, build_circuit, features, sample_window
from real_drift_detector import QUBITS, frozen_boundary_error, load_snapshots

P_PHYS, D, SHOTS, N_BASE, ZTHR, REL = 0.001, 5, 4000, 10, 3.0, 0.30


def wilson(k, n, z=1.96):
    if n == 0:
        return (float("nan"),) * 2
    p = k / n
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return max(0, c - h), min(1, c + h)


snaps = load_snapshots("data")
ts = [dt.datetime.fromisoformat(s[0].replace("Z", "+00:00")) for s in snaps]
hrs = np.array([(t - ts[0]).total_seconds() / 3600 for t in ts])
# IBM last_update per snapshot (metadata json carries it)
metas = {}
for f in glob.glob("data/metadata_*.json"):
    m = json.load(open(f))
    metas[m["timestamp_utc"]] = m["calibration"]
lu = [dt.datetime.fromisoformat(metas[s[0]]["last_update"]) for s in snaps]
lu_changed = np.array([False] + [lu[i] != lu[i - 1] for i in range(1, len(lu))])
ibm_ro = np.array([s[1] for s in snaps])  # (n,3)
ro_changed = np.array([False] + [not np.allclose(ibm_ro[i], ibm_ro[i - 1]) for i in range(1, len(snaps))])
print(f"{len(snaps)} snapshots, span {hrs[-1]:.1f} h ({hrs[-1]/24:.1f} d); last_update changes at {lu_changed.sum()} steps, "
      f"IBM readout numbers change at {ro_changed.sum()}, both at {(lu_changed & ro_changed).sum()}")

first = snaps[0][2]
out = {}
for q in QUBITS:
    c0, c1 = first[f"q{q}_state0"].mean(), first[f"q{q}_state1"].mean()
    # per-quadrature sigma about each cloud's own mean (pooled I and Q), from snapshot 0
    def sig(z):
        r = z - z.mean()
        return np.sqrt(0.5 * np.mean(r.real ** 2 + r.imag ** 2))
    s0 = 0.5 * (sig(first[f"q{q}_state0"]) + sig(first[f"q{q}_state1"]))
    p = np.array([max(np.mean(frozen_boundary_error(s[2][f"q{q}_state0"], s[2][f"q{q}_state1"], c0, c1)), 1e-4) for s in snaps])
    shift = np.array([max(abs(s[2][f"q{q}_state0"].mean() - c0), abs(s[2][f"q{q}_state1"].mean() - c1)) / s0 for s in snaps])
    pb = float(np.median(p[1:N_BASE + 1]))
    circ = build_circuit(D, p_readout=pb, p_phys=P_PHYS)
    lay = Layout(circ)
    ref = features(sample_window(circ, 200000, seed=1)[0], lay, np.ones(lay.n_anc))["per_anc"]
    bf = np.array([features(sample_window(circ, SHOTS, seed=100 + k)[0], lay, ref)["fire_rate"] for k in range(30)])
    fire = np.array([features(sample_window(build_circuit(D, p_readout=pi, p_phys=P_PHYS), SHOTS, seed=5000 + i)[0], lay, ref)["fire_rate"]
                     for i, pi in enumerate(p)])
    z = (fire - bf.mean()) / bf.std()
    alarm = (z > ZTHR) & (fire / bf.mean() - 1 > REL)
    base = max(pb, 0.005)
    ev, qu = p > 2 * base, p < 1.25 * base
    ev[:N_BASE + 1] = False  # baseline snapshots themselves are not scored
    qu[:N_BASE + 1] = False
    tp, fn = int((ev & alarm).sum()), int((ev & ~alarm).sum())
    fp, tn = int((qu & alarm).sum()), int((qu & ~alarm).sum())
    onsets = [i for i in range(N_BASE + 1, len(ev)) if ev[i] and not ev[i - 1]]
    lat = []
    for i in onsets:
        h = np.where(alarm[i:i + 4])[0]
        lat.append(int(h[0]) if len(h) else None)
    out[q] = dict(p=p, alarm=alarm, ev=ev)
    print(f"\n== q{q}: baseline error {pb:.4f} (event if > {2*base:.4f}), cloud sigma {s0:.3g} raw units")
    print(f"  centroid shift in cloud-sigma units: median {np.median(shift):.2f}, max {shift.max():.2f}, snapshots > 1 sigma: {(shift>1).sum()}, > 0.5 sigma: {(shift>0.5).sum()}")
    lo, hi = wilson(tp, tp + fn)
    print(f"  events {tp+fn}: alarmed {tp} (sensitivity {tp/max(tp+fn,1):.2f}, 95% CI {lo:.2f}-{hi:.2f}); missed {fn}")
    lo, hi = wilson(fp, fp + tn)
    print(f"  quiet snapshots {fp+tn}: false alarms {fp} ({fp/max(fp+tn,1):.3f}, 95% CI {lo:.3f}-{hi:.3f})")
    print(f"  onsets {len(onsets)}, caught within 4 windows {sum(l is not None for l in lat)}; latency windows {lat}")
    print(f"  alarms total {alarm.sum()} of {len(alarm)}; alarms on snapshots where IBM numbers changed: {(alarm & ro_changed).sum()} of {ro_changed.sum()}; on last_update change: {(alarm & lu_changed).sum()} of {lu_changed.sum()}")
    evi = np.where(ev)[0]
    print(f"  event snapshots (hours): {[round(float(hrs[i]),1) for i in evi]}; last_update changed at those: {int(lu_changed[evi].sum())}/{len(evi)}; IBM readout numbers changed: {int(ro_changed[evi].sum())}/{len(evi)}")

print(f"\nlatency: one window = {SHOTS} shots x {D} QEC rounds = {SHOTS*D} syndrome rounds; the detector decides at the end of a window.")
