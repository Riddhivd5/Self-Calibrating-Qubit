# Decoder check: is the LER lost to readout drift a decoder problem or a readout problem?

d = 5, physical error 0.001, 1500 shots per window. The fixed decoder is built at the calibration-time readout error; the informed decoder is rebuilt for every window from that window's true mean readout error (not available online: an upper bound on a decoder-side fix). LER in percent with 95% resampling intervals (runs for simulated drift, window blocks for the real replay, which is one trajectory re-sampled). Paired differences use the same resamples.

## Simulated 1 sigma step (step_q1): 8 runs x 43 windows x 1500 shots = 516,000 shots per arm

Mean readout error: frozen boundary 6.37%, oracle boundary 1.71%. Distinct informed decoders built: 31.

| arm | LER % [95% interval] | logical errors |
|---|---|---|
| frozen boundary, fixed decoder | 5.068 [4.962, 5.176] | 26,151 |
| frozen boundary, informed decoder | 4.007 [3.942, 4.076] | 20,676 |
| oracle boundary, fixed decoder | 0.270 [0.259, 0.282] | 1,395 |
| oracle boundary, informed decoder | 0.270 [0.258, 0.282] | 1,391 |

- Fixing the readout only (oracle boundary, fixed decoder) removes 4.798 percentage points of LER; this is the frozen-to-oracle gap used elsewhere.
- Fixing the decoder only (frozen boundary, informed decoder) changes LER by -1.061 [-1.157, -0.981] points, i.e. removes 0.22 [0.21, 0.24] of that gap.
- With the readout fixed, informing the decoder changes LER by -0.001 [-0.003, +0.001] points.
- LER still lost with a perfectly informed decoder but a frozen boundary, relative to fixing the readout: +3.737 [+3.665, +3.812] points.
- Consistency: the fixed-decoder arms reproduce the frozen and oracle arms of results/closed_loop/controlled/ler_windows.csv in 688 of 688 windows.

## Real replay q1 (real_q1): 8 runs x 149 windows x 1500 shots = 1,788,000 shots per arm

Mean readout error: frozen boundary 2.09%, oracle boundary 1.94%. Distinct informed decoders built: 68.

| arm | LER % [95% interval] | logical errors |
|---|---|---|
| frozen boundary, fixed decoder | 0.892 [0.512, 1.341] | 15,944 |
| frozen boundary, informed decoder | 0.848 [0.497, 1.261] | 15,165 |
| oracle boundary, fixed decoder | 0.663 [0.422, 0.940] | 11,862 |
| oracle boundary, informed decoder | 0.647 [0.413, 0.911] | 11,562 |

- Fixing the readout only (oracle boundary, fixed decoder) removes 0.228 percentage points of LER; this is the frozen-to-oracle gap used elsewhere.
- Fixing the decoder only (frozen boundary, informed decoder) changes LER by -0.044 [-0.085, -0.014] points, i.e. removes 0.19 [0.14, 0.34] of that gap.
- With the readout fixed, informing the decoder changes LER by -0.017 [-0.030, -0.006] points.
- LER still lost with a perfectly informed decoder but a frozen boundary, relative to fixing the readout: +0.185 [+0.046, +0.391] points.
- Consistency: the fixed-decoder arms reproduce the frozen and oracle arms of results/closed_loop/real/ler_windows.csv in 2384 of 2384 windows.

## Real replay q0 (real_q0): 8 runs x 149 windows x 1500 shots = 1,788,000 shots per arm

Mean readout error: frozen boundary 1.99%, oracle boundary 1.69%. Distinct informed decoders built: 38.

| arm | LER % [95% interval] | logical errors |
|---|---|---|
| frozen boundary, fixed decoder | 0.498 [0.412, 0.614] | 8,902 |
| frozen boundary, informed decoder | 0.485 [0.404, 0.594] | 8,673 |
| oracle boundary, fixed decoder | 0.428 [0.350, 0.531] | 7,652 |
| oracle boundary, informed decoder | 0.423 [0.347, 0.522] | 7,567 |

- Fixing the readout only (oracle boundary, fixed decoder) removes 0.070 percentage points of LER; this is the frozen-to-oracle gap used elsewhere.
- Fixing the decoder only (frozen boundary, informed decoder) changes LER by -0.013 [-0.020, -0.007] points, i.e. removes 0.18 [0.12, 0.26] of that gap.
- With the readout fixed, informing the decoder changes LER by -0.005 [-0.009, -0.001] points.
- LER still lost with a perfectly informed decoder but a frozen boundary, relative to fixing the readout: +0.057 [+0.041, +0.073] points.
- Consistency: the fixed-decoder arms reproduce the frozen and oracle arms of results/closed_loop/real/ler_windows.csv in 2384 of 2384 windows.

