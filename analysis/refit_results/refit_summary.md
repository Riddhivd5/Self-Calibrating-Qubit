# Generator refit on 149 real snapshots (375.2 h, 15.6 days)

Moment matching of IQDriftGenerator v1.5 parameters. Intervals are a parametric bootstrap (200 resamples) for ONE trajectory of this length, valid only if the model were true; the prediction check shows where it is not. Generator seeds per grid point: 150. The correlation-time grid starts at 2 h, so a fitted value at 2 h means 'no longer than that'.

## q0

A step of the separation (jump 0.25 of the initial value) is detected at snapshot 3; the fit starts at the plateau after it, with the reference geometry taken there. The step itself is a real drift event the generator cannot produce.

| parameter | existing profile | refit | 95% bootstrap interval |
|---|---|---|---|
| rotation_rate_deg_per_hr | 0.0039 | 0.004145 | [-0.002385, 0.01196] |
| gain_drift_per_hr | -0.0021 | 5.151e-05 | [1.804e-05, 8.578e-05] |
| stochastic_gain_amplitude | 0.08 | 0.04529 | [0.03021, 0.06231] |
| stochastic_rotation_amplitude_deg | 1.0 | 10.65 | [7.247, 14.13] |
| stochastic_centroid_wander_amplitude | 0.125 | 0.03773 | [0.02892, 0.04599] |
| stochastic_correlation_time_hr | 18.0 | 3 | [2, 3] |
| sigma_i | 0.2341 | 0.232 | [0.2304, 0.2333] |
| sigma_q | 0.1965 | 0.1998 | [0.1991, 0.2008] |
| iq_correlation | 0.0211 | 0.01783 | [0.01399, 0.02286] |
| decay_prob_base (tail beyond Gaussian) | 0 (off) | 0.0260 | excess error state 1 +0.0130, state 0 -0.0047 |

Prediction check: fitted generator simulated at the real snapshot times (95% interval over generator seeds) vs the real value

| statistic | real | generator 2.5% | median | 97.5% | real inside interval |
|---|---|---|---|---|---|
| slope_gain | 5.151e-05 | 1.692e-05 | 4.859e-05 | 8.238e-05 | yes |
| slope_theta | 0.004145 | -0.002275 | 0.003616 | 0.01234 | yes |
| std_gain | 0.01535 | 0.007709 | 0.01139 | 0.01526 | **NO** |
| std_theta | 2.706 | 1.882 | 2.691 | 3.546 | yes |
| std_shift | 0.01089 | 0.007743 | 0.009564 | 0.012 | yes |
| r3 | 0.3086 | 0.1948 | 0.2928 | 0.4225 | yes |
| r24 | 0.05457 | -0.1678 | -0.02599 | 0.07958 | yes |
| gain_min | 0.9351 | 0.947 | 0.9674 | 0.9907 | **NO** |
| gain_max | 1.026 | 1.03 | 1.055 | 1.078 | **NO** |
| R_min | 9.734 | 16.15 | 16.86 | 17.74 | **NO** |
| R_median | 18.42 | 18.35 | 19.02 | 19.66 | yes |
| R_max | 21.73 | 20.37 | 21.43 | 22.41 | yes |
| frozen_err_mean | 0.02112 | 0.01987 | 0.02124 | 0.02265 | yes |
| frozen_err_max | 0.0505 | 0.02543 | 0.02825 | 0.03082 | **NO** |
| event_fraction | 0 | 0 | 0 | 0 | yes |

Statistics the fitted model does not reproduce: std_gain, gain_min, gain_max, R_min, frozen_err_max.

### Events found in the real data (error > 2x baseline 0.0200 and a robust geometry outlier)

1 event(s) in 367 h: rate 0.0027/h = 0.07/day, 95% Poisson interval [0.00, 0.36]/day.  **Library of one event: the size distribution is not estimable; treat as indicative only.**

| at (h) | duration (h) | peak error | relative separation change | rotation (deg) | midpoint shift | noise factor along / across axis |
|---|---|---|---|---|---|---|
| 44.0 | 8.0 | 0.051 | -0.05 | 1.1 | 0.006 | 1.31 / 1.01 |

Prediction check with the event component (iq_generator_events.py; events resampled from the table above, Poisson timing, random rotation sign and shift direction):

| statistic | real | generator 2.5% | median | 97.5% | real inside interval |
|---|---|---|---|---|---|
| slope_gain | 5.151e-05 | -8.08e-07 | 4.825e-05 | 8.993e-05 | yes |
| slope_theta | 0.004145 | -0.002147 | 0.003548 | 0.01234 | yes |
| std_gain | 0.01535 | 0.008298 | 0.01397 | 0.02041 | yes |
| std_theta | 2.706 | 1.857 | 2.698 | 3.552 | yes |
| std_shift | 0.01089 | 0.00776 | 0.009588 | 0.01214 | yes |
| r3 | 0.3086 | 0.2033 | 0.3238 | 0.4479 | yes |
| r24 | 0.05457 | -0.1972 | -0.03435 | 0.09233 | yes |
| gain_min | 0.9351 | 0.9057 | 0.9515 | 0.9885 | yes |
| gain_max | 1.026 | 1.03 | 1.055 | 1.078 | **NO** |
| R_min | 9.734 | 8.706 | 9.777 | 17.53 | yes |
| R_median | 18.42 | 18.27 | 18.96 | 19.6 | yes |
| R_max | 21.73 | 20.37 | 21.43 | 22.31 | yes |
| frozen_err_mean | 0.02112 | 0.02005 | 0.02209 | 0.02643 | yes |
| frozen_err_max | 0.0505 | 0.026 | 0.066 | 0.07771 | yes |
| event_fraction | 0 | 0 | 0.01481 | 0.1185 | yes |

