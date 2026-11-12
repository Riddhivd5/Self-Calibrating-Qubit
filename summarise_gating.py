"""summarise_gating.py -- one table comparing the three step-size policies (always slow, always fast, gated by the v5 alarm) from
the ler_summary.md files written by ler_comparison.py, one sub-folder per update-batch size.

Usage (repo root): python summarise_gating.py results/gating
Writes <folder>/gating_summary.md. All numbers are copied from the ler_summary.md files; nothing is recomputed.
"""
import glob
import os
import re
import sys


def main():
    root = sys.argv[1] if len(sys.argv) > 1 else "results/gating"
    dirs = sorted(glob.glob(os.path.join(root, "*", "ler_summary.md")),
                  key=lambda p: (not os.path.basename(os.path.dirname(p)).startswith("n_unl"), int(re.search(r"(\d+)$", os.path.dirname(p)).group(1))))
    L = ["# Gating comparison: always slow (eta 0.3), always fast (eta 0.9), gated by the v5 alarm (0.3 quiet, 0.9 on alarm)", "",
         "LER in percent, pooled over runs. Online = one-step lag (a window is measured at the boundary from before that window's data), "
         "which is what a live controller faces. Differences are paired, in percentage points, with 95% intervals from resampling runs; "
         "negative = gated better. Source: the ler_summary.md in each sub-folder.", "",
         "| points per update | scenario | frozen | oracle | online slow | online fast | online gated | gated - fast | gated - slow | alarm fraction |",
         "|---|---|---|---|---|---|---|---|---|---|"]
    for p in dirs:
        n = re.search(r"(\d+)$", os.path.dirname(p)).group(1)
        for blk in open(p).read().split("### ")[1:]:
            name = blk.split("\n")[0]
            ler = {}
            for l in blk.split("\n"):
                if l.startswith("| ") and not l.startswith("| arm"):
                    c = [x.strip() for x in l.strip("|").split("|")]
                    ler[c[0]] = 100 * float(c[1].split()[0])
            d = {m.group(1): m.group(2) for m in re.finditer(r"- (\S+ - \S+): (\S+ \[[^\]]+\])", blk)}
            al = re.search(r"alarm fraction over all windows: (\S+)", blk).group(1)
            L.append(f"| {n} | {name} | {ler['frozen']:.3f} | {ler['oracle']:.3f} | {ler['em_pi_lag']:.3f} | {ler['em_pi_fast_lag']:.3f} | "
                     f"{ler['gated_v5_lag']:.3f} | {d['gated_v5_lag - em_pi_fast_lag']} | {d['gated_v5_lag - em_pi_lag']} | {al} |")
    out = os.path.join(root, "gating_summary.md")
    open(out, "w").write("\n".join(L) + "\n")
    print("\n".join(L))
    print(f"\nwrote {out}")


if __name__ == "__main__":
    main()
