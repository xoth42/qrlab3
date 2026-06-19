
import logging
import os
import sys

import matplotlib.pyplot as plt
import numpy as np

_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

import config
from measurement import Measurement1D
from pulseseq.pulselib import *
from pulseseq.sequencer import *  # provides Sequence, Trigger, Delay, Combined, etc.
from pulseseq.sequencer import Sequence

# Samples per µs at 1 GS/s AWG clock. Used to convert trigger_period (µs)
# to samples for sequence length checks. Update if AWG clock differs.
_SAMPLES_PER_US = 1000

logger = logging.getLogger(__name__)
DIGITIZER_SAMPLING_RATE = 500e6 

def plot_iq_trace(ret, delay, if_period, naverages, SAMPLING_RATE=DIGITIZER_SAMPLING_RATE, title=None):
    """Plot demodulated I, Q, and magnitude vs time.

    Args:
        ret:        complex array of demodulated IQ values, one per if_period bin
        delay:      channel_delay in samples; shown in default title
        if_period:  samples per IF period; sets x-axis bin width
        naverages:  number of averages used; shown in default title
        title:      optional override for the plot title
    """
    logger.debug('Plotting IQ trace with delay=%d samples, if_period=%d samples, naverages=%d',
        delay, if_period, naverages)
    logger.debug('max |ret|: %f', np.max(np.abs(ret)))
    logger.debug('max Re(ret): %f', np.max(np.real(ret)))
    logger.debug('min Re(ret): %f', np.min(np.real(ret)))
    logger.debug('max Im(ret): %f', np.max(np.imag(ret)))
    logger.debug('min Im(ret): %f', np.min(np.imag(ret)))



    xs_us = np.arange(len(ret)) * if_period / (SAMPLING_RATE / 1e6)
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(xs_us, np.real(ret), label='I value',   color='steelblue')
    ax.plot(xs_us, np.imag(ret), label='Q value',   color='tomato')
    ax.plot(xs_us, np.abs(ret),  label='magnitude', color='mediumseagreen')
    ax.axhline(0, color='k', lw=0.5, ls='--')
    ax.set_ylabel('amplitude [ADU]')
    ax.set_xlabel('time [µs]')
    ax.set_title(title or ('Readout pulse  delay=%d  (%d averages)' % (int(delay), naverages)))
    ax.legend(fontsize=9)
    plt.tight_layout()
    plt.show()


def plot_raw_trace(raw, delay, SAMPLING_RATE=DIGITIZER_SAMPLING_RATE, title=None):
    """Plot a single raw ADC capture (no demodulation/averaging) vs time.

    Args:
        raw:   1D array of raw ADC samples (one shot, naverages=1)
        delay: channel_delay in samples; shown in default title
        SAMPLING_RATE: digitizer sample rate in Hz, sets the x-axis scale
        title: optional override for the plot title
    """
    logger.debug('Plotting raw trace with delay=%d samples, %d samples total', delay, len(raw))
    if len(raw) == 0:
        logger.error('No raw samples captured (empty buffer) — digitizer never triggered/armed; nothing to plot')
        return
    logger.debug('max raw: %f, min raw: %f', np.max(raw), np.min(raw))

    xs_us = np.arange(len(raw)) / (SAMPLING_RATE / 1e6)
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(xs_us, raw, label='raw ADC counts', color='steelblue')
    ax.axhline(0, color='k', lw=0.5, ls='--')
    ax.set_ylabel('amplitude [ADU]')
    ax.set_xlabel('time [µs]')
    ax.set_title(title or ('Raw single-shot capture  delay=%d' % int(delay)))
    ax.legend(fontsize=9)
    plt.tight_layout()
    plt.show()


