# Gate 2 reviewer fixes: closed-loop logical error rate of decision-boundary policies, built on adaptive_boundary_v5.py

Produced by `ler_comparison.py`, which imports v5 unchanged: its hardware physics (true Stim outcomes read through the deployed
boundary with real IQ dots, asymmetric state-conditional misreads), the ControllerV5 fire-rate alarm (reference recorded right
after calibration, ZTHR 3.0, REL_RISE 0.30, K_REF 6), `em_step`, the fixed pi taken from the first stream, and the step sizes
tuned in v5 (eta quiet 0.3, eta alarm 0.9, read from `adaptive_boundary_v5.csv`). d=5, physical error 0.001, 1500 shots per
window (v5 settings). Added for the reviewers: logical error rate decoded from the same syndromes with a fixed baseline
PyMatching decoder, 95% Wilson intervals, an oracle arm, a periodic sweep (12/24/48 h), 8 held-out drift trajectories
(seeds 200-207, as in v5) with bootstrap intervals over trajectories, and readout-only / physical-only / combined drift.
stim 1.16.0, pymatching 2.4.0.

"Gap recovered" = (LER_frozen - LER_arm) / (LER_frozen - LER_oracle), pooled over runs, with a 95% bootstrap interval over runs; "median per
run" is v5's own statistic. It is not reported when the frozen-vs-oracle gap is not distinguishable from zero.

## What the numbers show
1. **EM+pi works without labels and matches v5's own readout-level result at the logical level.** Simulated q1 (drift x4,
   30% |1> stream): always-fast 0.99 [0.98, 0.99], v5-gated 0.98 [0.96, 0.99], EM+pi at fixed eta 0.3 0.86 [0.81, 0.91]; frozen
   LER 14.1%, oracle 0.46%. q0: fast 0.94 [0.90, 0.98], gated 0.94 [0.90, 0.97].
2. **The detector does not add recovery beyond adapting fast.** Gated and always-fast are within about 0.01 of each other in
   every simulated scenario, and gated is lower on real q1 (0.92 vs 1.00). The detector's demonstrated value is as an alarm.
3. **Periodic recalibration depends on its interval.** Simulated q1: 12 h 0.86 [0.78, 0.91], 24 h 0.65 [0.48, 0.76],
   48 h 0.32 [0.06, 0.50]. On real q1, 24 h recovers about nothing (-0.01 [-0.06, 0.04]).
4. **Plain moment re-centring (v1) breaks when the stream is not 50% |1>.** 10% |1>: -1.59 [-2.83, -0.98]; real q0 and q1 LER
   rise to 3.1% and 4.2% from 0.57% and 0.99% frozen. At 50% |1> it works (0.86).
5. **Physical-only drift:** adaptation does no harm (LER 0.576% always-fast, 0.573% gated, vs 0.571% frozen, intervals overlap),
   but the fire-rate alarm raises the gated arm's alarm fraction to 0.30 with no readout drift. A fire-rate-only alarm cannot
   attribute the cause; that is the job of the correlation / asymmetry features in the attribution work.
6. **Combined drift:** always-fast 0.99, gated 0.98.
7. **Small update batches:** 100 unlabelled IQ points per update: always-fast 0.98 [0.97, 0.99], gated 0.97 [0.95, 0.99];
   300 points: 0.99 / 0.98; default 1500 points: 0.99 / 0.98.
8. **Detector (v5 alarm, per window of 1500 shots), frozen boundary:** simulated q1 39/39 onsets caught within 12 h, 190/190
   event windows alarmed, 0/37 quiet windows alarmed; q0 21/21, 238/238, 0/20; q2 5/5, 8/8 but 68/272 quiet windows alarmed
   (q2's readout error is tiny, so the relative-rise test fires on very small absolute changes; the LER gap there is 0.007
   pp, so this is harmless). Real IBM snapshots: q0 116/116 onsets and 0/38 false alarms; q1 16/16 and 0/448; q2 16/16 and 0/386.
