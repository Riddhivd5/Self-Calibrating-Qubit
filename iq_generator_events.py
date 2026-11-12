"""
iq_generator_events.py -- IQDriftGenerator v1.5 plus rare drift EVENTS (steps/spikes of separation, rotation and midpoint).

Why: real IBM readout drift on the 149 snapshots is mostly small fast jitter plus a few events that cause the large
frozen-boundary errors (q1: 8 events in 15.6 days, errors 4-11%). The smooth AR(1) wander of v1.5 does not produce them
(see analysis/refit_generator.py, prediction check).

This is a subclass; iq_generator.py is not modified. With event_rate_per_hr = 0 (default) or no event library the geometry is
bit-identical to v1.5 for the same seed (tests/test_iq_generator_events.py).

Events also broaden the noise (measured in the real events: along-axis sigma up to +40%, +15% median); each library entry carries
sigma_ax_factor and sigma_pp_factor (optional, default 1) applied to the along-axis (I) and across-axis (Q) noise while the event is active.

Model: events arrive as a Poisson process (rate per hour). Each event copies one entry of an event library measured from real
data: duration, relative separation change, rotation (degrees) and common-mode midpoint shift (in units of the separation). The
sign of the rotation and the direction of the shift are randomised; the separation change keeps its sign. The effect is applied
for the event's duration around the instantaneous midpoint, in the same way as v1.5's own gain / rotation / shift. The noise
ellipse rotates with the centroid axis, as in v1.5. Event randomness uses its own RNG (seed + 2002), so v1.5's streams are untouched.
"""
import numpy as np

import iq_generator as ig


class IQDriftGeneratorEvents(ig.IQDriftGenerator):
    def __init__(self, params=None, events=None, event_rate_per_hr=0.0, extra_duration_hr=2.6, event_seed_offset=2002):
        super().__init__(params)
        self.event_rate_per_hr = float(event_rate_per_hr)
        self.events = list(events or [])
        self._ev = []
        if self.event_rate_per_hr > 0 and self.events:
            rng = np.random.default_rng(self.p.rng_seed + event_seed_offset)
            horizon = self.p.stochastic_max_hours
            starts = np.sort(rng.uniform(0.0, horizon, rng.poisson(self.event_rate_per_hr * horizon)))
            for s in starts:
                e = self.events[rng.integers(len(self.events))]
                shift = complex(*e["shift"]) if not isinstance(e["shift"], complex) else e["shift"]
                shift *= np.exp(1j * rng.uniform(0, 2 * np.pi))
                self._ev.append(dict(start=float(s), end=float(s + e["duration_hr"] + rng.uniform(0, extra_duration_hr)),
                                     dgain=float(e["gain_delta"]), theta=float(e["theta_deg"]) * float(rng.choice([-1, 1])), shift=shift,
                                     fi=float(e.get("sigma_ax_factor", 1.0)), fq=float(e.get("sigma_pp_factor", 1.0))))

    def active_events(self, t_hours):
        return [e for e in self._ev if e["start"] <= t_hours < e["end"]]

    def _generate_noise(self, n_samples):
        z = super()._generate_noise(n_samples)
        fi, fq = getattr(self, "_noise_factors", (1.0, 1.0))
        return z if (fi == 1.0 and fq == 1.0) else z.real * fi + 1j * z.imag * fq

    def _drifted_geometry(self, t_hours):
        c0, c1, decay, rot = super()._drifted_geometry(t_hours)
        self._noise_factors = (1.0, 1.0)
        for e in self.active_events(t_hours):
            self._noise_factors = (self._noise_factors[0] * e["fi"], self._noise_factors[1] * e["fq"])
            m = (c0 + c1) / 2.0
            f = max(1.0 + e["dgain"], 0.1) * np.exp(1j * np.deg2rad(e["theta"]))
            c0 = m + (c0 - m) * f + e["shift"]
            c1 = m + (c1 - m) * f + e["shift"]
            rot = rot * np.exp(1j * np.deg2rad(e["theta"]))
        return c0, c1, decay, rot
