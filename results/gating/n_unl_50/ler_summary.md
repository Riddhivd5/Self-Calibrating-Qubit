etas used (from adaptive_boundary_v5.csv): quiet 0.3, alarm 0.9; d=5, physical error 0.001

### quiet_q1
QUIET: controlled generator with no drift at all; 50 unlabelled IQ points per update.

8 run(s); 43 windows per run, 1500 shots per window, d=5, physical error 0.001.

| arm | pooled LER [95% Wilson CI, counts shots only] | [95% CI resampling runs] | shots | mean accuracy | gap recovered, pooled [95% bootstrap CI over runs] | median per run [IQR] | runs >= 0.8 |
|---|---|---|---|---|---|---|---|
| frozen | 0.00275 [0.00261, 0.00289] | [0.00262, 0.00287] | 516000 | 98.18% | - | - | - |
| periodic_12h | 0.00272 [0.00258, 0.00287] | [0.00263, 0.00281] | 516000 | 98.18% | - | - | - |
| periodic_24h | 0.00272 [0.00258, 0.00287] | [0.00262, 0.00282] | 516000 | 98.18% | - | - | - |
| periodic_48h | 0.00273 [0.00260, 0.00288] | [0.00262, 0.00284] | 516000 | 98.18% | - | - | - |
| oracle | 0.00275 [0.00261, 0.00290] | [0.00265, 0.00286] | 516000 | 98.18% | - | - | - |
| moment_v1 | 0.03881 [0.03828, 0.03934] | [0.03550, 0.04176] | 516000 | 95.36% | - | - | - |
| em_pi | 0.00277 [0.00263, 0.00291] | [0.00265, 0.00288] | 516000 | 98.16% | - | - | - |
| em_pi_fast | 0.00305 [0.00291, 0.00321] | [0.00291, 0.00318] | 516000 | 98.10% | - | - | - |
| em_pi_fast_lag | 0.00300 [0.00285, 0.00315] | [0.00292, 0.00307] | 516000 | 98.10% | - | - | - |
| gated_v5 | 0.00276 [0.00262, 0.00291] | [0.00265, 0.00287] | 516000 | 98.16% | - | - | - |
| em_pi_lag | 0.00275 [0.00261, 0.00289] | [0.00258, 0.00290] | 516000 | 98.16% | - | - | - |
| gated_v5_lag | 0.00275 [0.00261, 0.00290] | [0.00258, 0.00290] | 516000 | 98.16% | - | - | - |

frozen-vs-oracle LER gap: -0.001 percentage points  (not distinguishable from zero, recovery fractions are not reported)

Paired LER differences (percentage points, 95% CI from the same resamples; negative = first arm better):
- em_pi_fast - frozen: +0.030 [+0.019, +0.043]
- em_pi_fast - oracle: +0.030 [+0.018, +0.043]
- gated_v5 - em_pi_fast: -0.029 [-0.042, -0.017]
- em_pi_fast_lag - em_pi_fast: -0.006 [-0.014, +0.006]
- periodic_24h - em_pi_fast: -0.033 [-0.045, -0.022]
- em_pi - em_pi_fast: -0.029 [-0.042, -0.016]
- gated_v5 - em_pi: -0.001 [-0.002, +0.000]
- gated_v5_lag - em_pi_fast_lag: -0.024 [-0.036, -0.011]
- gated_v5_lag - em_pi_lag: +0.001 [+0.000, +0.002]
- em_pi_lag - em_pi_fast_lag: -0.025 [-0.037, -0.012]

Labelled calibration cost per run (43 windows, 2000 labelled shots per recalibration; these are readout calibration shots, not QEC shots): periodic_12h 14.0 recalibration(s) = 28000 labelled shots (43.4% of the QEC shots); periodic_24h 7.0 recalibration(s) = 14000 labelled shots (21.7% of the QEC shots); periodic_48h 3.0 recalibration(s) = 6000 labelled shots (9.3% of the QEC shots); oracle 43.0 recalibration(s) = 86000 labelled shots (133.3% of the QEC shots). Downtime per recalibration is not modelled; oracle recalibrates every window and is an upper bound, not deployable. Label-free arms need none.
gated arm alarm fraction over all windows: 0.01

### step_q1
CONTROLLED: imposed common-mode displacement, no other readout drift (step: 1 sigma along the centroid axis, applied at one third of the run); 50 unlabelled IQ points per update.

8 run(s); 43 windows per run, 1500 shots per window, d=5, physical error 0.001.

