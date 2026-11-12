etas used (from adaptive_boundary_v5.csv): quiet 0.3, alarm 0.9; d=5, physical error 0.001

### refit_q0
FITTED: profile refit on the 149 real snapshots (q0, jitter x1, events on, 336 h at 2 h steps).

8 run(s); 169 windows per run, 1500 shots per window, d=5, physical error 0.001.

| arm | pooled LER [95% Wilson CI, counts shots only] | [95% CI resampling runs] | shots | mean accuracy | gap recovered, pooled [95% bootstrap CI over runs] | median per run [IQR] | runs >= 0.8 |
|---|---|---|---|---|---|---|---|
| frozen | 0.00613 [0.00602, 0.00623] | [0.00552, 0.00677] | 2028000 | 97.70% | - | - | - |
| periodic_12h | 0.00608 [0.00598, 0.00619] | [0.00543, 0.00675] | 2028000 | 97.71% | - | - | - |
| periodic_24h | 0.00612 [0.00601, 0.00623] | [0.00548, 0.00679] | 2028000 | 97.70% | - | - | - |
| periodic_48h | 0.00618 [0.00607, 0.00628] | [0.00553, 0.00685] | 2028000 | 97.70% | - | - | - |
| oracle | 0.00603 [0.00592, 0.00613] | [0.00538, 0.00671] | 2028000 | 97.72% | - | - | - |
| moment_v1 | 0.05302 [0.05271, 0.05333] | [0.05060, 0.05561] | 2028000 | 94.46% | - | - | - |
| em_pi | 0.00602 [0.00591, 0.00612] | [0.00537, 0.00670] | 2028000 | 97.72% | - | - | - |
| em_pi_fast | 0.00604 [0.00594, 0.00615] | [0.00540, 0.00671] | 2028000 | 97.72% | - | - | - |
| em_pi_fast_lag | 0.00611 [0.00600, 0.00621] | [0.00549, 0.00677] | 2028000 | 97.71% | - | - | - |
| gated_v5 | 0.00604 [0.00593, 0.00615] | [0.00539, 0.00671] | 2028000 | 97.72% | - | - | - |
| em_pi_lag | 0.00607 [0.00596, 0.00617] | [0.00542, 0.00676] | 2028000 | 97.71% | - | - | - |
| gated_v5_lag | 0.00609 [0.00599, 0.00620] | [0.00545, 0.00680] | 2028000 | 97.71% | - | - | - |

frozen-vs-oracle LER gap: 0.010 percentage points  (not distinguishable from zero, recovery fractions are not reported)

Paired LER differences (percentage points, 95% CI from the same resamples; negative = first arm better):
- em_pi_fast - frozen: -0.008 [-0.014, -0.004]
- em_pi_fast - oracle: +0.002 [-0.002, +0.006]
- gated_v5 - em_pi_fast: -0.000 [-0.002, +0.001]
- em_pi_fast_lag - em_pi_fast: +0.006 [-0.000, +0.012]
- periodic_24h - em_pi_fast: +0.008 [+0.002, +0.013]
- em_pi - em_pi_fast: -0.003 [-0.005, +0.000]
- gated_v5 - em_pi: +0.002 [-0.000, +0.005]
- gated_v5_lag - em_pi_fast_lag: -0.001 [-0.005, +0.003]
- gated_v5_lag - em_pi_lag: +0.003 [+0.000, +0.005]
- em_pi_lag - em_pi_fast_lag: -0.004 [-0.009, +0.001]

Labelled calibration cost per run (169 windows, 2000 labelled shots per recalibration; these are readout calibration shots, not QEC shots): periodic_12h 28.0 recalibration(s) = 56000 labelled shots (22.1% of the QEC shots); periodic_24h 14.0 recalibration(s) = 28000 labelled shots (11.0% of the QEC shots); periodic_48h 7.0 recalibration(s) = 14000 labelled shots (5.5% of the QEC shots); oracle 169.0 recalibration(s) = 338000 labelled shots (133.3% of the QEC shots). Downtime per recalibration is not modelled; oracle recalibrates every window and is an upper bound, not deployable. Label-free arms need none.
gated arm alarm fraction over all windows: 0.04

### refit_q1
FITTED: profile refit on the 149 real snapshots (q1, jitter x1, events on, 336 h at 2 h steps).

8 run(s); 169 windows per run, 1500 shots per window, d=5, physical error 0.001.