9. **Real IBM data (68 snapshots, 237 h, held-out scoring):** frozen-vs-oracle gap 0.09 pp (q0), 0.28 pp (q1), none for q2.
   Always-fast recovers 0.92 [0.87, 0.96] (q0) and 1.00 [0.99, 1.02] (q1); v5-gated 0.92 [0.88, 0.96] and 0.92 [0.90, 0.94].

## Limitations (please read before quoting)
- The harness is mine; the physics, alarm, EM+pi step and step sizes are v5's. Timeline per step: the boundary is updated from
  the step's unlabelled stream (the gated arm first measures one alarm window at its old boundary), then a window is measured
  at the updated boundary and decoded.
- Simulated results use 8 held-out drift trajectories. The real-data intervals come from 8 resamplings of the unlabelled
  stream over the same real trajectory, so they reflect resampling only, not uncertainty about the drift itself.
- Physical error is 0.001, far below threshold, so the near-threshold regime in hypothesis E2 is not covered. Drift is strong
  (frozen LER 14% on q1), so absolute LER values are large.
- Stream |1> share is fixed per run (10%, 30%, 50%) and pi is estimated once from the first stream, as in v5; a share that
  changes during the run is not tested.
- Step sizes were tuned in v5 on q0 tuning seeds and not retuned here.
- Detection delay is below the window resolution (one window is 4 h in simulation and one snapshot in the real data); delay
  inside a window is not measured.
- d=5 only here (Gate 1 covers d=3 and d=5). No hardware overhead or FPGA validation.
- Real IQ: 1000 shots per state per snapshot; scoring uses a held-out half (about 0.4-0.5% standard error on misassignment per
  window); initial calibration uses the first three snapshots.

## Reproduce (from the repo root, about 10 minutes in total)
```
python ler_comparison.py --scenarios readout_q1 readout_q0 readout_q2 --seeds 8 --out-dir results/gate2/run1
python ler_comparison.py --scenarios mix10 mix50 physical --seeds 8 --out-dir results/gate2/run2
python ler_comparison.py --scenarios both real_q0 real_q1 real_q2 --seeds 8 --out-dir results/gate2/run3
python ler_comparison.py --scenarios batch100 batch300 --batch-sizes 100 300 --seeds 8 --no-detector --out-dir results/gate2/run4
```
The files in this folder are these four runs merged. mix10 / mix50 are the q1 x4 drift with a 10% / 50% |1> stream
(the 30% case is readout_q1).


### readout_q1
8 run(s); 43 windows per run, 1500 shots per window, d=5, physical error 0.001.

| arm | pooled LER [95% CI] | shots | mean accuracy | gap recovered, pooled [95% bootstrap CI over runs] | median per run [IQR] | runs >= 0.8 |
|---|---|---|---|---|---|---|
| frozen | 0.14084 [0.13989, 0.14179] | 516000 | 91.42% | - | - | - |
| periodic_12h | 0.02313 [0.02272, 0.02354] | 516000 | 96.63% | +0.86 [+0.78, +0.91] | +0.87 [+0.78, +0.90] | 0.75 (8) |
| periodic_24h | 0.05179 [0.05119, 0.05240] | 516000 | 95.35% | +0.65 [+0.48, +0.76] | +0.68 [+0.49, +0.78] | 0.25 (8) |
| periodic_48h | 0.09657 [0.09577, 0.09738] | 516000 | 93.30% | +0.32 [+0.05, +0.50] | +0.42 [+0.13, +0.50] | 0.00 (8) |
| oracle | 0.00462 [0.00444, 0.00481] | 516000 | 97.80% | +1.00 [+1.00, +1.00] | +1.00 [+1.00, +1.00] | 1.00 (8) |
| moment_v1 | 0.11696 [0.11609, 0.11784] | 516000 | 92.85% | +0.18 [-0.14, +0.35] | +0.09 [-0.21, +0.31] | 0.00 (8) |
| em_pi | 0.02327 [0.02286, 0.02368] | 516000 | 96.48% | +0.86 [+0.81, +0.91] | +0.86 [+0.81, +0.89] | 0.75 (8) |
| em_pi_fast | 0.00633 [0.00612, 0.00655] | 516000 | 97.59% | +0.99 [+0.98, +0.99] | +0.99 [+0.97, +0.99] | 1.00 (8) |
| gated_v5 | 0.00741 [0.00718, 0.00765] | 516000 | 97.42% | +0.98 [+0.96, +0.99] | +0.98 [+0.97, +0.99] | 1.00 (8) |

