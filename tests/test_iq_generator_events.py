"""Tests for the event component and the 149-snapshot refit profiles. Run from the repo root: python -m pytest tests -q"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import iq_generator as ig
import iq_generator_events as ige
from iq_generator_refit import make_generator

LIB = [dict(duration_hr=3.0, gain_delta=-0.2, theta_deg=10.0, shift=(0.05, 0.0), sigma_ax_factor=1.5, sigma_pp_factor=1.0)]


def test_events_off_is_bit_identical_to_v15():
    for prof in ("generic", "q0", "q1", "q2"):
        a = ig.IQDriftGenerator(ig.DriftParams(drift_profile=prof, rng_seed=7))
        b = ige.IQDriftGeneratorEvents(ig.DriftParams(drift_profile=prof, rng_seed=7))
        for t in (0.0, 5.5, 100.0, 375.0):
            assert all(np.array_equal(np.asarray(x), np.asarray(y)) for x, y in zip(a._drifted_geometry(t), b._drifted_geometry(t)))
        ia, sa = a.generate_shots(300, 12.0)
        ib, sb = b.generate_shots(300, 12.0)
        assert np.array_equal(ia, ib) and np.array_equal(sa, sb)


def test_event_changes_geometry_only_while_active():
    g = ige.IQDriftGeneratorEvents(ig.DriftParams(drift_profile="q1", rng_seed=3), events=LIB, event_rate_per_hr=0.02)
    base = ig.IQDriftGenerator(ig.DriftParams(drift_profile="q1", rng_seed=3))
    e = g._ev[0]
    t_in, t_out = 0.5 * (e["start"] + e["end"]), e["end"] + 0.01
    sep = lambda gen, t: abs(gen._drifted_geometry(t)[1] - gen._drifted_geometry(t)[0])
    assert abs(sep(g, t_in) / sep(base, t_in) - 0.8) < 1e-9          # gain_delta = -0.2
    ev_after = [x for x in g._ev if x["start"] <= t_out < x["end"]]
    if not ev_after:
        assert abs(sep(g, t_out) - sep(base, t_out)) < 1e-12
    ang = lambda gen, t: np.degrees(np.angle((gen._drifted_geometry(t)[1] - gen._drifted_geometry(t)[0])))
    d = (ang(g, t_in) - ang(base, t_in) + 180) % 360 - 180
    assert abs(abs(d) - 10.0) < 1e-6                                # rotation magnitude 10 degrees, sign randomised


def test_event_broadens_noise_along_the_axis():
    g = ige.IQDriftGeneratorEvents(ig.DriftParams(drift_profile="q1", rng_seed=3), events=LIB, event_rate_per_hr=0.02)
    t = g._ev[0]["start"] + 0.1
    z, _ = g.generate_shots(20000, t, p_state1=0.0)
    ref = ig.IQDriftGenerator(ig.DriftParams(drift_profile="q1", rng_seed=3))
    z0, _ = ref.generate_shots(20000, t, p_state1=0.0)
    assert 1.3 < np.std(z.real) / np.std(z0.real) < 1.7


def test_event_arrivals_are_poisson_with_the_requested_rate():
    rate = 0.02
    counts = [len(ige.IQDriftGeneratorEvents(ig.DriftParams(rng_seed=s), events=LIB, event_rate_per_hr=rate)._ev) for s in range(200)]
    assert abs(np.mean(counts) / (rate * 720.0) - 1) < 0.15


def test_refit_profiles_match_real_snr_at_t0():
    # Real median R = (separation / sigma)^2 over the 149 snapshots (analysis/refit_results, validate_lienhard.py): q0 18.4, q1 18.9, q2 37.5
    real = {"q0": 18.4, "q1": 18.9, "q2": 37.5}
    for q, r_real in real.items():
        iq, s = make_generator(q, seed=1).generate_shots(20000, 0.0)
        a, b = iq[s == 0], iq[s == 1]
        d = b.mean() - a.mean()
        u = d / abs(d)
        f = lambda z: ((z - z.mean()) * np.conj(u)).real
        R = (abs(d) / (0.5 * (f(a).std() + f(b).std()))) ** 2
        assert abs(R / r_real - 1) < 0.15, (q, R, r_real)


def test_refit_jitter_has_the_real_rotation_spread():
    # Detrended rotation std over 149 snapshots ~2.5 h apart: real q0 2.7 deg, q1 7.6 deg, q2 2.1 deg (refit_summary.md)
    t = np.arange(149) * 2.52
    real = {"q0": 2.7, "q1": 7.6, "q2": 2.1}
    for q, r_real in real.items():
        sds = []
        for seed in range(25):
            g = make_generator(q, seed=seed, events=False)
            th = np.array([np.degrees(np.angle(g._drifted_geometry(x)[1] - g._drifted_geometry(x)[0])) for x in t])
            co = np.polyfit(t, th, 1)
            sds.append(np.std(th - np.polyval(co, t)))
        assert 0.7 < np.median(sds) / r_real < 1.3, (q, np.median(sds), r_real)