Statistics still not reproduced with events: gain_max (before: std_gain, gain_min, gain_max, R_min, frozen_err_max).

## q1

No step detected in the first snapshots; reference = first 5 snapshots.

| parameter | existing profile | refit | 95% bootstrap interval |
|---|---|---|---|
| rotation_rate_deg_per_hr | 0.1895 | -0.006223 | [-0.02362, 0.01023] |
| gain_drift_per_hr | -0.00032 | 6.693e-05 | [-3.099e-05, 0.0001611] |
| stochastic_gain_amplitude | 0.03 | 0.1657 | [0.1152, 0.2196] |
| stochastic_rotation_amplitude_deg | 2.0 | 32.95 | [22.59, 44.66] |
| stochastic_centroid_wander_amplitude | 0.184 | 0.1093 | [0.08278, 0.1321] |
| stochastic_correlation_time_hr | 18.0 | 2 | [2, 3] |
| sigma_i | 0.2411 | 0.2307 | [0.2291, 0.233] |
| sigma_q | 0.2149 | 0.2067 | [0.2055, 0.2074] |
| iq_correlation | 0.0291 | 0.01703 | [0.01371, 0.02111] |
| decay_prob_base (tail beyond Gaussian) | 0 (off) | 0.0147 | excess error state 1 +0.0074, state 0 -0.0026 |

Prediction check: fitted generator simulated at the real snapshot times (95% interval over generator seeds) vs the real value

| statistic | real | generator 2.5% | median | 97.5% | real inside interval |
|---|---|---|---|---|---|
| slope_gain | 6.693e-05 | -2.857e-05 | 5.825e-05 | 0.0001675 | yes |
| slope_theta | -0.006223 | -0.0236 | -0.007436 | 0.01043 | yes |
| std_gain | 0.04002 | 0.02777 | 0.03904 | 0.0509 | yes |
| std_theta | 7.614 | 5.454 | 7.577 | 10.26 | yes |
| std_shift | 0.02663 | 0.02128 | 0.02575 | 0.032 | yes |
| r3 | 0.1461 | 0.09207 | 0.1928 | 0.3045 | yes |
| r24 | 0.0297 | -0.1164 | -0.01972 | 0.06419 | yes |
| gain_min | 0.7009 | 0.8432 | 0.8976 | 0.9882 | **NO** |
| gain_max | 1.048 | 1.036 | 1.135 | 1.18 | yes |
| R_min | 5.132 | 13.17 | 14.91 | 17.93 | **NO** |
| R_median | 18.95 | 16.99 | 19.3 | 21.74 | yes |
| R_max | 24.4 | 20.44 | 24.38 | 27 | yes |
| frozen_err_mean | 0.02238 | 0.01514 | 0.02031 | 0.02628 | yes |
| frozen_err_max | 0.1085 | 0.02393 | 0.03675 | 0.04775 | **NO** |
| event_fraction | 0.1232 | 0 | 0 | 0.009239 | **NO** |

Statistics the fitted model does not reproduce: gain_min, R_min, frozen_err_max, event_fraction.

### Events found in the real data (error > 2x baseline 0.0150 and a robust geometry outlier)

8 event(s) in 375 h: rate 0.0213/h = 0.51/day, 95% Poisson interval [0.22, 1.01]/day.

| at (h) | duration (h) | peak error | relative separation change | rotation (deg) | midpoint shift | noise factor along / across axis |
|---|---|---|---|---|---|---|
| 48.5 | 0.0 | 0.108 | -0.30 | 0.8 | 0.128 | 1.35 / 1.35 |
| 64.5 | 0.0 | 0.043 | -0.05 | 12.5 | 0.111 | 1.15 / 1.03 |
| 143.2 | 5.3 | 0.109 | -0.12 | 43.5 | 0.142 | 1.42 / 1.07 |
| 248.7 | 0.0 | 0.062 | -0.10 | 16.5 | 0.107 | 1.28 / 1.08 |
| 264.7 | 0.2 | 0.078 | -0.14 | 23.7 | 0.080 | 1.36 / 1.06 |
| 292.7 | 4.0 | 0.070 | -0.17 | 18.9 | 0.087 | 1.29 / 1.25 |
| 316.7 | 1.4 | 0.053 | -0.14 | 17.3 | 0.104 | 1.15 / 1.23 |
| 348.5 | 0.2 | 0.044 | -0.03 | 10.8 | 0.109 | 1.19 / 1.03 |