class ReadoutWindowDelaySweep(Measurement1D):
    """
        TODO
        Args:
            delays:   1D array of delay values in samples (ns at 1 GS/s)
            **kwargs: must include readout='readout_IQ'
    """

    def __init__(self, delays, pre_trigger_pad=1, post_readout_pad=10, no_error=False, shots_per_average=2, sequencer_minlen=1, **kwargs):
        """
        pre_trigger_pad:  samples of Trigger() before the delay+pulse. Matches the
                          lab-wide Trigger(250) convention used in Rabi and other
                          sequences. No-op on the output for this trigger wiring
                          (see assumption 3 in module docstring), but kept for
                          consistency with the rest of the pulse stack.
        post_readout_pad: samples of Delay() appended after do_get_sequence().
                          Gives the cavity/electronics time to ring down before the
                          HVI period repeats. Must be large enough that
                          pre_trigger_pad + max(delays) + pulse_total + post_readout_pad
                          fits within trigger_period (checked per-point in generate()).
        """
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
        assert pre_trigger_pad >= 0, "pre_trigger_pad must be >= 0"
        assert post_readout_pad >= 0, "post_readout_pad must be >= 0"

        self.delays          = delays
        self.pre_trigger_pad = int(pre_trigger_pad)
        self.post_readout_pad = int(post_readout_pad)
        self.no_error = no_error
        self.shots_per_average = shots_per_average
        self.sequencer_minlen = int(sequencer_minlen)
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

    def get_sequencer(self, seqs=None):
        s = Sequencer(seqs, minlen=self.sequencer_minlen)

        for i in self.infos:
            if hasattr(i, 'ssb_list'):
                for ssb in i.ssb_list:
                    s.add_ssb(ssb)
            else:
                if i.ssb:
                    s.add_ssb(i.ssb)
            if i.marker and i.marker['channel'] != '':
                s.add_marker(i.marker['channel'], i.channels[0],
                             ofs=i.marker['ofs'], bufwidth=i.marker['bufwidth'])
                s.add_marker(i.marker['channel'], i.channels[1],
                             ofs=i.marker['ofs'], bufwidth=i.marker['bufwidth'])

        if hasattr(config, 'required_markers'):
            for marker_dict in config.required_markers:
                 s.add_marker(marker_dict['out_chan'],
                              marker_dict['in_chan'],
                              ofs=marker_dict['ofs'],
                              bufwidth=marker_dict['bufwidth'])

        for ch in config.required_channels:
            s.add_required_channel(ch)

        return s

    def _pulse_total_samples(self):
        """AWG samples consumed by do_get_sequence(): flat top + 4*sigma edges."""
        # chop=4 is hard-coded in Readout_IQ_Info.do_get_sequence()
        return int(self.readout_driver.get_pulse_width()) + 4 * int(self.readout_driver.get_sigma())

    def show_pulse(self, delay, window=None, raw=False):
        """Fire a single shot and plot it, to visually confirm the pulse is
            arriving in the capture window, check the flat-top region, and
            pick a good channel_delay / nsamples.

            Args:
                delay:  channel_delay in samples — how many samples the digitizer skips
                        after the trigger edge before it starts capturing.  Equivalent to
                        dig.set_channel_delay(delay).  Sweep this to slide the capture
                        window forward until the pulse flat-top is centred.
                window: optional (start_sample, stop_sample) tuple to crop the x-axis.
                        None shows the full capture window.
                raw:    if True, bypass averaging/demodulation entirely and plot a
                        single raw ADC capture (naverages=1) via setup_raw_shot/
                        take_raw_shot. Useful for isolating triggering/acquisition
                        problems from demod-path issues.
        """
        dig = self.instruments['dig']


        # 1. Apply the requested channel_delay on the digitizer, then reload the
        #    fixed AWG sequence.  The AWG waveform does not change between calls —
        #    only the DIG capture offset changes.
        logger.info(
            'show_pulse(delay=%d, nsamples=%d, naverages=%d, if_period=%d, raw=%s)',
            int(delay),
            dig.get_nsamples(),
            dig.get_naverages(),
            dig.get_if_period(),
            raw,
        )
        logger.debug('Setting channel_delay to %d samples and reloading sequence', int(delay))
        dig.set_channel_delay(int(delay))
        self.stop_awgs()
        self.load(self.generate())
        self.start_awgs()

        if raw:
            # Bypass setup_avg_shot/take_avg_shot entirely: single raw shot,
            # no demod, no averaging, no ref channel involvement.
            logger.info('Taking raw shot with channel_delay=%d samples', int(delay))
            dig.setup_raw_shot(naverages=1)
            dig.arm()
            dig.start_hvi()
            raw_data = dig.take_raw_shot()
            dig.stop_hvi()
            dig.release_buf()

            sampling_rate = dig.get_sample_rate()
            logger.debug('Digitizer returned %d raw samples, sampling_rate=%.2f Hz', len(raw_data), sampling_rate)
            logger.debug('Plotting raw shot with channel_delay=%d samples', int(delay))
            plot_raw_trace(raw_data, delay, SAMPLING_RATE=sampling_rate)
            return

        # 2. Arm the digitizer and fire one averaged acquisition.
        #    setup_avg_shot() picks up the updated channel_delay set above and
        #    re-programs the DAQ registers before arming.
        logger.info('Taking averaged shot with channel_delay=%d samples', int(delay))
        dig.setup_avg_shot()
        dig.arm()
        dig.start_hvi()
        ret = dig.take_avg_shot(take_ref=False)
        dig.stop_hvi()
        dig.release_buf()

        # 3. Log bin count and hand off to the shared plotting helper.
        if_period = dig.get_if_period()
        sampling_rate = dig.get_sample_rate()

        logger.debug('Digitizer returned %d bins with if_period=%d samples, and sampling_rate=%.2f Hz', len(ret), if_period, sampling_rate)
        logger.debug('Plotting pulse with channel_delay=%d samples', int(delay))
        plot_iq_trace(ret, delay, if_period, dig.get_naverages(), SAMPLING_RATE=sampling_rate,)


    def generate(self):
        """Build and return a rendered AWG sequence.

            The sequence is fixed — it does not vary with channel_delay, which is a
            digitizer-side parameter set via dig.set_channel_delay().  Sweeping
            channel_delay slides the DIG capture window over the pulse without
            touching the AWG waveform.

            Sequence:
                Trigger(pre_trigger_pad) → do_get_sequence() → Delay(post_readout_pad)

            do_get_sequence() is a Combined pulse that fires ch3 (IQ I), ch4 (IQ Q),
            and ch1 (DIG trigger) simultaneously.

            Returns:
                Rendered sequence dict suitable for passing to self.load().
        """
        trigger_period_samples = self.instruments['dig'].get_trigger_period() * _SAMPLES_PER_US
        seq_len = self.pre_trigger_pad + self._pulse_total_samples() + self.post_readout_pad
        assert seq_len <= trigger_period_samples, (
            "sequence length %d samples exceeds trigger_period %d samples "
            "(%d µs). Increase post_readout_pad or trigger_period." % (
                seq_len, trigger_period_samples,
                self.instruments['dig'].get_trigger_period())
        )

        s = Sequence()
        s.append(Trigger(self.pre_trigger_pad))
        s.append(self.readout_driver.do_get_sequence())  # fires ch1 trigger + ch3,4 IQ together
        s.append(Delay(self.post_readout_pad))

        s = self.get_sequencer(s)
        seqs = s.render()

        assert seqs is not None and len(seqs) > 0, \
            "sequencer produced no output — check AWG channel mapping"
        return seqs

    def measure(self):
        dig = self.instruments['dig']

        # --- Pre-loop validation ---
        assert dig is not None, \
            "'dig' not in instruments — was create_instruments.py run?"

        pulse_total = self._pulse_total_samples()

        # nsamples must be large enough to capture the pulse at the maximum delay.
        # At the largest channel_delay the capture window starts furthest into the
        # pulse, so we need: nsamples >= pulse_total (to see the full flat-top).
        # The trigger fires at the pulse onset, so the window must also extend at
        # least pulse_total samples past the trigger.
        max_delay = int(np.max(self.delays))
        min_nsamples = pulse_total + max_delay + 200
        assert dig.get_nsamples() >= min_nsamples, (
            "dig.nsamples=%d too small. Need >= %d "
            "(pulse_total=%d + max_delay=%d + 200 margin). "
            "Fix: dig.set_nsamples(%d)" % (
                dig.get_nsamples(), min_nsamples,
                pulse_total, max_delay, min_nsamples)
        )

        # nsamples must be divisible by if_period for the demodulator reshape.
        assert dig.get_nsamples() % dig.get_if_period() == 0, (
            "dig.nsamples=%d not divisible by if_period=%d. "
            "Choose nsamples as a multiple of %d." % (
                dig.get_nsamples(), dig.get_if_period(), dig.get_if_period())
        )

        expected_iq_len = dig.get_nsamples() // dig.get_if_period()

        # Load the fixed AWG sequence once — it does not change across delay points.
        self.stop_awgs()
        self.load(self.generate())
        self.start_awgs()

        for i, delay in enumerate(self.delays):
            print('(%d/%d) delay = %d' % (i + 1, len(self.delays), delay), end='\t')

            # Update the digitizer capture offset for this delay point.
            # setup_avg_shot() re-programs the DAQ registers with the new channel_delay.
            dig.set_channel_delay(int(delay))
            data = []
            for shot in range(self.shots_per_average):
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
                data.append([
                    IQ,
                    amp_vals,
                    sem
                ])

            # Average over all shots for this delay point
            IQ = np.mean([d[0] for d in data])
            amp_vals = np.mean([d[1] for d in data], axis=0)
            sem = np.mean([d[2] for d in data])

            self.ampdata[i]   = np.abs(IQ)
            self.ampstd[i]    = sem
            self.phasedata[i] = np.angle(IQ, deg=True)
            print('amp = %.3f ± %.4f SEM, phase = %.1f deg' % (
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
                  'Check nsamples >= pulse_total + channel_delay, '
                  'and that max delay fits in trigger_period.' % (100 * amp_variation))

        stds = np.array(self.ampstd[:])

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 6), sharex=True)

        # Top: amplitude with shaded ±1σ band
        color = 'steelblue'
        ax1.plot(self.delays, amps, 'o-', color=color, lw=1.5, ms=4, label='mean amp')
        if not self.no_error:
            ax1.fill_between(self.delays,
                            amps - stds, amps + stds,
                            alpha=0.35, color=color, label='±SEM (N=%d bins)' % len(self.delays))
        ax1.set_ylabel('IQ amplitude [AU]')
        ax1.set_title('Readout window delay sweep')
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



