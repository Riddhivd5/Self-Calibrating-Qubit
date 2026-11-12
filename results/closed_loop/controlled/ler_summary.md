etas used (from adaptive_boundary_v5.csv): quiet 0.3, alarm 0.9; d=5, physical error 0.001

### step_q1
CONTROLLED: imposed common-mode displacement, no other readout drift (step: 1 sigma along the centroid axis, applied at one third of the run).

8 run(s); 43 windows per run, 1500 shots per window, d=5, physical error 0.001.

| arm | pooled LER [95% Wilson CI, counts shots only] | [95% CI resampling runs] | shots | mean accuracy | gap recovered, pooled [95% bootstrap CI over runs] | median per run [IQR] | runs >= 0.8 |
|---|---|---|---|---|---|---|---|
| frozen | 0.05068 [0.05009, 0.05128] | [0.04968, 0.05183] | 516000 | 95.15% | - | - | - |
| periodic_12h | 0.00431 [0.00414, 0.00450] | [0.00416, 0.00446] | 516000 | 98.08% | +0.97 [+0.96, +0.97] | +0.97 [+0.96, +0.97] | 1.00 (8) |
| periodic_24h | 0.00951 [0.00925, 0.00978] | [0.00916, 0.00986] | 516000 | 97.77% | +0.86 [+0.85, +0.87] | +0.85 [+0.85, +0.87] | 1.00 (8) |
| periodic_48h | 0.01907 [0.01870, 0.01945] | [0.01836, 0.01978] | 516000 | 97.13% | +0.66 [+0.64, +0.68] | +0.66 [+0.63, +0.68] | 0.00 (8) |
| oracle | 0.00270 [0.00257, 0.00285] | [0.00259, 0.00281] | 516000 | 98.18% | +1.00 [+1.00, +1.00] | +1.00 [+1.00, +1.00] | 1.00 (8) |
| moment_v1 | 0.05759 [0.05696, 0.05823] | [0.05611, 0.05913] | 516000 | 94.57% | -0.14 [-0.17, -0.11] | -0.14 [-0.18, -0.13] | 0.00 (8) |
| em_pi | 0.00414 [0.00397, 0.00432] | [0.00386, 0.00448] | 516000 | 98.02% | +0.97 [+0.96, +0.98] | +0.97 [+0.97, +0.98] | 1.00 (8) |
| em_pi_fast | 0.00285 [0.00271, 0.00300] | [0.00267, 0.00306] | 516000 | 98.16% | +1.00 [+0.99, +1.00] | +1.00 [+1.00, +1.00] | 1.00 (8) |
| em_pi_fast_lag | 0.00438 [0.00421, 0.00457] | [0.00415, 0.00460] | 516000 | 98.06% | +0.96 [+0.96, +0.97] | +0.96 [+0.96, +0.97] | 1.00 (8) |
| gated_v5 | 0.00282 [0.00268, 0.00297] | [0.00270, 0.00296] | 516000 | 98.16% | +1.00 [+1.00, +1.00] | +1.00 [+1.00, +1.00] | 1.00 (8) |
| em_pi_lag | 0.00575 [0.00555, 0.00596] | [0.00540, 0.00612] | 516000 | 97.91% | +0.94 [+0.93, +0.94] | +0.94 [+0.93, +0.94] | 1.00 (8) |
| gated_v5_lag | 0.00437 [0.00419, 0.00455] | [0.00415, 0.00460] | 516000 | 98.06% | +0.97 [+0.96, +0.97] | +0.97 [+0.96, +0.97] | 1.00 (8) |

frozen-vs-oracle LER gap: 4.798 percentage points

Paired LER differences (percentage points, 95% CI from the same resamples; negative = first arm better):
- em_pi_fast - frozen: -4.785 [-4.909, -4.674]
- em_pi_fast - oracle: +0.015 [+0.005, +0.027]
- gated_v5 - em_pi_fast: -0.003 [-0.013, +0.005]
- em_pi_fast_lag - em_pi_fast: +0.153 [+0.131, +0.179]
- periodic_24h - em_pi_fast: +0.665 [+0.629, +0.702]
- em_pi - em_pi_fast: +0.129 [+0.108, +0.151]
- gated_v5 - em_pi: -0.132 [-0.158, -0.109]
- gated_v5_lag - em_pi_fast_lag: -0.001 [-0.006, +0.003]
- gated_v5_lag - em_pi_lag: -0.138 [-0.156, -0.122]
- em_pi_lag - em_pi_fast_lag: +0.137 [+0.120, +0.156]

Labelled calibration cost per run (43 windows, 2000 labelled shots per recalibration; these are readout calibration shots, not QEC shots): periodic_12h 14.0 recalibration(s) = 28000 labelled shots (43.4% of the QEC shots); periodic_24h 7.0 recalibration(s) = 14000 labelled shots (21.7% of the QEC shots); periodic_48h 3.0 recalibration(s) = 6000 labelled shots (9.3% of the QEC shots); oracle 43.0 recalibration(s) = 86000 labelled shots (133.3% of the QEC shots). Downtime per recalibration is not modelled; oracle recalibrates every window and is an upper bound, not deployable. Label-free arms need none.
gated arm alarm fraction over all windows: 0.05

