etas used (from adaptive_boundary_v5.csv): quiet 0.3, alarm 0.9; d=5, physical error 0.001

### quiet_q1
QUIET: controlled generator with no drift at all; 20 unlabelled IQ points per update.

8 run(s); 43 windows per run, 1500 shots per window, d=5, physical error 0.001.

| arm | pooled LER [95% Wilson CI, counts shots only] | [95% CI resampling runs] | shots | mean accuracy | gap recovered, pooled [95% bootstrap CI over runs] | median per run [IQR] | runs >= 0.8 |
|---|---|---|---|---|---|---|---|
| frozen | 0.00275 [0.00261, 0.00289] | [0.00262, 0.00286] | 516000 | 98.19% | - | - | - |
| periodic_12h | 0.00272 [0.00258, 0.00287] | [0.00259, 0.00285] | 516000 | 98.19% | - | - | - |
| periodic_24h | 0.00274 [0.00260, 0.00288] | [0.00262, 0.00285] | 516000 | 98.19% | - | - | - |
| periodic_48h | 0.00273 [0.00260, 0.00288] | [0.00262, 0.00285] | 516000 | 98.19% | - | - | - |
| oracle | 0.00273 [0.00260, 0.00288] | [0.00260, 0.00286] | 516000 | 98.18% | - | - | - |
| moment_v1 | 0.06203 [0.06137, 0.06269] | [0.04957, 0.07518] | 516000 | 94.43% | - | - | - |
| em_pi | 0.00273 [0.00259, 0.00287] | [0.00256, 0.00292] | 516000 | 98.17% | - | - | - |
| em_pi_fast | 0.00349 [0.00333, 0.00366] | [0.00280, 0.00462] | 516000 | 98.02% | - | - | - |
| em_pi_fast_lag | 0.00340 [0.00324, 0.00356] | [0.00280, 0.00441] | 516000 | 98.04% | - | - | - |
| gated_v5 | 0.00273 [0.00259, 0.00287] | [0.00256, 0.00292] | 516000 | 98.17% | - | - | - |
| em_pi_lag | 0.00273 [0.00259, 0.00288] | [0.00258, 0.00286] | 516000 | 98.17% | - | - | - |
| gated_v5_lag | 0.00273 [0.00259, 0.00288] | [0.00258, 0.00286] | 516000 | 98.17% | - | - | - |

frozen-vs-oracle LER gap: 0.001 percentage points  (not distinguishable from zero, recovery fractions are not reported)

Paired LER differences (percentage points, 95% CI from the same resamples; negative = first arm better):
- em_pi_fast - frozen: +0.075 [+0.017, +0.179]
- em_pi_fast - oracle: +0.077 [+0.018, +0.180]
- gated_v5 - em_pi_fast: -0.077 [-0.172, -0.023]
- em_pi_fast_lag - em_pi_fast: -0.010 [-0.026, +0.007]
- periodic_24h - em_pi_fast: -0.076 [-0.179, -0.016]
- em_pi - em_pi_fast: -0.077 [-0.172, -0.023]
- gated_v5 - em_pi: +0.000 [+0.000, +0.000]
- gated_v5_lag - em_pi_fast_lag: -0.067 [-0.160, -0.016]
- gated_v5_lag - em_pi_lag: +0.000 [+0.000, +0.000]
- em_pi_lag - em_pi_fast_lag: -0.067 [-0.160, -0.016]

Labelled calibration cost per run (43 windows, 2000 labelled shots per recalibration; these are readout calibration shots, not QEC shots): periodic_12h 14.0 recalibration(s) = 28000 labelled shots (43.4% of the QEC shots); periodic_24h 7.0 recalibration(s) = 14000 labelled shots (21.7% of the QEC shots); periodic_48h 3.0 recalibration(s) = 6000 labelled shots (9.3% of the QEC shots); oracle 43.0 recalibration(s) = 86000 labelled shots (133.3% of the QEC shots). Downtime per recalibration is not modelled; oracle recalibrates every window and is an upper bound, not deployable. Label-free arms need none.
gated arm alarm fraction over all windows: 0.00

### step_q1
CONTROLLED: imposed common-mode displacement, no other readout drift (step: 1 sigma along the centroid axis, applied at one third of the run); 20 unlabelled IQ points per update.

8 run(s); 43 windows per run, 1500 shots per window, d=5, physical error 0.001.

