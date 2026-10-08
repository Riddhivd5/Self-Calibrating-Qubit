"""
drift_framework.py  --  one interface for healthy / readout-drift / physical-drift runs,
plus the three syndrome features (fire rate, round-to-round correlation, per-ancilla asymmetry).

Everything the detector uses is computed from integer counts of the detection-event array,
so it ports to RTL / a bit-exact NumPy emulator later.
"""
import numpy as np
import stim

# ---------------------------------------------------------------- circuit building
MEAS_GATES = {"M", "MR", "MX", "MRX", "MY", "MRY"}


def _add_readout_flips(circ, p, scale):
    """Insert X_ERROR(p * scale[q]) before every Z-basis measurement of qubit q."""
    out = stim.Circuit()
    for inst in circ:
        if isinstance(inst, stim.CircuitRepeatBlock):
            out.append(stim.CircuitRepeatBlock(
                inst.repeat_count, _add_readout_flips(inst.body_copy(), p, scale)))
            continue
        if inst.name in ("M", "MR") and p > 0:
            for t in inst.targets_copy():
                out.append("X_ERROR", [t.value], min(0.5, p * scale.get(t.value, 1.0)))
        out.append(inst)
    return out


def build_circuit(d, rounds=None, p_readout=0.0, p_phys=0.0, readout_scale=None, phys_mode="both"):
    """
    p_readout     : readout flip probability (before every measurement)
    p_phys        : physical error rate
    phys_mode     : "both" = data + gate noise, "data" = data-qubit noise only,
                    "gate" = gate noise only (hits the ancillas too, so it can mimic readout errors)
    readout_scale : optional {qubit_index: multiplier} so readout drift can hit some ancillas harder
    """
    rounds = rounds or d
    base = stim.Circuit.generated(
        "surface_code:rotated_memory_z", distance=d, rounds=rounds,
        before_round_data_depolarization=p_phys if phys_mode in ("both", "data") else 0.0,
        after_clifford_depolarization=p_phys if phys_mode in ("both", "gate") else 0.0)
    return _add_readout_flips(base, p_readout, readout_scale or {})


def sample_window(circ, shots, seed=None):
    s = circ.compile_detector_sampler(seed=seed)
    det, obs = s.sample(shots, separate_observables=True)
    return det, obs


# ---------------------------------------------------------------- features
class Layout:
    """Maps detector index -> (ancilla id, round) from Stim's detector coordinates."""

    def __init__(self, circ):
        coords = circ.get_detector_coordinates()
        xy = {}
        self.anc = np.zeros(circ.num_detectors, int)
        self.t = np.zeros(circ.num_detectors, int)
        for i in range(circ.num_detectors):
            x, y, t = coords[i][:3]
            self.anc[i] = xy.setdefault((x, y), len(xy))
            self.t[i] = int(t)
        self.n_anc = len(xy)
        # consecutive-round pairs on the same ancilla
        pairs = []
        for a in range(self.n_anc):
            idx = np.where(self.anc == a)[0]
            idx = idx[np.argsort(self.t[idx])]
            pairs += [(idx[k], idx[k + 1]) for k in range(len(idx) - 1)]
        self.pairs = np.array(pairs)


def features(det, lay, ref_rate=None):
    """
    det : (shots, n_det) bool detection events.
    Returns dict with
      fire_rate : mean detector firing probability
      tcorr     : excess same-ancilla co-firing in consecutive rounds, P(d_t & d_t+1) - P(d_t)P(d_t+1)
      asym      : std across ancillas of (per-ancilla rate / healthy per-ancilla rate)
    """
    det = det.astype(np.uint8)
    n = det.shape[0]
    rate_det = det.mean(0)
    fire = rate_det.mean()
    a, b = lay.pairs[:, 0], lay.pairs[:, 1]
    both = (det[:, a] & det[:, b]).mean(0)
    tcorr = float(np.mean(both - rate_det[a] * rate_det[b]))
    per_anc = np.array([rate_det[lay.anc == k].mean() for k in range(lay.n_anc)])
    asym = float(np.std(per_anc / ref_rate)) if ref_rate is not None else np.nan
    return dict(fire_rate=float(fire), tcorr=tcorr, asym=asym, per_anc=per_anc)


def logical_error_rate(circ, det, obs):
    import pymatching
    m = pymatching.Matching.from_detector_error_model(circ.detector_error_model(decompose_errors=True))
    pred = np.asarray(m.decode_batch(det)).reshape(-1)
    return float(np.mean(pred != np.asarray(obs).reshape(-1)))
