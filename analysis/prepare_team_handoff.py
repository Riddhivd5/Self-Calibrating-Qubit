"""
Prepare a clean Person 3 / Person 4 handoff from the validated v1.5
synthetic IQ datasets.

INPUT:
    data/synthetic/synthetic_*.npz

OUTPUT:
    data/handoff/
        raw/
            synthetic_000h.npz
            ...
        normalized/
            synthetic_000h.npz
            ...
        handoff_metadata.json
        README_HANDOFF.md

Raw files:
    Same raw IQ representation used by Person 4.
    raw IQ is approximately ±1e8 and uses the 2**28 scale.

Normalized files:
    raw / 2**28
    These are convenient for Person 3's software/QEC analysis.

Each dataset contains:
    q0_state0
    q0_state1
    q1_state0
    q1_state1
    q2_state0
    q2_state1

Each channel:
    shape = (1000,)
    dtype = complex128

The script also opens one sanity-check figure comparing the first and
last synthetic datasets in normalized coordinates.
"""

from __future__ import annotations

from pathlib import Path
import json
import re

import numpy as np
import matplotlib.pyplot as plt


# ---------------------------------------------------------------------
# Paths / constants
# ---------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

SYNTHETIC_DIR = PROJECT_ROOT / "data" / "synthetic"
HANDOFF_DIR = PROJECT_ROOT / "data" / "handoff"

RAW_DIR = HANDOFF_DIR / "raw"
NORMALIZED_DIR = HANDOFF_DIR / "normalized"

RAW_IQ_SCALE = 2 ** 28

EXPECTED_KEYS = {
    "q0_state0",
    "q0_state1",
    "q1_state0",
    "q1_state1",
    "q2_state0",
    "q2_state1",
}

FILE_RE = re.compile(
    r"synthetic_(\d+)h\.npz$"
)


# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------

def find_synthetic_files() -> list[Path]:
    files = sorted(
        SYNTHETIC_DIR.glob("synthetic_*.npz")
    )

    if not files:
        raise FileNotFoundError(
            f"No synthetic NPZ files found in {SYNTHETIC_DIR}"
        )

    def time_key(path: Path) -> int:
        match = FILE_RE.fullmatch(path.name)
        if match is None:
            raise ValueError(
                f"Unexpected synthetic filename: {path.name}"
            )
        return int(match.group(1))

    files.sort(key=time_key)
    return files


def load_and_validate(path: Path) -> dict[str, np.ndarray]:
    data = np.load(path)

    if set(data.files) != EXPECTED_KEYS:
        raise ValueError(
            f"{path.name} has unexpected keys.\n"
            f"Expected: {sorted(EXPECTED_KEYS)}\n"
            f"Found:    {sorted(data.files)}"
        )

    result = {}

    for key in sorted(EXPECTED_KEYS):
        arr = np.asarray(
            data[key],
            dtype=np.complex128,
        )

        if arr.shape != (1000,):
            raise ValueError(
                f"{path.name}:{key} has shape {arr.shape}; "
                "expected (1000,)"
            )

        if not np.all(np.isfinite(arr.real)):
            raise ValueError(
                f"{path.name}:{key} contains non-finite I values"
            )

        if not np.all(np.isfinite(arr.imag)):
            raise ValueError(
                f"{path.name}:{key} contains non-finite Q values"
            )

        result[key] = arr

    return result


def elapsed_hours_from_name(path: Path) -> float:
    match = FILE_RE.fullmatch(path.name)

    if match is None:
        raise ValueError(
            f"Cannot parse time from {path.name}"
        )

    return float(match.group(1))


def centroid(data: dict[str, np.ndarray], qubit: int, state: int):
    return np.mean(
        data[f"q{qubit}_state{state}"]
    )


def plot_sanity_check(
    first_raw: dict[str, np.ndarray],
    last_raw: dict[str, np.ndarray],
    first_name: str,
    last_name: str,
):
    fig, axes = plt.subplots(
        2,
        3,
        figsize=(18, 10),
    )

    first_norm = {
        key: value / RAW_IQ_SCALE
        for key, value in first_raw.items()
    }

    last_norm = {
        key: value / RAW_IQ_SCALE
        for key, value in last_raw.items()
    }

    for col, qubit in enumerate((0, 1, 2)):
        # Initial
        ax = axes[0, col]

        for state in (0, 1):
            samples = first_norm[
                f"q{qubit}_state{state}"
            ]

            ax.scatter(
                samples.real,
                samples.imag,
                s=8,
                alpha=0.3,
                label=f"state {state}",
            )

        ax.set_title(
            f"Q{qubit} — {first_name}"
        )
        ax.set_xlabel("I / 2^28")
        ax.set_ylabel("Q / 2^28")
        ax.grid(True, alpha=0.3)
        ax.legend()

        # Final
        ax = axes[1, col]

        for state in (0, 1):
            samples = last_norm[
                f"q{qubit}_state{state}"
            ]

            ax.scatter(
                samples.real,
                samples.imag,
                s=8,
                alpha=0.3,
                label=f"state {state}",
            )

        ax.set_title(
            f"Q{qubit} — {last_name}"
        )
        ax.set_xlabel("I / 2^28")
        ax.set_ylabel("Q / 2^28")
        ax.grid(True, alpha=0.3)
        ax.legend()

    fig.suptitle(
        "Synthetic v1.5 Team-Handoff Sanity Check"
    )
    fig.tight_layout()


