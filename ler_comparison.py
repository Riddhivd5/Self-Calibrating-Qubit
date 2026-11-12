"""
ler_comparison.py  --  closed-loop LOGICAL error rate of decision-boundary policies, built on adaptive_boundary_v5.py.

This script re-uses v5 unchanged: its Hardware physics (true Stim outcomes read through the deployed boundary with real
IQ dots, asymmetric state-conditional misreads), ControllerV5 alarm (fire rate only, reference recorded right after
calibration, ZTHR 3.0, REL_RISE 0.30, K_REF 6), em_step, the fixed pi estimated once from the first stream, the step sizes
(eta) tuned in v5 (read from adaptive_boundary_v5.csv), WIN = 1500 shots per window, P_PHYS = 0.001, d = 5.
v5 stops at misassignment and fire rate. This script adds what the poster reviewers asked for:
  * logical error rate, decoded from the same syndromes with a FIXED baseline PyMatching decoder (the decoder does not
    know about drift), with shot counts and 95% Wilson intervals
  * several drift trajectories (held-out seeds 200+, as in v5) with bootstrap intervals over seeds
  * an oracle arm and a periodic-recalibration sweep (12, 24, 48 h)
  * readout-only, physical-only and combined drift, controlled independently (physical error ramped by a Stim noise level)
  * detector scoring: onsets caught, false alarms on quiet windows, delay, alarmed fraction, per seed
  * small update batches and shifting |1> share
  * replay of the real IBM snapshots (held-out scoring) through the same loop
Arms: frozen | periodic_12h/24h/48h | oracle | moment (v1) | EM+pi (eta 0.3) | EM+pi fast (eta 0.9) | EM+pi fast, one-step lag |
gated (v5 alarm)
Label-free arms see only unlabelled IQ dots and syndrome features. Timeline per step as in v5: the boundary is updated from
the step's unlabelled stream (the gated arm first measures one alarm window at its old boundary), then a window is measured
at the updated boundary and decoded. That scores a boundary on the same window it was tuned on (offline re-assignment).
em_pi_fast_lag is the online case: its window is measured at the boundary it had BEFORE this step's data. Quote both.
em_pi_lag and gated_v5_lag are the same one-step-lag measurement for the fixed-eta and the gated policy, so the three policies
(always slow, always fast, gated) can be compared online.

Drift sources (the scenario class is printed in each summary heading):
  * stress test : hand-tuned v1.5 profiles q0/q1/q2 at --strength 4 (readout_*, mix*, batch*, both). Far stronger than the
                  drift measured on the device; kept for continuity and as a worst case.
  * fitted      : profiles refit on the 149 real snapshots (iq_generator_refit.py): fast jitter plus measured rare events and
                  a decay tail (refit_q0/q1/q2, refit_q1_noevents). --refit-strength multiplies the stochastic jitter only.
  * controlled  : a common-mode displacement of known size, in cloud sigma (iq_generator_controlled.py): step_q1 (step at one
                  third of the run) and slow_q1 (linear ramp reaching --shift-sigma at the end). No other readout drift.
  * real replay : the IBM snapshots themselves (real_q0/q1/q2).
  * physical    : readout fixed, physical error ramped (physical); "both" adds the ramp to the stress-test readout drift.
  * gating tests: quiet_q1 (controlled generator, no drift at all), physical_quiet_q1 (the same with the physical-error ramp),
                  mixshift_quiet_q1 and mixshift_step_q1 (the |1> share of the
                  unlabelled stream changes 0.3 -> 0.1 -> 0.5 by thirds of the run while pi stays at its first estimate).
                  --n-unl sets the number of unlabelled IQ points per update for the fitted and controlled scenarios.

Usage (repo root; needs adaptive_boundary_v5.py, adaptive_boundary.py, drift_framework.py, iq_generator.py,
real_drift_detector.py, data/ and adaptive_boundary_v5.csv):
    python ler_comparison.py --scenarios readout_q1 --seeds 8 --out-dir results/<new folder>
The fitted and controlled scenarios also need iq_generator_refit.py, iq_generator_events.py, iq_generator_controlled.py and
analysis/refit_results/refit_params.json.
Scenarios: readout_q0 readout_q1 readout_q2 mix10 mix50 physical both real_q0 real_q1 real_q2 batch<N>
           refit_q0 refit_q1 refit_q2 refit_q1_noevents step_q1 slow_q1 quiet_q1 mixshift_quiet_q1 mixshift_step_q1
           physical_quiet_q1
Flags: --d, --pphys (v5 etas and alarm thresholds were tuned at d=5, p=0.001 and are not retuned); --strength (stress tests);
       --refit-strength, --refit-hours, --refit-step (fitted); --shift-sigma (controlled); --n-unl; --phys-ramp; --batch-sizes;
       --no-detector; --force (outputs are never overwritten without it). run_config.json records the command and versions.
Outputs in --out-dir: ler_windows.csv, ler_summary.md, run_config.json, ler_<scenario>.png
"""
import argparse
import csv
import json
import os
import subprocess
import sys
import time

