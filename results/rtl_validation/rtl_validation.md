# RTL validation of the baseline discriminator (rtl/discriminator.v)

RTL simulation with Icarus Verilog version 12.0 (stable) (); every clock cycle of the RTL response (valid_out and state_bit) compared with the cycle-accurate Python model rtl/discriminator_model.py. This is simulation, not a run on the FPGA board; it gives no resource or timing numbers.

Total: 1,102,259 clock cycles simulated (13 s), 0 mismatching outputs.

| test | what it covers | clock cycles compared | valid samples | valid_out mismatches | state_bit mismatches | unknown (X) outputs |
|---|---|---|---|---|---|---|
| dataset | every labelled IQ point: 149 snapshots x 3 qubits x 2 states, one sample per clock, coefficients switched 446 times in mid-stream | 894,003 | 894,000 | 0 | 0 | 0 |
| boundary | sums of exactly zero and one step either side | 48 | 45 | 0 | 0 | 0 |
| extremes | all 6^5 combinations of extreme and near-zero values | 7,779 | 7,776 | 0 | 0 | 0 |
| random | random inputs, coefficients changing every cycle, valid_in random (70%) | 200,003 | 140,441 | 0 | 0 | 0 |
| reset_midstream | synchronous reset asserted twice during valid traffic | 403 | 400 | 0 | 0 | 0 |
| latency | one valid sample, then idle | 12 | 1 | 0 | 0 | 0 |

## Dataset

- 894,000 labelled IQ points (IBM 2026-09-11 to 2026-09-27); raw values divided by 2^28 and rounded to Q1.15. Points clipped by the Q1.15 range: 0. I range [-31028, 30439], Q range [-32193, 9290].
- RTL decision equals the bit-exact model on 894,000 of 894,000 points; valid_out asserted for 894,000 of 894,000.
- Boundary per qubit: perpendicular bisector of the two centroids of the first snapshot, held fixed for all snapshots (so the accuracy below includes the real drift of the later snapshots).

| qubit | Q1.15 coefficients (a, b, c) | points | fixed-point vs floating-point decisions that differ | accuracy, RTL (Q1.15) | accuracy, floating point |
|---|---|---|---|---|---|
| q0 | (32735, 108, 824) | 298,000 | 1 (0.0003%) | 97.773% | 97.773% |
| q1 | (32735, -1336, 494) | 298,000 | 0 (0.0000%) | 97.754% | 97.754% |
| q2 | (32735, -796, 107) | 298,000 | 1 (0.0003%) | 99.502% | 99.502% |
| all | | 894,000 | 2 (0.0002%) | 98.343% | 98.343% |

## Directed tests

- Boundary: 45 vectors, of which 14 have a sum of exactly zero. RTL output agrees with sum >= 0 on 45 of 45. For a sum of exactly zero the RTL outputs state 1 (14 of 14); the header comment of discriminator.v says state 1 needs a sum strictly above zero, so the comment and the implementation differ on that one value.
- Extremes: 7,776 vectors; largest |sum| 3,221,192,704 against a 34-bit signed range of 8,589,934,592, so the adder cannot overflow. RTL output agrees with the exact integer sum on 7,776 of 7,776.
- Pipeline latency measured on the RTL: valid_out appears 3 clock edges after the edge-aligned valid sample is presented; a new sample is accepted every clock cycle.
- Parameter update: coefficients are registered together with their sample, so a coefficient change applies from the sample presented in the same cycle and samples already in the pipeline keep the old coefficients (covered by the dataset and random tests).
- Reset: after a synchronous reset the samples in the pipeline are discarded and valid_out stays low until new samples have passed through (covered by the reset test).

