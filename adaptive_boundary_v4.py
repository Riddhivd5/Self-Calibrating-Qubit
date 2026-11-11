"""
adaptive_boundary_v4.py   (controller sees ONLY syndrome features; syndromes come from a physical readout model)

Interfaces (nothing crosses them except what is listed)
  Hardware      simulated physics. Inputs: the deployed boundary (c0,c1), IQ dot pools of the true |0> and |1>
                clouds at that time. It samples TRUE ancilla/data outcomes from the Stim surface code
                (no readout flips in the circuit), reads each outcome through the deployed boundary using real
                IQ dots of that state (so errors are state dependent), and converts the observed outcomes to
                detection events with Stim's measurement-to-detector converter.   OUTPUT: detection events.
  Features      fire rate and round-to-round correlation (drift_framework.features) of one window.
  Controller    sees ONLY (fire rate, correlation) per window and the unlabelled IQ stream. Healthy reference =
                first K_REF windows (no alarms then). Alarm = z > 3 and >= 30% above reference.
                It never receives labels, an error rate, or the hidden states.
Structural guarantees
  * stream (unlabelled) dots are stored WITHOUT states, so the controller code cannot touch them;
  * labels exist only in: the t=0 calibration, the "cal" and "ev" arrays (oracle / periodic baselines and
    offline measurement), and the Hardware pools (physics);
  * a test at start-up shuffles every label array and checks all adaptive trajectories are unchanged.
Validation printed by this script: pool-vs-eval consistency, physical syndrome model vs symmetric-flip model,
label isolation, healthy false-alarm rate, missed-drift/delay of the detector on drifting data, effect of a
contaminated reference period, step sizes tuned on q0 seeds 0-3 only, held-out seeds 100+ for all reporting.

Needs iq_generator.py, drift_framework.py, adaptive_boundary.py in the same folder. Optionally
adaptive_boundary_v3.csv to print v3 next to v4.
Usage: python adaptive_boundary_v4.py          (about 25 minutes)    python adaptive_boundary_v4.py --quick (smoke test)
Outputs: adaptive_boundary_v4.csv, adaptive_boundary_v4.png
"""
import argparse
import copy
import csv
import os

import numpy as np
import stim

from adaptive_boundary import classify, misassign
from drift_framework import Layout, build_circuit, features, sample_window
from iq_generator import DriftParams, IQDriftGenerator

P_PHYS, D = 0.001, 5
ZTHR, REL_RISE, K_REF, WIN = 3.0, 0.30, 6, 1500
P1S, ETA_FIXED, PERIOD = (0.5, 0.1), 0.3, 24.0
METHODS = ("frozen", "periodic", "moment (v1)", "two-means (v1)", "moment+pi", "EM+pi",
           "moment+pi gated", "EM+pi gated", "oracle")
ADAPTIVE = [m for m in METHODS if m not in ("frozen", "periodic", "oracle")]


# ======================================================================== simulated hardware (physics)
class Hardware:
    def __init__(self):
        self.circ = build_circuit(D, p_readout=0.0, p_phys=P_PHYS)       # TRUE outcomes: no readout flips here
        self.m2d = self.circ.compile_m2d_converter()
        self.lay = Layout(self.circ)
        self.ones = np.ones(self.lay.n_anc)

    def start(self, seed):
        self.sampler = self.circ.compile_sampler(seed=seed)

    def syndromes(self, pool0, pool1, c0, c1, rng):
        misread0 = classify(pool0, c0, c1) == 1          # prepared 0, discriminator says 1
        misread1 = classify(pool1, c0, c1) == 0          # prepared 1, discriminator says 0
        true_out = self.sampler.sample(WIN)              # (WIN, n_measurements) true outcomes
        idx = rng.integers(0, len(pool0), true_out.shape)
        flip = np.where(true_out, misread1[idx], misread0[idx])
        self.last_flip_rate = float(flip.mean())          # actual physical flip rate of this window (EVALUATION ONLY)
        return self.m2d.convert(measurements=true_out ^ flip, separate_observables=False)

    def features(self, det):
        f = features(det, self.lay, self.ones)
        return f["fire_rate"], f["tcorr"]


