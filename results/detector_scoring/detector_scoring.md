# Detector scoring: v5 fire-rate alarm, truth defined by the injected drift

Alarm: z-score > 3.0 and relative rise > 0.3 against 6 reference windows recorded right after calibration (adaptive_boundary_v5.ControllerV5, unchanged; thresholds not retuned per window size or case). Frozen boundary throughout.

## Part A: controlled states
20 independent calibrations (seeds 300-319), 40 consecutive windows per case, qubit q1, d=5, physical error 0.001. One shot = 5 syndrome rounds. Intervals: 95% Wilson over all windows, and in brackets the range of the per-calibration alarm fraction (10th-90th percentile), because windows that share a reference are not independent.

### Window = 250 shots (1250 syndrome rounds)

| case | readout error (x healthy) | fire-rate rise | windows | alarm fraction [95% CI] (10th-90th pct over calibrations) | reads as | first alarm: median / 90th pct window | median delay in shots (syndrome rounds) | streams never alarmed |
|---|---|---|---|---|---|---|---|---|
| healthy | 0.0176 (1.02x) | +1.6% | 800 | 0.000 [0.000, 0.005] (0.00-0.00) | false-positive rate | - | - | 20/20 |
| readout 0.1 sigma | 0.0196 (1.14x) | +11.8% | 800 | 0.016 [0.010, 0.028] (0.00-0.00) | detection rate (1 - false-negative rate) | 1 / 1 | 250 (1250) | 19/20 |
| readout 0.15 sigma | 0.0209 (1.21x) | +18.1% | 800 | 0.055 [0.041, 0.073] (0.00-0.08) | detection rate (1 - false-negative rate) | 4 / 16 | 1000 (5000) | 15/20 |
| readout 0.25 sigma | 0.0240 (1.39x) | +33.0% | 800 | 0.621 [0.587, 0.654] (0.17-0.98) | detection rate (1 - false-negative rate) | 1 / 3 | 250 (1250) | 0/20 |
| readout 0.35 sigma | 0.0286 (1.66x) | +53.7% | 800 | 1.000 [0.995, 1.000] (1.00-1.00) | detection rate (1 - false-negative rate) | 1 / 1 | 250 (1250) | 0/20 |
| readout 0.5 sigma | 0.0371 (2.15x) | +90.9% | 800 | 1.000 [0.995, 1.000] (1.00-1.00) | detection rate (1 - false-negative rate) | 1 / 1 | 250 (1250) | 0/20 |
| readout 1 sigma | 0.0886 (5.14x) | +293.1% | 800 | 1.000 [0.995, 1.000] (1.00-1.00) | detection rate (1 - false-negative rate) | 1 / 1 | 250 (1250) | 0/20 |
| physical x1.5 | 0.0176 (1.02x) | +12.4% | 800 | 0.014 [0.008, 0.024] (0.00-0.00) | alarm without readout drift | 3 / 3 | 750 (3750) | 19/20 |
| physical x2 | 0.0177 (1.02x) | +23.3% | 800 | 0.136 [0.114, 0.162] (0.00-0.33) | alarm without readout drift | 1 / 17 | 250 (1250) | 9/20 |
| physical x3 | 0.0177 (1.02x) | +44.1% | 800 | 0.990 [0.980, 0.995] (0.97-1.00) | alarm without readout drift | 1 / 1 | 250 (1250) | 0/20 |
| combined 0.5 sigma, x1.5 | 0.0368 (2.13x) | +100.0% | 800 | 1.000 [0.995, 1.000] (1.00-1.00) | detection rate (1 - false-negative rate) | 1 / 1 | 250 (1250) | 0/20 |
| combined 1 sigma, x2 | 0.0876 (5.08x) | +306.0% | 800 | 1.000 [0.995, 1.000] (1.00-1.00) | detection rate (1 - false-negative rate) | 1 / 1 | 250 (1250) | 0/20 |

### Window = 500 shots (2500 syndrome rounds)

