"""
Reference normalization + fixed-point quantization for IQ readout data.

This is the shared spec for the Self-Calibrating Qubit Readout project.

Pipeline:
    raw IQ (arbitrary units, from IBM kerneled readout)
        -> normalize (divide by SCALE, a fixed power of two)
        -> quantize (round to Q1.15 fixed-point, 16-bit signed)

Shared constants:
    SCALE = 2**28
    FRAC_BITS = 15
    INT_MIN = -32768
    INT_MAX = 32767
"""

import os

import numpy as np


# ============================================================
# Shared constants
# ============================================================

SCALE = 2 ** 28
FRAC_BITS = 15

INT_MIN = -(2 ** 15)
INT_MAX = 2 ** 15 - 1


# ============================================================
# Normalization
# ============================================================

def normalize(raw):
    """
    Divide raw IQ values by SCALE.

    Parameters
    ----------
    raw : numpy array
        Raw IQ values in arbitrary units.

    Returns
    -------
    numpy array
        Normalized floating-point values.
    """

    return raw / SCALE


# ============================================================
# Quantization
# ============================================================

def quantize(normalized):
    """
    Convert normalized values to Q1.15 signed int16.

    Parameters
    ----------
    normalized : numpy array
        Normalized real-valued IQ samples.

    Returns
    -------
    numpy array
        int16 fixed-point values.
    """

    scaled = (
        normalized
        * (2 ** FRAC_BITS)
    )

    rounded = np.round(
        scaled
    )

    clipped = np.clip(
        rounded,
        INT_MIN,
        INT_MAX
    )

    if not np.array_equal(
        rounded,
        clipped
    ):

        n_clipped = np.sum(
            rounded != clipped
        )

        print(
            f"WARNING: {n_clipped} "
            f"value(s) clipped during quantization "
            f"— check SCALE, it may be too small "
            f"for this dataset."
        )

    return clipped.astype(
        np.int16
    )


# ============================================================
# Dequantization
# ============================================================

def dequantize(fixed):
    """
    Convert Q1.15 int16 values back to normalized floats.
    """

    return (
        fixed.astype(
            np.float64
        )
        / (2 ** FRAC_BITS)
    )


# ============================================================
# Full raw -> fixed-point pipeline
# ============================================================

def raw_to_fixed_point(
    raw_complex
):
    """
    Convert raw complex IQ to two int16 arrays.

    Returns
    -------
    i_fixed, q_fixed
    """

    i_norm = normalize(
        raw_complex.real
    )

    q_norm = normalize(
        raw_complex.imag
    )

    i_fixed = quantize(
        i_norm
    )

    q_fixed = quantize(
        q_norm
    )

    return (
        i_fixed,
        q_fixed
    )


# ============================================================
# Self-check
# ============================================================

if __name__ == "__main__":

    # --------------------------------------------------------
    # Find project root
    # --------------------------------------------------------

    SCRIPT_DIR = os.path.dirname(
        os.path.abspath(__file__)
    )

    PROJECT_ROOT = SCRIPT_DIR

    DATA_DIR = os.path.join(
        PROJECT_ROOT,
        "data"
    )

    # --------------------------------------------------------
    # Original reference dataset
    # --------------------------------------------------------

    filename = (
        "iq_2026-09-11_08-58-08.npz"
    )

    data_path = os.path.join(
        DATA_DIR,
        filename
    )

    print(
        f"Loading IQ data from:\n"
        f"{data_path}"
    )

    if not os.path.exists(
        data_path
    ):

        raise FileNotFoundError(
            "\nCould not find the expected IQ file:\n"
            f"{data_path}\n\n"
            "Check that the file exists inside the "
            "'data' folder."
        )

    data = np.load(
        data_path
    )

    print(
        f"Found {len(data.keys())} IQ channels."
    )

    print()

    # --------------------------------------------------------
    # Convert every channel
    # --------------------------------------------------------

    print(
        f"{'channel':<12} "
        f"{'I range (fixed)':<20} "
        f"{'Q range (fixed)':<20}"
    )

    print(
        "-" * 60
    )

    for key in data.keys():

        raw = data[key]

        i_fixed, q_fixed = (
            raw_to_fixed_point(
                raw
            )
        )

        print(
            f"{key:<12} "
            f"[{i_fixed.min():>6}, "
            f"{i_fixed.max():>6}]      "
            f"[{q_fixed.min():>6}, "
            f"{q_fixed.max():>6}]"
        )

    # --------------------------------------------------------
    # Round-trip sanity check
    # --------------------------------------------------------

    raw = data[
        "q0_state0"
    ]

    i_fixed, q_fixed = (
        raw_to_fixed_point(
            raw
        )
    )

    i_back = (
        dequantize(
            i_fixed
        )
        * SCALE
    )

    max_err = np.max(
        np.abs(
            i_back
            - raw.real
        )
    )

    print()

    print(
        "Max round-trip error on "
        "q0_state0 (I): "
        f"{max_err:.1f} raw units "
        f"({max_err / SCALE * 100:.4f}% "
        f"of full scale)"
    )