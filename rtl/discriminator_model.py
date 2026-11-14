"""
discriminator_model.py -- bit-exact and cycle-accurate Python model of rtl/discriminator.v.

Arithmetic (all integers; I, Q and the coefficients are Q1.15 signed 16-bit):
    sum = I * a + Q * b + (c << 15)          # Q2.30, held in 34 bits in the RTL
    state = 1 if sum >= 0 else 0
Note: the RTL takes the sign bit of the sum, so a sum of exactly zero gives state 1. The header comment of discriminator.v
says "a*I + b*Q + c > 0 -> state 1"; the two differ only when the sum is exactly zero. This model follows the RTL.

Pipeline: 3 registered stages with a synchronous active-low reset. `simulate` reproduces valid_out and state_bit after every
rising clock edge, including reset and coefficient changes (coefficients travel down the pipeline with their sample).
"""
import numpy as np

FRAC_BITS = 15
LATENCY = 3   # clock edges from a sample being presented with valid_in to its state_bit appearing with valid_out


def classify(i, q, a, b, c):
    """Vectorised bit-exact decision for int arrays (any shape, broadcastable)."""
    s = np.asarray(i, np.int64) * np.asarray(a, np.int64) + np.asarray(q, np.int64) * np.asarray(b, np.int64) + (np.asarray(c, np.int64) << FRAC_BITS)
    return (s >= 0).astype(np.uint8)


def boundary_to_q15(c0, c1, scale):
    """Perpendicular-bisector boundary of two centroids (complex, raw units) as Q1.15 coefficients (a, b, c).
    Decision in normalised units: a*I + b*Q + c > 0 -> state 1, with (a, b) = (c1 - c0) scaled so max(|a|, |b|) is just under 1."""
    w = (c1 - c0) / scale
    mid = (c0 + c1) / 2 / scale
    k = 0.999 / max(abs(w.real), abs(w.imag))
    a, b = w.real * k, w.imag * k
    c = -(mid.real * a + mid.imag * b)
    q = lambda x: int(np.clip(np.round(x * 2 ** FRAC_BITS), -2 ** 15, 2 ** 15 - 1))
    return q(a), q(b), q(c), (a, b, c)


def simulate(rst_n, valid, i, q, a, b, c):
    """Cycle-accurate model. All arguments are equal-length integer arrays, one entry per clock cycle (values applied before
    the rising edge). Returns (valid_out, state_bit) as seen after each rising edge."""
    n = len(rst_n)
    rst_n = np.asarray(rst_n, bool)
    # stage 1 and stage 2 valid bits are cleared by reset; stage 3 output is cleared by reset
    v1 = np.where(rst_n, np.asarray(valid, np.uint8), 0)
    r1 = rst_n
    # stage 2 registers what stage 1 held before this edge
    v2 = np.zeros(n, np.uint8); v2[1:] = v1[:-1]; v2 = np.where(rst_n, v2, 0)
    # data registered in stage 1 at each edge (zero under reset)
    z = lambda x: np.where(r1, np.asarray(x, np.int64), 0)
    i1, q1, a1, b1, c1 = z(i), z(q), z(a), z(b), z(c)
    pa = np.zeros(n, np.int64); pb = np.zeros(n, np.int64); c2 = np.zeros(n, np.int64)
    pa[1:] = i1[:-1] * a1[:-1]; pb[1:] = q1[:-1] * b1[:-1]; c2[1:] = c1[:-1]
    pa, pb, c2 = np.where(rst_n, pa, 0), np.where(rst_n, pb, 0), np.where(rst_n, c2, 0)
    vout = np.zeros(n, np.uint8); st = np.zeros(n, np.uint8)
    s = pa + pb + (c2 << FRAC_BITS)
    vout[1:] = v2[:-1]; st[1:] = (s[:-1] >= 0)
    vout, st = np.where(rst_n, vout, 0), np.where(rst_n, st, 0)
    return vout.astype(np.uint8), st.astype(np.uint8)