import numpy as np
import pymatching

import adaptive_boundary_v5 as v5
from adaptive_boundary import classify, misassign
from drift_framework import build_circuit

ARMS = ["frozen", "periodic_12h", "periodic_24h", "periodic_48h", "oracle", "moment_v1", "em_pi", "em_pi_fast", "em_pi_fast_lag", "gated_v5",
        "em_pi_lag", "gated_v5_lag"]
PERIODS = {"periodic_12h": 12.0, "periodic_24h": 24.0, "periodic_48h": 48.0}
TEST0 = 200  # held-out seeds, same as v5
GAP_MIN = 0.0005  # a frozen-vs-oracle gap below 0.05 percentage points of LER is treated as zero


# ------------------------------------------------------------------ stats
def wilson(k, n, z=1.96):
    p = k / n
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return max(0.0, c - h), min(1.0, c + h)


def read_etas(path="adaptive_boundary_v5.csv"):
    r = next(csv.DictReader(open(path)))
    return float(r["eta_quiet_v5alarm"]), float(r["eta_alarm_v5alarm"])


# ------------------------------------------------------------------ hardware (v5 physics, plus the logical observable)
class HW(v5.Hardware):
    def __init__(self, p_phys):
        self.circ = build_circuit(v5.D, p_readout=0.0, p_phys=p_phys)
        self.m2d = self.circ.compile_m2d_converter()
        self.lay = v5.Layout(self.circ)
        self.ones = np.ones(self.lay.n_anc)
        self.last_flip_rate = np.nan


def read_window(hw, true_out, idx, pool0, pool1, c0, c1):
    """Same flip model as v5.Hardware.syndromes, but also returns the logical observable flips."""
    misread0 = classify(pool0, c0, c1) == 1
    misread1 = classify(pool1, c0, c1) == 0
    flip = np.where(true_out, misread1[idx], misread0[idx])
    det, obs = hw.m2d.convert(measurements=true_out ^ flip, separate_observables=True)
    return det, obs[:, 0], float(flip.mean())


# ------------------------------------------------------------------ real IBM data in v5's data format
def make_real_data(q, data_dir, rep, n_unl=1500):
    from real_drift_detector import load_snapshots
    import datetime as dt
    snaps = load_snapshots(data_dir)
    ts = np.array([dt.datetime.fromisoformat(s[0].replace("Z", "+00:00")).timestamp() for s in snaps])
    hours = (ts - ts[0]) / 3600.0
    rng = np.random.default_rng(5000 + rep)
    steps, A_first = [], []
    for i, s in enumerate(snaps):
        z = [s[2][f"q{q}_state0"], s[2][f"q{q}_state1"]]
        A, B = [], []
        for st in (0, 1):
            p = np.random.default_rng(1000 + i).permutation(len(z[st]))   # same split every repetition
            h = len(z[st]) // 2
            A.append(z[st][p[:h]]); B.append(z[st][p[h:]])
        if i < 3:
            A_first.append(A)
        unl = {}
        for p1 in v5.P1S:
            n1 = rng.binomial(n_unl, p1)
            unl[p1] = np.r_[rng.choice(A[1], n1), rng.choice(A[0], n_unl - n1)]
        ev = (np.r_[B[0], B[1]], np.r_[np.zeros(len(B[0]), int), np.ones(len(B[1]), int)])
        cal = (np.r_[A[0], A[1]], np.r_[np.zeros(len(A[0]), int), np.ones(len(A[1]), int)])
        steps.append(dict(t=float(hours[i]), unl=unl, ev=ev, cal=cal, pool0=B[0], pool1=B[1]))
    c0 = np.concatenate([a[0] for a in A_first])
    c1 = np.concatenate([a[1] for a in A_first])
    f0, f1 = c0.mean(), c1.mean()
    sig2 = 0.5 * np.mean(np.r_[np.abs(c0 - f0) ** 2, np.abs(c1 - f1) ** 2])
    return dict(f0=f0, f1=f1, sig2=sig2, steps=steps, seed=rep)


