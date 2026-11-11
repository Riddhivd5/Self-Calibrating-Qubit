"""
adaptive_boundary_v5.py   = v4 with exactly two detector changes (v4 is not modified)

  change 1  alarm trigger : fire rate ONLY. Round-to-round correlation is still computed, but cannot trigger an alarm.
  change 2  reference     : healthy reference = K_REF windows recorded IMMEDIATELY AFTER the labelled t=0 calibration,
                            with the freshly calibrated boundary (windows take milliseconds, so this is realistic),
                            not the first K_REF time points of the run. Alarms are possible from the first step.

Everything else is unchanged: physical syndrome model (true Stim outcomes read through the deployed boundary with real
IQ dots), controller sees only (fire rate, correlation) and unlabelled IQ dots, label-isolation test at start-up.
Both detectors are run on the SAME fresh held-out seeds (200+), each with its own step sizes tuned on seeds 0-2 only.
Each gated method has its own Stim sampler and random stream, so they do not influence each other.
Stream mixes tested: 50%, 30% (the realistic share of |1> among true outcomes in this circuit) and 10% |1>.

Needs iq_generator.py, drift_framework.py, adaptive_boundary.py.   Usage: python adaptive_boundary_v5.py (~35 min)  or --quick
Outputs: adaptive_boundary_v5.csv, adaptive_boundary_v5.png
"""
import argparse
import copy
import csv

import numpy as np

from adaptive_boundary import classify, misassign
from drift_framework import Layout, build_circuit, features
from iq_generator import DriftParams, IQDriftGenerator

P_PHYS, D = 0.001, 5
ZTHR, REL_RISE, K_REF, WIN = 3.0, 0.30, 6, 1500
P1S, ETA_FIXED, PERIOD = (0.5, 0.3, 0.1), 0.3, 24.0
G4, G5 = "EM+pi gated (v4 alarm)", "EM+pi gated (v5 alarm)"
FAST, ETA_FAST = "EM+pi always fast (no detector)", 0.9      # control: is the detector adding anything beyond adapting fast?
METHODS = ("frozen", "periodic", "moment (v1)", "two-means (v1)", "moment+pi", "EM+pi", FAST, G4, G5, "oracle")
ADAPTIVE = [m for m in METHODS if m not in ("frozen", "periodic", "oracle")]


class Hardware:
    """Simulated physics. Output: detection events. Never exposed to the controller except through those events."""

    def __init__(self):
        self.circ = build_circuit(D, p_readout=0.0, p_phys=P_PHYS)
        self.m2d = self.circ.compile_m2d_converter()
        self.lay = Layout(self.circ)
        self.ones = np.ones(self.lay.n_anc)
        self.last_flip_rate = np.nan

    def sampler(self, seed):
        return self.circ.compile_sampler(seed=seed)

    def syndromes(self, sampler, pool0, pool1, c0, c1, rng):
        misread0 = classify(pool0, c0, c1) == 1
        misread1 = classify(pool1, c0, c1) == 0
        true_out = sampler.sample(WIN)
        idx = rng.integers(0, len(pool0), true_out.shape)
        flip = np.where(true_out, misread1[idx], misread0[idx])
        self.last_flip_rate = float(flip.mean())                     # EVALUATION ONLY
        return self.m2d.convert(measurements=true_out ^ flip, separate_observables=False)

    def features(self, det):
        f = features(det, self.lay, self.ones)
        return f["fire_rate"], f["tcorr"]


class ControllerV4:
    """v4: reference = first K_REF windows of the run; either feature can alarm."""

    def __init__(self):
        self.f, self.t, self.n = [], [], 0

    def alarm(self, fire, tc):
        self.n += 1
        if self.n <= K_REF:
            self.f.append(fire); self.t.append(tc); return False
        mf, mt = np.mean(self.f), np.mean(self.t)
        sf, st = max(np.std(self.f), 1e-4 * mf), max(np.std(self.t), 1e-4 * abs(mt))
        return bool(((fire - mf) / sf > ZTHR and fire / mf - 1 > REL_RISE) or ((tc - mt) / st > ZTHR and tc / mt - 1 > REL_RISE))


