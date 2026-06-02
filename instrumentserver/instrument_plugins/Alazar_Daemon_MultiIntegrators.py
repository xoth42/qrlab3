# Alazar acquisition daemon.
#
# This daemon provides 2 shared objects:
# - AlazarCard, to directly set channel parameters
# - AlazarDaemon, to manage buffers and perform the actual acquisition

import sys
import copy
import ctypes
import types
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
mpl.rcParams['legend.fontsize'] = 8
import time
from lib.dll_support import alazar
AC = alazar.Constants
from lib.math import demod
from lib.math import excise
from .instrument import Instrument
import logging
import gc
import os

#from instrumentserver.instrument_plugins import Alazar_Daemon.
from instrumentserver.instrument_plugins.Alazar_Daemon import Alazar_Daemon

import objectsharer as objsh
#objsh.logger.setLevel(logging.DEBUG)
#import mclient

#objsh.backend.connect_to('tcp://127.0.0.1:55555')
#instruments = objsh.find_object('instruments')

import config
alazar_temp = config.alazar_data_temp

class Alazar_Daemon_MultiIntegrators(Alazar_Daemon):
    '''
        This class extends the base Alazar_Daemon class to add flexibility in the following ways:
        - ability to excise multiple sections of a measurement trace.
        - these excises sections may be integrated (with Trajecto ry_Integrator) an arbitrary number of times
        - this class returns data back in time ordered form

    '''

    def __init__(self, name, **kwargs):
        super(Alazar_Daemon_MultiIntegrators, self).__init__(name, **kwargs)
#        from mclient import instruments
#        self.instruments = instruments

        # TODO set to 1 if not using new excise_demod
        self.update_interval = 10

        # integration and weight functions will be applied by calling separate functions
#        self.remove_parameter('weight_func')

    def break_records_mi(self, cycles):
        self._cycles = cycles
        self._navg = self.get_naverages()

        nsamples = self.get_nsamples()
        naverages = self.get_naverages()

        MAX_BUFFER_SIZE = 20e6#24e6 # 24 MB
        BYTES_PER_NS = 2.0

        size_per_expt = cycles * nsamples * BYTES_PER_NS
        total_num_byts = size_per_expt*naverages
        cyclereps = MAX_BUFFER_SIZE // size_per_expt # cycle reps per buffer

#        cyclereps = max(MAX_BUFFER_SIZE // size_per_expt, 1) # cycle reps per buffer

#        cyclereps = MAX_BUFFER_SIZE / size_per_expt # approx # buffers
#        cyclereps = np.ceil(cyclereps)

        print(f'Cyclereps: {cyclereps}')

        assert cyclereps > 0

        cyclereps = min(cyclereps, naverages)
        self._cyclereps = cyclereps
        self._num_buffers_to_fill = naverages // cyclereps

        # delete this if using new take_excise_demod
#        if naverages % cyclereps != 0:
#            self._num_buffers_to_fill += 1

        # TODO updated: add requested buffers to ensure we end with a temp buffer update
        if naverages % (cyclereps * self.update_interval) != 0:
            nbufs = int(self._num_buffers_to_fill)
            self._num_buffers_to_fill = (int(nbufs)/self.update_interval + 1) * self.update_interval

        self.recperbuf = cyclereps * cycles

        print(f'Recperbuf {self.recperbuf}')
        print(f'number of buffers to fill {self._num_buffers_to_fill} ')

    def setup_alazar(self, cycles):
        '''
        Prepare alazar for capture, and begin capture.  Sets up records per
        buffer, buffer size, etc, allocates buffers, and finally begins filling
        them.
        '''
        self.end_capture()

        self.break_records_mi(cycles)

        self.set_nrecperbuf(self.recperbuf)
        self.set_ntotal_rec(self._num_buffers_to_fill * self.recperbuf)
        self.set_nbuffers(50)
        self.allocate_buffers()

        logging.info(f'number of buffers; {int(self.get_nbuffers())}')
        logging.info(f'Setup alazar: cycle repetitions {int(self._cyclereps)}, recs per buf {int(self.recperbuf)}, total records {int(self._num_buffers_to_fill * self.recperbuf)}',
                     )

#        periods = self.get_nsamples() / self.get_if_period()
#        self.set_demod(avg_periods=periods)
        timeout = min(50000 + 2000 * self._cycles, 600000)
        self.set_timeout(timeout)

        self.prepare_capture()
        self._card.post_buffers(self._bufs)
        self.start_capture()

    def setup_excise_demod(self,
                           excise_list,
                           integrate,
                           integrator_schedule,
                           rawbuf=None,
                           intbuf=None):
        '''
            NOTE THAT CYCLES MUST BE SPECIFIED BY len of <excise_list>
            TEMP: <max_integrators> specifies the maximaum number of integrators for
            a given excise--this can and should be determined by the shape of
            <integrator_schedule>
            - Setup alazar card for taking data
            - setup excise list for parsing data
            - setup integrators for processing excises
            - setup data buffers for raw data and integrated data

        '''
