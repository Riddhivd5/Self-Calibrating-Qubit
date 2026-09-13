"""
validate_lienhard.py

Week 2 task: check that IQDriftGenerator's output at t=0 is in a
physically plausible regime by comparing summary statistics against
Lienhard et al., "Deep-Neural-Network Discrimination of Multiplexed
Superconducting-Qubit States," Phys. Rev. Applied 17, 014024 (2022).

HOW TO USE THIS FILE
---------------------
1. Open the paper (arXiv:2102.12481 / PRApplied 17, 014024) and find
   their IQ-plane readout histograms (Fig. 2-ish) and/or their
   assignment-fidelity table. Read off, for one representative qubit:
     - the separation between the |0> and |1> cloud centroids
     - the cloud standard deviation (noise)
     - the reported assignment fidelity (or error rate)
2. Fill in the REFERENCE_STATS dict below with those real numbers.
3. Run this script. It generates shots from IQDriftGenerator at
   t=0, computes the same statistics, and prints both side by side.
4. If your generator's numbers are wildly off, adjust `sigma` and/or
   the centroid separation in DriftParams (in iq_generator.py) until
   they're in a comparable regime. They don't need to match exactly
   -- Lienhard's device isn't yours -- just be plausible.

DO NOT invent "real" numbers here without reading the paper -- the
whole point of this step is to ground the generator in a real
measurement, not to rubber-stamp default values.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import numpy as np
from iq_generator import IQDriftGenerator, DriftParams


# ---------------------------------------------------------------
# FILL THIS IN after reading Lienhard et al. 2022.
# Leave as None until you have the real numbers -- the script will
# tell you clearly if you haven't filled it in yet.
# ---------------------------------------------------------------
REFERENCE_STATS = {
    "separation_over_sigma": None,   # e.g. cloud-center distance / cloud std dev
    "assignment_fidelity": None,     # e.g. 0.98 (98%)
    "notes": "Fill in from Fig. 2 / Table I of Lienhard et al. 2022",
}


def compute_generator_stats(n_shots=5000, t_hours=0.0):
    """Compute the same-style summary statistics from our fake generator."""
    gen = IQDriftGenerator()
    iq, states = gen.generate_shots(n_shots=n_shots, t_hours=t_hours)

    c0_points = iq[states == 0]
    c1_points = iq[states == 1]

    c0_mean = c0_points.mean()
    c1_mean = c1_points.mean()
    separation = abs(c1_mean - c0_mean)

    sigma0 = np.std(np.concatenate([c0_points.real, c0_points.imag]))
    sigma1 = np.std(np.concatenate([c1_points.real, c1_points.imag]))
    sigma = (sigma0 + sigma1) / 2

    separation_over_sigma = separation / sigma if sigma > 0 else float("inf")

    predicted = np.where(np.abs(iq - c0_mean) < np.abs(iq - c1_mean), 0, 1)
    assignment_fidelity = np.mean(predicted == states)

    return {
        "separation_over_sigma": separation_over_sigma,
        "assignment_fidelity": assignment_fidelity,
    }


def main():
    gen_stats = compute_generator_stats()

    print("=" * 60)
    print("Validation against Lienhard et al. (2022)")
    print("=" * 60)

    for key in ["separation_over_sigma", "assignment_fidelity"]:
        ref_val = REFERENCE_STATS.get(key)
        gen_val = gen_stats.get(key)
        ref_str = f"{ref_val:.3f}" if ref_val is not None else "NOT FILLED IN YET"
        print(f"{key:28s} | generator: {gen_val:.3f} | paper: {ref_str}")

    if any(v is None for k, v in REFERENCE_STATS.items() if k != "notes"):
        print("\n[!] REFERENCE_STATS is incomplete. Open the Lienhard paper,")
        print("    read off the real numbers, and fill in the dict at the")
        print("    top of this file before treating this as 'validated'.")
    else:
        print("\nCompare the two columns above -- they should be in the same")
        print("ballpark (same order of magnitude), not identical.")


if __name__ == "__main__":
    main()