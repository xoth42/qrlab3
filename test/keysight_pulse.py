import logging
import os
import sys

import matplotlib
import matplotlib.pyplot as plt
import numpy as np

"""
Isaac Pelenur - 2024-06-15

TLDR: if_period = 2

Loopback pulse test and digitizer demod calibration notes
=========================================================

This test was used to debug the Keysight M3102A digitizer + AWG2 readout chain
using a direct loopback (AWG2 ch3 → DIG ch1), bypassing the cavity and mixers.
The main goal was to verify that the AWG is really sending a 50 MHz tone into
the digitizer and that the software demodulation (DemodulatorComplex) is
correctly configured.

Key findings:

- Raw loopback capture:
  - Using the full qrlab stack (create_instruments, HVI, ReadoutWindowDelaySweep),
    we captured raw ADC samples on the digitizer channel connected to AWG2 ch3.
  - The time-domain trace looks like a clean sinusoidal pulse during the
    readout window, confirming the AWG and cabling are OK.

- FFT-based sample-rate inference:
  - We took a single raw capture and computed an FFT over the pulse.
  - Sweeping the assumed sampling rate (Fs_guess = 250, 500, 1000 MS/s) and
    plotting the resulting frequency axis, the FFT peak always appeared at
    exactly half of Fs_guess (for example, peak at 125 MHz for 250 MS/s,
    250 MHz for 500 MS/s, etc.).
  - This means the tone is at the Nyquist frequency: the normalized frequency
    of the peak is 0.5, so the relationship is:
        f_tone = 0.5 * Fs_actual
    Given that the AWG is generating a 50 MHz readout tone, this implies:
        Fs_actual ≈ 100 MS/s
    for the M3102A under the current HVI configuration.

- Demodulation period (if_period) correction:
  - The software demodulator expects if_period to be:
        if_period = Fs_actual / f_IF
    where f_IF is the intermediate frequency (readout IF) in Hz.
  - For an IF of 50 MHz and a digitizer sample rate of about 100 MS/s,
    the correct if_period is 2 samples per IF cycle.
  - Old Alazar-based assumptions used 1 GS/s sample rate and if_period = 20
    for 50 MHz. Those values are not valid for the M3102A in this setup and
    lead to a demod LO at the wrong frequency (and the observed "only edges,
    no flat-top" behavior).

- Trigger period coincidence:
  - The HVI trigger period was configured as 100 microseconds, and the FFT
    suggested a sample rate of approximately 100 MS/s. These numbers both
    contain "100" but are conceptually independent:
      * trigger_period is the time between shots (100 microseconds),
      * Fs_actual is the ADC sampling rate (about 100 MS/s).
  - The equality of the numeric value is just a design choice in the HVI
    timing; it should not be used to infer the sample rate.

Practical takeaway for this test:

- Physically connect AWG2 ch3 (I channel) directly to the desired digitizer
  input (e.g. DIG ch1).
- Use the full qrlab path (create_instruments, ReadoutWindowDelaySweep,
  Keysight_DIG) to:
    1) load and run the standard readout pulse on AWG2,
    2) capture raw ADC data on the loopback channel,
    3) perform an FFT to verify that the tone is at 50 MHz and to infer the
       effective digitizer sample rate.
- Then set:
    if_period = round(Fs_actual / 50e6)
  and re-run the loopback test. With Fs_actual ≈ 100 MS/s, if_period should
  be 2, not 10 or 20. Once this is set, the demodulated I/Q magnitude should
  show a flat, high-amplitude plateau over the pulse flat-top instead of
  only large spikes at the edges.
"""

_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from mclient import instruments

matplotlib.use("QtAgg")  # for interactive plots; comment out if not available

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
for _noisy in ("matplotlib",):
    logging.getLogger(_noisy).setLevel(logging.WARNING)



from scripts.single_cavity.readout_window_delay_sweep import \
    ReadoutWindowDelaySweep

dig = instruments['dig']

# 1) Make sure we're reading from the wired ADC channel
# dig.set_main_channel(2)       # AWG2 ch3 → DIG ch2

# 2) Simple capture settings
nsamples = 3000
naverages = 1
dig.set_nsamples(nsamples)        # you can bump this later
dig.set_naverages(naverages)          # single shot, easier for FFT
dig.set_channel_delay(0)    # or 0 if you want from pulse start

# 3) Build readout measurement to get the AWG sequence + HVI exactly as usual
m = ReadoutWindowDelaySweep(
    delays=np.array([0, 1]),  # dummy; show_pulse/measure don't iterate this here
    readout='readout_IQ',
)

# 4) Load the AWG waveform and start the AWGs
# dig.set_channel_delay(150)
m.stop_awgs()
m.load(m.generate())
m.start_awgs()

# 5) Configure for raw single-shot capture (no demodulation)
dig.setup_raw_shot(channel=dig.get_main_channel(), naverages=naverages)
dig.arm()
dig.start_hvi()

# 6) Grab raw buffer via the proxy-safe method on Keysight_DIG
raw = dig.DAQbufferGet(dig.get_main_channel())

dig.stop_hvi()
dig.release_buf()

print("raw.shape:", raw.shape)
plt.plot(raw, linewidth=0.5, alpha=0.7)
plt.title("Raw samples")
plt.show()


# Window to reduce leakage
win = np.hanning(len(raw))
spec = np.fft.rfft(raw * win)

def check_fs(Fs_guess):
    freqs = np.fft.rfftfreq(len(raw), d=1.0/Fs_guess)
    mag = np.abs(spec)
    peak_idx = np.argmax(mag)
    peak_freq = freqs[peak_idx]
    print(f"Fs_guess = {Fs_guess/1e6:.1f} MS/s  ->  peak at {peak_freq/1e6:.3f} MHz")

for Fs in [250e6, 500e6, 1e9]:
    check_fs(Fs)

# Choose the Fs where the peak is closest to 50 MHz
Fs_best = 500e6  # example; choose based on printed output
freqs = np.fft.rfftfreq(len(raw), d=1.0/Fs_best)
plt.semilogy(freqs/1e6, np.abs(spec))
plt.xlim(0, 100)
plt.xlabel("Frequency [MHz]")
plt.ylabel("Magnitude [AU]")
plt.title(f"Raw spectrum assuming Fs = {Fs_best/1e6:.1f} MS/s")
plt.show()