| arm | pooled LER [95% Wilson CI, counts shots only] | [95% CI resampling runs] | shots | mean accuracy | gap recovered, pooled [95% bootstrap CI over runs] | median per run [IQR] | runs >= 0.8 |
|---|---|---|---|---|---|---|---|
| frozen | 0.05128 [0.05068, 0.05188] | [0.04985, 0.05246] | 516000 | 95.18% | - | - | - |
| periodic_12h | 0.00438 [0.00420, 0.00456] | [0.00421, 0.00455] | 516000 | 98.08% | +0.97 [+0.96, +0.97] | +0.97 [+0.97, +0.97] | 1.00 (8) |
| periodic_24h | 0.00969 [0.00943, 0.00996] | [0.00934, 0.01013] | 516000 | 97.76% | +0.86 [+0.85, +0.87] | +0.86 [+0.85, +0.86] | 1.00 (8) |
| periodic_48h | 0.01952 [0.01914, 0.01990] | [0.01884, 0.02020] | 516000 | 97.14% | +0.65 [+0.64, +0.67] | +0.66 [+0.65, +0.66] | 0.00 (8) |
| oracle | 0.00275 [0.00261, 0.00290] | [0.00265, 0.00286] | 516000 | 98.18% | +1.00 [+1.00, +1.00] | +1.00 [+1.00, +1.00] | 1.00 (8) |
| moment_v1 | 0.05439 [0.05377, 0.05501] | [0.04980, 0.05828] | 516000 | 94.83% | -0.06 [-0.14, +0.03] | -0.13 [-0.14, -0.03] | 0.00 (8) |
| em_pi | 0.00464 [0.00446, 0.00483] | [0.00434, 0.00499] | 516000 | 97.97% | +0.96 [+0.95, +0.97] | +0.96 [+0.96, +0.97] | 1.00 (8) |
| em_pi_fast | 0.00333 [0.00318, 0.00349] | [0.00311, 0.00355] | 516000 | 98.07% | +0.99 [+0.98, +0.99] | +0.99 [+0.98, +0.99] | 1.00 (8) |
| em_pi_fast_lag | 0.00514 [0.00494, 0.00533] | [0.00472, 0.00551] | 516000 | 97.96% | +0.95 [+0.94, +0.96] | +0.95 [+0.94, +0.96] | 1.00 (8) |
| gated_v5 | 0.00313 [0.00298, 0.00328] | [0.00299, 0.00328] | 516000 | 98.12% | +0.99 [+0.99, +1.00] | +0.99 [+0.99, +1.00] | 1.00 (8) |
| em_pi_lag | 0.00655 [0.00633, 0.00677] | [0.00608, 0.00712] | 516000 | 97.87% | +0.92 [+0.91, +0.93] | +0.92 [+0.92, +0.93] | 1.00 (8) |
| gated_v5_lag | 0.00484 [0.00465, 0.00503] | [0.00459, 0.00514] | 516000 | 98.02% | +0.96 [+0.95, +0.96] | +0.96 [+0.96, +0.96] | 1.00 (8) |

frozen-vs-oracle LER gap: 4.852 percentage points

Paired LER differences (percentage points, 95% CI from the same resamples; negative = first arm better):
- em_pi_fast - frozen: -4.793 [-4.916, -4.641]
- em_pi_fast - oracle: +0.058 [+0.035, +0.084]
- gated_v5 - em_pi_fast: -0.020 [-0.033, -0.008]
- em_pi_fast_lag - em_pi_fast: +0.181 [+0.142, +0.213]
- periodic_24h - em_pi_fast: +0.636 [+0.598, +0.684]
- em_pi - em_pi_fast: +0.131 [+0.103, +0.162]
- gated_v5 - em_pi: -0.151 [-0.178, -0.129]
- gated_v5_lag - em_pi_fast_lag: -0.030 [-0.064, +0.006]
- gated_v5_lag - em_pi_lag: -0.172 [-0.199, -0.146]
- em_pi_lag - em_pi_fast_lag: +0.142 [+0.102, +0.181]

Labelled calibration cost per run (43 windows, 2000 labelled shots per recalibration; these are readout calibration shots, not QEC shots): periodic_12h 14.0 recalibration(s) = 28000 labelled shots (43.4% of the QEC shots); periodic_24h 7.0 recalibration(s) = 14000 labelled shots (21.7% of the QEC shots); periodic_48h 3.0 recalibration(s) = 6000 labelled shots (9.3% of the QEC shots); oracle 43.0 recalibration(s) = 86000 labelled shots (133.3% of the QEC shots). Downtime per recalibration is not modelled; oracle recalibrates every window and is an upper bound, not deployable. Label-free arms need none.
gated arm alarm fraction over all windows: 0.06

