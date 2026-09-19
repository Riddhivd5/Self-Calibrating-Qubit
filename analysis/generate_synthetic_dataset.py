"""
Generate synthetic IQ datasets using IQDriftGenerator v1.4.

The output intentionally matches the real IBM NPZ structure:

    q0_state0
    q0_state1
    q1_state0
    q1_state1
    q2_state0
    q2_state1

Each array contains 1000 raw-scale complex IQ shots.

The generated raw values use the qubit-specific v1.4 profiles and the
Person 4-compatible 2**28 raw scale.

Output:
    data/synthetic/
        synthetic_000h.npz
        synthetic_024h.npz
        synthetic_048h.npz
        synthetic_072h.npz
        synthetic_096h.npz
        synthetic_120h.npz
        synthetic_144h.npz

No plots are produced by this script.
"""

from __future__ import annotations

from pathlib import Path
import sys

import numpy as np

# ---------------------------------------------------------------------
# Make project root importable when running from analysis/
# ---------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from iq_generator import IQDriftGenerator, DriftParams


# ---------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------

OUTPUT_DIR = PROJECT_ROOT / "data" / "synthetic"

N_SHOTS_PER_STATE = 1000

DRIFT_TIMES_HOURS = [
    0.0,
    24.0,
    48.0,
    72.0,
    96.0,
    120.0,
    144.0,
]

BASE_SEEDS = {
    "q0": 1000,
    "q1": 2000,
    "q2": 3000,
}


# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------

def make_generator(profile: str) -> IQDriftGenerator:
    """Create one persistent generator per qubit profile."""
    return IQDriftGenerator(
        DriftParams(
            drift_profile=profile,
            stochastic_drift_strength=1.0,
            rng_seed=BASE_SEEDS[profile],
        )
    )


def generate_state(
    generator: IQDriftGenerator,
    t_hours: float,
    state: int,
):
    """Generate exactly N_SHOTS_PER_STATE raw IQ samples for one state."""
    if state not in (0, 1):
        raise ValueError("state must be 0 or 1")

    # p_state1=0 -> every shot is state 0
    # p_state1=1 -> every shot is state 1
    p_state1 = float(state)

    raw_iq, true_states = generator.generate_shots_raw(
        n_shots=N_SHOTS_PER_STATE,
        t_hours=t_hours,
        p_state1=p_state1,
    )

    # Safety checks
    if raw_iq.shape != (N_SHOTS_PER_STATE,):
        raise RuntimeError(
            f"Unexpected IQ shape: {raw_iq.shape}"
        )

    if true_states.shape != (N_SHOTS_PER_STATE,):
        raise RuntimeError(
            f"Unexpected state shape: {true_states.shape}"
        )

    if not np.all(np.isfinite(raw_iq.real)):
        raise RuntimeError("Non-finite I values generated.")

    if not np.all(np.isfinite(raw_iq.imag)):
        raise RuntimeError("Non-finite Q values generated.")

    if not np.all(true_states == state):
        raise RuntimeError(
            f"Generator returned an unexpected state for state={state}."
        )

    return raw_iq.astype(np.complex128)


def generate_one_dataset(
    t_hours: float,
    generators: dict[str, IQDriftGenerator],
) -> dict[str, np.ndarray]:
    """Generate one six-channel dataset at one elapsed time."""
    dataset = {}

    for qubit_number in (0, 1, 2):
        profile = f"q{qubit_number}"
        generator = generators[profile]

        dataset[f"q{qubit_number}_state0"] = generate_state(
            generator,
            t_hours,
            0,
        )

        dataset[f"q{qubit_number}_state1"] = generate_state(
            generator,
            t_hours,
            1,
        )

    return dataset


