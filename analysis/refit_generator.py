"""
refit_generator.py -- refit the drift parameters of IQDriftGenerator (v1.5) to the real IBM snapshots and check the result.

What it does, per qubit (q0, q1, q2), without changing iq_generator.py:
  1. Extract real trajectories from every snapshot (iq_*.npz + metadata_*.json): separation gain, rotation, midpoint shift
     (all relative to a reference state), noise ellipse along / across the centroid axis, and the tail beyond a Gaussian.
  2. Detect a step in the first snapshots (a persistent jump of the separation); if found, the fit starts at the plateau after it.
  3. Fit the generator's parameters by matching summary statistics: linear trend slopes (OLS), amplitudes of the three
     correlated wander processes (std of detrended residual, corrected for centroid-estimation noise from finite shots),
     one shared correlation time (grid search on residual autocorrelation at ~3 h and ~24 h), noise sigma_i / sigma_q /
     correlation, and a decay probability from the tail excess beyond a Gaussian.
     The generator divides every wander process by its own peak over a 720 h grid, so amplitudes are fitted by simulation
     (std per unit amplitude from many generator seeds), not by copying the standard deviation.
  4. Bootstrap covariance of the fitted parameters: parametric (simulate the fitted generator at the real snapshot times, add the
     finite-shot centroid noise, refit) for drift parameters; iid resampling of snapshots for the noise parameters. This is the
     estimator's spread for ONE trajectory of this length if the model were true; it does not cover steps or spikes.
  5. Prediction check: simulate many generator trajectories at the real snapshot times with the fitted parameters and report
     where real summary statistics fall inside the generator's 95% interval; statistics outside it are model failures.

Usage:  python analysis/refit_generator.py [data_dir] [--out refit_results]
"""
import argparse
import datetime as dt
import glob
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(__file__))

import numpy as np
from scipy.stats import chi2, norm

import iq_generator as ig
import iq_generator_events as ige

TAUS = [2, 3, 4, 6, 9, 12, 18, 24, 36, 48]  # correlation-time grid (hours)
N_SIM = 150  # generator seeds per grid point / prediction interval
N_BOOT = 200
BLOCK = 20  # snapshots per bootstrap block
SHOTS_NOTE = 1000  # shots per state per real snapshot


# ------------------------------------------------------------------ data
def load(data_dir):
    snaps = []
    for f in sorted(glob.glob(os.path.join(data_dir, "iq_*.npz"))):
        mf = os.path.join(data_dir, os.path.basename(f).replace("iq_", "metadata_").replace(".npz", ".json"))
        if not os.path.exists(mf):
            continue
        meta = json.load(open(mf))
        snaps.append((dt.datetime.fromisoformat(meta["timestamp_utc"].replace("Z", "+00:00")).timestamp(), np.load(f)))
    snaps.sort(key=lambda s: s[0])
    t = np.array([s[0] for s in snaps])
    return (t - t[0]) / 3600.0, [s[1] for s in snaps]


def find_step(gain_raw, max_i=25, thr=0.10):
    """Index where a persistent jump of the separation happens in the first snapshots (0 = none)."""
    best_i, best_j = 0, 0.0
    for i in range(2, max_i):
        j = abs(np.median(gain_raw[:i]) - np.median(gain_raw[i:i + 15]))
        if j > best_j:
            best_i, best_j = i, j
    return (best_i, best_j) if best_j > thr else (0, best_j)


def noise_axes(z0, z1, u):
    """Noise std along and across the centroid axis u (about each cloud's own mean) and their correlation."""
    ax, pp = [], []
    for z in (z0, z1):
        r = (z - z.mean()) * np.conj(u)
        ax.append(r.real)
        pp.append((r * np.conj(1j)).real)
    a, p = np.concatenate(ax), np.concatenate(pp)
    return 0.5 * (ax[0].std() + ax[1].std()), 0.5 * (pp[0].std() + pp[1].std()), float(np.corrcoef(a, p)[0, 1])


