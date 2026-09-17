"""
IQ Drift Generator

Generates synthetic superconducting-qubit IQ readout data.

Version: 1.4

Features:
- Two IQ clouds for |0> and |1>
- Elliptical IQ noise
- Correlated I/Q noise
- Baseline rotation drift
- Baseline gain/separation drift
- Smooth correlated stochastic drift
- Configurable qubit-specific drift profiles
- Common-mode centroid wandering
- T1-inspired decay
- Decay drift
- Time-dependent I/Q readout traces

The noise parameters are calibrated from 31 real IBM IQ datasets.

The drift profiles are approximate models based on approximately
140 hours of real IBM measurements.

Available profiles:
    "generic"
    "q0"
    "q1"
    "q2"

The generic profile provides a general-purpose drift model.

The q0/q1/q2 profiles provide approximate qubit-specific drift
and noise behavior observed in the real IBM dataset.

The default T1-inspired decay is disabled for kerneled single-shot
validation because the real dataset does not provide a time-resolved
T1 trajectory. Decay can still be enabled explicitly by setting
`decay_prob_base` and/or `decay_drift_per_hr` in DriftParams.

Version 1.4 also provides explicit raw-IQ output helpers for the
shared Person 4 hardware pipeline. The internal scientific model
remains normalized; raw output is centered, scaled by the
qubit-specific real-data separation scale, and multiplied by 2**28.

Functions:
    generate_shots()
        Generates one IQ point per measurement shot.

    generate_traces()
        Generates I(t) and Q(t) traces for every measurement shot.
"""

from dataclasses import dataclass

import numpy as np


__version__ = "1.4"


# =============================================================
# Drift profile definitions
# =============================================================

DRIFT_PROFILES = {

    # ---------------------------------------------------------
    # Generic profile
    # ---------------------------------------------------------

    "generic": {
        "rotation_rate_deg_per_hr": 0.02,
        "gain_drift_per_hr": -0.0007,

        "stochastic_gain_amplitude": 0.06,
        "stochastic_rotation_amplitude_deg": 1.5,
        "stochastic_centroid_wander_amplitude": 0.03,
    },

    # ---------------------------------------------------------
    # Q0
    #
    # Real data:
    # separation decreased strongly over ~100 hours.
    # Angle changed only slightly.
    # Midpoint movement was relatively large.
    # ---------------------------------------------------------

    "q0": {
        # Tuned against 31 datasets; nominal stochastic strength = 1.0
        "rotation_rate_deg_per_hr": 0.0039,
        "gain_drift_per_hr": -0.0021,

        "stochastic_gain_amplitude": 0.08,
        "stochastic_rotation_amplitude_deg": 1.0,
        "stochastic_centroid_wander_amplitude": 0.125,

        # Q0 noise profile calibrated from 31 real datasets
        "sigma_i": 0.2341,
        "sigma_q": 0.1965,
        "iq_correlation": 0.0211,
    },

    # ---------------------------------------------------------
    # Q1
    #
    # Real data:
    # separation was almost stable.
    # Angle changed more strongly.
    # Midpoint movement was comparatively small.
    # ---------------------------------------------------------

    "q1": {
        # Tuned against 31 datasets; nominal stochastic strength = 1.0
        "rotation_rate_deg_per_hr": 0.1895,
        "gain_drift_per_hr": -0.00032,

        "stochastic_gain_amplitude": 0.03,
        "stochastic_rotation_amplitude_deg": 2.0,
        "stochastic_centroid_wander_amplitude": 0.184,

        # Q1 noise profile calibrated from 31 real datasets
        "sigma_i": 0.2411,
        "sigma_q": 0.2149,
        "iq_correlation": 0.0291,
    },

    # ---------------------------------------------------------
    # Q2
    #
    # Real data:
    # separation was almost stable.
    # Angle change was small.
    # Midpoint movement was moderate.
    # ---------------------------------------------------------

    "q2": {
        # Tuned against 31 datasets; nominal stochastic strength = 1.0
        "rotation_rate_deg_per_hr": -0.0163,
        "gain_drift_per_hr": -0.00013,

        "stochastic_gain_amplitude": 0.03,
        "stochastic_rotation_amplitude_deg": 0.75,
        "stochastic_centroid_wander_amplitude": 0.048,

        # Q2 noise profile calibrated from 31 real datasets
        "sigma_i": 0.1641,
        "sigma_q": 0.1517,
        "iq_correlation": 0.0115,
    },
}