Prediction check with the event component (iq_generator_events.py; events resampled from the table above, Poisson timing, random rotation sign and shift direction):

| statistic | real | generator 2.5% | median | 97.5% | real inside interval |
|---|---|---|---|---|---|
| slope_gain | 6.693e-05 | -7.54e-05 | 5.596e-05 | 0.0001833 | yes |
| slope_theta | -0.006223 | -0.03014 | -0.008862 | 0.01663 | yes |
| std_gain | 0.04002 | 0.03543 | 0.05149 | 0.07201 | yes |
| std_theta | 7.614 | 6.349 | 10.05 | 14.3 | yes |
| std_shift | 0.02663 | 0.02521 | 0.03208 | 0.0405 | yes |
| r3 | 0.1461 | 0.06884 | 0.2035 | 0.3562 | yes |
| r24 | 0.0297 | -0.1095 | -0.0188 | 0.06551 | yes |
| gain_min | 0.7009 | 0.6509 | 0.7686 | 0.8939 | yes |
| gain_max | 1.048 | 1.032 | 1.135 | 1.18 | yes |
| R_min | 5.132 | 2.865 | 6.108 | 9.778 | yes |
| R_median | 18.95 | 16.92 | 19.2 | 21.51 | yes |
| R_max | 24.4 | 20.44 | 24.38 | 27 | yes |
| frozen_err_mean | 0.02238 | 0.01818 | 0.02591 | 0.03465 | yes |
| frozen_err_max | 0.1085 | 0.08834 | 0.1566 | 0.2936 | yes |
| event_fraction | 0.1232 | 0.01449 | 0.05797 | 0.1159 | **NO** |

Statistics still not reproduced with events: event_fraction (before: gain_min, R_min, frozen_err_max, event_fraction).

## q2

No step detected in the first snapshots; reference = first 5 snapshots.

| parameter | existing profile | refit | 95% bootstrap interval |
|---|---|---|---|
| rotation_rate_deg_per_hr | -0.0163 | 0.006277 | [0.0009216, 0.01131] |
| gain_drift_per_hr | -0.00013 | 4.367e-05 | [1.516e-06, 8.35e-05] |
| stochastic_gain_amplitude | 0.03 | 0.05225 | [0.0365, 0.06887] |
| stochastic_rotation_amplitude_deg | 0.75 | 8.756 | [6.058, 11.92] |
| stochastic_centroid_wander_amplitude | 0.048 | 0.05048 | [0.03817, 0.06073] |
| stochastic_correlation_time_hr | 18.0 | 3 | [2, 4] |
| sigma_i | 0.1641 | 0.1625 | [0.1616, 0.1635] |
| sigma_q | 0.1517 | 0.1515 | [0.1511, 0.1521] |
| iq_correlation | 0.0115 | 0.007184 | [0.001933, 0.01316] |
| decay_prob_base (tail beyond Gaussian) | 0 (off) | 0.0120 | excess error state 1 +0.0060, state 0 +0.0008 |

Prediction check: fitted generator simulated at the real snapshot times (95% interval over generator seeds) vs the real value

| statistic | real | generator 2.5% | median | 97.5% | real inside interval |
|---|---|---|---|---|---|
| slope_gain | 4.367e-05 | 7.431e-06 | 3.933e-05 | 7.923e-05 | yes |
| slope_theta | 0.006277 | 0.0006368 | 0.005834 | 0.01131 | yes |
| std_gain | 0.01453 | 0.008681 | 0.01278 | 0.01658 | yes |
| std_theta | 2.126 | 1.48 | 2.094 | 2.793 | yes |
| std_shift | 0.01304 | 0.01007 | 0.01231 | 0.01522 | yes |
| r3 | 0.3332 | 0.2313 | 0.3236 | 0.4356 | yes |
| r24 | 0.2132 | -0.1423 | -0.02714 | 0.06598 | **NO** |
| gain_min | 0.9365 | 0.9496 | 0.967 | 0.9946 | **NO** |
| gain_max | 1.042 | 1.024 | 1.054 | 1.071 | yes |
| R_min | 26.87 | 32.02 | 34.2 | 36.27 | **NO** |
| R_median | 37.49 | 37.03 | 38.59 | 39.98 | yes |
| R_max | 43.6 | 41.11 | 43.46 | 45.58 | yes |
| frozen_err_mean | 0.005034 | 0.003786 | 0.004003 | 0.004382 | **NO** |
| frozen_err_max | 0.016 | 0.00625 | 0.00675 | 0.00825 | **NO** |
| event_fraction | 0.03623 | 0 | 0 | 0 | **NO** |

Statistics the fitted model does not reproduce: r24, gain_min, R_min, frozen_err_mean, frozen_err_max, event_fraction.

### Events found in the real data (error > 2x baseline 0.0050 and a robust geometry outlier)

None. Flagged-by-error snapshots without a geometry outlier are consistent with shot noise and the tail (1000 shots per state per snapshot).

