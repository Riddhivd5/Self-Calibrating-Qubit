etas used (from adaptive_boundary_v5.csv): quiet 0.3, alarm 0.9; d=5, physical error 0.001

### quiet_q1
QUIET: controlled generator with no drift at all; 150 unlabelled IQ points per update.

8 run(s); 43 windows per run, 1500 shots per window, d=5, physical error 0.001.

| arm | pooled LER [95% Wilson CI, counts shots only] | [95% CI resampling runs] | shots | mean accuracy | gap recovered, pooled [95% bootstrap CI over runs] | median per run [IQR] | runs >= 0.8 |
|---|---|---|---|---|---|---|---|
| frozen | 0.00274 [0.00261, 0.00289] | [0.00262, 0.00286] | 516000 | 98.20% | - | - | - |
| periodic_12h | 0.00274 [0.00260, 0.00289] | [0.00261, 0.00287] | 516000 | 98.20% | - | - | - |
| periodic_24h | 0.00275 [0.00261, 0.00289] | [0.00261, 0.00289] | 516000 | 98.20% | - | - | - |
| periodic_48h | 0.00273 [0.00260, 0.00288] | [0.00261, 0.00286] | 516000 | 98.20% | - | - | - |
| oracle | 0.00273 [0.00259, 0.00288] | [0.00259, 0.00287] | 516000 | 98.19% | - | - | - |
| moment_v1 | 0.03927 [0.03874, 0.03980] | [0.03650, 0.04219] | 516000 | 95.24% | - | - | - |
| em_pi | 0.00274 [0.00260, 0.00288] | [0.00263, 0.00285] | 516000 | 98.19% | - | - | - |
| em_pi_fast | 0.00282 [0.00268, 0.00297] | [0.00272, 0.00295] | 516000 | 98.18% | - | - | - |
| em_pi_fast_lag | 0.00281 [0.00267, 0.00296] | [0.00272, 0.00289] | 516000 | 98.17% | - | - | - |
| gated_v5 | 0.00274 [0.00260, 0.00288] | [0.00263, 0.00285] | 516000 | 98.19% | - | - | - |
| em_pi_lag | 0.00273 [0.00259, 0.00288] | [0.00263, 0.00284] | 516000 | 98.19% | - | - | - |
| gated_v5_lag | 0.00273 [0.00259, 0.00288] | [0.00263, 0.00284] | 516000 | 98.19% | - | - | - |

frozen-vs-oracle LER gap: 0.001 percentage points  (not distinguishable from zero, recovery fractions are not reported)

Paired LER differences (percentage points, 95% CI from the same resamples; negative = first arm better):
- em_pi_fast - frozen: +0.008 [+0.000, +0.015]
- em_pi_fast - oracle: +0.009 [+0.000, +0.017]
- gated_v5 - em_pi_fast: -0.008 [-0.012, -0.004]
- em_pi_fast_lag - em_pi_fast: -0.001 [-0.009, +0.007]
- periodic_24h - em_pi_fast: -0.007 [-0.015, -0.000]
- em_pi - em_pi_fast: -0.008 [-0.012, -0.004]
- gated_v5 - em_pi: +0.000 [+0.000, +0.000]
- gated_v5_lag - em_pi_fast_lag: -0.008 [-0.015, -0.002]
- gated_v5_lag - em_pi_lag: +0.000 [+0.000, +0.000]
- em_pi_lag - em_pi_fast_lag: -0.008 [-0.015, -0.002]

Labelled calibration cost per run (43 windows, 2000 labelled shots per recalibration; these are readout calibration shots, not QEC shots): periodic_12h 14.0 recalibration(s) = 28000 labelled shots (43.4% of the QEC shots); periodic_24h 7.0 recalibration(s) = 14000 labelled shots (21.7% of the QEC shots); periodic_48h 3.0 recalibration(s) = 6000 labelled shots (9.3% of the QEC shots); oracle 43.0 recalibration(s) = 86000 labelled shots (133.3% of the QEC shots). Downtime per recalibration is not modelled; oracle recalibrates every window and is an upper bound, not deployable. Label-free arms need none.
gated arm alarm fraction over all windows: 0.00

### step_q1
CONTROLLED: imposed common-mode displacement, no other readout drift (step: 1 sigma along the centroid axis, applied at one third of the run); 150 unlabelled IQ points per update.

8 run(s); 43 windows per run, 1500 shots per window, d=5, physical error 0.001.