#        if rawbuf is not None:
#            logging.info('rawbuf shape %s' % (rawbuf.shape,))

#        self.setup_alazar(cycles)
        logging.info('setup_excise_demod')

        self._cycles = len(excise_list)
        self.excise_list = excise_list
        self.integrate = integrate
#        self.data = data
        self.integrator_schedule = integrator_schedule

#        logging.info('calling ti_lq directly')
#        ti_hq = self.instruments['ti_lq']
#        logging.info('done calling ti_lq')

#        self.integrator_schedule = []
#        for ti_cycle in integrator_schedule:
#            cycle = []
#            for ti_excise in ti_cycle:
##                logging.info('building integrator_schedule list %s' % (ti_excise))
#                cycle.append(self.instruments[ti_excise])
#            self.integrator_schedule.append(cycle)

        logging.info('done integrator_schedule list')
#        self.intruments[self_integrator_schedul[i]]

        self.break_records_mi(self._cycles)
        logging.info('done breaking records')

        self.excisor = excise.ExciseDemodulate(excise_list,
                           if_period=self.get_if_period(),
#                           naverages=self._cyclereps)
                           naverages=self._cyclereps*self.update_interval)
       # TODO: updated for temp buffers

        # max number of excise segments and the max excise length
        self.excise_num = self.excisor.excise_num
        self.excise_len = self.excisor.excise_len/self.get_if_period()

        logging.info('excise_demod: finished setting up excisor')
        # contains excised data before integrated
        rawbuf_shape = (self.get_naverages(),
                        self._cycles,
                        self.excise_num,
                        self.excise_len)
#        logging.info(rawbuf_shape)
        if rawbuf is None:
            logging.info('generating IQraw')
            self.IQraw = np.full(rawbuf_shape,
                               np.nan + 1j*np.nan,
                               dtype=np.complex64)
        else:
            logging.info('using IQraw')
#            rawbuf.setflags(write=True)
            self.IQraw = rawbuf

#        self.IQraw.setflags(write=True)

            # NOTE: self.IQraw.shape (IQraw is nparray) causes a timeout
#            logging.info('set IQraw')
#            if type(self.IQraw) is np.ndarray:
#                logging.info('data_shape np array')
#                data_shape = self.IQraw.shape
#                logging.info(data_shape)
#            else:
#                logging.info('data shape objectsharer')
#                data_shape = self.IQraw.get_shape()
#            logging.info('before compare')
#
#            if list(data_shape) != list(rawbuf_shape):
#                raise ValueError('raw buffer shape is not correct!')
        logging.info('starting intbuf')
#         contains integrated according to integrator_schedule
        intbuf_shape = (self.get_naverages(),
                        self._cycles,
                        self.excise_num,)
        logging.info(f'{intbuf_shape}')
        if intbuf is None:
            logging.info('generating intbuf')
            self.intbuf = np.full(intbuf_shape,
                                  np.nan,
                                  dtype=np.float32)
        else:
            logging.info('in inbuf')
            self.intbuf = intbuf
#            if type(self.intbuf) is np.ndarray:
#                data_shape = self.intbuf.shape
#            else:
#                data_shape = self.intbuf.get_shape()
#            if list(data_shape) != list(intbuf_shape):
#                raise ValueError('int buf shape is not correct!')

        self.setup_alazar(self._cycles)

    def get_IQraw(self):
        return self.IQraw

    def get_intbuf(self):
        return self.intbuf

    def take_excise_demod_old(self, acqtimeout=None):
        '''
        Acquire <naverages> demodulated shots, appyling the excise schedule as
        specified by <excist_list>
        '''

        if acqtimeout is None:
            acqtimeout = self.get_timeout()
        print(acqtimeout)

        buf_index = 0
        nsamples = self.get_nsamples()
        nrecperbuf = self.get_nrecperbuf()
        buf_len = nrecperbuf * nsamples
        update_interval = 5
        for i in range(self._num_buffers_to_fill):
            if (i % update_interval) == 0:
                logging.info(f'Acquiring {int(i)}'*self._cyclereps, )
                self.emit('capture-progress', i*self._cyclereps)
                # save data

            buf = self.get_next_buffer(acqtimeout)

            bufA = np.reshape(buf[:buf_len], (nrecperbuf, nsamples))
            bufB = np.reshape(buf[buf_len:], (nrecperbuf, nsamples))

            start = int(i*self._cyclereps)
            end = int(min((i+1)*self._cyclereps, self.get_naverages()))
            delta = end - start
            logging.info(f'saving cycle average {int(start)} to {int(end)}, delta = {int(delta)}')

            start_time = time.clock()
            iqraw_data = self.excisor.apply_excise_demod(bufA, bufB)[:delta]
            logging.info(f'apply_excise_demod: {1000000.0 * (time.clock() - start_time):0.3f}')

            self.IQraw[start:end,:,:,:] = iqraw_data

