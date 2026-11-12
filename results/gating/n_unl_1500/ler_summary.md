etas used (from adaptive_boundary_v5.csv): quiet 0.3, alarm 0.9; d=5, physical error 0.001

### quiet_q1
QUIET: controlled generator with no drift at all.

8 run(s); 43 windows per run, 1500 shots per window, d=5, physical error 0.001.

| arm | pooled LER [95% Wilson CI, counts shots only] | [95% CI resampling runs] | shots | mean accuracy | gap recovered, pooled [95% bootstrap CI over runs] | median per run [IQR] | runs >= 0.8 |
|---|---|---|---|---|---|---|---|
| frozen | 0.00274 [0.00260, 0.00289] | [0.00261, 0.00286] | 516000 | 98.19% | - | - | - |
| periodic_12h | 0.00270 [0.00256, 0.00285] | [0.00259, 0.00281] | 516000 | 98.18% | - | - | - |
| periodic_24h | 0.00272 [0.00258, 0.00287] | [0.00259, 0.00285] | 516000 | 98.18% | - | - | - |
| periodic_48h | 0.00273 [0.00259, 0.00287] | [0.00259, 0.00286] | 516000 | 98.18% | - | - | - |
| oracle | 0.00270 [0.00257, 0.00285] | [0.00259, 0.00282] | 516000 | 98.18% | - | - | - |
| moment_v1 | 0.03912 [0.03859, 0.03965] | [0.03816, 0.04012] | 516000 | 95.15% | - | - | - |
| em_pi | 0.00272 [0.00258, 0.00286] | [0.00259, 0.00285] | 516000 | 98.19% | - | - | - |
| em_pi_fast | 0.00272 [0.00258, 0.00286] | [0.00256, 0.00288] | 516000 | 98.18% | - | - | - |
| em_pi_fast_lag | 0.00271 [0.00257, 0.00285] | [0.00260, 0.00281] | 516000 | 98.18% | - | - | - |
| gated_v5 | 0.00272 [0.00258, 0.00286] | [0.00259, 0.00285] | 516000 | 98.19% | - | - | - |
| em_pi_lag | 0.00272 [0.00258, 0.00286] | [0.00259, 0.00284] | 516000 | 98.19% | - | - | - |
| gated_v5_lag | 0.00272 [0.00258, 0.00286] | [0.00259, 0.00284] | 516000 | 98.19% | - | - | - |

frozen-vs-oracle LER gap: 0.004 percentage points  (not distinguishable from zero, recovery fractions are not reported)

Paired LER differences (percentage points, 95% CI from the same resamples; negative = first arm better):
- em_pi_fast - frozen: -0.002 [-0.009, +0.005]
- em_pi_fast - oracle: +0.001 [-0.005, +0.009]
- gated_v5 - em_pi_fast: -0.000 [-0.006, +0.005]
- em_pi_fast_lag - em_pi_fast: -0.001 [-0.009, +0.006]
- periodic_24h - em_pi_fast: +0.000 [-0.006, +0.006]
- em_pi - em_pi_fast: -0.000 [-0.006, +0.005]
- gated_v5 - em_pi: +0.000 [+0.000, +0.000]
- gated_v5_lag - em_pi_fast_lag: +0.001 [-0.003, +0.005]
- gated_v5_lag - em_pi_lag: +0.000 [+0.000, +0.000]
- em_pi_lag - em_pi_fast_lag: +0.001 [-0.003, +0.005]

Labelled calibration cost per run (43 windows, 2000 labelled shots per recalibration; these are readout calibration shots, not QEC shots): periodic_12h 14.0 recalibration(s) = 28000 labelled shots (43.4% of the QEC shots); periodic_24h 7.0 recalibration(s) = 14000 labelled shots (21.7% of the QEC shots); periodic_48h 3.0 recalibration(s) = 6000 labelled shots (9.3% of the QEC shots); oracle 43.0 recalibration(s) = 86000 labelled shots (133.3% of the QEC shots). Downtime per recalibration is not modelled; oracle recalibrates every window and is an upper bound, not deployable. Label-free arms need none.
gated arm alarm fraction over all windows: 0.00

### step_q1
CONTROLLED: imposed common-mode displacement, no other readout drift (step: 1 sigma along the centroid axis, applied at one third of the run).

8 run(s); 43 windows per run, 1500 shots per window, d=5, physical error 0.001.

