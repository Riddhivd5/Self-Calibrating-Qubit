import glob
import json
import numpy as np
import stim
import pymatching
import matplotlib.pyplot as plt


# ============================================================
# 1. READ REAL IBM CALIBRATION DATA
# ============================================================

metadata_files = glob.glob("data/metadata_*.json")

real_data = []

for filename in metadata_files:
    with open(filename, "r") as f:
        metadata = json.load(f)

    timestamp = metadata["timestamp_utc"]
    calibration = metadata["calibration"]

    errors = [
        calibration["q0"]["readout_error"],
        calibration["q1"]["readout_error"],
        calibration["q2"]["readout_error"],
    ]

    # Use the mean readout error across q0, q1 and q2
    mean_error = np.mean(errors)

    real_data.append((timestamp, mean_error, errors))


# Sort chronologically
real_data.sort(key=lambda x: x[0])

print("\nREAL IBM DATA")
print("=" * 60)
print("Number of datasets:", len(real_data))

print("\nFirst measurement:")
print(real_data[0][0])
print("q0/q1/q2:",
      [round(x * 100, 3) for x in real_data[0][2]])

print("\nLast measurement:")
print(real_data[-1][0])
print("q0/q1/q2:",
      [round(x * 100, 3) for x in real_data[-1][2]])


# ============================================================
# 2. EXTRACT REAL READOUT-ERROR TRAJECTORY
# ============================================================

real_errors = np.array([x[1] for x in real_data])

print("\nMean readout error across all datasets:")
print("Minimum:", round(real_errors.min() * 100, 3), "%")
print("Maximum:", round(real_errors.max() * 100, 3), "%")
print("Range:",
      round((real_errors.max() - real_errors.min()) * 100, 3),
      "percentage points")


# ============================================================
# 3. PLOT REAL READOUT ERROR VS DATASET TIME
# ============================================================

timestamps = np.arange(len(real_errors))

plt.figure(figsize=(10, 5))

plt.plot(
    timestamps,
    real_errors * 100,
    marker="o",
    markersize=3
)

plt.xlabel("Dataset index (chronological)")
plt.ylabel("Mean readout error (%)")
plt.title("Real IBM Readout Error Variation")

plt.grid(True, alpha=0.3)
plt.tight_layout()

plt.savefig(
    "gate1_real_readout_drift.png",
    dpi=200
)

plt.show()


# ============================================================
# 4. BUILD A REAL-DRIFT PROFILE FOR QEC REPLAY
# ============================================================

# Interpolate the 68 real calibration measurements
# across a fixed number of QEC shots.

TOTAL_SHOTS = 5000

shot_positions = np.linspace(
    0,
    len(real_errors) - 1,
    TOTAL_SHOTS
)

real_drift_profile = np.interp(
    shot_positions,
    np.arange(len(real_errors)),
    real_errors
)


# ============================================================
# 5. RUN ONE QEC SHOT
# ============================================================

def run_single_shot(distance, readout_error):

    circuit = stim.Circuit.generated(
        "surface_code:rotated_memory_z",
        distance=distance,
        rounds=distance,
        before_measure_flip_probability=readout_error
    )

    dem = circuit.detector_error_model()

    matching = pymatching.Matching.from_detector_error_model(
        dem
    )

    sampler = circuit.compile_detector_sampler()

    detector_results, observable_results = sampler.sample(
        1,
        separate_observables=True
    )

    prediction = matching.decode_batch(
        detector_results
    )

    prediction = np.asarray(prediction).reshape(-1)

    actual = np.asarray(
        observable_results
    ).reshape(-1)

    return prediction[0] != actual[0]


# ============================================================
# 6. REPLAY REAL DRIFT THROUGH STIM + PYMATCHING
# ============================================================

def run_real_drift_replay(distance):

    logical_errors = []

    print(
        f"\nRunning real-drift replay for d={distance}..."
    )

    for shot, readout_error in enumerate(
        real_drift_profile
    ):

        logical_error = run_single_shot(
            distance,
            readout_error
        )

        logical_errors.append(logical_error)

        if (shot + 1) % 500 == 0:
            print(
                f"  completed {shot + 1}/{TOTAL_SHOTS}"
            )

    return np.array(logical_errors)


# ============================================================
# 7. RUN d=3 AND d=5
# ============================================================

results = {}

for distance in [3, 5]:

    errors = run_real_drift_replay(distance)

    results[distance] = errors


# ============================================================
# 8. CALCULATE WINDOWED LER
# ============================================================

WINDOW_SIZE = 500

window_centers = []
ler_results = {}

for distance in [3, 5]:

    logical_errors = results[distance]

    window_ler = []

    for start in range(
        0,
        TOTAL_SHOTS,
        WINDOW_SIZE
    ):

        end = min(
            start + WINDOW_SIZE,
            TOTAL_SHOTS
        )

        ler = np.mean(
            logical_errors[start:end]
        )

        window_ler.append(
            ler * 100
        )

    ler_results[distance] = window_ler

window_centers = np.arange(
    1,
    len(ler_results[3]) + 1
)


# ============================================================
# 9. PRINT RESULTS
# ============================================================

print("\n")
print("=" * 60)
print("GATE 1 REAL-DRIFT QEC REPLAY")
print("=" * 60)

for distance in [3, 5]:

    print(f"\nd={distance}")

    print(
        "Windowed LER (%):",
        [round(x, 3)
         for x in ler_results[distance]]
    )

    print(
        "Initial window LER:",
        round(ler_results[distance][0], 3),
        "%"
    )

    print(
        "Final window LER:",
        round(ler_results[distance][-1], 3),
        "%"
    )


# ============================================================
# 10. PLOT REAL-DRIFT LER
# ============================================================

plt.figure(figsize=(10, 5))

plt.plot(
    window_centers,
    ler_results[3],
    marker="o",
    label="d=3"
)

plt.plot(
    window_centers,
    ler_results[5],
    marker="o",
    label="d=5"
)

plt.xlabel("Chronological drift window")
plt.ylabel("Logical error rate (%)")

plt.title(
    "LER Under Real IBM Readout-Error Drift"
)

plt.legend()
plt.grid(True, alpha=0.3)

plt.tight_layout()

plt.savefig(
    "gate1_real_drift_ler.png",
    dpi=200
)

plt.show()
