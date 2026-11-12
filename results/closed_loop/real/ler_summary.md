etas used (from adaptive_boundary_v5.csv): quiet 0.3, alarm 0.9; d=5, physical error 0.001

### real_q0
REAL REPLAY: the IBM snapshots.

8 run(s); 149 windows per run, 1500 shots per window, d=5, physical error 0.001.

| arm | pooled LER [95% Wilson CI, counts shots only] | [95% CI resampling window blocks, one shared trajectory] | shots | mean accuracy | gap recovered, pooled [95% bootstrap CI over runs] | median per run [IQR] | runs >= 0.8 |
|---|---|---|---|---|---|---|---|
| frozen | 0.00498 [0.00488, 0.00508] | [0.00412, 0.00609] | 1788000 | 97.81% | - | - | - |
| periodic_12h | 0.00448 [0.00438, 0.00458] | [0.00352, 0.00581] | 1788000 | 97.93% | +0.72 [+0.68, +0.75] | +0.72 [+0.70, +0.74] | 0.00 (8) |
| periodic_24h | 0.00437 [0.00427, 0.00447] | [0.00352, 0.00546] | 1788000 | 97.92% | +0.87 [+0.85, +0.90] | +0.87 [+0.86, +0.90] | 1.00 (8) |
| periodic_48h | 0.00442 [0.00432, 0.00452] | [0.00355, 0.00558] | 1788000 | 97.92% | +0.80 [+0.77, +0.84] | +0.79 [+0.78, +0.81] | 0.25 (8) |
| oracle | 0.00428 [0.00419, 0.00438] | [0.00348, 0.00531] | 1788000 | 97.95% | +1.00 [+1.00, +1.00] | +1.00 [+1.00, +1.00] | 1.00 (8) |
| moment_v1 | 0.03047 [0.03022, 0.03072] | [0.02806, 0.03349] | 1788000 | 95.58% | -36.46 [-39.16, -34.15] | -36.74 [-37.59, -35.19] | 0.00 (8) |
| em_pi | 0.00429 [0.00420, 0.00439] | [0.00347, 0.00537] | 1788000 | 97.94% | +0.98 [+0.97, +1.00] | +0.99 [+0.97, +1.00] | 1.00 (8) |
| em_pi_fast | 0.00429 [0.00419, 0.00438] | [0.00350, 0.00531] | 1788000 | 97.94% | +0.99 [+0.98, +1.00] | +0.99 [+0.98, +1.00] | 1.00 (8) |
| em_pi_fast_lag | 0.00442 [0.00432, 0.00452] | [0.00352, 0.00564] | 1788000 | 97.93% | +0.80 [+0.75, +0.85] | +0.79 [+0.73, +0.88] | 0.50 (8) |
| gated_v5 | 0.00429 [0.00419, 0.00439] | [0.00349, 0.00531] | 1788000 | 97.94% | +0.99 [+0.96, +1.01] | +1.00 [+0.98, +1.01] | 1.00 (8) |
| em_pi_lag | 0.00436 [0.00427, 0.00446] | [0.00349, 0.00553] | 1788000 | 97.93% | +0.88 [+0.85, +0.91] | +0.88 [+0.85, +0.93] | 1.00 (8) |
| gated_v5_lag | 0.00440 [0.00430, 0.00450] | [0.00352, 0.00559] | 1788000 | 97.93% | +0.83 [+0.79, +0.88] | +0.81 [+0.77, +0.90] | 0.50 (8) |

frozen-vs-oracle LER gap: 0.070 percentage points

Real-data scenario: one 15.6-day trajectory replayed repeatedly (runs differ only in which unlabelled IQ points are drawn). The block-bootstrap interval describes uncertainty within this trajectory; it is not a set of independent real-world trajectories.

Paired LER differences (percentage points, 95% CI from the same resamples; negative = first arm better):
- em_pi_fast - frozen: -0.069 [-0.091, -0.049]
- em_pi_fast - oracle: +0.001 [-0.005, +0.007]
- gated_v5 - em_pi_fast: +0.000 [-0.002, +0.002]
- em_pi_fast_lag - em_pi_fast: +0.013 [-0.001, +0.034]
- periodic_24h - em_pi_fast: +0.008 [-0.001, +0.018]
- em_pi - em_pi_fast: +0.000 [-0.006, +0.008]
- gated_v5 - em_pi: -0.000 [-0.007, +0.005]
- gated_v5_lag - em_pi_fast_lag: -0.002 [-0.007, +0.001]
- gated_v5_lag - em_pi_lag: +0.004 [-0.001, +0.009]
- em_pi_lag - em_pi_fast_lag: -0.006 [-0.013, +0.001]

