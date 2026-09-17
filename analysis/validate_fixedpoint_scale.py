"""
validate_fixedpoint_scale_v1_4.py

Validate IQDriftGenerator v1.4 raw output against Person 4's
shared raw-IQ / Q1.15 fixed-point pipeline.

v1.4 provides:
    generate_shots_raw()

which:
    1. keeps the scientific generator internally normalized,
    2. centers the two-state geometry,
    3. applies the qubit-specific real-data separation scale,
    4. multiplies by 2**28.

This script then feeds that raw output directly into
Person 4's iq_fixedpoint.raw_to_fixed_point().

Checks:
    - real raw range
    - synthetic raw range
    - ratio to real maximum
    - Q1.15 clipping warnings
    - fixed-point ranges

Run:
    python analysis/validate_fixedpoint_scale_v1_4.py

Terminal only. No graphs.
"""

import importlib.util
import json
import os
import sys
from datetime import datetime

import numpy as np


# ============================================================
# Paths
# ============================================================

SCRIPT_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

PROJECT_ROOT = os.path.abspath(
    os.path.join(
        SCRIPT_DIR,
        ".."
    )
)

DATA_DIR = os.path.join(
    PROJECT_ROOT,
    "data"
)


# ============================================================
# Settings
# ============================================================

N_SHOTS = 10000

TEST_TIMES_HOURS = [
    0.0,
    70.0,
    139.25,
]

PROFILE_NAMES = {
    0: "q0",
    1: "q1",
    2: "q2",
}


# ============================================================
# Load Person 4's exact module
# ============================================================

def load_iq_fixedpoint():

    candidates = [
        os.path.join(
            PROJECT_ROOT,
            "iq_fixedpoint.py"
        ),
        os.path.join(
            SCRIPT_DIR,
            "iq_fixedpoint.py"
        ),
    ]

    module_path = None

    for candidate in candidates:

        if os.path.exists(candidate):

            module_path = candidate
            break

    if module_path is None:

        raise FileNotFoundError(
            "Could not find Person 4's iq_fixedpoint.py."
        )

    spec = (
        importlib.util.spec_from_file_location(
            "iq_fixedpoint",
            module_path
        )
    )

    if spec is None or spec.loader is None:

        raise ImportError(
            f"Could not load {module_path}"
        )

    module = (
        importlib.util.module_from_spec(
            spec
        )
    )

    spec.loader.exec_module(
        module
    )

    return module


# ============================================================
# Import generator
# ============================================================

sys.path.insert(
    0,
    PROJECT_ROOT
)

from iq_generator import (
    IQDriftGenerator,
    DriftParams,
    ABSOLUTE_IQ_SEPARATION_SCALE,
    RAW_IQ_SCALE,
)


# ============================================================
# Find real files
# ============================================================

def find_iq_files():

    files = [
        filename
        for filename in os.listdir(DATA_DIR)
        if filename.startswith("iq_")
        and filename.endswith(".npz")
    ]

    files.sort()

    if not files:

        raise FileNotFoundError(
            f"No IQ files found in {DATA_DIR}"
        )

    return files


# ============================================================
# Timestamp
# ============================================================

def read_timestamp(filename):

    metadata_filename = (
        filename
        .replace(
            "iq_",
            "metadata_",
            1
        )
        .replace(
            ".npz",
            ".json"
        )
    )

    metadata_path = os.path.join(
        DATA_DIR,
        metadata_filename
    )

    if os.path.exists(
        metadata_path
    ):

        with open(
            metadata_path,
            "r",
            encoding="utf-8"
        ) as file:

            metadata = json.load(
                file
            )

        timestamp = metadata.get(
            "timestamp_utc"
        )

        if timestamp:

            return datetime.fromisoformat(
                timestamp
            )

    timestamp_text = (
        filename
        .replace(
            "iq_",
            ""
        )
        .replace(
            ".npz",
            ""
        )
    )

    return datetime.strptime(
        timestamp_text,
        "%Y-%m-%d_%H-%M-%S"
    )


# ============================================================
# Real range
# ============================================================

def analyze_real_range(files):

    abs_max = 0.0

    i_min = np.inf
    i_max = -np.inf

    q_min = np.inf
    q_max = -np.inf

    location = None

    for filename in files:

        path = os.path.join(
            DATA_DIR,
            filename
        )

        data = np.load(
            path
        )

        for key in data.keys():

            raw = data[key]

            i_values = raw.real
            q_values = raw.imag

            i_min = min(
                i_min,
                np.min(i_values)
            )

            i_max = max(
                i_max,
                np.max(i_values)
            )

            q_min = min(
                q_min,
                np.min(q_values)
            )

            q_max = max(
                q_max,
                np.max(q_values)
            )

            local_max = max(
                np.max(
                    np.abs(i_values)
                ),
                np.max(
                    np.abs(q_values)
                )
            )

            if local_max > abs_max:

                abs_max = float(
                    local_max
                )

                location = (
                    filename,
                    key
                )

    return {
        "i_min": float(i_min),
        "i_max": float(i_max),
        "q_min": float(q_min),
        "q_max": float(q_max),
        "abs_max": float(abs_max),
        "location": location,
    }


# ============================================================
# Generate synthetic raw IQ
# ============================================================

