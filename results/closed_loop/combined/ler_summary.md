etas used (from adaptive_boundary_v5.csv): quiet 0.3, alarm 0.9; d=5, physical error 0.001

### physical_quiet_q1
PHYSICAL ONLY: controlled generator with no readout drift, physical error ramped x3.

8 run(s); 43 windows per run, 1500 shots per window, d=5, physical error 0.001 ramped x3.

| arm | pooled LER [95% Wilson CI, counts shots only] | [95% CI resampling runs] | shots | mean accuracy | gap recovered, pooled [95% bootstrap CI over runs] | median per run [IQR] | runs >= 0.8 |
|---|---|---|---|---|---|---|---|
| frozen | 0.00528 [0.00509, 0.00549] | [0.00510, 0.00549] | 516000 | 98.19% | - | - | - |
| periodic_12h | 0.00526 [0.00507, 0.00546] | [0.00511, 0.00542] | 516000 | 98.18% | - | - | - |
| periodic_24h | 0.00530 [0.00511, 0.00551] | [0.00510, 0.00552] | 516000 | 98.18% | - | - | - |
| periodic_48h | 0.00529 [0.00510, 0.00549] | [0.00511, 0.00550] | 516000 | 98.18% | - | - | - |
| oracle | 0.00527 [0.00507, 0.00547] | [0.00509, 0.00546] | 516000 | 98.18% | - | - | - |
| moment_v1 | 0.04657 [0.04600, 0.04715] | [0.04535, 0.04781] | 516000 | 95.15% | - | - | - |
| em_pi | 0.00525 [0.00506, 0.00545] | [0.00505, 0.00547] | 516000 | 98.19% | - | - | - |
| em_pi_fast | 0.00523 [0.00504, 0.00543] | [0.00503, 0.00547] | 516000 | 98.18% | - | - | - |
| em_pi_fast_lag | 0.00526 [0.00506, 0.00546] | [0.00507, 0.00548] | 516000 | 98.18% | - | - | - |
| gated_v5 | 0.00522 [0.00503, 0.00542] | [0.00502, 0.00543] | 516000 | 98.18% | - | - | - |
| em_pi_lag | 0.00527 [0.00507, 0.00547] | [0.00505, 0.00551] | 516000 | 98.19% | - | - | - |
| gated_v5_lag | 0.00527 [0.00507, 0.00547] | [0.00504, 0.00550] | 516000 | 98.18% | - | - | - |

frozen-vs-oracle LER gap: 0.002 percentage points  (not distinguishable from zero, recovery fractions are not reported)

Paired LER differences (percentage points, 95% CI from the same resamples; negative = first arm better):
- em_pi_fast - frozen: -0.005 [-0.010, -0.000]
- em_pi_fast - oracle: -0.003 [-0.009, +0.003]
- gated_v5 - em_pi_fast: -0.001 [-0.005, +0.003]
- em_pi_fast_lag - em_pi_fast: +0.002 [-0.003, +0.007]
- periodic_24h - em_pi_fast: +0.007 [+0.002, +0.012]
- em_pi - em_pi_fast: +0.002 [-0.004, +0.007]
- gated_v5 - em_pi: -0.003 [-0.006, -0.000]
- gated_v5_lag - em_pi_fast_lag: +0.001 [-0.003, +0.004]
- gated_v5_lag - em_pi_lag: -0.000 [-0.002, +0.002]
- em_pi_lag - em_pi_fast_lag: +0.001 [-0.002, +0.004]

Labelled calibration cost per run (43 windows, 2000 labelled shots per recalibration; these are readout calibration shots, not QEC shots): periodic_12h 14.0 recalibration(s) = 28000 labelled shots (43.4% of the QEC shots); periodic_24h 7.0 recalibration(s) = 14000 labelled shots (21.7% of the QEC shots); periodic_48h 3.0 recalibration(s) = 6000 labelled shots (9.3% of the QEC shots); oracle 43.0 recalibration(s) = 86000 labelled shots (133.3% of the QEC shots). Downtime per recalibration is not modelled; oracle recalibrates every window and is an upper bound, not deployable. Label-free arms need none.
gated arm alarm fraction over all windows: 0.29

### step_physical_q1
COMBINED: imposed 1 sigma step of the readout at one third of the run AND physical error ramped x3 between one third and two thirds of the run (controlled generator, no other readout drift).

8 run(s); 43 windows per run, 1500 shots per window, d=5, physical error 0.001 ramped x3.

