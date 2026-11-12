"""
iq_generator_controlled.py -- readout drift of a KNOWN size and shape, for controlled experiments.

The refit profiles (iq_generator_refit.py) describe what the real device did. This module instead imposes a common-mode
displacement of both clouds along the centroid axis (the direction that moves one cloud towards the decision boundary),
specified in units of the along-axis cloud standard deviation, so results can be stated as "a shift of 1 sigma does X":

    from iq_generator_controlled import make_controlled
    gen = make_controlled("q1", seed=3, kind="step", shift_sigma=1.0, t_on=56.0)             # 0 before t_on, 1 sigma after
    gen = make_controlled("q1", seed=3, kind="slow", shift_sigma=1.0, hours=168.0)           # linear ramp, 1 sigma at `hours`

The noise (sigma_i, sigma_q, correlation) and the decay tail are those of the refit profile of the chosen qubit. The profile's
stochastic jitter is switched off by default (background=0) so the imposed displacement is the only readout drift; background=1
adds the fitted jitter. Events are never included. iq_generator.py is not modified; with shift_sigma=0 the output is
bit-identical to the refit generator without events (tests/test_iq_generator_controlled.py).
"""
import numpy as np

import iq_generator as ig
from iq_generator_refit import PARAMS_PATH, register_profiles

KINDS = ("step", "slow")


class ControlledShiftGenerator(ig.IQDriftGenerator):
    def __init__(self, params, kind="step", shift_sigma=1.0, t_on=56.0, hours=168.0):
        if kind not in KINDS:
            raise ValueError(f"kind must be one of {KINDS}")
        super().__init__(params)
        self.kind, self.shift_sigma, self.t_on, self.hours = kind, float(shift_sigma), float(t_on), float(hours)
        self.sigma_axis = float(self._profile_value("sigma_i"))  # along-axis sigma, in units of the t=0 separation

    def shift_in_sigma(self, t_hours):
        if self.kind == "step":
            return self.shift_sigma if t_hours >= self.t_on else 0.0
        return self.shift_sigma * float(np.clip(t_hours / self.hours, 0.0, 1.0))

    def _drifted_geometry(self, t_hours):
        c0, c1, decay, rot = super()._drifted_geometry(t_hours)
        s = self.shift_in_sigma(t_hours)
        if s != 0.0:
            d = s * self.sigma_axis * (c1 - c0) / abs(c1 - c0)   # towards |1>: the |0> cloud moves towards the boundary
            c0, c1 = c0 + d, c1 + d
        return c0, c1, decay, rot


def make_controlled(qubit="q1", seed=0, kind="step", shift_sigma=1.0, t_on=56.0, hours=168.0, background=0.0, decay=True,
                    params_path=PARAMS_PATH):
    f = register_profiles(params_path)[qubit]
    prm = ig.DriftParams(drift_profile=f"{qubit}_149", rng_seed=seed, stochastic_correlation_time_hr=float(f["tau"]),
                         stochastic_drift_strength=float(background), decay_prob_base=float(f["decay_prob"]) if decay else 0.0)
    return ControlledShiftGenerator(prm, kind=kind, shift_sigma=shift_sigma, t_on=t_on, hours=hours)