class Controller:
    """Sees only syndrome features."""

    def __init__(self):
        self.f, self.t, self.n = [], [], 0

    def alarm(self, fire, tc):
        self.n += 1
        if self.n <= K_REF:
            self.f.append(fire); self.t.append(tc); return False
        mf, mt = np.mean(self.f), np.mean(self.t)
        sf, st = max(np.std(self.f), 1e-4 * mf), max(np.std(self.t), 1e-4 * abs(mt))
        return bool(((fire - mf) / sf > ZTHR and fire / mf - 1 > REL_RISE) or
                    ((tc - mt) / st > ZTHR and tc / mt - 1 > REL_RISE))


# ======================================================================== data
def make_data(profile, strength, seed, hours=168.0, step=4.0, n_unl=1500, n_eval=3000, n_cal=2000, n_pool=4000, fixed_t=None):
    prm = dict(drift_profile=profile, stochastic_drift_strength=strength, rng_seed=seed)
    gen, genp = IQDriftGenerator(DriftParams(**prm)), IQDriftGenerator(DriftParams(**prm))   # genp: physics pools only
    iq, st = gen.generate_shots(n_shots=20000, t_hours=0)
    f0, f1 = iq[st == 0].mean(), iq[st == 1].mean()                    # labelled t=0 calibration (once)
    sig2 = 0.5 * np.mean(np.r_[np.abs(iq[st == 0] - f0) ** 2, np.abs(iq[st == 1] - f1) ** 2])
    steps = []
    for t in np.arange(0, hours + 1e-9, step):
        te = t if fixed_t is None else fixed_t
        steps.append(dict(
            t=t,
            unl={p1: gen.generate_shots(n_shots=n_unl, t_hours=te, p_state1=p1)[0] for p1 in P1S},   # dots only, NO states
            ev=gen.generate_shots(n_shots=n_eval, t_hours=te, p_state1=0.5),                          # labels: offline measurement
            cal=gen.generate_shots(n_shots=n_cal, t_hours=te),                                        # labels: oracle/periodic
            pool0=genp.generate_shots(n_shots=n_pool, t_hours=te, p_state1=0.0)[0],                   # physics
            pool1=genp.generate_shots(n_shots=n_pool, t_hours=te, p_state1=1.0)[0]))
    return dict(f0=f0, f1=f1, sig2=sig2, steps=steps, seed=seed)


def em_step(iq, c0, c1, pi, sig2):
    l1 = np.log(pi) - np.abs(iq - c1) ** 2 / (2 * sig2)
    l0 = np.log(1 - pi) - np.abs(iq - c0) ** 2 / (2 * sig2)
    r = 1.0 / (1.0 + np.exp(np.clip(l0 - l1, -50, 50)))
    n1, n0 = r.sum(), (1 - r).sum()
    return ((1 - r) @ iq / n0 if n0 > 10 else c0), (r @ iq / n1 if n1 > 10 else c1)


# ======================================================================== one run
def simulate(data, p1, hw, eta_q, eta_a):
    f0, f1, sig2 = data["f0"], data["f1"], data["sig2"]
    w0 = f1 - f0
    pi = float(np.clip(classify(data["steps"][0]["unl"][p1], f0, f1).mean(), 0.02, 0.98))   # label-free
    rng = np.random.default_rng(10_000 + data["seed"] * 7 + int(p1 * 10))
    hw.start(20_000 + data["seed"] * 7 + int(p1 * 10))
    S = {m: [f0, f1] for m in METHODS}
    ctrl = {"moment+pi gated": Controller(), "EM+pi gated": Controller()}
    alarms = {k: 0 for k in ctrl}
    mid, last_cal = (f0 + f1) / 2, 0.0
    out = {m: [] for m in METHODS}
    traj = {m: [] for m in ADAPTIVE}
    for sd in data["steps"]:
        t, iq = sd["t"], sd["unl"][p1]
        eiq, est = sd["ev"]; ciq, cst = sd["cal"]

        def gated_eta(name):
            c0, c1 = S[name]
            det = hw.syndromes(sd["pool0"], sd["pool1"], c0, c1, rng)       # physics -> detection events
            a = ctrl[name].alarm(*hw.features(det))                          # controller sees features only
            alarms[name] += a
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
        for m in METHODS: out[m].append(misassign(eiq, est, *S[m]))
        for m in ADAPTIVE: traj[m].append(tuple(S[m]))
    res = {m: np.array(v) for m, v in out.items()}
    res["alarm_frac"] = {k: v / len(data["steps"]) for k, v in alarms.items()}
    res["traj"] = {m: np.array(v) for m, v in traj.items()}
    e0 = max(res["frozen"][0], 0.005)
    res["contaminated"] = bool(res["frozen"][:K_REF].max() > 2 * e0)       # drift already inside the reference period
    return res