# ------------------------------------------------------------------ fitted / controlled generators in v5's data format
def make_data_from(factory, seed, hours=168.0, step=4.0, n_unl=1500, n_eval=3000, n_cal=2000, n_pool=4000):
    """Same construction and draw order as v5.make_data, for any generator: factory() must return a NEW generator each call."""
    gen, genp = factory(), factory()
    iq, st = gen.generate_shots(n_shots=20000, t_hours=0)
    f0, f1 = iq[st == 0].mean(), iq[st == 1].mean()
    sig2 = 0.5 * np.mean(np.r_[np.abs(iq[st == 0] - f0) ** 2, np.abs(iq[st == 1] - f1) ** 2])
    steps = []
    for t in np.arange(0, hours + 1e-9, step):
        steps.append(dict(t=float(t),
                          unl={p1: gen.generate_shots(n_shots=n_unl, t_hours=t, p_state1=p1)[0] for p1 in v5.P1S},
                          ev=gen.generate_shots(n_shots=n_eval, t_hours=t, p_state1=0.5),
                          cal=gen.generate_shots(n_shots=n_cal, t_hours=t),
                          pool0=genp.generate_shots(n_shots=n_pool, t_hours=t, p_state1=0.0)[0],
                          pool1=genp.generate_shots(n_shots=n_pool, t_hours=t, p_state1=1.0)[0]))
    return dict(f0=f0, f1=f1, sig2=sig2, steps=steps, seed=seed)


def build_data(cfg, seed, rep, a):
    kind = cfg["kind"]
    if kind == "gen":
        return v5.make_data(cfg["prof"], cfg["strength"], seed, fixed_t=cfg.get("fixed_t"), n_unl=cfg.get("n_unl", 1500))
    if kind == "real":
        return make_real_data(cfg["q"], a.data_dir, rep, n_unl=cfg.get("n_unl", 1500))
    if kind == "refit":
        from iq_generator_refit import make_generator
        return make_data_from(lambda: make_generator(cfg["q"], seed=seed, events=cfg["events"], strength=a.refit_strength),
                              seed, hours=a.refit_hours, step=a.refit_step, n_unl=a.n_unl)
    if kind == "controlled":
        from iq_generator_controlled import make_controlled
        hours = 168.0
        shift = cfg.get("shift", a.shift_sigma)
        return make_data_from(lambda: make_controlled(cfg["q"], seed=seed, kind=cfg["shape"], shift_sigma=shift,
                                                      t_on=hours / 3, hours=hours), seed, hours=hours, step=4.0, n_unl=a.n_unl)
    raise ValueError(kind)


CLASS = {"gen": "STRESS TEST: hand-tuned v1.5 profile, far stronger than the drift measured on the device",
         "refit": "FITTED: profile refit on the 149 real snapshots",
         "controlled": "CONTROLLED: imposed common-mode displacement, no other readout drift",
         "real": "REAL REPLAY: the IBM snapshots"}


def scenario_class(name, cfg, a):
    if name == "physical":
        return "PHYSICAL ONLY: readout held at its calibration-time state, physical error ramped"
    if name == "physical_quiet_q1":
        return (f"PHYSICAL ONLY: controlled generator with no readout drift, physical error ramped x{a.phys_ramp:g}"
                + (f"; {a.n_unl} unlabelled IQ points per update" if a.n_unl != 1500 else ""))
    c = CLASS[cfg["kind"]]
    if cfg["kind"] == "gen":
        c += f" (profile {cfg['prof']}, strength x{cfg['strength']:g}" + (", plus a physical-error ramp)" if name == "both" else ")")
    if cfg["kind"] == "refit":
        c += f" (q{cfg['q'][-1]}, jitter x{a.refit_strength:g}, events {'on' if cfg['events'] else 'off'}, {a.refit_hours:g} h at {a.refit_step:g} h steps)"
    if cfg["kind"] == "controlled":
        sh = cfg.get("shift", a.shift_sigma)
        c = (c if sh else "QUIET: controlled generator with no drift at all") + (
            "" if not sh else f" ({cfg['shape']}: {sh:g} sigma along the centroid axis, "
            + ("applied at one third of the run)" if cfg["shape"] == "step" else "reached linearly at the end of the run)"))
    if callable(cfg["p1"]):
        c += "; |1> share of the unlabelled stream changes 0.3 -> 0.1 -> 0.5 by thirds of the run, pi fixed at its first estimate"
    if cfg["kind"] in ("refit", "controlled") and a.n_unl != 1500:
        c += f"; {a.n_unl} unlabelled IQ points per update"
    return c


