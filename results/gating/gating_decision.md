# Gating decision

Question: is there any condition in which gating the adaptation step size on the v5 syndrome alarm gives a lower logical error
rate than a fixed step size? Earlier results (results/gate2) found none, with 1500 unlabelled IQ points per update.

Every number below is in gating_summary.md (built by summarise_gating.py from the ler_summary.md files in the sub-folders).
8 independent runs per row, d = 5, physical error 0.001, 1500 QEC shots per window, q1 noise profile, online (one-step-lag)
scoring. Step sizes are the ones tuned earlier in v5 (0.3 quiet, 0.9 on alarm) and were not retuned.

## Answer

Yes, but only when an update uses few IQ points. Stated precisely:

1. With 1500 points per update, gating does not lower LER relative to always-fast adaptation: the paired difference is within
   +/-0.008 percentage points in all six conditions, and its interval includes zero in five of them (the exception is the quiet
   run with a changing |1> share, -0.008 [-0.014, -0.003], about 3% of that LER). This confirms the earlier finding.
2. With 150 points or fewer, always-fast adaptation follows the noise of its own centroid estimates when nothing has drifted.
   In the quiet run its LER is 0.281% (150 points), 0.300% (50) and 0.340% (20) against 0.273-0.275% for the gated policy, which
   stays at the slow step because the alarm is silent: gated - fast = -0.008 [-0.015, -0.002], -0.024 [-0.036, -0.011] and
   -0.067 [-0.160, -0.016] percentage points.
3. After a 1 sigma step, always-slow adaptation lags: gated - slow is between -0.131 and -0.313 percentage points at every batch
   size, every interval excluding zero. Gated matches always-fast there (intervals include zero, except -0.022 [-0.039, -0.002]
   for the changing-share step run at 150 points).
4. On the fitted q1 profile (jitter plus events), gated is better than always-fast at 50 points (-0.063 [-0.112, -0.012]) and
   better than always-slow at 1500 points (-0.042 [-0.070, -0.016]); it is not significantly worse than either in both cases.
5. Cost of the alarm not knowing the cause: under physical-only drift the alarm fires on 27-29% of windows and switches the gated
   policy to the fast step although the readout has not moved. The penalty against always-slow is +0.015 [+0.008, +0.022]
   percentage points at 50 points per update and +0.005 [+0.001, +0.009] at 20; none is measurable at 150 or 1500.

So the supported claim is: gating on the syndrome alarm matches the better of the two fixed step sizes, to within 0.015
percentage points of LER, in every condition tested;
it lowers LER relative to always-fast adaptation only when updates are small (150 IQ points or fewer), and relative to
always-slow adaptation whenever there is a step. With large updates the detector is a monitor, not an LER improvement.

## What this does not show

- No intermediate fixed step size (for example 0.6) was tested; one might do as well as gating at a given batch size.
- Whether an FPGA implementation would use small update batches is a hardware design question that has not been evaluated.
- One noise profile (q1), one code distance and physical error rate, 8 runs per condition, 22 conditions with no correction
  for multiple comparisons. The physical-drift penalty would need the attribution step to remove.
- The fitted q1 profile appears stronger than the real q1 data (see the detector scoring and LER notes), so row 4 is a
  simulation result, not a statement about the device.