| case | readout error (x healthy) | fire-rate rise | windows | alarm fraction [95% CI] (10th-90th pct over calibrations) | reads as | first alarm: median / 90th pct window | median delay in shots (syndrome rounds) | streams never alarmed |
|---|---|---|---|---|---|---|---|---|
| healthy | 0.0176 (1.01x) | +1.1% | 800 | 0.000 [0.000, 0.005] (0.00-0.00) | false-positive rate | - | - | 20/20 |
| readout 0.1 sigma | 0.0196 (1.12x) | +10.9% | 800 | 0.000 [0.000, 0.005] (0.00-0.00) | detection rate (1 - false-negative rate) | - | - | 20/20 |
| readout 0.15 sigma | 0.0209 (1.20x) | +17.2% | 800 | 0.015 [0.009, 0.026] (0.00-0.03) | detection rate (1 - false-negative rate) | 14 / 29 | 7000 (35000) | 17/20 |
| readout 0.25 sigma | 0.0241 (1.38x) | +31.9% | 800 | 0.598 [0.563, 0.631] (0.19-1.00) | detection rate (1 - false-negative rate) | 1 / 2 | 500 (2500) | 1/20 |
| readout 0.35 sigma | 0.0287 (1.65x) | +52.9% | 800 | 1.000 [0.995, 1.000] (1.00-1.00) | detection rate (1 - false-negative rate) | 1 / 1 | 500 (2500) | 0/20 |
| readout 0.5 sigma | 0.0371 (2.13x) | +89.6% | 800 | 1.000 [0.995, 1.000] (1.00-1.00) | detection rate (1 - false-negative rate) | 1 / 1 | 500 (2500) | 0/20 |
| readout 1 sigma | 0.0887 (5.10x) | +290.5% | 800 | 1.000 [0.995, 1.000] (1.00-1.00) | detection rate (1 - false-negative rate) | 1 / 1 | 500 (2500) | 0/20 |
| physical x1.5 | 0.0176 (1.01x) | +11.8% | 800 | 0.001 [0.000, 0.007] (0.00-0.00) | alarm without readout drift | 11 / 11 | 5500 (27500) | 19/20 |
| physical x2 | 0.0176 (1.01x) | +22.1% | 800 | 0.071 [0.055, 0.091] (0.00-0.14) | alarm without readout drift | 4 / 33 | 2000 (10000) | 11/20 |
| physical x3 | 0.0177 (1.02x) | +42.9% | 800 | 0.994 [0.985, 0.997] (0.97-1.00) | alarm without readout drift | 1 / 1 | 500 (2500) | 0/20 |
| combined 0.5 sigma, x1.5 | 0.0369 (2.12x) | +98.7% | 800 | 1.000 [0.995, 1.000] (1.00-1.00) | detection rate (1 - false-negative rate) | 1 / 1 | 500 (2500) | 0/20 |
| combined 1 sigma, x2 | 0.0877 (5.04x) | +302.9% | 800 | 1.000 [0.995, 1.000] (1.00-1.00) | detection rate (1 - false-negative rate) | 1 / 1 | 500 (2500) | 0/20 |

### Window = 1000 shots (5000 syndrome rounds)

| case | readout error (x healthy) | fire-rate rise | windows | alarm fraction [95% CI] (10th-90th pct over calibrations) | reads as | first alarm: median / 90th pct window | median delay in shots (syndrome rounds) | streams never alarmed |
|---|---|---|---|---|---|---|---|---|
| healthy | 0.0176 (1.01x) | +1.0% | 800 | 0.000 [0.000, 0.005] (0.00-0.00) | false-positive rate | - | - | 20/20 |
| readout 0.1 sigma | 0.0196 (1.12x) | +10.8% | 800 | 0.000 [0.000, 0.005] (0.00-0.00) | detection rate (1 - false-negative rate) | - | - | 20/20 |
| readout 0.15 sigma | 0.0209 (1.20x) | +17.2% | 800 | 0.004 [0.001, 0.011] (0.00-0.00) | detection rate (1 - false-negative rate) | 3 / 5 | 3000 (15000) | 18/20 |
| readout 0.25 sigma | 0.0240 (1.38x) | +31.8% | 800 | 0.593 [0.558, 0.626] (0.02-1.00) | detection rate (1 - false-negative rate) | 1 / 7 | 1000 (5000) | 2/20 |
| readout 0.35 sigma | 0.0287 (1.65x) | +52.7% | 800 | 1.000 [0.995, 1.000] (1.00-1.00) | detection rate (1 - false-negative rate) | 1 / 1 | 1000 (5000) | 0/20 |
| readout 0.5 sigma | 0.0371 (2.13x) | +89.3% | 800 | 1.000 [0.995, 1.000] (1.00-1.00) | detection rate (1 - false-negative rate) | 1 / 1 | 1000 (5000) | 0/20 |
| readout 1 sigma | 0.0887 (5.10x) | +290.0% | 800 | 1.000 [0.995, 1.000] (1.00-1.00) | detection rate (1 - false-negative rate) | 1 / 1 | 1000 (5000) | 0/20 |
| physical x1.5 | 0.0176 (1.01x) | +11.6% | 800 | 0.000 [0.000, 0.005] (0.00-0.00) | alarm without readout drift | - | - | 20/20 |
| physical x2 | 0.0176 (1.01x) | +22.2% | 800 | 0.039 [0.027, 0.054] (0.00-0.01) | alarm without readout drift | 8 / 14 | 8500 (42500) | 18/20 |
| physical x3 | 0.0177 (1.01x) | +42.6% | 800 | 1.000 [0.995, 1.000] (1.00-1.00) | alarm without readout drift | 1 / 1 | 1000 (5000) | 0/20 |
| combined 0.5 sigma, x1.5 | 0.0369 (2.12x) | +98.5% | 800 | 1.000 [0.995, 1.000] (1.00-1.00) | detection rate (1 - false-negative rate) | 1 / 1 | 1000 (5000) | 0/20 |
| combined 1 sigma, x2 | 0.0876 (5.04x) | +302.4% | 800 | 1.000 [0.995, 1.000] (1.00-1.00) | detection rate (1 - false-negative rate) | 1 / 1 | 1000 (5000) | 0/20 |

