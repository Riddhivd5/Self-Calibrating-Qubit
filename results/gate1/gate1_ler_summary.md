# Gate 1 LER under readout drift (physical error fixed at 0.001, 20000 shots/window, 95% Wilson CIs, fixed baseline decoder)

## Simulated drift: readout error 1.0% -> 2.5% over 10 windows

- d=3: LER first 0.0036 [0.0029, 0.0045] -> last 0.0133 [0.0118, 0.0150] (20000 shots per window); first-vs-last p = 3.1e-26; trend p = 1.6e-59 (rising)
  control (constant readout error): pooled LER 0.0031 [0.0029, 0.0034]; first-vs-last p = 0.78; trend p = 0.29; drift windows whose CI lies entirely above the control CI: 8 of 10

- d=5: LER first 0.0009 [0.0006, 0.0015] -> last 0.0056 [0.0047, 0.0068] (20000 shots per window); first-vs-last p = 2.5e-16; trend p = 2.2e-38 (rising)
  control (constant readout error): pooled LER 0.0008 [0.0007, 0.0009]; first-vs-last p = 0.72; trend p = 0.18; drift windows whose CI lies entirely above the control CI: 7 of 10

## Real IBM drift replay: 68 snapshots, 2026-09-11T08:58:08 to 2026-09-21T05:30:08 (237 h)

Acquisition schedule: gaps between consecutive snapshots, median 2.71 h, min 0.53 h, max 16.00 h; 1 gaps shorter than 1 h. One QEC window per snapshot, no interpolation.

Readout error per snapshot: IBM-reported mean 0.0116 to 0.0282; frozen-boundary misassignment on real IQ 0.0100 to 0.0573 (IQ points per state per snapshot: 1000).

- d=3, IBM-reported readout error (20000 shots per window): control pooled LER 0.0044 [0.0043, 0.0046]; windows whose CI lies entirely above the control CI: 50 of 68; peak window at 53 h: LER 0.0170 [0.0153, 0.0189] (readout error 0.0282), 3.8x the control; control windows above the control CI: 3 of 68
  correlation between readout error and window LER: +0.94

- d=3, frozen-boundary error on real IQ (20000 shots per window): control pooled LER 0.0050 [0.0048, 0.0051]; windows whose CI lies entirely above the control CI: 37 of 68; peak window at 49 h: LER 0.0549 [0.0518, 0.0581] (readout error 0.0573), 11.1x the control; control windows above the control CI: 2 of 68
  correlation between readout error and window LER: +0.98

- d=5, IBM-reported readout error (20000 shots per window): control pooled LER 0.0012 [0.0011, 0.0012]; windows whose CI lies entirely above the control CI: 42 of 68; peak window at 53 h: LER 0.0081 [0.0069, 0.0094] (readout error 0.0282), 6.9x the control; control windows above the control CI: 1 of 68
  correlation between readout error and window LER: +0.89

- d=5, frozen-boundary error on real IQ (20000 shots per window): control pooled LER 0.0014 [0.0013, 0.0014]; windows whose CI lies entirely above the control CI: 29 of 68; peak window at 49 h: LER 0.0463 [0.0435, 0.0493] (readout error 0.0573), 34.2x the control; control windows above the control CI: 0 of 68
  correlation between readout error and window LER: +0.95