| arm | pooled LER [95% Wilson CI, counts shots only] | [95% CI resampling runs] | shots | mean accuracy | gap recovered, pooled [95% bootstrap CI over runs] | median per run [IQR] | runs >= 0.8 |
|---|---|---|---|---|---|---|---|
| frozen | 0.05005 [0.04946, 0.05065] | [0.04917, 0.05099] | 516000 | 95.15% | - | - | - |
| periodic_12h | 0.00446 [0.00428, 0.00465] | [0.00430, 0.00463] | 516000 | 98.08% | +0.96 [+0.96, +0.97] | +0.96 [+0.96, +0.97] | 1.00 (8) |
| periodic_24h | 0.01001 [0.00974, 0.01028] | [0.00975, 0.01033] | 516000 | 97.76% | +0.85 [+0.84, +0.85] | +0.85 [+0.84, +0.86] | 1.00 (8) |
| periodic_48h | 0.02047 [0.02009, 0.02086] | [0.02007, 0.02082] | 516000 | 97.11% | +0.63 [+0.62, +0.63] | +0.63 [+0.61, +0.63] | 0.00 (8) |
| oracle | 0.00273 [0.00260, 0.00288] | [0.00260, 0.00286] | 516000 | 98.18% | +1.00 [+1.00, +1.00] | +1.00 [+1.00, +1.00] | 1.00 (8) |
| moment_v1 | 0.08197 [0.08123, 0.08272] | [0.06743, 0.09625] | 516000 | 93.82% | -0.67 [-0.98, -0.36] | -0.61 [-1.01, -0.48] | 0.00 (8) |
| em_pi | 0.00924 [0.00898, 0.00950] | [0.00775, 0.01086] | 516000 | 97.36% | +0.86 [+0.83, +0.89] | +0.88 [+0.83, +0.90] | 0.75 (8) |
| em_pi_fast | 0.00720 [0.00697, 0.00743] | [0.00505, 0.00966] | 516000 | 97.59% | +0.91 [+0.85, +0.95] | +0.92 [+0.88, +0.97] | 0.88 (8) |
| em_pi_fast_lag | 0.00855 [0.00830, 0.00880] | [0.00622, 0.01135] | 516000 | 97.52% | +0.88 [+0.82, +0.93] | +0.89 [+0.84, +0.94] | 0.75 (8) |
| gated_v5 | 0.00729 [0.00706, 0.00753] | [0.00527, 0.00944] | 516000 | 97.59% | +0.90 [+0.86, +0.95] | +0.92 [+0.88, +0.94] | 0.88 (8) |
| em_pi_lag | 0.01068 [0.01040, 0.01096] | [0.00910, 0.01240] | 516000 | 97.28% | +0.83 [+0.80, +0.87] | +0.84 [+0.79, +0.87] | 0.75 (8) |
| gated_v5_lag | 0.00866 [0.00841, 0.00892] | [0.00673, 0.01087] | 516000 | 97.50% | +0.87 [+0.83, +0.92] | +0.89 [+0.85, +0.92] | 0.88 (8) |

frozen-vs-oracle LER gap: 4.732 percentage points

Paired LER differences (percentage points, 95% CI from the same resamples; negative = first arm better):
- em_pi_fast - frozen: -4.283 [-4.526, -3.991]
- em_pi_fast - oracle: +0.449 [+0.230, +0.697]
- gated_v5 - em_pi_fast: +0.009 [-0.035, +0.070]
- em_pi_fast_lag - em_pi_fast: +0.136 [+0.079, +0.186]
- periodic_24h - em_pi_fast: +0.279 [+0.042, +0.487]
- em_pi - em_pi_fast: +0.203 [+0.094, +0.302]
- gated_v5 - em_pi: -0.194 [-0.297, -0.097]
- gated_v5_lag - em_pi_fast_lag: +0.010 [-0.055, +0.088]
- gated_v5_lag - em_pi_lag: -0.202 [-0.304, -0.109]
- em_pi_lag - em_pi_fast_lag: +0.212 [+0.085, +0.319]

Labelled calibration cost per run (43 windows, 2000 labelled shots per recalibration; these are readout calibration shots, not QEC shots): periodic_12h 14.0 recalibration(s) = 28000 labelled shots (43.4% of the QEC shots); periodic_24h 7.0 recalibration(s) = 14000 labelled shots (21.7% of the QEC shots); periodic_48h 3.0 recalibration(s) = 6000 labelled shots (9.3% of the QEC shots); oracle 43.0 recalibration(s) = 86000 labelled shots (133.3% of the QEC shots). Downtime per recalibration is not modelled; oracle recalibrates every window and is an upper bound, not deployable. Label-free arms need none.
gated arm alarm fraction over all windows: 0.47