Labelled calibration cost per run (149 windows, 1000 labelled shots per recalibration; these are readout calibration shots, not QEC shots): periodic_12h 27.0 recalibration(s) = 27000 labelled shots (12.1% of the QEC shots); periodic_24h 14.0 recalibration(s) = 14000 labelled shots (6.3% of the QEC shots); periodic_48h 7.0 recalibration(s) = 7000 labelled shots (3.1% of the QEC shots); oracle 149.0 recalibration(s) = 149000 labelled shots (66.7% of the QEC shots). Downtime per recalibration is not modelled; oracle recalibrates every window and is an upper bound, not deployable. Label-free arms need none.
gated arm alarm fraction over all windows: 0.65

### real_q1
REAL REPLAY: the IBM snapshots.

8 run(s); 149 windows per run, 1500 shots per window, d=5, physical error 0.001.

| arm | pooled LER [95% Wilson CI, counts shots only] | [95% CI resampling window blocks, one shared trajectory] | shots | mean accuracy | gap recovered, pooled [95% bootstrap CI over runs] | median per run [IQR] | runs >= 0.8 |
|---|---|---|---|---|---|---|---|
| frozen | 0.00892 [0.00878, 0.00906] | [0.00514, 0.01379] | 1788000 | 97.72% | - | - | - |
| periodic_12h | 0.00881 [0.00867, 0.00894] | [0.00522, 0.01327] | 1788000 | 97.72% | +0.05 [+0.03, +0.06] | +0.05 [+0.05, +0.06] | 0.00 (8) |
| periodic_24h | 0.00963 [0.00949, 0.00978] | [0.00554, 0.01456] | 1788000 | 97.69% | -0.31 [-0.35, -0.28] | -0.30 [-0.35, -0.29] | 0.00 (8) |
| periodic_48h | 0.01050 [0.01036, 0.01065] | [0.00657, 0.01532] | 1788000 | 97.48% | -0.70 [-0.75, -0.64] | -0.73 [-0.74, -0.68] | 0.00 (8) |
| oracle | 0.00663 [0.00652, 0.00675] | [0.00425, 0.00963] | 1788000 | 97.86% | +1.00 [+1.00, +1.00] | +1.00 [+1.00, +1.00] | 1.00 (8) |
| moment_v1 | 0.04234 [0.04205, 0.04264] | [0.03194, 0.05436] | 1788000 | 95.18% | -14.64 [-15.35, -13.93] | -14.94 [-15.26, -14.27] | 0.00 (8) |
| em_pi | 0.00742 [0.00729, 0.00755] | [0.00464, 0.01071] | 1788000 | 97.79% | +0.66 [+0.63, +0.69] | +0.65 [+0.62, +0.67] | 0.00 (8) |
| em_pi_fast | 0.00667 [0.00655, 0.00679] | [0.00428, 0.00967] | 1788000 | 97.85% | +0.99 [+0.97, +1.00] | +0.98 [+0.96, +1.00] | 1.00 (8) |
| em_pi_fast_lag | 0.00824 [0.00811, 0.00838] | [0.00519, 0.01189] | 1788000 | 97.73% | +0.30 [+0.25, +0.32] | +0.32 [+0.30, +0.32] | 0.00 (8) |
| gated_v5 | 0.00684 [0.00672, 0.00696] | [0.00442, 0.00984] | 1788000 | 97.80% | +0.91 [+0.89, +0.93] | +0.92 [+0.89, +0.93] | 1.00 (8) |
| em_pi_lag | 0.00844 [0.00831, 0.00858] | [0.00516, 0.01231] | 1788000 | 97.72% | +0.21 [+0.17, +0.24] | +0.21 [+0.19, +0.23] | 0.00 (8) |
| gated_v5_lag | 0.00836 [0.00822, 0.00849] | [0.00527, 0.01201] | 1788000 | 97.70% | +0.25 [+0.18, +0.30] | +0.26 [+0.19, +0.29] | 0.00 (8) |

frozen-vs-oracle LER gap: 0.228 percentage points

Real-data scenario: one 15.6-day trajectory replayed repeatedly (runs differ only in which unlabelled IQ points are drawn). The block-bootstrap interval describes uncertainty within this trajectory; it is not a set of independent real-world trajectories.

Paired LER differences (percentage points, 95% CI from the same resamples; negative = first arm better):
- em_pi_fast - frozen: -0.230 [-0.510, -0.062]
- em_pi_fast - oracle: +0.003 [-0.016, +0.021]
- gated_v5 - em_pi_fast: +0.017 [+0.003, +0.033]
- em_pi_fast_lag - em_pi_fast: +0.159 [+0.070, +0.256]
- periodic_24h - em_pi_fast: +0.299 [+0.116, +0.529]
- em_pi - em_pi_fast: +0.076 [+0.030, +0.132]
- gated_v5 - em_pi: -0.059 [-0.111, -0.016]
- gated_v5_lag - em_pi_fast_lag: +0.012 [-0.008, +0.032]
- gated_v5_lag - em_pi_lag: -0.009 [-0.074, +0.055]
- em_pi_lag - em_pi_fast_lag: +0.021 [-0.043, +0.089]