frozen-vs-oracle LER gap: 13.622 percentage points
detector (v5 alarm on the frozen boundary, per window of 1500 shots): onsets caught within 12 h 39/39; event windows alarmed 190/190; false alarms on quiet windows 0/37; delay median 0 window(s) (one window = 4 h in simulation, one snapshot in real data; delay inside a window is not resolved)
gated arm alarm fraction over all windows: 0.48

### readout_q0
8 run(s); 43 windows per run, 1500 shots per window, d=5, physical error 0.001.

| arm | pooled LER [95% CI] | shots | mean accuracy | gap recovered, pooled [95% bootstrap CI over runs] | median per run [IQR] | runs >= 0.8 |
|---|---|---|---|---|---|---|
| frozen | 0.12851 [0.12760, 0.12943] | 516000 | 92.02% | - | - | - |
| periodic_12h | 0.06054 [0.05989, 0.06119] | 516000 | 94.58% | +0.81 [+0.66, +0.90] | +0.76 [+0.63, +0.89] | 0.50 (8) |
| periodic_24h | 0.07856 [0.07783, 0.07930] | 516000 | 93.85% | +0.59 [+0.38, +0.74] | +0.49 [+0.27, +0.75] | 0.12 (8) |
| periodic_48h | 0.10747 [0.10663, 0.10832] | 516000 | 92.43% | +0.25 [-0.03, +0.46] | +0.20 [-0.02, +0.34] | 0.00 (8) |
| oracle | 0.04415 [0.04359, 0.04471] | 516000 | 95.34% | +1.00 [+1.00, +1.00] | +1.00 [+1.00, +1.00] | 1.00 (8) |
| moment_v1 | 0.15437 [0.15339, 0.15536] | 516000 | 91.46% | -0.31 [-0.93, +0.01] | -0.31 [-1.34, -0.04] | 0.00 (8) |
| em_pi | 0.06664 [0.06596, 0.06732] | 516000 | 94.33% | +0.73 [+0.57, +0.86] | +0.68 [+0.56, +0.87] | 0.38 (8) |
| em_pi_fast | 0.04895 [0.04836, 0.04954] | 516000 | 95.12% | +0.94 [+0.90, +0.98] | +0.96 [+0.90, +0.98] | 1.00 (8) |
| gated_v5 | 0.04922 [0.04863, 0.04981] | 516000 | 95.07% | +0.94 [+0.90, +0.97] | +0.95 [+0.87, +0.97] | 1.00 (8) |

frozen-vs-oracle LER gap: 8.437 percentage points
detector (v5 alarm on the frozen boundary, per window of 1500 shots): onsets caught within 12 h 21/21; event windows alarmed 238/238; false alarms on quiet windows 0/20; delay median 0 window(s) (one window = 4 h in simulation, one snapshot in real data; delay inside a window is not resolved)
gated arm alarm fraction over all windows: 0.74

### readout_q2
8 run(s); 43 windows per run, 1500 shots per window, d=5, physical error 0.001.

| arm | pooled LER [95% CI] | shots | mean accuracy | gap recovered, pooled [95% bootstrap CI over runs] | median per run [IQR] | runs >= 0.8 |
|---|---|---|---|---|---|---|
| frozen | 0.00020 [0.00017, 0.00025] | 516000 | 99.75% | - | - | - |
| periodic_12h | 0.00013 [0.00011, 0.00017] | 516000 | 99.84% | - | - | - |
| periodic_24h | 0.00014 [0.00011, 0.00018] | 516000 | 99.82% | - | - | - |
| periodic_48h | 0.00019 [0.00015, 0.00023] | 516000 | 99.76% | - | - | - |
| oracle | 0.00013 [0.00010, 0.00016] | 516000 | 99.87% | - | - | - |
| moment_v1 | 0.00741 [0.00718, 0.00765] | 516000 | 98.28% | - | - | - |
| em_pi | 0.00012 [0.00010, 0.00016] | 516000 | 99.85% | - | - | - |
| em_pi_fast | 0.00013 [0.00010, 0.00016] | 516000 | 99.87% | - | - | - |
| gated_v5 | 0.00012 [0.00009, 0.00015] | 516000 | 99.85% | - | - | - |

