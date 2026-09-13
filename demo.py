"""
demo.py

Quick visual sanity check: plots the fake IQ clouds at a few
different timestamps to confirm drift is behaving as expected.
Run this directly: python demo.py
"""

import matplotlib.pyplot as plt
from iq_generator import IQDriftGenerator

def main():
    gen = IQDriftGenerator()

    fig, axes = plt.subplots(1, 3, figsize=(15, 5), sharex=True, sharey=True)
    for ax, t in zip(axes, [0, 6, 24]):
        iq, states = gen.generate_shots(n_shots=3000, t_hours=t)
        ax.scatter(iq[states == 0].real, iq[states == 0].imag, s=3, alpha=0.4, label="prep |0>")
        ax.scatter(iq[states == 1].real, iq[states == 1].imag, s=3, alpha=0.4, label="prep |1>")
        ax.set_title(f"t = {t} hr")
        ax.set_xlabel("I")
        ax.set_aspect("equal")

    axes[0].set_ylabel("Q")
    axes[0].legend(markerscale=4)
    fig.suptitle("Fake IQ readout clouds drifting over time")
    fig.tight_layout()
    fig.savefig("drift_demo.png", dpi=150)
    print("Saved drift_demo.png")

if __name__ == "__main__":
    main()