# Evidence sheet for the camera-ready paper (stream B: QEC, detector, adaptation)

Each line: the claim, the number with its interval, the conditions, the file it comes from, and the limit that must be stated
with it. All QEC results are Stim/PyMatching simulation of a rotated surface code (d = 5, physical error 0.001 unless stated)
with a fixed decoder built at the calibration-time readout error. "Real" means measured IBM IQ readout data (ibm_fez, q0-q2)
replayed through that simulation; no syndromes were measured on hardware.

## Dataset (answers Reviewer 3)
- 149 snapshots, 11 to 27 Sep 2026, span 375.2 h (15.6 days); 1000 shots per state per qubit per snapshot; gaps between
  snapshots median 2.56 h, minimum 0.15 h, maximum 16.0 h. Source: results/real149/real_event_checks.txt.
- Limit: the planned schedule (every 6 h for 12 weeks) was not met. Seven snapshot timestamps are job-submission times; five of
  those jobs ran 5.4 to 14.6 h later (queueing). One trajectory on one device.

## Readout drift degrades LER (Gate 1; answers "shot counts and confidence intervals")
- Simulated drift, readout error 1.0% to 2.5% over 10 windows, 20,000 shots per window: d = 3 LER 0.0036 [0.0029, 0.0045] to
  0.0133 [0.0118, 0.0150]; d = 5 0.0009 [0.0006, 0.0015] to 0.0056 [0.0047, 0.0068]; no-drift control flat (first-vs-last
  p = 0.78 and 0.72). Source: results/gate1_149/gate1_ler_summary.md.
- Real readout error, 149 windows of 20,000 shots, d = 3: the three windows with the highest frozen-boundary readout error
  (chosen without looking at LER) have LER 0.0387 [0.0372, 0.0403] against a control of 0.0052; selection-aware permutation
  p = 0.0002; rank correlation of window readout error with window LER +0.94. Same source.
- Limit: each window's LER is simulated from its measured readout error, so this shows that readout error drives LER with a
  fixed decoder, not a hardware LER measurement.

## Closed loop: frozen vs periodic vs oracle vs adaptive (the result all three reviewers asked for)
Source for every number: results/closed_loop/closed_loop_table.md (built from the ler_summary.md files beside it).
Figure: results/closed_loop/closed_loop_figure.pdf. LER in percent with 95% resampling intervals; recovery = share of the
frozen-to-oracle LER gap removed.
- Simulated 1 sigma step (8 runs x 43 windows x 1500 shots = 516,000 shots per arm): frozen 5.068 [4.968, 5.183], oracle
  0.270 [0.259, 0.281], adaptive scored on the window it was tuned on 0.285 [0.267, 0.306] (recovery 1.00 [0.99, 1.00]),
  adaptive online 0.438 [0.415, 0.460] (recovery 0.96 [0.96, 0.97]), periodic recalibration every 24 h 0.951 [0.916, 0.986]
  (recovery 0.86 [0.85, 0.87]).
- Simulated slow ramp to 1 sigma (same size): frozen 1.825 [1.775, 1.875], oracle 0.270, adaptive online 0.271 [0.260, 0.283]
  (recovery 1.00 [1.00, 1.00]).
- Real q1 replay (8 re-samplings x 149 windows x 1500 shots = 1,788,000 shots per arm): frozen 0.892 [0.514, 1.379], oracle
  0.663 [0.425, 0.963]; the frozen-to-oracle gap is 0.228 percentage points. Adaptive on the same window 0.667 (recovery
  0.99 [0.97, 1.00]); adaptive online 0.824 [0.519, 1.189] (recovery 0.30 [0.25, 0.32]); periodic 24 h 0.963 (recovery
  -0.31 [-0.35, -0.28], i.e. worse than frozen). Paired difference online minus same-window: +0.159 [+0.070, +0.256] points.
- Real q0 replay: frozen 0.498, oracle 0.428 (gap 0.070 points); adaptive online 0.442 (recovery 0.80 [0.75, 0.85]).
- Real q2 replay: frozen 0.034, oracle 0.032; the gap is not distinguishable from zero, so there is nothing to recover.
- Fitted q1 profile (8 runs x 169 windows x 1500 shots): frozen 1.764 [1.089, 2.392], oracle 0.995 [0.649, 1.324], adaptive
  same window recovery 0.91 [0.88, 0.94], online 0.52 [0.42, 0.57]. Fitted q0 and q2: no resolvable gap.
- What it supports: label-free adaptation removes nearly all of the LER lost to a persistent displacement (step or ramp), online
  as well as offline. On the real trajectory the loss comes from short events; an online controller recovers about a third of
  it on q1, and the oracle itself stays at 0.66% because most of the event error is not a boundary error.
