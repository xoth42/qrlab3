import logging
import os
import sys

import matplotlib
import matplotlib.pyplot as plt
import numpy as np

"""
Isaac Pelenur - 2024-06-15


This test was used to debug the Keysight M3102A digitizer + AWG2 readout chain
using a direct loopback (AWG2 ch3 → DIG ch1), bypassing the cavity and mixers.

Important notes:
Keysight AWG operates at a rate normally at 1000MS/s.
Keysight DIG reads samples at max 500MS/s. But this occationally gets set to 100MS/s, likely due to HVI shenanigans. 

If all is well, then a pulse of 40000 Samples from AWG -> DIG should show a pulse of 20000 samples. 

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
nsamples = 25000
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


logger.info(f"Connected to digitizer: {dig.do_get_part()}\nSample rate: {dig.do_get_clock_freq()/1e6:.1f} MS/s\nIF_period: {dig.do_get_if_period()} samples per IF cycle\nClock_sync_freq:{dig.do_get_clock_sync_freq()/1e6:.1f} MHz")

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
