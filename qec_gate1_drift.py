
import stim
import pymatching
import numpy as np
import matplotlib.pyplot as plt


def run_single_shot(distance, readout_error):
    """
    Run ONE QEC shot with its own readout-error probability.
    """

    # Create surface-code circuit
    circuit = stim.Circuit.generated(
        "surface_code:rotated_memory_z",
        distance=distance,
        rounds=distance,
        before_measure_flip_probability=readout_error
    )

    # Detector Error Model
    dem = circuit.detector_error_model()

    # PyMatching decoder
    matching = pymatching.Matching.from_detector_error_model(dem)

    # Run one shot
    sampler = circuit.compile_detector_sampler()

    detector_results, observable_results = sampler.sample(
        1,
        separate_observables=True
    )

    # Decode
    prediction = matching.decode_batch(detector_results)

    prediction = np.asarray(prediction).reshape(-1)
    actual = np.asarray(observable_results).reshape(-1)

    # Did this shot have a logical error?
    logical_error = prediction[0] != actual[0]

    return logical_error


# ==================================================
# SIMULATED DRIFT
# ==================================================

# Total number of shots
total_shots = 5000

# Readout error starts at 1% and gradually drifts to 2.5%
drift_rates = np.linspace(0.01, 0.025, total_shots)


# ==================================================
# RUN d=3 AND d=5
# ==================================================

all_ler_over_time = {}

window_size = 500

for distance in [3, 5]:

    print("\n==============================")
    print(f"Surface Code: d={distance}")
    print(f"Total shots: {total_shots}")
    print("==============================")

    logical_errors = []

    for shot_number, p in enumerate(drift_rates):

        error = run_single_shot(
            distance=distance,
            readout_error=p
        )

        logical_errors.append(error)

        if (shot_number + 1) % 500 == 0:
            print(
                f"Completed {shot_number + 1}/{total_shots} shots "
                f"(current readout error = {p:.2%})"
            )

    # Convert logical-error results to NumPy array
    logical_errors = np.array(logical_errors, dtype=int)

    # ==================================================
    # WINDOWED LER
    # ==================================================

    windowed_ler = []

    for start in range(0, total_shots, window_size):

        end = start + window_size

        window_errors = logical_errors[start:end]

        ler = np.mean(window_errors)

        windowed_ler.append(ler)

    # Store results for this distance
    all_ler_over_time[distance] = windowed_ler


# ==================================================
# PLOT WINDOWED LER
# ==================================================

window_numbers = np.arange(
    1,
    len(all_ler_over_time[3]) + 1
)

plt.figure(figsize=(9, 6))

plt.plot(
    window_numbers,
    np.array(all_ler_over_time[3]) * 100,
    marker="o",
    label="d=3"
)

plt.plot(
    window_numbers,
    np.array(all_ler_over_time[5]) * 100,
    marker="o",
    label="d=5"
)

plt.xlabel("Drift Window (500 shots)")
plt.ylabel("Logical Error Rate (%)")
plt.title("Logical Error Rate Under Simulated Readout Drift")
plt.legend()
plt.grid(True)

plt.show()
