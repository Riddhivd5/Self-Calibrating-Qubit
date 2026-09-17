# Synthetic IQ Handoff — Person 2

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

- synthetic_000h.npz
- synthetic_024h.npz
- synthetic_048h.npz
- synthetic_072h.npz
- synthetic_096h.npz
- synthetic_120h.npz
- synthetic_144h.npz

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
