"""check_claims.py -- confirm that the numbers quoted in results/paper_evidence.md match the result files.

Each check recomputes a value from a results CSV (or, for resampling intervals, finds the quoted text in the summary file that
produced it) and also requires the quoted text to be present in the evidence sheet, so the sheet and the data cannot drift
apart unnoticed. Exit code 0 if every check passes, 1 otherwise.

Usage (repo root): python check_claims.py            # prints one line per check
                   python check_claims.py --quiet    # prints only failures and the total
"""
import csv
import math
import os
import re
import sys

SHEET = "results/paper_evidence.md"
R = []          # (ok, label, detail)


def rows(path):
    return list(csv.DictReader(open(path)))


def squash(s):
    return re.sub(r"\s+", " ", s)


def check(label, quoted, computed=None, expected=None, tol=0.0, source_text=None, source_path=None):
    """quoted: text that must appear in the sheet. computed/expected: numbers that must agree within tol.
    source_text: text that must appear in source_path (used for resampling intervals, which are not recomputed)."""
    probs = []
    for q in ([quoted] if isinstance(quoted, str) else quoted):
        if squash(q) not in SHEET_TEXT:
            probs.append(f"not in evidence sheet: '{q}'")
    if computed is not None:
        if isinstance(computed, float) and math.isnan(computed) or abs(computed - expected) > tol + 1e-12:
            probs.append(f"recomputed {computed:.6g}, sheet says {expected:.6g}")
    if source_text is not None:
        if squash(source_text) not in squash(open(source_path).read()):
            probs.append(f"'{source_text}' not found in {source_path}")
    R.append((not probs, label, "; ".join(probs) if probs else (f"recomputed {computed:.6g}" if computed is not None else "text matches source")))


def pooled(win_rows, scenario, arm):
    k = sum(int(r["errors"]) for r in win_rows if r["scenario"] == scenario and r["arm"] == arm)
    n = sum(int(r["shots"]) for r in win_rows if r["scenario"] == scenario and r["arm"] == arm)
    return k, n