frozen-vs-oracle LER gap: 0.007 percentage points  (not distinguishable from zero, recovery fractions are not reported)
detector (v5 alarm on the frozen boundary, per window of 1500 shots): onsets caught within 12 h 5/5; event windows alarmed 8/8; false alarms on quiet windows 68/272; delay median 0 window(s) (one window = 4 h in simulation, one snapshot in real data; delay inside a window is not resolved)
gated arm alarm fraction over all windows: 0.07


### mix10
8 run(s); 43 windows per run, 1500 shots per window, d=5, physical error 0.001.

| arm | pooled LER [95% CI] | shots | mean accuracy | gap recovered, pooled [95% bootstrap CI over runs] | median per run [IQR] | runs >= 0.8 |
|---|---|---|---|---|---|---|
| frozen | 0.14084 [0.13989, 0.14179] | 516000 | 91.42% | - | - | - |
| periodic_12h | 0.02313 [0.02272, 0.02354] | 516000 | 96.63% | +0.86 [+0.78, +0.91] | +0.87 [+0.78, +0.90] | 0.75 (8) |
| periodic_24h | 0.05179 [0.05119, 0.05240] | 516000 | 95.35% | +0.65 [+0.48, +0.76] | +0.68 [+0.49, +0.78] | 0.25 (8) |
| periodic_48h | 0.09657 [0.09577, 0.09738] | 516000 | 93.30% | +0.32 [+0.05, +0.50] | +0.42 [+0.13, +0.50] | 0.00 (8) |
| oracle | 0.00462 [0.00444, 0.00481] | 516000 | 97.80% | +1.00 [+1.00, +1.00] | +1.00 [+1.00, +1.00] | 1.00 (8) |
| moment_v1 | 0.35771 [0.35640, 0.35902] | 516000 | 82.88% | -1.59 [-2.74, -0.98] | -1.64 [-3.12, -0.96] | 0.00 (8) |
| em_pi | 0.03212 [0.03164, 0.03260] | 516000 | 96.18% | +0.80 [+0.73, +0.87] | +0.77 [+0.75, +0.86] | 0.38 (8) |
| em_pi_fast | 0.00854 [0.00830, 0.00880] | 516000 | 97.42% | +0.97 [+0.95, +0.98] | +0.97 [+0.94, +0.98] | 1.00 (8) |
| gated_v5 | 0.00891 [0.00866, 0.00917] | 516000 | 97.30% | +0.97 [+0.95, +0.98] | +0.97 [+0.95, +0.98] | 1.00 (8) |

frozen-vs-oracle LER gap: 13.622 percentage points
detector (v5 alarm on the frozen boundary, per window of 1500 shots): onsets caught within 12 h 39/39; event windows alarmed 190/190; false alarms on quiet windows 0/37; delay median 0 window(s) (one window = 4 h in simulation, one snapshot in real data; delay inside a window is not resolved)
gated arm alarm fraction over all windows: 0.49

### mix50
8 run(s); 43 windows per run, 1500 shots per window, d=5, physical error 0.001.