# =============================================================
# Raw IQ scale profiles
# =============================================================
#
# Person 4's shared hardware representation uses:
#
#     raw IQ / (2**28) -> Q1.15
#
# The internal generator uses a nominal state separation of 1.0.
# These factors convert that internal separation to the observed
# initial real-data separation in the shared normalized scale.
#
# Approximate initial real separations:
#     Q0 ~ 1.309e8 raw units -> 0.4876 * 2**28
#     Q1 ~ 7.498e7 raw units -> 0.2793 * 2**28
#     Q2 ~ 2.133e8 raw units -> 0.7946 * 2**28
#
# The regular generate_shots()/generate_traces() functions remain
# in normalized units for backward compatibility. Use the explicit
# *_raw() helpers when preparing data for Person 4.
#

ABSOLUTE_IQ_SEPARATION_SCALE = {
    "generic": 1.0,
    "q0": 0.4876,
    "q1": 0.2793,
    "q2": 0.7946,
}

RAW_IQ_SCALE = 2 ** 28


@dataclass
class DriftParams:

    # =========================================================
    # Initial IQ cloud locations
    # =========================================================

    centroid0: complex = 0.0 + 0.0j
    centroid1: complex = 1.0 + 0.0j

    # =========================================================
    # IQ noise
    # =========================================================

    # Kept for compatibility with earlier versions
    sigma: float = 0.15

    # Calibrated from 31 real IBM datasets
    sigma_i: float = 0.2131
    sigma_q: float = 0.1877

    # Calibrated from 31 real IBM datasets
    iq_correlation: float = 0.0181

    # =========================================================
    # Drift profile
    # =========================================================

    # Available:
    #
    # "generic"
    # "q0"
    # "q1"
    # "q2"
    #
    drift_profile: str = "generic"

    # =========================================================
    # Baseline drift
    #
    # These values are used when a parameter is not overridden
    # by the selected profile.
    # =========================================================

    rotation_rate_deg_per_hr: float = 0.02
    gain_drift_per_hr: float = -0.0007

    # =========================================================
    # Smooth stochastic drift
    # =========================================================

    # 0.0 = stochastic drift disabled
    # 1.0 = normal stochastic drift
    # >1.0 = stronger stochastic drift
    stochastic_drift_strength: float = 1.0

    # Generic defaults
    stochastic_gain_amplitude: float = 0.06
    stochastic_rotation_amplitude_deg: float = 1.5
    stochastic_centroid_wander_amplitude: float = 0.03

    # Correlation time of the hidden drift process
    stochastic_correlation_time_hr: float = 18.0

    # Time resolution of the hidden stochastic process
    stochastic_grid_step_hr: float = 1.0

    # Maximum supported simulation time
    stochastic_max_hours: float = 720.0

    # =========================================================
    # Decay parameters
    # =========================================================

    # Phenomenological only.
    #
    # The real kerneled single-shot dataset does not directly
    # provide a time-resolved T1 trajectory.
    #
    # Disabled by default for the main kerneled single-shot
    # validation. It can be enabled explicitly when desired.
    decay_prob_base: float = 0.0

    decay_drift_per_hr: float = 0.0

    # =========================================================
    # Readout trace parameters
    # =========================================================

    trace_duration_ns: float = 1000.0
    sample_interval_ns: float = 2.0
    response_tau_ns: float = 50.0

    # =========================================================
    # Random number generator
    # =========================================================

    rng_seed: int = 0


