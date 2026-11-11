"""
adaptive_boundary_v3.py   (v2 with the label leak in the detector alarm removed)

What was wrong in v2: the alarm was computed as  np.mean(classify(iq, c0, c1) != true_states), i.e. the
controller used TRUE LABELS to decide whether to adapt faster. A real system never has them.

What v3 does instead
  simulated world : knows the true states, so it can work out how often the DEPLOYED boundary flips a
                    readout outcome (p_world). It turns that into real Stim syndromes (surface code d=5).
                    This is physics, not information the controller receives.
  controller      : sees ONLY the syndromes: detector fire rate and round-to-round correlation
                    (drift_framework.features), measured over 1500-shot windows.
  alarm threshold : learned from a healthy reference period = the first K_REF time points (24 h).
                    Alarm = (z > 3) AND (at least 30% above the reference), same rule as
                    real_drift_detector.py. No alarms are possible during the reference period.
  other label use : the t=0 calibration (initial centroids, cloud width) is labelled, once, as in any
                    real calibration. The |1> fraction pi is estimated from the discriminator's own t=0
                    decisions. The oracle and periodic baselines use labels by definition. All error
                    MEASUREMENTS use labels (offline evaluation).

Step sizes are chosen on q0 with tuning seeds 0-4, and everything reported uses seeds 100+ (q0, q1, q2).
Prints v2 (leaky) next to v3 (label-free) when adaptive_boundary_v2.csv is in the same folder.

Needs iq_generator.py, drift_framework.py and adaptive_boundary.py in the same folder.
Usage: python adaptive_boundary_v3.py            (about 15 minutes)
Outputs: adaptive_boundary_v3.csv, adaptive_boundary_v3.png
"""
import argparse
import csv
import os

import numpy as np

from adaptive_boundary import classify, misassign
from drift_framework import Layout, build_circuit, features
from iq_generator import DriftParams, IQDriftGenerator

P_PHYS, D = 0.001, 5
ZTHR, REL_RISE = 3.0, 0.30
K_REF = 6            # healthy reference period (time points)
WIN = 1500           # QEC shots per detector window
P1S = (0.5, 0.1)
ETA_FIXED, PERIOD = 0.3, 24.0
METHODS = ("frozen", "periodic", "moment (v1)", "two-means (v1)", "moment+pi", "EM+pi",
           "moment+pi gated", "EM+pi gated", "oracle")


# ---------------------------------------------------------------- simulated syndrome world
class SyndromeWorld:
    """Stim surface code with a readout flip probability chosen from a grid; returns syndrome features only."""

    def __init__(self):
        self.grid = np.geomspace(2e-4, 0.5, 48)
        circs = [build_circuit(D, p_readout=p, p_phys=P_PHYS) for p in self.grid]
        self.samplers = [c.compile_detector_sampler(seed=1000 + i) for i, c in enumerate(circs)]
        self.lay = Layout(circs[0])
        self.ones = np.ones(self.lay.n_anc)

    def observe(self, p_world, rng):
        x = np.interp(np.log(max(p_world, 2e-4)), np.log(self.grid), np.arange(len(self.grid)))
        i = int(np.floor(x)); i += int(rng.random() < (x - i)); i = min(i, len(self.grid) - 1)
        det = self.samplers[i].sample(WIN)
        f = features(det, self.lay, self.ones)
        return f["fire_rate"], f["tcorr"]


class Detector:
    """Controller-side detector: sees syndrome features only."""

    def __init__(self, world):
        self.world, self.f, self.t, self.n = world, [], [], 0

    def alarm(self, p_world, rng):
        fire, tc = self.world.observe(p_world, rng)   # p_world is consumed by the simulated hardware, not the controller
        self.n += 1
        if self.n <= K_REF:
            self.f.append(fire); self.t.append(tc); return False
        mf, mt = np.mean(self.f), np.mean(self.t)
        sf, st = max(np.std(self.f), 1e-4 * mf), max(np.std(self.t), 1e-4 * abs(mt))
        hit_f = (fire - mf) / sf > ZTHR and fire / mf - 1 > REL_RISE
        hit_t = (tc - mt) / st > ZTHR and tc / mt - 1 > REL_RISE
        return bool(hit_f or hit_t)


# ---------------------------------------------------------------- data (same generator and seeds as v2)
def make_data(profile, strength, seed, hours=168.0, step=4.0, n_unl=1500, n_eval=3000, n_cal=2000):
    gen = IQDriftGenerator(DriftParams(drift_profile=profile, stochastic_drift_strength=strength, rng_seed=seed))
    iq, st = gen.generate_shots(n_shots=20000, t_hours=0)
    f0, f1 = iq[st == 0].mean(), iq[st == 1].mean()
    sig2 = 0.5 * np.mean(np.r_[np.abs(iq[st == 0] - f0) ** 2, np.abs(iq[st == 1] - f1) ** 2])
    times = np.arange(0, hours + 1e-9, step)
    steps = [dict(t=t,
                  unl={p1: gen.generate_shots(n_shots=n_unl, t_hours=t, p_state1=p1) for p1 in P1S},
                  ev=gen.generate_shots(n_shots=n_eval, t_hours=t, p_state1=0.5),
                  cal=gen.generate_shots(n_shots=n_cal, t_hours=t)) for t in times]
    return dict(f0=f0, f1=f1, sig2=sig2, steps=steps, seed=seed)


