# Readout acquisition window calibration for Keysight digitizer (M3102A).
#
# TRIGGER ARCHITECTURE IN THIS SETUP
# ====================================
# AWG2 (slot 8) channel 1 is wired physically to the Digitizer TRG I/O port.
# The digitizer is configured with triggerIOconfig(AOU_TRG_IN) and
# DAQtriggerExternalConfig(..., TRIGGER_EXTERN, TRIGGER_RISE, ...) so it
# starts capturing on the rising edge of that physical line.
#
# The trigger pulse on AWG2 ch1 comes from acq_chan='1m1' inside
# Readout_IQ_Info.do_get_sequence(). Specifically:
#
#   do_get_sequence() returns Combined([
#       DataPulse(..., chan=3),          # IQ I output
#       DataPulse(..., chan=4),          # IQ Q output
#       Constant(pulse_total, 1, chan='1m1')  # <-- THIS is the trigger on ch1
#   ])
#
# Combined means all three fire simultaneously. Therefore:
#
#   THE TRIGGER AND THE IQ READOUT PULSE FIRE AT THE SAME MOMENT.
#
# The HVI backplane is still used to start the AWG cycle (SWHVITRIG for the
# first waveform), but per-shot timing is set by AWG2 ch1 → DIG TRG port.
#
# CONSEQUENCE FOR THE DELAY SWEEP
# =================================
# The sequence in generate() is:
#
#   Trigger(250) → Delay(d) → do_get_sequence()
#                                ├── ch3 IQ I  ─┐
#                                ├── ch4 IQ Q   ├── all fire at t = 250 + d
#                                └── ch1 trigger ┘
#
# Varying d shifts the trigger AND the IQ pulse together. The digitizer
# always sees the pulse at position 0 of its capture window (offset by
# channel_delay), regardless of d. The sweep produces flat amplitude —
# it does NOT locate the pulse onset in the capture window.
#
# WHAT THE SWEEP ACTUALLY MEASURES HERE
# =======================================
# Because trigger == pulse onset, this sweep is useful for:
#   - Confirming the system fires at all (non-zero amplitude)
#   - Checking amplitude is stable across trigger timings (HVI cycle health)
#   - Confirming nsamples is large enough (amplitude should not vary with d)
#
# It does NOT calibrate channel_delay in this co-fired configuration.
#
# CORRECT CALIBRATION FOR THIS TRIGGER SCHEME
# =============================================
# Two valid approaches:
#
#   Approach A — Sweep channel_delay on the DIG (simplest):
#     Keep sequence fixed. Sweep dig.set_channel_delay(cd) for cd in range.
#     Plot amplitude vs cd. Amplitude is low for cd=0 (capturing rising edge
#     transient), peaks across the flat top, then drops after the pulse ends.
#     → Set channel_delay to the rising-edge onset (skip the transient).
#     → Set nsamples to cover flat_top at that channel_delay.
#     See TODO below for ReadoutWindowChannelDelaySweep class.
#
#   Approach B — Separate trigger from IQ pulse:
#     Fire a short trigger pulse on AWG2 ch1 at t=0 (BEFORE the delay sweep).
#     Then sweep the IQ pulse delay independently. This requires NOT using
#     do_get_sequence() directly (it always co-fires ch1 with ch3,4), and
#     instead constructing the IQ waveform manually or modifying
#     Readout_IQ_Info to accept include_acq_chan=False.
#     See generate_separated() below for a skeleton.
#
# ASSUMPTIONS THAT MAY BE WRONG
# ===============================
# 1. '1m1' maps to AWG2 ch1 analog output via the awgloader channel map.
#    Confirm: after a measurement, AWG2 ch1 should show a pulse on a scope
#    that matches the readout timing.
#
# 2. AWG2 ch1 amplitude (1.5V from create_instruments.py) × pulse amplitude
#    (1.0 in Constant) = 1.5V peak. The M3102A TRG input threshold is
#    typically ~1V. This should trigger reliably, but verify on a scope.
#    If trigger is unreliable: increase channel amplitude in create_instruments
#    or reduce the threshold via dig.dig.triggerIOconfig().
#
# 3. Trigger(250) in the sequence is a no-op for this trigger path.
#    Trigger() in pulseseq generates a pulse on "master channels" configured
#    via config.slave_triggers. If config.slave_triggers is not set, Trigger()
#    does nothing on the output side. The actual per-shot trigger is
#    entirely from ch1 via acq_chan.
#
# 4. _SAMPLES_PER_US = 1000 assumes 1 GS/s AWG clock. Verify with
#    AWG2.get_clock_freq() and dig.get_clock_freq() before trusting
#    any timing calculations.
#
# 5. channel_delay=150 in create_instruments.py was set by hand. It skips
#    ~150 ns of transient at the rising edge of the combined trigger+IQ pulse.
#    Whether 150 is optimal has not been verified with data.
#
# BEFORE RUNNING
# ===============
# - dig.set_nsamples() must be large enough: pulse_total + margin
#   pulse_total = pulse_width + 4*sigma = 4500 + 40 = 4540 samples
#   Minimum nsamples >= 4540 + channel_delay + ~200 margin ≈ 5000
#   Current value (2000) is too small even for a fixed-delay single shot.
#   Fix: dig.set_nsamples(5000) before calling measure().
# - RF source (SCtest) must be on at the correct readout frequency.
# - AWG2 and AWG3 must be initialized (create_instruments.py run).
# - HVI file 2slot100us.HVI must be loaded (happens at DIG init).