class IQDriftGenerator:

    def __init__(self, params: DriftParams = None):

        self.p = params or DriftParams()

        # -----------------------------------------------------
        # Validate profile
        # -----------------------------------------------------

        if self.p.drift_profile not in DRIFT_PROFILES:

            raise ValueError(
                "Unknown drift profile: "
                f"{self.p.drift_profile}. "
                "Available profiles: "
                f"{list(DRIFT_PROFILES.keys())}"
            )

        # -----------------------------------------------------
        # Main RNG for IQ shots and noise
        # -----------------------------------------------------

        self._rng = np.random.default_rng(
            self.p.rng_seed
        )

        # -----------------------------------------------------
        # Separate RNG for slow drift
        # -----------------------------------------------------

        self._drift_rng = np.random.default_rng(
            self.p.rng_seed + 1001
        )

        # -----------------------------------------------------
        # Create stochastic drift processes
        # -----------------------------------------------------

        self._drift_grid = self._create_drift_grid()

        self._gain_process = (
            self._create_correlated_process()
        )

        self._rotation_process = (
            self._create_correlated_process()
        )

        self._centroid_i_process = (
            self._create_correlated_process()
        )

        self._centroid_q_process = (
            self._create_correlated_process()
        )

    # =========================================================
    # Profile parameter lookup
    # =========================================================

    def _profile_value(
        self,
        parameter_name: str
    ):

        profile = DRIFT_PROFILES[
            self.p.drift_profile
        ]

        if parameter_name in profile:

            return profile[
                parameter_name
            ]

        return getattr(
            self.p,
            parameter_name
        )

    # =========================================================
    # Create stochastic drift time grid
    # =========================================================

    # =========================================================
    # Raw IQ scale lookup
    # =========================================================

    def _absolute_iq_separation_scale(self):

        return ABSOLUTE_IQ_SEPARATION_SCALE[
            self.p.drift_profile
        ]

    # =========================================================
    # Convert normalized complex IQ to raw IQ
    # =========================================================

    def _normalized_to_raw_iq(
        self,
        iq
    ):
        """
        Convert internal IQ coordinates into the raw arbitrary-unit
        representation expected by Person 4.

        Internal convention:
            |0> ~= 0
            |1> ~= 1

        Raw normalized-by-2^28 convention:
            |0> ~= -S/2
            |1> ~= +S/2

        where S is the profile-specific initial separation scale.
        """

        separation_scale = (
            self._absolute_iq_separation_scale()
        )

        centered = (
            iq - 0.5
        )

        return (
            centered
            * separation_scale
            * RAW_IQ_SCALE
        )

    def _create_drift_grid(self):

        p = self.p

        n_points = int(
            np.ceil(
                p.stochastic_max_hours
                / p.stochastic_grid_step_hr
            )
        ) + 1

        return (
            np.arange(n_points)
            * p.stochastic_grid_step_hr
        )

    # =========================================================
    # Generate smooth correlated random process
    # =========================================================

    def _create_correlated_process(self):

        p = self.p

        n_points = len(
            self._drift_grid
        )

        correlation_time = max(
            p.stochastic_correlation_time_hr,
            p.stochastic_grid_step_hr
        )

        dt = p.stochastic_grid_step_hr

        # AR(1)-style correlation coefficient
        alpha = np.exp(
            -dt / correlation_time
        )

        innovation_std = np.sqrt(
            1.0 - alpha ** 2
        )

        process = np.empty(
            n_points,
            dtype=float
        )

        process[0] = (
            self._drift_rng.normal()
        )

        for i in range(1, n_points):

            innovation = (
                self._drift_rng.normal()
            )

            process[i] = (
                alpha * process[i - 1]
                + innovation_std * innovation
            )

        # Make stochastic contribution start at zero.
        process = (
            process - process[0]
        )

        max_abs = np.max(
            np.abs(process)
        )

        if max_abs > 0:

            process = (
                process / max_abs
            )

        return process

    # =========================================================
    # Evaluate stochastic process
    # =========================================================

    def _evaluate_correlated_process(
        self,
        process,
        t_hours
    ):

        if t_hours < 0:

            raise ValueError(
                "t_hours must be >= 0."
            )

        if (
            t_hours
            > self.p.stochastic_max_hours
        ):

            raise ValueError(
                "t_hours exceeds "
                "stochastic_max_hours."
            )

        return np.interp(
            t_hours,
            self._drift_grid,
            process
        )

    # =========================================================
    # Calculate stochastic drift components
    # =========================================================

    def _stochastic_components(
        self,
        t_hours
    ):

        p = self.p

        strength = (
            p.stochastic_drift_strength
        )

        # -----------------------------------------------------
        # Gain wandering
        # -----------------------------------------------------

        gain_wave = (
            self._evaluate_correlated_process(
                self._gain_process,
                t_hours
            )
        )

        stochastic_gain = (
            strength
            * self._profile_value(
                "stochastic_gain_amplitude"
            )
            * gain_wave
        )

        # -----------------------------------------------------
        # Rotation wandering
        # -----------------------------------------------------

        rotation_wave = (
            self._evaluate_correlated_process(
                self._rotation_process,
                t_hours
            )
        )

        stochastic_rotation_deg = (
            strength
            * self._profile_value(
                "stochastic_rotation_amplitude_deg"
            )
            * rotation_wave
        )

        # -----------------------------------------------------
        # Centroid I wandering
        # -----------------------------------------------------

        centroid_i_wave = (
            self._evaluate_correlated_process(
                self._centroid_i_process,
                t_hours
            )
        )

        centroid_i_shift = (
            strength
            * self._profile_value(
                "stochastic_centroid_wander_amplitude"
            )
            * centroid_i_wave
        )

        # -----------------------------------------------------
        # Centroid Q wandering
        # -----------------------------------------------------

        centroid_q_wave = (
            self._evaluate_correlated_process(
                self._centroid_q_process,
                t_hours
            )
        )

        centroid_q_shift = (
            strength
            * self._profile_value(
                "stochastic_centroid_wander_amplitude"
            )
            * centroid_q_wave
        )

        centroid_shift = (
            centroid_i_shift
            + 1j * centroid_q_shift
        )

        return (
            stochastic_gain,
            stochastic_rotation_deg,
            centroid_shift
        )

    # =========================================================
    # Calculate drifted IQ geometry
    # =========================================================

    def _drifted_geometry(
        self,
        t_hours: float
    ):

        p = self.p

        # -----------------------------------------------------
        # Baseline rotation
        # -----------------------------------------------------

        rotation_rate = (
            self._profile_value(
                "rotation_rate_deg_per_hr"
            )
        )

        baseline_theta_deg = (
            rotation_rate
            * t_hours
        )

        # -----------------------------------------------------
        # Stochastic drift
        # -----------------------------------------------------

        (
            stochastic_gain,
            stochastic_rotation_deg,
            centroid_shift
        ) = self._stochastic_components(
            t_hours
        )

        total_theta_deg = (
            baseline_theta_deg
            + stochastic_rotation_deg
        )

        theta = np.deg2rad(
            total_theta_deg
        )

        rot = np.exp(
            1j * theta
        )

        # -----------------------------------------------------
        # Initial midpoint
        # -----------------------------------------------------

        mid = (
            p.centroid0
            + p.centroid1
        ) / 2.0

        # -----------------------------------------------------
        # Baseline gain
        # -----------------------------------------------------

        gain_rate = (
            self._profile_value(
                "gain_drift_per_hr"
            )
        )

        baseline_gain = (
            1.0
            + gain_rate
            * t_hours
        )

        # -----------------------------------------------------
        # Total gain
        # -----------------------------------------------------

        gain = (
            baseline_gain
            + stochastic_gain
        )

        gain = max(
            gain,
            0.1
        )

        # -----------------------------------------------------
        # Drifted centroids
        # -----------------------------------------------------

        c0 = (
            mid
            + (
                p.centroid0
                - mid
            )
            * gain
            * rot
        )

        c1 = (
            mid
            + (
                p.centroid1
                - mid
            )
            * gain
            * rot
        )

        # -----------------------------------------------------
        # Common-mode wandering
        # -----------------------------------------------------

        c0 = (
            c0
            + centroid_shift
        )

        c1 = (
            c1
            + centroid_shift
        )

        # -----------------------------------------------------
        # Drifted decay probability
        # -----------------------------------------------------

        decay_prob = np.clip(
            p.decay_prob_base
            + p.decay_drift_per_hr
            * t_hours,
            0.0,
            0.9
        )

        return (
            c0,
            c1,
            decay_prob,
            rot
        )

    # =========================================================
    # Generate correlated IQ noise
    # =========================================================

    def _generate_noise(
        self,
        n_samples
    ):

        # Use profile-specific noise for q0/q1/q2.
        # The generic profile intentionally falls back to the
        # DriftParams values so old custom parameter usage remains
        # compatible.
        sigma_i = self._profile_value(
            "sigma_i"
        )

        sigma_q = self._profile_value(
            "sigma_q"
        )

        iq_correlation = self._profile_value(
            "iq_correlation"
        )

        z_i = self._rng.normal(
            0,
            sigma_i,
            size=n_samples
        )

        z_q_independent = self._rng.normal(
            0,
            sigma_q,
            size=n_samples
        )

        z_q = (
            iq_correlation
            * z_i
            +
            np.sqrt(
                1
                - iq_correlation ** 2
            )
            * z_q_independent
        )

        return (
            z_i
            + 1j * z_q
        )

    # =========================================================
    # Generate single-shot IQ points
    # =========================================================

    def generate_shots(
        self,
        n_shots: int,
        t_hours: float,
        p_state1: float = 0.5
    ):

        (
            c0,
            c1,
            decay_prob,
            rot
        ) = self._drifted_geometry(
            t_hours
        )

        true_states = self._rng.binomial(
            1,
            p_state1,
            size=n_shots
        )

        iq_points = np.empty(
            n_shots,
            dtype=complex
        )

        for i, state in enumerate(
            true_states
        ):

            if state == 0:

                mean = c0

            else:

                if (
                    self._rng.random()
                    < decay_prob
                ):

                    frac = (
                        self._rng.random()
                    )

                    mean = (
                        c1
                        + frac
                        * (c0 - c1)
                    )

                else:

                    mean = c1

            noise = (
                self._generate_noise(1)[0]
            )

            noise = (
                noise
                * rot
            )

            iq_points[i] = (
                mean
                + noise
            )

        return (
            iq_points,
            true_states
        )

    # =========================================================
    # Generate full I(t), Q(t) traces
    # =========================================================

    def generate_traces(
        self,
        n_shots: int,
        t_hours: float,
        p_state1: float = 0.5
    ):

        p = self.p

        n_samples = int(
            p.trace_duration_ns
            / p.sample_interval_ns
        )

        times = (
            np.arange(n_samples)
            * p.sample_interval_ns
        )

        (
            c0,
            c1,
            decay_prob,
            rot
        ) = self._drifted_geometry(
            t_hours
        )

        true_states = self._rng.binomial(
            1,
            p_state1,
            size=n_shots
        )

        iq_traces = np.empty(
            (
                n_shots,
                n_samples
            ),
            dtype=complex
        )

        response = (
            1.0
            - np.exp(
                -times
                / p.response_tau_ns
            )
        )

        for shot in range(
            n_shots
        ):

            state = (
                true_states[shot]
            )

            if state == 0:

                mean_trace = (
                    c0
                    * response
                )

            else:

                mean_trace = (
                    c1
                    * response
                )

                if (
                    self._rng.random()
                    < decay_prob
                ):

                    decay_index = (
                        self._rng.integers(
                            1,
                            n_samples
                        )
                    )

                    mean_trace[
                        :decay_index
                    ] = (
                        c1
                        * response[
                            :decay_index
                        ]
                    )

                    remaining_response = (
                        response[
                            decay_index:
                        ]
                    )

                    mean_trace[
                        decay_index:
                    ] = (
                        c1
                        * response[
                            decay_index
                        ]
                        + (
                            c0 - c1
                        )
                        * remaining_response
                    )

            noise = (
                self._generate_noise(
                    n_samples
                )
            )

            noise = (
                noise
                * rot
            )

            iq_traces[shot] = (
                mean_trace
                + noise
            )

        I = (
            iq_traces.real
        )

        Q = (
            iq_traces.imag
        )

        return (
            I,
            Q,
            true_states
        )

    # =========================================================
    # Generate raw-scale single-shot IQ points
    # =========================================================

    def generate_shots_raw(
        self,
        n_shots: int,
        t_hours: float,
        p_state1: float = 0.5
    ):
        """
        Generate single-shot IQ points in raw arbitrary units
        for Person 4's fixed-point pipeline.
        """

        iq_points, true_states = (
            self.generate_shots(
                n_shots=n_shots,
                t_hours=t_hours,
                p_state1=p_state1,
            )
        )

        raw_iq = (
            self._normalized_to_raw_iq(
                iq_points
            )
        )

        return (
            raw_iq,
            true_states
        )

    # =========================================================
    # Generate raw-scale full I(t), Q(t) traces
    # =========================================================

    def generate_traces_raw(
        self,
        n_shots: int,
        t_hours: float,
        p_state1: float = 0.5
    ):
        """
        Generate full I(t), Q(t) traces in raw arbitrary units.
        """

        I, Q, true_states = (
            self.generate_traces(
                n_shots=n_shots,
                t_hours=t_hours,
                p_state1=p_state1,
            )
        )

        iq_traces = (
            I
            + 1j * Q
        )

        raw_traces = (
            self._normalized_to_raw_iq(
                iq_traces
            )
        )

        return (
            raw_traces.real,
            raw_traces.imag,
            true_states
        )


