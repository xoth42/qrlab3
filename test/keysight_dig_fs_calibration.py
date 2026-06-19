import json
import logging
import os
import sys

import matplotlib
import matplotlib.pyplot as plt
import numpy as np

"""
DIG sample-rate calibration ("Fs hack"): infers the DIG's true effective
sample rate by feeding a known tone from the AWG (trusted clock) into the
DIG and reading the FFT peak, rather than trusting clockGetFrequency().
Loopback wiring: AWG(slot8) ch1 -> DIG(slot3) trigger, AWG ch3 -> DIG ch1.
"""

_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

matplotlib.use("QtAgg")  # for interactive plots; comment out if not available

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
for _noisy in ("matplotlib",):
    logging.getLogger(_noisy).setLevel(logging.WARNING)

# Per-HVI sample rate + introspected constants, see instrumentserver/instrument_plugins/HVI/build_hvi_info.py
HVI_INFO_PATH = os.path.join(
    _REPO_ROOT, "instrumentserver", "instrument_plugins", "HVI", "HVI_INFO.json"
)
with open(HVI_INFO_PATH) as f:
    HVI_INFO = {k: v for k, v in json.load(f).items() if not k.startswith("_")}

# Server startup MUST happen before importing mclient (which connects on import)
from lib.server_support.lifeline import clear_servers, start_servers
clear_servers()
start_servers()

from mclient import instruments

AWG_SLOT = 8
DIG_SLOT = 3
NUM_AWG_SLOTS = 1  # len(awg_list) passed to Keysight_DIG; determines the HVI filename below
TRIGGER_PERIOD_US = 100
# Keysight_DIG.load_hvi() builds this exact filename as f"{num_slots}slot{trigger_period}us.HVI"
HVI_NAME = f"{NUM_AWG_SLOTS}slot{TRIGGER_PERIOD_US}us.HVI"
HVI_SAMPLE_RATE_HZ = HVI_INFO.get(HVI_NAME, {}).get("sample_rate", float("nan"))

EXPECTED_AWG_FS_HZ = 1000e6  # M3202A native rate; the Fs hack depends on this being true
AWG_FS_TOLERANCE = 0.01  # 1%

F_REF_HZ = 50e6  # reference tone fed into DIG ch1 via AWG ch3; safely below Nyquist for Fs >= 100 MS/s
NSAMPLES = 8000  # DIG raw capture length; at the slowest plausible Fs (100 MS/s) this is 80 us, fits inside the 100 us trigger_period
NRUNS = 5


def verify_awg_sample_rate(awg, context):
    fs = awg.do_get_clock_freq()
    logger.info("AWG sample rate check (%s): %.3f MS/s", context, fs / 1e6)
    if abs(fs - EXPECTED_AWG_FS_HZ) > EXPECTED_AWG_FS_HZ * AWG_FS_TOLERANCE:
        raise RuntimeError(
            f"AWG sample rate is {fs / 1e6:.3f} MS/s, expected "
            f"{EXPECTED_AWG_FS_HZ / 1e6:.0f} MS/s ({context}). The DIG "
            "sample-rate hack assumes a trustworthy 1000 MS/s AWG clock; "
            "aborting before trusting any inferred Fs."
        )
    return fs


def build_trigger_and_tone(n_samples, awg_fs_hz, f_tone_hz, trigger_high_samples=200):
    t = np.arange(n_samples) / awg_fs_hz
    tone = np.sin(2 * np.pi * f_tone_hz * t)
    trigger = np.zeros(n_samples)
    trigger[:trigger_high_samples] = 1.0
    return trigger, tone


def calibrate_sample_rate(dig, awg, f_ref_hz, n_samples, n_runs):
    channel = dig.get_main_channel()

    dig.set_nsamples(n_samples)
    dig.set_naverages(1)
    dig.set_channel_delay(0)

    estimates = []
    for i in range(n_runs):
        verify_awg_sample_rate(awg, context=f"calibration run {i + 1}/{n_runs}")

        # Re-configure buffer pool each iteration (setup_raw_shot calls release_buf internally)
        dig.setup_raw_shot(channel=channel, naverages=1)
        dig.run_channel(channel)  # start only the configured channel, not all 4
        dig.start_hvi()
        raw = dig.DAQbufferGet(channel)
        dig.stop_hvi()

        if len(raw) == 0:
            logger.error("run %d/%d: DAQbufferGet returned empty — DIG not triggered (check wiring)", i + 1, n_runs)
            continue

        win = np.hanning(len(raw))  # reduce spectral leakage from the non-periodic capture window
        spec = np.fft.rfft(win * raw)
        k_peak = int(np.argmax(np.abs(spec)))
        fs_est = f_ref_hz * len(raw) / k_peak  # bin k -> freq k*Fs/N, solved for Fs since f_ref is known
        logger.info(
            "run %d/%d: k_peak=%d -> Fs_est=%.3f MS/s", i + 1, n_runs, k_peak, fs_est / 1e6
        )
        estimates.append(fs_est)

    dig.release_buf()

    fs_mean = float(np.mean(estimates)) if estimates else float("nan")
    fs_std = float(np.std(estimates)) if estimates else float("nan")
    return fs_mean, fs_std, estimates