def main():
    global SHEET_TEXT
    SHEET_TEXT = squash(open(SHEET).read())

    # ---------------------------------------------------------------- dataset
    p = "results/real149/real_event_checks.csv"
    q0 = [r for r in rows(p) if r["qubit"] == "0"]
    hrs = [float(r["hours"]) for r in q0]
    gaps = sorted(b - a for a, b in zip(hrs, hrs[1:]))
    med = (gaps[len(gaps) // 2] + gaps[(len(gaps) - 1) // 2]) / 2
    check("dataset: number of snapshots", "149 snapshots", len(q0), 149)
    check("dataset: span in hours", "span 375.2 h", hrs[-1], 375.2, 0.05)
    check("dataset: median gap", "median 2.56 h", med, 2.56, 0.005)
    check("dataset: minimum gap", "minimum 0.15 h", gaps[0], 0.15, 0.005)
    check("dataset: maximum gap", "maximum 16.0 h", gaps[-1], 16.0, 0.05)
    late = sorted(-float(r["timestamp_minus_last_update_h"]) for r in q0 if float(r["timestamp_minus_last_update_h"]) < 0)
    check("dataset: snapshots whose job ran after the timestamp", "Seven snapshot timestamps", len(late), 7)
    big = [x for x in late if x > 5]
    check("dataset: late jobs over 5 h", "five of those jobs ran 5.4 to 14.6 h later", len(big), 5)
    check("dataset: shortest of the long delays", "5.4 to 14.6 h", big[0], 5.4, 0.05)
    check("dataset: longest delay", "5.4 to 14.6 h", big[-1], 14.6, 0.05)

    # ---------------------------------------------------------------- Gate 1
    p = "results/gate1_149/gate1_ler_results.csv"
    g = rows(p)
    sel = lambda part, d, series: sorted([r for r in g if r["part"] == part and r["d"] == str(d) and r["series"] == series], key=lambda r: int(r["window"]))
    for d, first, last in ((3, "0.0036 [0.0029, 0.0045]", "0.0133 [0.0118, 0.0150]"), (5, "0.0009 [0.0006, 0.0015]", "0.0056 [0.0047, 0.0068]")):
        s = sel("simulated", d, "drift")
        for r, txt, lab in ((s[0], first, "first"), (s[-1], last, "last")):
            v = [float(x) for x in re.findall(r"[\d.]+", txt)]
            check(f"gate 1 simulated d={d} {lab} window LER", txt, float(r["ler"]), v[0], 5e-5)
            check(f"gate 1 simulated d={d} {lab} window CI low", txt, float(r["lo"]), v[1], 5e-5)
            check(f"gate 1 simulated d={d} {lab} window CI high", txt, float(r["hi"]), v[2], 5e-5)
            check(f"gate 1 simulated d={d} {lab} window shots", "20,000 shots per window", int(r["n"]), 20000)
    s = sel("real_iq", 3, "drift")
    top = sorted(s, key=lambda r: -float(r["p"]))[:3]
    check("gate 1 real d=3: LER of the three windows with the highest frozen-boundary readout error", "LER 0.0387 [0.0372, 0.0403]",
          sum(int(r["k"]) for r in top) / sum(int(r["n"]) for r in top), 0.0387, 5e-5)
    c = sel("real_iq", 3, "control")
    check("gate 1 real d=3: control LER", "against a control of 0.0052", sum(int(r["k"]) for r in c) / sum(int(r["n"]) for r in c), 0.0052, 5e-5)
    check("gate 1 real: number of windows", "149 windows of 20,000 shots", len(s), 149)
    sm = "results/gate1_149/gate1_ler_summary.md"
    check("gate 1 real d=3: permutation p and rank correlation (from the summary)", ["selection-aware permutation p = 0.0002", "window LER +0.94"],
          source_text="rank correlation between window readout error and window LER +0.94, permutation p = 0.0002", source_path=sm)
    check("gate 1 simulated: control p-values (from the summary)", "p = 0.78 and 0.72", source_text="first-vs-last p = 0.78", source_path=sm)
    check("gate 1 simulated: control p-value d=5 (from the summary)", "p = 0.78 and 0.72", source_text="first-vs-last p = 0.72", source_path=sm)

    # ---------------------------------------------------------------- closed loop
    tab = "results/closed_loop/closed_loop_table.md"
    quoted = {
        ("controlled", "step_q1"): dict(frozen=("5.068", "5.068 [4.968, 5.183]"), oracle=("0.270", "0.270 [0.259, 0.281]"),
                                        em_pi_fast=("0.285", "0.285 [0.267, 0.306]"), em_pi_fast_lag=("0.438", "0.438 [0.415, 0.460]"),
                                        periodic_24h=("0.951", "0.951 [0.916, 0.986]")),
        ("controlled", "slow_q1"): dict(frozen=("1.825", "1.825 [1.775, 1.875]"), oracle=("0.270", None), em_pi_fast_lag=("0.271", "0.271 [0.260, 0.283]")),
        ("real", "real_q1"): dict(frozen=("0.892", "0.892 [0.514, 1.379]"), oracle=("0.663", "0.663 [0.425, 0.963]"), em_pi_fast=("0.667", None),
                                  em_pi_fast_lag=("0.824", "0.824 [0.519, 1.189]"), periodic_24h=("0.963", None)),
        ("real", "real_q0"): dict(frozen=("0.498", None), oracle=("0.428", None), em_pi_fast_lag=("0.442", None)),
        ("real", "real_q2"): dict(frozen=("0.034", None), oracle=("0.032", None)),
        ("fitted", "refit_q1"): dict(frozen=("1.764", "1.764 [1.089, 2.392]"), oracle=("0.995", "0.995 [0.649, 1.324]")),
    }
    rec = {("controlled", "step_q1"): dict(em_pi_fast=(1.00, "recovery 1.00 [0.99, 1.00]", "+1.00 [+0.99, +1.00]"),
                                            em_pi_fast_lag=(0.96, "recovery 0.96 [0.96, 0.97]", "+0.96 [+0.96, +0.97]"),
                                            periodic_24h=(0.86, "recovery 0.86 [0.85, 0.87]", "+0.86 [+0.85, +0.87]")),
           ("controlled", "slow_q1"): dict(em_pi_fast_lag=(1.00, "recovery 1.00 [1.00, 1.00]", "+1.00 [+1.00, +1.00]")),
           ("real", "real_q1"): dict(em_pi_fast=(0.99, "recovery 0.99 [0.97, 1.00]", "+0.99 [+0.97, +1.00]"),
                                     em_pi_fast_lag=(0.30, "recovery 0.30 [0.25, 0.32]", "+0.30 [+0.25, +0.32]"),
                                     periodic_24h=(-0.31, "-0.31 [-0.35, -0.28]", "-0.31 [-0.35, -0.28]")),
           ("real", "real_q0"): dict(em_pi_fast_lag=(0.80, "recovery 0.80 [0.75, 0.85]", "+0.80 [+0.75, +0.85]")),
           ("fitted", "refit_q1"): dict(em_pi_fast=(0.91, "0.91 [0.88, 0.94]", "+0.91 [+0.88, +0.94]"),
                                        em_pi_fast_lag=(0.52, "0.52 [0.42, 0.57]", "+0.52 [+0.42, +0.57]"))}
    cache = {}
    for (sub, sc), arms in quoted.items():
        w = cache.setdefault(sub, rows(f"results/closed_loop/{sub}/ler_windows.csv"))
        for arm, (val, full) in arms.items():
            k, n = pooled(w, sc, arm)
            check(f"closed loop {sc} {arm}: pooled LER (%)", full or val, 100 * k / n, float(val), 5e-4)
            if full:
                iv = full[full.index("["):]
                check(f"closed loop {sc} {arm}: resampling interval (from the table)", full, source_text=f"{val} {iv}", source_path=tab)
        kf, nf = pooled(w, sc, "frozen")
        ko, _ = pooled(w, sc, "oracle")
        for arm, (val, qtxt, ttxt) in rec.get((sub, sc), {}).items():
            ka, _ = pooled(w, sc, arm)
            check(f"closed loop {sc} {arm}: recovery", qtxt, (kf - ka) / (kf - ko), val, 5e-3)
            check(f"closed loop {sc} {arm}: recovery interval (from the table)", qtxt, source_text=ttxt, source_path=tab)
    w = cache["controlled"]
    check("closed loop step: shots per arm", "516,000 shots per arm", pooled(w, "step_q1", "frozen")[1], 516000)
    w = cache["real"]
    kf, nf = pooled(w, "real_q1", "frozen"); ko, _ = pooled(w, "real_q1", "oracle")
    check("closed loop real q1: shots per arm", "1,788,000 shots per arm", nf, 1788000)
    check("closed loop real q1: frozen-to-oracle gap (points)", "gap is 0.228 percentage points", 100 * (kf - ko) / nf, 0.228, 5e-4)
    kf, nf = pooled(w, "real_q0", "frozen"); ko, _ = pooled(w, "real_q0", "oracle")
    check("closed loop real q0: gap (points)", "gap 0.070 points", 100 * (kf - ko) / nf, 0.070, 5e-4)
    check("closed loop real q1: online minus same-window (from the summary)", "+0.159 [+0.070, +0.256]",
          source_text="em_pi_fast_lag - em_pi_fast: +0.159 [+0.070, +0.256]", source_path="results/closed_loop/real/ler_summary.md")
    for sc in ("real_q2",):
        check(f"closed loop {sc}: gap not resolvable (from the summary)", "the gap is not distinguishable from zero",
              source_text="(not distinguishable from zero, recovery fractions are not reported)", source_path="results/closed_loop/real/ler_summary.md")

    # ---------------------------------------------------------------- detector
    d = rows("results/detector_scoring/detector_scoring.csv")
    A = lambda src: [r for r in d if r["part"] == "A" and r["source"] == src]
    h = A("healthy")
    check("detector: healthy windows per window size", "0 of 800 healthy windows", min(int(r["n_windows"]) for r in h), 800)
    check("detector: false alarms on healthy windows (all four sizes)", "0 of 800 healthy windows", sum(int(r["alarms"]) for r in h), 0)
    check("detector: window sizes tested", "250, 500, 1000 and 1500 shots", len(h), 4)
    check("detector: healthy 95% upper bound", "95% upper bound 0.5%", max(float(r["ci_hi"]) for r in h), 0.005, 5e-4)
    r35 = A("readout 0.35 sigma")
    check("detector: 0.35 sigma alarms", "alarms on 800 of 800 windows", min(int(r["alarms"]) for r in r35), 800)
    check("detector: 0.35 sigma readout error ratio", "readout error 1.65x healthy", sum(float(r["error_ratio"]) for r in r35) / 4, 1.65, 0.01)
    check("detector: 0.35 sigma first-alarm window", "the first window after the step alarms", max(float(r["median_first_alarm_window"]) for r in r35), 1)
    for src, lo, hi, txt in (("readout 0.25 sigma", 0.55, 0.62, "0.25 sigma on 0.55 to 0.62 of windows"), ("readout 0.15 sigma", 0.00, 0.06, "0.15 sigma on 0.00 to 0.06"),
                             ("physical x3", 0.99, 1.00, "alarms on 0.99 to 1.00 of windows"), ("physical x2", 0.03, 0.14, "a 2x rise on 0.03 to 0.14")):
        f = [float(r["alarm_fraction"]) for r in A(src)]
        check(f"detector: {src} lowest alarm fraction", txt, min(f), lo, 5e-3)
        check(f"detector: {src} highest alarm fraction", txt, max(f), hi, 5e-3)
    for q, k, n in ((0, 0, 86), (1, 0, 1032), (2, 3, 1028)):
        r = [x for x in d if x["part"] == "B" and x["source"] == f"real q{q}" and x["group"] == "rise under 0.25 pp"][0]
        check(f"detector: real q{q} alarms where the rise is under 0.25 points", "0 of 86 (q0), 0 of 1032 (q1), 3 of 1028 (q2)", int(r["alarms"]), k)
        check(f"detector: real q{q} windows where the rise is under 0.25 points", "0 of 86 (q0), 0 of 1032 (q1), 3 of 1028 (q2)", int(r["n_windows"]), n)
    big = [x for x in d if x["part"] == "B" and x["source"].startswith("real") and x["group"] in ("rise 1 to 2 pp", "rise over 2 pp") and int(x["n_windows"])]
    check("detector: real windows with a rise over 1 point that did not alarm", "every window with a rise over 1 point alarmed",
          sum(int(x["n_windows"]) - int(x["alarms"]) for x in big), 0)

    # ---------------------------------------------------------------- attribution
    a = rows("results/attribution_heldout/attribution_heldout.csv")
    ab = lambda win, feat, phys="all": [r for r in a if r["table"] == "ablation" and r["window"] == str(win) and r["features"] == feat and r["physical"] == phys][0]
    check("attribution: pooled AUC, 250-shot windows", "0.903 and 0.898", float(ab(250, "all three")["auc"]), 0.903, 5e-4)
    check("attribution: pooled AUC, 1500-shot windows", "0.903 and 0.898", float(ab(1500, "all three")["auc"]), 0.898, 5e-4)
    lo = min(float(ab(w_, "all three")["ci_lo"]) for w_ in (250, 1500)); hi = max(float(ab(w_, "all three")["ci_hi"]) for w_ in (250, 1500))
    check("attribution: pooled AUC interval, lower", "AUC 0.90 [0.89, 0.91]", lo, 0.89, 5e-3)
    check("attribution: pooled AUC interval, upper", "AUC 0.90 [0.89, 0.91]", hi, 0.91, 5e-3)
    check("attribution: pooled accuracy", "accuracy 0.88", (float(ab(250, "all three")["accuracy"]) + float(ab(1500, "all three")["accuracy"])) / 2, 0.88, 5e-3)
    check("attribution: fire rate alone", "Fire rate alone 0.51", (float(ab(250, "fire rate only")["auc"]) + float(ab(1500, "fire rate only")["auc"])) / 2, 0.51, 5e-3)
    check("attribution: correlation alone", "correlation alone 0.86", (float(ab(250, "correlation only")["auc"]) + float(ab(1500, "correlation only")["auc"])) / 2, 0.86, 5e-3)
    check("attribution: chance band lower", "0.48 to 0.52", min(float(ab(w_, "all three")["chance_lo"]) for w_ in (250, 1500)), 0.48, 5e-3)
    check("attribution: chance band upper", "0.48 to 0.52", max(float(ab(w_, "all three")["chance_hi"]) for w_ in (250, 1500)), 0.52, 5e-3)
    kind = [r for r in a if r["table"] == "by kind"]
    non = [float(r["auc"]) for r in kind if r["physical"] != "reset"]
    rst = [float(r["auc"]) for r in kind if r["physical"] == "reset"]
    check("attribution: lowest AUC against non-reset physical noise", "AUC 0.997 to 1.000", min(non), 0.997, 5e-4)
    check("attribution: highest AUC against non-reset physical noise", "AUC 0.997 to 1.000", max(non), 1.000, 5e-4)
    check("attribution: lowest AUC against reset errors", "AUC is 0.14 to 0.63", min(rst), 0.14, 5e-3)
    check("attribution: highest AUC against reset errors", "AUC is 0.14 to 0.63", max(rst), 0.63, 5e-3)
    r0 = ab(250, "all three")
    check("attribution: test windows", "5400 test windows", int(r0["n_pos"]) + int(r0["n_neg"]), 5400)

    # ---------------------------------------------------------------- gating
    g50 = rows("results/gating/n_unl_50/ler_windows.csv")
    kg, ng = pooled(g50, "quiet_q1", "gated_v5_lag"); kf, nf = pooled(g50, "quiet_q1", "em_pi_fast_lag")
    check("gating: quiet run at 50 points, gated online LER (%)", "0.275% against 0.300% at 50 points", 100 * kg / ng, 0.275, 5e-4)
    check("gating: quiet run at 50 points, always-fast online LER (%)", "0.275% against 0.300% at 50 points", 100 * kf / nf, 0.300, 5e-4)
    check("gating: paired difference at 50 points (from the summary)", "difference -0.024 [-0.036, -0.011] points",
          source_text="gated_v5_lag - em_pi_fast_lag: -0.024 [-0.036, -0.011]", source_path="results/gating/n_unl_50/ler_summary.md")
    worst = 0.0
    for sub in ("n_unl_1500", "fitted_n_unl_1500"):
        w = rows(f"results/gating/{sub}/ler_windows.csv")
        for sc in sorted({r["scenario"] for r in w}):
            kg, ng = pooled(w, sc, "gated_v5_lag"); kf, nf = pooled(w, sc, "em_pi_fast_lag")
            worst = max(worst, abs(100 * kg / ng - 100 * kf / nf))
    check("gating: largest gated-minus-fast difference at 1500 points (points)", "within 0.008 points", worst, 0.008, 6e-4)

    quiet = "--quiet" in sys.argv
    bad = [r for r in R if not r[0]]
    for ok, label, detail in R:
        if not ok or not quiet:
            print(f"{'PASS' if ok else 'FAIL'}  {label}  ({detail})")
    print(f"\n{len(R) - len(bad)} of {len(R)} checks passed" + ("" if not bad else f"; {len(bad)} FAILED"))
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
