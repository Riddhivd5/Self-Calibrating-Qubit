"""
decoder_check.py -- how much of the LER lost to readout drift is the decoder being out of date, and how much is lost at the
readout itself?

Every other script here decodes with a FIXED decoder built at the calibration-time readout error. This one decodes the same
syndromes twice: with that fixed decoder, and with an "informed" decoder rebuilt for each window from the readout error the
window actually had (the mean flip rate, which the experimenter would not know online; this is an upper bound on what a
decoder-side fix could do). Both are applied to the frozen boundary and to the oracle boundary (labelled recalibration every
window):
    frozen boundary + fixed decoder      the drifted system as it is
    frozen boundary + informed decoder   fix the decoder only
    oracle boundary + fixed decoder      fix the readout only
    oracle boundary + informed decoder   fix both
The windows, true outcomes and IQ draws are the same as in ler_comparison.py (same seeds), so "frozen + fixed" and
"oracle + fixed" reproduce its frozen and oracle arms; --check-against verifies that against a ler_windows.csv.
The informed decoder models readout error as a symmetric flip at the window's mean rate; the simulated readout errors are
state-dependent, so it is informed of the size of the error, not of its asymmetry.

Usage (repo root): python decoder_check.py --out-dir results/<new folder> [--check-against results/closed_loop]
"""
import argparse
import csv
import json
import os
import sys
import time

import numpy as np
import pymatching

import adaptive_boundary_v5 as v5
import ler_comparison as lc
from drift_framework import build_circuit

ARMS = ("frozen_fixed", "frozen_informed", "oracle_fixed", "oracle_informed")
NICE = {"frozen_fixed": "frozen boundary, fixed decoder", "frozen_informed": "frozen boundary, informed decoder",
        "oracle_fixed": "oracle boundary, fixed decoder", "oracle_informed": "oracle boundary, informed decoder"}
SCEN = {"step_q1": ("controlled", "Simulated 1 sigma step"), "real_q1": ("real", "Real replay q1"), "real_q0": ("real", "Real replay q0")}


def informed(cache, p):
    key = round(max(p, 1e-4), 3) or 0.001
    if key not in cache:
        c = build_circuit(v5.D, p_readout=key, p_phys=v5.P_PHYS)
        cache[key] = pymatching.Matching.from_detector_error_model(c.detector_error_model(decompose_errors=True))
    return cache[key]


def run(data, hw, matcher, seed, cache):
    f0, f1 = data["f0"], data["f1"]
    out = {m: [] for m in ARMS}
    flips = {"frozen": [], "oracle": []}
    for si, sd in enumerate(data["steps"]):
        ciq, cst = sd["cal"]
        base = 90_000 + 1000 * seed + si                      # same draws as ler_comparison.run
        true_out = hw.circ.compile_sampler(seed=base).sample(v5.WIN)
        idx = np.random.default_rng(base).integers(0, len(sd["pool0"]), true_out.shape)
        for name, bnd in (("frozen", (f0, f1)), ("oracle", (ciq[cst == 0].mean(), ciq[cst == 1].mean()))):
            det, obs, flip = lc.read_window(hw, true_out, idx, sd["pool0"], sd["pool1"], *bnd)
            flips[name].append(flip)
            for dec, mt in (("fixed", matcher), ("informed", informed(cache, flip))):
                pred = np.asarray(mt.decode_batch(det)).reshape(-1)
                out[f"{name}_{dec}"].append(int(np.sum(pred != obs)))
    return {m: np.array(v) for m, v in out.items()}, {k: np.array(v) for k, v in flips.items()}, np.array([sd["t"] for sd in data["steps"]])