| arm | pooled LER [95% Wilson CI, counts shots only] | [95% CI resampling runs] | shots | mean accuracy | gap recovered, pooled [95% bootstrap CI over runs] | median per run [IQR] | runs >= 0.8 |
|---|---|---|---|---|---|---|---|
| frozen | 0.05068 [0.05009, 0.05128] | [0.04968, 0.05172] | 516000 | 95.15% | - | - | - |
| periodic_12h | 0.00431 [0.00414, 0.00450] | [0.00416, 0.00445] | 516000 | 98.08% | +0.97 [+0.96, +0.97] | +0.97 [+0.96, +0.97] | 1.00 (8) |
| periodic_24h | 0.00951 [0.00925, 0.00978] | [0.00914, 0.00986] | 516000 | 97.77% | +0.86 [+0.85, +0.87] | +0.85 [+0.85, +0.87] | 1.00 (8) |
| periodic_48h | 0.01907 [0.01870, 0.01945] | [0.01839, 0.01978] | 516000 | 97.13% | +0.66 [+0.64, +0.68] | +0.66 [+0.63, +0.68] | 0.00 (8) |
| oracle | 0.00270 [0.00257, 0.00285] | [0.00259, 0.00281] | 516000 | 98.18% | +1.00 [+1.00, +1.00] | +1.00 [+1.00, +1.00] | 1.00 (8) |
| moment_v1 | 0.05759 [0.05696, 0.05823] | [0.05605, 0.05925] | 516000 | 94.57% | -0.14 [-0.17, -0.11] | -0.14 [-0.18, -0.13] | 0.00 (8) |
| em_pi | 0.00414 [0.00397, 0.00432] | [0.00385, 0.00450] | 516000 | 98.02% | +0.97 [+0.96, +0.98] | +0.97 [+0.97, +0.98] | 1.00 (8) |
| em_pi_fast | 0.00285 [0.00271, 0.00300] | [0.00267, 0.00306] | 516000 | 98.16% | +1.00 [+0.99, +1.00] | +1.00 [+1.00, +1.00] | 1.00 (8) |
| em_pi_fast_lag | 0.00438 [0.00421, 0.00457] | [0.00416, 0.00459] | 516000 | 98.06% | +0.96 [+0.96, +0.97] | +0.96 [+0.96, +0.97] | 1.00 (8) |
| gated_v5 | 0.00282 [0.00268, 0.00297] | [0.00270, 0.00296] | 516000 | 98.16% | +1.00 [+1.00, +1.00] | +1.00 [+1.00, +1.00] | 1.00 (8) |
| em_pi_lag | 0.00575 [0.00555, 0.00596] | [0.00539, 0.00612] | 516000 | 97.91% | +0.94 [+0.93, +0.94] | +0.94 [+0.93, +0.94] | 1.00 (8) |
| gated_v5_lag | 0.00437 [0.00419, 0.00455] | [0.00414, 0.00459] | 516000 | 98.06% | +0.97 [+0.96, +0.97] | +0.97 [+0.96, +0.97] | 1.00 (8) |

frozen-vs-oracle LER gap: 4.798 percentage points

Paired LER differences (percentage points, 95% CI from the same resamples; negative = first arm better):
- em_pi_fast - frozen: -4.783 [-4.897, -4.670]
- em_pi_fast - oracle: +0.015 [+0.005, +0.027]
- gated_v5 - em_pi_fast: -0.003 [-0.012, +0.005]
- em_pi_fast_lag - em_pi_fast: +0.153 [+0.132, +0.177]
- periodic_24h - em_pi_fast: +0.666 [+0.630, +0.704]
- em_pi - em_pi_fast: +0.129 [+0.108, +0.151]
- gated_v5 - em_pi: -0.132 [-0.159, -0.109]
- gated_v5_lag - em_pi_fast_lag: -0.001 [-0.006, +0.003]
- gated_v5_lag - em_pi_lag: -0.138 [-0.155, -0.122]
- em_pi_lag - em_pi_fast_lag: +0.137 [+0.119, +0.156]

Labelled calibration cost per run (43 windows, 2000 labelled shots per recalibration; these are readout calibration shots, not QEC shots): periodic_12h 14.0 recalibration(s) = 28000 labelled shots (43.4% of the QEC shots); periodic_24h 7.0 recalibration(s) = 14000 labelled shots (21.7% of the QEC shots); periodic_48h 3.0 recalibration(s) = 6000 labelled shots (9.3% of the QEC shots); oracle 43.0 recalibration(s) = 86000 labelled shots (133.3% of the QEC shots). Downtime per recalibration is not modelled; oracle recalibrates every window and is an upper bound, not deployable. Label-free arms need none.
gated arm alarm fraction over all windows: 0.05