### mixshift_quiet_q1
QUIET: controlled generator with no drift at all; |1> share of the unlabelled stream changes 0.3 -> 0.1 -> 0.5 by thirds of the run, pi fixed at its first estimate; 20 unlabelled IQ points per update.

8 run(s); 43 windows per run, 1500 shots per window, d=5, physical error 0.001.

| arm | pooled LER [95% Wilson CI, counts shots only] | [95% CI resampling runs] | shots | mean accuracy | gap recovered, pooled [95% bootstrap CI over runs] | median per run [IQR] | runs >= 0.8 |
|---|---|---|---|---|---|---|---|
| frozen | 0.00275 [0.00261, 0.00289] | [0.00263, 0.00287] | 516000 | 98.19% | - | - | - |
| periodic_12h | 0.00272 [0.00258, 0.00287] | [0.00260, 0.00285] | 516000 | 98.19% | - | - | - |
| periodic_24h | 0.00274 [0.00260, 0.00288] | [0.00263, 0.00285] | 516000 | 98.19% | - | - | - |
| periodic_48h | 0.00273 [0.00260, 0.00288] | [0.00262, 0.00285] | 516000 | 98.19% | - | - | - |
| oracle | 0.00273 [0.00260, 0.00288] | [0.00261, 0.00286] | 516000 | 98.18% | - | - | - |
| moment_v1 | 0.13732 [0.13638, 0.13826] | [0.12776, 0.14890] | 516000 | 92.55% | - | - | - |
| em_pi | 0.00275 [0.00261, 0.00290] | [0.00263, 0.00288] | 516000 | 98.17% | - | - | - |
| em_pi_fast | 0.00334 [0.00319, 0.00351] | [0.00287, 0.00399] | 516000 | 98.04% | - | - | - |
| em_pi_fast_lag | 0.00338 [0.00323, 0.00354] | [0.00291, 0.00404] | 516000 | 98.05% | - | - | - |
| gated_v5 | 0.00275 [0.00261, 0.00290] | [0.00263, 0.00288] | 516000 | 98.17% | - | - | - |
| em_pi_lag | 0.00276 [0.00262, 0.00291] | [0.00263, 0.00290] | 516000 | 98.17% | - | - | - |
| gated_v5_lag | 0.00276 [0.00262, 0.00291] | [0.00263, 0.00290] | 516000 | 98.17% | - | - | - |

frozen-vs-oracle LER gap: 0.001 percentage points  (not distinguishable from zero, recovery fractions are not reported)

Paired LER differences (percentage points, 95% CI from the same resamples; negative = first arm better):
- em_pi_fast - frozen: +0.060 [+0.019, +0.118]
- em_pi_fast - oracle: +0.061 [+0.020, +0.119]
- gated_v5 - em_pi_fast: -0.060 [-0.113, -0.022]
- em_pi_fast_lag - em_pi_fast: +0.003 [-0.012, +0.017]
- periodic_24h - em_pi_fast: -0.061 [-0.118, -0.019]
- em_pi - em_pi_fast: -0.060 [-0.113, -0.022]
- gated_v5 - em_pi: +0.000 [+0.000, +0.000]
- gated_v5_lag - em_pi_fast_lag: -0.062 [-0.121, -0.021]
- gated_v5_lag - em_pi_lag: +0.000 [+0.000, +0.000]
- em_pi_lag - em_pi_fast_lag: -0.062 [-0.121, -0.021]

Labelled calibration cost per run (43 windows, 2000 labelled shots per recalibration; these are readout calibration shots, not QEC shots): periodic_12h 14.0 recalibration(s) = 28000 labelled shots (43.4% of the QEC shots); periodic_24h 7.0 recalibration(s) = 14000 labelled shots (21.7% of the QEC shots); periodic_48h 3.0 recalibration(s) = 6000 labelled shots (9.3% of the QEC shots); oracle 43.0 recalibration(s) = 86000 labelled shots (133.3% of the QEC shots). Downtime per recalibration is not modelled; oracle recalibrates every window and is an upper bound, not deployable. Label-free arms need none.
gated arm alarm fraction over all windows: 0.00

### mixshift_step_q1
CONTROLLED: imposed common-mode displacement, no other readout drift (step: 1 sigma along the centroid axis, applied at one third of the run); |1> share of the unlabelled stream changes 0.3 -> 0.1 -> 0.5 by thirds of the run, pi fixed at its first estimate; 20 unlabelled IQ points per update.