import matplotlib.pyplot as plt
import numpy as np

from measurement import Measurement1D
from pulseseq.pulselib import *
from pulseseq.sequencer import *  # provides Sequence, Trigger, Delay, Combined, etc.

# Samples per µs at 1 GS/s AWG clock. Used to convert trigger_period (µs)
# to samples for sequence length checks. Update if AWG clock differs.
_SAMPLES_PER_US = 1000


class ReadoutWindowDelaySweep(Measurement1D):
    """
    Sweep the AWG delay before do_get_sequence() and measure IQ amplitude.

    NOTE: In the current trigger scheme (trigger co-fired with IQ pulse via
    acq_chan='1m1'), this sweep does NOT calibrate channel_delay. It produces
    flat amplitude because trigger and pulse always arrive together.

    It is still useful for:
    - Confirming the full chain (AWG → microwave → DIG) is alive
    - Verifying amplitude stability across HVI cycle positions
    - Checking that nsamples is large enough (amplitude should not dip)

    For actual channel_delay calibration, use ReadoutWindowChannelDelaySweep
    (see TODO below) or Approach B (separated trigger).

    Args:
        delays:   1D array of delay values in samples (ns at 1 GS/s)
        **kwargs: must include readout='readout_IQ'
    """

    def __init__(self, delays, **kwargs):
        delays = np.asarray(delays, dtype=float)

        # --- Input validation ---
        assert delays.ndim == 1, \
            "delays must be a 1D array, got shape %s" % (delays.shape,)
        assert len(delays) >= 2, \
            "need at least 2 delay points, got %d" % len(delays)
        assert np.all(delays >= 0), \
            "all delays must be >= 0; min given: %g" % delays.min()
        assert np.all(np.isfinite(delays)), \
            "delays contains NaN or Inf"

        self.delays = delays

        # cyclelen=1: using setup_avg_shot() (single-point, N averages), not
        # setup_experiment() (which expects cyclelen simultaneous points).
        # infos=[]: Readout_IQ_Info.do_get_sequence() performs inline IQ
        # modulation — no SSB registration needed via get_sequencer().
        super(ReadoutWindowDelaySweep, self).__init__(
            1, infos=[], **kwargs
        )

        # --- Post-construction validation ---
        assert self.readout_driver is not None, (
            "readout_driver is None — pass readout='readout_IQ' to constructor. "
            "Got readout=%r" % kwargs.get('readout', '<not passed>')
        )
        assert hasattr(self.readout_driver, 'do_get_sequence'), \
            "readout_driver has no do_get_sequence — expected Readout_IQ_Info"
        assert hasattr(self.readout_driver, 'get_pulse_width') and \
               hasattr(self.readout_driver, 'get_sigma'), \
            "readout_driver missing get_pulse_width or get_sigma"

        self.data.create_dataset('delays', data=delays)
        self.ampdata   = self.data.create_dataset('amplitudes', shape=(len(delays),))
        self.ampstd    = self.data.create_dataset('amp_std',    shape=(len(delays),))
        self.phasedata = self.data.create_dataset('phases',     shape=(len(delays),))

    def _pulse_total_samples(self):
        """AWG samples consumed by do_get_sequence(): flat top + 4*sigma edges."""
        # chop=4 is hard-coded in Readout_IQ_Info.do_get_sequence()
        return int(self.readout_driver.get_pulse_width()) + 4 * int(self.readout_driver.get_sigma())

    def generate(self, delay):
        # Sequence: Trigger(250) → Delay(d) → do_get_sequence()
        #
        # IMPORTANT: do_get_sequence() fires ch3 IQ + ch1 trigger simultaneously
        # (Combined). Delay(d) shifts both together. The digitizer always sees
        # the pulse at the same position in its window. See module docstring.
        assert delay >= 0, "delay must be >= 0, got %g" % delay

        # Total samples must fit within the HVI trigger_period.
        # trigger_period is in µs; convert to samples at 1 GS/s.
        trigger_period_samples = self.instruments['dig'].get_trigger_period() * _SAMPLES_PER_US
        seq_len = 250 + int(delay) + self._pulse_total_samples() + 2000
        assert seq_len <= trigger_period_samples, (
            "sequence length %d samples exceeds trigger_period %d samples "
            "(%d µs). Reduce max delay or increase trigger_period on the "
            "digitizer." % (seq_len, trigger_period_samples,
                            self.instruments['dig'].get_trigger_period())
        )

        s = Sequence()
        s.append(Trigger(250))       # likely no-op — see assumption 3 in module docstring
        s.append(Delay(int(delay)))
        s.append(self.readout_driver.do_get_sequence())  # fires ch1 trigger + ch3,4 IQ together
        s.append(Delay(2000))

        s = self.get_sequencer(s)
        seqs = s.render()

        assert seqs is not None and len(seqs) > 0, \
            "sequencer produced no output for delay=%d — check AWG channel mapping" % delay
        return seqs

    def measure(self):
        dig = self.instruments['dig']

        # --- Pre-loop validation ---
        assert dig is not None, \
            "'dig' not in instruments — was create_instruments.py run?"

        pulse_total = self._pulse_total_samples()

        # nsamples must cover the full pulse length even at delay=0.
        # In the co-fired scheme the pulse always starts at the beginning of
        # the capture window, so nsamples >= pulse_total + channel_delay + margin.
        min_nsamples = pulse_total + dig.get_channel_delay() + 200
        assert dig.get_nsamples() >= min_nsamples, (
            "dig.nsamples=%d too small. Need >= %d "
            "(pulse_total=%d + channel_delay=%d + 200 margin). "
            "Fix: dig.set_nsamples(%d)" % (
                dig.get_nsamples(), min_nsamples,
                pulse_total, dig.get_channel_delay(), min_nsamples)
        )

        # nsamples must be divisible by if_period for the demodulator reshape.
        assert dig.get_nsamples() % dig.get_if_period() == 0, (
            "dig.nsamples=%d not divisible by if_period=%d. "
            "Choose nsamples as a multiple of %d." % (
                dig.get_nsamples(), dig.get_if_period(), dig.get_if_period())
        )

        expected_iq_len = dig.get_nsamples() // dig.get_if_period()

        for i, delay in enumerate(self.delays):
            print('Delay %d/%d: %d samples' % (i + 1, len(self.delays), delay))

            # Reload every point — waveform changes each iteration.
            # stop_awgs() → awg.all_off() → flushes waveform memory on the AWG.
            self.stop_awgs()
            self.load(self.generate(delay))
            self.start_awgs()

            dig.setup_avg_shot()
            dig.arm()
            dig.start_hvi()
            ret = dig.take_avg_shot(take_ref=False)
            dig.stop_hvi()
            dig.release_buf()

            assert ret is not None, \
                "take_avg_shot returned None at delay=%d — DIG not triggered?" % delay
            assert len(ret) == expected_iq_len, (
                "take_avg_shot returned %d IQ points, expected %d "
                "(nsamples=%d / if_period=%d)" % (
                    len(ret), expected_iq_len,
                    dig.get_nsamples(), dig.get_if_period())
            )

            IQ = np.average(ret)
            amp_vals = np.abs(ret)          # amplitude at each IF-period bin in the window
            sem = np.std(amp_vals) / np.sqrt(len(amp_vals))   # SEM: uncertainty on the mean
            self.ampdata[i]   = np.abs(IQ)
            self.ampstd[i]    = sem
            self.phasedata[i] = np.angle(IQ, deg=True)
            print('  amp = %.3f ± %.4f SEM, phase = %.1f deg' % (
                np.abs(IQ), sem, np.angle(IQ, deg=True)))

        self.analyze()

    def analyze(self, data=None, fig=None):
        amps = np.array(self.ampdata[:]) if data is None else np.asarray(data)

        assert len(amps) == len(self.delays), (
            "amplitude array length %d does not match delays length %d" % (
                len(amps), len(self.delays))
        )
        assert np.max(amps) > 0, (
            "all amplitudes are zero — no signal. "
            "Check: RF source on, AWG cables connected, "
            "dig.nsamples >= pulse_total + channel_delay."
        )

        # In the co-fired scheme amplitude should be FLAT (pulse always at
        # position 0 in capture window). A slope or dip indicates either:
        #   - sequence is running out of the HVI trigger_period at large delays
        #   - nsamples is borderline and the pulse is getting clipped
        amp_variation = (np.max(amps) - np.min(amps)) / np.max(amps)
        # 10% point-to-point noise is normal for co-fired scheme with uncontrolled LO phase.
        # Only warn above 50%: that signals a real problem (sequence overflow, nsamples too small).
        if amp_variation > 0.5:
            print('WARNING: amplitude varies by %.0f%% across delays. '
                  'Expected flat for co-fired trigger. '
                  'Check nsamples >= pulse_total + channel_delay, '
                  'and that max delay fits in trigger_period.' % (100 * amp_variation))

        stds = np.array(self.ampstd[:])

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 6), sharex=True)

        # Top: amplitude with shaded ±1σ band
        color = 'steelblue'
        ax1.plot(self.delays, amps, 'o-', color=color, lw=1.5, ms=4, label='mean amp')
        ax1.fill_between(self.delays,
                         amps - stds, amps + stds,
                         alpha=0.35, color=color, label='±SEM (N=%d bins)' % len(self.delays))
        ax1.set_ylabel('IQ amplitude [AU]')
        ax1.set_title('Readout window delay sweep  (co-fired: expect flat amplitude)')
        ax1.legend(fontsize=8)
        ax1.axhline(np.mean(amps), color=color, lw=0.8, ls='--', alpha=0.5)

        # Bottom: phase
        phases = np.array(self.phasedata[:])
        ax2.plot(self.delays, phases, 's-', color='tomato', lw=1.5, ms=4, label='phase')
        ax2.set_ylabel('Phase [deg]')
        ax2.set_xlabel('AWG delay (samples = ns at 1 GS/s)')
        ax2.axhline(np.mean(phases), color='tomato', lw=0.8, ls='--', alpha=0.5,
                    label='mean %.1f°' % np.mean(phases))
        ax2.legend(fontsize=8)

        plt.tight_layout()
        plt.show()

        print('Mean amplitude: %.3f  Variation: %.1f%%' % (
            np.mean(amps), 100 * amp_variation))
        return np.mean(amps)