def extract(snaps, q, i0, nref=5):
    z0 = [s[f"q{q}_state0"] for s in snaps]
    z1 = [s[f"q{q}_state1"] for s in snaps]
    c0 = np.array([z.mean() for z in z0]); c1 = np.array([z.mean() for z in z1])
    d = c1 - c0
    dref = d[i0:i0 + nref].mean()
    mref = ((c0 + c1) / 2)[i0:i0 + nref].mean()
    sc = abs(dref)
    gain = np.abs(d) / sc
    theta = np.degrees(np.angle(d / dref))
    shift = ((c0 + c1) / 2 - mref) / sc
    n = len(snaps)
    s_ax = np.empty(n); s_pp = np.empty(n); rho = np.empty(n); e0 = np.empty(n); e1 = np.empty(n)
    for k in range(n):
        u = d[k] / abs(d[k])
        s_ax[k], s_pp[k], rho[k] = noise_axes(z0[k], z1[k], u)
        # per-state error of the nearest-centroid boundary at this snapshot (own centroids): tail beyond the Gaussian
        e0[k] = np.mean(np.abs(z0[k] - c0[k]) > np.abs(z0[k] - c1[k]))
        e1[k] = np.mean(np.abs(z1[k] - c1[k]) > np.abs(z1[k] - c0[k]))
    # frozen boundary (reference centroids) error, averaged over the two states, per snapshot
    r0, r1 = c0[i0:i0 + nref].mean(), c1[i0:i0 + nref].mean()
    pfro = np.array([0.5 * (np.mean(np.abs(a - r0) > np.abs(a - r1)) + np.mean(np.abs(b - r1) > np.abs(b - r0))) for a, b in zip(z0, z1)])
    return dict(gain=gain, theta=theta, shift=shift, s_ax=s_ax / sc, s_pp=s_pp / sc, rho=rho, e0=e0, e1=e1, pfro=pfro, sc=sc)


# ------------------------------------------------------------------ statistics shared by real data and simulation
def detrend(y, t):
    A = np.vstack([t, np.ones_like(t)]).T
    co = np.linalg.lstsq(A, y, rcond=None)[0]
    return co[0], y - A @ co


def pair_corr(res, t, lag, tol):
    D = t[None, :] - t[:, None]
    i, j = np.where((D > 0) & (np.abs(D - lag) < tol))
    if len(i) < 8:
        return np.nan
    xs = np.concatenate([r[i] / r.std() for r in res])
    ys = np.concatenate([r[j] / r.std() for r in res])
    return float(np.corrcoef(xs, ys)[0, 1])


def stats(gain, theta, shI, shQ, t):
    sg, rg = detrend(gain, t)
    sr, rr = detrend(theta, t)
    rI, rQ = shI - shI.mean(), shQ - shQ.mean()
    return dict(slope_gain=sg, slope_theta=sr, std_gain=rg.std(), std_theta=rr.std(), std_shift=np.sqrt(0.5 * (rI.std() ** 2 + rQ.std() ** 2)),
                r3=pair_corr([rg, rr, rI, rQ], t, 3.0, 1.5), r24=pair_corr([rg, rr, rI, rQ], t, 24.0, 3.0))


def noise_floor(sig_ax, sig_pp, n=SHOTS_NOTE):
    """Std of the centroid-estimation noise (finite shots) in units of the reference separation."""
    return dict(gain=sig_ax * np.sqrt(2.0 / n), theta=np.degrees(sig_pp * np.sqrt(2.0 / n)),
                shift=np.sqrt(0.5 * (sig_ax ** 2 + sig_pp ** 2) / (2.0 * n)))


# ------------------------------------------------------------------ generator side
def set_profile(rot=0.0, gain=0.0, ag=1.0, ar=1.0, ac=1.0, si=0.2, sq=0.2, rho=0.0):
    ig.DRIFT_PROFILES["fit"] = {"rotation_rate_deg_per_hr": rot, "gain_drift_per_hr": gain, "stochastic_gain_amplitude": ag,
                                "stochastic_rotation_amplitude_deg": ar, "stochastic_centroid_wander_amplitude": ac,
                                "sigma_i": si, "sigma_q": sq, "iq_correlation": rho}


