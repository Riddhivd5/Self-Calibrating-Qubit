# Syndrome-guided readout adaptation: specification (as implemented in adaptive_boundary_v5.py and evaluated in ler_comparison.py)

Written in response to reviewer R1's request to specify the detection statistic, boundary-update rule, stability safeguards,
adaptation interval and hardware overhead. Every value below is taken from `adaptive_boundary_v5.py`.

## Detection statistic
- Feature: detector **fire rate** of a window (mean detection-event probability), from the QEC syndrome stream only.
  Round-to-round correlation is computed but cannot trigger an alarm.
- Window: 1500 QEC shots, d = 5 surface code, physical error 0.001.
- Reference: K_REF = 6 windows recorded immediately after the labelled t = 0 calibration, with the freshly calibrated boundary
  (windows take milliseconds), so drift during the run cannot contaminate it. Mean m and standard deviation s of those
  windows; s is floored at 1e-4 x m.
- Alarm: (fire - m) / s > 3.0 (ZTHR) and fire / m - 1 > 0.30 (REL_RISE), evaluated every window.
- Not used for alarming: round-to-round correlation and per-ancilla asymmetry. They attribute the cause (readout vs
  physical) and belong to the attribution work: the fire-rate alarm also rises on physical-only drift (gated-arm alarm
  fraction 0.30 in the physical-only scenario).

## Boundary representation
- Perpendicular bisector of the two centroids c0, c1 in the IQ plane (as in the FPGA discriminator).

## Update rule (EM+pi)
- Input: the step's unlabelled IQ points (1500 per update by default; 100 and 300 also tested).
- Model: two Gaussian clouds with a shared isotropic variance sig2 fixed from the labelled calibration; the |1> share pi is
  estimated once from the first stream by classifying it with the calibrated boundary (clipped to [0.02, 0.98]) and then held
  fixed.
- One EM step per update (`em_step`): soft assignment, then responsibility-weighted means.
- Applied step: c <- (1 - eta) c + eta c_EM. eta = 0.3 (fixed EM+pi), 0.9 (always fast), or for the gated arm eta_quiet = 0.3 and
  eta_alarm = 0.9 (tuned in v5 on q0 tuning seeds 0-2, grid eta_quiet in {0.1, 0.2, 0.3} x eta_alarm in {0.5, 0.9}).

## Stability safeguards
- A cloud's centroid is left unchanged if fewer than 10 points are softly assigned to it.
- pi clipped to [0.02, 0.98]; sig2 fixed from calibration (not re-estimated online).
- Detector reference fixed at calibration; an alarm needs both a z-score and a relative rise.
- Label isolation: v5's start-up test shows every adaptive centroid trajectory is identical after shuffling all evaluation and
  calibration labels, so the controller cannot be using labels.

## Adaptation interval and gating
- One update per step (4 h of simulated drift per step; in a real system an update would run every few windows, each window
  taking milliseconds).
- Always-fast arm: eta = 0.9 every step, no detector. Gated arm: eta switches between 0.3 and 0.9 on the alarm of the same step,
  evaluated on a window measured at the pre-update boundary. It never freezes.

## Baselines
- frozen: calibrated once on 20000 labelled shots. periodic: labelled recalibration (2000 labelled shots) every 12, 24 or 48 h.
  oracle: labelled recalibration at every step. plain moment re-centring (v1): midpoint set to the smoothed stream mean.

## Hardware overhead
- Not evaluated. The detector (fire-rate counter and comparison), the EM step and the centroid update have not been written in
  RTL or synthesised; no LUT/FF/DSP/BRAM or latency numbers exist yet.
