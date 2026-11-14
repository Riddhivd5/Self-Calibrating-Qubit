"""
validate_discriminator.py -- validate rtl/discriminator.v in RTL simulation (Icarus Verilog) against the bit-exact,
cycle-accurate Python model (rtl/discriminator_model.py), on every labelled IQ point in data/ and on directed tests.

This replaces the six-vector check of discriminator_tb.v as evidence. It is RTL SIMULATION, not a run on the FPGA board, and it
says nothing about resources or timing.

Tests (one stimulus line per clock cycle; every cycle of the RTL response is compared with the model):
  1. dataset      every labelled IQ point of every snapshot and qubit, one sample per clock with no gaps (sustained traffic); the
                  boundary coefficients switch between qubits in mid-stream (parameter updates)
  2. boundary     sums of exactly zero and one least-significant step either side
  3. extremes     every combination of {-32768, -32767, -1, 0, 1, 32767} on I, Q and the three coefficients (overflow check)
  4. random       uniformly random 16-bit inputs and coefficients changing every cycle, valid_in asserted at random
  5. reset        synchronous reset asserted in the middle of valid traffic
  6. latency      a single valid sample; cycles until valid_out
Also reported for the dataset: how often the Q1.15 decision differs from the floating-point decision, and the accuracy of each
against the prepared-state labels (boundary frozen at the first snapshot, so later snapshots include real drift).

Usage (repo root; needs iverilog and vvp on PATH):
    python rtl/validate_discriminator.py --data-dir data --out-dir results/<new folder>
"""
import argparse
import glob
import itertools
import json
import os
import subprocess
import sys
import tempfile
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import discriminator_model as dm
from iq_fixedpoint import SCALE, raw_to_fixed_point