### Window = 1500 shots (7500 syndrome rounds)

| case | readout error (x healthy) | fire-rate rise | windows | alarm fraction [95% CI] (10th-90th pct over calibrations) | reads as | first alarm: median / 90th pct window | median delay in shots (syndrome rounds) | streams never alarmed |
|---|---|---|---|---|---|---|---|---|
| healthy | 0.0176 (1.01x) | +0.6% | 800 | 0.000 [0.000, 0.005] (0.00-0.00) | false-positive rate | - | - | 20/20 |
| readout 0.1 sigma | 0.0196 (1.12x) | +10.6% | 800 | 0.000 [0.000, 0.005] (0.00-0.00) | detection rate (1 - false-negative rate) | - | - | 20/20 |
| readout 0.15 sigma | 0.0209 (1.20x) | +16.8% | 800 | 0.000 [0.000, 0.005] (0.00-0.00) | detection rate (1 - false-negative rate) | - | - | 20/20 |
| readout 0.25 sigma | 0.0240 (1.38x) | +31.3% | 800 | 0.551 [0.517, 0.585] (0.11-1.00) | detection rate (1 - false-negative rate) | 1 / 6 | 1500 (7500) | 2/20 |
| readout 0.35 sigma | 0.0287 (1.65x) | +52.3% | 800 | 1.000 [0.995, 1.000] (1.00-1.00) | detection rate (1 - false-negative rate) | 1 / 1 | 1500 (7500) | 0/20 |
| readout 0.5 sigma | 0.0371 (2.13x) | +88.8% | 800 | 1.000 [0.995, 1.000] (1.00-1.00) | detection rate (1 - false-negative rate) | 1 / 1 | 1500 (7500) | 0/20 |
| readout 1 sigma | 0.0887 (5.09x) | +289.0% | 800 | 1.000 [0.995, 1.000] (1.00-1.00) | detection rate (1 - false-negative rate) | 1 / 1 | 1500 (7500) | 0/20 |
| physical x1.5 | 0.0176 (1.01x) | +11.3% | 800 | 0.000 [0.000, 0.005] (0.00-0.00) | alarm without readout drift | - | - | 20/20 |
| physical x2 | 0.0176 (1.01x) | +21.7% | 800 | 0.033 [0.022, 0.047] (0.00-0.01) | alarm without readout drift | 2 / 4 | 3750 (18750) | 18/20 |
| physical x3 | 0.0177 (1.02x) | +42.5% | 800 | 1.000 [0.995, 1.000] (1.00-1.00) | alarm without readout drift | 1 / 1 | 1500 (7500) | 0/20 |
| combined 0.5 sigma, x1.5 | 0.0369 (2.12x) | +97.9% | 800 | 1.000 [0.995, 1.000] (1.00-1.00) | detection rate (1 - false-negative rate) | 1 / 1 | 1500 (7500) | 0/20 |
| combined 1 sigma, x2 | 0.0876 (5.03x) | +301.4% | 800 | 1.000 [0.995, 1.000] (1.00-1.00) | detection rate (1 - false-negative rate) | 1 / 1 | 1500 (7500) | 0/20 |

## Part B: trajectories, window = 1500 shots, every window scored

Reference readout error per trajectory is the mean flip rate of its own reference windows. On real data those windows draw on the first snapshot's 500 held-out IQ points per state, so the real reference carries visible sampling noise.

### Fitted profile q0 (8 trajectories of 336 h at 2 h steps, events on; 1352 windows, 24 with a generator event active; reference readout error 1.94%, alarms on 28 windows)

