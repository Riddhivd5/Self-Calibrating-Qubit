"""
v4_diagnostics.py  -- investigates the four open issues of adaptive_boundary_v4.py (v4 itself is not modified).

 1. Does the Hardware model map Stim measurement bits to the right IQ cloud?  (synthetic pools with known misread rates)
 2. Why do the physical and the symmetric-flip models disagree under asymmetric errors? (stream-weighted flip rate)
 3. q2 healthy false alarms: which feature triggers them, and which alarm rule fixes them without losing events?
 4. Which drift onsets are missed, and what do they have in common?

Usage: python v4_diagnostics.py      (about 12 minutes)       needs adaptive_boundary_v4.py and its dependencies
"""
import numpy as np
from adaptive_boundary_v4 import (WIN, K_REF, P_PHYS, D, Hardware, classify, make_data, misassign, build_circuit, sample_window)

hw = Hardware()
C0, C1 = 0.0 + 0j, 1.0 + 0j                       # a boundary at 0.5 on the real axis


def synth_pools(e0, e1, n=20000):
    """pool0: fraction e0 of dots land on the '1' side; pool1: fraction e1 land on the '0' side."""
    p0 = np.where(np.arange(n) < int(e0 * n), 0.8, 0.0).astype(complex)
    p1 = np.where(np.arange(n) < int(e1 * n), 0.2, 1.0).astype(complex)
    return p0, p1


# ============================================================ 1. mapping tests
print("=== 1. STATE-TO-IQ MAPPING TESTS (synthetic pools with known misread rates) ===")
rng = np.random.default_rng(0)
p0, p1 = synth_pools(0.0, 0.0)
hw.start(77); det_a = hw.syndromes(p0, p1, C0, C1, rng)
true = hw.circ.compile_sampler(seed=77).sample(WIN)
det_b = hw.m2d.convert(measurements=true, separate_observables=False)
print(f"T1 perfect readout: detection events identical to noiseless Stim conversion: {np.array_equal(det_a, det_b)}")
for e0, e1, tag in ((0.30, 0.0, "only prepared-0 outcomes can be misread"), (0.0, 0.50, "only prepared-1 outcomes can be misread")):
    p0, p1 = synth_pools(e0, e1); hw.start(78)
    hw.syndromes(p0, p1, C0, C1, rng); fr = hw.last_flip_rate
    true = hw.circ.compile_sampler(seed=78).sample(WIN)
    exp = e0 * (1 - true.mean()) + e1 * true.mean()
    wrong = e1 * (1 - true.mean()) + e0 * true.mean()           # what you would get if the pools were swapped
    print(f"T2 e0={e0:.2f}, e1={e1:.2f} ({tag}): measured flip rate {fr:.4f}, expected {exp:.4f}, if pools were swapped {wrong:.4f}")
e = 0.02; p0, p1 = synth_pools(e, e); hw.start(79)
fp = np.mean([hw.syndromes(p0, p1, C0, C1, rng).mean() for _ in range(4)])
fs = sample_window(build_circuit(D, p_readout=e, p_phys=P_PHYS), 6000, seed=3)[0].mean()
print(f"T3 symmetric 2% readout error: fire rate physical model {fp:.4f} vs symmetric Stim circuit {fs:.4f}  (ratio {fp/fs:.3f})")
true = hw.circ.compile_sampler(seed=5).sample(WIN)
print(f"T4 fraction of TRUE outcomes equal to 1 in this circuit: overall {true.mean():.3f}; "
      f"first 120 measurements (24 ancillas x 5 rounds, assumed order) {true[:, :120].mean():.3f}; last 25 (data qubits) {true[:, 120:].mean():.3f}")

# ============================================================ 2. symmetric vs physical
print("\n=== 2. PHYSICAL vs SYMMETRIC MODEL: is the difference just how many of the outcomes are 1s? ===")
d0 = make_data("q1", 4.0, 100); pi_s = true.mean()
rows = []
for k, s in enumerate(d0["steps"]):
    e0_ = np.mean(classify(s["pool0"], d0["f0"], d0["f1"]) == 1); e1_ = np.mean(classify(s["pool1"], d0["f0"], d0["f1"]) == 0)
    rows.append((0.5 * (e0_ + e1_), k, e0_, e1_))