if __name__ == '__main__':
   
    import argparse



    parser = argparse.ArgumentParser(
        description=(
            'Readout window calibration.\n'
            '  --delay X   : single-shot inspection at channel_delay=X (show_pulse only, no data saved).\n'
            '  (no args)   : full sweep from channel_delay=0 to --max-delay.'
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        '--debug', action='store_true',
        help='Enable DEBUG-level logging (default is WARNING).',
    )
    parser.add_argument(
        '--delay', type=int, default=None, metavar='SAMPLES',
        help='channel_delay in samples: digitizer skips this many samples after the trigger '
             'edge before capturing. Runs show_pulse() only.',
    )
    parser.add_argument(
        '--max-delay', type=int, default=1200, metavar='SAMPLES',
        help='Maximum channel_delay for the full sweep (min is always 0). Default: 1200.',
    )
    parser.add_argument(
        '--npoints', type=int, default=25, metavar='N',
        help='Number of evenly-spaced delay points in the full sweep. Default: 25.',
    )
    # nsamples: raw ADC samples per trigger.
    # Must be a multiple of if_period (2 for 50 MHz IF at 100 MS/s) and
    # >= pulse_total + max_delay + 200.
    #   pulse_total and channel_delay are in DIG samples (10 ns each at Fs=100 MS/s).
    parser.add_argument(
        '--nsamples', type=int, default=41440, metavar='SAMPLES',
        help='Override dig.nsamples. Must be a multiple of if_period=2 and '
             '>= pulse_total + max_delay + 200. Default: leave digitizer setting unchanged.',
    )
    # naverages: shots averaged per point. More → lower noise by sqrt(N).
    parser.add_argument(
        '--naverages', type=int, default=None, metavar='N',
        help='Override dig.naverages. More averages reduce shot-to-shot noise by sqrt(N). '
             'Default: leave digitizer setting unchanged.',
    )
    # number of shots to run : shots averaged per point. More → lower noise by sqrt(N).
    parser.add_argument(
        '--shots-per-average', type=int, default=2, metavar='N',
        help='Number of shots to run per average. More shots reduce shot-to-shot noise by sqrt(N). '
             'Default: 2.',
    )
    parser.add_argument(
        '--raw', action='store_true',
        help='Force naverages=1 before running --delay. With a single shot the pulse '
             'envelope is visible as a clear high→low amplitude transition at bin ~226 '
             '(pulse_width=4500, if_period=2). Flat amplitude to the window edge means '
             'CW carrier leakthrough rather than a pulsed signal.',
    )
    parser.add_argument(
        '--no-error', action='store_true',
        help='Do not plot error bars'
    )

    args = parser.parse_args()

    
    from mclient import instruments


    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG) 
    # silence noisy third-party loggers
    for _noisy in ('matplotlib',):
        logging.getLogger(_noisy).setLevel(logging.WARNING)

    import matplotlib
    matplotlib.use('Qt5Agg')  # for interactive plots

    dig = instruments['dig']

    logger.info(dig.scan())

    if args.nsamples is not None:
        dig.set_nsamples(args.nsamples)
    if args.naverages is not None:
        dig.set_naverages(args.naverages)
    if args.raw:
        # Override naverages=1 so the pulse envelope is visible without phase averaging.
        # Amplitude should be high for ~226 bins then drop; flat all the way means CW leakthrough.
        dig.set_naverages(1)

    

    readoutargs = dict(readout='readout_IQ', no_error=args.no_error, shots_per_average=args.shots_per_average)

    if args.delay is not None:
        # Single-shot inspection: show I/Q/amplitude at this channel_delay.
        m = ReadoutWindowDelaySweep(
            delays=np.array([0, 1]),  # dummy — show_pulse() doesn't iterate self.delays
            **readoutargs
        )
        m.show_pulse(delay=args.delay, raw=args.raw)
    else:
        # Full sweep: channel_delay from 0 to max_delay across npoints.
        delays = np.linspace(0, args.max_delay, args.npoints)
        m = ReadoutWindowDelaySweep(delays=delays, **readoutargs)
        m.measure()