- Limits: the "same window" figure is offline re-assignment, not a live controller; quote it only next to the online figure.
  Real-replay intervals cover sampling noise within one 15.6-day trajectory. The fitted q1 profile gives a larger frozen LER
  (1.76%) than the real replay (0.89%), so it is a secondary result. Periodic recalibration downtime is not modelled. One code
  distance and one physical error rate; adaptation step sizes were tuned earlier at these settings and not retuned.
- Pre-registered hypothesis E5 (cheap adaptation recovers more than 80% of the drift-induced LER increase on step and slow
  drift): met in simulation for both (online 0.96 and 1.00). Not met online on real q1 (0.30). Hardware cost not evaluated.

## Detector (answers "detection delay, false-positive and false-negative rates")
Source: results/detector_scoring/detector_scoring.md. Alarm = fire-rate z-score > 3 and relative rise > 30% against six
reference windows recorded after calibration; 20 independent calibrations x 40 windows per case.
- False positives: 0 of 800 healthy windows at each of 250, 500, 1000 and 1500 shots per window (95% upper bound 0.5%).
- Detection: a displacement of 0.35 cloud sigma or more (readout error 1.65x healthy) alarms on 800 of 800 windows; 0.25 sigma on
  0.55 to 0.62 of windows; 0.15 sigma on 0.00 to 0.06.
- Delay: for 0.35 sigma or more the first window after the step alarms, i.e. 250 shots = 1250 syndrome rounds at the smallest
  window tested.
- Not specific to readout: with no readout drift, a 3x rise in physical error alarms on 0.99 to 1.00 of windows, a 2x rise on
  0.03 to 0.14.
- Real snapshots (1500-shot windows, 8 re-samplings): where readout error rose less than 0.25 percentage points over the
  reference, alarms on 0 of 86 (q0), 0 of 1032 (q1), 3 of 1028 (q2) windows; every window with a rise over 1 point alarmed.
- Limits: simulation; q1 noise profile; thresholds not retuned per window size. On real data the reference rests on the first
  snapshot's 500 held-out IQ points per state, which makes the real-data behaviour reference-dependent.

## Attribution: readout drift vs physical drift (answers "classification accuracy", "isolate readout drift")
Source: results/attribution_heldout/attribution_heldout.md. Logistic regression on fire rate, round-to-round correlation and
per-ancilla asymmetry; classes matched in fire rate; trained on three drift kinds at +40/+100/+200% fire-rate rise, tested on
nine kinds at +30/+60/+150/+250%; 5400 test windows.
- All held-out conditions pooled: AUC 0.90 [0.89, 0.91], accuracy 0.88 (250- and 1500-shot windows agree: 0.903 and 0.898);
  chance band from shuffled test labels 0.48 to 0.52. Fire rate alone 0.51; correlation alone 0.86.
- Against data, gate, T1-style and dephasing noise: AUC 0.997 to 1.000 in every pairing, including kinds never seen in training.
- Limit that must be stated: against reset (state-preparation) errors AUC is 0.14 to 0.63; they leave the same syndrome
  signature as a misread and cannot be separated by these features. The pooled 0.90 depends on reset being one of six
  physical kinds. Simultaneous readout and physical drift was not tested. Simulation only.

## What the syndromes are used for (wording of "syndrome-guided")
- The boundary update itself is label-free and uses unlabelled IQ points (one EM step with a fixed |1> share). The syndrome
  stream supplies the alarm, the attribution, and the choice of step size.
- Gating the step size on the alarm lowers LER relative to always-fast adaptation only when an update uses 150 IQ points or
  fewer (nothing drifting: 0.275% against 0.300% at 50 points, difference -0.024 [-0.036, -0.011] points); at 1500 points per
  update the two are within 0.008 points. Source: results/gating/gating_summary.md, results/gating/gating_decision.md.

## Specification in brief (answers Reviewer 1; full text in SPEC.md)
- Detection statistic: mean detector fire rate per window; alarm when z-score > 3.0 and relative rise > 0.30 against six
  post-calibration reference windows.
- Update rule: one EM step on the window's unlabelled IQ points with a shared fixed variance and a fixed |1> share, then
  c <- (1 - eta) c + eta c_EM, eta = 0.3 (quiet) or 0.9 (alarm).
- Safeguards: a centroid is left unchanged if fewer than 10 points are softly assigned to it; the |1> share is clipped to
  [0.02, 0.98]; variance is fixed at calibration; the alarm needs both conditions.
- Adaptation interval: one update per window. Hardware overhead: not evaluated.

## Not available from this stream
- Any FPGA resource, latency or bit-exactness number for the detector or the adaptation.
- LER from syndromes measured on hardware.
- Results at other code distances or physical error rates for the closed loop.