class ControllerV5:
    """v5: reference = windows recorded right after calibration; only the fire rate can alarm."""

    def __init__(self, ref_fire):
        self.m = float(np.mean(ref_fire)); self.s = max(float(np.std(ref_fire)), 1e-4 * self.m)

    def alarm(self, fire, tc):                      # tc (correlation) is accepted but deliberately ignored
        return bool((fire - self.m) / self.s > ZTHR and fire / self.m - 1 > REL_RISE)


def reference_windows(hw, data, seed):
    """K_REF windows at the calibration-time state with the freshly calibrated boundary."""
    smp, rng, s0 = hw.sampler(40_000 + seed), np.random.default_rng(40_000 + seed), data["steps"][0]
    return np.array([hw.features(hw.syndromes(smp, s0["pool0"], s0["pool1"], data["f0"], data["f1"], rng))[0] for _ in range(K_REF)])


def make_data(profile, strength, seed, hours=168.0, step=4.0, n_unl=1500, n_eval=3000, n_cal=2000, n_pool=4000, fixed_t=None):
    prm = dict(drift_profile=profile, stochastic_drift_strength=strength, rng_seed=seed)
    gen, genp = IQDriftGenerator(DriftParams(**prm)), IQDriftGenerator(DriftParams(**prm))
    iq, st = gen.generate_shots(n_shots=20000, t_hours=0)
    f0, f1 = iq[st == 0].mean(), iq[st == 1].mean()
    sig2 = 0.5 * np.mean(np.r_[np.abs(iq[st == 0] - f0) ** 2, np.abs(iq[st == 1] - f1) ** 2])
    steps = []
    for t in np.arange(0, hours + 1e-9, step):
        te = t if fixed_t is None else fixed_t
        steps.append(dict(t=t,
                          unl={p1: gen.generate_shots(n_shots=n_unl, t_hours=te, p_state1=p1)[0] for p1 in P1S},   # dots only
                          ev=gen.generate_shots(n_shots=n_eval, t_hours=te, p_state1=0.5),
                          cal=gen.generate_shots(n_shots=n_cal, t_hours=te),
                          pool0=genp.generate_shots(n_shots=n_pool, t_hours=te, p_state1=0.0)[0],
                          pool1=genp.generate_shots(n_shots=n_pool, t_hours=te, p_state1=1.0)[0]))
    return dict(f0=f0, f1=f1, sig2=sig2, steps=steps, seed=seed)


def em_step(iq, c0, c1, pi, sig2):
    l1 = np.log(pi) - np.abs(iq - c1) ** 2 / (2 * sig2)
    l0 = np.log(1 - pi) - np.abs(iq - c0) ** 2 / (2 * sig2)
    r = 1.0 / (1.0 + np.exp(np.clip(l0 - l1, -50, 50)))
    n1, n0 = r.sum(), (1 - r).sum()
    return ((1 - r) @ iq / n0 if n0 > 10 else c0), (r @ iq / n1 if n1 > 10 else c1)