Labelled calibration cost per run (149 windows, 1000 labelled shots per recalibration; these are readout calibration shots, not QEC shots): periodic_12h 27.0 recalibration(s) = 27000 labelled shots (12.1% of the QEC shots); periodic_24h 14.0 recalibration(s) = 14000 labelled shots (6.3% of the QEC shots); periodic_48h 7.0 recalibration(s) = 7000 labelled shots (3.1% of the QEC shots); oracle 149.0 recalibration(s) = 149000 labelled shots (66.7% of the QEC shots). Downtime per recalibration is not modelled; oracle recalibrates every window and is an upper bound, not deployable. Label-free arms need none.
gated arm alarm fraction over all windows: 0.08

### real_q2
REAL REPLAY: the IBM snapshots.

8 run(s); 149 windows per run, 1500 shots per window, d=5, physical error 0.001.

| arm | pooled LER [95% Wilson CI, counts shots only] | [95% CI resampling window blocks, one shared trajectory] | shots | mean accuracy | gap recovered, pooled [95% bootstrap CI over runs] | median per run [IQR] | runs >= 0.8 |
|---|---|---|---|---|---|---|---|
| frozen | 0.00034 [0.00031, 0.00036] | [0.00027, 0.00042] | 1788000 | 99.49% | - | - | - |
| periodic_12h | 0.00033 [0.00031, 0.00036] | [0.00027, 0.00041] | 1788000 | 99.50% | - | - | - |
| periodic_24h | 0.00033 [0.00031, 0.00036] | [0.00027, 0.00041] | 1788000 | 99.49% | - | - | - |
| periodic_48h | 0.00033 [0.00030, 0.00036] | [0.00026, 0.00041] | 1788000 | 99.50% | - | - | - |
| oracle | 0.00032 [0.00030, 0.00035] | [0.00026, 0.00040] | 1788000 | 99.50% | - | - | - |
| moment_v1 | 0.00271 [0.00264, 0.00279] | [0.00228, 0.00318] | 1788000 | 98.49% | - | - | - |
| em_pi | 0.00033 [0.00031, 0.00036] | [0.00027, 0.00041] | 1788000 | 99.50% | - | - | - |
| em_pi_fast | 0.00033 [0.00030, 0.00036] | [0.00026, 0.00041] | 1788000 | 99.50% | - | - | - |
| em_pi_fast_lag | 0.00034 [0.00031, 0.00036] | [0.00027, 0.00042] | 1788000 | 99.49% | - | - | - |
| gated_v5 | 0.00033 [0.00030, 0.00036] | [0.00026, 0.00041] | 1788000 | 99.50% | - | - | - |
| em_pi_lag | 0.00034 [0.00031, 0.00036] | [0.00027, 0.00042] | 1788000 | 99.49% | - | - | - |
| gated_v5_lag | 0.00034 [0.00031, 0.00036] | [0.00027, 0.00041] | 1788000 | 99.49% | - | - | - |

frozen-vs-oracle LER gap: 0.001 percentage points  (not distinguishable from zero, recovery fractions are not reported)

Real-data scenario: one 15.6-day trajectory replayed repeatedly (runs differ only in which unlabelled IQ points are drawn). The block-bootstrap interval describes uncertainty within this trajectory; it is not a set of independent real-world trajectories.

Paired LER differences (percentage points, 95% CI from the same resamples; negative = first arm better):
- em_pi_fast - frozen: -0.001 [-0.002, +0.000]
- em_pi_fast - oracle: +0.001 [+0.000, +0.001]
- gated_v5 - em_pi_fast: +0.000 [-0.001, +0.001]
- em_pi_fast_lag - em_pi_fast: +0.001 [-0.000, +0.002]
- periodic_24h - em_pi_fast: +0.001 [-0.000, +0.002]
- em_pi - em_pi_fast: +0.001 [-0.000, +0.002]
- gated_v5 - em_pi: -0.000 [-0.001, +0.000]
- gated_v5_lag - em_pi_fast_lag: -0.000 [-0.001, +0.000]
- gated_v5_lag - em_pi_lag: -0.000 [-0.000, +0.000]
- em_pi_lag - em_pi_fast_lag: -0.000 [-0.001, +0.000]

Labelled calibration cost per run (149 windows, 1000 labelled shots per recalibration; these are readout calibration shots, not QEC shots): periodic_12h 27.0 recalibration(s) = 27000 labelled shots (12.1% of the QEC shots); periodic_24h 14.0 recalibration(s) = 14000 labelled shots (6.3% of the QEC shots); periodic_48h 7.0 recalibration(s) = 7000 labelled shots (3.1% of the QEC shots); oracle 149.0 recalibration(s) = 149000 labelled shots (66.7% of the QEC shots). Downtime per recalibration is not modelled; oracle recalibrates every window and is an upper bound, not deployable. Label-free arms need none.
gated arm alarm fraction over all windows: 0.13