| arm | pooled LER [95% Wilson CI, counts shots only] | [95% CI resampling runs] | shots | mean accuracy | gap recovered, pooled [95% bootstrap CI over runs] | median per run [IQR] | runs >= 0.8 |
|---|---|---|---|---|---|---|---|
| frozen | 0.01764 [0.01746, 0.01782] | [0.01089, 0.02392] | 2028000 | 97.25% | - | - | - |
| periodic_12h | 0.01580 [0.01563, 0.01597] | [0.00982, 0.02145] | 2028000 | 97.36% | +0.24 [+0.04, +0.39] | +0.25 [+0.09, +0.34] | 0.00 (8) |
| periodic_24h | 0.01645 [0.01628, 0.01663] | [0.01027, 0.02212] | 2028000 | 97.30% | +0.16 [-0.00, +0.26] | +0.21 [-0.08, +0.24] | 0.00 (8) |
| periodic_48h | 0.01752 [0.01734, 0.01771] | [0.01080, 0.02383] | 2028000 | 97.21% | +0.02 [-0.11, +0.14] | -0.02 [-0.13, +0.13] | 0.00 (8) |
| oracle | 0.00995 [0.00982, 0.01009] | [0.00649, 0.01324] | 2028000 | 97.77% | +1.00 [+1.00, +1.00] | +1.00 [+1.00, +1.00] | 1.00 (8) |
| moment_v1 | 0.06694 [0.06660, 0.06729] | [0.05530, 0.07809] | 2028000 | 94.15% | -6.41 [-10.36, -4.62] | -6.62 [-14.22, -5.28] | 0.00 (8) |
| em_pi | 0.01243 [0.01228, 0.01259] | [0.00790, 0.01666] | 2028000 | 97.62% | +0.68 [+0.61, +0.73] | +0.67 [+0.64, +0.70] | 0.00 (8) |
| em_pi_fast | 0.01068 [0.01054, 0.01083] | [0.00674, 0.01436] | 2028000 | 97.74% | +0.91 [+0.88, +0.94] | +0.92 [+0.89, +0.99] | 1.00 (8) |
| em_pi_fast_lag | 0.01368 [0.01352, 0.01384] | [0.00868, 0.01845] | 2028000 | 97.50% | +0.52 [+0.42, +0.57] | +0.55 [+0.37, +0.57] | 0.00 (8) |
| gated_v5 | 0.01083 [0.01069, 0.01098] | [0.00691, 0.01449] | 2028000 | 97.69% | +0.89 [+0.86, +0.91] | +0.89 [+0.86, +0.93] | 0.88 (8) |
| em_pi_lag | 0.01402 [0.01386, 0.01418] | [0.00887, 0.01881] | 2028000 | 97.50% | +0.47 [+0.34, +0.55] | +0.48 [+0.38, +0.51] | 0.00 (8) |
| gated_v5_lag | 0.01361 [0.01345, 0.01377] | [0.00865, 0.01831] | 2028000 | 97.50% | +0.52 [+0.43, +0.58] | +0.54 [+0.44, +0.57] | 0.00 (8) |

frozen-vs-oracle LER gap: 0.769 percentage points

Paired LER differences (percentage points, 95% CI from the same resamples; negative = first arm better):
- em_pi_fast - frozen: -0.694 [-0.980, -0.407]
- em_pi_fast - oracle: +0.073 [+0.028, +0.115]
- gated_v5 - em_pi_fast: +0.015 [+0.009, +0.020]
- em_pi_fast_lag - em_pi_fast: +0.299 [+0.189, +0.407]
- periodic_24h - em_pi_fast: +0.575 [+0.351, +0.789]
- em_pi - em_pi_fast: +0.174 [+0.112, +0.234]
- gated_v5 - em_pi: -0.159 [-0.218, -0.096]
- gated_v5_lag - em_pi_fast_lag: -0.008 [-0.021, +0.007]
- gated_v5_lag - em_pi_lag: -0.041 [-0.070, -0.015]
- em_pi_lag - em_pi_fast_lag: +0.034 [+0.002, +0.063]