rows.sort()
pick = [rows[i] for i in (5, 20, 35, 41)] + [r for r in rows if abs(r[2] - r[3]) > 0.5][:1]
print(" step   e0     e1    mean(e0,e1)  stream flip rate (actual / predicted)   fire: physical | symmetric@mean(e0,e1) | symmetric@stream flip rate")
hw.start(5); rng = np.random.default_rng(1)
for _, k, e0_, e1_ in pick:
    s = d0["steps"][k]
    fp = np.mean([hw.syndromes(s["pool0"], s["pool1"], d0["f0"], d0["f1"], rng).mean() for _ in range(3)]); fr = hw.last_flip_rate
    f_mean = sample_window(build_circuit(D, p_readout=0.5 * (e0_ + e1_), p_phys=P_PHYS), 6000, seed=3)[0].mean()
    f_str = sample_window(build_circuit(D, p_readout=fr, p_phys=P_PHYS), 6000, seed=3)[0].mean()
    print(f" {k:3d}  {e0_:5.3f}  {e1_:5.3f}   {0.5*(e0_+e1_):6.3f}        {fr:6.3f} / {e0_*(1-pi_s)+e1_*pi_s:6.3f}"
          f"                {fp:6.4f} | {f_mean:6.4f} (x{fp/f_mean:4.2f}) | {f_str:6.4f} (x{fp/f_str:4.2f})")

# ============================================================ 3 & 4. detector rules and missed onsets
print("\n=== collecting syndrome feature traces (healthy and drifting) ===", flush=True)


def trace(d, seed):
    rng = np.random.default_rng(seed); hw.start(30_000 + seed); F, T, L = [], [], []
    for sd in d["steps"]:
        f, t = hw.features(hw.syndromes(sd["pool0"], sd["pool1"], d["f0"], d["f1"], rng)); F.append(f); T.append(t); L.append(hw.last_flip_rate)
    return np.array(F), np.array(T), np.array(L)


healthy = [(p, *trace(make_data(p, 1.0, 500 + k, fixed_t=0.0), 500 + k)) for p in ("q0", "q1", "q2") for k in range(30)]
drift = [(p, s, 100 + k, *trace(make_data(p, s, 100 + k), 100 + k)) for p in ("q0", "q1", "q2") for s in (1.0, 4.0) for k in range(8)]


def rule(F, T, rise=0.30, mode="or", consec=1, feats="ft", kref=K_REF, z=3.0):
    def hit(x):
        m, s = np.mean(x[:kref]), max(np.std(x[:kref]), 1e-4 * abs(np.mean(x[:kref])))
        h = np.zeros(len(x), bool); h[kref:] = ((x[kref:] - m) / s > z) & (x[kref:] / m - 1 > rise); return h
    hs = [hit(F)] if feats == "f" else [hit(F), hit(T)]
    h = hs[0] if len(hs) == 1 else (hs[0] | hs[1] if mode == "or" else hs[0] & hs[1])
    out = h.copy()
    for j in range(1, consec): out[j:] &= h[:-j]; out[:j] = False
    return out


RULES = {"A  current (either feature, 30% rise, 1 window)": dict(),
         "B  both features must rise": dict(mode="and"),
         "C  2 consecutive windows": dict(consec=2),
         "D  fire rate only": dict(feats="f"),
         "E  50% rise instead of 30%": dict(rise=0.5),
         "F  both features, 2 consecutive": dict(mode="and", consec=2),
         "G  reference of 10 windows": dict(kref=10)}


def onsets(ev):
    return [i for i in range(K_REF, len(ev)) if ev[i] and not ev[i - 1]]


