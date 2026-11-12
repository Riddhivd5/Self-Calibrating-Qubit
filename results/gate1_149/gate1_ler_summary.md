# Gate 1 LER under readout drift (physical error fixed at 0.001, 20000 shots/window, 95% Wilson CIs, fixed baseline decoder)

## Simulated drift: readout error 1.0% -> 2.5% over 10 windows

- d=3: LER first 0.0036 [0.0029, 0.0045] -> last 0.0133 [0.0118, 0.0150] (20000 shots per window); first-vs-last p = 3.1e-26; trend p = 1.6e-59 (rising)
  control (constant readout error): pooled LER 0.0031 [0.0029, 0.0034]; first-vs-last p = 0.78; trend p = 0.29; drift windows whose CI lies entirely above the control CI: 8 of 10

- d=5: LER first 0.0009 [0.0006, 0.0015] -> last 0.0056 [0.0047, 0.0068] (20000 shots per window); first-vs-last p = 2.5e-16; trend p = 2.2e-38 (rising)
  control (constant readout error): pooled LER 0.0008 [0.0007, 0.0009]; first-vs-last p = 0.72; trend p = 0.18; drift windows whose CI lies entirely above the control CI: 7 of 10

## Real IBM drift replay: 149 snapshots, 2026-09-11T08:58:08 to 2026-09-27T00:12:49 (375 h)

Acquisition schedule: gaps between consecutive snapshots, median 2.56 h, min 0.15 h, max 16.00 h; 22 gaps shorter than 1 h. One QEC window per snapshot, no interpolation.

Readout error per snapshot: IBM-reported mean 0.0116 to 0.0282; frozen-boundary misassignment on real IQ 0.0100 to 0.0573 (IQ points per state per snapshot: 1000).

- d=3, IBM-reported readout error (20000 shots per window): control pooled LER 0.0048 [0.0047, 0.0048]; 3 windows with the highest readout error (chosen without looking at LER; readout error 0.0265-0.0282): pooled LER 0.0155 [0.0145, 0.0165] vs control 0.0048, selection-aware permutation p = 0.0002 (random windows give 0.0074); rank correlation between window readout error and window LER +0.91, permutation p = 0.0002; windows whose CI lies entirely above the control CI: 90 of 149 (control windows above the control CI: 0 of 149); descriptive only, selected by max LER and biased upward: window at 53 h, LER 0.0170
  correlation between readout error and window LER: +0.98

- d=3, frozen-boundary error on real IQ (20000 shots per window): control pooled LER 0.0052 [0.0051, 0.0053]; 3 windows with the highest readout error (chosen without looking at LER; readout error 0.0352-0.0573): pooled LER 0.0387 [0.0372, 0.0403] vs control 0.0052, selection-aware permutation p = 0.0002 (random windows give 0.0074); rank correlation between window readout error and window LER +0.94, permutation p = 0.0002; windows whose CI lies entirely above the control CI: 73 of 149 (control windows above the control CI: 3 of 149); descriptive only, selected by max LER and biased upward: window at 49 h, LER 0.0549
  correlation between readout error and window LER: +0.97

- d=5, IBM-reported readout error (20000 shots per window): control pooled LER 0.0013 [0.0012, 0.0013]; 3 windows with the highest readout error (chosen without looking at LER; readout error 0.0265-0.0282): pooled LER 0.0071 [0.0065, 0.0078] vs control 0.0013, selection-aware permutation p = 0.0004 (random windows give 0.0026); rank correlation between window readout error and window LER +0.86, permutation p = 0.0002; windows whose CI lies entirely above the control CI: 78 of 149 (control windows above the control CI: 1 of 149); descriptive only, selected by max LER and biased upward: window at 53 h, LER 0.0080
  correlation between readout error and window LER: +0.96

- d=5, frozen-boundary error on real IQ (20000 shots per window): control pooled LER 0.0015 [0.0014, 0.0015]; 3 windows with the highest readout error (chosen without looking at LER; readout error 0.0352-0.0573): pooled LER 0.0285 [0.0272, 0.0298] vs control 0.0015, selection-aware permutation p = 0.0002 (random windows give 0.0028); rank correlation between window readout error and window LER +0.90, permutation p = 0.0002; windows whose CI lies entirely above the control CI: 63 of 149 (control windows above the control CI: 4 of 149); descriptive only, selected by max LER and biased upward: window at 49 h, LER 0.0461
  correlation between readout error and window LER: +0.92

