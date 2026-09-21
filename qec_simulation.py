import stim
import pymatching
import numpy as np
import matplotlib.pyplot as plt


def run_ler_simulation(distance, readout_error,shots=20000):

    # Create the rotated surface-code circuit
    circuit = stim.Circuit.generated(
        "surface_code:rotated_memory_z",
        distance=distance,
        rounds=distance,
        before_measure_flip_probability=readout_error
    )

    # Create the detector error model
    dem = circuit.detector_error_model()

    # Create the PyMatching decoder
    matching = pymatching.Matching.from_detector_error_model(dem)

    # Sample detector and logical-observable data
    sampler = circuit.compile_detector_sampler()

    detector_results, observable_results = sampler.sample(
        shots,
        separate_observables=True
    )

    # Decode the detector results
    predictions = matching.decode_batch(detector_results)

    # Convert to 1D arrays
    predictions = np.asarray(predictions).reshape(-1)
    actual = np.asarray(observable_results).reshape(-1)

    # Compare predicted and actual logical outcomes
    logical_errors = predictions != actual

    # Count logical failures
    logical_failures = np.sum(logical_errors)

    # Calculate Logical Error Rate
    ler = logical_failures / shots

    return ler, logical_failures


drift_rates = [0.01, 0.012, 0.015, 0.020, 0.025]
shots_per_period = 2000


# Store results for plotting
all_ler_results = {}


# Run simulation for d=3 and d=5
for distance in [3, 5]:

    print(f"\n========== d={distance} ==========")

    ler_rates = []

    for p in drift_rates:

        ler, failures = run_ler_simulation(
            distance=distance,
            readout_error=p,
            shots=2000
        )

        ler_rates.append(ler)

        print(
            f"Readout error = {p:.2%}"
            f" -> LER = {ler:.4%}"
            f" ({failures}/2000)"
        )

    all_ler_results[distance] = ler_rates
# --------------------------------------------------
# Plot LER curves
# --------------------------------------------------

plt.figure()

# --------------------------------------------------
# Plot LER curves under simulated drift
# --------------------------------------------------

plt.figure()

plt.plot(
    np.array(drift_rates) * 100,
    np.array(all_ler_results[3]) * 100,
    marker="o",
    label="d=3"
)

plt.plot(
    np.array(drift_rates) * 100,
    np.array(all_ler_results[5]) * 100,
    marker="o",
    label="d=5"
)

plt.xlabel("Readout Error (%)")
plt.ylabel("Logical Error Rate (%)")
plt.title("Logical Error Rate Under Simulated Readout Drift")
plt.legend()
plt.grid(True)

plt.show()
