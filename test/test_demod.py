# Tests for lib.math.demod.DemodulatorComplex against a synthetic buffer
# shaped exactly like the one Keysight_DIG.take_avg_shot() feeds it: a flat
# concatenation of naverages shots, each nsamples long, with a known
# IF tone of known amplitude/phase per shot.

from __future__ import annotations

import os
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from lib.math import demod  # noqa: E402


def _make_buffer(naverages, nsamples, if_period, amplitudes, phases):
    """Build a flat buffer of naverages shots, each containing a pure
    cosine at one cycle per if_period samples, with per-shot amplitude
    and phase. Matches the layout DAQbufferGet() returns to take_avg_shot.
    """
    t = np.arange(nsamples)
    # DAQbufferGet returns float32 samples; np.dot(float32, complex64) stays
    # complex64, matching the demodulator's `out=self.IQ` dtype. float64
    # input would promote to complex128 and the out= write would fail.
    buf = np.zeros(naverages * nsamples, dtype=np.float32)
    for shot in range(naverages):
        omega = 2 * np.pi / if_period
        buf[shot * nsamples : (shot + 1) * nsamples] = amplitudes[shot] * np.cos(
            omega * t + phases[shot]
        )
    return buf


def test_demodulator_complex_recovers_amplitude_and_phase():
    naverages = 5
    nsamples = 40
    if_period = 20  # 2 IF cycles per shot

    rng = np.random.default_rng(0)
    amplitudes = rng.uniform(0.5, 2.0, size=naverages)
    phases = rng.uniform(-np.pi, np.pi, size=naverages)

    buf = _make_buffer(naverages, nsamples, if_period, amplitudes, phases)

    demodulator = demod.DemodulatorComplex(naverages * nsamples, if_period, avg_periods=1)
    demodulator.demodulate(buf)

    # Same reshape Keysight_DIG.take_avg_shot does to go from the flat
    # per-IF-cycle IQ stream back to a (shot, time-within-shot) grid.
    IQ = demodulator.IQ.reshape([naverages, nsamples // if_period])

    # demodulate() sums (does not average) cos(omega*t+phi)*exp(i*omega*t)
    # over one full IF period (samples_per_point samples, since avg_periods=1
    # here means no extra /period normalization beyond the /avg_periods in
    # _exp_iphi). For a tone at exactly the demod frequency, that sum equals
    # (A * if_period / 2) * exp(-i*phi), since cos = (e^{i*x}+e^{-i*x})/2 and
    # only the matching-frequency term survives the sum over a full cycle.
    expected_mag = amplitudes * if_period / 2
    expected_phase = -phases

    recovered_mag = np.abs(IQ).mean(axis=1)
    recovered_phase = np.angle(IQ).mean(axis=1)

    np.testing.assert_allclose(recovered_mag, expected_mag, rtol=1e-3)
    np.testing.assert_allclose(
        np.angle(np.exp(1j * (recovered_phase - expected_phase))), 0, atol=1e-3
    )


def test_demodulator_complex_rejects_misaligned_buffer_length():
    with pytest.raises(ValueError):
        demod.DemodulatorComplex(nsamples=37, period=20, avg_periods=1)