# ------------------------------------------------------------------ one closed-loop run
def run(data, p1, hw0, hws, matcher, etas, phys_fn, seed):
    """Returns {arm: dict(k, n, p, flip, alarm)} per step."""
    f0, f1, sig2 = data["f0"], data["f1"], data["sig2"]
    w0 = f1 - f0
    p1_at = p1 if callable(p1) else (lambda i, n: p1)
    n_all = len(data["steps"])
    pi = float(np.clip(classify(data["steps"][0]["unl"][p1_at(0, n_all)], f0, f1).mean(), 0.02, 0.98))
    ctrl = v5.ControllerV5(v5.reference_windows(hw0, data, seed))
    S = {m: [f0, f1] for m in ARMS}
    mid, last_cal = (f0 + f1) / 2, {m: 0.0 for m in PERIODS}
    out = {m: dict(k=[], p=[], flip=[], fire=[]) for m in ARMS}
    alarms, n_steps = [], len(data["steps"])
    n_recal = {m: 0 for m in PERIODS}
    cal_shots = 0
    for si, sd in enumerate(data["steps"]):
        t, iq = sd["t"], sd["unl"][p1_at(si, n_all)]
        ciq, cst = sd["cal"]
        eiq, est = sd["ev"]
        hw = hws(phys_fn(si, n_steps))
        MB = {}  # boundary each arm MEASURES with this step (default: its updated state)
        base = 90_000 + 1000 * seed + si
        smp = hw.circ.compile_sampler(seed=base)
        rg = np.random.default_rng(base)
        true_out = smp.sample(v5.WIN)
        idx = rg.integers(0, len(sd["pool0"]), true_out.shape)
        # --- label-free arms
        mid = (1 - v5.ETA_FIXED) * mid + v5.ETA_FIXED * iq.mean()
        S["moment_v1"] = [mid - w0 / 2, mid + w0 / 2]
        for name, eta in (("em_pi", v5.ETA_FIXED), ("em_pi_fast", v5.ETA_FAST), ("em_pi_fast_lag", v5.ETA_FAST), ("gated_v5", None)):
            if name == "em_pi_fast_lag":  # one-step lag: measure at the boundary from BEFORE this step's data
                MB[name] = list(S[name])
            if name in ("em_pi", "gated_v5"):  # the same policies measured with one-step lag
                MB[name + "_lag"] = list(S[name])
            if name == "gated_v5":  # one alarm window measured at the OLD boundary, features only
                smp_a = hw.circ.compile_sampler(seed=base + 500_000)
                rg_a = np.random.default_rng(base + 500_000)
                to_a = smp_a.sample(v5.WIN)
                id_a = rg_a.integers(0, len(sd["pool0"]), to_a.shape)
                det_a, _, _ = read_window(hw, to_a, id_a, sd["pool0"], sd["pool1"], *S[name])
                a = ctrl.alarm(*hw.features(det_a))
                alarms.append(int(a))
                eta = etas[1] if a else etas[0]
            n0, n1 = v5.em_step(iq, S[name][0], S[name][1], pi, sig2)
            S[name] = [(1 - eta) * S[name][0] + eta * n0, (1 - eta) * S[name][1] + eta * n1]
        S["em_pi_lag"], S["gated_v5_lag"] = S["em_pi"], S["gated_v5"]
        # --- labelled arms
        o0, o1 = ciq[cst == 0].mean(), ciq[cst == 1].mean()
        for m, per in PERIODS.items():
            if t - last_cal[m] >= per - 1e-9:
                S[m] = [o0, o1]
                last_cal[m] = t
                n_recal[m] += 1
        cal_shots = len(cst)
        S["oracle"] = [o0, o1]
        # --- measure and decode one window per arm at its (updated) boundary; same true outcomes for every arm
        for m in ARMS:
            bnd = MB.get(m, S[m])
            det, obs, flip = read_window(hw, true_out, idx, sd["pool0"], sd["pool1"], *bnd)
            pred = np.asarray(matcher.decode_batch(det)).reshape(-1)
            out[m]["k"].append(int(np.sum(pred != obs)))
            out[m]["p"].append(misassign(eiq, est, *bnd))
            out[m]["flip"].append(flip)
            out[m]["fire"].append(float(det.mean()))
    res = {m: {k: np.array(v) for k, v in d.items()} for m, d in out.items()}
    res["_alarm"] = np.array(alarms)
    res["_recal"] = dict(n_recal, oracle=n_steps)
    res["_cal_shots"] = cal_shots
    res["_t"] = np.array([sd["t"] for sd in data["steps"]])
    return res


def design_matcher(data):
    s0 = data["steps"][0]
    p_design = max(misassign(*s0["ev"], data["f0"], data["f1"]), 1e-3)
    circ = build_circuit(v5.D, p_readout=p_design, p_phys=v5.P_PHYS)
    return pymatching.Matching.from_detector_error_model(circ.detector_error_model(decompose_errors=True))