### mixshift_quiet_q1
QUIET: controlled generator with no drift at all; |1> share of the unlabelled stream changes 0.3 -> 0.1 -> 0.5 by thirds of the run, pi fixed at its first estimate; 50 unlabelled IQ points per update.

8 run(s); 43 windows per run, 1500 shots per window, d=5, physical error 0.001.

| arm | pooled LER [95% Wilson CI, counts shots only] | [95% CI resampling runs] | shots | mean accuracy | gap recovered, pooled [95% bootstrap CI over runs] | median per run [IQR] | runs >= 0.8 |
|---|---|---|---|---|---|---|---|
| frozen | 0.00275 [0.00261, 0.00289] | [0.00263, 0.00287] | 516000 | 98.18% | - | - | - |
| periodic_12h | 0.00272 [0.00258, 0.00287] | [0.00263, 0.00281] | 516000 | 98.18% | - | - | - |
| periodic_24h | 0.00272 [0.00258, 0.00287] | [0.00263, 0.00282] | 516000 | 98.18% | - | - | - |
| periodic_48h | 0.00273 [0.00260, 0.00288] | [0.00263, 0.00284] | 516000 | 98.18% | - | - | - |
| oracle | 0.00275 [0.00261, 0.00290] | [0.00266, 0.00287] | 516000 | 98.18% | - | - | - |
| moment_v1 | 0.12969 [0.12878, 0.13061] | [0.12182, 0.13722] | 516000 | 93.00% | - | - | - |
| em_pi | 0.00280 [0.00266, 0.00295] | [0.00271, 0.00290] | 516000 | 98.16% | - | - | - |
| em_pi_fast | 0.00311 [0.00296, 0.00326] | [0.00290, 0.00336] | 516000 | 98.10% | - | - | - |
| em_pi_fast_lag | 0.00306 [0.00291, 0.00321] | [0.00288, 0.00330] | 516000 | 98.11% | - | - | - |
| gated_v5 | 0.00280 [0.00266, 0.00295] | [0.00271, 0.00290] | 516000 | 98.17% | - | - | - |
| em_pi_lag | 0.00276 [0.00262, 0.00291] | [0.00259, 0.00292] | 516000 | 98.17% | - | - | - |
| gated_v5_lag | 0.00277 [0.00263, 0.00291] | [0.00260, 0.00293] | 516000 | 98.17% | - | - | - |

frozen-vs-oracle LER gap: -0.001 percentage points  (not distinguishable from zero, recovery fractions are not reported)

Paired LER differences (percentage points, 95% CI from the same resamples; negative = first arm better):
- em_pi_fast - frozen: +0.036 [+0.012, +0.066]
- em_pi_fast - oracle: +0.036 [+0.012, +0.065]
- gated_v5 - em_pi_fast: -0.031 [-0.056, -0.011]
- em_pi_fast_lag - em_pi_fast: -0.005 [-0.014, +0.005]
- periodic_24h - em_pi_fast: -0.039 [-0.067, -0.016]
- em_pi - em_pi_fast: -0.031 [-0.055, -0.011]
- gated_v5 - em_pi: -0.000 [-0.001, +0.000]
- gated_v5_lag - em_pi_fast_lag: -0.029 [-0.058, -0.008]
- gated_v5_lag - em_pi_lag: +0.000 [+0.000, +0.001]
- em_pi_lag - em_pi_fast_lag: -0.030 [-0.058, -0.009]

Labelled calibration cost per run (43 windows, 2000 labelled shots per recalibration; these are readout calibration shots, not QEC shots): periodic_12h 14.0 recalibration(s) = 28000 labelled shots (43.4% of the QEC shots); periodic_24h 7.0 recalibration(s) = 14000 labelled shots (21.7% of the QEC shots); periodic_48h 3.0 recalibration(s) = 6000 labelled shots (9.3% of the QEC shots); oracle 43.0 recalibration(s) = 86000 labelled shots (133.3% of the QEC shots). Downtime per recalibration is not modelled; oracle recalibrates every window and is an upper bound, not deployable. Label-free arms need none.
gated arm alarm fraction over all windows: 0.01

### mixshift_step_q1
CONTROLLED: imposed common-mode displacement, no other readout drift (step: 1 sigma along the centroid axis, applied at one third of the run); |1> share of the unlabelled stream changes 0.3 -> 0.1 -> 0.5 by thirds of the run, pi fixed at its first estimate; 50 unlabelled IQ points per update.

