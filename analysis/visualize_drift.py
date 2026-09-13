"""
visualize_drift.py

Visualizes how IQ clouds move under drift.

The discriminator is calibrated at t = 0
and remains fixed at later times.
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
    """Find the IQ centroids."""

    iq0 = iq[states == 0]
    iq1 = iq[states == 1]

    return np.mean(iq0), np.mean(iq1)


def plot_case(name, params, filename):

    generator = IQDriftGenerator(params)

    # ---------------------------------------------------------
    # CALIBRATION AT t = 0
    # ---------------------------------------------------------

    iq0_cal, states_cal = generator.generate_shots(
        n_shots=5000,
        t_hours=0
    )

    centroid0, centroid1 = get_centroids(
        iq0_cal,
        states_cal
    )

    # Midpoint between calibration centroids
    midpoint = (centroid0 + centroid1) / 2

    # Direction from |0> to |1>
    direction = centroid1 - centroid0

    # ---------------------------------------------------------
    # DATA AT 0 AND 24 HOURS
    # ---------------------------------------------------------

    iq_0, states_0 = generator.generate_shots(
        n_shots=3000,
        t_hours=0
    )

    iq_24, states_24 = generator.generate_shots(
        n_shots=3000,
        t_hours=24
    )

    # ---------------------------------------------------------
    # PLOT
    # ---------------------------------------------------------

    fig, axes = plt.subplots(
        1,
        2,
        figsize=(12, 5)
    )

    datasets = [
        (axes[0], iq_0, states_0, "t = 0 hours"),
        (axes[1], iq_24, states_24, "t = 24 hours")
    ]

    for ax, iq, states, title in datasets:

        ax.scatter(
            iq[states == 0].real,
            iq[states == 0].imag,
            s=4,
            alpha=0.35,
            label="|0>"
        )

        ax.scatter(
            iq[states == 1].real,
            iq[states == 1].imag,
            s=4,
            alpha=0.35,
            label="|1>"
        )

        # Plot the OLD decision boundary
        #
        # For our simple two-centroid discriminator,
        # the boundary is perpendicular to the line
        # joining the two calibration centroids.

        boundary_direction = 1j * direction

        length = 2.0

        p1 = midpoint - boundary_direction / abs(direction) * length
        p2 = midpoint + boundary_direction / abs(direction) * length

        ax.plot(
            [p1.real, p2.real],
            [p1.imag, p2.imag],
            linestyle="--",
            label="Old boundary"
        )

        ax.set_title(title)
        ax.set_xlabel("I")
        ax.set_ylabel("Q")
        ax.set_aspect("equal")
        ax.legend()

    fig.suptitle(name)

    plt.tight_layout()

    plt.savefig(
        filename,
        dpi=150
    )

    print(f"Saved: {filename}")


def main():

    # ---------------------------------------------------------
    # ROTATION ONLY
    # ---------------------------------------------------------

    rotation_params = DriftParams(
        rotation_rate_deg_per_hr=0.4,
        gain_drift_per_hr=0.0,
        decay_prob_base=0.03,
        decay_drift_per_hr=0.0,
        rng_seed=10
    )

    plot_case(
        "Rotation Drift: Old Discriminator",
        rotation_params,
        "rotation_visual.png"
    )

    # ---------------------------------------------------------
    # DECAY ONLY
    # ---------------------------------------------------------

    decay_params = DriftParams(
        rotation_rate_deg_per_hr=0.0,
        gain_drift_per_hr=0.0,
        decay_prob_base=0.03,
        decay_drift_per_hr=0.002,
        rng_seed=20
    )

    plot_case(
        "Decay Drift: Old Discriminator",
        decay_params,
        "decay_visual.png"
    )


if __name__ == "__main__":
    main()