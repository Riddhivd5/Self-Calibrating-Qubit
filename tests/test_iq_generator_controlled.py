"""Tests for the controlled-shift generator. Run from the repo root: python -m pytest tests -q"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from iq_generator_controlled import make_controlled
from iq_generator_refit import make_generator


def centroids(gen, t, n=40000):
    iq, st = gen.generate_shots(n_shots=n, t_hours=t, p_state1=0.5)
    return iq[st == 0].mean(), iq[st == 1].mean(), iq, st


def test_zero_shift_is_bit_identical_to_refit_without_events():
    a = make_controlled("q1", seed=5, kind="step", shift_sigma=0.0, background=1.0)
    b = make_generator("q1", seed=5, events=False)
    for t in (0.0, 30.0, 100.0):
        ia, sa = a.generate_shots(500, t)
        ib, sb = b.generate_shots(500, t)
        assert np.array_equal(ia, ib) and np.array_equal(sa, sb)


def test_step_is_zero_before_onset_and_has_the_requested_size_after():
    g = make_controlled("q1", seed=1, kind="step", shift_sigma=1.0, t_on=56.0, decay=False)
    a0, a1, iq, st = centroids(g, 0.0)
    b0, b1, _, _ = centroids(g, 52.0)
    c0, c1, _, _ = centroids(g, 60.0)
    axis = (a1 - a0) / abs(a1 - a0)
    r = (iq[st == 0] - a0) * np.conj(axis)
    sigma_along = r.real.std()                       # measured along-axis sigma of the |0> cloud at t = 0
    assert abs(((b0 - a0) * np.conj(axis)).real) < 0.03 * sigma_along
    for before, after in ((a0, c0), (a1, c1)):
        shift = ((after - before) * np.conj(axis)).real / sigma_along
        assert abs(shift - 1.0) < 0.05, shift
    assert abs(abs(c1 - c0) / abs(a1 - a0) - 1.0) < 0.02   # separation unchanged: a pure displacement


def test_slow_ramp_is_linear_and_reaches_the_requested_size():
    g = make_controlled("q1", seed=2, kind="slow", shift_sigma=2.0, hours=100.0)
    assert g.shift_in_sigma(0.0) == 0.0
    assert abs(g.shift_in_sigma(25.0) - 0.5) < 1e-12
    assert abs(g.shift_in_sigma(100.0) - 2.0) < 1e-12
    assert g.shift_in_sigma(500.0) == 2.0


def test_background_zero_means_no_stochastic_drift():
    g = make_controlled("q1", seed=3, kind="step", shift_sigma=0.0, background=0.0)
    # only the profile's (tiny) linear trends remain: under 0.5% of the separation over 100 h
    c0a, c1a = g._drifted_geometry(0.0)[:2]
    c0b, c1b = g._drifted_geometry(100.0)[:2]
    assert max(abs(c0b - c0a), abs(c1b - c1a)) < 0.02 * abs(c1a - c0a)
