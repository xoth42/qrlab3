
import logging
import os
import sys

import matplotlib.pyplot as plt
import numpy as np

_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from measurement import Measurement1D
from pulseseq.pulselib import *
from pulseseq.sequencer import *  # provides Sequence, Trigger, Delay, Combined, etc.
from pulseseq.sequencer import Sequence

# Samples per µs at 1 GS/s AWG clock. Used to convert trigger_period (µs)
# to samples for sequence length checks. Update if AWG clock differs.
_SAMPLES_PER_US = 1000

logger = logging.getLogger(__name__)
DIGITIZER_SAMPLING_RATE = 500e6

def plot_iq_trace(ret, if_hz, if_period, naverages, SAMPLING_RATE=DIGITIZER_SAMPLING_RATE, title=None):
    """Plot demodulated I, Q, and magnitude vs time at a given IF.

    Args:
        ret:        complex array of demodulated IQ values, one per if_period bin
        if_hz:      IF frequency in Hz; shown in default title
        if_period:  samples per IF period; sets x-axis bin width
        naverages:  number of averages used; shown in default title
        title:      optional override for the plot title
    """
    logger.debug('Plotting IQ trace with IF=%.1f MHz, if_period=%d samples, naverages=%d',
        if_hz / 1e6, if_period, naverages)
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
    ax.set_title(title or ('Readout pulse  IF=%.1f MHz  (%d averages)' % (if_hz / 1e6, naverages)))
    ax.legend(fontsize=9)
    plt.tight_layout()
    plt.show()