| arm | pooled LER [95% Wilson CI, counts shots only] | [95% CI resampling runs] | shots | mean accuracy | gap recovered, pooled [95% bootstrap CI over runs] | median per run [IQR] | runs >= 0.8 |
|---|---|---|---|---|---|---|---|
| frozen | 0.05046 [0.04986, 0.05106] | [0.04957, 0.05147] | 516000 | 95.20% | - | - | - |
| periodic_12h | 0.00445 [0.00427, 0.00464] | [0.00423, 0.00470] | 516000 | 98.09% | +0.96 [+0.96, +0.97] | +0.96 [+0.96, +0.97] | 1.00 (8) |
| periodic_24h | 0.00991 [0.00964, 0.01018] | [0.00940, 0.01051] | 516000 | 97.78% | +0.85 [+0.84, +0.86] | +0.86 [+0.84, +0.86] | 1.00 (8) |
| periodic_48h | 0.02017 [0.01979, 0.02055] | [0.01931, 0.02129] | 516000 | 97.15% | +0.63 [+0.61, +0.65] | +0.64 [+0.63, +0.65] | 0.00 (8) |
| oracle | 0.00273 [0.00259, 0.00288] | [0.00259, 0.00287] | 516000 | 98.19% | +1.00 [+1.00, +1.00] | +1.00 [+1.00, +1.00] | 1.00 (8) |
| moment_v1 | 0.05759 [0.05696, 0.05823] | [0.05369, 0.06160] | 516000 | 94.65% | -0.15 [-0.24, -0.07] | -0.16 [-0.21, -0.05] | 0.00 (8) |
| em_pi | 0.00409 [0.00391, 0.00426] | [0.00372, 0.00449] | 516000 | 98.04% | +0.97 [+0.96, +0.98] | +0.97 [+0.97, +0.98] | 1.00 (8) |
| em_pi_fast | 0.00295 [0.00281, 0.00311] | [0.00283, 0.00310] | 516000 | 98.16% | +1.00 [+0.99, +1.00] | +1.00 [+0.99, +1.00] | 1.00 (8) |
| em_pi_fast_lag | 0.00443 [0.00425, 0.00462] | [0.00400, 0.00481] | 516000 | 98.06% | +0.96 [+0.96, +0.97] | +0.96 [+0.95, +0.97] | 1.00 (8) |
| gated_v5 | 0.00287 [0.00273, 0.00302] | [0.00274, 0.00300] | 516000 | 98.17% | +1.00 [+1.00, +1.00] | +1.00 [+1.00, +1.00] | 1.00 (8) |
| em_pi_lag | 0.00566 [0.00546, 0.00587] | [0.00512, 0.00622] | 516000 | 97.94% | +0.94 [+0.93, +0.95] | +0.94 [+0.93, +0.95] | 1.00 (8) |
| gated_v5_lag | 0.00435 [0.00418, 0.00454] | [0.00405, 0.00465] | 516000 | 98.07% | +0.97 [+0.96, +0.97] | +0.97 [+0.96, +0.97] | 1.00 (8) |

frozen-vs-oracle LER gap: 4.773 percentage points

Paired LER differences (percentage points, 95% CI from the same resamples; negative = first arm better):
- em_pi_fast - frozen: -4.750 [-4.857, -4.656]
- em_pi_fast - oracle: +0.022 [+0.014, +0.031]
- gated_v5 - em_pi_fast: -0.009 [-0.014, -0.004]
- em_pi_fast_lag - em_pi_fast: +0.147 [+0.107, +0.183]
- periodic_24h - em_pi_fast: +0.695 [+0.651, +0.745]
- em_pi - em_pi_fast: +0.113 [+0.085, +0.144]
- gated_v5 - em_pi: -0.122 [-0.151, -0.094]
- gated_v5_lag - em_pi_fast_lag: -0.008 [-0.025, +0.010]
- gated_v5_lag - em_pi_lag: -0.131 [-0.158, -0.105]
- em_pi_lag - em_pi_fast_lag: +0.123 [+0.097, +0.152]

Labelled calibration cost per run (43 windows, 2000 labelled shots per recalibration; these are readout calibration shots, not QEC shots): periodic_12h 14.0 recalibration(s) = 28000 labelled shots (43.4% of the QEC shots); periodic_24h 7.0 recalibration(s) = 14000 labelled shots (21.7% of the QEC shots); periodic_48h 3.0 recalibration(s) = 6000 labelled shots (9.3% of the QEC shots); oracle 43.0 recalibration(s) = 86000 labelled shots (133.3% of the QEC shots). Downtime per recalibration is not modelled; oracle recalibrates every window and is an upper bound, not deployable. Label-free arms need none.
gated arm alarm fraction over all windows: 0.05

