# Attribution with held-out drift sizes and kinds: readout drift (positive) vs physical drift

d=5, physical error 0.001, healthy readout errors e0=0.01, e1=0.02 (state-dependent), healthy fire rate 0.03658. Each condition is tuned to a fire-rate rise; training levels +40%, +100%, +200%, held-out test levels +30%, +60%, +150%, +250%. Trained on kinds symmetric, shift, both only; 150 windows per condition. AUC intervals: 95% bootstrap over test windows (1000 resamples). The v5 alarm needs a +30% rise, so +30% is the smallest drift it flags.

Drift size that gives each fire-rate rise (multiplier for symmetric/both/data/gate, added probability otherwise):

| kind | +30% | +40% | +60% | +100% | +150% | +200% | +250% |
|---|---|---|---|---|---|---|---|
| symmetric | 1.436 | 1.582 | 1.879 | 2.487 | 3.265 | 4.074 | 4.908 |
| shift | 0.01126 | 0.01379 | 0.01895 | 0.02943 | 0.04283 | 0.05674 | 0.07114 |
| decay | 0.02097 | 0.02835 | 0.04324 | 0.0748 | 0.119 | 0.1698 | 0.2313 |
| both | 2.12 | 2.493 | 3.271 | 4.848 | 6.904 | 9.076 | 11.37 |
| data | 6.936 | 8.845 | 12.91 | 21.02 | 31.62 | 42.73 | 54.33 |
| gate | 2.386 | 2.852 | 3.824 | 5.749 | 8.302 | 10.96 | 13.8 |
| t1 | 0.006744 | 0.009064 | 0.01346 | 0.02298 | 0.03506 | 0.0477 | 0.06076 |
| dephasing | 0.005835 | 0.007837 | 0.01204 | 0.02053 | 0.03264 | 0.04602 | 0.0616 |
| reset | 0.005658 | 0.007379 | 0.01119 | 0.01888 | 0.02866 | 0.03884 | 0.0492 |

## Window = 250 shots (1250 syndrome rounds)

### Feature ablation, all held-out conditions pooled (1800 readout and 3600 physical test windows)

| features | AUC [95% CI] | accuracy at 0.5 | chance band: AUC with shuffled TEST labels (2.5th-97.5th pct) | AUC after training on shuffled labels: median (2.5th-97.5th pct) |
|---|---|---|---|---|
| fire rate only | 0.506 [0.491, 0.522] | 0.333 | 0.484-0.517 | 0.506 (0.493-0.507) |
| correlation only | 0.857 [0.848, 0.867] | 0.766 | 0.484-0.517 | 0.857 (0.143-0.857) |
| asymmetry only | 0.595 [0.580, 0.611] | 0.403 | 0.484-0.515 | 0.405 (0.405-0.595) |
| correlation + asymmetry | 0.865 [0.856, 0.874] | 0.804 | 0.484-0.516 | 0.511 (0.132-0.867) |
| all three | 0.903 [0.895, 0.911] | 0.880 | 0.483-0.516 | 0.483 (0.139-0.827) |

### Feature ablation, held-out conditions pooled, WITHOUT the reset-error kind (1800 readout and 3000 physical test windows)

| features | AUC [95% CI] | accuracy at 0.5 | chance band: AUC with shuffled TEST labels (2.5th-97.5th pct) | AUC after training on shuffled labels: median (2.5th-97.5th pct) |
|---|---|---|---|---|
| fire rate only | 0.507 [0.490, 0.524] | 0.375 | 0.484-0.515 | 0.507 (0.493-0.507) |
| correlation only | 0.938 [0.932, 0.944] | 0.843 | 0.483-0.516 | 0.062 (0.062-0.938) |
| asymmetry only | 0.589 [0.572, 0.605] | 0.441 | 0.483-0.517 | 0.589 (0.411-0.589) |
| correlation + asymmetry | 0.968 [0.964, 0.972] | 0.899 | 0.483-0.516 | 0.493 (0.043-0.967) |
| all three | 1.000 [0.999, 1.000] | 0.990 | 0.483-0.518 | 0.504 (0.127-0.931) |

Two nulls. Shuffling the TEST labels gives the band a classifier with no information reaches on a test set of this size. Training on shuffled labels shows what the fitted model does without label information; with one or two features it still outputs a monotone function of a real feature, so it lands on either the real AUC or one minus it, and the median is the informative number.

### AUC by kind, all three features, held-out levels pooled (kinds marked * were never seen in training)

| physical \ readout | symmetric | shift | decay * |
|---|---|---|---|
| both | 1.000 [1.000, 1.000] | 1.000 [1.000, 1.000] | 1.000 [0.999, 1.000] |
| data * | 1.000 [1.000, 1.000] | 1.000 [1.000, 1.000] | 1.000 [1.000, 1.000] |
| gate * | 1.000 [1.000, 1.000] | 1.000 [1.000, 1.000] | 0.999 [0.999, 1.000] |
| t1 * | 1.000 [1.000, 1.000] | 1.000 [1.000, 1.000] | 0.999 [0.998, 1.000] |
| dephasing * | 1.000 [1.000, 1.000] | 1.000 [1.000, 1.000] | 0.997 [0.995, 0.998] |
| reset * | 0.423 [0.391, 0.457] | 0.632 [0.603, 0.665] | 0.200 [0.175, 0.224] |

### AUC by held-out level, all three features, all kinds pooled

