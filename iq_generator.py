"""
IQ Drift Generator

Generates synthetic single-shot IQ readout data for a
superconducting-qubit readout project.

Version: 0.2

Features:
- Two IQ clouds for |0> and |1>
- Elliptical IQ noise
- Correlated I/Q noise
- Rotation drift
- Gain drift
- T1-inspired decay
- Decay drift
"""

from dataclasses import dataclass

import numpy as np


__version__ = "0.2"


@dataclass
class DriftParams:
    # ---------------------------------------------------------
    # Initial IQ cloud locations
    # ---------------------------------------------------------

    centroid0: complex = 0.0 + 0.0j
    centroid1: complex = 1.0 + 0.0j

    # ---------------------------------------------------------
    # IQ noise
    # ---------------------------------------------------------

    # Overall noise scale
    sigma: float = 0.15

    # Separate noise along I and Q
    sigma_i: float = 0.10
    sigma_q: float = 0.20

    # Correlation between I and Q
    #
    # 0.0 = no correlation
    # 1.0 = strong positive correlation
    iq_correlation: float = 0.30

    # ---------------------------------------------------------
    # Drift parameters
    # ---------------------------------------------------------

    # Rotation of the IQ geometry
    # degrees per hour
    rotation_rate_deg_per_hr: float = 0.4

    # Expansion/contraction of IQ geometry
    # fractional change per hour
    gain_drift_per_hr: float = 0.01

    # ---------------------------------------------------------
    # T1-inspired decay
    # ---------------------------------------------------------

    # Initial probability that a prepared |1> decays
    decay_prob_base: float = 0.03

    # Increase in decay probability per hour
    decay_drift_per_hr: float = 0.002

    # ---------------------------------------------------------
    # Random number generator
    # ---------------------------------------------------------

    rng_seed: int = 0


class IQDriftGenerator:

    def __init__(self, params: DriftParams = None):

        self.p = params or DriftParams()

        self._rng = np.random.default_rng(
            self.p.rng_seed
        )

    # =========================================================
    # Calculate drifted IQ geometry
    # =========================================================

    def _drifted_geometry(self, t_hours: float):

        p = self.p

        # -----------------------------------------------------
        # Rotation
        # -----------------------------------------------------

        theta = np.deg2rad(
            p.rotation_rate_deg_per_hr * t_hours
        )

        rot = np.exp(1j * theta)

        # -----------------------------------------------------
        # Midpoint between |0> and |1>
        # -----------------------------------------------------

        mid = (
            p.centroid0 +
            p.centroid1
        ) / 2

        # -----------------------------------------------------
        # Gain drift
        # -----------------------------------------------------

        gain = (
            1.0 +
            p.gain_drift_per_hr * t_hours
        )

        # -----------------------------------------------------
        # Apply gain + rotation
        # -----------------------------------------------------

        c0 = (
            mid +
            (p.centroid0 - mid)
            * gain
            * rot
        )

        c1 = (
            mid +
            (p.centroid1 - mid)
            * gain
            * rot
        )

        # -----------------------------------------------------
        # Decay probability
        # -----------------------------------------------------

        decay_prob = np.clip(
            p.decay_prob_base
            + p.decay_drift_per_hr * t_hours,
            0.0,
            0.9
        )

        return c0, c1, decay_prob

    # =========================================================
    # Generate single-shot IQ data
    # =========================================================

    def generate_shots(
        self,
        n_shots: int,
        t_hours: float,
        p_state1: float = 0.5
    ):

        # Get current drifted geometry
        c0, c1, decay_prob = (
            self._drifted_geometry(t_hours)
        )

        # -----------------------------------------------------
        # Randomly choose prepared qubit states
        # -----------------------------------------------------

        true_states = self._rng.binomial(
            1,
            p_state1,
            size=n_shots
        )

        # Array for complex IQ points
        iq_points = np.empty(
            n_shots,
            dtype=complex
        )

        # =====================================================
        # Generate each shot
        # =====================================================

        for i, s in enumerate(true_states):

            # -------------------------------------------------
            # Prepared |0>
            # -------------------------------------------------

            if s == 0:

                mean = c0

            # -------------------------------------------------
            # Prepared |1>
            # -------------------------------------------------

            else:

                # Decide whether this |1> shot decays
                if self._rng.random() < decay_prob:

                    # Random point between |1> and |0>
                    frac = self._rng.random()

                    mean = (
                        c1 +
                        frac * (c0 - c1)
                    )

                else:

                    mean = c1

            # =================================================
            # Generate elliptical correlated IQ noise
            # =================================================

            # Noise along I
            z_i = self._rng.normal(
                0,
                self.p.sigma_i
            )

            # Independent component for Q
            z_q_independent = self._rng.normal(
                0,
                self.p.sigma_q
            )

            # Correlated Q noise
            z_q = (
                self.p.iq_correlation * z_i
                +
                np.sqrt(
                    1 -
                    self.p.iq_correlation ** 2
                )
                * z_q_independent
            )

            # Combine I and Q into complex IQ value
            noise = z_i + 1j * z_q

            # Final measured IQ point
            iq_points[i] = mean + noise

        return iq_points, true_states