def em_step(iq, c0, c1, pi, sig2):
    l1 = np.log(pi) - np.abs(iq - c1) ** 2 / (2 * sig2)
    l0 = np.log(1 - pi) - np.abs(iq - c0) ** 2 / (2 * sig2)
    r = 1.0 / (1.0 + np.exp(np.clip(l0 - l1, -50, 50)))
    n1, n0 = r.sum(), (1 - r).sum()
    return ((1 - r) @ iq / n0 if n0 > 10 else c0), (r @ iq / n1 if n1 > 10 else c1)


def simulate(data, p1, world, eta_q, eta_a):
    f0, f1, sig2 = data["f0"], data["f1"], data["sig2"]
    w0 = f1 - f0
    pi = float(np.clip(classify(data["steps"][0]["unl"][p1][0], f0, f1).mean(), 0.02, 0.98))
    rng = np.random.default_rng(10_000 + data["seed"] * 7 + int(p1 * 10))
    S = {m: [f0, f1] for m in METHODS}
    det = {"moment+pi gated": Detector(world), "EM+pi gated": Detector(world)}
    alarms = {k: 0 for k in det}
    mid, last_cal = (f0 + f1) / 2, 0.0
    out = {m: [] for m in METHODS}
    for sd in data["steps"]:
        t = sd["t"]; iq, stt = sd["unl"][p1]; eiq, est = sd["ev"]; ciq, cst = sd["cal"]

        def gated_eta(name):
            c0, c1 = S[name]
            p_world = np.mean(classify(iq, c0, c1) != stt)    # simulated hardware only
            a = det[name].alarm(p_world, rng); alarms[name] += a
            return eta_a if a else eta_q

        mid = (1 - ETA_FIXED) * mid + ETA_FIXED * iq.mean()
        S["moment (v1)"] = [mid - w0 / 2, mid + w0 / 2]
        c0, c1 = S["two-means (v1)"]; lab = classify(iq, c0, c1)
        if (lab == 0).sum() > 10: c0 = (1 - ETA_FIXED) * c0 + ETA_FIXED * iq[lab == 0].mean()
        if (lab == 1).sum() > 10: c1 = (1 - ETA_FIXED) * c1 + ETA_FIXED * iq[lab == 1].mean()
        S["two-means (v1)"] = [c0, c1]

        for name in ("moment+pi", "moment+pi gated"):
            eta = gated_eta(name) if "gated" in name else ETA_FIXED
            c0 = (1 - eta) * S[name][0] + eta * (iq.mean() - pi * w0)
            S[name] = [c0, c0 + w0]
        for name in ("EM+pi", "EM+pi gated"):
            eta = gated_eta(name) if "gated" in name else ETA_FIXED
            n0, n1 = em_step(iq, S[name][0], S[name][1], pi, sig2)
            S[name] = [(1 - eta) * S[name][0] + eta * n0, (1 - eta) * S[name][1] + eta * n1]

        o0, o1 = ciq[cst == 0].mean(), ciq[cst == 1].mean()
        if t - last_cal >= PERIOD - 1e-9:
            S["periodic"] = [o0, o1]; last_cal = t
        S["oracle"] = [o0, o1]
        for m in METHODS:
            out[m].append(misassign(eiq, est, *S[m]))
    res = {m: np.array(v) for m, v in out.items()}
    res["alarm_frac"] = {k: v / len(data["steps"]) for k, v in alarms.items()}
    return res


def recovery(r, m):
    den = r["frozen"].mean() - r["oracle"].mean()
    return np.nan if den < 0.002 else (r["frozen"].mean() - r[m].mean()) / den