| arm | pooled LER [95% Wilson CI, counts shots only] | [95% CI resampling runs] | shots | mean accuracy | gap recovered, pooled [95% bootstrap CI over runs] | median per run [IQR] | runs >= 0.8 |
|---|---|---|---|---|---|---|---|
| frozen | 0.06004 [0.05940, 0.06069] | [0.05835, 0.06184] | 516000 | 95.15% | - | - | - |
| periodic_12h | 0.00688 [0.00665, 0.00711] | [0.00670, 0.00705] | 516000 | 98.08% | +0.97 [+0.97, +0.97] | +0.97 [+0.97, +0.97] | 1.00 (8) |
| periodic_24h | 0.01213 [0.01183, 0.01243] | [0.01187, 0.01236] | 516000 | 97.77% | +0.87 [+0.87, +0.88] | +0.87 [+0.86, +0.89] | 1.00 (8) |
| periodic_48h | 0.02275 [0.02235, 0.02316] | [0.02200, 0.02341] | 516000 | 97.13% | +0.68 [+0.66, +0.70] | +0.68 [+0.65, +0.70] | 0.00 (8) |
| oracle | 0.00527 [0.00507, 0.00547] | [0.00508, 0.00546] | 516000 | 98.18% | +1.00 [+1.00, +1.00] | +1.00 [+1.00, +1.00] | 1.00 (8) |
| moment_v1 | 0.06543 [0.06476, 0.06611] | [0.06374, 0.06719] | 516000 | 94.57% | -0.10 [-0.13, -0.07] | -0.11 [-0.13, -0.06] | 0.00 (8) |
| em_pi | 0.00670 [0.00648, 0.00693] | [0.00646, 0.00693] | 516000 | 98.02% | +0.97 [+0.97, +0.98] | +0.97 [+0.97, +0.98] | 1.00 (8) |
| em_pi_fast | 0.00538 [0.00519, 0.00559] | [0.00516, 0.00561] | 516000 | 98.16% | +1.00 [+1.00, +1.00] | +1.00 [+1.00, +1.00] | 1.00 (8) |
| em_pi_fast_lag | 0.00699 [0.00677, 0.00722] | [0.00673, 0.00722] | 516000 | 98.06% | +0.97 [+0.96, +0.97] | +0.97 [+0.96, +0.97] | 1.00 (8) |
| gated_v5 | 0.00541 [0.00521, 0.00561] | [0.00520, 0.00560] | 516000 | 98.16% | +1.00 [+1.00, +1.00] | +1.00 [+1.00, +1.00] | 1.00 (8) |
| em_pi_lag | 0.00833 [0.00808, 0.00858] | [0.00805, 0.00862] | 516000 | 97.91% | +0.94 [+0.94, +0.95] | +0.95 [+0.94, +0.95] | 1.00 (8) |
| gated_v5_lag | 0.00700 [0.00678, 0.00723] | [0.00674, 0.00723] | 516000 | 98.06% | +0.97 [+0.96, +0.97] | +0.97 [+0.97, +0.97] | 1.00 (8) |

frozen-vs-oracle LER gap: 5.478 percentage points

Paired LER differences (percentage points, 95% CI from the same resamples; negative = first arm better):
- em_pi_fast - frozen: -5.465 [-5.655, -5.292]
- em_pi_fast - oracle: +0.012 [+0.003, +0.021]
- gated_v5 - em_pi_fast: +0.002 [-0.002, +0.007]
- em_pi_fast_lag - em_pi_fast: +0.161 [+0.139, +0.185]
- periodic_24h - em_pi_fast: +0.674 [+0.641, +0.712]
- em_pi - em_pi_fast: +0.132 [+0.114, +0.146]
- gated_v5 - em_pi: -0.129 [-0.144, -0.112]
- gated_v5_lag - em_pi_fast_lag: +0.001 [-0.003, +0.004]
- gated_v5_lag - em_pi_lag: -0.132 [-0.145, -0.120]
- em_pi_lag - em_pi_fast_lag: +0.133 [+0.119, +0.147]

Labelled calibration cost per run (43 windows, 2000 labelled shots per recalibration; these are readout calibration shots, not QEC shots): periodic_12h 14.0 recalibration(s) = 28000 labelled shots (43.4% of the QEC shots); periodic_24h 7.0 recalibration(s) = 14000 labelled shots (21.7% of the QEC shots); periodic_48h 3.0 recalibration(s) = 6000 labelled shots (9.3% of the QEC shots); oracle 43.0 recalibration(s) = 86000 labelled shots (133.3% of the QEC shots). Downtime per recalibration is not modelled; oracle recalibrates every window and is an upper bound, not deployable. Label-free arms need none.
gated arm alarm fraction over all windows: 0.35