| arm | pooled LER [95% CI] | shots | mean accuracy | gap recovered, pooled [95% bootstrap CI over runs] | median per run [IQR] | runs >= 0.8 |
|---|---|---|---|---|---|---|
| frozen | 0.14084 [0.13989, 0.14179] | 516000 | 91.42% | - | - | - |
| periodic_12h | 0.02313 [0.02272, 0.02354] | 516000 | 96.63% | +0.86 [+0.78, +0.91] | +0.87 [+0.78, +0.90] | 0.75 (8) |
| periodic_24h | 0.05179 [0.05119, 0.05240] | 516000 | 95.35% | +0.65 [+0.48, +0.76] | +0.68 [+0.49, +0.78] | 0.25 (8) |
| periodic_48h | 0.09657 [0.09577, 0.09738] | 516000 | 93.30% | +0.32 [+0.05, +0.52] | +0.42 [+0.13, +0.50] | 0.00 (8) |
| oracle | 0.00462 [0.00444, 0.00481] | 516000 | 97.80% | +1.00 [+1.00, +1.00] | +1.00 [+1.00, +1.00] | 1.00 (8) |
| moment_v1 | 0.02304 [0.02264, 0.02346] | 516000 | 96.30% | +0.86 [+0.81, +0.91] | +0.82 [+0.79, +0.92] | 0.75 (8) |
| em_pi | 0.02170 [0.02130, 0.02210] | 516000 | 96.53% | +0.87 [+0.83, +0.91] | +0.88 [+0.82, +0.90] | 0.75 (8) |
| em_pi_fast | 0.00622 [0.00601, 0.00644] | 516000 | 97.60% | +0.99 [+0.98, +0.99] | +0.99 [+0.98, +0.99] | 1.00 (8) |
| gated_v5 | 0.00761 [0.00737, 0.00785] | 516000 | 97.40% | +0.98 [+0.96, +0.99] | +0.98 [+0.97, +0.99] | 1.00 (8) |

frozen-vs-oracle LER gap: 13.622 percentage points
detector (v5 alarm on the frozen boundary, per window of 1500 shots): onsets caught within 12 h 39/39; event windows alarmed 190/190; false alarms on quiet windows 0/37; delay median 0 window(s) (one window = 4 h in simulation, one snapshot in real data; delay inside a window is not resolved)
gated arm alarm fraction over all windows: 0.46

### physical
8 run(s); 43 windows per run, 1500 shots per window, d=5, physical error 0.001 ramped x3.

| arm | pooled LER [95% CI] | shots | mean accuracy | gap recovered, pooled [95% bootstrap CI over runs] | median per run [IQR] | runs >= 0.8 |
|---|---|---|---|---|---|---|
| frozen | 0.00571 [0.00550, 0.00591] | 516000 | 98.10% | - | - | - |
| periodic_12h | 0.00571 [0.00551, 0.00592] | 516000 | 98.09% | - | - | - |
| periodic_24h | 0.00572 [0.00552, 0.00593] | 516000 | 98.09% | - | - | - |
| periodic_48h | 0.00572 [0.00552, 0.00593] | 516000 | 98.09% | - | - | - |
| oracle | 0.00568 [0.00548, 0.00589] | 516000 | 98.09% | - | - | - |
| moment_v1 | 0.05256 [0.05195, 0.05317] | 516000 | 94.90% | - | - | - |
| em_pi | 0.00574 [0.00554, 0.00595] | 516000 | 98.09% | - | - | - |
| em_pi_fast | 0.00576 [0.00555, 0.00597] | 516000 | 98.09% | - | - | - |
| gated_v5 | 0.00573 [0.00553, 0.00594] | 516000 | 98.09% | - | - | - |

frozen-vs-oracle LER gap: 0.003 percentage points  (not distinguishable from zero, recovery fractions are not reported)
gated arm alarm fraction over all windows: 0.30


### both
8 run(s); 43 windows per run, 1500 shots per window, d=5, physical error 0.001 ramped x3.