8 run(s); 43 windows per run, 1500 shots per window, d=5, physical error 0.001.

| arm | pooled LER [95% Wilson CI, counts shots only] | [95% CI resampling runs] | shots | mean accuracy | gap recovered, pooled [95% bootstrap CI over runs] | median per run [IQR] | runs >= 0.8 |
|---|---|---|---|---|---|---|---|
| frozen | 0.05128 [0.05068, 0.05188] | [0.04992, 0.05248] | 516000 | 95.18% | - | - | - |
| periodic_12h | 0.00438 [0.00420, 0.00456] | [0.00421, 0.00456] | 516000 | 98.08% | +0.97 [+0.96, +0.97] | +0.97 [+0.97, +0.97] | 1.00 (8) |
| periodic_24h | 0.00969 [0.00943, 0.00996] | [0.00934, 0.01014] | 516000 | 97.76% | +0.86 [+0.85, +0.87] | +0.86 [+0.85, +0.86] | 1.00 (8) |
| periodic_48h | 0.01952 [0.01914, 0.01990] | [0.01887, 0.02023] | 516000 | 97.14% | +0.65 [+0.64, +0.67] | +0.66 [+0.65, +0.66] | 0.00 (8) |
| oracle | 0.00275 [0.00261, 0.00290] | [0.00265, 0.00287] | 516000 | 98.18% | +1.00 [+1.00, +1.00] | +1.00 [+1.00, +1.00] | 1.00 (8) |
| moment_v1 | 0.15397 [0.15299, 0.15496] | [0.14665, 0.16145] | 516000 | 92.22% | -2.12 [-2.23, -2.00] | -2.05 [-2.31, -1.99] | 0.00 (8) |
| em_pi | 0.00716 [0.00693, 0.00739] | [0.00663, 0.00783] | 516000 | 97.66% | +0.91 [+0.90, +0.92] | +0.92 [+0.90, +0.92] | 1.00 (8) |
| em_pi_fast | 0.00429 [0.00412, 0.00447] | [0.00368, 0.00499] | 516000 | 97.94% | +0.97 [+0.95, +0.98] | +0.98 [+0.96, +0.98] | 1.00 (8) |
| em_pi_fast_lag | 0.00605 [0.00584, 0.00626] | [0.00533, 0.00686] | 516000 | 97.84% | +0.93 [+0.91, +0.95] | +0.94 [+0.93, +0.95] | 1.00 (8) |
| gated_v5 | 0.00410 [0.00393, 0.00428] | [0.00366, 0.00462] | 516000 | 97.98% | +0.97 [+0.96, +0.98] | +0.98 [+0.96, +0.98] | 1.00 (8) |
| em_pi_lag | 0.00894 [0.00869, 0.00920] | [0.00822, 0.00993] | 516000 | 97.56% | +0.87 [+0.85, +0.89] | +0.88 [+0.86, +0.89] | 1.00 (8) |
| gated_v5_lag | 0.00583 [0.00563, 0.00604] | [0.00548, 0.00623] | 516000 | 97.87% | +0.94 [+0.93, +0.94] | +0.94 [+0.93, +0.94] | 1.00 (8) |

frozen-vs-oracle LER gap: 4.852 percentage points

Paired LER differences (percentage points, 95% CI from the same resamples; negative = first arm better):
- em_pi_fast - frozen: -4.700 [-4.845, -4.538]
- em_pi_fast - oracle: +0.152 [+0.089, +0.228]
- gated_v5 - em_pi_fast: -0.018 [-0.050, +0.009]
- em_pi_fast_lag - em_pi_fast: +0.176 [+0.133, +0.211]
- periodic_24h - em_pi_fast: +0.541 [+0.466, +0.612]
- em_pi - em_pi_fast: +0.289 [+0.196, +0.381]
- gated_v5 - em_pi: -0.308 [-0.396, -0.230]
- gated_v5_lag - em_pi_fast_lag: -0.020 [-0.079, +0.034]
- gated_v5_lag - em_pi_lag: -0.313 [-0.400, -0.237]
- em_pi_lag - em_pi_fast_lag: +0.293 [+0.184, +0.397]