def simulate(data, p1, hw, etas):
    """etas: {G4: (eta_quiet, eta_alarm), G5: (...)}"""
    f0, f1, sig2 = data["f0"], data["f1"], data["sig2"]; w0 = f1 - f0; seed = data["seed"]
    pi = float(np.clip(classify(data["steps"][0]["unl"][p1], f0, f1).mean(), 0.02, 0.98))      # label-free
    tag = seed * 7 + int(p1 * 10)
    smp = {G4: hw.sampler(20_000 + tag), G5: hw.sampler(21_000 + tag)}
    rng = {G4: np.random.default_rng(10_000 + tag), G5: np.random.default_rng(11_000 + tag)}
    ctrl = {G4: ControllerV4(), G5: ControllerV5(reference_windows(hw, data, seed))}
    alarms = {G4: 0, G5: 0}
    S = {m: [f0, f1] for m in METHODS}
    mid, last_cal = (f0 + f1) / 2, 0.0
    out = {m: [] for m in METHODS}; traj = {m: [] for m in ADAPTIVE}
    for sd in data["steps"]:
        t, iq = sd["t"], sd["unl"][p1]; eiq, est = sd["ev"]; ciq, cst = sd["cal"]
        mid = (1 - ETA_FIXED) * mid + ETA_FIXED * iq.mean()
        S["moment (v1)"] = [mid - w0 / 2, mid + w0 / 2]
        c0, c1 = S["two-means (v1)"]; lab = classify(iq, c0, c1)
        if (lab == 0).sum() > 10: c0 = (1 - ETA_FIXED) * c0 + ETA_FIXED * iq[lab == 0].mean()
        if (lab == 1).sum() > 10: c1 = (1 - ETA_FIXED) * c1 + ETA_FIXED * iq[lab == 1].mean()
        S["two-means (v1)"] = [c0, c1]
        c0 = (1 - ETA_FIXED) * S["moment+pi"][0] + ETA_FIXED * (iq.mean() - pi * w0); S["moment+pi"] = [c0, c0 + w0]
        for name in ("EM+pi", FAST, G4, G5):
            if name == "EM+pi": eta = ETA_FIXED
            elif name == FAST: eta = ETA_FAST
            else:
                det = hw.syndromes(smp[name], sd["pool0"], sd["pool1"], S[name][0], S[name][1], rng[name])   # physics
                a = ctrl[name].alarm(*hw.features(det)); alarms[name] += a                                       # features only
                eta = etas[name][1] if a else etas[name][0]
            n0, n1 = em_step(iq, S[name][0], S[name][1], pi, sig2)
            S[name] = [(1 - eta) * S[name][0] + eta * n0, (1 - eta) * S[name][1] + eta * n1]
        o0, o1 = ciq[cst == 0].mean(), ciq[cst == 1].mean()
        if t - last_cal >= PERIOD - 1e-9: S["periodic"] = [o0, o1]; last_cal = t
        S["oracle"] = [o0, o1]
        for m in METHODS: out[m].append(misassign(eiq, est, *S[m]))
        for m in ADAPTIVE: traj[m].append(tuple(S[m]))
    res = {m: np.array(v) for m, v in out.items()}
    res["alarm_frac"] = {k: v / len(data["steps"]) for k, v in alarms.items()}
    res["traj"] = {m: np.array(v) for m, v in traj.items()}
    res["contaminated"] = bool(res["frozen"][:K_REF].max() > 2 * max(res["frozen"][0], 0.005))
    return res


def recovery(r, m):
    den = r["frozen"].mean() - r["oracle"].mean()
    return np.nan if den < 0.002 else (r["frozen"].mean() - r[m].mean()) / den


def shuffled_labels(data, seed=0):
    d = copy.deepcopy(data); rg = np.random.default_rng(seed)
    for sd in d["steps"]:
        sd["ev"] = (sd["ev"][0], rg.permutation(sd["ev"][1])); sd["cal"] = (sd["cal"][0], rg.permutation(sd["cal"][1]))
    return d


