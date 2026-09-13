"""
analyze_iq_data.py

Tests how a discriminator calibrated at t = 0
performs as the IQ readout drifts over time.

Important:
The discriminator is NOT recalibrated at later times.

This simulates a stale discriminator.
"""

import sys
import os

sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
)

import numpy as np
import matplotlib.pyplot as plt

from iq_generator import IQDriftGenerator


def calculate_cloud_properties(iq, states):
    """Calculate properties of the two IQ clouds."""

    iq0 = iq[states == 0]
    iq1 = iq[states == 1]

    centroid0 = np.mean(iq0)
    centroid1 = np.mean(iq1)

    separation = abs(centroid1 - centroid0)

    sigma0 = np.sqrt(
        np.var(iq0.real) + np.var(iq0.imag)
    )

    sigma1 = np.sqrt(
        np.var(iq1.real) + np.var(iq1.imag)
    )

    average_sigma = (sigma0 + sigma1) / 2

    separation_over_sigma = separation / average_sigma

    return {
        "centroid0": centroid0,
        "centroid1": centroid1,
        "separation": separation,
        "sigma0": sigma0,
        "sigma1": sigma1,
        "average_sigma": average_sigma,
        "separation_over_sigma": separation_over_sigma,
    }


def apply_discriminator(iq, centroid0, centroid1):
    """
    Apply a fixed discriminator.

    The centroids are deliberately NOT recalculated.
    """

    predicted_states = np.where(
        np.abs(iq - centroid0) < np.abs(iq - centroid1),
        0,
        1
    )

    return predicted_states


def main():

    generator = IQDriftGenerator()

    times = [0, 6, 12, 18, 24]

    # ---------------------------------------------------------
    # STEP 1: Calibrate discriminator at t = 0
    # ---------------------------------------------------------

    iq_cal, states_cal = generator.generate_shots(
        n_shots=10000,
        t_hours=0
    )

    calibration = calculate_cloud_properties(
        iq_cal,
        states_cal
    )

    centroid0_cal = calibration["centroid0"]
    centroid1_cal = calibration["centroid1"]

    print("\n" + "=" * 75)
    print("STALE DISCRIMINATOR DRIFT ANALYSIS")
    print("=" * 75)

    print("\nDiscriminator calibrated at t = 0 hr")

    print(f"  |0> centroid: {centroid0_cal}")
    print(f"  |1> centroid: {centroid1_cal}")

    # ---------------------------------------------------------
    # STEP 2: Test the SAME discriminator over time
    # ---------------------------------------------------------

    results = []

    for t in times:

        iq, states = generator.generate_shots(
            n_shots=10000,
            t_hours=t
        )

        # Measure current cloud properties
        properties = calculate_cloud_properties(
            iq,
            states
        )

        # IMPORTANT:
        # Use the ORIGINAL t=0 discriminator
        predicted_states = apply_discriminator(
            iq,
            centroid0_cal,
            centroid1_cal
        )

        fidelity = np.mean(
            predicted_states == states
        )

        results.append({
            "time": t,
            "separation": properties["separation"],
            "average_sigma": properties["average_sigma"],
            "separation_over_sigma":
                properties["separation_over_sigma"],
            "fidelity": fidelity,
        })

        print(f"\nTime = {t:2d} hr")

        print(
            f"  Current separation:     "
            f"{properties['separation']:.4f}"
        )

        print(
            f"  Current average sigma:  "
            f"{properties['average_sigma']:.4f}"
        )

        print(
            f"  Current separation/sigma: "
            f"{properties['separation_over_sigma']:.4f}"
        )

        print(
            f"  OLD discriminator fidelity: "
            f"{fidelity * 100:.2f}%"
        )

    # ---------------------------------------------------------
    # STEP 3: Summary
    # ---------------------------------------------------------

    print("\n" + "=" * 75)
    print("SUMMARY")
    print("=" * 75)

    print(
        f"{'Time':>8} "
        f"{'Separation':>14} "
        f"{'Avg Sigma':>14} "
        f"{'Sep/Sigma':>14} "
        f"{'OLD Fidelity':>16}"
    )

    print("-" * 75)

    for r in results:

        print(
            f"{r['time']:>7}h "
            f"{r['separation']:>14.4f} "
            f"{r['average_sigma']:>14.4f} "
            f"{r['separation_over_sigma']:>14.4f} "
            f"{r['fidelity'] * 100:>15.2f}%"
        )

    # ---------------------------------------------------------
    # STEP 4: Plot fidelity
    # ---------------------------------------------------------

    fidelities = [
        r["fidelity"] * 100
        for r in results
    ]

    plt.figure(figsize=(8, 5))

    plt.plot(
        times,
        fidelities,
        marker="o"
    )

    plt.xlabel("Time (hours)")
    plt.ylabel("Assignment fidelity (%)")
    plt.title(
        "Performance of a Fixed Discriminator Under Readout Drift"
    )

    plt.grid(True)

    plt.tight_layout()

    plt.savefig(
        "stale_discriminator_fidelity.png",
        dpi=150
    )

    print(
        "\nSaved plot: "
        "stale_discriminator_fidelity.png"
    )


if __name__ == "__main__":
    main()