#            start_time = time.clock()
            if self.integrate:
#                self.apply_integrators(iqraw_data, self.intbuf, start, end)
                self.apply_integrators_cycle(iqraw_data, self.intbuf, start, end)

#            logging.info('apply_integrators: %0.3f' % (1e6*(time.clock() - start_time)))

            self._card.post_buffers(buf)

#        self._hist_buf[buf_index:buf_index+len(tmp_buf)] = tmp_buf

        self.end_capture()

        return self.intbuf #self.IQraw
#        return bufA, bufB

    def take_excise_demod(self, acqtimeout=None):
        '''
        EXPERIMENTAL - currently creating a buffer to decrease the frequency
        of excise_demod + integrate calls.
        Acquire <naverages> demodulated shots, appyling the excise schedule as
        specified by <excist_list>
        '''

        if acqtimeout is None:
            acqtimeout = self.get_timeout()

        buf_index = 0
        nsamples = self.get_nsamples()
        nrecperbuf = self.get_nrecperbuf()
        buf_len = nrecperbuf * nsamples
        update_interval = self.update_interval

        # prepare averaging buffer
        multi_buf_shape = (nrecperbuf*update_interval, nsamples)
#        bufA = np.full(multi_buf_shape, np.nan, np.complex64)
#        bufB = np.full(multi_buf_shape, np.nan, np.complex64)

        bufA = np.empty(multi_buf_shape, np.complex64)
        bufB = np.empty(multi_buf_shape, np.complex64)

        logging.info(f'multi_buf_shape = {multi_buf_shape}')

        for i in range(self._num_buffers_to_fill):
            buf = self.get_next_buffer(acqtimeout)

            A = np.reshape(buf[:buf_len], (nrecperbuf, nsamples))
            B = np.reshape(buf[buf_len:], (nrecperbuf, nsamples))

            order = i % update_interval
            bufA[nrecperbuf*order:nrecperbuf*(order+1),:] = A
            bufB[nrecperbuf*order:nrecperbuf*(order+1),:] = B

            logging.info(f'filled temp buffer : {int(i)}, {int(order)}')
            self._card.post_buffers(buf)

            if (i % update_interval) == 0:
                logging.info(f'Acquiring {int(i)}'*self._cyclereps, )
                self.emit('capture-progress', i*self._cyclereps)

                idx = (i/update_interval)-1
                start = int(idx*update_interval*self._cyclereps) #int(i*update_interval*self._cyclereps)
                end = int(min((idx+1)*update_interval*self._cyclereps,
                              self.get_naverages()))
                delta = end - start
                logging.info(f'processing cycle average {int(start)} to {int(end)}, delta = {int(delta)}')

                start_time = time.clock()
                iqraw_data = self.excisor.apply_excise_demod(bufA, bufB)[:delta]
                logging.info(f'apply_excise_demod: {1000.0 * (time.clock() - start_time):0.3f} ms')
#                logging.info('bufA.shape: %s' % ((bufA.shape,)))

                self.IQraw[start:end,:,:,:] = iqraw_data

                start_time = time.clock()
                if self.integrate:
    #                self.apply_integrators(iqraw_data, self.intbuf, start, end)
                    self.apply_integrators_cycle(iqraw_data, self.intbuf, start, end)
                logging.info(f'apply_integrators: {1000.0 * (time.clock() - start_time):0.3f} ms')

#                start_time = time.clock()
#                bufA *= np.nan
#                bufB *= np.nan
#                logging.info('nans: %0.3f ms' % (1e3*(time.clock() - start_time)))

#        self._hist_buf[buf_index:buf_index+len(tmp_buf)] = tmp_buf

        self.end_capture()

        return self.intbuf #self.IQraw
#        return bufA, bufB

    def apply_integrators(self, iqraw_data, outbuf, start, stop):
        '''
        Integrate raw IF data from <iqraw_data> and apply to <out_buf>.

        iqraw passed as np array
        outbuf passed as dataset
        '''
