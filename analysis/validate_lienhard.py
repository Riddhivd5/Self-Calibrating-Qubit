"""
validate_lienhard.py -- check IQDriftGenerator at t=0 against Lienhard et al.,
"Deep-Neural-Network Discrimination of Multiplexed Superconducting-Qubit States",
Phys. Rev. Applied 17, 014024 (2022), arXiv:2102.12481.

Statistic definitions (matching the paper, Appendix C):
  R = (<S0> - <S1>)^2 / var(S)      (Eq. C3)  -> sqrt(R) = separation / sigma,
  where S is the 1-D matched-filter projection, i.e. the signal projected onto
  the axis joining the two centroids, and var(S) is its variance about each
  state's own mean.
  F_ach = Phi(sqrt(R)/2): ideal two-Gaussian assignment fidelity (checked
  against Table V: Phi(sqrt(26.817)/2)=0.995 for qubit 1, Phi(sqrt(3.001)/2)=0.807 for qubit 2).

Fix vs previous version: sigma was computed with np.std of the I and Q values
pooled together, which mixes two different means (I about ~Re(centroid), Q about
~Im(centroid)) and inflates sigma. Here sigma is taken along the centroid axis
after subtracting each cloud's own mean.

Reference numbers below are copied from the paper (Table V: R, F_ach, F^MF;
Table I: MF single-qubit fidelity). The paper's device is not ours; the test is
"same regime", not "identical". Note on Table V: Eq. C4 of the paper is F_ach = 0.5*[1+erf(sqrt(R/8))] = Phi(sqrt(R)/2),
which is the formula used here. The printed <S0>, <S1>, var(S) columns do NOT reproduce
the printed R through Eq. C3 (qubit 1: about 10.4 vs 26.8; qubits 3 and 5 similarly off by
~2.6-2.9x; qubit 2 close), cause unknown, so those three columns are not used. R is
cross-checked by the measured matched-filter fidelities in Table I, which track F^MF
(derived from R) to within 0.003 for qubits 1, 3, 4, 5 (0.033 for qubit 2).
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import numpy as np
from scipy.stats import norm

import glob

from iq_generator import IQDriftGenerator, DriftParams, DRIFT_PROFILES

# Lienhard et al. 2022, Table V (1 us, matched filter) and Table I (MF, 1Q).
REFERENCE = {
    "q1": dict(R=26.817, F_ach=0.995, F_MF_upper=0.974, F_MF_1Q=0.971),
    "q2": dict(R=3.001, F_ach=0.807, F_MF_upper=0.773, F_MF_1Q=0.740),
    "q3": dict(R=28.927, F_ach=0.996, F_MF_upper=0.965, F_MF_1Q=0.962),
    "q4": dict(R=19.953, F_ach=0.987, F_MF_upper=0.950, F_MF_1Q=0.946),
    "q5": dict(R=33.614, F_ach=0.998, F_MF_upper=0.979, F_MF_1Q=0.976),
}


def cloud_stats(iq, states):
    a, b = iq[states == 0], iq[states == 1]
    d = b.mean() - a.mean()
    u = d / abs(d)                                   # unit vector along centroid axis
    ax = lambda z: ((z - z.mean()) * np.conj(u)).real        # about own mean
    pp = lambda z: ((z - z.mean()) * np.conj(1j * u)).real
    sigma_axis = 0.5 * (ax(a).std() + ax(b).std())
    sigma_perp = 0.5 * (pp(a).std() + pp(b).std())
    sep = abs(d)
    # empirical nearest-centroid fidelity (perpendicular-bisector boundary)
    pred = np.where(np.abs(iq - a.mean()) < np.abs(iq - b.mean()), 0, 1)
    return dict(separation=sep, sigma_axis=sigma_axis, sigma_perp=sigma_perp,
                sep_over_sigma=sep / sigma_axis, R=(sep / sigma_axis) ** 2,
                F_gauss=norm.cdf(sep / sigma_axis / 2), F_empirical=float(np.mean(pred == states)))


def generator_stats(n_shots=200_000, t_hours=0.0, profile="generic"):
    gen = IQDriftGenerator(DriftParams(drift_profile=profile))
    try:
        iq, s = gen.generate_shots(n_shots=n_shots, t_hours=t_hours)
    except TypeError:
        iq, s = gen.generate_shots(n_shots, t_hours)
    return cloud_stats(iq, s)


def real_stats(data_dir, qubits=(0, 1, 2)):
    """R, Gaussian fidelity and empirical nearest-centroid error on every real IBM snapshot (iq_*.npz)."""
    files = sorted(glob.glob(os.path.join(data_dir, "iq_*.npz")))
    out = {}
    for q in qubits:
        rows = []
        for f in files:
            z = np.load(f)
            a, b = z[f"q{q}_state0"], z[f"q{q}_state1"]
            c = cloud_stats(np.concatenate([a, b]), np.r_[np.zeros(len(a), int), np.ones(len(b), int)])
            rows.append((c["R"], c["F_gauss"], 1 - c["F_empirical"]))
        out[q] = np.array(rows)
    return out, len(files)


def main():
    g = generator_stats()
    print("Generator at t=0 (statistics along the centroid axis, about each cloud's own mean)")
    print(f"  separation {g['separation']:.4f}, sigma_axis {g['sigma_axis']:.4f}, sigma_perp {g['sigma_perp']:.4f}")
    print(f"  sqrt(R)=sep/sigma {g['sep_over_sigma']:.2f}, R {g['R']:.1f}, F_gauss {g['F_gauss']:.4f}, F_empirical {g['F_empirical']:.4f}")
    print("\nLienhard et al. 2022 (copied from Tables V and I):")
    print("  qubit   sqrt(R)   R       F_ach   F^MF(upper)  F_MF(1Q, measured)")
    for q, r in REFERENCE.items():
        print(f"  {q}      {r['R']**.5:5.2f}   {r['R']:6.2f}   {r['F_ach']:.3f}   {r['F_MF_upper']:.3f}        {r['F_MF_1Q']:.3f}")
    Rs = [r["R"] for r in REFERENCE.values()]
    good = [r["R"] for k, r in REFERENCE.items() if k != "q2"]
    inside = min(good) <= g["R"] <= max(good)
    print(f"\nGenerator R = {g['R']:.1f}; paper's well-separated qubits span {min(good):.1f}-{max(good):.1f} "
          f"(all five: {min(Rs):.1f}-{max(Rs):.1f}). Inside the well-separated range: {inside}.")
    print("\nGenerator by qubit profile at t=0 vs real IBM snapshots (R is dimensionless, so raw ADC units do not matter):")
    data_dir = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), "..", "data")
    real, nfiles = real_stats(data_dir) if os.path.isdir(data_dir) else ({}, 0)
    if not nfiles:
        print(f"  (no real snapshots found in {data_dir}; pass the data directory as the first argument to enable this check)")
    for q in (0, 1, 2):
        gp = generator_stats(profile=f"q{q}")
        line = f"  q{q}: generator R {gp['R']:5.1f}, F_gauss {gp['F_gauss']:.4f}, empirical error {1-gp['F_empirical']:.4f}"
        if nfiles:
            r = real[q]
            line += (f" | real ({nfiles} snapshots) R median {np.median(r[:,0]):.1f} [{r[:,0].min():.1f}-{r[:,0].max():.1f}], "
                     f"F_gauss {np.median(r[:,1]):.4f}, empirical error {np.median(r[:,2]):.4f}")
        print(line)
    if nfiles:
        print("  Empirical error above (1 - F_gauss) means heavier-than-Gaussian tails (overlap, T1, state-prep) in the real data;\n"
              "  real centroids are the snapshot's own, 1000 shots/state, so single-snapshot error counts are small (~10-40 shots).")
    print("Note: at t=0 the generator's empirical fidelity matches its Gaussian value (clouds are Gaussian). The paper's\n"
          "measured MF fidelities are below F_ach; the cause was not checked here, so compare R and F_ach only.")

if __name__ == "__main__":
    main()