def sim_geometry(tau, seed, t, decay=0.0, events=None, rate=0.0):
    prm = ig.DriftParams(drift_profile="fit", rng_seed=seed, stochastic_correlation_time_hr=float(tau), decay_prob_base=decay)
    g = ige.IQDriftGeneratorEvents(prm, events=events, event_rate_per_hr=rate) if events else ig.IQDriftGenerator(prm)
    c0, c1, rot = np.empty(len(t), complex), np.empty(len(t), complex), np.empty(len(t), complex)
    g._factor_series = []  # per-time noise factors (events broaden the noise); used by frozen_error_sim
    for k, tt in enumerate(t):
        c0[k], c1[k], _, rot[k] = g._drifted_geometry(float(tt))
        g._factor_series.append(getattr(g, "_noise_factors", (1.0, 1.0)))
    return g, c0, c1, rot


def sim_stats(tau, seed, t):
    _, c0, c1, _ = sim_geometry(tau, seed, t)
    d = c1 - c0
    m = (c0 + c1) / 2 - 0.5
    return stats(np.abs(d), np.degrees(np.angle(d)), m.real, m.imag, t)


def unit_table(t, seeds=N_SIM):
    """Per grid tau: mean std per unit amplitude (gain, theta, shift) and mean autocorrelations, from generator seeds."""
    set_profile()
    tab = {}
    for tau in TAUS:
        S = [sim_stats(tau, 5000 + s, t) for s in range(seeds)]
        tab[tau] = {k: float(np.nanmean([x[k] for x in S])) for k in S[0]}
    return tab


def fit_from_stats(obs, floor, tab):
    """Parameters from observed summary statistics: tau by autocorrelation, amplitudes by std per unit amplitude."""
    best = min(TAUS, key=lambda tau: np.nansum([(obs["r3"] - tab[tau]["r3"]) ** 2, (obs["r24"] - tab[tau]["r24"]) ** 2]))
    var = lambda s, f: np.sqrt(max(s ** 2 - f ** 2, 0.0))
    return dict(tau=best, rot=obs["slope_theta"], gain=obs["slope_gain"],
                ag=var(obs["std_gain"], floor["gain"]) / tab[best]["std_gain"],
                ar=var(obs["std_theta"], floor["theta"]) / tab[best]["std_theta"],
                ac=var(obs["std_shift"], floor["shift"]) / tab[best]["std_shift"])


def frozen_error_sim(g, c0, c1, rot, n=2000, decay=0.0):
    """Frozen-boundary (reference centroids 0 and 1) error per time point, Monte Carlo with the generator's own noise and,
    for state 1, its decay mechanism (with probability `decay` the mean lies at a uniform point between c1 and c0)."""
    p = np.empty(len(c0))
    for k in range(len(c0)):
        if hasattr(g, "_noise_factors"):
            g._noise_factors = g._factor_series[k]
        z0 = c0[k] + g._generate_noise(n) * rot[k]
        dec = g._rng.random(n) < decay
        m1 = np.where(dec, c1[k] + g._rng.random(n) * (c0[k] - c1[k]), c1[k])
        z1 = m1 + g._generate_noise(n) * rot[k]
        p[k] = 0.5 * (np.mean(np.abs(z0 - 0.0) > np.abs(z0 - 1.0)) + np.mean(np.abs(z1 - 1.0) > np.abs(z1 - 0.0)))
    return p


def event_fraction(p, base_slice=slice(1, 11), floor=0.005):
    base = max(float(np.median(p[base_slice])), floor)
    return float(np.mean(p[11:] > 2 * base)), base


def mad_sigma(x):
    return 1.4826 * np.median(np.abs(x - np.median(x)))


