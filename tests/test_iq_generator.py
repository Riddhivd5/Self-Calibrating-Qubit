"""
test_iq_generator.py

Minimal sanity tests for IQDriftGenerator.

Run with:
    pytest
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import numpy as np
from iq_generator import IQDriftGenerator, DriftParams


def test_shots_shape():
    gen = IQDriftGenerator()

    iq, states = gen.generate_shots(
        n_shots=500,
        t_hours=0
    )

    assert iq.shape == (500,)
    assert states.shape == (500,)


def test_state0_near_centroid_at_t0():
    params = DriftParams(
        sigma=0.05
    )

    gen = IQDriftGenerator(params)

    iq, states = gen.generate_shots(
        n_shots=2000,
        t_hours=0
    )

    zeros = iq[states == 0]

    mean_pos = zeros.mean()

    # Should land close to centroid0
    assert abs(mean_pos - params.centroid0) < 0.05


def test_drift_moves_centroids():
    gen = IQDriftGenerator()

    iq_early, states_early = gen.generate_shots(
        n_shots=3000,
        t_hours=0,
        p_state1=0.0
    )

    iq_late, states_late = gen.generate_shots(
        n_shots=3000,
        t_hours=48,
        p_state1=0.0
    )

    mean_early = iq_early.mean()
    mean_late = iq_late.mean()

    # After 48 hours of drift, the |0> centroid
    # should have moved measurably.
    assert abs(mean_early - mean_late) > 0.01


def test_decay_bridge_exists():
    # Use a high decay probability so this test
    # reliably checks that the decay mechanism works.
    params = DriftParams(
        decay_prob_base=0.50,
        decay_drift_per_hr=0.00
    )

    gen = IQDriftGenerator(params)

    iq, states = gen.generate_shots(
        n_shots=5000,
        t_hours=24,
        p_state1=1.0
    )

    # _drifted_geometry() returns:
    # c0, c1, decay_prob, rot
    c0, c1, _, _ = gen._drifted_geometry(24)

    dist_to_0 = np.abs(iq - c0)
    dist_to_1 = np.abs(iq - c1)

    fraction_closer_to_0 = np.mean(
        dist_to_0 < dist_to_1
    )

    # A noticeable number of |1> shots should
    # move toward |0> because of decay.
    assert fraction_closer_to_0 > 0.05


def test_trace_shape():
    generator = IQDriftGenerator()

    I, Q, states = generator.generate_traces(
        n_shots=100,
        t_hours=0
    )

    assert I.shape == (100, 500)
    assert Q.shape == (100, 500)
    assert states.shape == (100,)


def test_trace_values_are_finite():
    generator = IQDriftGenerator()

    I, Q, states = generator.generate_traces(
        n_shots=20,
        t_hours=0
    )

    assert np.all(np.isfinite(I))
    assert np.all(np.isfinite(Q))