| true rise in readout error over the reference (percentage points) | windows | alarm fraction [95% CI] |
|---|---|---|
| under 0.25 | 1090 | 0.000 [0.000, 0.004] |
| 0.25 to 0.5 | 200 | 0.000 [0.000, 0.019] |
| 0.5 to 0.75 | 36 | 0.056 [0.015, 0.181] |
| 0.75 to 1 | 2 | 1.000 [0.342, 1.000] |
| 1 to 2 | 0 | - |
| over 2 | 24 | 1.000 [0.862, 1.000] |
| generator event active | 24 | 1.000 [0.862, 1.000] |
| no event active | 1328 | 0.003 [0.001, 0.008] |

### Fitted profile q1 (8 trajectories of 336 h at 2 h steps, events on; 1352 windows, 68 with a generator event active; reference readout error 1.69%, alarms on 390 windows)

| true rise in readout error over the reference (percentage points) | windows | alarm fraction [95% CI] |
|---|---|---|
| under 0.25 | 638 | 0.000 [0.000, 0.006] |
| 0.25 to 0.5 | 212 | 0.000 [0.000, 0.018] |
| 0.5 to 0.75 | 140 | 0.229 [0.167, 0.305] |
| 0.75 to 1 | 124 | 0.968 [0.920, 0.987] |
| 1 to 2 | 156 | 1.000 [0.976, 1.000] |
| over 2 | 82 | 1.000 [0.955, 1.000] |
| generator event active | 68 | 0.985 [0.921, 0.997] |
| no event active | 1284 | 0.252 [0.229, 0.276] |

### Fitted profile q2 (8 trajectories of 336 h at 2 h steps, events on; 1352 windows, 0 with a generator event active; reference readout error 0.26%, alarms on 9 windows)

| true rise in readout error over the reference (percentage points) | windows | alarm fraction [95% CI] |
|---|---|---|
| under 0.25 | 1351 | 0.006 [0.003, 0.012] |
| 0.25 to 0.5 | 1 | 1.000 [0.207, 1.000] |
| 0.5 to 0.75 | 0 | - |
| 0.75 to 1 | 0 | - |
| 1 to 2 | 0 | - |
| over 2 | 0 | - |
| generator event active | 0 | - |
| no event active | 1352 | 0.007 [0.004, 0.013] |

### Real IBM snapshots q0 (149 snapshots x 8 repetitions = 1192 windows; repetitions re-draw the QEC shots over the SAME 15.6-day trajectory, so the intervals describe sampling noise only, not other devices or periods; reference readout error 0.96%, alarms on 1045 windows)

| true rise in readout error over the reference (percentage points) | windows | alarm fraction [95% CI] |
|---|---|---|
| under 0.25 | 86 | 0.000 [0.000, 0.043] |
| 0.25 to 0.5 | 93 | 0.355 [0.265, 0.456] |
| 0.5 to 0.75 | 194 | 0.995 [0.971, 0.999] |
| 0.75 to 1 | 295 | 1.000 [0.987, 1.000] |
| 1 to 2 | 454 | 1.000 [0.992, 1.000] |
| over 2 | 70 | 1.000 [0.948, 1.000] |

### Real IBM snapshots q1 (149 snapshots x 8 repetitions = 1192 windows; repetitions re-draw the QEC shots over the SAME 15.6-day trajectory, so the intervals describe sampling noise only, not other devices or periods; reference readout error 2.56%, alarms on 123 windows)

| true rise in readout error over the reference (percentage points) | windows | alarm fraction [95% CI] |
|---|---|---|
| under 0.25 | 1032 | 0.000 [0.000, 0.004] |
| 0.25 to 0.5 | 16 | 0.000 [0.000, 0.194] |
| 0.5 to 0.75 | 8 | 0.000 [0.000, 0.324] |
| 0.75 to 1 | 14 | 0.071 [0.013, 0.315] |
| 1 to 2 | 42 | 1.000 [0.916, 1.000] |
| over 2 | 80 | 1.000 [0.954, 1.000] |

### Real IBM snapshots q2 (149 snapshots x 8 repetitions = 1192 windows; repetitions re-draw the QEC shots over the SAME 15.6-day trajectory, so the intervals describe sampling noise only, not other devices or periods; reference readout error 0.38%, alarms on 146 windows)

| true rise in readout error over the reference (percentage points) | windows | alarm fraction [95% CI] |
|---|---|---|
| under 0.25 | 1028 | 0.003 [0.001, 0.009] |
| 0.25 to 0.5 | 125 | 0.832 [0.757, 0.887] |
| 0.5 to 0.75 | 23 | 1.000 [0.857, 1.000] |
| 0.75 to 1 | 16 | 1.000 [0.806, 1.000] |
| 1 to 2 | 0 | - |
| over 2 | 0 | - |