### mixshift_quiet_q1
QUIET: controlled generator with no drift at all; |1> share of the unlabelled stream changes 0.3 -> 0.1 -> 0.5 by thirds of the run, pi fixed at its first estimate.

8 run(s); 43 windows per run, 1500 shots per window, d=5, physical error 0.001.

| arm | pooled LER [95% Wilson CI, counts shots only] | [95% CI resampling runs] | shots | mean accuracy | gap recovered, pooled [95% bootstrap CI over runs] | median per run [IQR] | runs >= 0.8 |
|---|---|---|---|---|---|---|---|
| frozen | 0.00274 [0.00260, 0.00289] | [0.00262, 0.00286] | 516000 | 98.19% | - | - | - |
| periodic_12h | 0.00270 [0.00256, 0.00285] | [0.00259, 0.00281] | 516000 | 98.18% | - | - | - |
| periodic_24h | 0.00272 [0.00258, 0.00287] | [0.00259, 0.00285] | 516000 | 98.18% | - | - | - |
| periodic_48h | 0.00273 [0.00259, 0.00287] | [0.00259, 0.00286] | 516000 | 98.18% | - | - | - |
| oracle | 0.00270 [0.00257, 0.00285] | [0.00260, 0.00281] | 516000 | 98.18% | - | - | - |
| moment_v1 | 0.13046 [0.12955, 0.13138] | [0.12888, 0.13217] | 516000 | 92.96% | - | - | - |
| em_pi | 0.00278 [0.00264, 0.00292] | [0.00264, 0.00294] | 516000 | 98.16% | - | - | - |
| em_pi_fast | 0.00289 [0.00275, 0.00304] | [0.00273, 0.00306] | 516000 | 98.14% | - | - | - |
| em_pi_fast_lag | 0.00287 [0.00272, 0.00302] | [0.00271, 0.00302] | 516000 | 98.14% | - | - | - |
| gated_v5 | 0.00277 [0.00263, 0.00292] | [0.00263, 0.00293] | 516000 | 98.16% | - | - | - |
| em_pi_lag | 0.00279 [0.00265, 0.00294] | [0.00266, 0.00294] | 516000 | 98.16% | - | - | - |
| gated_v5_lag | 0.00278 [0.00264, 0.00293] | [0.00265, 0.00292] | 516000 | 98.16% | - | - | - |

frozen-vs-oracle LER gap: 0.004 percentage points  (not distinguishable from zero, recovery fractions are not reported)

Paired LER differences (percentage points, 95% CI from the same resamples; negative = first arm better):
- em_pi_fast - frozen: +0.015 [+0.010, +0.022]
- em_pi_fast - oracle: +0.019 [+0.013, +0.026]
- gated_v5 - em_pi_fast: -0.012 [-0.020, -0.005]
- em_pi_fast_lag - em_pi_fast: -0.003 [-0.007, +0.001]
- periodic_24h - em_pi_fast: -0.017 [-0.023, -0.013]
- em_pi - em_pi_fast: -0.012 [-0.019, -0.004]
- gated_v5 - em_pi: -0.000 [-0.001, +0.000]
- gated_v5_lag - em_pi_fast_lag: -0.008 [-0.014, -0.003]
- gated_v5_lag - em_pi_lag: -0.001 [-0.002, +0.000]
- em_pi_lag - em_pi_fast_lag: -0.008 [-0.014, -0.002]

Labelled calibration cost per run (43 windows, 2000 labelled shots per recalibration; these are readout calibration shots, not QEC shots): periodic_12h 14.0 recalibration(s) = 28000 labelled shots (43.4% of the QEC shots); periodic_24h 7.0 recalibration(s) = 14000 labelled shots (21.7% of the QEC shots); periodic_48h 3.0 recalibration(s) = 6000 labelled shots (9.3% of the QEC shots); oracle 43.0 recalibration(s) = 86000 labelled shots (133.3% of the QEC shots). Downtime per recalibration is not modelled; oracle recalibrates every window and is an upper bound, not deployable. Label-free arms need none.
gated arm alarm fraction over all windows: 0.01

### mixshift_step_q1
CONTROLLED: imposed common-mode displacement, no other readout drift (step: 1 sigma along the centroid axis, applied at one third of the run); |1> share of the unlabelled stream changes 0.3 -> 0.1 -> 0.5 by thirds of the run, pi fixed at its first estimate.