| fire-rate rise | AUC [95% CI] | accuracy at 0.5 |
|---|---|---|
| +30% | 0.904 [0.887, 0.918] | 0.856 |
| +60% | 0.904 [0.889, 0.920] | 0.887 |
| +150% | 0.895 [0.877, 0.911] | 0.889 |
| +250% | 0.891 [0.872, 0.908] | 0.889 |

### Mean feature values on the held-out test windows (correlation and asymmetry as multiples of the healthy value)

| kind | fire-rate rise | correlation / healthy | asymmetry / healthy |
|---|---|---|---|
| symmetric | +122% | 2.25 | 1.61 |
| shift | +122% | 2.49 | 4.00 |
| decay | +122% | 1.81 | 3.95 |
| both | +123% | 1.21 | 1.84 |
| data | +123% | 0.86 | 1.75 |
| gate | +122% | 1.30 | 1.92 |
| t1 | +123% | 1.30 | 1.67 |
| dephasing | +123% | 1.18 | 7.62 |
| reset | +123% | 2.33 | 2.07 |

## Window = 1500 shots (7500 syndrome rounds)

### Feature ablation, all held-out conditions pooled (1800 readout and 3600 physical test windows)

| features | AUC [95% CI] | accuracy at 0.5 | chance band: AUC with shuffled TEST labels (2.5th-97.5th pct) | AUC after training on shuffled labels: median (2.5th-97.5th pct) |
|---|---|---|---|---|
| fire rate only | 0.510 [0.494, 0.526] | 0.333 | 0.484-0.516 | 0.510 (0.490-0.510) |
| correlation only | 0.858 [0.849, 0.867] | 0.778 | 0.485-0.516 | 0.142 (0.142-0.858) |
| asymmetry only | 0.582 [0.565, 0.598] | 0.333 | 0.483-0.516 | 0.582 (0.418-0.582) |
| correlation + asymmetry | 0.872 [0.863, 0.880] | 0.821 | 0.483-0.516 | 0.515 (0.130-0.872) |
| all three | 0.898 [0.889, 0.906] | 0.883 | 0.483-0.516 | 0.507 (0.169-0.838) |

### Feature ablation, held-out conditions pooled, WITHOUT the reset-error kind (1800 readout and 3000 physical test windows)

| features | AUC [95% CI] | accuracy at 0.5 | chance band: AUC with shuffled TEST labels (2.5th-97.5th pct) | AUC after training on shuffled labels: median (2.5th-97.5th pct) |
|---|---|---|---|---|
| fire rate only | 0.510 [0.494, 0.526] | 0.375 | 0.483-0.516 | 0.490 (0.490-0.510) |
| correlation only | 0.941 [0.935, 0.947] | 0.849 | 0.485-0.518 | 0.941 (0.059-0.941) |
| asymmetry only | 0.574 [0.556, 0.590] | 0.374 | 0.482-0.516 | 0.426 (0.426-0.574) |
| correlation + asymmetry | 0.977 [0.974, 0.980] | 0.923 | 0.484-0.517 | 0.562 (0.029-0.961) |
| all three | 1.000 [1.000, 1.000] | 0.993 | 0.484-0.516 | 0.494 (0.067-0.948) |

Two nulls. Shuffling the TEST labels gives the band a classifier with no information reaches on a test set of this size. Training on shuffled labels shows what the fitted model does without label information; with one or two features it still outputs a monotone function of a real feature, so it lands on either the real AUC or one minus it, and the median is the informative number.

### AUC by kind, all three features, held-out levels pooled (kinds marked * were never seen in training)

| physical \ readout | symmetric | shift | decay * |
|---|---|---|---|
| both | 1.000 [1.000, 1.000] | 1.000 [1.000, 1.000] | 1.000 [1.000, 1.000] |
| data * | 1.000 [1.000, 1.000] | 1.000 [1.000, 1.000] | 1.000 [1.000, 1.000] |
| gate * | 1.000 [1.000, 1.000] | 1.000 [1.000, 1.000] | 1.000 [1.000, 1.000] |
| t1 * | 1.000 [1.000, 1.000] | 1.000 [1.000, 1.000] | 1.000 [1.000, 1.000] |
| dephasing * | 1.000 [1.000, 1.000] | 1.000 [1.000, 1.000] | 1.000 [1.000, 1.000] |
| reset * | 0.393 [0.361, 0.426] | 0.625 [0.594, 0.654] | 0.142 [0.122, 0.164] |

### AUC by held-out level, all three features, all kinds pooled

| fire-rate rise | AUC [95% CI] | accuracy at 0.5 |
|---|---|---|
| +30% | 0.898 [0.881, 0.914] | 0.865 |
| +60% | 0.894 [0.875, 0.911] | 0.889 |
| +150% | 0.890 [0.872, 0.907] | 0.889 |
| +250% | 0.889 [0.871, 0.906] | 0.889 |

### Mean feature values on the held-out test windows (correlation and asymmetry as multiples of the healthy value)

| kind | fire-rate rise | correlation / healthy | asymmetry / healthy |
|---|---|---|---|
| symmetric | +122% | 2.24 | 2.20 |
| shift | +122% | 2.48 | 9.05 |
| decay | +122% | 1.79 | 8.86 |
| both | +122% | 1.21 | 3.28 |
| data | +122% | 0.85 | 3.10 |
| gate | +122% | 1.29 | 3.51 |
| t1 | +122% | 1.29 | 2.73 |
| dephasing | +122% | 1.17 | 18.02 |
| reset | +122% | 2.31 | 3.70 |

