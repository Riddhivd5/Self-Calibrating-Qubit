from qiskit import QuantumCircuit
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager

from pathlib import Path
from datetime import datetime, timezone
import numpy as np
import json
import sys


# ============================================================
# EXPERIMENT CONFIGURATION
# ============================================================

BACKEND_NAME = "ibm_fez"

QUBITS = [0, 1, 2]

SHOTS = 1000


# ============================================================
# DATA DIRECTORY
# ============================================================

data_dir = Path("data")
data_dir.mkdir(exist_ok=True)


# ============================================================
# TIMESTAMP
# ============================================================

timestamp = datetime.now(timezone.utc)

timestamp_str = timestamp.strftime(
    "%Y-%m-%d_%H-%M-%S"
)


# ============================================================
# START
# ============================================================

print("=" * 60)
print("SELF-CALIBRATING QUBIT READOUT")
print("Real IQ Data Collection")
print("=" * 60)

print(f"Timestamp: {timestamp.isoformat()}")
print(f"Backend: {BACKEND_NAME}")
print(f"Qubits: {QUBITS}")
print(f"Shots per circuit: {SHOTS}")


# ============================================================
# CONNECT TO IBM QUANTUM
# ============================================================

try:
    service = QiskitRuntimeService()

    backend = service.backend(BACKEND_NAME)

except Exception as e:
    print(f"ERROR: Could not connect to IBM Quantum:")
    print(e)

    print("Collection attempt skipped.")
    sys.exit(1)


print(f"Connected to {BACKEND_NAME}")


# ============================================================
# CREATE CIRCUITS
# ============================================================

circuits = []

for q in QUBITS:

    # --------------------------------------------------------
    # Prepare |0>
    # --------------------------------------------------------

    qc0 = QuantumCircuit(3, 1)

    qc0.measure(q, 0)

    circuits.append(qc0)


    # --------------------------------------------------------
    # Prepare |1>
    # --------------------------------------------------------

    qc1 = QuantumCircuit(3, 1)

    qc1.x(q)

    qc1.measure(q, 0)

    circuits.append(qc1)


print(f"Created {len(circuits)} circuits")


# ============================================================
# TRANSPILATION
# ============================================================

try:

    pm = generate_preset_pass_manager(
        backend=backend,
        optimization_level=1
    )

    isa_circuits = pm.run(circuits)

except Exception as e:

    print("ERROR: Circuit transpilation failed:")
    print(e)

    sys.exit(1)


print("Circuits transpiled")


# ============================================================
# SAMPLER
# ============================================================

sampler = Sampler(mode=backend)

sampler.options.execution.meas_type = "kerneled"

print(
    f"Measurement mode: "
    f"{sampler.options.execution.meas_type}"
)


# ============================================================
# SUBMIT JOB
# ============================================================

try:

    job = sampler.run(
        isa_circuits,
        shots=SHOTS
    )

except Exception as e:

    print("ERROR: Could not submit job:")
    print(e)

    print("Collection attempt skipped.")
    sys.exit(1)


print(f"Job submitted: {job.job_id()}")

print("Waiting for job to complete...")


# ============================================================
# WAIT FOR RESULT
# ============================================================

try:

    result = job.result()

except Exception as e:

    print("ERROR: Job failed or could not be retrieved:")
    print(e)

    print("No IQ data will be saved.")

    sys.exit(1)


print("Job completed")


# ============================================================
# QPU USAGE
# ============================================================

try:

    usage = job.usage()

    print(f"QPU usage: {usage} seconds")

except Exception as e:

    usage = None

    print(
        "WARNING: Could not retrieve QPU usage:"
    )

    print(e)


# ============================================================
# EXTRACT IQ DATA
# ============================================================

iq_data = {}


for i, pub_result in enumerate(result):

    # Get complex IQ samples
    iq = pub_result.data.c.flatten()

    # Determine which qubit this circuit belongs to
    qubit = QUBITS[i // 2]

    # Determine prepared state
    state = 0 if i % 2 == 0 else 1

    key = f"q{qubit}_state{state}"

    iq_data[key] = iq

    print(
        f"{key}: "
        f"{len(iq)} IQ points"
    )


# ============================================================
# SAVE IQ DATA
# ============================================================

iq_file = (
    data_dir /
    f"iq_{timestamp_str}.npz"
)

np.savez_compressed(
    iq_file,
    **iq_data
)

print(f"IQ data saved to: {iq_file}")


# ============================================================
# GET CALIBRATION METADATA
# ============================================================

calibration = {}

try:

    properties = job.properties()

    for q in QUBITS:

        calibration[f"q{q}"] = {

            "T1_seconds":
                properties.t1(q),

            "T2_seconds":
                properties.t2(q),

            "readout_error":
                properties.readout_error(q),

            "readout_length_seconds":
                properties.readout_length(q)
        }


    calibration["last_update"] = (
        str(properties.last_update_date)
    )

    print("Calibration metadata retrieved")


except Exception as e:

    print(
        "WARNING: Could not retrieve "
        "calibration metadata:"
    )

    print(e)

    calibration = {}


# ============================================================
# CREATE METADATA RECORD
# ============================================================

metadata = {

    "timestamp_utc":
        timestamp.isoformat(),

    "backend":
        BACKEND_NAME,

    "job_id":
        job.job_id(),

    "qubits":
        QUBITS,

    "shots_per_circuit":
        SHOTS,

    "circuits":
        len(circuits),

    "total_iq_points":
        len(QUBITS) * 2 * SHOTS,

    "measurement_type":
        "kerneled",

    "qpu_usage_seconds":
        usage,

    "calibration":
        calibration
}


# ============================================================
# SAVE METADATA
# ============================================================

metadata_file = (
    data_dir /
    f"metadata_{timestamp_str}.json"
)


with open(metadata_file, "w") as f:

    json.dump(
        metadata,
        f,
        indent=4,
        default=str
    )


print(
    f"Metadata saved to: {metadata_file}"
)


# ============================================================
# FINISHED
# ============================================================

print("=" * 60)
print("COLLECTION COMPLETE")
print("=" * 60)