etas used (from adaptive_boundary_v5.csv): quiet 0.3, alarm 0.9; d=5, physical error 0.001

### refit_q1
FITTED: profile refit on the 149 real snapshots (q1, jitter x1, events on, 336 h at 2 h steps); 50 unlabelled IQ points per update.

8 run(s); 169 windows per run, 1500 shots per window, d=5, physical error 0.001.

| arm | pooled LER [95% Wilson CI, counts shots only] | [95% CI resampling runs] | shots | mean accuracy | gap recovered, pooled [95% bootstrap CI over runs] | median per run [IQR] | runs >= 0.8 |
|---|---|---|---|---|---|---|---|
| frozen | 0.01771 [0.01753, 0.01790] | [0.01131, 0.02471] | 2028000 | 97.25% | - | - | - |
| periodic_12h | 0.01572 [0.01555, 0.01589] | [0.00997, 0.02176] | 2028000 | 97.37% | +0.26 [+0.10, +0.38] | +0.27 [+0.13, +0.39] | 0.00 (8) |
| periodic_24h | 0.01643 [0.01626, 0.01661] | [0.01059, 0.02280] | 2028000 | 97.30% | +0.17 [+0.03, +0.27] | +0.17 [+0.01, +0.26] | 0.00 (8) |
| periodic_48h | 0.01746 [0.01728, 0.01764] | [0.01102, 0.02464] | 2028000 | 97.22% | +0.03 [-0.10, +0.17] | +0.02 [-0.11, +0.12] | 0.00 (8) |
| oracle | 0.01002 [0.00989, 0.01016] | [0.00673, 0.01362] | 2028000 | 97.77% | +1.00 [+1.00, +1.00] | +1.00 [+1.00, +1.00] | 1.00 (8) |
| moment_v1 | 0.07114 [0.07079, 0.07150] | [0.05864, 0.08387] | 2028000 | 94.08% | -6.95 [-11.24, -5.23] | -6.85 [-16.38, -5.69] | 0.00 (8) |
| em_pi | 0.01290 [0.01275, 0.01306] | [0.00833, 0.01768] | 2028000 | 97.59% | +0.63 [+0.52, +0.71] | +0.62 [+0.55, +0.67] | 0.00 (8) |
| em_pi_fast | 0.01183 [0.01168, 0.01198] | [0.00759, 0.01626] | 2028000 | 97.64% | +0.77 [+0.67, +0.85] | +0.79 [+0.73, +0.83] | 0.50 (8) |
| em_pi_fast_lag | 0.01522 [0.01506, 0.01539] | [0.00985, 0.02092] | 2028000 | 97.40% | +0.32 [+0.14, +0.46] | +0.32 [-0.05, +0.45] | 0.00 (8) |
| gated_v5 | 0.01173 [0.01158, 0.01188] | [0.00757, 0.01602] | 2028000 | 97.64% | +0.78 [+0.71, +0.85] | +0.79 [+0.70, +0.82] | 0.50 (8) |
| em_pi_lag | 0.01436 [0.01420, 0.01452] | [0.00929, 0.01966] | 2028000 | 97.48% | +0.44 [+0.28, +0.55] | +0.44 [+0.29, +0.47] | 0.00 (8) |
| gated_v5_lag | 0.01461 [0.01445, 0.01478] | [0.00935, 0.02005] | 2028000 | 97.45% | +0.40 [+0.26, +0.53] | +0.36 [+0.27, +0.43] | 0.00 (8) |

frozen-vs-oracle LER gap: 0.769 percentage points

Paired LER differences (percentage points, 95% CI from the same resamples; negative = first arm better):
- em_pi_fast - frozen: -0.595 [-0.875, -0.340]
- em_pi_fast - oracle: +0.184 [+0.088, +0.291]
- gated_v5 - em_pi_fast: -0.011 [-0.039, +0.008]
- em_pi_fast_lag - em_pi_fast: +0.344 [+0.223, +0.470]
- periodic_24h - em_pi_fast: +0.466 [+0.277, +0.692]
- em_pi - em_pi_fast: +0.108 [+0.069, +0.145]
- gated_v5 - em_pi: -0.119 [-0.171, -0.069]
- gated_v5_lag - em_pi_fast_lag: -0.063 [-0.112, -0.012]
- gated_v5_lag - em_pi_lag: +0.025 [-0.009, +0.074]
- em_pi_lag - em_pi_fast_lag: -0.088 [-0.158, -0.025]

Labelled calibration cost per run (169 windows, 2000 labelled shots per recalibration; these are readout calibration shots, not QEC shots): periodic_12h 28.0 recalibration(s) = 56000 labelled shots (22.1% of the QEC shots); periodic_24h 14.0 recalibration(s) = 28000 labelled shots (11.0% of the QEC shots); periodic_48h 7.0 recalibration(s) = 14000 labelled shots (5.5% of the QEC shots); oracle 169.0 recalibration(s) = 338000 labelled shots (133.3% of the QEC shots). Downtime per recalibration is not modelled; oracle recalibrates every window and is an upper bound, not deployable. Label-free arms need none.
gated arm alarm fraction over all windows: 0.20