| arm | pooled LER [95% CI] | shots | mean accuracy | gap recovered, pooled [95% bootstrap CI over runs] | median per run [IQR] | runs >= 0.8 |
|---|---|---|---|---|---|---|
| frozen | 0.14814 [0.14717, 0.14911] | 516000 | 91.42% | - | - | - |
| periodic_12h | 0.02741 [0.02697, 0.02786] | 516000 | 96.63% | +0.86 [+0.78, +0.91] | +0.87 [+0.77, +0.90] | 0.75 (8) |
| periodic_24h | 0.05688 [0.05625, 0.05751] | 516000 | 95.35% | +0.65 [+0.49, +0.75] | +0.67 [+0.51, +0.77] | 0.12 (8) |
| periodic_48h | 0.10359 [0.10276, 0.10443] | 516000 | 93.30% | +0.32 [+0.06, +0.49] | +0.40 [+0.13, +0.47] | 0.00 (8) |
| oracle | 0.00782 [0.00758, 0.00807] | 516000 | 97.80% | +1.00 [+1.00, +1.00] | +1.00 [+1.00, +1.00] | 1.00 (8) |
| moment_v1 | 0.12562 [0.12472, 0.12653] | 516000 | 92.85% | +0.16 [-0.14, +0.33] | +0.09 [-0.19, +0.28] | 0.00 (8) |
| em_pi | 0.02897 [0.02852, 0.02943] | 516000 | 96.48% | +0.85 [+0.79, +0.90] | +0.84 [+0.80, +0.87] | 0.75 (8) |
| em_pi_fast | 0.00986 [0.00960, 0.01014] | 516000 | 97.59% | +0.99 [+0.98, +0.99] | +0.98 [+0.98, +0.99] | 1.00 (8) |
| gated_v5 | 0.01053 [0.01025, 0.01081] | 516000 | 97.49% | +0.98 [+0.97, +0.99] | +0.98 [+0.97, +0.99] | 1.00 (8) |

frozen-vs-oracle LER gap: 14.032 percentage points
gated arm alarm fraction over all windows: 0.66

### real_q0
8 run(s); 68 windows per run, 1500 shots per window, d=5, physical error 0.001.

| arm | pooled LER [95% CI] | shots | mean accuracy | gap recovered, pooled [95% bootstrap CI over runs] | median per run [IQR] | runs >= 0.8 |
|---|---|---|---|---|---|---|
| frozen | 0.00574 [0.00557, 0.00590] | 816000 | 97.74% | - | - | - |
| periodic_12h | 0.00532 [0.00517, 0.00549] | 816000 | 97.86% | +0.45 [+0.38, +0.49] | +0.46 [+0.42, +0.49] | 0.00 (8) |
| periodic_24h | 0.00502 [0.00487, 0.00518] | 816000 | 97.88% | +0.78 [+0.74, +0.83] | +0.76 [+0.73, +0.83] | 0.38 (8) |
| periodic_48h | 0.00513 [0.00497, 0.00528] | 816000 | 97.87% | +0.66 [+0.62, +0.71] | +0.66 [+0.61, +0.72] | 0.00 (8) |
| oracle | 0.00481 [0.00467, 0.00497] | 816000 | 97.91% | +1.00 [+1.00, +1.00] | +1.00 [+1.00, +1.00] | 1.00 (8) |
| moment_v1 | 0.03067 [0.03030, 0.03105] | 816000 | 95.61% | -27.09 [-29.94, -24.58] | -27.32 [-30.63, -24.74] | 0.00 (8) |
| em_pi | 0.00494 [0.00479, 0.00509] | 816000 | 97.88% | +0.87 [+0.82, +0.91] | +0.89 [+0.80, +0.92] | 0.75 (8) |
| em_pi_fast | 0.00489 [0.00474, 0.00504] | 816000 | 97.90% | +0.92 [+0.87, +0.96] | +0.94 [+0.90, +0.96] | 1.00 (8) |
| gated_v5 | 0.00489 [0.00474, 0.00504] | 816000 | 97.89% | +0.92 [+0.88, +0.96] | +0.95 [+0.86, +0.96] | 1.00 (8) |

frozen-vs-oracle LER gap: 0.092 percentage points
detector (v5 alarm on the frozen boundary, per window of 1500 shots): onsets caught within 12 h 116/116; event windows alarmed 274/274; false alarms on quiet windows 0/38; delay median 0 window(s) (one window = 4 h in simulation, one snapshot in real data; delay inside a window is not resolved)
gated arm alarm fraction over all windows: 0.62

### real_q1
8 run(s); 68 windows per run, 1500 shots per window, d=5, physical error 0.001.

