"""
v4_reference_test.py -- does taking the healthy reference right after calibration (t=0 state) fix missed onsets
and keep false alarms low, compared with the in-run 24 h reference used in v4?

In v4 the reference is the first 6 detector windows of the run, one per 4 h time point, so drift inside those 24 h
contaminates it. A real detector window takes milliseconds, so the system can record its reference immediately
after a labelled calibration. Here the 'calibration-time reference' = 6 independent windows from the t=0 state with
the freshly calibrated boundary. The detector series itself is unchanged (same seeds as v4_diagnostics.py).

Alarm rules compared: A (either feature) and D (fire rate only), each with the in-run and the calibration-time reference.
Needs adaptive_boundary_v4.py. Usage: python v4_reference_test.py   (about 10 minutes)
"""
import numpy as np
from adaptive_boundary_v4 import WIN, K_REF, Hardware, make_data

hw = Hardware()


def windows(d, seed, steps_idx=None, n_ref=0):
    rng = np.random.default_rng(seed); hw.start(30_000 + seed); F, T, L = [], [], []
    for sd in d["steps"]:
        f, t = hw.features(hw.syndromes(sd["pool0"], sd["pool1"], d["f0"], d["f1"], rng)); F.append(f); T.append(t); L.append(hw.last_flip_rate)
    rng = np.random.default_rng(seed + 99_000); hw.start(60_000 + seed); RF, RT = [], []
    s0 = d["steps"][0]                                                    # t=0 state, fresh calibration
    for _ in range(n_ref):
        f, t = hw.features(hw.syndromes(s0["pool0"], s0["pool1"], d["f0"], d["f1"], rng)); RF.append(f); RT.append(t)
    return np.array(F), np.array(T), np.array(L), np.array(RF), np.array(RT)


def alarms(F, T, RF, RT, feats, z=3.0, rise=0.30):
    def hit(x, r):
        m, s = np.mean(r), max(np.std(r), 1e-4 * abs(np.mean(r)))
        return ((x - m) / s > z) & (x / m - 1 > rise)
    h = hit(F, RF) if feats == "f" else hit(F, RF) | hit(T, RT)
    return h


healthy = [(p, *windows(make_data(p, 1.0, 500 + k, fixed_t=0.0), 500 + k, n_ref=K_REF)) for p in ("q0", "q1", "q2") for k in range(30)]
drift = [(p, s, 100 + k, *windows(make_data(p, s, 100 + k), 100 + k, n_ref=K_REF)) for p in ("q0", "q1", "q2") for s in (1.0, 4.0) for k in range(8)]

print("                                   | healthy false-alarm steps % (q0 / q1 / q2) | events alarmed % (steps 6+) | onsets caught <=12h (6+): all / contaminated-reference runs / clean-reference runs")
for rname, feats in (("A either feature", "ft"), ("D fire rate only", "f")):
    for ref_kind in ("in-run reference (v4)", "calibration-time reference"):
        fa = {}
        for p, F, T, L, RF, RT in healthy:
            if ref_kind.startswith("in-run"): a = alarms(F, T, F[:K_REF], T[:K_REF], feats); a[:K_REF] = False
            else: a = alarms(F, T, RF, RT, feats)
            n, c = fa.get(p, (0, 0)); fa[p] = (n + len(a[K_REF:]), c + a[K_REF:].sum())
        evN = evH = 0; on = {"all": [0, 0], "con": [0, 0], "cle": [0, 0]}
        for p, s, seed, F, T, L, RF, RT in drift:
            if ref_kind.startswith("in-run"): a = alarms(F, T, F[:K_REF], T[:K_REF], feats); a[:K_REF] = False
            else: a = alarms(F, T, RF, RT, feats)
            base = max(L[0], 0.005); ev = L > 2 * base; contam = L[:K_REF].max() > 2 * base
            post = np.arange(len(F)) >= K_REF
            evN += (ev & post).sum(); evH += (ev & a & post).sum()
            for i in range(K_REF, len(ev)):
                if ev[i] and not ev[i - 1]:
                    got = bool(a[i:i + 4].any())
                    for k in ("all", "con" if contam else "cle"): on[k][0] += got; on[k][1] += 1
        print(f"{rname:17s} {ref_kind:28s} | {100*fa['q0'][1]/fa['q0'][0]:5.2f} / {100*fa['q1'][1]/fa['q1'][0]:5.2f} / {100*fa['q2'][1]/fa['q2'][0]:5.2f}"
              f"            | {100*evH/evN:5.1f}                       | {on['all'][0]}/{on['all'][1]}   {on['con'][0]}/{on['con'][1]}   {on['cle'][0]}/{on['cle'][1]}", flush=True)