#        data = np.empty_like(out_buf,
#                       dtype=np.complex64)

        iqraw_shape = iqraw_data.shape
        # outbuf shape function call depends if outbuf is wrapped as an ObjectProxy object
        if type(outbuf) is np.ndarray:
            outbuf_shape = outbuf.shape
        else:
            outbuf_shape = outbuf.get_shape()#note start, stop
#        if outbuf_shape != iqraw_shape[:-1]:
#            raise ValueError('apply_integrators: outbuf shape is not correct! iqraw: %s vs. outbuf: %s' % (iqraw_shape, outbuf_shape))

        # since outbuf is actually a dataserver call, fill a local buffer and
        # make one call to outbuf at the end.
        local_buf = np.full((stop-start,outbuf_shape[1], outbuf_shape[2],), np.nan, np.float)

        for cidx, int_cycle in enumerate(self.integrator_schedule):
            for eidx, integrator in enumerate(int_cycle):
                ret = integrator.process_data(iqraw_data[:,cidx,eidx,:])#, totlen=self.excise_len)


#                outbuf[start:stop,cidx,eidx] = ret
                local_buf[:,cidx,eidx] = ret

        outbuf[start:stop,:,:] = local_buf


    def apply_integrators_cycle(self, iqraw_data, outbuf, start, stop):
        '''
        Integrate raw IF data from <iqraw_data> and apply to <out_buf>.

        iqraw passed as np array
        outbuf passed as dataset

        IMPORTANT: This version assumes that the integrator schedule is the same for all cycles.
        '''
#        data = np.empty_like(out_buf,
#                       dtype=np.complex64)

        iqraw_shape = iqraw_data.shape
        # outbuf shape function call depends if outbuf is wrapped as an ObjectProxy object
        if type(outbuf) is np.ndarray:
            outbuf_shape = outbuf.shape
        else:
            outbuf_shape = outbuf.get_shape()#note start, stop
#        if outbuf_shape != iqraw_shape[:-1]:
#            raise ValueError('apply_integrators: outbuf shape is not correct! iqraw: %s vs. outbuf: %s' % (iqraw_shape, outbuf_shape))

        # since outbuf is actually a dataserver call, fill a local buffer and
        # make one call to outbuf at the end.
        local_buf = np.full((stop-start, outbuf_shape[1], outbuf_shape[2],), np.nan, np.float)
        # shape: (cycle_avgs, cycle, IQs)

        int_cycle = self.integrator_schedule[0]

        start_time = time.clock()
        for eidx, integrator in enumerate(int_cycle):
#            logging.info('iqraw_data = %s' % (iqraw_data[:,:,eidx,:].shape,))
            iqraw_flatcycle = np.swapaxes(iqraw_data[:,:,eidx,:], 0, 1)
            iqraw_flatcycle = np.concatenate((iqraw_flatcycle), axis=0)

#            start_time = time.clock()
            ret = integrator.process_data(iqraw_flatcycle)
#            logging.info('process_data took %0.3f ms' % ((time.clock()-start_time)*1e3))

            # reshape (cycles, avg)
            ret = np.reshape(ret, (outbuf_shape[1],stop-start,))
            # swap so that data is saved as (avg, cycles)
            local_buf[:,:,eidx] = np.swapaxes(ret, 0, 1)

#        logging.info('process_data took %0.3f ms' % ((time.clock()-start_time)*1e3))

        outbuf[start:stop,:,:] = local_buf
#        logging.info('process_data2 took %0.3f ms' % ((time.clock()-start_time)*1e3))


#        for cidx, cycle_tuple in enumerate(self.integrator_schedule):
#            for eidx, excise_tuple in enumerate(cycle_tuple):
#                for iidx, integrator in enumerate(excise_tuple):
#                    ret = integrator.process_data(iqraw_data[:,cidx,eidx,:])#, totlen=self.excise_len)

#                    outbuf[start:stop,cidx,eidx,iidx] = ret


#            self._demodA.demodulate(buf[:Nperbuf*nsamples])
#            IQA = self._demodA.IQ.reshape([Nperbuf, periods])
#
#            # Calculate reference angles
#            self._demodB.demodulate(buf[Nperbuf*nsamples:])
#            IQB = self._demodB.IQ.reshape([Nperbuf, periods])
#            refs = np.exp(-1j * np.angle(np.average(IQB, 1)))
#            IQA = IQA * refs[:, np.newaxis]
#
#            # Use weighting function
#            if self._Iweight is not None:
#                IQr[i:i+Nperbuf,:] = self.apply_IQ_weight(IQA, Iweight, Qweight)
#            else:
#                IQr[i:i+Nperbuf,:] = IQA

#            self._card.post_buffers(buf)
#            recs_so_far += Nperbuf
#
#        self.end_capture()
#
#        return self.convert_signal(np.array(IQr))


