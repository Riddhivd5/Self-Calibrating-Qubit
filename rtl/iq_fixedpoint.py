"""
Reference normalization + fixed-point quantization for IQ readout data.

This is the shared spec for the Self-Calibrating Qubit Readout project.
Everyone converting IQ data to hardware format should use this exact
function so real (Sanath), synthetic (Gautham), and hardware (Riddhi)
data all land in the same numeric representation.

Pipeline: raw IQ (arbitrary units, from IBM kerneled readout)
          -> normalize (divide by SCALE, a fixed power of two)
          -> quantize (round to Q1.15 fixed-point, 16-bit signed)

Derived from real calibration data (iq_2026-09-11_08-58-08.npz):
observed global |I|, |Q| max was ~2.24e8, so SCALE = 2**28 keeps
normalized values within about +-0.84, safely inside the [-1, 1) range
Q1.15 can represent.
"""

import numpy as np

# --- Shared constants: change these in ONE place, everyone re-syncs ---
SCALE = 2 ** 28          # normalization divisor (raw arbitrary units -> ~[-1, 1])
FRAC_BITS = 15            # Q1.15: 1 sign bit + 15 fractional bits
INT_MIN = -(2 ** 15)      # -32768
INT_MAX = 2 ** 15 - 1     #  32767


def normalize(raw):
    """
    Divide raw IQ values (arbitrary units, e.g. straight from IBM's
    kerneled readout) by SCALE to bring them into roughly [-1, 1].

    raw: numpy array of complex128 (real IQ) or float (I or Q alone)
    returns: same shape, float64, normalized
    """
    return raw / SCALE


def quantize(normalized):
    """
    Convert normalized float values (~[-1, 1]) into Q1.15 signed
    16-bit fixed-point integers, the same format the FPGA discriminator
    expects on its input port.

    normalized: numpy array of float (real-valued, e.g. .real or .imag
                of a normalized complex array)
    returns: numpy array of int16
    """
    scaled = normalized * (2 ** FRAC_BITS)
    rounded = np.round(scaled)
    clipped = np.clip(rounded, INT_MIN, INT_MAX)
    if not np.array_equal(rounded, clipped):
        n_clipped = np.sum(rounded != clipped)
        print(f"WARNING: {n_clipped} value(s) clipped during quantization "
              f"— check SCALE, it may be too small for this dataset.")
    return clipped.astype(np.int16)


def dequantize(fixed):
    """
    Inverse of quantize(): Q1.15 int16 -> normalized float.
    Useful for verifying round-trip accuracy in the NumPy emulator.
    """
    return fixed.astype(np.float64) / (2 ** FRAC_BITS)


def raw_to_fixed_point(raw_complex):
    """
    Full pipeline: raw complex IQ (arbitrary units) -> (I_fixed, Q_fixed)
    as two int16 arrays, ready to feed into the RTL testbench or the
    NumPy emulator.

    raw_complex: numpy array of complex128
    returns: (i_fixed, q_fixed) — both int16 arrays, same shape as input
    """
    i_norm = normalize(raw_complex.real)
    q_norm = normalize(raw_complex.imag)
    i_fixed = quantize(i_norm)
    q_fixed = quantize(q_norm)
    return i_fixed, q_fixed


if __name__ == "__main__":
    # Quick self-check against the real data Sanath collected.
    data = np.load("iq_2026-09-11_08-58-08.npz")

    print(f"{'channel':<12} {'I range (fixed)':<20} {'Q range (fixed)':<20}")
    for key in data.keys():
        raw = data[key]
        i_fixed, q_fixed = raw_to_fixed_point(raw)
        print(f"{key:<12} "
              f"[{i_fixed.min():>6}, {i_fixed.max():>6}]      "
              f"[{q_fixed.min():>6}, {q_fixed.max():>6}]")

    # Round-trip sanity check on one channel
    raw = data["q0_state0"]
    i_fixed, q_fixed = raw_to_fixed_point(raw)
    i_back = dequantize(i_fixed) * SCALE
    max_err = np.max(np.abs(i_back - raw.real))
    print(f"\nMax round-trip error on q0_state0 (I): {max_err:.1f} "
          f"raw units ({max_err / SCALE * 100:.4f}% of full scale)")