def boot(K, shared, rng, n_boot=2000, block=6):
    """Paired bootstrap of pooled LER per arm: over runs (independent trajectories) or window blocks (one shared trajectory)."""
    R, T = K[ARMS[0]].shape
    out = {m: np.empty(n_boot) for m in ARMS}
    for b in range(n_boot):
        if shared:
            starts = rng.integers(0, T, int(np.ceil(T / block)))
            ix = np.concatenate([(s + np.arange(block)) % T for s in starts])[:T]
            for m in ARMS:
                out[m][b] = K[m][:, ix].sum() / (R * T * v5.WIN)
        else:
            ix = rng.integers(0, R, R)
            for m in ARMS:
                out[m][b] = K[m][ix].sum() / (R * T * v5.WIN)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default=".")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--scenarios", nargs="+", default=list(SCEN))
    ap.add_argument("--seeds", type=int, default=8)
    ap.add_argument("--data-dir", default="data")
    ap.add_argument("--shift-sigma", type=float, default=1.0)
    ap.add_argument("--check-against", default=None, help="folder holding controlled/ and real/ ler_windows.csv from ler_comparison.py")
    a = ap.parse_args()
    a.n_unl, a.refit_strength, a.refit_hours, a.refit_step, a.strength = 1500, 1.0, 336.0, 2.0, 4.0
    os.makedirs(a.out_dir, exist_ok=True)
    outs = [os.path.join(a.out_dir, f) for f in ("decoder_check.md", "decoder_check.csv", "decoder_check_config.json")]
    if any(os.path.exists(f) for f in outs) and not a.force:
        sys.exit(f"outputs exist in {a.out_dir}; use a new --out-dir or --force")
    import stim
    json.dump(dict(args=vars(a), cmd=" ".join(sys.argv), time=time.strftime("%Y-%m-%d %H:%M:%S"), numpy=np.__version__, stim=stim.__version__,
                   pymatching=pymatching.__version__), open(outs[2], "w"), indent=1)
    hw = lc.HW(v5.P_PHYS)
    S = lc.scenarios(argparse.Namespace(strength=4.0, phys_ramp=3.0, batch_sizes=[]))
    rng = np.random.default_rng(1)
    rows = []
    L = ["# Decoder check: is the LER lost to readout drift a decoder problem or a readout problem?", "",
         f"d = {v5.D}, physical error {v5.P_PHYS}, {v5.WIN} shots per window. The fixed decoder is built at the calibration-time readout error; the "
         "informed decoder is rebuilt for every window from that window's true mean readout error (not available online: an upper bound on a "
         "decoder-side fix). LER in percent with 95% resampling intervals (runs for simulated drift, window blocks for the real replay, which is "
         "one trajectory re-sampled). Paired differences use the same resamples.", ""]
    for name in a.scenarios:
        cfg = S[name]
        K = {m: [] for m in ARMS}
        FL = {"frozen": [], "oracle": []}
        cache = {}
        for k in range(a.seeds):
            seed = lc.TEST0 + k
            data = lc.build_data(cfg, seed, k, a)
            matcher = lc.design_matcher(data)
            r, fl, t = run(data, hw, matcher, seed, cache)
            for m in ARMS:
                K[m].append(r[m])
                for i in range(len(t)):
                    rows.append(dict(scenario=name, run=k, arm=m, step=i, t=t[i], errors=int(r[m][i]), shots=v5.WIN))
            for b in FL:
                FL[b].append(fl[b])
            print(f"  {name} run {k + 1}/{a.seeds} done", flush=True)
        K = {m: np.array(v) for m, v in K.items()}
        R, T = K[ARMS[0]].shape
        n = R * T * v5.WIN
        shared = cfg["kind"] == "real"
        bs = boot(K, shared, rng)
        ler = {m: K[m].sum() / n for m in ARMS}
        L.append(f"## {SCEN.get(name, ('', name))[1]} ({name}): {R} runs x {T} windows x {v5.WIN} shots = {n:,} shots per arm")
        L.append("")
        L.append(f"Mean readout error: frozen boundary {100 * np.mean(FL['frozen']):.2f}%, oracle boundary {100 * np.mean(FL['oracle']):.2f}%. "
                 f"Distinct informed decoders built: {len(cache)}.")
        L.append("")
        L.append("| arm | LER % [95% interval] | logical errors |")
        L.append("|---|---|---|")
        for m in ARMS:
            lo, hi = np.percentile(bs[m], [2.5, 97.5])
            L.append(f"| {NICE[m]} | {100 * ler[m]:.3f} [{100 * lo:.3f}, {100 * hi:.3f}] | {int(K[m].sum()):,} |")
        L.append("")
        gap = ler["frozen_fixed"] - ler["oracle_fixed"]
        d = lambda x, y: (100 * (ler[x] - ler[y]), *np.percentile(100 * (bs[x] - bs[y]), [2.5, 97.5]))
        share = lambda x: ((ler["frozen_fixed"] - ler[x]) / gap, *np.percentile((bs["frozen_fixed"] - bs[x]) / np.where(bs["frozen_fixed"] - bs["oracle_fixed"] > 0,
                                                                                                                    bs["frozen_fixed"] - bs["oracle_fixed"], np.nan), [2.5, 97.5]))
        L.append(f"- Fixing the readout only (oracle boundary, fixed decoder) removes {100 * gap:.3f} percentage points of LER; this is the "
                 "frozen-to-oracle gap used elsewhere.")
        v = d("frozen_informed", "frozen_fixed"); sh = share("frozen_informed")
        L.append(f"- Fixing the decoder only (frozen boundary, informed decoder) changes LER by {v[0]:+.3f} [{v[1]:+.3f}, {v[2]:+.3f}] points, "
                 f"i.e. removes {sh[0]:.2f} [{np.nanmin([sh[1], sh[2]]):.2f}, {np.nanmax([sh[1], sh[2]]):.2f}] of that gap.")
        v = d("oracle_informed", "oracle_fixed")
        L.append(f"- With the readout fixed, informing the decoder changes LER by {v[0]:+.3f} [{v[1]:+.3f}, {v[2]:+.3f}] points.")
        v = d("frozen_informed", "oracle_fixed")
        L.append(f"- LER still lost with a perfectly informed decoder but a frozen boundary, relative to fixing the readout: "
                 f"{v[0]:+.3f} [{v[1]:+.3f}, {v[2]:+.3f}] points.")
        if a.check_against:
            p = os.path.join(a.check_against, SCEN[name][0], "ler_windows.csv")
            ref = {}
            for r_ in csv.DictReader(open(p)):
                if r_["scenario"] == name and r_["arm"] in ("frozen", "oracle"):
                    ref[(r_["arm"], int(r_["run"]), int(r_["step"]))] = int(r_["errors"])
            bad = sum(1 for (arm, k, i), e in ref.items() if k < R and int(K[f"{arm}_fixed"][k, i]) != e)
            tot = sum(1 for (arm, k, i) in ref if k < R)
            L.append(f"- Consistency: the fixed-decoder arms reproduce the frozen and oracle arms of {p} in {tot - bad} of {tot} windows.")
        L.append("")
        print("\n".join(L[-14:]), flush=True)
    open(outs[0], "w").write("\n".join(L) + "\n")
    with open(outs[1], "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)
    print(f"wrote {outs[0]} and {outs[1]}")


if __name__ == "__main__":
    main()