### mixshift_quiet_q1
QUIET: controlled generator with no drift at all; |1> share of the unlabelled stream changes 0.3 -> 0.1 -> 0.5 by thirds of the run, pi fixed at its first estimate; 150 unlabelled IQ points per update.

8 run(s); 43 windows per run, 1500 shots per window, d=5, physical error 0.001.

| arm | pooled LER [95% Wilson CI, counts shots only] | [95% CI resampling runs] | shots | mean accuracy | gap recovered, pooled [95% bootstrap CI over runs] | median per run [IQR] | runs >= 0.8 |
|---|---|---|---|---|---|---|---|
| frozen | 0.00274 [0.00261, 0.00289] | [0.00262, 0.00286] | 516000 | 98.20% | - | - | - |
| periodic_12h | 0.00274 [0.00260, 0.00289] | [0.00261, 0.00287] | 516000 | 98.20% | - | - | - |
| periodic_24h | 0.00275 [0.00261, 0.00289] | [0.00261, 0.00289] | 516000 | 98.20% | - | - | - |
| periodic_48h | 0.00273 [0.00260, 0.00288] | [0.00262, 0.00286] | 516000 | 98.20% | - | - | - |
| oracle | 0.00273 [0.00259, 0.00288] | [0.00260, 0.00287] | 516000 | 98.19% | - | - | - |
| moment_v1 | 0.12792 [0.12701, 0.12883] | [0.12339, 0.13238] | 516000 | 93.05% | - | - | - |
| em_pi | 0.00291 [0.00277, 0.00306] | [0.00280, 0.00303] | 516000 | 98.16% | - | - | - |
| em_pi_fast | 0.00318 [0.00303, 0.00334] | [0.00299, 0.00341] | 516000 | 98.09% | - | - | - |
| em_pi_fast_lag | 0.00319 [0.00304, 0.00335] | [0.00307, 0.00333] | 516000 | 98.10% | - | - | - |
| gated_v5 | 0.00291 [0.00277, 0.00306] | [0.00281, 0.00302] | 516000 | 98.15% | - | - | - |
| em_pi_lag | 0.00287 [0.00272, 0.00302] | [0.00275, 0.00298] | 516000 | 98.16% | - | - | - |
| gated_v5_lag | 0.00288 [0.00274, 0.00303] | [0.00275, 0.00302] | 516000 | 98.16% | - | - | - |

frozen-vs-oracle LER gap: 0.001 percentage points  (not distinguishable from zero, recovery fractions are not reported)

Paired LER differences (percentage points, 95% CI from the same resamples; negative = first arm better):
- em_pi_fast - frozen: +0.044 [+0.028, +0.062]
- em_pi_fast - oracle: +0.045 [+0.031, +0.063]
- gated_v5 - em_pi_fast: -0.027 [-0.044, -0.015]
- em_pi_fast_lag - em_pi_fast: +0.001 [-0.010, +0.010]
- periodic_24h - em_pi_fast: -0.043 [-0.062, -0.028]
- em_pi - em_pi_fast: -0.027 [-0.039, -0.016]
- gated_v5 - em_pi: +0.000 [-0.007, +0.006]
- gated_v5_lag - em_pi_fast_lag: -0.031 [-0.041, -0.022]
- gated_v5_lag - em_pi_lag: +0.001 [-0.001, +0.004]
- em_pi_lag - em_pi_fast_lag: -0.033 [-0.040, -0.026]

Labelled calibration cost per run (43 windows, 2000 labelled shots per recalibration; these are readout calibration shots, not QEC shots): periodic_12h 14.0 recalibration(s) = 28000 labelled shots (43.4% of the QEC shots); periodic_24h 7.0 recalibration(s) = 14000 labelled shots (21.7% of the QEC shots); periodic_48h 3.0 recalibration(s) = 6000 labelled shots (9.3% of the QEC shots); oracle 43.0 recalibration(s) = 86000 labelled shots (133.3% of the QEC shots). Downtime per recalibration is not modelled; oracle recalibrates every window and is an upper bound, not deployable. Label-free arms need none.
gated arm alarm fraction over all windows: 0.03

### mixshift_step_q1
CONTROLLED: imposed common-mode displacement, no other readout drift (step: 1 sigma along the centroid axis, applied at one third of the run); |1> share of the unlabelled stream changes 0.3 -> 0.1 -> 0.5 by thirds of the run, pi fixed at its first estimate; 150 unlabelled IQ points per update.