# ---------------------------------------------------------------------------
# Build instruments (create style, as in create_instruments.py).
# ---------------------------------------------------------------------------
AWG2 = instruments.create(
    "AWG2",
    "Keysight_AWG",
    chassis=0,
    slot=AWG_SLOT,
    AWG_PRODUCT="M3202A",
    amps=[1.5, 1.5, 1.5, 1.5],
    ofs=[0.0, 0.0, 0.0, 0.0],
)
verify_awg_sample_rate(AWG2, context="immediately after AWG creation")

dig = instruments.create(
    "dig",
    "Keysight_DIG",
    chassis=0,
    slot=DIG_SLOT,
    trigger_period=TRIGGER_PERIOD_US,
    trigger_only=False,
    naverages=1,
    nsamples=NSAMPLES,
    awg_list=[AWG_SLOT],
    channel_delay=0,
    deltaf=F_REF_HZ,
)
logger.info(
    "Loaded HVI for this config: %s (HVI_INFO.json says %.1f MS/s)",
    HVI_NAME, HVI_SAMPLE_RATE_HZ / 1e6,
)

verify_awg_sample_rate(AWG2, context="after DIG/HVI creation, before loading waveforms")

# ---------------------------------------------------------------------------
# Load known reference tone (ch3) + trigger pulse (ch1) onto the AWG
# ---------------------------------------------------------------------------
awg_fs = verify_awg_sample_rate(AWG2, context="before building reference waveforms")

n_samples_awg = int(round(TRIGGER_PERIOD_US * 1e-6 * awg_fs))  # fill one full HVI trigger_period at the AWG's own (trusted) rate
trigger_wave, tone_wave = build_trigger_and_tone(n_samples_awg, awg_fs, F_REF_HZ)

AWG2.stop()
AWG2.add_waveform("trig_pulse", trigger_wave)
AWG2.add_waveform("tone_ref", tone_wave)
# trig=True -> SWHVITRIG queue mode, so both channels fire together on the same HVI start (co-fired trigger scheme)
AWG2.set_seq_element(ch=1, el=0, wname="trig_pulse", repeat=1, trig=True)
AWG2.set_seq_element(ch=3, el=0, wname="tone_ref", repeat=1, trig=True)
AWG2.run()  # arms ch1/ch3 to wait for the next HVI-issued software trigger

verify_awg_sample_rate(AWG2, context="right before calibration loop")

# ---------------------------------------------------------------------------
# Run the calibrator
# ---------------------------------------------------------------------------
fs_mean, fs_std, estimates = calibrate_sample_rate(
    dig, AWG2, f_ref_hz=F_REF_HZ, n_samples=NSAMPLES, n_runs=NRUNS
)

verify_awg_sample_rate(AWG2, context="after calibration loop")

logger.info(
    "Calibrated DIG sample rate: %.3f MS/s (std %.3f MS/s over %d runs); "
    "HVI_INFO.json['%s'].sample_rate = %.1f MS/s",
    fs_mean / 1e6, fs_std / 1e6, NRUNS, HVI_NAME, HVI_SAMPLE_RATE_HZ / 1e6,
)

print(f"Fs_mean = {fs_mean / 1e6:.3f} MS/s, Fs_std = {fs_std / 1e6:.3f} MS/s")
print(f"Estimates (MS/s): {[round(e / 1e6, 3) for e in estimates]}")

plt.figure()
plt.plot(np.array(estimates) / 1e6, "o-", label="calibrated")
plt.axhline(
    HVI_SAMPLE_RATE_HZ / 1e6, color="r", linestyle="--", label="HVI_INFO.json"
)
plt.xlabel("Run")
plt.ylabel("Estimated Fs [MS/s]")
plt.title(f"DIG sample-rate calibration ({HVI_NAME})")
plt.legend()
plt.show()