def generate_synthetic_raw(
    qubit,
    t_hours
):

    profile = PROFILE_NAMES[
        qubit
    ]

    generator = IQDriftGenerator(
        DriftParams(
            drift_profile=profile,
            stochastic_drift_strength=1.0,
            rng_seed=9000 + qubit,
        )
    )

    state0, _ = (
        generator.generate_shots_raw(
            n_shots=N_SHOTS,
            t_hours=t_hours,
            p_state1=0.0,
        )
    )

    state1, _ = (
        generator.generate_shots_raw(
            n_shots=N_SHOTS,
            t_hours=t_hours,
            p_state1=1.0,
        )
    )

    return np.concatenate(
        [
            state0,
            state1
        ]
    )


# ============================================================
# Raw range helper
# ============================================================

def analyze_raw(values):

    return {
        "i_min": float(
            np.min(values.real)
        ),
        "i_max": float(
            np.max(values.real)
        ),
        "q_min": float(
            np.min(values.imag)
        ),
        "q_max": float(
            np.max(values.imag)
        ),
        "abs_max": float(
            max(
                np.max(
                    np.abs(
                        values.real
                    )
                ),
                np.max(
                    np.abs(
                        values.imag
                    )
                )
            )
        ),
    }


# ============================================================
# Main
# ============================================================

def main():

    print(
        "=" * 80
    )

    print(
        "V1.4 RAW IQ / FIXED-POINT SCALE VALIDATION"
    )

    print(
        "=" * 80
    )

    iq_fixedpoint = (
        load_iq_fixedpoint()
    )

    files = find_iq_files()

    print(
        f"Found {len(files)} real IQ datasets."
    )

    print()
    print(
        "PERSON 4 CONSTANTS"
    )

    print(
        f"SCALE = {iq_fixedpoint.SCALE}"
    )

    print(
        f"Q1.15 range = "
        f"[{iq_fixedpoint.INT_MIN}, "
        f"{iq_fixedpoint.INT_MAX}]"
    )

    print()

    real = analyze_real_range(
        files
    )

    print(
        "REAL RAW DATA"
    )

    print(
        f"I range = "
        f"[{real['i_min']:+.3e}, "
        f"{real['i_max']:+.3e}]"
    )

    print(
        f"Q range = "
        f"[{real['q_min']:+.3e}, "
        f"{real['q_max']:+.3e}]"
    )

    print(
        f"Global |I/Q| max = "
        f"{real['abs_max']:.3e}"
    )

    print(
        f"Global max / 2^28 = "
        f"{real['abs_max'] / RAW_IQ_SCALE:.6f}"
    )

    print(
        f"Maximum location = "
        f"{real['location'][0]} -> "
        f"{real['location'][1]}"
    )

    # --------------------------------------------------------
    # Synthetic
    # --------------------------------------------------------

    for qubit in range(3):

        profile = PROFILE_NAMES[
            qubit
        ]

        print()
        print(
            "=" * 80
        )

        print(
            f"Q{qubit} / profile '{profile}'"
        )

        print(
            "=" * 80
        )

        print(
            f"Configured separation scale = "
            f"{ABSOLUTE_IQ_SEPARATION_SCALE[profile]:.4f}"
        )

        print(
            f"Expected raw separation = "
            f"{ABSOLUTE_IQ_SEPARATION_SCALE[profile] * RAW_IQ_SCALE:.3e}"
        )

        for t_hours in TEST_TIMES_HOURS:

            print()
            print(
                f"t = {t_hours:.2f} hours"
            )

            raw = generate_synthetic_raw(
                qubit,
                t_hours
            )

            stats = analyze_raw(
                raw
            )

            print(
                f"Raw I range = "
                f"[{stats['i_min']:+.3e}, "
                f"{stats['i_max']:+.3e}]"
            )

            print(
                f"Raw Q range = "
                f"[{stats['q_min']:+.3e}, "
                f"{stats['q_max']:+.3e}]"
            )

            print(
                f"Raw |I/Q| max = "
                f"{stats['abs_max']:.3e}"
            )

            print(
                f"Ratio to real global max = "
                f"{stats['abs_max'] / real['abs_max']:.3f}x"
            )

            print(
                f"Ratio to 2^28 = "
                f"{stats['abs_max'] / RAW_IQ_SCALE:.6f}"
            )

            print(
                "Person 4 fixed-point conversion:"
            )

            i_fixed, q_fixed = (
                iq_fixedpoint.raw_to_fixed_point(
                    raw
                )
            )

            print(
                f"I fixed range = "
                f"[{i_fixed.min()}, "
                f"{i_fixed.max()}]"
            )

            print(
                f"Q fixed range = "
                f"[{q_fixed.min()}, "
                f"{q_fixed.max()}]"
            )

            # These counts are diagnostic only. The actual clipping
            # warning is emitted by Person 4's quantize() function.
            i_boundary = np.sum(
                (
                    i_fixed
                    == iq_fixedpoint.INT_MIN
                )
                |
                (
                    i_fixed
                    == iq_fixedpoint.INT_MAX
                )
            )

            q_boundary = np.sum(
                (
                    q_fixed
                    == iq_fixedpoint.INT_MIN
                )
                |
                (
                    q_fixed
                    == iq_fixedpoint.INT_MAX
                )
            )

            print(
                f"Boundary-valued fixed samples: "
                f"I={i_boundary}, "
                f"Q={q_boundary}"
            )

    print()
    print(
        "=" * 80
    )

    print(
        "V1.4 RAW IQ / FIXED-POINT VALIDATION COMPLETE"
    )

    print(
        "=" * 80
    )


if __name__ == "__main__":
    main()