8 run(s); 43 windows per run, 1500 shots per window, d=5, physical error 0.001.

| arm | pooled LER [95% Wilson CI, counts shots only] | [95% CI resampling runs] | shots | mean accuracy | gap recovered, pooled [95% bootstrap CI over runs] | median per run [IQR] | runs >= 0.8 |
|---|---|---|---|---|---|---|---|
| frozen | 0.05046 [0.04986, 0.05106] | [0.04956, 0.05167] | 516000 | 95.20% | - | - | - |
| periodic_12h | 0.00445 [0.00427, 0.00464] | [0.00423, 0.00469] | 516000 | 98.09% | +0.96 [+0.96, +0.97] | +0.96 [+0.96, +0.97] | 1.00 (8) |
| periodic_24h | 0.00991 [0.00964, 0.01018] | [0.00941, 0.01053] | 516000 | 97.78% | +0.85 [+0.84, +0.86] | +0.86 [+0.84, +0.86] | 1.00 (8) |
| periodic_48h | 0.02017 [0.01979, 0.02055] | [0.01933, 0.02129] | 516000 | 97.15% | +0.63 [+0.61, +0.65] | +0.64 [+0.63, +0.65] | 0.00 (8) |
| oracle | 0.00273 [0.00259, 0.00288] | [0.00259, 0.00288] | 516000 | 98.19% | +1.00 [+1.00, +1.00] | +1.00 [+1.00, +1.00] | 1.00 (8) |
| moment_v1 | 0.15333 [0.15235, 0.15431] | [0.14847, 0.15774] | 516000 | 92.24% | -2.16 [-2.26, -2.05] | -2.16 [-2.29, -2.02] | 0.00 (8) |
| em_pi | 0.00605 [0.00584, 0.00626] | [0.00529, 0.00675] | 516000 | 97.78% | +0.93 [+0.91, +0.95] | +0.93 [+0.91, +0.94] | 1.00 (8) |
| em_pi_fast | 0.00347 [0.00332, 0.00364] | [0.00321, 0.00373] | 516000 | 98.06% | +0.98 [+0.98, +0.99] | +0.98 [+0.98, +0.99] | 1.00 (8) |
| em_pi_fast_lag | 0.00498 [0.00479, 0.00517] | [0.00440, 0.00542] | 516000 | 97.97% | +0.95 [+0.94, +0.96] | +0.95 [+0.94, +0.96] | 1.00 (8) |
| gated_v5 | 0.00328 [0.00313, 0.00344] | [0.00305, 0.00351] | 516000 | 98.10% | +0.99 [+0.98, +0.99] | +0.99 [+0.99, +0.99] | 1.00 (8) |
| em_pi_lag | 0.00756 [0.00733, 0.00780] | [0.00664, 0.00838] | 516000 | 97.68% | +0.90 [+0.88, +0.92] | +0.90 [+0.87, +0.91] | 1.00 (8) |
| gated_v5_lag | 0.00476 [0.00458, 0.00495] | [0.00437, 0.00512] | 516000 | 98.00% | +0.96 [+0.95, +0.97] | +0.96 [+0.95, +0.96] | 1.00 (8) |

frozen-vs-oracle LER gap: 4.773 percentage points

Paired LER differences (percentage points, 95% CI from the same resamples; negative = first arm better):
- em_pi_fast - frozen: -4.701 [-4.841, -4.590]
- em_pi_fast - oracle: +0.074 [+0.055, +0.094]
- gated_v5 - em_pi_fast: -0.019 [-0.027, -0.013]
- em_pi_fast_lag - em_pi_fast: +0.150 [+0.107, +0.193]
- periodic_24h - em_pi_fast: +0.644 [+0.595, +0.700]
- em_pi - em_pi_fast: +0.257 [+0.198, +0.314]
- gated_v5 - em_pi: -0.276 [-0.331, -0.217]
- gated_v5_lag - em_pi_fast_lag: -0.022 [-0.039, -0.002]
- gated_v5_lag - em_pi_lag: -0.279 [-0.336, -0.221]
- em_pi_lag - em_pi_fast_lag: +0.258 [+0.208, +0.309]

