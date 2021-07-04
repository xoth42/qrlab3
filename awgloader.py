import hashlib
import numpy as np
import logging
import time
from .lib.file_support import awg_files
import os

''' JEFF. Added another 0 to let AWG load '''
AWG_TIMEOUT = 2400000
AWG_TIMEOUT_SHORT = 100e4
NGROUP = 100

def chars_in_str(chars, s):
    for ch in chars:
        if ch in s:
            return True
    return False

class AWGLoader:

    def __init__(self, hashname=True, bulkload=False, fileload=False,
                 dot_awg_path=None):
        self._awgs = {}
        self._loaded_wforms = []
        self._hashname = hashname
        self._active_awgs = []
        self._bulkload = bulkload
        self._fileload = fileload
        self._dot_awg_path = dot_awg_path #For fileload


    def add_awg(self, awg, ch_map):
        self._awgs[awg] = ch_map

    def get_awgs(self):
        return list(self._awgs.keys())

    def get_active_awgs(self):
        return self._active_awgs
        
    ''' JEFF. check if awg is running to see if priming is done '''
#    def is_awg_running(self):
#        for awg in self._active_awgs:
#            try:
#                for i in range(4):
#                    if awg.do_get_output(i):
#                        print('channel', i, 'status', awg.do_get_output(i))
#                        return True
#            except:
#                return False
        

    def load_file(self, seqs, delay_override=False):
        for awg, ch_map in self._awgs.items():
            start = time.clock()

            seqs_to_load = {}
            for dst_ch, src_ch in ch_map.items():
                if src_ch in seqs:
                    m1seq = seqs.get('%sm1'%src_ch, None)
                    m2seq = seqs.get('%sm2'%src_ch, None)

                    seqs_to_load[dst_ch] = seqs[src_ch]
                    seqs_to_load[str(dst_ch)+'m1'] = m1seq
                    seqs_to_load[str(dst_ch)+'m2'] = m2seq

                    if awg not in self._active_awgs:
                        self._active_awgs.append(awg)

            awgld = awg_files.Dot_AWG_Load(seqs_to_load,
                                           path=self._dot_awg_path,
                                           awg=awg)
            awgld.load_seqs(delay_override=delay_override)

            dt = time.clock() - start
            print('Loaded in %.03f sec' % (dt))

    def load_direct(self, seqs):
        for awg, ch_map in self._awgs.items():
            seqlen = None
            for dst_ch, src_ch in ch_map.items():
                if src_ch in seqs:
                    seqlen = len(seqs[src_ch].seq)
                    break
            if seqlen is None:
                continue
            print("sequence length is %d \n" %(seqlen))
            

            awg.delete_all_waveforms(timeout=AWG_TIMEOUT)     # This can take a while
            self._loaded_wforms = []
            awg.setup_sequence(seqlen, reset=True, loop=True)

            for dst_ch, src_ch in ch_map.items():
                if src_ch in seqs:
                    m1seq = seqs.get('%sm1'%src_ch, None)
                    m2seq = seqs.get('%sm2'%src_ch, None)
                    self.load_channel_sequence(awg, dst_ch, seqs[src_ch], m1seq, m2seq)
                    awg.wait_done(timeout=AWG_TIMEOUT_SHORT)
                    if awg not in self._active_awgs:
                        self._active_awgs.append(awg)

            
            
    def load(self, seqs, delay_override=False):
        '''
        Load sequence to AWGs.
        If this instance has fileload=True it will write .awg files.
        Otherwise it talks to the AWGs directly.
        <delay_override> specifies how long the timeout to wait after file
        loading is (the AWG can be slow to respond).
        (fileload and dot_awg_path can be set in config.py)
        '''
        
        self._active_awgs = []
        if self._fileload:
            return self.load_file(seqs, delay_override=delay_override)
        else:
            return self.load_direct(seqs)

    def set_all_awgs_active(self):
        self._active_awgs = self.get_awgs()

    def run(self):
        '''
        Some AWGs have the issue that they throw the marker channels high
        when not in run mode, so we have to do it in this order.
        Function generator should be stopped at this point so that the
        AWG does not start outputting already.
        '''

        for awg in self._active_awgs:
            logging.info('Starting %s' % awg.get_name())
            logging.info('...turning on channels')
            awg.all_on()

            logging.info('...set to run mode')
            awg_name = awg.get_name()