# TODO: implement ReadoutWindowChannelDelaySweep
#
# This is the correct calibration for the co-fired trigger scheme.
#
# Keep sequence fixed (no AWG delay sweep). Sweep dig.set_channel_delay(cd)
# for cd in range(0, pulse_total, step). For each cd:
#   1. Call dig.set_channel_delay(cd)         # re-init DIG capture offset
#   2. dig.setup_avg_shot() / arm / start_hvi / take_avg_shot / stop_hvi
#   3. Record IQ amplitude
#
# Expected result:
#   cd = 0:              captures rising edge transient → low amplitude
#   cd = ~sigma*4:       entering flat top → amplitude rising
#   cd = flat top start: amplitude plateaus → this is the optimal channel_delay
#   cd > pulse_total:    capturing after pulse ends → amplitude drops to noise
#
# From the plateau:
#   channel_delay = onset of plateau (skip transient)
#   nsamples      = plateau_end - plateau_start (flat top width) + margin
#
# Key assert to add:
#   after sweep: assert plateau width > 0 (i.e. a flat region exists)
#   assert cd_at_plateau_start < pulse_total - 4*sigma (flat top exists)
#
# NOTE: set_channel_delay() calls __init__ on the DIG
# (see Keysight_DIG.do_set_trigger_period which reinits — check if
# set_channel_delay has the same side effect before using in a loop).