### slow_q1
CONTROLLED: imposed common-mode displacement, no other readout drift (slow: 1 sigma along the centroid axis, reached linearly at the end of the run).

8 run(s); 43 windows per run, 1500 shots per window, d=5, physical error 0.001.

| arm | pooled LER [95% Wilson CI, counts shots only] | [95% CI resampling runs] | shots | mean accuracy | gap recovered, pooled [95% bootstrap CI over runs] | median per run [IQR] | runs >= 0.8 |
|---|---|---|---|---|---|---|---|
| frozen | 0.01825 [0.01789, 0.01862] | [0.01775, 0.01875] | 516000 | 96.73% | - | - | - |
| periodic_12h | 0.00274 [0.00260, 0.00288] | [0.00260, 0.00288] | 516000 | 98.18% | +1.00 [+0.99, +1.00] | +1.00 [+1.00, +1.00] | 1.00 (8) |
| periodic_24h | 0.00279 [0.00265, 0.00294] | [0.00267, 0.00292] | 516000 | 98.16% | +0.99 [+0.99, +1.00] | +1.00 [+0.99, +1.00] | 1.00 (8) |
| periodic_48h | 0.00307 [0.00292, 0.00323] | [0.00291, 0.00325] | 516000 | 98.10% | +0.98 [+0.97, +0.98] | +0.98 [+0.97, +0.99] | 1.00 (8) |
| oracle | 0.00270 [0.00257, 0.00285] | [0.00260, 0.00281] | 516000 | 98.18% | +1.00 [+1.00, +1.00] | +1.00 [+1.00, +1.00] | 1.00 (8) |
| moment_v1 | 0.04911 [0.04852, 0.04970] | [0.04792, 0.05026] | 516000 | 94.74% | -1.98 [-2.05, -1.92] | -2.02 [-2.04, -1.92] | 0.00 (8) |
| em_pi | 0.00278 [0.00264, 0.00292] | [0.00269, 0.00287] | 516000 | 98.17% | +1.00 [+0.99, +1.00] | +1.00 [+0.99, +1.00] | 1.00 (8) |
| em_pi_fast | 0.00271 [0.00257, 0.00286] | [0.00257, 0.00286] | 516000 | 98.18% | +1.00 [+1.00, +1.00] | +1.00 [+1.00, +1.00] | 1.00 (8) |
| em_pi_fast_lag | 0.00271 [0.00257, 0.00285] | [0.00260, 0.00283] | 516000 | 98.18% | +1.00 [+1.00, +1.00] | +1.00 [+1.00, +1.00] | 1.00 (8) |
| gated_v5 | 0.00277 [0.00263, 0.00292] | [0.00268, 0.00287] | 516000 | 98.17% | +1.00 [+0.99, +1.00] | +1.00 [+0.99, +1.00] | 1.00 (8) |
| em_pi_lag | 0.00283 [0.00268, 0.00297] | [0.00273, 0.00292] | 516000 | 98.16% | +0.99 [+0.99, +1.00] | +0.99 [+0.99, +0.99] | 1.00 (8) |
| gated_v5_lag | 0.00282 [0.00268, 0.00297] | [0.00273, 0.00291] | 516000 | 98.16% | +0.99 [+0.99, +1.00] | +0.99 [+0.99, +0.99] | 1.00 (8) |

frozen-vs-oracle LER gap: 1.555 percentage points

Paired LER differences (percentage points, 95% CI from the same resamples; negative = first arm better):
- em_pi_fast - frozen: -1.553 [-1.607, -1.501]
- em_pi_fast - oracle: +0.001 [-0.004, +0.006]
- gated_v5 - em_pi_fast: +0.006 [-0.003, +0.015]
- em_pi_fast_lag - em_pi_fast: -0.001 [-0.006, +0.005]
- periodic_24h - em_pi_fast: +0.008 [-0.000, +0.017]
- em_pi - em_pi_fast: +0.006 [-0.002, +0.015]
- gated_v5 - em_pi: -0.000 [-0.001, +0.000]
- gated_v5_lag - em_pi_fast_lag: +0.012 [+0.005, +0.019]
- gated_v5_lag - em_pi_lag: -0.000 [-0.001, +0.000]
- em_pi_lag - em_pi_fast_lag: +0.012 [+0.005, +0.019]

Labelled calibration cost per run (43 windows, 2000 labelled shots per recalibration; these are readout calibration shots, not QEC shots): periodic_12h 14.0 recalibration(s) = 28000 labelled shots (43.4% of the QEC shots); periodic_24h 7.0 recalibration(s) = 14000 labelled shots (21.7% of the QEC shots); periodic_48h 3.0 recalibration(s) = 6000 labelled shots (9.3% of the QEC shots); oracle 43.0 recalibration(s) = 86000 labelled shots (133.3% of the QEC shots). Downtime per recalibration is not modelled; oracle recalibrates every window and is an upper bound, not deployable. Label-free arms need none.
gated arm alarm fraction over all windows: 0.01