def probe(data, hw, seed, kind):
    """Detector alone on the FROZEN boundary. Truth (event/quiet) uses the hardware's actual flip rate: evaluation only."""
    smp, rng = hw.sampler(30_000 + seed), np.random.default_rng(seed)
    c = ControllerV4() if kind == "v4" else ControllerV5(reference_windows(hw, data, seed))
    al, ev, qu, e0 = [], [], [], None
    for sd in data["steps"]:
        al.append(c.alarm(*hw.features(hw.syndromes(smp, sd["pool0"], sd["pool1"], data["f0"], data["f1"], rng))))
        e = hw.last_flip_rate; e0 = e if e0 is None else e0; b = max(e0, 0.005); ev.append(e > 2 * b); qu.append(e < 1.25 * b)
    return np.array(al), np.array(ev), np.array(qu)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tune-seeds", type=int, default=3)
    ap.add_argument("--test-seeds", type=int, default=8)
    ap.add_argument("--healthy-runs", type=int, default=30)
    ap.add_argument("--strengths", nargs="+", type=float, default=[1.0, 4.0])
    ap.add_argument("--quick", action="store_true")
    a = ap.parse_args()
    if a.quick: a.tune_seeds, a.test_seeds, a.healthy_runs, a.strengths = 1, 2, 4, [4.0]
    hw = Hardware(); TEST0 = 200
    assert set(range(a.tune_seeds)).isdisjoint(range(TEST0, TEST0 + a.test_seeds))

    print("== LABEL ISOLATION TEST ==", flush=True)
    d0 = make_data("q0", 4.0, TEST0); et = {G4: (0.3, 0.9), G5: (0.3, 0.9)}
    ra, rb = simulate(d0, 0.1, hw, et), simulate(shuffled_labels(d0), 0.1, hw, et)
    same = all(np.array_equal(ra["traj"][m], rb["traj"][m]) for m in ADAPTIVE)
    print(f"all adaptive centroid trajectories identical after shuffling every evaluation/calibration label: {same}", flush=True)
    assert same

    print("\n== STEP SIZES, chosen per detector on q0 tuning seeds (never reported below) ==", flush=True)
    tune = [make_data("q0", s, seed) for s in a.strengths for seed in range(a.tune_seeds)]
    scores = {G4: {}, G5: {}}
    for eq in (0.1, 0.2, 0.3):
        for ea in (0.5, 0.9):
            rec = {G4: [], G5: []}
            for d in tune:
                for p1 in P1S:
                    r = simulate(d, p1, hw, {G4: (eq, ea), G5: (eq, ea)})
                    for g in rec: rec[g].append(recovery(r, g))
            for g in rec: scores[g][(eq, ea)] = np.nanmedian(rec[g])
    etas = {g: max(scores[g], key=scores[g].get) for g in scores}
    for g in etas: print(f"  {g}: eta_quiet, eta_alarm = {etas[g]} (tuning median recovery {scores[g][etas[g]]:.2f})", flush=True)

    rows, runs_all, probes, example = [], [], [], {}
    print("\n== HELD-OUT RESULTS, fresh seeds 200+ (median recovery [IQR], share of runs >= 0.8, share of steps alarmed) ==", flush=True)
    print(f"{'prof':4s} {'str':>3s} {'p1':>4s} {'gap pp':>6s} {'runs':>4s} | {'period.':>7s} {'EM fix':>6s} {'EM fast':>7s} | {'gated, v4 alarm':^36s} | {'gated, v5 alarm':^36s}", flush=True)
    fmt = lambda x: f"{x:5.2f}" if np.isfinite(x) else "  n/a"
    for prof in ("q0", "q1", "q2"):
        for s in a.strengths:
            data = [make_data(prof, s, TEST0 + k) for k in range(a.test_seeds)]
            for d in data:
                for kind in ("v4", "v5"): probes.append((prof, s, kind, *probe(d, hw, d["seed"], kind)))
            for p1 in P1S:
                R = [simulate(d, p1, hw, etas) for d in data]
                for r in R: runs_all.append((prof, s, p1, r))
                gap = np.mean([(r["frozen"].mean() - r["oracle"].mean()) * 100 for r in R]); cell = {}
                for m in METHODS[1:-1]:
                    rec = np.array([recovery(r, m) for r in R]); fin = np.isfinite(rec)
                    q = np.percentile(rec[fin], [25, 50, 75]) if fin.any() else [np.nan] * 3
                    fr = np.mean(rec[fin] >= 0.8) if fin.any() else np.nan
                    af = np.mean([r["alarm_frac"][m] for r in R]) if m in (G4, G5) else ""
                    rows.append((prof, s, p1, gap, m, q[1], q[0], q[2], fr, int(fin.sum()), af)); cell[m] = (q, fr, af, int(fin.sum()))
                g4, g5 = cell[G4], cell[G5]
                print(f"{prof:4s} {s:3.0f} {p1:4.2f} {gap:6.2f} {g4[3]:4d} | {fmt(cell['periodic'][0][1]):>7s} {fmt(cell['EM+pi'][0][1]):>6s} {fmt(cell[FAST][0][1]):>7s} | "
                      f"{fmt(g4[0][1])} [{fmt(g4[0][0])} to {fmt(g4[0][2])}] {fmt(g4[1])} {100*g4[2]:4.0f}% | "
                      f"{fmt(g5[0][1])} [{fmt(g5[0][0])} to {fmt(g5[0][2])}] {fmt(g5[1])} {100*g5[2]:4.0f}%", flush=True)
                if (prof, s, p1) == ("q1", 4.0, 0.3): example = (data[0]["steps"], R[0])

    print("\n== DETECTOR VALIDATION ON FRESH SEEDS ==", flush=True)
    print("healthy false-alarm steps (frozen boundary, steps after the first 6 for both detectors):")
    for kind in ("v4", "v5"):
        line = f"  {kind} detector: "
        for prof in ("q0", "q1", "q2"):
            n = c = runs = 0
            for k in range(a.healthy_runs):
                d = make_data(prof, 1.0, 600 + k, fixed_t=0.0); al = probe(d, hw, 600 + k, kind)[0][K_REF:]
                n += len(al); c += al.sum(); runs += int(al.any())
            line += f"{prof} {c}/{n} ({100*c/n:.2f}%, {runs}/{a.healthy_runs} runs)   "
        print(line, flush=True)
    print("drifting data, frozen boundary, steps 6+ (event = actual flip rate > 2x start):")
    for kind in ("v4", "v5"):
        evN = evH = 0; on = {"all": [0, 0], "contaminated": [0, 0], "clean": [0, 0]}; qN = qF = 0
        for prof, s, kd, al, ev, qu in probes:
            if kd != kind: continue
            post = np.arange(len(al)) >= K_REF; evN += (ev & post).sum(); evH += (ev & al & post).sum()
            qN += (qu & post).sum(); qF += (qu & al & post).sum()
            for i in range(K_REF, len(ev)):
                if ev[i] and not ev[i - 1]:
                    got = bool(al[i:i + 4].any()); key = "contaminated" if (ev[:K_REF].any()) else "clean"
                    for k in ("all", key): on[k][0] += got; on[k][1] += 1
        print(f"  {kind} detector: event steps alarmed {100*evH/max(evN,1):.1f}% | quiet steps alarmed {100*qF/max(qN,1):.1f}% | onsets caught within 12 h: "
              f"all {on['all'][0]}/{on['all'][1]}, contaminated-reference {on['contaminated'][0]}/{on['contaminated'][1]}, clean {on['clean'][0]}/{on['clean'][1]}", flush=True)
    print("recovery split by whether drift is already present in the first 24 h:")
    for g in (FAST, G4, G5):
        for tag, flag in (("clean", False), ("contaminated", True)):
            rec = np.array([recovery(r, g) for _, _, _, r in runs_all if r["contaminated"] == flag]); rec = rec[np.isfinite(rec)]
            print(f"  {g:24s} {tag:13s}: {len(rec):3d} runs, median {np.median(rec) if len(rec) else float('nan'):.2f}, share >= 0.8: {np.mean(rec >= 0.8) if len(rec) else float('nan'):.2f}")

    with open("adaptive_boundary_v5.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["profile", "strength", "p_state1", "frozen_minus_oracle_pp", "method", "median_recovery", "q25", "q75", "fraction_runs_ge_0.8",
                    "n_runs_with_drift", "alarm_fraction", "eta_quiet_v4alarm", "eta_alarm_v4alarm", "eta_quiet_v5alarm", "eta_alarm_v5alarm"])
        for r in rows: w.writerow([*r, *etas[G4], *etas[G5]])
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    if example:
        steps, r = example; t = [x["t"] for x in steps]
        plt.figure(figsize=(9, 4.2))
        for m, kw in (("frozen", dict(lw=2)), ("periodic", dict(lw=1)), (FAST, dict(lw=1.2)), (G4, dict(lw=1.4)), (G5, dict(lw=2.2)), ("oracle", dict(ls="--", lw=1.2))):
            plt.plot(t, r[m] * 100, label=m, **kw)
        plt.xlabel("hours"); plt.ylabel("misassignment (%)"); plt.legend(fontsize=8)
        plt.title("q1, drift x4, 30% |1> stream (first held-out seed)", fontsize=9); plt.tight_layout(); plt.savefig("adaptive_boundary_v5.png", dpi=150)
    print("\nwrote adaptive_boundary_v5.csv and adaptive_boundary_v5.png", flush=True)


if __name__ == "__main__":
    main()