HERE = os.path.dirname(os.path.abspath(__file__))
QUBITS = (0, 1, 2)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", default="data")
    ap.add_argument("--out-dir", default=".")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--random", type=int, default=200000)
    a = ap.parse_args()
    os.makedirs(a.out_dir, exist_ok=True)
    out_md, out_js = os.path.join(a.out_dir, "rtl_validation.md"), os.path.join(a.out_dir, "rtl_validation.json")
    if (os.path.exists(out_md) or os.path.exists(out_js)) and not a.force:
        sys.exit(f"outputs exist in {a.out_dir}; use a new --out-dir or --force")
    files = sorted(glob.glob(os.path.join(a.data_dir, "iq_*.npz")))
    if not files:
        sys.exit(f"no iq_*.npz in {a.data_dir}")
    rng = np.random.default_rng(2026)

    # ---------------------------------------------------------------- boundaries, frozen at the first snapshot
    first = np.load(files[0])
    coef, coef_f = {}, {}
    for q in QUBITS:
        c0, c1 = first[f"q{q}_state0"].mean(), first[f"q{q}_state1"].mean()
        qa, qb, qc, fl = dm.boundary_to_q15(c0, c1, SCALE)
        coef[q], coef_f[q] = (qa, qb, qc), fl

    seg = []    # (name, rst_n, valid, i, q, a, b, c)

    def add(name, i, q, a_, b_, c_, valid=None, rst=None):
        n = len(i)
        full = lambda x: np.full(n, x, np.int64) if np.isscalar(x) else np.asarray(x, np.int64)
        seg.append((name, np.ones(n, np.int64) if rst is None else np.asarray(rst, np.int64),
                    np.ones(n, np.int64) if valid is None else np.asarray(valid, np.int64), full(i), full(q), full(a_), full(b_), full(c_)))

    add("reset", np.zeros(4), 0, 0, 0, 0, valid=np.zeros(4), rst=np.zeros(4))
    # ---------------------------------------------------------------- 1. dataset
    I, Q, A, B, C, LAB, QB, FLT = [], [], [], [], [], [], [], []
    clipped = 0
    for f in files:
        z = np.load(f)
        for q in QUBITS:
            for st in (0, 1):
                raw = z[f"q{q}_state{st}"]
                fi, fq = raw_to_fixed_point(raw)
                clipped += int(np.sum((np.round(raw.real / SCALE * 2 ** 15) != fi) | (np.round(raw.imag / SCALE * 2 ** 15) != fq)))
                n = len(raw)
                I.append(fi.astype(np.int64)); Q.append(fq.astype(np.int64))
                A.append(np.full(n, coef[q][0])); B.append(np.full(n, coef[q][1])); C.append(np.full(n, coef[q][2]))
                LAB.append(np.full(n, st)); QB.append(np.full(n, q))
                fa, fb, fc = coef_f[q]
                FLT.append(((raw.real / SCALE) * fa + (raw.imag / SCALE) * fb + fc > 0).astype(np.uint8))
    I, Q, A, B, C, LAB, QB, FLT = (np.concatenate(x) for x in (I, Q, A, B, C, LAB, QB, FLT))
    add("dataset", I, Q, A, B, C)
    n_data = len(I)
    switches = int(np.sum(np.diff(QB) != 0))
    add("gap", np.zeros(4), 0, 0, 0, 0, valid=np.zeros(4))

    # ---------------------------------------------------------------- 2. boundary cases: (I, Q, a, b, c) with a known exact sum
    bc = []
    for base in ((0, 0, 1, 0, 0), (5, 5, 16384, -16384, 0), (2, 0, 16384, 0, -1), (-2, 0, 16384, 0, 1), (32767, 32767, 1, -1, 0),
                 (-32768, 0, 1, 0, 1), (1, 1, -32768, 32767, 1), (0, 0, 0, 0, 0), (123, -77, 0, 0, 0)):
        i0, q0, a0, b0, c0 = base
        bc.append(base)
        bc.append((i0 + 1, q0, a0, b0, c0)); bc.append((i0 - 1, q0, a0, b0, c0))
        if c0 > -32768:
            bc.append((i0, q0, a0, b0, c0 - 1))
        if c0 < 32767:
            bc.append((i0, q0, a0, b0, c0 + 1))
    bc = np.array(bc, np.int64)
    bc[:, 0] = np.clip(bc[:, 0], -32768, 32767)
    add("boundary", bc[:, 0], bc[:, 1], bc[:, 2], bc[:, 3], bc[:, 4])
    bsum = bc[:, 0] * bc[:, 2] + bc[:, 1] * bc[:, 3] + (bc[:, 4] << 15)
    add("gap", np.zeros(4), 0, 0, 0, 0, valid=np.zeros(4))

    # ---------------------------------------------------------------- 3. extremes
    ex = np.array(list(itertools.product((-32768, -32767, -1, 0, 1, 32767), repeat=5)), np.int64)
    add("extremes", ex[:, 0], ex[:, 1], ex[:, 2], ex[:, 3], ex[:, 4])
    esum = ex[:, 0] * ex[:, 2] + ex[:, 1] * ex[:, 3] + (ex[:, 4] << 15)
    add("gap", np.zeros(4), 0, 0, 0, 0, valid=np.zeros(4))

    # ---------------------------------------------------------------- 4. random traffic with gaps
    n = a.random
    rv = (rng.random(n) < 0.7).astype(np.int64)
    add("random", *(rng.integers(-32768, 32768, n) for _ in range(5)), valid=rv)
    add("gap", np.zeros(4), 0, 0, 0, 0, valid=np.zeros(4))

    # ---------------------------------------------------------------- 5. reset in the middle of valid traffic
    n = 400
    rst = np.ones(n, np.int64)
    rst[100:102] = 0; rst[250] = 0
    add("reset_midstream", *(rng.integers(-32768, 32768, n) for _ in range(5)), rst=rst)
    add("gap", np.zeros(6), 0, 0, 0, 0, valid=np.zeros(6))

    # ---------------------------------------------------------------- 6. latency: one valid sample, then idle
    v = np.zeros(12, np.int64); v[0] = 1
    add("latency", np.full(12, 1000), 0, 16384, 0, 0, valid=v)

    names = np.concatenate([np.full(len(s[1]), k) for k, s in enumerate(seg)])
    R_, V_, I_, Q_, A_, B_, C_ = (np.concatenate([s[j] for s in seg]) for j in range(1, 8))
    exp_v, exp_s = dm.simulate(R_, V_, I_, Q_, A_, B_, C_)

    # ---------------------------------------------------------------- run the RTL
    with tempfile.TemporaryDirectory() as tmp:
        stim, resp, sim = (os.path.join(tmp, x) for x in ("stimulus.txt", "response.txt", "sim.vvp"))
        np.savetxt(stim, np.c_[R_, V_, I_, Q_, A_, B_, C_], fmt="%d")
        subprocess.run(["iverilog", "-g2012", "-o", sim, os.path.join(HERE, "discriminator_file_tb.v"), os.path.join(HERE, "discriminator.v")], check=True)
        t0 = time.time()
        subprocess.run(["vvp", sim, f"+stim={stim}", f"+resp={resp}"], check=True, capture_output=True)
        sim_s = time.time() - t0
        txt = np.loadtxt(resp, dtype=str)
    to_int = lambda col: np.array([int(x) if x in ("0", "1") else -1 for x in col])
    got_v, got_s = to_int(txt[:, 0]), to_int(txt[:, 1])
    if len(got_v) != len(exp_v):
        sys.exit(f"RTL produced {len(got_v)} cycles, model {len(exp_v)}")
    iv = subprocess.run(["iverilog", "-V"], capture_output=True, text=True).stdout.split("\n")[0]

    # ---------------------------------------------------------------- compare, per test
    res = {}
    for k, s in enumerate(seg):
        if s[0] in ("gap", "reset"):
            continue
        m = names == k
        # responses to this segment's samples appear LATENCY cycles later; compare the cycles [start, end + LATENCY)
        idx = np.where(m)[0]
        lo, hi = idx[0], min(idx[-1] + 1 + dm.LATENCY, len(exp_v))
        sl = slice(lo, hi)
        res[s[0]] = dict(cycles=int(hi - lo), samples=int(s[2].sum()), valid_out_expected=int(exp_v[sl].sum()),
                         valid_mismatch=int(np.sum(got_v[sl] != exp_v[sl])), state_mismatch=int(np.sum(got_s[sl] != exp_s[sl])),
                         unknown=int(np.sum((got_v[sl] < 0) | (got_s[sl] < 0))))
    total_cyc = len(exp_v)
    total_mis = int(np.sum(got_v != exp_v) + np.sum(got_s != exp_s))

    # decisions of the RTL for the dataset samples (aligned by the pipeline latency)
    d0 = np.where(names == [k for k, s in enumerate(seg) if s[0] == "dataset"][0])[0][0]
    rtl_dec = got_s[d0 + dm.LATENCY - 1: d0 + dm.LATENCY - 1 + n_data]
    rtl_val = got_v[d0 + dm.LATENCY - 1: d0 + dm.LATENCY - 1 + n_data]
    mdl_dec = dm.classify(I, Q, A, B, C)
    # latency measured on the RTL response: first valid_out after the single valid sample
    l0 = np.where(names == [k for k, s in enumerate(seg) if s[0] == "latency"][0])[0][0]
    lat = int(np.argmax(got_v[l0:l0 + 12] == 1)) + 1
    # boundary and extremes directly against the exact sums
    b0 = np.where(names == [k for k, s in enumerate(seg) if s[0] == "boundary"][0])[0][0]
    b_dec = got_s[b0 + dm.LATENCY - 1: b0 + dm.LATENCY - 1 + len(bc)]
    e0 = np.where(names == [k for k, s in enumerate(seg) if s[0] == "extremes"][0])[0][0]
    e_dec = got_s[e0 + dm.LATENCY - 1: e0 + dm.LATENCY - 1 + len(ex)]

    L = ["# RTL validation of the baseline discriminator (rtl/discriminator.v)", "",
         f"RTL simulation with {iv}; every clock cycle of the RTL response (valid_out and state_bit) compared with the cycle-accurate "
         "Python model rtl/discriminator_model.py. This is simulation, not a run on the FPGA board; it gives no resource or timing "
         "numbers.", "",
         f"Total: {total_cyc:,} clock cycles simulated ({sim_s:.0f} s), {total_mis} mismatching outputs.", "",
         "| test | what it covers | clock cycles compared | valid samples | valid_out mismatches | state_bit mismatches | unknown (X) outputs |",
         "|---|---|---|---|---|---|---|"]
    what = {"dataset": f"every labelled IQ point: {len(files)} snapshots x {len(QUBITS)} qubits x 2 states, one sample per clock, coefficients switched "
                       f"{switches} times in mid-stream",
            "boundary": "sums of exactly zero and one step either side", "extremes": "all 6^5 combinations of extreme and near-zero values",
            "random": "random inputs, coefficients changing every cycle, valid_in random (70%)",
            "reset_midstream": "synchronous reset asserted twice during valid traffic", "latency": "one valid sample, then idle"}
    for k, r in res.items():
        L.append(f"| {k} | {what[k]} | {r['cycles']:,} | {r['samples']:,} | {r['valid_mismatch']} | {r['state_mismatch']} | {r['unknown']} |")
    L.append("")
    L.append("## Dataset")
    L.append("")
    L.append(f"- {n_data:,} labelled IQ points (IBM {os.path.basename(files[0])[3:13]} to {os.path.basename(files[-1])[3:13]}); raw values divided by "
             f"2^{int(np.log2(SCALE))} and rounded to Q1.15. Points clipped by the Q1.15 range: {clipped}. I range [{I.min()}, {I.max()}], Q range [{Q.min()}, {Q.max()}].")
    L.append(f"- RTL decision equals the bit-exact model on {int(np.sum(rtl_dec == mdl_dec)):,} of {n_data:,} points; valid_out asserted for "
             f"{int(np.sum(rtl_val == 1)):,} of {n_data:,}.")
    L.append("- Boundary per qubit: perpendicular bisector of the two centroids of the first snapshot, held fixed for all snapshots "
             "(so the accuracy below includes the real drift of the later snapshots).")
    L.append("")
    L.append("| qubit | Q1.15 coefficients (a, b, c) | points | fixed-point vs floating-point decisions that differ | accuracy, RTL (Q1.15) | accuracy, floating point |")
    L.append("|---|---|---|---|---|---|")
    summary = {}
    for q in QUBITS:
        m = QB == q
        dis = int(np.sum(rtl_dec[m] != FLT[m]))
        acc_r, acc_f = float(np.mean(rtl_dec[m] == LAB[m])), float(np.mean(FLT[m] == LAB[m]))
        L.append(f"| q{q} | ({coef[q][0]}, {coef[q][1]}, {coef[q][2]}) | {int(m.sum()):,} | {dis} ({100 * dis / m.sum():.4f}%) | {100 * acc_r:.3f}% | {100 * acc_f:.3f}% |")
        summary[f"q{q}"] = dict(points=int(m.sum()), coef=coef[q], fixed_vs_float_differ=dis, accuracy_rtl=acc_r, accuracy_float=acc_f)
    dis_all = int(np.sum(rtl_dec != FLT))
    L.append(f"| all | | {n_data:,} | {dis_all} ({100 * dis_all / n_data:.4f}%) | {100 * np.mean(rtl_dec == LAB):.3f}% | {100 * np.mean(FLT == LAB):.3f}% |")
    L.append("")
    L.append("## Directed tests")
    L.append("")
    L.append(f"- Boundary: {len(bc)} vectors, of which {int(np.sum(bsum == 0))} have a sum of exactly zero. RTL output agrees with sum >= 0 on "
             f"{int(np.sum(b_dec == (bsum >= 0)))} of {len(bc)}. For a sum of exactly zero the RTL outputs state 1 "
             f"({int(np.sum(b_dec[bsum == 0] == 1))} of {int(np.sum(bsum == 0))}); the header comment of discriminator.v says state 1 needs a sum "
             "strictly above zero, so the comment and the implementation differ on that one value.")
    L.append(f"- Extremes: {len(ex):,} vectors; largest |sum| {int(np.abs(esum).max()):,} against a 34-bit signed range of {2 ** 33:,}, so the adder "
             f"cannot overflow. RTL output agrees with the exact integer sum on {int(np.sum(e_dec == (esum >= 0))):,} of {len(ex):,}.")
    L.append(f"- Pipeline latency measured on the RTL: valid_out appears {lat} clock edges after the edge-aligned valid sample is presented; a new "
             "sample is accepted every clock cycle.")
    L.append("- Parameter update: coefficients are registered together with their sample, so a coefficient change applies from the sample "
             "presented in the same cycle and samples already in the pipeline keep the old coefficients (covered by the dataset and random tests).")
    L.append("- Reset: after a synchronous reset the samples in the pipeline are discarded and valid_out stays low until new samples "
             "have passed through (covered by the reset test).")
    L.append("")
    open(out_md, "w").write("\n".join(L) + "\n")
    json.dump(dict(simulator=iv, cycles=total_cyc, mismatches=total_mis, tests=res, dataset=dict(points=n_data, snapshots=len(files), clipped=clipped,
                                                                                               coefficient_switches=switches, fixed_vs_float_differ=dis_all,
                                                                                               accuracy_rtl=float(np.mean(rtl_dec == LAB)),
                                                                                               accuracy_float=float(np.mean(FLT == LAB)),
                                                                                               rtl_equals_model=int(np.sum(rtl_dec == mdl_dec)), per_qubit=summary),
                   latency_clock_edges=lat, boundary=dict(vectors=len(bc), zero_sum=int(np.sum(bsum == 0)), agree=int(np.sum(b_dec == (bsum >= 0)))),
                   extremes=dict(vectors=len(ex), agree=int(np.sum(e_dec == (esum >= 0))), max_abs_sum=int(np.abs(esum).max())),
                   cmd=" ".join(sys.argv), time=time.strftime("%Y-%m-%d %H:%M:%S"), numpy=np.__version__), open(out_js, "w"), indent=1)
    print("\n".join(L))
    print(f"wrote {out_md} and {out_js}")
    sys.exit(1 if total_mis else 0)


if __name__ == "__main__":
    main()