| arm | pooled LER [95% CI] | shots | mean accuracy | gap recovered, pooled [95% bootstrap CI over runs] | median per run [IQR] | runs >= 0.8 |
|---|---|---|---|---|---|---|
| frozen | 0.00992 [0.00970, 0.01013] | 816000 | 97.75% | - | - | - |
| periodic_12h | 0.00946 [0.00925, 0.00967] | 816000 | 97.76% | +0.16 [+0.13, +0.20] | +0.16 [+0.12, +0.20] | 0.00 (8) |
| periodic_24h | 0.00993 [0.00972, 0.01015] | 816000 | 97.75% | -0.01 [-0.06, +0.04] | +0.00 [-0.07, +0.06] | 0.00 (8) |
| periodic_48h | 0.01102 [0.01079, 0.01125] | 816000 | 97.48% | -0.40 [-0.46, -0.35] | -0.37 [-0.43, -0.34] | 0.00 (8) |
| oracle | 0.00715 [0.00697, 0.00734] | 816000 | 97.88% | +1.00 [+1.00, +1.00] | +1.00 [+1.00, +1.00] | 1.00 (8) |
| moment_v1 | 0.04227 [0.04184, 0.04271] | 816000 | 95.22% | -11.71 [-12.36, -11.17] | -11.63 [-12.21, -11.18] | 0.00 (8) |
| em_pi | 0.00763 [0.00744, 0.00782] | 816000 | 97.84% | +0.83 [+0.79, +0.86] | +0.83 [+0.80, +0.85] | 0.75 (8) |
| em_pi_fast | 0.00714 [0.00696, 0.00732] | 816000 | 97.89% | +1.00 [+0.99, +1.02] | +1.01 [+0.99, +1.02] | 1.00 (8) |
| gated_v5 | 0.00736 [0.00718, 0.00755] | 816000 | 97.83% | +0.92 [+0.90, +0.94] | +0.93 [+0.91, +0.95] | 1.00 (8) |

frozen-vs-oracle LER gap: 0.276 percentage points
detector (v5 alarm on the frozen boundary, per window of 1500 shots): onsets caught within 12 h 16/16; event windows alarmed 23/23; false alarms on quiet windows 0/448; delay median 0 window(s) (one window = 4 h in simulation, one snapshot in real data; delay inside a window is not resolved)
gated arm alarm fraction over all windows: 0.07

### real_q2
8 run(s); 68 windows per run, 1500 shots per window, d=5, physical error 0.001.

| arm | pooled LER [95% CI] | shots | mean accuracy | gap recovered, pooled [95% bootstrap CI over runs] | median per run [IQR] | runs >= 0.8 |
|---|---|---|---|---|---|---|
| frozen | 0.00039 [0.00035, 0.00044] | 816000 | 99.42% | - | - | - |
| periodic_12h | 0.00039 [0.00035, 0.00043] | 816000 | 99.43% | - | - | - |
| periodic_24h | 0.00039 [0.00035, 0.00043] | 816000 | 99.42% | - | - | - |
| periodic_48h | 0.00038 [0.00034, 0.00043] | 816000 | 99.44% | - | - | - |
| oracle | 0.00038 [0.00034, 0.00042] | 816000 | 99.44% | - | - | - |
| moment_v1 | 0.00301 [0.00290, 0.00313] | 816000 | 98.45% | - | - | - |
| em_pi | 0.00039 [0.00035, 0.00043] | 816000 | 99.43% | - | - | - |
| em_pi_fast | 0.00038 [0.00034, 0.00043] | 816000 | 99.44% | - | - | - |
| gated_v5 | 0.00038 [0.00034, 0.00043] | 816000 | 99.43% | - | - | - |

frozen-vs-oracle LER gap: 0.001 percentage points  (not distinguishable from zero, recovery fractions are not reported)
detector (v5 alarm on the frozen boundary, per window of 1500 shots): onsets caught within 12 h 16/16; event windows alarmed 16/16; false alarms on quiet windows 0/386; delay median 0 window(s) (one window = 4 h in simulation, one snapshot in real data; delay inside a window is not resolved)
gated arm alarm fraction over all windows: 0.18


### batch100
8 run(s); 43 windows per run, 1500 shots per window, d=5, physical error 0.001.

