import hashlib
import logging
import time
import numpy as np

from lib.file_support import awg_files

# JEFF: extra timeout margin helps slow AWGs finish loading large sequences.
AWG_TIMEOUT = 2400000
AWG_TIMEOUT_SHORT = 100e4
NGROUP = 100

LOGGER = logging.getLogger(__name__)


def chars_in_str(chars, s):
    return any(ch in s for ch in chars)


class AWGLoader:

    def __init__(
        self, hashname=True, bulkload=False, fileload=False, dot_awg_path=None
    ):
        self._awgs = {}
        self._loaded_wforms = []
        self._hashname = hashname
        self._active_awgs = []
        self._bulkload = bulkload
        self._fileload = fileload
        self._dot_awg_path = dot_awg_path  # For fileload.

    def add_awg(self, awg, ch_map):
        self._awgs[awg] = ch_map

    def get_awgs(self):
        return list(self._awgs.keys())

    def get_active_awgs(self):
        return self._active_awgs

    # JEFF: check if awg is running to see if priming is done.
    # def is_awg_running(self):
    #     ...

    def _mark_active(self, awg):
        if awg not in self._active_awgs:
            self._active_awgs.append(awg)

    def _is_hashable_wname(self, wname):
        return self._hashname and (
            len(wname) > 64 or chars_in_str("(),", wname)
        )

    def load_file(self, seqs, delay_override=False):
        for awg, ch_map in self._awgs.items():
            start = time.perf_counter()

            seqs_to_load = {}
            for dst_ch, src_ch in ch_map.items():
                if src_ch in seqs:
                    m1seq = seqs.get('%sm1'%src_ch, None)
                    m2seq = seqs.get('%sm2'%src_ch, None)
                    seqs_to_load[dst_ch] = seqs[src_ch]
                    seqs_to_load[f"{dst_ch}m1"] = m1seq
                    seqs_to_load[f"{dst_ch}m2"] = m2seq
                    self._mark_active(awg)

            awgld = awg_files.Dot_AWG_Load(
                seqs_to_load, path=self._dot_awg_path, awg=awg
            )
            awgld.load_seqs(delay_override=delay_override)

            dt = time.perf_counter() - start
            LOGGER.info("Loaded %s in %.03f sec", awg.get_name(), dt)

    def load_direct(self, seqs):
        for awg, ch_map in self._awgs.items():
            seqlen = None
            for dst_ch, src_ch in ch_map.items():
                if src_ch in seqs:
                    seqlen = len(seqs[src_ch].seq)
                    break
            if seqlen is None:
                continue
            LOGGER.info("Sequence length is %d", seqlen)

            # Clearing the AWG first can take a while on large waveform sets.
            awg.delete_all_waveforms(timeout=AWG_TIMEOUT)
            self._loaded_wforms = []
            awg.setup_sequence(seqlen, reset=True, loop=True)

            for dst_ch, src_ch in ch_map.items():
                if src_ch in seqs:
                    m1seq = seqs.get('%sm1'%src_ch, None)
                    m2seq = seqs.get('%sm2'%src_ch, None)
                    self.load_channel_sequence(awg, dst_ch, seqs[src_ch], m1seq, m2seq)
                    awg.wait_done(timeout=AWG_TIMEOUT_SHORT)
                    self._mark_active(awg)

    def load(self, seqs, delay_override=False):
        """
        Load sequence to AWGs.
        If this instance has fileload=True it will write .awg files.
        Otherwise it talks to the AWGs directly.
        <delay_override> specifies how long the timeout to wait after file
        loading is (the AWG can be slow to respond).
        (fileload and dot_awg_path can be set in config.py)
        """

        self._active_awgs = []
        if self._fileload:
            return self.load_file(seqs, delay_override=delay_override)
        return self.load_direct(seqs)

    def set_all_awgs_active(self):
        self._active_awgs = self.get_awgs()

    def run(self):
        """
        Some AWGs have the issue that they throw the marker channels high
        when not in run mode, so we have to do it in this order.
        Function generator should be stopped at this point so that the
        AWG does not start outputting already.
        """

        for awg in self._active_awgs:
            LOGGER.info("Starting %s", awg.get_name())
            LOGGER.info("...turning on channels")
            awg.all_on()

            LOGGER.info("...set to run mode")
            awg_name = awg.get_name()
            awg.run()

            # AWGs sometimes take a while to start running, especially for
            # long sequences. We allow for a delay for the AWG to catch up.
            state = 0
            for tries in range(10):
                if state != 0:
                    break
                try:
                    state = awg.get_runstate()
                except Exception as exc:
                    LOGGER.info("%s (%d): %s", awg_name, tries, exc)
                    time.sleep(2)
            if state == 0:
                err_msg = "AWG %s did not run." % (awg.get_name(),)
                LOGGER.error(err_msg)
                raise Exception(err_msg)

            LOGGER.info("...took %d tries to get ready.", tries)

        LOGGER.info("...waiting for trigger")

    def stop(self):
        # This should also reset the AWGs to state 0, I think.
        LOGGER.info("Stopping AWGs")
        for awg in self._active_awgs:
            awg.stop()

    def _get_wname_m1m2(self, p, m1seq, m2seq, i_seq):
        """
        Get name of waveform including marker waveforms
        """

        wname = p.name
        m1 = None
        m2 = None
        if m1seq and np.count_nonzero(m1seq.seq[i_seq].data) > 0:
            m1 = m1seq.seq[i_seq]
            wname += "_m1%s" % m1.name
            m1 = m1.data
        if m2seq and np.count_nonzero(m2seq.seq[i_seq].data) > 0:
            m2 = m2seq.seq[i_seq]
            wname += "_m2%s" % m2.name
            m2 = m2.data
        if self._is_hashable_wname(wname):
            wname = hashlib.md5(wname.encode()).hexdigest()

        if wname not in self._loaded_wforms:
            return True, wname, m1, m2
        else:
            return False, wname, m1, m2

    def load_channel_sequence_simple(
        self, awg, chan, seq, m1seq=None, m2seq=None
    ):
        """
        Load sequence for a particular channel.
        """
        LOGGER.info(
            "Loading sequence with %d elements to channel %s on %s",
            len(seq.seq),
            chan,
            awg.get_name(),
        )

        for i_seq, p in enumerate(seq.seq):
            load, wname, m1, m2 = self._get_wname_m1m2(p, m1seq, m2seq, i_seq)
            if load:
                LOGGER.info(
                    "Loading waveform %s (%d bytes)", wname, len(p.data)
                )
                awg.add_waveform(wname, p.data, m1=m1, m2=m2, replace=True)
                self._loaded_wforms.append(wname)

            awg.set_seq_element(
                chan,
                i_seq + 1,
                wname,
                p.repeat,
                p.trigger,
                timeout=AWG_TIMEOUT,
            )
        LOGGER.info("Completed channel %s on %s", chan, awg.get_name())

    def load_channel_sequence_bulk(
        self, awg, chan, seq, m1seq=None, m2seq=None
    ):
        """
        Load sequence for a particular channel.
        """
        LOGGER.info(
            "Bulk loading sequence with %d elements to channel %s on %s",
            len(seq.seq),
            chan,
            awg.get_name(),
        )

        bulk_wforms = []
        bulk_wform_len = 0
        bulk_seq = []

        for i_seq, p in enumerate(seq.seq):
            load, wname, m1, m2 = self._get_wname_m1m2(p, m1seq, m2seq, i_seq)
            if load:
                bulk_wforms.append((wname, p.data, m1, m2))
                self._loaded_wforms.append(wname)
                bulk_wform_len += len(p.data)

                # Load if waveform length large enough
                if bulk_wform_len > 50000:
                    awg.bulk_waveform_load(bulk_wforms, timeout=AWG_TIMEOUT)
                    bulk_wforms = []
                    bulk_wform_len = 0

            # Queue sequences for loading
            bulk_seq.append((i_seq + 1, wname, p.repeat, p.trigger))

        # Load remaining waveforms and sequence data
        awg.bulk_waveform_load(bulk_wforms, timeout=AWG_TIMEOUT)
        awg.bulk_sequence_load(chan, bulk_seq, timeout=AWG_TIMEOUT)

    def load_channel_sequence(self, awg, chan, seq, m1seq=None, m2seq=None):
        if (
            self._bulkload
            and hasattr(awg, "bulk_waveform_load")
            and hasattr(awg, "bulk_sequence_load")
        ):
            return self.load_channel_sequence_bulk(
                awg, chan, seq, m1seq=m1seq, m2seq=m2seq
            )
        return self.load_channel_sequence_simple(
            awg, chan, seq, m1seq=m1seq, m2seq=m2seq
        )
