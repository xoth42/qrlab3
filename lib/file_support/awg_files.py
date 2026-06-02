'''
Jacob Blumoff 6/24/2014
'''

import numpy as np
import struct
import time
import hashlib


import glob
import os

import config

def clear_dot_awgs(path=None, delete='all'):
    #Todo:  Pull path from config, delete by date/time
    if path is None:
        path, _ = os.path.split(config.dot_awg_path)

    key = os.path.join(path, '*.awg')
    dalist = glob.glob(key)
    for idx,item in enumerate(dalist):
        marked_for_death = True

        if marked_for_death:
            os.remove(item)
            print(f'Deleting ({idx + 1}/{len(dalist)}): {item}')
    pass

NULL = chr(0)

'''Make sure the AWG has the path loaded, and that it's mounted as
the same drive letter.'''

class Dot_AWG_Load():
    def __init__(self, seqs, path=None, awg=None):
        '''At a high level this will only know about one AWG.
        Each seqs will already be predivided into the relevant channels
        '''
        self.awg = awg
        self.seqs = seqs
        stem, _ = os.path.splitext(path)
        self.path = stem + str(int(time.time() * 1000)) + '.awg'

        self.rl = [] #initial record list
        self.loaded_wfs = [] #List of names of loaded wfs
        self.admin_duty = 1 #Triggering, looping, repeating:  only done once

    def load_seqs(self, delay_override = 600e3, verbose = False):
        '''The main routine'''

        MAX_ATTEMPTS = 6
        self.parse_seqs()

        for load_attempt_no in range(MAX_ATTEMPTS):
            print('beginning attempt')
            try:
                self.pull_stubborn_params()
                print('params pulled')
                self.clear_awg_and_pull_data(delay_override)
                print('cleared awg and pulled data')

                self.write_attempt_no = 0
                self.write_wrapper()
                print('finished write wrapper')

                self.awg.load_dot_awg(self.path)
                print('loaded dog awg')
                if delay_override:
                    self.awg.wait_getID(delay=delay_override, timeout=delay_override)
                self.restore_stubborn_params()

                self.check_seq_length()
                return

            except Exception as e:
                if load_attempt_no != MAX_ATTEMPTS - 1:
                    msg = f'Failed AWG load ({e}), big loop, retrying. ({load_attempt_no}/{MAX_ATTEMPTS}) '
                    print(msg)
                else:
                    print('ABORTING, LOAD FAILURE')
                    print(f'{e}')
                    raise Exception('AWG load failed')

    def clear_awg_and_pull_data(self, delay):
        '''Delete all of the waveform and sequence memory, save a .awg
        file that contains only the device settings.
        The timeout=delay makes ObjectSharer wait long enough for the AWG
        process to respond'''
        self.awg.clear_sequence(timeout=delay)
        self.awg.delete_all_waveforms(wait=delay, timeout=delay) #wait = timeout.  Deleting
                                                  #large expts can take a while.
        self.awg.wait_getID(timeout=delay)
        self.awg.pull_dot_awg(self.path, timeout=delay)

    def pull_stubborn_params(self):
        '''This is where we handle params that aren't maintained by
        restoring the .awg  (there aren't many of them and we're not
        totally sure why this is necessary)'''
        self.offsets = []
        for ch in [1,2,3,4]:
            self.offsets.append(self.awg.do_get_offset(ch))
        #also direct output, filter, DC output - to be added
        #Every other setting I've checked looks fine.

    def restore_stubborn_params(self):
        for ch in [1,2,3,4]:
            self.awg.do_set_offset(float(self.offsets[ch-1]),ch)

    def parse_seqs(self):
        '''Calls add waveform for each sequence element'''
        for chan in self.seqs:
            if not isinstance(chan, int):
                continue
            for idx, _ in enumerate(self.seqs[chan]):
                self.add_waveform(idx, chan)
            self.admin_duty = 0 #After the first channel

    def add_waveform(self, idx, chan):
        '''Converts a sequence object into a set of .awg records or
        instructions.  Adds both waveform data and sequence data.'''
        if chan not in self.seqs:
            return

        pulse = self.seqs[chan][idx]
        pulse_name = pulse.get_name()
        pulse_repeat = pulse.repeat
        pulse_len = int(pulse.get_length() // pulse_repeat)
        pulse_data = pulse.get_data()
        pulse_trigger = pulse.get_trigger()

        m1_chan = '%dm1' % chan
        if m1_chan in self.seqs and self.seqs[m1_chan] is not None:
            m1 = self.seqs[m1_chan][idx]
            m1_name = m1.get_name()
            m1_data = m1.get_data()
        else:
            m1_name = 'delay%d' % pulse_len
            m1_data = np.zeros(pulse_len)

        m2_chan = '%dm2' % chan
        if m2_chan in self.seqs and self.seqs[m2_chan] is not None:
            m2 = self.seqs[m2_chan][idx]
            m2_name = m2.get_name()
            m2_data = m2.get_data()
        else:
            m2_name = 'delay%d' % pulse_len
            m2_data = np.zeros(pulse_len)

        idx += 1 #AWG indexing starts at 1
        waveform_name = pulse_name+'_'+m1_name+'_'+m2_name
        # Keep the on-disk AWG record name short and deterministic.
        waveform_name = hashlib.md5(waveform_name.encode('utf-8')).hexdigest()

        if waveform_name not in self.loaded_wfs:
            n_wf = len(self.loaded_wfs)+1 #unique waveform #

            '''each new waveform takes 5 records'''
            self.rl.append(['WAVEFORM_NAME_%d' % n_wf,
                            waveform_name])
            self.rl.append(['WAVEFORM_TYPE_%d' % n_wf,
                            np.array([1], dtype=np.uint16)])
            self.rl.append(['WAVEFORM_LENGTH_%d' % n_wf,
                            np.array([pulse_len], dtype=np.uint32)])
            self.rl.append(['WAVEFORM_TIMESTAMP_%d' % n_wf,
                            self.make_timestamp()])

            '''Combine the analog and marker data into 16 bit words'''
            pulse_data_processed =  self.awg.get_bindata(pulse_data,
                                                     m1=m1_data,
                                                     m2=m2_data)
            self.rl.append(['WAVEFORM_DATA_%d' % n_wf,
                            pulse_data_processed])

            self.loaded_wfs.append(waveform_name)

            if n_wf > 32000:
                raise ValueError('Too many waveforms!  32000 wf limit.')

        '''element by element sequencing'''
        self.rl.append(['SEQUENCE_WAVEFORM_NAME_CH_%d_%d' % (chan,idx),
                        waveform_name])

        if self.admin_duty:
            '''It's important that these are only written once, otherwise
            the awg fails'''
            goto_idx = int(idx == len(self.seqs[chan].seq))
            self.rl.append(['SEQUENCE_GOTO_%d' % (idx),
                            np.array([goto_idx],dtype='<u2')])

            self.rl.append(['SEQUENCE_WAIT_%d' % (idx),
                            np.array([pulse_trigger],dtype='<u2')])

            self.rl.append(['SEQUENCE_JUMP_%d' % (idx),
                            np.array([0],dtype='<u2')])

            self.rl.append(['SEQUENCE_LOOP_%d' % (idx),
                            np.array([pulse_repeat],dtype='<u4')])

    def compose_record(self,name, data):
        '''
        Composes the line-item instructions in the .awg file into the
        proper format.

        name should be an AWG record name, i.e. 'MAGIC' or 'WAVEFORM_NAME_1'
        data is a 1D numpy array or a string.
        '''
        name += NULL #The Record_Name ends in NULL
        name_len = len(name)

        if isinstance(data, str):
            data = data.encode('utf-8')
        if isinstance(data, (bytes, bytearray, memoryview)):
            data = np.frombuffer(data, dtype=np.uint8)
            data = np.concatenate([data, np.array([0], dtype=np.uint8)])
        data_bytes = data.tobytes()
        data_len = len(data_bytes)
        fmt_string = '<II' + '%ds%ds' % (name_len, data_len)

        return struct.pack(fmt_string, name_len, data_len, name, data_bytes)

    def write_dot_awg(self):
        recs = [' ']*len(self.rl)
        for idx,[name,data] in enumerate(self.rl):
            recs[idx] = self.compose_record(name, data)

        try:
            initial_file_size = os.path.getsize(self.path)
            print(f'.AWG file init: {initial_file_size} bytes')
        except OSError:
            raise Exception('Failed at reading init filezise')

        with open(self.path,'ab') as f:
            '''Note the 'a' for appending to the pulled .awg'''
            for rec in recs:
                f.write(rec)

        try:
            final_file_size = os.path.getsize(self.path)
            print(f'.AWG file final: {final_file_size} bytes')
        except OSError:
            raise Exception('Failed at reading final filezise')

    def write_wrapper(self):
        MAX_ATTEMPTS = 6
        self.write_attempt_no += 1
        try:
            self.write_dot_awg()
        except Exception:
            if self.write_attempt_no < MAX_ATTEMPTS:
                print(
                    f'Failed AWG write wrapper, retrying. '
                    f'({self.write_attempt_no}/{MAX_ATTEMPTS}) '
                )
                self.write_wrapper()
            else:
                self.write_attempt_no = 0
                raise Exception('AWG writing failed six times.')

    def make_timestamp(self):
        return np.array([
            2014, 6, 3, 24, 16, 8, 11, 0
        ], dtype=np.uint16)

    def check_seq_length(self):
        val = int(self.awg.ask('SEQ:LENG?'))
        print(f'NUM LOADED SEQS: {val}')
        if val == 0:
            raise Exception('AWG is reporting seq len = 0')