if __name__ == '__main__':
    # RF CHAIN
    # --------
    # Signal Core LO → Splitter
    #     A → 3-way subtract mixer (LO reference to downconvert cavity output)
    #     B → 4-way IQ mixer (LO input)
    # AWG2 ch3 I + ch4 Q (IF at deltaf=50 MHz, SSB modulated Gaussian-square)
    #     → Band Pass Filters → 4-way IQ mixer → measurement frequency → Cavity
    #     → 3-way subtract mixer (vs LO-A) → IF at 50 MHz → Digitizer channel 1
    # AWG2 ch1 → Digitizer trigger input (co-fires with IQ pulse via acq_chan='1m1')
    #
    # PULSE TIMING PER SHOT (at delay=d)
    # ------------------------------------
    #   t = 0 .. 250       Trigger(250)      no-op for this wiring
    #   t = 250 + d        ch3 I:            Gaussian-square, 4540 ns, amp=0.4*1.5V, SSB @ 50 MHz
    #   t = 250 + d        ch4 Q:            same, 90 deg phase shift
    #   t = 250 + d        ch1 trigger:      1.5V rectangular, 4540 ns → DIG TRG port rising edge
    #   t = 250 + d + 150  DIG captures:     5000 samples of IF @ 50 MHz (channel_delay=150)
    #                      SW demod @ 20 samples/IF cycle → 250 complex IQ values
    #                      np.average() → 1 complex value per shot
    #                      mean over naverages=1000 shots → 1 data point stored
    #
    # EXPECTED RESULT: amplitude flat across all delays (trigger co-fires with pulse).
    # Any dip at large d → sequence overflowing trigger_period, or nsamples too small.
    #
    # PRE-RUN CHECKLIST
    # -----------------
    # [ ] create_instruments.py run (dig, AWG2, readout_IQ live in mclient)
    # [ ] Signal Core (SCtest) ON at the LO frequency
    # [ ] All cables connected per diagram (BPFs, 4-way, 3-way, DIG ch1, trigger wire)
    # [ ] nsamples set here matches a multiple of if_period=20 and >= 4890
    #
    import mclient

    dig = mclient.instruments['dig']

    # if_period = 1 GS/s / deltaf = 1e9 / 50e6 = 20 samples per IF cycle
    # nsamples must be a multiple of 20 and >= pulse_total + channel_delay + 200
    #   pulse_total = 4500 + 4*10 = 4540,  channel_delay = 150
    #   min = 4540 + 150 + 200 = 4890  →  round up to 5000 (= 250 * 20)
    # nsamples: pulse_total + channel_delay + 200 margin, rounded up to multiple of if_period.
    # Tighter window = fewer post-pulse noise bins diluting the average → smoother amplitude.
    #   pulse_total=4540  channel_delay=150  margin=200  if_period=20
    #   min = 4540+150+200 = 4890  →  ceil(4890/20)*20 = 4900
    dig.set_nsamples(4900)

    # naverages: more averages per point → lower shot-to-shot scatter.
    # 1000 → 5000 reduces point-to-point noise by ~√5 ≈ 2.2×.
    # dig.set_naverages(5000)
    dig.set_naverages(10000)

    # Delay sweep points
    # delays = np.arange(0, 1201, 25)  # large sweep
    # Tight sweep to look at oscillation
    delays = np.linspace(0,40,100)

    m = ReadoutWindowDelaySweep(
        delays,
        readout='readout_IQ',
    )
    m.measure()