def write_readme(files: list[Path]):
    readme = f"""# Synthetic IQ Handoff — Person 2

Generated from the validated **IQDriftGenerator v1.5**.

## Files

- `raw/` — raw IQ data for the Person 4 hardware/fixed-point pipeline.
- `normalized/` — the same data divided by `2^28`, convenient for software/QEC analysis.
- `handoff_metadata.json` — dataset list and representation details.

## Dataset structure

Each `.npz` contains exactly six channels:

- `q0_state0`
- `q0_state1`
- `q1_state0`
- `q1_state1`
- `q2_state0`
- `q2_state1`

Each channel contains **1000 complex IQ shots**.

## Representation

### Raw

Raw values are in the same arbitrary-unit representation used by Person 4.

```text
normalized value = raw / 2^28
```

### Normalized

The normalized files are simply:

```text
normalized = raw / 2^28
```

Do not apply the `2^28` conversion a second time.

## Generated datasets

{chr(10).join(f"- {p.name}" for p in files)}

## Intended use

### Person 3

Use the files in:

```text
data/handoff/normalized/
```

for readout/QEC software experiments.

### Person 4

Use the files in:

```text
data/handoff/raw/
```

for the raw-IQ to Q1.15 fixed-point pipeline.

## Important

These synthetic datasets are a calibrated simulation, not a replacement for the
real IBM measurements. They reproduce the project's modeled qubit-specific
noise and drift behavior and provide repeatable inputs for downstream testing.
"""

    (HANDOFF_DIR / "README_HANDOFF.md").write_text(
        readme,
        encoding="utf-8",
    )


# ---------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------

def main():
    print("=" * 78)
    print("PERSON 3 / PERSON 4 SYNTHETIC IQ HANDOFF")
    print("=" * 78)

    files = find_synthetic_files()

    print(f"\nFound {len(files)} synthetic datasets.")

    RAW_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    NORMALIZED_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    metadata = {
        "generator_version": "1.5",
        "raw_iq_scale": RAW_IQ_SCALE,
        "shots_per_state": 1000,
        "channels_per_dataset": 6,
        "qubit_profiles": {
            "q0": "q0",
            "q1": "q1",
            "q2": "q2",
        },
        "datasets": [],
    }

    loaded = {}

    for source_path in files:
        raw_data = load_and_validate(
            source_path
        )

        loaded[source_path.name] = raw_data

        raw_output = RAW_DIR / source_path.name
        normalized_output = (
            NORMALIZED_DIR / source_path.name
        )

        # Raw handoff copy.
        np.savez(
            raw_output,
            **raw_data,
        )

        # Normalized handoff copy.
        normalized_data = {
            key: value / RAW_IQ_SCALE
            for key, value in raw_data.items()
        }

        np.savez(
            normalized_output,
            **normalized_data,
        )

        dataset_record = {
            "filename": source_path.name,
            "elapsed_hours": elapsed_hours_from_name(
                source_path
            ),
            "raw_file": str(
                raw_output.relative_to(PROJECT_ROOT)
            ),
            "normalized_file": str(
                normalized_output.relative_to(PROJECT_ROOT)
            ),
        }

        metadata["datasets"].append(
            dataset_record
        )

        print(
            f"OK: {source_path.name} "
            f"-> raw + normalized"
        )

    # Write metadata and README.
    (HANDOFF_DIR / "handoff_metadata.json").write_text(
        json.dumps(
            metadata,
            indent=4,
        ),
        encoding="utf-8",
    )

    write_readme(files)

    # Sanity checks for the first and last datasets.
    first_file = files[0]
    last_file = files[-1]

    first_raw = loaded[first_file.name]
    last_raw = loaded[last_file.name]

    print("\n" + "=" * 78)
    print("HANDOFF DIRECTORY")
    print("=" * 78)
    print(HANDOFF_DIR)

    print("\nRaw:")
    print(RAW_DIR)

    print("\nNormalized:")
    print(NORMALIZED_DIR)

    print("\nMetadata:")
    print(HANDOFF_DIR / "handoff_metadata.json")

    print("\nREADME:")
    print(HANDOFF_DIR / "README_HANDOFF.md")

    print("\n" + "=" * 78)
    print("SANITY CHECK")
    print("=" * 78)

    for qubit in (0, 1, 2):
        first_sep = abs(
            centroid(first_raw, qubit, 1)
            - centroid(first_raw, qubit, 0)
        )

        last_sep = abs(
            centroid(last_raw, qubit, 1)
            - centroid(last_raw, qubit, 0)
        )

        print(
            f"Q{qubit}: "
            f"separation {first_file.name} = {first_sep:.3e}, "
            f"{last_file.name} = {last_sep:.3e}"
        )

    plot_sanity_check(
        first_raw,
        last_raw,
        first_file.name.replace(".npz", ""),
        last_file.name.replace(".npz", ""),
    )

    print("\n" + "=" * 78)
    print("TEAM HANDOFF PREPARATION COMPLETE")
    print("=" * 78)
    print("Raw files are ready for Person 4.")
    print("Normalized files are ready for Person 3.")
    print("Close the graph window when finished.")

    plt.show()


if __name__ == "__main__":
    main()