def extract_events(X, sl, t_abs):
    """Real events: snapshots where the frozen-boundary error exceeds twice its baseline AND a geometry channel (separation,
    rotation, midpoint shift) is a robust outlier (|z| > 4, MAD scale); consecutive flagged snapshots (gap <= 1 snapshot)
    form one event. Each event is described by the peak-error snapshot: relative separation change, rotation, midpoint shift,
    duration (first to last flagged snapshot). Returns (library, rate per hour, 95% Poisson interval, span in hours)."""
    g, th, sh, p, t = X["gain"][sl], X["theta"][sl], X["shift"][sl], X["pfro"][sl], t_abs
    zg, zt = (g - np.median(g)) / mad_sigma(g), (th - np.median(th)) / mad_sigma(th)
    zs = (np.abs(sh) - np.median(np.abs(sh))) / mad_sigma(np.abs(sh))
    base = max(float(np.median(p[1:11])), 0.005)
    flag_p = p > 2 * base
    flag_z = (np.abs(zg) > 4) | (np.abs(zt) > 4) | (zs > 4)
    sax_q = float(np.median(X["s_ax"][sl][~flag_p])); spp_q = float(np.median(X["s_pp"][sl][~flag_p]))  # quiet-snapshot noise
    clusters = []
    for i in np.where(flag_p)[0]:
        if clusters and i - clusters[-1][-1] <= 2:
            clusters[-1].append(i)
        else:
            clusters.append([i])
    lib = []
    for c in clusters:
        if not flag_z[c].any():
            continue  # error elevated but no geometry outlier: not counted (shot noise or tail)
        k = c[int(np.argmax(p[c]))]
        lib.append(dict(sigma_ax_factor=float(X["s_ax"][sl][k] / sax_q), sigma_pp_factor=float(X["s_pp"][sl][k] / spp_q), duration_hr=float(t[c[-1]] - t[c[0]]), gain_delta=float(g[k] - np.median(g)), theta_deg=float(abs(th[k] - np.median(th))),
                        shift=[float((sh[k] - np.median(sh)).real), float((sh[k] - np.median(sh)).imag)], peak_error=float(p[k]), at_hours=float(t[k])))
    span = float(t[-1] - t[0])
    n = len(lib)
    lo = chi2.ppf(0.025, 2 * n) / 2 / span if n else 0.0
    hi = chi2.ppf(0.975, 2 * n + 2) / 2 / span
    return lib, n / span, (float(lo), float(hi)), span, base


# ------------------------------------------------------------------ main per-qubit analysis
def analyse(q, t_all, snaps, rng, tab_cache):
    g_raw = None
    # step detection on the raw separation relative to the first three snapshots
    tmp = extract(snaps, q, 0, nref=3)
    i0, jump = find_step(tmp["gain"])
    X = extract(snaps, q, i0)
    sl = slice(i0, None)
    t = t_all[sl] - t_all[i0]
    gain, theta, shift = X["gain"][sl], X["theta"][sl], X["shift"][sl]
    shI, shQ = shift.real, shift.imag
    obs = stats(gain, theta, shI, shQ, t)
    sig_ax = float(np.median(X["s_ax"][sl])); sig_pp = float(np.median(X["s_pp"][sl])); rho = float(np.median(X["rho"][sl]))
    floor = noise_floor(sig_ax, sig_pp)
    key = (q, i0)
    if key not in tab_cache:
        tab_cache[key] = unit_table(t)
    tab = tab_cache[key]
    fit = fit_from_stats(obs, floor, tab)

    # tail beyond Gaussian: per-state error minus Gaussian expectation Phi(-sqrt(R)/2) with R from this snapshot
    R = (X["gain"][sl] / np.sqrt(X["s_ax"][sl] * X["s_ax"][sl])) ** 2
    gauss = norm.cdf(-np.sqrt(R) / 2)
    excess1 = np.median(X["e1"][sl] - gauss)
    excess0 = np.median(X["e0"][sl] - gauss)
    fit.update(sigma_i=sig_ax, sigma_q=sig_pp, iq_corr=rho, decay_prob=float(max(2 * excess1, 0.0)),
               excess_err_state1=float(excess1), excess_err_state0=float(excess0))

    # parametric bootstrap: simulate the fitted generator at the real snapshot times, add the finite-shot centroid noise, refit.
    # This gives the sampling spread of the estimator for ONE trajectory of this length IF the model were true; it does not
    # cover model failures (steps, spikes), which the prediction check reports separately.
    set_profile(rot=fit["rot"], gain=fit["gain"], ag=fit["ag"], ar=fit["ar"], ac=fit["ac"], si=sig_ax, sq=sig_pp, rho=rho)
    boots = []
    for b_i in range(N_BOOT):
        _, c0, c1, _ = sim_geometry(fit["tau"], 20000 + b_i, t)
        d = c1 - c0
        m = (c0 + c1) / 2 - 0.5
        nz = lambda sd: rng.normal(0, sd, len(t))
        b_obs = stats(np.abs(d) + nz(floor["gain"]), np.degrees(np.angle(d)) + nz(floor["theta"]), m.real + nz(floor["shift"]), m.imag + nz(floor["shift"]), t)
        b = fit_from_stats(b_obs, floor, tab)
        jj = rng.integers(0, len(t), len(t))
        b.update(sigma_i=float(np.median(X["s_ax"][sl][jj])), sigma_q=float(np.median(X["s_pp"][sl][jj])), iq_corr=float(np.median(X["rho"][sl][jj])))
        boots.append(b)
    lib, rate, rate_ci, span, base = extract_events(X, sl, t)
    return dict(i0=i0, step_jump=jump, t=t, X=X, sl=sl, obs=obs, fit=fit, boots=boots, floor=floor, tab=tab,
                events=lib, event_rate=rate, event_rate_ci=rate_ci, event_base=base)