8 run(s); 43 windows per run, 1500 shots per window, d=5, physical error 0.001.

| arm | pooled LER [95% Wilson CI, counts shots only] | [95% CI resampling runs] | shots | mean accuracy | gap recovered, pooled [95% bootstrap CI over runs] | median per run [IQR] | runs >= 0.8 |
|---|---|---|---|---|---|---|---|
| frozen | 0.05068 [0.05009, 0.05128] | [0.04960, 0.05177] | 516000 | 95.15% | - | - | - |
| periodic_12h | 0.00431 [0.00414, 0.00450] | [0.00416, 0.00447] | 516000 | 98.08% | +0.97 [+0.96, +0.97] | +0.97 [+0.96, +0.97] | 1.00 (8) |
| periodic_24h | 0.00951 [0.00925, 0.00978] | [0.00913, 0.00986] | 516000 | 97.77% | +0.86 [+0.85, +0.87] | +0.85 [+0.85, +0.87] | 1.00 (8) |
| periodic_48h | 0.01907 [0.01870, 0.01945] | [0.01838, 0.01982] | 516000 | 97.13% | +0.66 [+0.64, +0.68] | +0.66 [+0.63, +0.68] | 0.00 (8) |
| oracle | 0.00270 [0.00257, 0.00285] | [0.00259, 0.00282] | 516000 | 98.18% | +1.00 [+1.00, +1.00] | +1.00 [+1.00, +1.00] | 1.00 (8) |
| moment_v1 | 0.15613 [0.15514, 0.15712] | [0.15445, 0.15798] | 516000 | 92.15% | -2.20 [-2.27, -2.12] | -2.24 [-2.28, -2.08] | 0.00 (8) |
| em_pi | 0.00576 [0.00556, 0.00597] | [0.00534, 0.00622] | 516000 | 97.79% | +0.94 [+0.93, +0.94] | +0.94 [+0.93, +0.95] | 1.00 (8) |
| em_pi_fast | 0.00316 [0.00302, 0.00332] | [0.00297, 0.00343] | 516000 | 98.10% | +0.99 [+0.99, +0.99] | +0.99 [+0.99, +0.99] | 1.00 (8) |
| em_pi_fast_lag | 0.00469 [0.00451, 0.00488] | [0.00443, 0.00497] | 516000 | 97.99% | +0.96 [+0.95, +0.96] | +0.96 [+0.95, +0.96] | 1.00 (8) |
| gated_v5 | 0.00315 [0.00300, 0.00331] | [0.00298, 0.00337] | 516000 | 98.10% | +0.99 [+0.99, +0.99] | +0.99 [+0.99, +0.99] | 1.00 (8) |
| em_pi_lag | 0.00735 [0.00712, 0.00759] | [0.00685, 0.00786] | 516000 | 97.69% | +0.90 [+0.89, +0.91] | +0.90 [+0.89, +0.92] | 1.00 (8) |
| gated_v5_lag | 0.00468 [0.00449, 0.00487] | [0.00440, 0.00496] | 516000 | 98.00% | +0.96 [+0.95, +0.96] | +0.96 [+0.95, +0.96] | 1.00 (8) |

frozen-vs-oracle LER gap: 4.798 percentage points

Paired LER differences (percentage points, 95% CI from the same resamples; negative = first arm better):
- em_pi_fast - frozen: -4.752 [-4.870, -4.632]
- em_pi_fast - oracle: +0.046 [+0.035, +0.063]
- gated_v5 - em_pi_fast: -0.001 [-0.008, +0.004]
- em_pi_fast_lag - em_pi_fast: +0.152 [+0.130, +0.176]
- periodic_24h - em_pi_fast: +0.634 [+0.594, +0.672]
- em_pi - em_pi_fast: +0.260 [+0.225, +0.291]
- gated_v5 - em_pi: -0.261 [-0.291, -0.228]
- gated_v5_lag - em_pi_fast_lag: -0.001 [-0.007, +0.003]
- gated_v5_lag - em_pi_lag: -0.268 [-0.295, -0.242]
- em_pi_lag - em_pi_fast_lag: +0.267 [+0.240, +0.296]

