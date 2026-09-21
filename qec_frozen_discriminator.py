
import stim
import pymatching
import numpy as np
import matplotlib.pyplot as plt
import math


# ==================================================
# FROZEN DISCRIMINATOR MODEL
# ==================================================

def frozen_discriminator_error(drift_fraction):
    """
    Simulate two IQ clouds separated by a fixed discriminator
    boundary.

    Initially the clouds are well separated.
    Drift moves both cloud centers toward the fixed boundary.
    """

    # Fixed discriminator boundary
    threshold = 0.0

    # Readout-cloud standard deviation
    sigma = 1.0

    # Initial distance of each cloud from the boundary
    initial_distance = 2.33

    # Final distance after simulated drift
    final_distance = 1.88

    # Cloud distance from frozen boundary
    distance = (
        initial_distance
        - drift_fraction * (initial_distance - final_distance)
    )

    # Probability that a Gaussian cloud crosses the fixed boundary
    error_probability = 0.5 * math.erfc(
        distance / (sigma * math.sqrt(2))
    )

    return error_probability


# ==================================================
# ONE QEC SHOT
# ==================================================

def run_single_shot(distance, readout_error):

    circuit = stim.Circuit.generated(
        "surface_code:rotated_memory_z",
        distance=distance,
        rounds=distance,
        before_measure_flip_probability=readout_error
    )

    dem = circuit.detector_error_model()

    matching = pymatching.Matching.from_detector_error_model(dem)

    sampler = circuit.compile_detector_sampler()

    detector_results, observable_results = sampler.sample(
        1,
        separate_observables=True
    )

    prediction = matching.decode_batch(detector_results)

    prediction = np.asarray(prediction).reshape(-1)
    actual = np.asarray(observable_results).reshape(-1)

    logical_error = prediction[0] != actual[0]

    return logical_error


# ==================================================
# SIMULATED DRIFT
# ==================================================

total_shots = 5000

# Drift goes from 0% to 100% of our simulated drift range
drift_profile = np.linspace(0.0, 1.0, total_shots)


# ==================================================
# SHOW READOUT ERROR CAUSED BY FROZEN DISCRIMINATOR
# ==================================================

readout_errors = np.array([
    frozen_discriminator_error(d)
    for d in drift_profile
])

print("\n======================================")
print("FROZEN DISCRIMINATOR DRIFT")
print("======================================")

print(
    f"Initial readout error = "
    f"{readout_errors[0] * 100:.2f}%"
)

print(
    f"Final readout error = "
    f"{readout_errors[-1] * 100:.2f}%"
)


# ==================================================
# RUN QEC
# ==================================================

all_ler_over_time = {}

window_size = 500

for distance in [3, 5]:

    print("\n======================================")
    print(f"Surface Code: d={distance}")
    print(f"Total shots: {total_shots}")
    print("======================================")

    logical_errors = []

    for shot_number, readout_error in enumerate(readout_errors):

        error = run_single_shot(
            distance=distance,
            readout_error=readout_error
        )

        logical_errors.append(error)

        if (shot_number + 1) % 500 == 0:

            print(
                f"Completed {shot_number + 1}/{total_shots} "
                f"shots "
                f"(readout error = "
                f"{readout_error * 100:.2f}%)"
            )

    logical_errors = np.array(
        logical_errors,
        dtype=int
    )

    # ==============================================
    # WINDOWED LER
    # ==============================================

    windowed_ler = []

    for start in range(
        0,
        total_shots,
        window_size
    ):

        end = start + window_size

        window_errors = logical_errors[start:end]

        ler = np.mean(window_errors)

        windowed_ler.append(ler)

    all_ler_over_time[distance] = windowed_ler


# ==================================================
# PLOT LER UNDER FROZEN DISCRIMINATOR DRIFT
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

plt.title(
    "LER Under Frozen Discriminator and Simulated Drift"
)

plt.legend()
plt.grid(True)

plt.show()
