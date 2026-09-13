"""
controlled_drift.py

Tests different types of IQ readout drift separately.

Cases:
1. Rotation drift
2. Gain drift
3. Decay drift

For every case:
- Calibrate the discriminator at t = 0
- Keep the discriminator fixed
- Generate data at later times
- Measure how well the old discriminator performs
"""

import sys
import os

sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
)

import numpy as np
import matplotlib.pyplot as plt

from iq_generator import IQDriftGenerator, DriftParams


def get_centroids(iq, states):
    """Find the two IQ cloud centroids."""

    iq0 = iq[states == 0]
    iq1 = iq[states == 1]

    centroid0 = np.mean(iq0)
    centroid1 = np.mean(iq1)

    return centroid0, centroid1


def apply_discriminator(iq, centroid0, centroid1):
    """Use a fixed nearest-centroid discriminator."""

    predicted_states = np.where(
        np.abs(iq - centroid0) <
        np.abs(iq - centroid1),
        0,
        1
    )

    return predicted_states


def run_experiment(name, params):
    """
    Run one controlled drift experiment.

    The discriminator is calibrated only at t = 0.
    """

    print("\n" + "=" * 75)
    print(name.upper())
    print("=" * 75)

    # New generator for this experiment
    generator = IQDriftGenerator(params)

    # ---------------------------------------------------------
    # CALIBRATION AT t = 0
    # ---------------------------------------------------------

    iq_cal, states_cal = generator.generate_shots(
        n_shots=10000,
        t_hours=0
    )

    centroid0, centroid1 = get_centroids(
        iq_cal,
        states_cal
    )

    print("\nDiscriminator calibrated at t = 0 hr")

    print(f"|0> centroid = {centroid0}")
    print(f"|1> centroid = {centroid1}")

    # ---------------------------------------------------------
    # TEST AT DIFFERENT TIMES
    # ---------------------------------------------------------

    times = [0, 6, 12, 18, 24]

    fidelities = []

    for t in times:

        iq, states = generator.generate_shots(
            n_shots=10000,
            t_hours=t
        )

        predicted = apply_discriminator(
            iq,
            centroid0,
            centroid1
        )

        fidelity = np.mean(
            predicted == states
        )

        fidelities.append(fidelity * 100)

        print(
            f"Time = {t:2d} hr  |  "
            f"Fidelity = {fidelity * 100:.2f}%"
        )

    return times, fidelities


def main():

    # =========================================================
    # CASE 1: ROTATION DRIFT ONLY
    # =========================================================

    rotation_params = DriftParams(
        rotation_rate_deg_per_hr=0.4,
        gain_drift_per_hr=0.0,
        decay_prob_base=0.03,
        decay_drift_per_hr=0.0,
        rng_seed=1
    )

    rotation_times, rotation_fidelity = run_experiment(
        "Case 1 - Rotation Drift",
        rotation_params
    )

    # =========================================================
    # CASE 2: GAIN DRIFT ONLY
    # =========================================================

    gain_params = DriftParams(
        rotation_rate_deg_per_hr=0.0,
        gain_drift_per_hr=0.01,
        decay_prob_base=0.03,
        decay_drift_per_hr=0.0,
        rng_seed=2
    )

    gain_times, gain_fidelity = run_experiment(
        "Case 2 - Gain Drift",
        gain_params
    )

    # =========================================================
    # CASE 3: DECAY DRIFT ONLY
    # =========================================================

    decay_params = DriftParams(
        rotation_rate_deg_per_hr=0.0,
        gain_drift_per_hr=0.0,
        decay_prob_base=0.03,
        decay_drift_per_hr=0.002,
        rng_seed=3
    )

    decay_times, decay_fidelity = run_experiment(
        "Case 3 - Decay Drift",
        decay_params
    )

    # =========================================================
    # SUMMARY
    # =========================================================

    print("\n" + "=" * 75)
    print("COMPARISON")
    print("=" * 75)

    print(
        f"{'Time':>8}"
        f"{'Rotation':>15}"
        f"{'Gain':>15}"
        f"{'Decay':>15}"
    )

    print("-" * 75)

    for i, t in enumerate(rotation_times):

        print(
            f"{t:>7}h"
            f"{rotation_fidelity[i]:>14.2f}%"
            f"{gain_fidelity[i]:>14.2f}%"
            f"{decay_fidelity[i]:>14.2f}%"
        )

    # =========================================================
    # PLOT
    # =========================================================

    plt.figure(figsize=(9, 6))

    plt.plot(
        rotation_times,
        rotation_fidelity,
        marker="o",
        label="Rotation drift"
    )

    plt.plot(
        gain_times,
        gain_fidelity,
        marker="s",
        label="Gain drift"
    )

    plt.plot(
        decay_times,
        decay_fidelity,
        marker="^",
        label="Decay drift"
    )

    plt.xlabel("Time (hours)")
    plt.ylabel("Old discriminator fidelity (%)")

    plt.title(
        "Effect of Different Drift Mechanisms"
    )

    plt.grid(True)
    plt.legend()

    plt.tight_layout()

    plt.savefig(
        "controlled_drift_comparison.png",
        dpi=150
    )

    print(
        "\nSaved plot: "
        "controlled_drift_comparison.png"
    )


if __name__ == "__main__":
    main()