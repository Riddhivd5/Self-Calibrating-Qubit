etas used (from adaptive_boundary_v5.csv): quiet 0.3, alarm 0.9; d=5, physical error 0.001

### refit_q1
FITTED: profile refit on the 149 real snapshots (q1, jitter x1, events on, 336 h at 2 h steps).

8 run(s); 169 windows per run, 1500 shots per window, d=5, physical error 0.001.

| arm | pooled LER [95% Wilson CI, counts shots only] | [95% CI resampling runs] | shots | mean accuracy | gap recovered, pooled [95% bootstrap CI over runs] | median per run [IQR] | runs >= 0.8 |
|---|---|---|---|---|---|---|---|
| frozen | 0.01764 [0.01746, 0.01782] | [0.01130, 0.02463] | 2028000 | 97.25% | - | - | - |
| periodic_12h | 0.01580 [0.01563, 0.01597] | [0.01003, 0.02192] | 2028000 | 97.36% | +0.24 [+0.05, +0.39] | +0.25 [+0.09, +0.34] | 0.00 (8) |
| periodic_24h | 0.01645 [0.01628, 0.01663] | [0.01055, 0.02275] | 2028000 | 97.30% | +0.16 [-0.01, +0.26] | +0.21 [-0.08, +0.24] | 0.00 (8) |
| periodic_48h | 0.01752 [0.01734, 0.01771] | [0.01113, 0.02457] | 2028000 | 97.21% | +0.02 [-0.10, +0.15] | -0.02 [-0.13, +0.13] | 0.00 (8) |
| oracle | 0.00995 [0.00982, 0.01009] | [0.00665, 0.01353] | 2028000 | 97.77% | +1.00 [+1.00, +1.00] | +1.00 [+1.00, +1.00] | 1.00 (8) |
| moment_v1 | 0.06694 [0.06660, 0.06729] | [0.05585, 0.07910] | 2028000 | 94.15% | -6.41 [-10.55, -4.75] | -6.62 [-14.22, -5.28] | 0.00 (8) |
| em_pi | 0.01243 [0.01228, 0.01259] | [0.00816, 0.01700] | 2028000 | 97.62% | +0.68 [+0.60, +0.73] | +0.67 [+0.64, +0.70] | 0.00 (8) |
| em_pi_fast | 0.01068 [0.01054, 0.01083] | [0.00701, 0.01468] | 2028000 | 97.74% | +0.91 [+0.88, +0.94] | +0.92 [+0.89, +0.99] | 1.00 (8) |
| em_pi_fast_lag | 0.01368 [0.01352, 0.01384] | [0.00891, 0.01882] | 2028000 | 97.50% | +0.52 [+0.42, +0.56] | +0.55 [+0.37, +0.57] | 0.00 (8) |
| gated_v5 | 0.01083 [0.01069, 0.01098] | [0.00716, 0.01481] | 2028000 | 97.69% | +0.89 [+0.86, +0.91] | +0.89 [+0.86, +0.93] | 0.88 (8) |
| em_pi_lag | 0.01402 [0.01386, 0.01418] | [0.00915, 0.01923] | 2028000 | 97.50% | +0.47 [+0.34, +0.55] | +0.48 [+0.38, +0.51] | 0.00 (8) |
| gated_v5_lag | 0.01361 [0.01345, 0.01377] | [0.00895, 0.01867] | 2028000 | 97.50% | +0.52 [+0.43, +0.58] | +0.54 [+0.44, +0.57] | 0.00 (8) |

frozen-vs-oracle LER gap: 0.769 percentage points

Paired LER differences (percentage points, 95% CI from the same resamples; negative = first arm better):
- em_pi_fast - frozen: -0.705 [-0.992, -0.424]
- em_pi_fast - oracle: +0.075 [+0.029, +0.118]
- gated_v5 - em_pi_fast: +0.015 [+0.009, +0.020]
- em_pi_fast_lag - em_pi_fast: +0.304 [+0.196, +0.416]
- periodic_24h - em_pi_fast: +0.584 [+0.360, +0.805]
- em_pi - em_pi_fast: +0.177 [+0.113, +0.238]
- gated_v5 - em_pi: -0.162 [-0.223, -0.098]
- gated_v5_lag - em_pi_fast_lag: -0.008 [-0.022, +0.007]
- gated_v5_lag - em_pi_lag: -0.042 [-0.070, -0.016]
- em_pi_lag - em_pi_fast_lag: +0.035 [+0.003, +0.063]

Labelled calibration cost per run (169 windows, 2000 labelled shots per recalibration; these are readout calibration shots, not QEC shots): periodic_12h 28.0 recalibration(s) = 56000 labelled shots (22.1% of the QEC shots); periodic_24h 14.0 recalibration(s) = 28000 labelled shots (11.0% of the QEC shots); periodic_48h 7.0 recalibration(s) = 14000 labelled shots (5.5% of the QEC shots); oracle 169.0 recalibration(s) = 338000 labelled shots (133.3% of the QEC shots). Downtime per recalibration is not modelled; oracle recalibrates every window and is an upper bound, not deployable. Label-free arms need none.
gated arm alarm fraction over all windows: 0.18