def recovery(r, m):
    den = r["frozen"].mean() - r["oracle"].mean()
    return np.nan if den < 0.002 else (r["frozen"].mean() - r[m].mean()) / den


# ======================================================================== validation helpers
def shuffled_labels(data, seed=0):
    d = copy.deepcopy(data); rg = np.random.default_rng(seed)
    for sd in d["steps"]:
        sd["ev"] = (sd["ev"][0], rg.permutation(sd["ev"][1])); sd["cal"] = (sd["cal"][0], rg.permutation(sd["cal"][1]))
    return d


def probe_detector(data, hw, seed=0):
    """Detector alone on the FROZEN boundary. Truth (event/quiet) uses labels, for evaluation only."""
    rng = np.random.default_rng(seed); hw.start(30_000 + seed)
    c = Controller(); al, ev, qu = [], [], []
    e0 = None
    for sd in data["steps"]:
        al.append(c.alarm(*hw.features(hw.syndromes(sd["pool0"], sd["pool1"], data["f0"], data["f1"], rng))))
        err = hw.last_flip_rate; e0 = err if e0 is None else e0      # truth = what the QEC stream actually suffered
        base = max(e0, 0.005); ev.append(err > 2 * base); qu.append(err < 1.25 * base)
    return np.array(al), np.array(ev), np.array(qu)


def load_v3(path="adaptive_boundary_v3.csv"):
    v3 = {}
    if os.path.exists(path):
        for r in csv.DictReader(open(path)):
            v3[(r["profile"], float(r["strength"]), float(r["p_state1"]), r["method"])] = float(r["median_recovery"])
    return v3