Labelled calibration cost per run (169 windows, 2000 labelled shots per recalibration; these are readout calibration shots, not QEC shots): periodic_12h 28.0 recalibration(s) = 56000 labelled shots (22.1% of the QEC shots); periodic_24h 14.0 recalibration(s) = 28000 labelled shots (11.0% of the QEC shots); periodic_48h 7.0 recalibration(s) = 14000 labelled shots (5.5% of the QEC shots); oracle 169.0 recalibration(s) = 338000 labelled shots (133.3% of the QEC shots). Downtime per recalibration is not modelled; oracle recalibrates every window and is an upper bound, not deployable. Label-free arms need none.
gated arm alarm fraction over all windows: 0.18

### refit_q2
FITTED: profile refit on the 149 real snapshots (q2, jitter x1, events on, 336 h at 2 h steps).

8 run(s); 169 windows per run, 1500 shots per window, d=5, physical error 0.001.

| arm | pooled LER [95% Wilson CI, counts shots only] | [95% CI resampling runs] | shots | mean accuracy | gap recovered, pooled [95% bootstrap CI over runs] | median per run [IQR] | runs >= 0.8 |
|---|---|---|---|---|---|---|---|
| frozen | 0.00020 [0.00018, 0.00022] | [0.00018, 0.00022] | 2028000 | 99.59% | - | - | - |
| periodic_12h | 0.00020 [0.00018, 0.00022] | [0.00018, 0.00021] | 2028000 | 99.59% | - | - | - |
| periodic_24h | 0.00020 [0.00018, 0.00022] | [0.00018, 0.00022] | 2028000 | 99.59% | - | - | - |
| periodic_48h | 0.00020 [0.00018, 0.00022] | [0.00018, 0.00022] | 2028000 | 99.59% | - | - | - |
| oracle | 0.00019 [0.00018, 0.00021] | [0.00018, 0.00021] | 2028000 | 99.60% | - | - | - |
| moment_v1 | 0.00401 [0.00392, 0.00410] | [0.00361, 0.00443] | 2028000 | 98.22% | - | - | - |
| em_pi | 0.00020 [0.00018, 0.00022] | [0.00018, 0.00022] | 2028000 | 99.60% | - | - | - |
| em_pi_fast | 0.00020 [0.00018, 0.00022] | [0.00018, 0.00022] | 2028000 | 99.60% | - | - | - |
| em_pi_fast_lag | 0.00020 [0.00018, 0.00022] | [0.00018, 0.00022] | 2028000 | 99.59% | - | - | - |
| gated_v5 | 0.00020 [0.00018, 0.00022] | [0.00018, 0.00022] | 2028000 | 99.60% | - | - | - |
| em_pi_lag | 0.00020 [0.00018, 0.00022] | [0.00018, 0.00022] | 2028000 | 99.59% | - | - | - |
| gated_v5_lag | 0.00020 [0.00018, 0.00022] | [0.00018, 0.00022] | 2028000 | 99.59% | - | - | - |

frozen-vs-oracle LER gap: 0.000 percentage points  (not distinguishable from zero, recovery fractions are not reported)

Paired LER differences (percentage points, 95% CI from the same resamples; negative = first arm better):
- em_pi_fast - frozen: -0.000 [-0.001, +0.001]
- em_pi_fast - oracle: +0.000 [+0.000, +0.001]
- gated_v5 - em_pi_fast: +0.000 [-0.000, +0.000]
- em_pi_fast_lag - em_pi_fast: +0.000 [-0.001, +0.001]
- periodic_24h - em_pi_fast: +0.000 [-0.000, +0.001]
- em_pi - em_pi_fast: +0.000 [-0.000, +0.000]
- gated_v5 - em_pi: +0.000 [+0.000, +0.000]
- gated_v5_lag - em_pi_fast_lag: +0.000 [-0.000, +0.000]
- gated_v5_lag - em_pi_lag: +0.000 [+0.000, +0.000]
- em_pi_lag - em_pi_fast_lag: +0.000 [-0.000, +0.000]

Labelled calibration cost per run (169 windows, 2000 labelled shots per recalibration; these are readout calibration shots, not QEC shots): periodic_12h 28.0 recalibration(s) = 56000 labelled shots (22.1% of the QEC shots); periodic_24h 14.0 recalibration(s) = 28000 labelled shots (11.0% of the QEC shots); periodic_48h 7.0 recalibration(s) = 14000 labelled shots (5.5% of the QEC shots); oracle 169.0 recalibration(s) = 338000 labelled shots (133.3% of the QEC shots). Downtime per recalibration is not modelled; oracle recalibrates every window and is an upper bound, not deployable. Label-free arms need none.
gated arm alarm fraction over all windows: 0.00