print("\n=== 3. ALARM RULES (healthy: false alarms; drifting: events caught) ===")
print(f"{'rule':50s} | healthy false-alarm steps %  (q0 / q1 / q2)  runs>=1 of 30 (q2) | events alarmed % (all / q0+q1) | onsets caught <=12h  (all / q0+q1) | median delay")
for name, kw in RULES.items():
    fa = {}; runs_q2 = 0
    for p, F, T, L in healthy:
        a = rule(F, T, **kw)[K_REF:]; n, c = fa.get(p, (0, 0)); fa[p] = (n + len(a), c + a.sum())
        if p == "q2": runs_q2 += int(a.any())
    evN = evH = evN2 = evH2 = onN = onH = onN2 = onH2 = 0; delays = []
    for p, s, seed, F, T, L in drift:
        al = rule(F, T, **kw); base = max(L[0], 0.005); ev = L > 2 * base; post = np.arange(len(F)) >= K_REF
        evN += (ev & post).sum(); evH += (ev & al & post).sum()
        if p != "q2": evN2 += (ev & post).sum(); evH2 += (ev & al & post).sum()
        for i in onsets(ev):
            j = np.where(al[i:i + 4])[0]; onN += 1; onN2 += p != "q2"
            if len(j): onH += 1; onH2 += p != "q2"; delays.append(j[0])
    print(f"{name:50s} | {100*fa['q0'][1]/fa['q0'][0]:5.2f} / {100*fa['q1'][1]/fa['q1'][0]:5.2f} / {100*fa['q2'][1]/fa['q2'][0]:5.2f}      {runs_q2:3d}"
          f"                       | {100*evH/evN:5.1f} / {100*evH2/max(evN2,1):5.1f}              | {onH}/{onN}  /  {onH2}/{onN2}              | {np.median(delays) if delays else float('nan'):.0f}", flush=True)

# which feature triggers the q2 false alarms (rule A)?
nf = nt = nboth = 0; relf = []; relt = []
for p, F, T, L in healthy:
    if p != "q2": continue
    hf = rule(F, T, feats="f")[K_REF:]; ht = rule(F, T, feats="ft")[K_REF:] & ~hf
    nf += hf.sum(); nt += ht.sum()
    relf.append(np.std(F[:K_REF]) / np.mean(F[:K_REF])); relt.append(np.std(T[:K_REF]) / abs(np.mean(T[:K_REF])))
print(f"\nq2 healthy false alarms under rule A: triggered by fire rate {nf}, by correlation only {nt}")
print(f"relative noise of one {WIN}-shot window on healthy q2: fire rate {100*np.median(relf):.1f}%, correlation {100*np.median(relt):.1f}%  (reference std estimated from only {K_REF} windows)")
for p in ("q0", "q1", "q2"):
    a = [np.std(F[:K_REF]) / np.mean(F[:K_REF]) for pp, F, T, L in healthy if pp == p]; b = [np.std(T[:K_REF]) / abs(np.mean(T[:K_REF])) for pp, F, T, L in healthy if pp == p]
    print(f"  {p}: fire-rate relative noise {100*np.median(a):.1f}%, correlation relative noise {100*np.median(b):.1f}%")

print("\n=== 4. MISSED vs DETECTED ONSETS (rule A) ===")
rec = []
for p, s, seed, F, T, L in drift:
    al = rule(F, T); base = max(L[0], 0.005); ev = L > 2 * base; contam = L[:K_REF].max() > 2 * max(L[0], 0.005)
    for i in onsets(ev):
        dur = 1
        while i + dur < len(ev) and ev[i + dur]: dur += 1
        rec.append(dict(p=p, s=s, ratio=L[i] / base, abs=L[i], dur=dur, contam=contam, det=bool(al[i:i + 4].any()),
                        late=bool(al[i + 4:i + 12].any())))
for tag, sel in (("detected within 12 h", [r for r in rec if r["det"]]), ("missed", [r for r in rec if not r["det"]])):
    if not sel: continue
    print(f"{tag:22s}: {len(sel):3d} onsets | median flip-rate at onset {100*np.median([r['abs'] for r in sel]):.2f}% ({np.median([r['ratio'] for r in sel]):.1f}x start) | "
          f"median event length {np.median([r['dur'] for r in sel]):.0f} steps | one-step events {100*np.mean([r['dur']==1 for r in sel]):.0f}% | "
          f"reference contaminated {100*np.mean([r['contam'] for r in sel]):.0f}% | q2 {100*np.mean([r['p']=='q2' for r in sel]):.0f}% | strength 4x {100*np.mean([r['s']==4 for r in sel]):.0f}%")
ms = [r for r in rec if not r["det"]]
print(f"of the {len(ms)} missed onsets, {sum(r['late'] for r in ms)} were alarmed later (steps 4 to 11 after onset)")