8 run(s); 43 windows per run, 1500 shots per window, d=5, physical error 0.001.

| arm | pooled LER [95% Wilson CI, counts shots only] | [95% CI resampling runs] | shots | mean accuracy | gap recovered, pooled [95% bootstrap CI over runs] | median per run [IQR] | runs >= 0.8 |
|---|---|---|---|---|---|---|---|
| frozen | 0.05005 [0.04946, 0.05065] | [0.04913, 0.05103] | 516000 | 95.15% | - | - | - |
| periodic_12h | 0.00446 [0.00428, 0.00465] | [0.00429, 0.00464] | 516000 | 98.08% | +0.96 [+0.96, +0.97] | +0.96 [+0.96, +0.97] | 1.00 (8) |
| periodic_24h | 0.01001 [0.00974, 0.01028] | [0.00975, 0.01034] | 516000 | 97.76% | +0.85 [+0.84, +0.85] | +0.85 [+0.84, +0.86] | 1.00 (8) |
| periodic_48h | 0.02047 [0.02009, 0.02086] | [0.02007, 0.02082] | 516000 | 97.11% | +0.63 [+0.62, +0.63] | +0.63 [+0.61, +0.63] | 0.00 (8) |
| oracle | 0.00273 [0.00260, 0.00288] | [0.00260, 0.00287] | 516000 | 98.18% | +1.00 [+1.00, +1.00] | +1.00 [+1.00, +1.00] | 1.00 (8) |
| moment_v1 | 0.16122 [0.16022, 0.16223] | [0.15101, 0.17170] | 516000 | 91.75% | -2.35 [-2.59, -2.13] | -2.32 [-2.49, -2.17] | 0.00 (8) |
| em_pi | 0.00790 [0.00766, 0.00814] | [0.00702, 0.00898] | 516000 | 97.57% | +0.89 [+0.87, +0.91] | +0.90 [+0.88, +0.92] | 1.00 (8) |
| em_pi_fast | 0.00670 [0.00648, 0.00692] | [0.00528, 0.00824] | 516000 | 97.65% | +0.92 [+0.89, +0.95] | +0.92 [+0.88, +0.96] | 1.00 (8) |
| em_pi_fast_lag | 0.00816 [0.00792, 0.00841] | [0.00632, 0.01011] | 516000 | 97.57% | +0.89 [+0.84, +0.93] | +0.90 [+0.83, +0.93] | 0.88 (8) |
| gated_v5 | 0.00619 [0.00598, 0.00641] | [0.00503, 0.00734] | 516000 | 97.74% | +0.93 [+0.90, +0.95] | +0.92 [+0.89, +0.95] | 1.00 (8) |
| em_pi_lag | 0.00949 [0.00923, 0.00976] | [0.00840, 0.01061] | 516000 | 97.48% | +0.86 [+0.83, +0.88] | +0.86 [+0.83, +0.89] | 0.88 (8) |
| gated_v5_lag | 0.00769 [0.00745, 0.00793] | [0.00635, 0.00903] | 516000 | 97.64% | +0.90 [+0.87, +0.92] | +0.90 [+0.85, +0.94] | 1.00 (8) |

frozen-vs-oracle LER gap: 4.732 percentage points

Paired LER differences (percentage points, 95% CI from the same resamples; negative = first arm better):
- em_pi_fast - frozen: -4.334 [-4.481, -4.179]
- em_pi_fast - oracle: +0.398 [+0.249, +0.557]
- gated_v5 - em_pi_fast: -0.050 [-0.116, +0.003]
- em_pi_fast_lag - em_pi_fast: +0.147 [+0.079, +0.206]
- periodic_24h - em_pi_fast: +0.329 [+0.202, +0.456]
- em_pi - em_pi_fast: +0.119 [+0.003, +0.217]
- gated_v5 - em_pi: -0.170 [-0.250, -0.097]
- gated_v5_lag - em_pi_fast_lag: -0.048 [-0.137, +0.031]
- gated_v5_lag - em_pi_lag: -0.180 [-0.262, -0.116]
- em_pi_lag - em_pi_fast_lag: +0.132 [+0.003, +0.235]