Labelled calibration cost per run (43 windows, 2000 labelled shots per recalibration; these are readout calibration shots, not QEC shots): periodic_12h 14.0 recalibration(s) = 28000 labelled shots (43.4% of the QEC shots); periodic_24h 7.0 recalibration(s) = 14000 labelled shots (21.7% of the QEC shots); periodic_48h 3.0 recalibration(s) = 6000 labelled shots (9.3% of the QEC shots); oracle 43.0 recalibration(s) = 86000 labelled shots (133.3% of the QEC shots). Downtime per recalibration is not modelled; oracle recalibrates every window and is an upper bound, not deployable. Label-free arms need none.
gated arm alarm fraction over all windows: 0.14

### physical_quiet_q1
PHYSICAL ONLY: controlled generator with no readout drift, physical error ramped x3; 150 unlabelled IQ points per update.

8 run(s); 43 windows per run, 1500 shots per window, d=5, physical error 0.001.

| arm | pooled LER [95% Wilson CI, counts shots only] | [95% CI resampling runs] | shots | mean accuracy | gap recovered, pooled [95% bootstrap CI over runs] | median per run [IQR] | runs >= 0.8 |
|---|---|---|---|---|---|---|---|
| frozen | 0.00531 [0.00511, 0.00551] | [0.00509, 0.00551] | 516000 | 98.20% | - | - | - |
| periodic_12h | 0.00533 [0.00513, 0.00553] | [0.00511, 0.00553] | 516000 | 98.20% | - | - | - |
| periodic_24h | 0.00535 [0.00516, 0.00556] | [0.00512, 0.00558] | 516000 | 98.20% | - | - | - |
| periodic_48h | 0.00535 [0.00516, 0.00555] | [0.00513, 0.00557] | 516000 | 98.20% | - | - | - |
| oracle | 0.00532 [0.00512, 0.00552] | [0.00513, 0.00550] | 516000 | 98.19% | - | - | - |
| moment_v1 | 0.04654 [0.04597, 0.04712] | [0.04339, 0.04990] | 516000 | 95.24% | - | - | - |
| em_pi | 0.00535 [0.00516, 0.00556] | [0.00516, 0.00555] | 516000 | 98.19% | - | - | - |
| em_pi_fast | 0.00544 [0.00525, 0.00565] | [0.00526, 0.00563] | 516000 | 98.18% | - | - | - |
| em_pi_fast_lag | 0.00546 [0.00527, 0.00567] | [0.00522, 0.00570] | 516000 | 98.17% | - | - | - |
| gated_v5 | 0.00541 [0.00521, 0.00561] | [0.00522, 0.00560] | 516000 | 98.18% | - | - | - |
| em_pi_lag | 0.00536 [0.00517, 0.00557] | [0.00514, 0.00559] | 516000 | 98.19% | - | - | - |
| gated_v5_lag | 0.00538 [0.00518, 0.00558] | [0.00514, 0.00561] | 516000 | 98.18% | - | - | - |

frozen-vs-oracle LER gap: -0.001 percentage points  (not distinguishable from zero, recovery fractions are not reported)

Paired LER differences (percentage points, 95% CI from the same resamples; negative = first arm better):
- em_pi_fast - frozen: +0.014 [+0.006, +0.022]
- em_pi_fast - oracle: +0.013 [+0.001, +0.022]
- gated_v5 - em_pi_fast: -0.004 [-0.012, +0.004]
- em_pi_fast_lag - em_pi_fast: +0.002 [-0.009, +0.014]
- periodic_24h - em_pi_fast: -0.009 [-0.020, +0.002]
- em_pi - em_pi_fast: -0.009 [-0.017, +0.000]
- gated_v5 - em_pi: +0.005 [+0.001, +0.008]
- gated_v5_lag - em_pi_fast_lag: -0.009 [-0.014, -0.004]
- gated_v5_lag - em_pi_lag: +0.001 [-0.004, +0.006]
- em_pi_lag - em_pi_fast_lag: -0.010 [-0.017, -0.003]

Labelled calibration cost per run (43 windows, 2000 labelled shots per recalibration; these are readout calibration shots, not QEC shots): periodic_12h 14.0 recalibration(s) = 28000 labelled shots (43.4% of the QEC shots); periodic_24h 7.0 recalibration(s) = 14000 labelled shots (21.7% of the QEC shots); periodic_48h 3.0 recalibration(s) = 6000 labelled shots (9.3% of the QEC shots); oracle 43.0 recalibration(s) = 86000 labelled shots (133.3% of the QEC shots). Downtime per recalibration is not modelled; oracle recalibrates every window and is an upper bound, not deployable. Label-free arms need none.
gated arm alarm fraction over all windows: 0.28