# =============================================================
# v1.4 raw-scale self-test
# =============================================================

if __name__ == "__main__":

    print("=" * 70)
    print(
        f"IQDriftGenerator version {__version__}"
    )
    print("=" * 70)

    for profile_name in [
        "q0",
        "q1",
        "q2",
    ]:

        generator = IQDriftGenerator(
            DriftParams(
                drift_profile=profile_name,
                stochastic_drift_strength=1.0,
                rng_seed=42,
            )
        )

        raw_iq, _ = (
            generator.generate_shots_raw(
                n_shots=10000,
                t_hours=0.0,
                p_state1=0.5,
            )
        )

        scale = (
            ABSOLUTE_IQ_SEPARATION_SCALE[
                profile_name
            ]
        )

        print()
        print(
            f"Profile: {profile_name}"
        )

        print(
            f"Separation scale: {scale:.4f}"
        )

        print(
            f"Expected raw separation: "
            f"{scale * RAW_IQ_SCALE:.3e}"
        )

        print(
            f"Raw I range: "
            f"[{raw_iq.real.min():+.3e}, "
            f"{raw_iq.real.max():+.3e}]"
        )

        print(
            f"Raw Q range: "
            f"[{raw_iq.imag.min():+.3e}, "
            f"{raw_iq.imag.max():+.3e}]"
        )

        raw_max = max(
            np.max(np.abs(raw_iq.real)),
            np.max(np.abs(raw_iq.imag))
        )

        print(
            f"Raw max |I/Q|: "
            f"{raw_max:.3e}"
        )

    print()
    print("=" * 70)
    print("RAW-SCALE SELF-TEST COMPLETE")
    print("=" * 70)