def predict_check(q, A, t_all, snaps, events=None, rate=0.0):
    """Simulate the fitted generator at the real snapshot times; compare real summary statistics with its 95% interval."""
    f, X, sl, t = A["fit"], A["X"], A["sl"], A["t"]
    set_profile(rot=f["rot"], gain=f["gain"], ag=f["ag"], ar=f["ar"], ac=f["ac"], si=f["sigma_i"], sq=f["sigma_q"], rho=f["iq_corr"])
    rows = {k: [] for k in ["slope_gain", "slope_theta", "std_gain", "std_theta", "std_shift", "r3", "r24", "gain_min", "gain_max", "R_min", "R_median", "R_max",
                            "frozen_err_mean", "frozen_err_max", "event_fraction"]}
    for s in range(N_SIM):
        g, c0, c1, rot = sim_geometry(f["tau"], 9000 + s, t, decay=f["decay_prob"], events=events, rate=rate)
        d = c1 - c0
        m = (c0 + c1) / 2 - 0.5
        st = stats(np.abs(d), np.degrees(np.angle(d)), m.real, m.imag, t)
        for k in ("slope_gain", "slope_theta", "std_gain", "std_theta", "std_shift", "r3", "r24"):
            rows[k].append(st[k])
        gn = np.abs(d)
        # R as it would be MEASURED from 1000 shots per state: event noise broadening, finite-shot error on the separation and on sigma
        fi = np.array([x[0] for x in g._factor_series])
        rr = np.random.default_rng(31000 + s)
        gn_obs = gn + rr.normal(0, A["floor"]["gain"], len(gn))
        sig_obs = f["sigma_i"] * fi * (1 + rr.normal(0, 1.0 / np.sqrt(2 * 2 * SHOTS_NOTE), len(gn)))
        Rr = (gn_obs / sig_obs) ** 2
        rows["gain_min"].append(gn_obs.min()); rows["gain_max"].append(gn_obs.max())
        rows["R_min"].append(Rr.min()); rows["R_median"].append(np.median(Rr)); rows["R_max"].append(Rr.max())
        p = frozen_error_sim(g, c0, c1, rot, decay=f["decay_prob"])
        rows["frozen_err_mean"].append(p.mean()); rows["frozen_err_max"].append(p.max())
        rows["event_fraction"].append(event_fraction(p)[0])
    gain, theta = X["gain"][sl], X["theta"][sl]
    sh = X["shift"][sl]
    real = stats(gain, theta, sh.real, sh.imag, t)
    Rr = (gain / X["s_ax"][sl]) ** 2
    pr = X["pfro"][sl]
    real.update(gain_min=gain.min(), gain_max=gain.max(), R_min=Rr.min(), R_median=float(np.median(Rr)), R_max=Rr.max(),
                frozen_err_mean=pr.mean(), frozen_err_max=pr.max(), event_fraction=event_fraction(pr)[0])
    out = []
    for k in rows:
        lo, med, hi = np.nanpercentile(rows[k], [2.5, 50, 97.5])
        out.append((k, real[k], lo, med, hi, bool(lo <= real[k] <= hi)))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("data_dir", nargs="?", default=os.path.join(os.path.dirname(__file__), "..", "data"))
    ap.add_argument("--out", default="refit_results")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--allow-small", action="store_true", help="run even with fewer than 100 snapshots")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    outf = [os.path.join(a.out, f) for f in ("refit_summary.md", "refit_params.json")]
    if any(os.path.exists(f) for f in outf) and not a.force:
        sys.exit(f"refusing to overwrite results in {a.out}; use a new --out or --force")
    t_all, snaps = load(a.data_dir)
    print(f"loaded {len(snaps)} snapshots spanning {t_all[-1]:.1f} h from {os.path.abspath(a.data_dir)}", flush=True)
    if len(snaps) < 100 and not a.allow_small:
        sys.exit(f"only {len(snaps)} snapshots found in {a.data_dir}; the full set is 149 (the data/ folder on the iq-generator branch "
                 "holds only part of it). Pass the data folder from the main branch, or use --allow-small.")
    rng = np.random.default_rng(0)
    cache = {}
    md = [f"# Generator refit on {len(snaps)} real snapshots ({t_all[-1]:.1f} h, {t_all[-1] / 24:.1f} days)\n",
          "Moment matching of IQDriftGenerator v1.5 parameters. Intervals are a parametric bootstrap "
          f"({N_BOOT} resamples) for ONE trajectory of this length, valid only if the model were true; the prediction check shows where it is not. "
          f"Generator seeds per grid point: {N_SIM}. The correlation-time grid starts at {TAUS[0]} h, so a fitted value at {TAUS[0]} h means 'no longer than that'.\n"]
    params = {}
    for q in (0, 1, 2):
        A = analyse(q, t_all, snaps, rng, cache)
        f = A["fit"]
        ci = lambda k: np.percentile([b[k] for b in A["boots"]], [2.5, 97.5])
        params[f"q{q}"] = dict(start_snapshot=A["i0"], step_jump=A["step_jump"], **{k: (float(v) if not isinstance(v, (int, np.integer)) else int(v)) for k, v in f.items()},
                               ci95={k: [float(x) for x in ci(k)] for k in ("rot", "gain", "ag", "ar", "ac", "tau", "sigma_i", "sigma_q", "iq_corr")})
        names = dict(rot="rotation_rate_deg_per_hr", gain="gain_drift_per_hr", ag="stochastic_gain_amplitude", ar="stochastic_rotation_amplitude_deg",
                     ac="stochastic_centroid_wander_amplitude", tau="stochastic_correlation_time_hr", sigma_i="sigma_i", sigma_q="sigma_q", iq_corr="iq_correlation")
        old = ig.DRIFT_PROFILES[f"q{q}"]
        md += [f"## q{q}", ""]
        if A["i0"]:
            md.append(f"A step of the separation (jump {A['step_jump']:.2f} of the initial value) is detected at snapshot {A['i0']}; the fit starts at the "
                      f"plateau after it, with the reference geometry taken there. The step itself is a real drift event the generator cannot produce.\n")
        else:
            md.append("No step detected in the first snapshots; reference = first 5 snapshots.\n")
        md += ["| parameter | existing profile | refit | 95% bootstrap interval |", "|---|---|---|---|"]
        for k, nm in names.items():
            ov = old.get(nm, getattr(ig.DriftParams(), nm, None))
            lo, hi = ci(k)
            md.append(f"| {nm} | {ov} | {f[k]:.4g} | [{lo:.4g}, {hi:.4g}] |")
        md.append(f"| decay_prob_base (tail beyond Gaussian) | 0 (off) | {f['decay_prob']:.4f} | excess error state 1 {f['excess_err_state1']:+.4f}, state 0 {f['excess_err_state0']:+.4f} |")
        cov = np.cov(np.array([[b[k] for k in ("rot", "gain", "ag", "ar", "ac", "tau")] for b in A["boots"]]).T)
        params[f"q{q}"]["bootstrap_cov_rot_gain_ag_ar_ac_tau"] = cov.tolist()
        md += ["", "Prediction check: fitted generator simulated at the real snapshot times (95% interval over generator seeds) vs the real value", "",
               "| statistic | real | generator 2.5% | median | 97.5% | real inside interval |", "|---|---|---|---|---|---|"]
        chk = predict_check(q, A, t_all, snaps)
        for k, r, lo, med, hi, ok in chk:
            md.append(f"| {k} | {r:.4g} | {lo:.4g} | {med:.4g} | {hi:.4g} | {'yes' if ok else '**NO**'} |")
        bad = [k for k, *_, ok in chk if not ok]
        md += ["", f"Statistics the fitted model does not reproduce: {', '.join(bad) if bad else 'none'}.", ""]
        params[f"q{q}"]["not_reproduced"] = bad
        lib = A["events"]
        md += [f"### Events found in the real data (error > 2x baseline {A['event_base']:.4f} and a robust geometry outlier)", ""]
        if not lib:
            md += ["None. Flagged-by-error snapshots without a geometry outlier are consistent with shot noise and the tail (1000 shots per state per snapshot).", ""]
        else:
            lo, hi = A["event_rate_ci"]
            md += [f"{len(lib)} event(s) in {A['t'][-1]:.0f} h: rate {A['event_rate']:.4f}/h = {24 * A['event_rate']:.2f}/day, 95% Poisson interval "
                   f"[{24 * lo:.2f}, {24 * hi:.2f}]/day." + ("  **Library of one event: the size distribution is not estimable; treat as indicative only.**" if len(lib) == 1 else ""), "",
                   "| at (h) | duration (h) | peak error | relative separation change | rotation (deg) | midpoint shift | noise factor along / across axis |", "|---|---|---|---|---|---|---|"]
            for e in lib:
                md.append(f"| {e['at_hours']:.1f} | {e['duration_hr']:.1f} | {e['peak_error']:.3f} | {e['gain_delta']:+.2f} | {e['theta_deg']:.1f} | {abs(complex(*e['shift'])):.3f} | {e['sigma_ax_factor']:.2f} / {e['sigma_pp_factor']:.2f} |")
            md += ["", "Prediction check with the event component (iq_generator_events.py; events resampled from the table above, Poisson timing, "
                   "random rotation sign and shift direction):", "", "| statistic | real | generator 2.5% | median | 97.5% | real inside interval |", "|---|---|---|---|---|---|"]
            chk2 = predict_check(q, A, t_all, snaps, events=lib, rate=A["event_rate"])
            for k, r, lo2, med, hi2, ok in chk2:
                md.append(f"| {k} | {r:.4g} | {lo2:.4g} | {med:.4g} | {hi2:.4g} | {'yes' if ok else '**NO**'} |")
            bad2 = [k for k, *_, ok in chk2 if not ok]
            md += ["", f"Statistics still not reproduced with events: {', '.join(bad2) if bad2 else 'none'} (before: {', '.join(bad) if bad else 'none'}).", ""]
            params[f"q{q}"]["not_reproduced_with_events"] = bad2
        params[f"q{q}"]["event_library"] = lib
        params[f"q{q}"]["event_rate_per_hr"] = A["event_rate"]
        params[f"q{q}"]["event_rate_ci95_per_hr"] = list(A["event_rate_ci"])
        print(md[-1], flush=True)
    open(outf[0], "w").write("\n".join(md) + "\n")
    json.dump(params, open(outf[1], "w"), indent=1)
    print("\n".join(md))


if __name__ == "__main__":
    main()