class ReadoutIFSweep(Measurement1D):
    """
    Sweep demodulation IF frequency and record IQ magnitude.

    The AWG waveform is fixed (same readout tone each shot).  For each IF point:
      1. dig.do_set_deltaf(if_hz)       — updates digitizer demod LO + if_period
      2. readout_driver.set_deltaf(if_hz) — keeps readout_IQ in sync
      3. dig.setup_avg_shot() + arm/start — acquires naverages averaged shots
      4. records mean IQ amplitude and phase

    Args:
        IFs:    1D array of IF frequencies in Hz (must all be > 0).
                Typical sweep: np.linspace(10e6, 100e6, 25)
        **kwargs: must include readout='readout_IQ'
    """

    def __init__(self, IFs, pre_trigger_pad=1, post_readout_pad=10, no_error=False, shots_per_average=2, **kwargs):
        """
        pre_trigger_pad:  samples of Trigger() before the pulse.
        post_readout_pad: samples of Delay() after do_get_sequence().
        """
        IFs = np.asarray(IFs, dtype=float)

        # --- Input validation ---
        assert IFs.ndim == 1, \
            "IFs must be a 1D array, got shape %s" % (IFs.shape,)
        assert len(IFs) >= 2, \
            "need at least 2 IF points, got %d" % len(IFs)
        assert np.all(IFs > 0), \
            "all IFs must be > 0 Hz (DC demod is undefined); min given: %g" % IFs.min()
        assert np.all(np.isfinite(IFs)), \
            "IFs contains NaN or Inf"
        assert pre_trigger_pad >= 0, "pre_trigger_pad must be >= 0"
        assert post_readout_pad >= 0, "post_readout_pad must be >= 0"

        self.IFs              = IFs
        self.pre_trigger_pad  = int(pre_trigger_pad)
        self.post_readout_pad = int(post_readout_pad)
        self.no_error         = no_error
        self.shots_per_average = shots_per_average

        super(ReadoutIFSweep, self).__init__(
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

        self.data.create_dataset('IFs', data=IFs)
        self.ampdata   = self.data.create_dataset('amplitudes', shape=(len(IFs),))
        self.ampstd    = self.data.create_dataset('amp_std',    shape=(len(IFs),))
        self.phasedata = self.data.create_dataset('phases',     shape=(len(IFs),))

    def _pulse_total_samples(self):
        """AWG samples consumed by do_get_sequence(): flat top + 4*sigma edges."""
        return int(self.readout_driver.get_pulse_width()) + 4 * int(self.readout_driver.get_sigma())

    def _set_if(self, dig, if_hz):
        """Set demodulation IF on both the digitizer and readout_IQ."""
        # TODO: verify dig.do_set_deltaf is the correct low-level setter here
        #       (bypasses QTLab parameter caching). Alternatively use dig.set_deltaf(if_hz).
        dig.do_set_deltaf(if_hz)
        # TODO: confirm readout_driver.set_deltaf only affects the demod reference
        #       frequency stored in Readout_IQ_Info, and does NOT modify the AWG
        #       waveform content (pulse shape / envelope stays the same).
        self.readout_driver.set_deltaf(if_hz)

    def show_pulse(self, if_hz, window=None):
        """Fire a single averaged shot at a given IF and plot I, Q, magnitude vs time.

        Useful for checking that the pulse flat-top is visible and that demod
        is working at the specified IF.

        Args:
            if_hz:  IF frequency in Hz.
            window: optional (start_sample, stop_sample) to crop the x-axis.
        """
        dig = self.instruments['dig']

        logger.debug('Setting IF to %.1f MHz and reloading sequence', if_hz / 1e6)
        self._set_if(dig, if_hz)
        self.stop_awgs()
        self.load(self.generate())
        self.start_awgs()

        logger.debug('Taking averaged shot at IF=%.1f MHz', if_hz / 1e6)
        dig.setup_avg_shot()
        dig.arm()
        dig.start_hvi()
        ret = dig.take_avg_shot(take_ref=False)
        dig.stop_hvi()
        dig.release_buf()

        if_period    = dig.get_if_period()
        sampling_rate = dig.get_sample_rate()
        logger.debug('Digitizer returned %d bins with if_period=%d samples, and sampling_rate=%.2f Hz',
            len(ret), if_period, sampling_rate)
        plot_iq_trace(ret, if_hz, if_period, dig.get_naverages(), SAMPLING_RATE=sampling_rate)

    def generate(self):
        """Build and return a rendered AWG sequence.

        The AWG waveform is independent of IF — the same readout tone is used
        at every sweep point.  Only the digitizer demod LO changes between points.

        Sequence:
            Trigger(pre_trigger_pad) → do_get_sequence() → Delay(post_readout_pad)
        """
        trigger_period_samples = self.instruments['dig'].get_trigger_period() * _SAMPLES_PER_US
        seq_len = self.pre_trigger_pad + self._pulse_total_samples() + self.post_readout_pad
        assert seq_len <= trigger_period_samples, (
            "sequence length %d samples exceeds trigger_period %d samples "
            "(%d µs). Reduce pulse_width or post_readout_pad." % (
                seq_len, trigger_period_samples,
                self.instruments['dig'].get_trigger_period())
        )

        s = Sequence()
        s.append(Trigger(self.pre_trigger_pad))
        s.append(self.readout_driver.do_get_sequence())
        s.append(Delay(self.post_readout_pad))

        s = self.get_sequencer(s)
        seqs = s.render()

        assert seqs is not None and len(seqs) > 0, \
            "sequencer produced no output — check AWG channel mapping"
        return seqs

    def measure(self):
        dig = self.instruments['dig']

        assert dig is not None, \
            "'dig' not in instruments — was create_instruments.py run?"

        # AWG sequence is fixed; load once before the IF sweep.
        self.stop_awgs()
        self.load(self.generate())
        self.start_awgs()

        for i, if_hz in enumerate(self.IFs):
            print('(%d/%d) IF = %.1f MHz' % (i + 1, len(self.IFs), if_hz / 1e6), end='\t')

            # --- Set IF on both the digitizer and readout_IQ ---
            # TODO: after _set_if, dig.get_if_period() = int(500e6 / if_hz).
            #       nsamples must be divisible by this new if_period.
            #       If not, setup_avg_shot() or take_avg_shot() will raise.
            #       Consider pre-computing a nsamples that is divisible by all
            #       if_periods in the sweep (LCM), or warn+skip bad points here.
            self._set_if(dig, if_hz)
            if_period = dig.get_if_period()

            # TODO: verify that setup_avg_shot() reinitializes _demodA/_demodB
            #       with the new if_period after _set_if(). Without that, the
            #       demodulator arrays would still be sized for the old if_period.

            data = []
            for shot in range(self.shots_per_average):
                dig.setup_avg_shot()
                dig.arm()
                dig.start_hvi()
                ret = dig.take_avg_shot(take_ref=False)
                dig.stop_hvi()
                dig.release_buf()

                assert ret is not None, \
                    "take_avg_shot returned None at IF=%.1f MHz — DIG not triggered?" % (if_hz / 1e6)

                IQ      = np.average(ret)
                amp_vals = np.abs(ret)
                sem     = np.std(amp_vals) / np.sqrt(len(amp_vals))
                data.append([IQ, amp_vals, sem])

            IQ       = np.mean([d[0] for d in data])
            amp_vals = np.mean([d[1] for d in data], axis=0)
            sem      = np.mean([d[2] for d in data])

            self.ampdata[i]   = np.abs(IQ)
            self.ampstd[i]    = sem
            self.phasedata[i] = np.angle(IQ, deg=True)
            print('amp = %.3f ± %.4f SEM, phase = %.1f deg' % (
                np.abs(IQ), sem, np.angle(IQ, deg=True)))

        self.analyze()

    def analyze(self, data=None, fig=None):
        amps = np.array(self.ampdata[:]) if data is None else np.asarray(data)

        assert len(amps) == len(self.IFs), (
            "amplitude array length %d does not match IFs length %d" % (
                len(amps), len(self.IFs))
        )
        assert np.max(amps) > 0, (
            "all amplitudes are zero — no signal. "
            "Check: RF source on, AWG cables connected, IF within digitizer bandwidth."
        )

        stds    = np.array(self.ampstd[:])
        phases  = np.array(self.phasedata[:])
        IFs_MHz = self.IFs / 1e6

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 6), sharex=True)

        color = 'steelblue'
        ax1.plot(IFs_MHz, amps, 'o-', color=color, lw=1.5, ms=4, label='mean amp')
        if not self.no_error:
            ax1.fill_between(IFs_MHz,
                             amps - stds, amps + stds,
                             alpha=0.35, color=color, label='±SEM')
        ax1.set_ylabel('IQ amplitude [AU]')
        ax1.set_title('Readout IF sweep')
        ax1.legend(fontsize=8)
        ax1.axhline(np.mean(amps), color=color, lw=0.8, ls='--', alpha=0.5)

        ax2.plot(IFs_MHz, phases, 's-', color='tomato', lw=1.5, ms=4, label='phase')
        ax2.set_ylabel('Phase [deg]')
        ax2.set_xlabel('IF [MHz]')
        ax2.axhline(np.mean(phases), color='tomato', lw=0.8, ls='--', alpha=0.5,
                    label='mean %.1f°' % np.mean(phases))
        ax2.legend(fontsize=8)

        plt.tight_layout()
        plt.show()

        print('Mean amplitude: %.3f' % np.mean(amps))
        return np.mean(amps)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
        description=(
            'Readout IF sweep.\n'
            '  --if X      : single-shot inspection at IF=X MHz (show_pulse only, no data saved).\n'
            '  (no args)   : full sweep from --min-if to --max-if.'
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        '--debug', action='store_true',
        help='Enable DEBUG-level logging (default is WARNING).',
    )
    parser.add_argument(
        '--if', type=float, default=None, metavar='MHZ', dest='if_mhz',
        help='IF in MHz for single-shot show_pulse inspection.',
    )
    parser.add_argument(
        '--min-if', type=float, default=10.0, metavar='MHZ',
        help='Minimum IF for the full sweep in MHz. Default: 10.',
    )
    parser.add_argument(
        '--max-if', type=float, default=100.0, metavar='MHZ',
        help='Maximum IF for the full sweep in MHz. Default: 100.',
    )
    parser.add_argument(
        '--npoints', type=int, default=25, metavar='N',
        help='Number of evenly-spaced IF points in the full sweep. Default: 25.',
    )
    parser.add_argument(
        '--nsamples', type=int, default=None, metavar='SAMPLES',
        help='Override dig.nsamples. Must be a multiple of if_period for every IF in the sweep.',
    )
    parser.add_argument(
        '--naverages', type=int, default=None, metavar='N',
        help='Override dig.naverages. More averages reduce shot-to-shot noise by sqrt(N). '
             'Default: leave digitizer setting unchanged.',
    )
    parser.add_argument(
        '--shots-per-average', type=int, default=2, metavar='N',
        help='Number of shots to run per average. Default: 2.',
    )
    parser.add_argument(
        '--raw', action='store_true',
        help='Force naverages=1 before running --if (single-shot; pulse envelope visible).',
    )
    parser.add_argument(
        '--no-error', action='store_true',
        help='Do not plot error bars.',
    )

    args = parser.parse_args()

    from mclient import instruments

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    for _noisy in ('matplotlib',):
        logging.getLogger(_noisy).setLevel(logging.WARNING)

    import matplotlib
    matplotlib.use('Qt5Agg')

    dig = instruments['dig']

    logger.info(dig.scan())

    if args.nsamples is not None:
        dig.set_nsamples(args.nsamples)
    if args.naverages is not None:
        dig.set_naverages(args.naverages)
    if args.raw:
        dig.set_naverages(1)

    readoutargs = dict(readout='readout_IQ', no_error=args.no_error, shots_per_average=args.shots_per_average)

    if args.if_mhz is not None:
        # Single-shot inspection at the specified IF.
        m = ReadoutIFSweep(
            IFs=np.array([args.if_mhz * 1e6, args.if_mhz * 1e6 + 1e6]),  # dummy 2-point array
            **readoutargs
        )
        m.show_pulse(if_hz=args.if_mhz * 1e6)
    else:
        # Full sweep from min-if to max-if.
        IFs = np.linspace(args.min_if * 1e6, args.max_if * 1e6, args.npoints)
        m = ReadoutIFSweep(IFs=IFs, **readoutargs)
        m.measure()