def load_v2(path="adaptive_boundary_v2.csv"):
    v2 = {}
    if os.path.exists(path):
        for r in csv.DictReader(open(path)):
            v2[(r["profile"], float(r["strength"]), float(r["p_state1"]), r["method"])] = float(r["median_recovery"])
    return v2


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tune-seeds", type=int, default=5)
    ap.add_argument("--test-seeds", type=int, default=8)
    ap.add_argument("--strengths", nargs="+", type=float, default=[1.0, 4.0])
    a = ap.parse_args()
    print("building the syndrome world (48 Stim circuits)...", flush=True)
    world = SyndromeWorld()

    print("choosing step sizes on q0 with tuning seeds (never reported below)...", flush=True)
    tune = [make_data("q0", s, seed) for s in a.strengths for seed in range(a.tune_seeds)]
    best = None
    for eq in (0.1, 0.2, 0.3):
        for ea in (0.5, 0.9):
            rec = [recovery(simulate(d, p1, world, eq, ea), m) for d in tune for p1 in P1S for m in ("moment+pi gated", "EM+pi gated")]
            score = np.nanmedian(rec)
            if best is None or score > best[0]: best = (score, eq, ea)
    eq, ea = best[1], best[2]
    print(f"  chosen: eta_quiet={eq}, eta_alarm={ea}   (tuning-set median recovery {best[0]:.2f})", flush=True)

    v2 = load_v2(); rows = []; example = {}
    show = ("periodic", "moment (v1)", "moment+pi", "EM+pi", "moment+pi gated", "EM+pi gated")
    print("\nMEDIAN RECOVERY, held-out seeds (v3 = label-free alarm)   [v2 = leaky alarm, for comparison]", flush=True)
    print(f"{'profile':6s} {'str':>3s} {'p1':>4s} {'gap pp':>6s} |" + "".join(f"{m[:11]:>12s}" for m in show) + f" | {'v2 EM gated':>11s} {'alarm frac':>10s}", flush=True)
    for prof in ("q0", "q1", "q2"):
        for s in a.strengths:
            data = [make_data(prof, s, 100 + k) for k in range(a.test_seeds)]
            for p1 in P1S:
                R = [simulate(d, p1, world, eq, ea) for d in data]
                gap = np.mean([(r["frozen"].mean() - r["oracle"].mean()) * 100 for r in R])
                af = np.mean([r["alarm_frac"]["EM+pi gated"] for r in R])
                line = f"{prof:6s} {s:3.0f} {p1:4.2f} {gap:6.2f} |"
                for m in METHODS[1:-1]:
                    rec = np.array([recovery(r, m) for r in R]); fin = np.isfinite(rec)
                    med = np.median(rec[fin]) if fin.any() else np.nan
                    frac = np.mean(rec[fin] >= 0.8) if fin.any() else np.nan
                    rows.append((prof, s, p1, gap, m, med, frac, int(fin.sum()), af if "EM+pi gated" == m else ""))
                    if m in show: line += f"{med:12.2f}" if np.isfinite(med) else f"{'n/a':>12s}"
                v2v = v2.get((prof, s, p1, "EM+pi gated"))
                line += f" | {v2v:11.2f}" if v2v is not None and np.isfinite(v2v) else f" | {'n/a':>11s}"
                print(line + f" {af:10.2f}", flush=True)
                if (prof, s, p1) in (("q1", 4.0, 0.5), ("q1", 4.0, 0.1)):
                    example[p1] = (data[0]["steps"], R[0])

    print("\nFRACTION OF HELD-OUT RUNS WITH RECOVERY >= 0.8 (v3, label-free; runs with no drift are skipped)", flush=True)
    print(f"{'profile':6s} {'str':>3s} {'p1':>4s} {'runs':>4s} |" + "".join(f"{m[:11]:>12s}" for m in show), flush=True)
    for prof in ("q0", "q1", "q2"):
        for s in a.strengths:
            for p1 in P1S:
                sel = {r[4]: r for r in rows if r[0] == prof and r[1] == s and r[2] == p1}
                print(f"{prof:6s} {s:3.0f} {p1:4.2f} {sel['frozen' if 'frozen' in sel else 'periodic'][7]:4d} |" + "".join(
                    (f"{sel[m][6]:12.2f}" if np.isfinite(sel[m][6]) else f"{'n/a':>12s}") for m in show), flush=True)

    with open("adaptive_boundary_v3.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["profile", "strength", "p_state1", "frozen_minus_oracle_pp", "method", "median_recovery",
                    "fraction_runs_ge_0.8", "n_runs_with_drift", "alarm_fraction_EMpi_gated", "eta_quiet", "eta_alarm"])
        for r in rows: w.writerow([*r, eq, ea])

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1, 2, figsize=(12, 4.2), sharey=True)
    for k, p1 in enumerate(P1S):
        steps, r = example[p1]; t = [x["t"] for x in steps]
        for m, kw in (("frozen", dict(lw=2)), ("periodic", dict(lw=1)), ("EM+pi", dict(lw=1.2)),
                      ("EM+pi gated", dict(lw=2.2)), ("oracle", dict(ls="--", lw=1.2))):
            ax[k].plot(t, r[m] * 100, label=m, **kw)
        ax[k].axvspan(0, K_REF * 4, color="gray", alpha=0.15)
        ax[k].set_title(f"q1, drift x4, stream {p1:.0%} |1> (held-out seed; gray = detector reference period)"); ax[k].set_xlabel("hours")
        ax[k].title.set_fontsize(8)
    ax[0].set_ylabel("misassignment (%)"); ax[0].legend(fontsize=8)
    fig.tight_layout(); fig.savefig("adaptive_boundary_v3.png", dpi=150)
    print("\nwrote adaptive_boundary_v3.csv and adaptive_boundary_v3.png", flush=True)


if __name__ == "__main__":
    main()
