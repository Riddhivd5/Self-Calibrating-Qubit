"""
iq_generator_refit.py -- generators for q0/q1/q2 with drift parameters refit on the 149 real IBM snapshots
(analysis/refit_generator.py -> analysis/refit_results/refit_params.json), plus the measured event component.

    from iq_generator_refit import make_generator
    gen = make_generator("q1", seed=3)                       # fitted jitter + events + decay tail
    gen = make_generator("q1", seed=3, events=False)         # jitter only
    gen = make_generator("q1", seed=3, strength=2.0)         # stochastic jitter x2 (a stress test, not the fitted drift)

iq_generator.py is not modified; profiles "q0_149", "q1_149", "q2_149" are registered at import. Time t=0 is the reference state
used in the fit (for q0 the plateau after the early separation step, which the generator does not reproduce).
Known limits (see refit_summary.md): amplitudes are peak-over-720-h values of v1.5's normalised processes; q2 has no events
(its flagged snapshots are consistent with shot noise) and is not fully reproduced in the extremes; q0's event library has one entry.
"""
import json
import os

import iq_generator as ig
import iq_generator_events as ige

PARAMS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "analysis", "refit_results", "refit_params.json")


def _load(path=PARAMS_PATH):
    return json.load(open(path))


def register_profiles(path=PARAMS_PATH):
    P = _load(path)
    for q, f in P.items():
        ig.DRIFT_PROFILES[f"{q}_149"] = {
            "rotation_rate_deg_per_hr": f["rot"], "gain_drift_per_hr": f["gain"],
            "stochastic_gain_amplitude": f["ag"], "stochastic_rotation_amplitude_deg": f["ar"],
            "stochastic_centroid_wander_amplitude": f["ac"],
            "sigma_i": f["sigma_i"], "sigma_q": f["sigma_q"], "iq_correlation": f["iq_corr"]}
    return P


def make_generator(qubit, seed=0, events=True, decay=True, strength=1.0, params_path=PARAMS_PATH):
    P = register_profiles(params_path)
    f = P[qubit]
    prm = ig.DriftParams(drift_profile=f"{qubit}_149", rng_seed=seed, stochastic_correlation_time_hr=float(f["tau"]),
                         stochastic_drift_strength=float(strength), decay_prob_base=float(f["decay_prob"]) if decay else 0.0)
    lib = f.get("event_library") or []
    if events and lib and f.get("event_rate_per_hr", 0) > 0:
        return ige.IQDriftGeneratorEvents(prm, events=lib, event_rate_per_hr=f["event_rate_per_hr"])
    return ig.IQDriftGenerator(prm)


register_profiles()