def summarize_dataset(
    dataset: dict[str, np.ndarray],
    t_hours: float,
):
    """Print a compact raw-scale summary."""
    print(f"\nSynthetic dataset: t = {t_hours:.2f} h")

    global_max = 0.0

    for qubit_number in (0, 1, 2):
        state0 = dataset[f"q{qubit_number}_state0"]
        state1 = dataset[f"q{qubit_number}_state1"]

        for state_number, samples in ((0, state0), (1, state1)):
            max_abs = max(
                float(np.max(np.abs(samples.real))),
                float(np.max(np.abs(samples.imag))),
            )

            global_max = max(global_max, max_abs)

            print(
                f"  q{qubit_number}_state{state_number}: "
                f"I=[{samples.real.min():+.3e}, "
                f"{samples.real.max():+.3e}]  "
                f"Q=[{samples.imag.min():+.3e}, "
                f"{samples.imag.max():+.3e}]"
            )

        c0 = np.mean(state0)
        c1 = np.mean(state1)
        separation = abs(c1 - c0)

        print(
            f"  q{qubit_number} centroid separation: "
            f"{separation:.3e}"
        )

    print(
        f"  global max |I/Q|: {global_max:.3e}"
    )


# ---------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------

def main():
    print("=" * 78)
    print("SYNTHETIC IQ DATASET GENERATOR - v1.4")
    print("=" * 78)

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    print(f"\nOutput directory:")
    print(OUTPUT_DIR)

    print("\nGenerating profiles:")
    print("  Q0 -> q0")
    print("  Q1 -> q1")
    print("  Q2 -> q2")

    generators = {
        profile: make_generator(profile)
        for profile in ("q0", "q1", "q2")
    }

    print("\nDrift times:")
    print(
        "  "
        + ", ".join(
            f"{t:g} h"
            for t in DRIFT_TIMES_HOURS
        )
    )

    print(
        f"\nShots per state: {N_SHOTS_PER_STATE}"
    )

    created_files = []

    for t_hours in DRIFT_TIMES_HOURS:
        dataset = generate_one_dataset(
            t_hours=t_hours,
            generators=generators,
        )

        filename = (
            f"synthetic_{int(round(t_hours)):03d}h.npz"
        )

        output_path = OUTPUT_DIR / filename

        np.savez(
            output_path,
            **dataset,
        )

        created_files.append(output_path)

        summarize_dataset(
            dataset,
            t_hours,
        )

        print(
            f"  Saved: {output_path.name}"
        )

    # ---------------------------------------------------------------
    # Final verification
    # ---------------------------------------------------------------

    print("\n" + "=" * 78)
    print("FINAL VERIFICATION")
    print("=" * 78)

    for output_path in created_files:
        data = np.load(output_path)

        expected_keys = {
            "q0_state0",
            "q0_state1",
            "q1_state0",
            "q1_state1",
            "q2_state0",
            "q2_state1",
        }

        actual_keys = set(data.files)

        if actual_keys != expected_keys:
            raise RuntimeError(
                f"{output_path.name} has unexpected keys: "
                f"{sorted(actual_keys)}"
            )

        for key in sorted(expected_keys):
            array = data[key]

            if array.shape != (N_SHOTS_PER_STATE,):
                raise RuntimeError(
                    f"{output_path.name}:{key} has shape "
                    f"{array.shape}"
                )

            if array.dtype != np.complex128:
                raise RuntimeError(
                    f"{output_path.name}:{key} has dtype "
                    f"{array.dtype}"
                )

            if not np.all(np.isfinite(array.real)):
                raise RuntimeError(
                    f"{output_path.name}:{key} contains non-finite I."
                )

            if not np.all(np.isfinite(array.imag)):
                raise RuntimeError(
                    f"{output_path.name}:{key} contains non-finite Q."
                )

        print(
            f"OK: {output_path.name} "
            f"({len(data.files)} channels × "
            f"{N_SHOTS_PER_STATE} shots)"
        )

    print("\n" + "=" * 78)
    print(
        f"GENERATED {len(created_files)} SYNTHETIC DATASETS SUCCESSFULLY"
    )
    print("=" * 78)


if __name__ == "__main__":
    main()