#            print('awgloader run before awg', awg)
            awg.run()

            # AWGs sometimes take a while to start running, especially for
            # long sequences. We allow for a delay for the AWG to catch up.
            i = 0
            state = 0
            while i < 10 and state == 0:
                try:
                    state = awg.get_runstate()
                except Exception as e:
                    logging.info('%s (%d): %s' % (awg_name, i, e))
                    time.sleep(2)
                i += 1
            if i > 10:
                err_msg = 'AWG %s did not run.' % (awg.get_name(),)
                logging.error(err_msg)
                raise Exception (err_msg)

            logging.info('...took %d tries to get ready.' % (i))

        logging.info('...waiting for trigger')

    def stop(self):
        #This should also reset the AWGs to state 0, I think.
        logging.info('Stopping AWGs')
        for awg in self._active_awgs:
            awg.stop()

    def _get_wname_m1m2(self, p, m1seq, m2seq, i_seq):
        '''
        Get name of waveform including marker waveforms
        '''

        wname = p.name
        m1 = None
        m2 = None
        if m1seq and np.count_nonzero(m1seq.seq[i_seq].data) > 0:
            m1 = m1seq.seq[i_seq]
            wname += '_m1%s' % m1.name
            m1 = m1.data
        if m2seq and np.count_nonzero(m2seq.seq[i_seq].data) > 0:
            m2 = m2seq.seq[i_seq]
            wname += '_m2%s' % m2.name
            m2 = m2.data
        if self._hashname and len(wname) > 64 or chars_in_str('(),', wname):
            wname = hashlib.md5(wname).hexdigest()

        if wname not in self._loaded_wforms:
            return True, wname, m1, m2
        else:
            return False, wname, m1, m2

    def load_channel_sequence_simple(self, awg, chan, seq, m1seq=None, m2seq=None):
        '''
        Load sequence for a particular channel.
        '''
#        logging.info('Loading sequence with %d elements to channel %s on %s' % (len(seq.seq), chan, awg.get_name()))

        for i_seq, p in enumerate(seq.seq):
            load, wname, m1, m2 = self._get_wname_m1m2(p, m1seq, m2seq, i_seq)
            if load:
#                logging.info('Loading waveform %s (%d bytes)' % (wname, len(p.data)))
#                print('Inside load_channel_sequence_simple')
                awg.add_waveform(wname, p.data, m1=m1, m2=m2, replace=True)
                self._loaded_wforms.append(wname)

            awg.set_seq_element(chan, i_seq+1, wname, p.repeat, p.trigger, timeout=AWG_TIMEOUT)
        print("completed a channel\n")

    def load_channel_sequence_bulk(self, awg, chan, seq, m1seq=None, m2seq=None):
        '''
        Load sequence for a particular channel.
        '''
        logging.info('Bulk loading sequence with %d elements to channel %s on %s' % (len(seq.seq), chan, awg.get_name()))

        bulk_wforms = []
        bulk_wform_len = 0
        bulk_seq = []

        for i_seq, p in enumerate(seq.seq):
            load, wname, m1, m2 = self._get_wname_m1m2(p, m1seq, m2seq, i_seq)
            if load:
#               logging.info('Loading waveform %s (%d bytes)' % (wname, len(p.data)))
                bulk_wforms.append((wname, p.data, m1, m2))
                self._loaded_wforms.append(wname)
                bulk_wform_len += len(p.data)

                # Load if waveform length large enough
                if bulk_wform_len > 50000:
                    awg.bulk_waveform_load(bulk_wforms, timeout=AWG_TIMEOUT)
                    bulk_wforms = []
                    bulk_wform_len = 0

            # Queue sequences for loading
            bulk_seq.append((i_seq+1, wname, p.repeat, p.trigger))

        # Load remaining waveforms and sequence data
        awg.bulk_waveform_load(bulk_wforms, timeout=AWG_TIMEOUT)
        awg.bulk_sequence_load(chan, bulk_seq, timeout=AWG_TIMEOUT)

    def load_channel_sequence(self, awg, chan, seq, m1seq=None, m2seq=None):
        if self._bulkload and hasattr(awg, 'bulk_waveform_load') and hasattr(awg, 'bulk_sequence_load'):
            return self.load_channel_sequence_bulk(awg, chan, seq, m1seq=m1seq, m2seq=m2seq)
        else:
            return self.load_channel_sequence_simple(awg, chan, seq, m1seq=m1seq, m2seq=m2seq)