Labelled calibration cost per run (43 windows, 2000 labelled shots per recalibration; these are readout calibration shots, not QEC shots): periodic_12h 14.0 recalibration(s) = 28000 labelled shots (43.4% of the QEC shots); periodic_24h 7.0 recalibration(s) = 14000 labelled shots (21.7% of the QEC shots); periodic_48h 3.0 recalibration(s) = 6000 labelled shots (9.3% of the QEC shots); oracle 43.0 recalibration(s) = 86000 labelled shots (133.3% of the QEC shots). Downtime per recalibration is not modelled; oracle recalibrates every window and is an upper bound, not deployable. Label-free arms need none.
gated arm alarm fraction over all windows: 0.24

### physical_quiet_q1
PHYSICAL ONLY: controlled generator with no readout drift, physical error ramped x3; 50 unlabelled IQ points per update.

8 run(s); 43 windows per run, 1500 shots per window, d=5, physical error 0.001.

| arm | pooled LER [95% Wilson CI, counts shots only] | [95% CI resampling runs] | shots | mean accuracy | gap recovered, pooled [95% bootstrap CI over runs] | median per run [IQR] | runs >= 0.8 |
|---|---|---|---|---|---|---|---|
| frozen | 0.00525 [0.00506, 0.00545] | [0.00501, 0.00548] | 516000 | 98.18% | - | - | - |
| periodic_12h | 0.00525 [0.00505, 0.00545] | [0.00502, 0.00545] | 516000 | 98.18% | - | - | - |
| periodic_24h | 0.00527 [0.00507, 0.00547] | [0.00503, 0.00547] | 516000 | 98.18% | - | - | - |
| periodic_48h | 0.00526 [0.00506, 0.00546] | [0.00502, 0.00548] | 516000 | 98.18% | - | - | - |
| oracle | 0.00531 [0.00512, 0.00552] | [0.00509, 0.00552] | 516000 | 98.18% | - | - | - |
| moment_v1 | 0.04612 [0.04555, 0.04670] | [0.04258, 0.04947] | 516000 | 95.36% | - | - | - |
| em_pi | 0.00537 [0.00518, 0.00558] | [0.00517, 0.00559] | 516000 | 98.16% | - | - | - |
| em_pi_fast | 0.00574 [0.00553, 0.00595] | [0.00557, 0.00590] | 516000 | 98.10% | - | - | - |
| em_pi_fast_lag | 0.00571 [0.00551, 0.00592] | [0.00552, 0.00591] | 516000 | 98.10% | - | - | - |
| gated_v5 | 0.00553 [0.00533, 0.00573] | [0.00524, 0.00580] | 516000 | 98.14% | - | - | - |
| em_pi_lag | 0.00532 [0.00512, 0.00552] | [0.00510, 0.00554] | 516000 | 98.16% | - | - | - |
| gated_v5_lag | 0.00547 [0.00528, 0.00568] | [0.00522, 0.00574] | 516000 | 98.14% | - | - | - |

frozen-vs-oracle LER gap: -0.006 percentage points  (not distinguishable from zero, recovery fractions are not reported)

Paired LER differences (percentage points, 95% CI from the same resamples; negative = first arm better):
- em_pi_fast - frozen: +0.049 [+0.034, +0.066]
- em_pi_fast - oracle: +0.042 [+0.028, +0.057]
- gated_v5 - em_pi_fast: -0.021 [-0.037, -0.009]
- em_pi_fast_lag - em_pi_fast: -0.003 [-0.014, +0.009]
- periodic_24h - em_pi_fast: -0.047 [-0.064, -0.032]
- em_pi - em_pi_fast: -0.036 [-0.047, -0.027]
- gated_v5 - em_pi: +0.015 [+0.005, +0.025]
- gated_v5_lag - em_pi_fast_lag: -0.024 [-0.039, -0.013]
- gated_v5_lag - em_pi_lag: +0.015 [+0.008, +0.022]
- em_pi_lag - em_pi_fast_lag: -0.039 [-0.051, -0.028]

Labelled calibration cost per run (43 windows, 2000 labelled shots per recalibration; these are readout calibration shots, not QEC shots): periodic_12h 14.0 recalibration(s) = 28000 labelled shots (43.4% of the QEC shots); periodic_24h 7.0 recalibration(s) = 14000 labelled shots (21.7% of the QEC shots); periodic_48h 3.0 recalibration(s) = 6000 labelled shots (9.3% of the QEC shots); oracle 43.0 recalibration(s) = 86000 labelled shots (133.3% of the QEC shots). Downtime per recalibration is not modelled; oracle recalibrates every window and is an upper bound, not deployable. Label-free arms need none.
gated arm alarm fraction over all windows: 0.27