# ------------------------------------------------------------------ scenarios
def scenarios(a):
    ramp = lambda i, n: v5.P_PHYS * (1 + (a.phys_ramp - 1) * float(np.clip((i - n / 3) / (n / 3), 0, 1)))
    flat = lambda i, n: v5.P_PHYS
    S = {}
    for q in ("q0", "q1", "q2"):
        S[f"readout_{q}"] = dict(kind="gen", prof=q, strength=a.strength, p1=0.3, phys=flat)
    S["mix10"] = dict(kind="gen", prof="q1", strength=a.strength, p1=0.1, phys=flat)
    S["mix50"] = dict(kind="gen", prof="q1", strength=a.strength, p1=0.5, phys=flat)
    S["physical"] = dict(kind="gen", prof="q1", strength=1.0, p1=0.3, phys=ramp, fixed_t=0.0)
    S["both"] = dict(kind="gen", prof="q1", strength=a.strength, p1=0.3, phys=ramp)
    for q in (0, 1, 2):
        S[f"real_q{q}"] = dict(kind="real", q=q, p1=0.3, phys=flat)
    for nb in a.batch_sizes:
        S[f"batch{nb}"] = dict(kind="gen", prof="q1", strength=a.strength, p1=0.3, phys=flat, n_unl=nb)
    for q in ("q0", "q1", "q2"):
        S[f"refit_{q}"] = dict(kind="refit", q=q, events=True, p1=0.3, phys=flat)
    S["refit_q1_noevents"] = dict(kind="refit", q="q1", events=False, p1=0.3, phys=flat)
    S["step_q1"] = dict(kind="controlled", q="q1", shape="step", p1=0.3, phys=flat)
    S["slow_q1"] = dict(kind="controlled", q="q1", shape="slow", p1=0.3, phys=flat)
    mix = lambda i, n: (0.3, 0.1, 0.5)[min(3 * i // n, 2)]
    S["quiet_q1"] = dict(kind="controlled", q="q1", shape="step", shift=0.0, p1=0.3, phys=flat)
    S["mixshift_quiet_q1"] = dict(kind="controlled", q="q1", shape="step", shift=0.0, p1=mix, phys=flat)
    S["mixshift_step_q1"] = dict(kind="controlled", q="q1", shape="step", p1=mix, phys=flat)
    S["physical_quiet_q1"] = dict(kind="controlled", q="q1", shape="step", shift=0.0, p1=0.3, phys=ramp)
    return S


def detector_stats(data, hw0, seed):
    al, ev, qu = v5.probe(data, hw0, seed, "v5")
    post = np.arange(len(al)) >= v5.K_REF
    onsets = [i for i in range(v5.K_REF, len(ev)) if ev[i] and not ev[i - 1]]
    delays = []
    for i in onsets:
        hit = np.where(al[i:i + 4])[0]
        delays.append(int(hit[0]) if len(hit) else None)
    return dict(onsets=len(onsets), caught=sum(d is not None for d in delays), delays=[d for d in delays if d is not None],
                ev_n=int((ev & post).sum()), ev_alarmed=int((ev & al & post).sum()), q_n=int((qu & post).sum()),
                q_false=int((qu & al & post).sum()))


def gap_resolvable(runs, rng, boot=2000):
    """Gap is reported as real only if it is >= GAP_MIN and its bootstrap (over runs) lower bound is above zero."""
    kf, nf = pooled(runs, "frozen")
    ko, _ = pooled(runs, "oracle")
    if (kf - ko) / nf < GAP_MIN:
        return False
    if len(runs) < 2:
        return True
    g = []
    for _ in range(boot):
        ix = rng.integers(0, len(runs), len(runs))
        g.append(sum(runs[i]["frozen"]["k"].sum() - runs[i]["oracle"]["k"].sum() for i in ix))
    return bool(np.percentile(g, 2.5) > 0)


def pooled(runs, arm):
    k = sum(r[arm]["k"].sum() for r in runs)
    n = sum(len(r[arm]["k"]) * v5.WIN for r in runs)
    return int(k), int(n)


def recovery_stats(runs, arm, rng, boot=2000):
    kf, nf = pooled(runs, "frozen")
    ko, _ = pooled(runs, "oracle")
    ka, _ = pooled(runs, arm)
    gap = kf - ko
    per = []
    for r in runs:
        d = r["frozen"]["k"].sum() - r["oracle"]["k"].sum()
        per.append(np.nan if d / (len(r["frozen"]["k"]) * v5.WIN) < GAP_MIN else (r["frozen"]["k"].sum() - r[arm]["k"].sum()) / d)
    per = np.array(per)
    fin = np.isfinite(per)
    rec = (kf - ka) / gap if gap / nf >= GAP_MIN else np.nan
    ci = (np.nan, np.nan)
    if np.isfinite(rec) and len(runs) > 1:
        bs = []
        for _ in range(boot):
            ix = rng.integers(0, len(runs), len(runs))
            f = sum(runs[i]["frozen"]["k"].sum() for i in ix); o = sum(runs[i]["oracle"]["k"].sum() for i in ix)
            x = sum(runs[i][arm]["k"].sum() for i in ix)
            if f - o > 0:
                bs.append((f - x) / (f - o))
        if bs:
            ci = tuple(np.percentile(bs, [2.5, 97.5]))
    q = np.percentile(per[fin], [25, 50, 75]) if fin.any() else [np.nan] * 3
    return rec, ci, q, (float(np.mean(per[fin] >= 0.8)) if fin.any() else np.nan), int(fin.sum())


BLOCK = 6  # windows per resampling block (about one day at the simulated 4 h spacing)


def boot_samples(runs, shared_traj, rng, boot=2000):
    """Bootstrap pooled LER per arm with the SAME resample for every arm (so differences are paired).
    Independent trajectories (generator scenarios, one per seed): resample runs. One shared trajectory (real data, or a single
    run): circular block bootstrap over windows, same blocks for every run, because windows in a drifting series are not independent."""
    K = {m: np.array([r[m]["k"] for r in runs], float) for m in ARMS}
    R, T = K["frozen"].shape
    out = {m: np.empty(boot) for m in ARMS}
    for b in range(boot):
        if shared_traj or R < 2:
            starts = rng.integers(0, T, int(np.ceil(T / BLOCK)))
            ix = np.concatenate([(s0 + np.arange(BLOCK)) % T for s0 in starts])[:T]
            for m in ARMS:
                out[m][b] = K[m][:, ix].sum() / (R * T * v5.WIN)
        else:
            ix = rng.integers(0, R, R)
            for m in ARMS:
                out[m][b] = K[m][ix].sum() / (R * T * v5.WIN)
    return out


def summarise(name, cfg, runs, dstats, a, rng):
    shared = cfg["kind"] == "real" or len(runs) < 2
    L = [f"### {name}", f"{scenario_class(name, cfg, a)}.", "", f"{len(runs)} run(s); {len(runs[0]['_t'])} windows per run, {v5.WIN} shots per window, d={v5.D}, "
         f"physical error {v5.P_PHYS}" + (f" ramped x{a.phys_ramp:g}" if cfg["phys"].__name__ == "<lambda>" and name in ("physical", "both") else "") + ".", "",
         "| arm | pooled LER [95% Wilson CI, counts shots only] | [95% CI resampling " + ("window blocks, one shared trajectory" if shared else "runs") + "] | shots | mean accuracy | gap recovered, pooled [95% bootstrap CI over runs] | median per run [IQR] | runs >= 0.8 |",
         "|---|---|---|---|---|---|---|---|"]
    kf, nf = pooled(runs, "frozen"); ko, _ = pooled(runs, "oracle")
    resolvable = gap_resolvable(runs, rng)
    bs = boot_samples(runs, shared, rng)
    for m in ARMS:
        k, n = pooled(runs, m); lo, hi = wilson(k, n)
        acc = 100 * (1 - np.mean([r[m]["p"].mean() for r in runs]))
        if m == "frozen" or not resolvable:
            rs = "-"; md = "-"; ge = "-"
        else:
            rec, ci, q, fr, nfin = recovery_stats(runs, m, rng)
            rs = f"{rec:+.2f} [{ci[0]:+.2f}, {ci[1]:+.2f}]" if np.isfinite(ci[0]) else (f"{rec:+.2f}" if np.isfinite(rec) else "-")
            md = f"{q[1]:+.2f} [{q[0]:+.2f}, {q[2]:+.2f}]"; ge = f"{fr:.2f} ({nfin})"
        bl, bh = np.percentile(bs[m], [2.5, 97.5])
        L.append(f"| {m} | {k / n:.5f} [{lo:.5f}, {hi:.5f}] | [{bl:.5f}, {bh:.5f}] | {n} | {acc:.2f}% | {rs} | {md} | {ge} |")
    L.append("")
    L.append(f"frozen-vs-oracle LER gap: {100 * (kf - ko) / nf:.3f} percentage points"
             + ("" if resolvable else "  (not distinguishable from zero, recovery fractions are not reported)"))
    if dstats:
        on = sum(d["onsets"] for d in dstats); ca = sum(d["caught"] for d in dstats)
        dl = [x for d in dstats for x in d["delays"]]
        L.append(f"detector (v5 alarm on the frozen boundary, per window of {v5.WIN} shots): onsets caught within 4 windows {ca}/{on}; "
                 f"event windows alarmed {sum(d['ev_alarmed'] for d in dstats)}/{sum(d['ev_n'] for d in dstats)}; "
                 f"false alarms on quiet windows {sum(d['q_false'] for d in dstats)}/{sum(d['q_n'] for d in dstats)}; "
                 f"delay median {np.median(dl) if dl else float('nan'):.0f} window(s); the alarm decides at the end of a window, so latency is at most "
                 f"{((np.median(dl) if dl else float('nan')) + 1) * v5.WIN:.0f} shots = {((np.median(dl) if dl else float('nan')) + 1) * v5.WIN * v5.D:.0f} syndrome rounds "
                 f"(d={v5.D}); delay inside a window is not resolved (one window per simulated time step or per real snapshot). "
                 "Event = flip rate above 2x the starting value, quiet = below 1.25x; windows in between are NOT scored here. "
                 "detector_scoring.py scores every window, with the truth defined by the injected drift, and sweeps the window size")
    if cfg["kind"] == "real":
        L.append("")
        L.append("Real-data scenario: one 15.6-day trajectory replayed repeatedly (runs differ only in which unlabelled IQ points are drawn). "
                 "The block-bootstrap interval describes uncertainty within this trajectory; it is not a set of independent real-world trajectories.")
    L.append("")
    L.append("Paired LER differences (percentage points, 95% CI from the same resamples; negative = first arm better):")
    for x, y in (("em_pi_fast", "frozen"), ("em_pi_fast", "oracle"), ("gated_v5", "em_pi_fast"), ("em_pi_fast_lag", "em_pi_fast"),
                 ("periodic_24h", "em_pi_fast"), ("em_pi", "em_pi_fast"), ("gated_v5", "em_pi"),
                 ("gated_v5_lag", "em_pi_fast_lag"), ("gated_v5_lag", "em_pi_lag"), ("em_pi_lag", "em_pi_fast_lag")):
        d = 100 * (bs[x] - bs[y]); L.append(f"- {x} - {y}: {100 * (np.mean(bs[x]) - np.mean(bs[y])):+.3f} [{np.percentile(d, 2.5):+.3f}, {np.percentile(d, 97.5):+.3f}]")
    nst = len(runs[0]["_t"]); cs = runs[0]["_cal_shots"]
    L.append("")
    L.append(f"Labelled calibration cost per run ({nst} windows, {cs} labelled shots per recalibration; these are readout calibration shots, not QEC shots): "
             + "; ".join(f"{m} {np.mean([r['_recal'][m] for r in runs]):.1f} recalibration(s) = {np.mean([r['_recal'][m] for r in runs]) * cs:.0f} labelled shots "
                         f"({100 * np.mean([r['_recal'][m] for r in runs]) * cs / (nst * v5.WIN):.1f}% of the QEC shots)" for m in list(PERIODS) + ["oracle"])
             + ". Downtime per recalibration is not modelled; oracle recalibrates every window and is an upper bound, not deployable. Label-free arms need none.")
    al = np.concatenate([r["_alarm"] for r in runs])
    L.append(f"gated arm alarm fraction over all windows: {al.mean():.2f}")
    L.append("")
    return "\n".join(L)


def plot(name, runs, path, a):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    r = runs[0]
    fig, ax = plt.subplots(2, 1, figsize=(9, 6), sharex=True)
    for m in ARMS:
        if m in ("moment_v1", "periodic_12h", "periodic_48h"):
            continue
        k = r[m]["k"]
        ler = k / v5.WIN
        ax[0].plot(r["_t"], ler * 100, lw=1.1, label=m)
        ax[1].plot(r["_t"], r[m]["p"] * 100, lw=1.1, label=m)
    lo, hi = zip(*[wilson(int(x), v5.WIN) for x in r["frozen"]["k"]])
    ax[0].fill_between(r["_t"], np.array(lo) * 100, np.array(hi) * 100, alpha=0.12, color="C0")
    ax[0].set_ylabel(f"LER %  ({v5.WIN} shots/window; band = frozen 95% CI)")
    ax[1].set_ylabel("misassignment %")
    ax[1].set_xlabel("hours")
    ax[0].set_title(f"{name}, first run (d={v5.D})")
    ax[0].legend(fontsize=7, ncol=3)
    fig.tight_layout(); fig.savefig(path, dpi=140); plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scenarios", nargs="+", default=["readout_q1"])
    ap.add_argument("--seeds", type=int, default=8)
    ap.add_argument("--strength", type=float, default=4.0)
    ap.add_argument("--phys-ramp", type=float, default=3.0)
    ap.add_argument("--refit-strength", type=float, default=1.0, help="fitted scenarios: multiplier on the stochastic jitter only (1 = as fitted; events unchanged)")
    ap.add_argument("--refit-hours", type=float, default=336.0, help="fitted scenarios: run length in hours")
    ap.add_argument("--refit-step", type=float, default=2.0, help="fitted scenarios: hours between windows (real median gap is 2.56 h)")
    ap.add_argument("--shift-sigma", type=float, default=1.0, help="controlled scenarios: displacement in along-axis cloud sigma")
    ap.add_argument("--n-unl", type=int, default=1500, help="fitted and controlled scenarios: unlabelled IQ points per update")
    ap.add_argument("--batch-sizes", nargs="*", type=int, default=[100, 300])
    ap.add_argument("--data-dir", default="data")
    ap.add_argument("--out-dir", default=".")
    ap.add_argument("--no-detector", action="store_true")
    ap.add_argument("--d", type=int, default=5, help="code distance (v5 etas and alarm thresholds were tuned at d=5, p=0.001, not retuned)")
    ap.add_argument("--pphys", type=float, default=0.001, help="physical error rate")
    ap.add_argument("--force", action="store_true", help="allow overwriting existing outputs in --out-dir")
    a = ap.parse_args()
    v5.D, v5.P_PHYS = a.d, a.pphys
    os.makedirs(a.out_dir, exist_ok=True)
    outs = ["ler_windows.csv", "ler_summary.md", "run_config.json"] + [f"ler_{n}.png" for n in a.scenarios]
    clash = [f for f in outs if os.path.exists(os.path.join(a.out_dir, f))]
    if clash and not a.force:
        sys.exit(f"refusing to overwrite {clash} in {a.out_dir}; use a new --out-dir or pass --force")
    try:
        commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    except Exception:
        commit = ""
    import stim
    json.dump(dict(args=vars(a), git_commit=commit, time=time.strftime("%Y-%m-%d %H:%M:%S"), numpy=np.__version__,
                   stim=stim.__version__, pymatching=pymatching.__version__, cmd=" ".join(sys.argv)),
              open(os.path.join(a.out_dir, "run_config.json"), "w"), indent=1)
    etas = read_etas()
    rng = np.random.default_rng(1)
    cache = {}
    hws = lambda pp: cache.setdefault(round(pp, 5), HW(pp))
    hw0 = hws(v5.P_PHYS)
    S = scenarios(a)
    rows, md = [], [f"etas used (from adaptive_boundary_v5.csv): quiet {etas[0]}, alarm {etas[1]}; d={a.d}, physical error {a.pphys}"
                    + ("" if (a.d, a.pphys) == (5, 0.001) else "  (NOTE: etas and the v5 alarm thresholds were tuned at d=5, p=0.001 and are NOT retuned here)") + "\n"]
    for name in a.scenarios:
        cfg = S[name]
        runs, dstats = [], []
        for k in range(a.seeds):
            seed = TEST0 + k
            data = build_data(cfg, seed, k, a)
            matcher = design_matcher(data)
            r = run(data, cfg["p1"], hw0, hws, matcher, etas, cfg["phys"], seed)
            runs.append(r)
            if not a.no_detector and name not in ("physical", "both"):
                dstats.append(detector_stats(data, hw0, seed))
            for m in ARMS:
                for i in range(len(r["_t"])):
                    rows.append(dict(scenario=name, d=a.d, pphys=a.pphys, run=k, arm=m, step=i, t=r["_t"][i], errors=int(r[m]["k"][i]),
                                     shots=v5.WIN, ler=r[m]["k"][i] / v5.WIN, misassign=r[m]["p"][i], flip=r[m]["flip"][i],
                                     gated_alarm=int(r["_alarm"][i]) if m in ("gated_v5", "gated_v5_lag") else ""))
            print(f"  {name} run {k + 1}/{a.seeds} done", flush=True)
        text = summarise(name, cfg, runs, dstats, a, rng)
        print(text, flush=True)
        md.append(text)
        plot(name, runs, os.path.join(a.out_dir, f"ler_{name}.png"), a)
    with open(os.path.join(a.out_dir, "ler_windows.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)
    open(os.path.join(a.out_dir, "ler_summary.md"), "w").write("\n".join(md) + "\n")


if __name__ == "__main__":
    main()