# ======================================================================== main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tune-seeds", type=int, default=4)
    ap.add_argument("--test-seeds", type=int, default=8)
    ap.add_argument("--healthy-runs", type=int, default=30)
    ap.add_argument("--strengths", nargs="+", type=float, default=[1.0, 4.0])
    ap.add_argument("--quick", action="store_true")
    a = ap.parse_args()
    if a.quick: a.tune_seeds, a.test_seeds, a.healthy_runs, a.strengths = 1, 2, 4, [4.0]
    hw = Hardware()
    assert set(range(a.tune_seeds)).isdisjoint(range(100, 100 + a.test_seeds))

    # ---- V1/V2: is the physical syndrome model grounded?
    print("== VALIDATION OF THE SYNDROME MODEL ==", flush=True)
    d0 = make_data("q1", 4.0, 100)
    pe = np.array([0.5 * (np.mean(classify(s["pool0"], d0["f0"], d0["f1"]) == 1) + np.mean(classify(s["pool1"], d0["f0"], d0["f1"]) == 0)) for s in d0["steps"]])
    ee = np.array([misassign(*s["ev"], d0["f0"], d0["f1"]) for s in d0["steps"]])
    print(f"V1 pool vs evaluation dots (same drift path?): correlation of frozen-boundary error over 43 steps = {np.corrcoef(pe, ee)[0, 1]:.3f}"
          f"  (pool mean {pe.mean()*100:.2f}%, eval mean {ee.mean()*100:.2f}%)", flush=True)
    rng = np.random.default_rng(1); hw.start(5)
    print("V2 fire rate: physical model vs symmetric-flip model at the SAME mean readout error (q1 x4, frozen boundary)")
    print("     step  e0(prep0)  e1(prep1)  mean err   fire(physical)  fire(symmetric)  ratio")
    for k in np.argsort(pe)[[5, 20, 35, 42]]:
        s = d0["steps"][k]
        e0_ = np.mean(classify(s["pool0"], d0["f0"], d0["f1"]) == 1); e1_ = np.mean(classify(s["pool1"], d0["f0"], d0["f1"]) == 0)
        fp = hw.syndromes(s["pool0"], s["pool1"], d0["f0"], d0["f1"], rng).mean()
        fs = sample_window(build_circuit(D, p_readout=0.5 * (e0_ + e1_), p_phys=P_PHYS), WIN * 4, seed=3)[0].mean()
        print(f"     {k:4d}   {e0_:8.3f}   {e1_:8.3f}   {0.5*(e0_+e1_):7.3f}   {fp:13.4f}   {fs:14.4f}   {fp/fs:5.2f}")

    # ---- label isolation test
    print("\n== LABEL ISOLATION TEST ==", flush=True)
    r_a = simulate(d0, 0.1, hw, 0.3, 0.9); r_b = simulate(shuffled_labels(d0), 0.1, hw, 0.3, 0.9)
    same = all(np.array_equal(r_a["traj"][m], r_b["traj"][m]) for m in ADAPTIVE)
    print(f"all adaptive centroid trajectories identical after shuffling every evaluation/calibration label: {same}")
    print(f"(measured errors differ as expected: frozen {r_a['frozen'].mean()*100:.2f}% -> {r_b['frozen'].mean()*100:.2f}% with shuffled labels)")
    assert same, "controller depends on labels"

    # ---- tuning on q0 seeds 0..3 only
    print("\n== STEP SIZES (q0, tuning seeds only) ==", flush=True)
    tune = [make_data("q0", s, seed) for s in a.strengths for seed in range(a.tune_seeds)]
    best = None
    for eq in (0.1, 0.2, 0.3):
        for ea in (0.5, 0.9):
            rec = [recovery(simulate(d, p1, hw, eq, ea), m) for d in tune for p1 in P1S for m in ("moment+pi gated", "EM+pi gated")]
            sc = np.nanmedian(rec)
            if best is None or sc > best[0]: best = (sc, eq, ea)
    eq, ea = best[1], best[2]
    print(f"chosen eta_quiet={eq}, eta_alarm={ea} (tuning median recovery {best[0]:.2f})", flush=True)

    # ---- held-out experiments
    v3 = load_v3(); rows, runs_all, example, probes = [], [], {}, []
    print("\n== HELD-OUT RESULTS (seeds 100+; v4 = physical syndromes, controller sees features only) ==", flush=True)
    print(f"{'prof':4s} {'str':>3s} {'p1':>4s} {'gap pp':>6s} {'runs':>4s} | {'periodic':>8s} {'EM+pi':>6s} | {'EM+pi gated v4: median [IQR]':>30s} {'>=0.8':>6s} | {'v3':>5s} {'alarm%':>6s}", flush=True)
    for prof in ("q0", "q1", "q2"):
        for s in a.strengths:
            data = [make_data(prof, s, 100 + k) for k in range(a.test_seeds)]
            for d in data: probes.append((prof, s, *probe_detector(d, hw, d["seed"])))
            for p1 in P1S:
                R = [simulate(d, p1, hw, eq, ea) for d in data]
                for r in R: runs_all.append((prof, s, p1, r))
                gap = np.mean([(r["frozen"].mean() - r["oracle"].mean()) * 100 for r in R])
                af = np.mean([r["alarm_frac"]["EM+pi gated"] for r in R])
                med = {}
                for m in METHODS[1:-1]:
                    rec = np.array([recovery(r, m) for r in R]); fin = np.isfinite(rec)
                    q = np.percentile(rec[fin], [25, 50, 75]) if fin.any() else [np.nan] * 3
                    frac = np.mean(rec[fin] >= 0.8) if fin.any() else np.nan
                    rows.append((prof, s, p1, gap, m, q[1], q[0], q[2], frac, int(fin.sum()), af if m == "EM+pi gated" else ""))
                    med[m] = (q, frac, int(fin.sum()))
                q, frac, nr = med["EM+pi gated"]; v3v = v3.get((prof, s, p1, "EM+pi gated"))
                f = lambda x: f"{x:5.2f}" if np.isfinite(x) else "  n/a"
                print(f"{prof:4s} {s:3.0f} {p1:4.2f} {gap:6.2f} {nr:4d} | {f(med['periodic'][0][1]):>8s} {f(med['EM+pi'][0][1]):>6s} | "
                      f"{f(q[1])} [{f(q[0])} to {f(q[2])}]".ljust(30) + f"{f(frac):>8s} | {f(v3v) if v3v is not None else '  n/a':>5s} {af*100:6.1f}", flush=True)
                if (prof, s, p1) in (("q1", 4.0, 0.5), ("q1", 4.0, 0.1)): example[p1] = (data[0]["steps"], R[0])

    # ---- detector validation: healthy false alarms
    print("\n== DETECTOR VALIDATION ==", flush=True)
    print("healthy (no drift) false-alarm rate, frozen boundary, steps after the reference period:")
    for prof in ("q0", "q1", "q2"):
        n_al = n_st = n_run = 0
        for k in range(a.healthy_runs):
            d = make_data(prof, 1.0, 500 + k, fixed_t=0.0)
            al, _, _ = probe_detector(d, hw, 500 + k)
            n_al += al[K_REF:].sum(); n_st += len(al[K_REF:]); n_run += int(al[K_REF:].any())
        print(f"  {prof}: {n_al}/{n_st} steps alarmed ({100*n_al/n_st:.1f}%), runs with at least one false alarm: {n_run}/{a.healthy_runs}", flush=True)

    # ---- missed drift / delay on drifting data
    ev_n = ev_hit = qu_n = qu_fa = 0; delays = []; missed_onsets = 0
    for prof, s, al, ev, qu in probes:
        post = np.arange(len(al)) >= K_REF
        ev_n += (ev & post).sum(); ev_hit += (ev & al & post).sum(); qu_n += (qu & post).sum(); qu_fa += (qu & al & post).sum()
        for i in range(K_REF, len(ev)):
            if ev[i] and not ev[i - 1]:
                j = np.where(al[i:])[0]
                if len(j) and j[0] <= 3: delays.append(j[0])
                else: missed_onsets += 1
    print(f"drifting data (frozen boundary; event = actual flip rate > 2x its start value, quiet = < 1.25x), after the reference period:")
    print(f"  event steps alarmed: {ev_hit}/{ev_n} ({100*ev_hit/max(ev_n,1):.0f}%)   quiet steps falsely alarmed: {qu_fa}/{qu_n} ({100*qu_fa/max(qu_n,1):.1f}%)")
    print(f"  event onsets: {len(delays)} detected within 12 h (median delay {np.median(delays) if delays else float('nan'):.0f} steps of 4 h), {missed_onsets} missed")

    # ---- reference contamination
    print("reference-period contamination (drift already present in the first 24 h):")
    for tag, flag in (("clean reference", False), ("contaminated reference", True)):
        rec = np.array([recovery(r, "EM+pi gated") for _, _, _, r in runs_all if r["contaminated"] == flag])
        rec = rec[np.isfinite(rec)]
        print(f"  {tag:24s}: {len(rec):3d} runs with drift, median recovery {np.median(rec) if len(rec) else float('nan'):.2f}, "
              f"fraction >= 0.8: {np.mean(rec >= 0.8) if len(rec) else float('nan'):.2f}")

    with open("adaptive_boundary_v4.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["profile", "strength", "p_state1", "frozen_minus_oracle_pp", "method", "median_recovery", "q25", "q75",
                    "fraction_runs_ge_0.8", "n_runs_with_drift", "alarm_fraction_EMpi_gated", "eta_quiet", "eta_alarm"])
        for r in rows: w.writerow([*r, eq, ea])

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1, 2, figsize=(12, 4.2), sharey=True)
    for k, p1 in enumerate(P1S):
        if p1 not in example: continue
        steps, r = example[p1]; t = [x["t"] for x in steps]
        for m, kw in (("frozen", dict(lw=2)), ("periodic", dict(lw=1)), ("EM+pi", dict(lw=1.2)), ("EM+pi gated", dict(lw=2.2)), ("oracle", dict(ls="--", lw=1.2))):
            ax[k].plot(t, r[m] * 100, label=m, **kw)
        ax[k].axvspan(0, K_REF * 4, color="gray", alpha=0.15); ax[k].set_xlabel("hours")
        ax[k].set_title(f"q1, drift x4, stream {p1:.0%} |1> (held-out seed; gray = reference period)", fontsize=8)
    ax[0].set_ylabel("misassignment (%)"); ax[0].legend(fontsize=8)
    fig.tight_layout(); fig.savefig("adaptive_boundary_v4.png", dpi=150)
    print("\nwrote adaptive_boundary_v4.csv and adaptive_boundary_v4.png", flush=True)


if __name__ == "__main__":
    main()