Labelled calibration cost per run (43 windows, 2000 labelled shots per recalibration; these are readout calibration shots, not QEC shots): periodic_12h 14.0 recalibration(s) = 28000 labelled shots (43.4% of the QEC shots); periodic_24h 7.0 recalibration(s) = 14000 labelled shots (21.7% of the QEC shots); periodic_48h 3.0 recalibration(s) = 6000 labelled shots (9.3% of the QEC shots); oracle 43.0 recalibration(s) = 86000 labelled shots (133.3% of the QEC shots). Downtime per recalibration is not modelled; oracle recalibrates every window and is an upper bound, not deployable. Label-free arms need none.
gated arm alarm fraction over all windows: 0.12

### physical_quiet_q1
PHYSICAL ONLY: controlled generator with no readout drift, physical error ramped x3.

8 run(s); 43 windows per run, 1500 shots per window, d=5, physical error 0.001.

| arm | pooled LER [95% Wilson CI, counts shots only] | [95% CI resampling runs] | shots | mean accuracy | gap recovered, pooled [95% bootstrap CI over runs] | median per run [IQR] | runs >= 0.8 |
|---|---|---|---|---|---|---|---|
| frozen | 0.00528 [0.00509, 0.00549] | [0.00508, 0.00549] | 516000 | 98.19% | - | - | - |
| periodic_12h | 0.00526 [0.00507, 0.00546] | [0.00510, 0.00542] | 516000 | 98.18% | - | - | - |
| periodic_24h | 0.00530 [0.00511, 0.00551] | [0.00509, 0.00552] | 516000 | 98.18% | - | - | - |
| periodic_48h | 0.00529 [0.00510, 0.00549] | [0.00509, 0.00550] | 516000 | 98.18% | - | - | - |
| oracle | 0.00527 [0.00507, 0.00547] | [0.00508, 0.00546] | 516000 | 98.18% | - | - | - |
| moment_v1 | 0.04657 [0.04600, 0.04715] | [0.04531, 0.04778] | 516000 | 95.15% | - | - | - |
| em_pi | 0.00525 [0.00506, 0.00545] | [0.00504, 0.00546] | 516000 | 98.19% | - | - | - |
| em_pi_fast | 0.00523 [0.00504, 0.00543] | [0.00501, 0.00546] | 516000 | 98.18% | - | - | - |
| em_pi_fast_lag | 0.00526 [0.00506, 0.00546] | [0.00505, 0.00547] | 516000 | 98.18% | - | - | - |
| gated_v5 | 0.00522 [0.00503, 0.00542] | [0.00500, 0.00543] | 516000 | 98.18% | - | - | - |
| em_pi_lag | 0.00527 [0.00507, 0.00547] | [0.00504, 0.00550] | 516000 | 98.19% | - | - | - |
| gated_v5_lag | 0.00527 [0.00507, 0.00547] | [0.00503, 0.00549] | 516000 | 98.18% | - | - | - |

frozen-vs-oracle LER gap: 0.002 percentage points  (not distinguishable from zero, recovery fractions are not reported)

Paired LER differences (percentage points, 95% CI from the same resamples; negative = first arm better):
- em_pi_fast - frozen: -0.005 [-0.010, -0.000]
- em_pi_fast - oracle: -0.003 [-0.010, +0.003]
- gated_v5 - em_pi_fast: -0.001 [-0.006, +0.003]
- em_pi_fast_lag - em_pi_fast: +0.002 [-0.003, +0.007]
- periodic_24h - em_pi_fast: +0.007 [+0.002, +0.012]
- em_pi - em_pi_fast: +0.002 [-0.004, +0.008]
- gated_v5 - em_pi: -0.003 [-0.006, -0.001]
- gated_v5_lag - em_pi_fast_lag: +0.001 [-0.003, +0.004]
- gated_v5_lag - em_pi_lag: -0.000 [-0.003, +0.002]
- em_pi_lag - em_pi_fast_lag: +0.001 [-0.002, +0.004]

Labelled calibration cost per run (43 windows, 2000 labelled shots per recalibration; these are readout calibration shots, not QEC shots): periodic_12h 14.0 recalibration(s) = 28000 labelled shots (43.4% of the QEC shots); periodic_24h 7.0 recalibration(s) = 14000 labelled shots (21.7% of the QEC shots); periodic_48h 3.0 recalibration(s) = 6000 labelled shots (9.3% of the QEC shots); oracle 43.0 recalibration(s) = 86000 labelled shots (133.3% of the QEC shots). Downtime per recalibration is not modelled; oracle recalibrates every window and is an upper bound, not deployable. Label-free arms need none.
gated arm alarm fraction over all windows: 0.29