| arm | pooled LER [95% CI] | shots | mean accuracy | gap recovered, pooled [95% bootstrap CI over runs] | median per run [IQR] | runs >= 0.8 |
|---|---|---|---|---|---|---|
| frozen | 0.14187 [0.14092, 0.14282] | 516000 | 91.46% | - | - | - |
| periodic_12h | 0.02287 [0.02246, 0.02328] | 516000 | 96.64% | +0.87 [+0.79, +0.91] | +0.87 [+0.77, +0.91] | 0.75 (8) |
| periodic_24h | 0.05253 [0.05192, 0.05314] | 516000 | 95.32% | +0.65 [+0.47, +0.76] | +0.67 [+0.48, +0.79] | 0.25 (8) |
| periodic_48h | 0.09746 [0.09665, 0.09827] | 516000 | 93.28% | +0.32 [+0.04, +0.50] | +0.41 [+0.12, +0.52] | 0.00 (8) |
| oracle | 0.00465 [0.00446, 0.00483] | 516000 | 97.82% | +1.00 [+1.00, +1.00] | +1.00 [+1.00, +1.00] | 1.00 (8) |
| moment_v1 | 0.11767 [0.11680, 0.11855] | 516000 | 92.92% | +0.18 [-0.10, +0.33] | +0.12 [-0.28, +0.32] | 0.00 (8) |
| em_pi | 0.02418 [0.02376, 0.02460] | 516000 | 96.49% | +0.86 [+0.80, +0.90] | +0.86 [+0.81, +0.88] | 0.75 (8) |
| em_pi_fast | 0.00676 [0.00654, 0.00699] | 516000 | 97.56% | +0.98 [+0.97, +0.99] | +0.98 [+0.97, +0.99] | 1.00 (8) |
| gated_v5 | 0.00811 [0.00787, 0.00835] | 516000 | 97.39% | +0.97 [+0.95, +0.99] | +0.98 [+0.96, +0.99] | 1.00 (8) |

frozen-vs-oracle LER gap: 13.722 percentage points
gated arm alarm fraction over all windows: 0.47

### batch300
8 run(s); 43 windows per run, 1500 shots per window, d=5, physical error 0.001.

| arm | pooled LER [95% CI] | shots | mean accuracy | gap recovered, pooled [95% bootstrap CI over runs] | median per run [IQR] | runs >= 0.8 |
|---|---|---|---|---|---|---|
| frozen | 0.14191 [0.14096, 0.14287] | 516000 | 91.42% | - | - | - |
| periodic_12h | 0.02326 [0.02286, 0.02368] | 516000 | 96.64% | +0.86 [+0.78, +0.91] | +0.87 [+0.77, +0.91] | 0.75 (8) |
| periodic_24h | 0.05223 [0.05163, 0.05284] | 516000 | 95.35% | +0.65 [+0.47, +0.76] | +0.69 [+0.48, +0.79] | 0.25 (8) |
| periodic_48h | 0.09707 [0.09626, 0.09788] | 516000 | 93.33% | +0.33 [+0.05, +0.52] | +0.43 [+0.13, +0.51] | 0.00 (8) |
| oracle | 0.00462 [0.00444, 0.00481] | 516000 | 97.82% | +1.00 [+1.00, +1.00] | +1.00 [+1.00, +1.00] | 1.00 (8) |
| moment_v1 | 0.11934 [0.11845, 0.12022] | 516000 | 92.83% | +0.16 [-0.12, +0.34] | +0.07 [-0.22, +0.31] | 0.00 (8) |
| em_pi | 0.02352 [0.02311, 0.02394] | 516000 | 96.49% | +0.86 [+0.81, +0.91] | +0.86 [+0.79, +0.90] | 0.75 (8) |
| em_pi_fast | 0.00650 [0.00628, 0.00672] | 516000 | 97.59% | +0.99 [+0.98, +0.99] | +0.99 [+0.97, +0.99] | 1.00 (8) |
| gated_v5 | 0.00767 [0.00743, 0.00791] | 516000 | 97.42% | +0.98 [+0.96, +0.99] | +0.98 [+0.96, +0.99] | 1.00 (8) |

frozen-vs-oracle LER gap: 13.729 percentage points
gated arm alarm fraction over all windows: 0.45