Labelled calibration cost per run (43 windows, 2000 labelled shots per recalibration; these are readout calibration shots, not QEC shots): periodic_12h 14.0 recalibration(s) = 28000 labelled shots (43.4% of the QEC shots); periodic_24h 7.0 recalibration(s) = 14000 labelled shots (21.7% of the QEC shots); periodic_48h 3.0 recalibration(s) = 6000 labelled shots (9.3% of the QEC shots); oracle 43.0 recalibration(s) = 86000 labelled shots (133.3% of the QEC shots). Downtime per recalibration is not modelled; oracle recalibrates every window and is an upper bound, not deployable. Label-free arms need none.
gated arm alarm fraction over all windows: 0.30

### physical_quiet_q1
PHYSICAL ONLY: controlled generator with no readout drift, physical error ramped x3; 20 unlabelled IQ points per update.

8 run(s); 43 windows per run, 1500 shots per window, d=5, physical error 0.001.

| arm | pooled LER [95% Wilson CI, counts shots only] | [95% CI resampling runs] | shots | mean accuracy | gap recovered, pooled [95% bootstrap CI over runs] | median per run [IQR] | runs >= 0.8 |
|---|---|---|---|---|---|---|---|
| frozen | 0.00530 [0.00511, 0.00550] | [0.00508, 0.00551] | 516000 | 98.19% | - | - | - |
| periodic_12h | 0.00528 [0.00509, 0.00548] | [0.00509, 0.00548] | 516000 | 98.19% | - | - | - |
| periodic_24h | 0.00530 [0.00511, 0.00551] | [0.00507, 0.00554] | 516000 | 98.19% | - | - | - |
| periodic_48h | 0.00531 [0.00512, 0.00551] | [0.00509, 0.00552] | 516000 | 98.19% | - | - | - |
| oracle | 0.00535 [0.00516, 0.00556] | [0.00510, 0.00560] | 516000 | 98.18% | - | - | - |
| moment_v1 | 0.07022 [0.06953, 0.07093] | [0.05693, 0.08274] | 516000 | 94.43% | - | - | - |
| em_pi | 0.00539 [0.00519, 0.00559] | [0.00510, 0.00568] | 516000 | 98.17% | - | - | - |
| em_pi_fast | 0.00629 [0.00608, 0.00651] | [0.00532, 0.00790] | 516000 | 98.02% | - | - | - |
| em_pi_fast_lag | 0.00627 [0.00606, 0.00649] | [0.00538, 0.00778] | 516000 | 98.04% | - | - | - |
| gated_v5 | 0.00545 [0.00525, 0.00565] | [0.00511, 0.00578] | 516000 | 98.15% | - | - | - |
| em_pi_lag | 0.00541 [0.00522, 0.00562] | [0.00513, 0.00569] | 516000 | 98.17% | - | - | - |
| gated_v5_lag | 0.00547 [0.00527, 0.00567] | [0.00517, 0.00576] | 516000 | 98.15% | - | - | - |

frozen-vs-oracle LER gap: -0.005 percentage points  (not distinguishable from zero, recovery fractions are not reported)

Paired LER differences (percentage points, 95% CI from the same resamples; negative = first arm better):
- em_pi_fast - frozen: +0.100 [+0.016, +0.249]
- em_pi_fast - oracle: +0.095 [+0.012, +0.239]
- gated_v5 - em_pi_fast: -0.085 [-0.218, -0.012]
- em_pi_fast_lag - em_pi_fast: -0.002 [-0.015, +0.012]
- periodic_24h - em_pi_fast: -0.100 [-0.247, -0.016]
- em_pi - em_pi_fast: -0.091 [-0.226, -0.016]
- gated_v5 - em_pi: +0.006 [-0.002, +0.013]
- gated_v5_lag - em_pi_fast_lag: -0.082 [-0.212, -0.011]
- gated_v5_lag - em_pi_lag: +0.005 [+0.001, +0.009]
- em_pi_lag - em_pi_fast_lag: -0.087 [-0.217, -0.017]

Labelled calibration cost per run (43 windows, 2000 labelled shots per recalibration; these are readout calibration shots, not QEC shots): periodic_12h 14.0 recalibration(s) = 28000 labelled shots (43.4% of the QEC shots); periodic_24h 7.0 recalibration(s) = 14000 labelled shots (21.7% of the QEC shots); periodic_48h 3.0 recalibration(s) = 6000 labelled shots (9.3% of the QEC shots); oracle 43.0 recalibration(s) = 86000 labelled shots (133.3% of the QEC shots). Downtime per recalibration is not modelled; oracle recalibrates every window and is an upper bound, not deployable. Label-free arms need none.
gated arm alarm fraction over all windows: 0.28

