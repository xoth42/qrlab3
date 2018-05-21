import mclient
import config
import types
import time
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib import gridspec
import logging
logging.getLogger().setLevel(logging.INFO)
import signal
import objectsharer as objsh
from lib import jsonext
import os
import pulseseq
import awgloader

#from PyQt4 import QtGui
from pulseseq import sequencer
from pulseseq import pulselib

STYLE_IMAGE = 'IMAGE'
STYLE_LINES = 'LINES'

def is_complex(ar):
    return ar.dtype in (np.complex, np.complex64, np.complex128)

class Measurement(object):
    '''
    Measurement class.

    Performs/provides several functions:
    - A 'main loop' for data taking using an Alazar (while staying interactive
    and allowing to interrupt)
    - Setup AWGs (called AWG<n>, n = 1..5)
    - Control function generator (called 'funcgen')

    The procedure to start an experiment is as follows:
    - stop function generator (if present)
    - load AWGs
    - if function generator used:
        - start AWGs
        - arm alazar
        - start function generator
    - Otherwise:
        - arm alazar
        - start AWGs

    This last case sometimes gives weird results because some AWGs throw their
    marker channels high when starting. A function generator (using the sync
    output!) is strongly recommended.
    '''

    def __init__(self, cyclelen,
                     readout='readout',
                     keep_shots=False,
                     name=None,
                     histogram=False,
                     singleshotbin=False,
                     generate=True,
                     fig=None, title='',
                     residuals=True, res_vert=True,
                     release_seqs=True, plot_seqs=False, print_seqs=False,
                     keep_data=True,
                     infos=None,
                     extra_info=None,
                     comment='',
                     use_sync=True,
                     real_signals=False,
                     analysis_func=None,
                     savefig=True,
                     imagetype='png',
                     print_progress=True,
                     ):
        if name is None:
            name = self.__class__.__name__

        self.name = name
        self.cyclelen = cyclelen
        self.histogram = histogram
        self.singleshotbin = singleshotbin
        self.keep_shots = keep_shots
        self.do_generate = generate
        self.real_signals = real_signals
        self.fig = fig
        self.title = title
        self.residuals = residuals
        self.res_vert = res_vert
        self.comment = comment
        self._datacol = None
        self._awgloader = None
        self._old_signal = None
        self._interrupted = False
        self.release_seqs = release_seqs
        self.plot_seqs = plot_seqs
        self.print_seqs = print_seqs
        self.keep_data = keep_data
        self.savefig = savefig
        self.imagetype = imagetype
        self.print_progress = print_progress

        # Build list of info objects
        if infos is None:
            infos = []
        elif type(infos) is types.TupleType:
            infos = list(infos)
        elif type(infos) is not types.ListType:
            infos = [infos,]
        if extra_info is not None:
            if type(extra_info) in (types.ListType, types.TupleType):
                infos.extend(extra_info)
            else:
                infos.append(extra_info)
        self.infos = infos

        self.analysis_func = analysis_func

        self.setup_data(name)

        self.instruments = mclient.instruments
        self.readout_info = mclient.get_readout_info(readout)
        self._funcgen = mclient.instruments.get('funcgen')
        self.use_sync = use_sync

    def setup_data(self, name):
        if self.keep_data:
            self.datafile = mclient.datafile
        else:
            self.datafile = mclient.get_temp_file()

        ts = time.localtime()
        tstr = time.strftime('%Y%m%d/%H%M%S', ts)
        self._timestamp_str = tstr
        self._groupname = '%s_%s'  % (tstr, name)
        self.data = self.datafile.create_group(self._groupname)
        self.data.set_attrs(
            title=self.title,
            comment=self.comment
        )

    def drop_data(self):
        '''
        Remove data from hdf5 file but keep arrays in memory.
        Remove temporary file.
        '''
        try:
            if self.avg_data:
                avgdata = np.array(self.avg_data[:])
            else:
                avgdata = None
            if self.pp_data:
                ppdata = np.array(self.pp_data[:])
            else:
                ppdata = None
            if self.shot_data:
                shotdata = np.array(self.shot_data[:])
            else:
                shotdata = None

            logging.info('Dropping data group %s' % self._groupname)
            del self.datafile[self._groupname]
            mclient.remove_temp_file()
            self.data = None

            self.avg_data = avgdata
            self.pp_data = ppdata
            self.shot_data = shotdata

        except Exception, e:
            logging.warning('Unable to remove data: %s' % str(e))

    def set_parameters(self, **kwargs):
        self.data.set_attrs(kwargs)

    def get_sequencer(self, seqs=None):
        s = pulseseq.sequencer.Sequencer(seqs)

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

        # Add master/slave settings to sequencer
        if hasattr(config, 'slave_triggers'):
            slave_chan = int(config.slave_triggers[0][0].split('m')[0])
            master_awg = ((slave_chan - 1) / 4) + 1
            logging.info('AWG %d seems to be the master' % master_awg)
            for i in range(4):
                ch = 4 * (master_awg - 1) + i + 1
                s.add_master_channel(ch)
                s.add_master_channel('%dm1'%ch)
                s.add_master_channel('%dm2'%ch)

            for chan, delay in config.slave_triggers:
                s.add_slave_trigger(chan, delay)

        # Add channel delays settings to sequencer
        if hasattr(config, 'channel_delays'):
            for ch, delay in config.channel_delays:
                s.add_channel_delay(ch, delay)

        if hasattr(config, 'flatten_waveforms'):
            s.set_flatten(config.flatten_waveforms)

        if hasattr(config, 'channel_convolutions'):
            s.set_flatten(True)
            for ch, path in config.channel_convolutions:
                kernel = np.loadtxt(path)
                s.add_convolution(ch, kernel)
                logging.info('adding convolution channel: %d' % ch)

        return s

    def generate(self):
        '''
        This function should generate the pulse sequence and return it.
        '''
        return None

    def get_awg_loader_old(self):
        '''
        Detect all AWGs and map channels:
        AWG1 gets channel 1-4, AWG2 5-8, etc.
        '''
        if self._awgloader:
            return self._awgloader

        l = awgloader.AWGLoader(bulkload=config.awg_bulkload)
        base = 1
        for i in range(1, 5):
            awg = self.instruments['AWG%d'%i]
            if awg:
                chanmap = {1:base, 2:base+1, 3:base+2, 4:base+3}
                logging.info('Adding AWG%d, channel map: %s', i, chanmap)
                l.add_awg(awg, chanmap)
                base += 4

        self._awgloader = l
        return l

    def get_awg_loader(self):
        '''
        Detect all AWGs and map channels:
        AWG1 gets channel 1-4, AWG2 5-8, etc.
        '''
        if self._awgloader:
            return self._awgloader

        if hasattr(config,'awg_fileload') and hasattr(config,'dot_awg_path'):
            fl = config.awg_fileload
            fp = config.dot_awg_path
        else:
            fl = False
            fp = None

        l = awgloader.AWGLoader(bulkload=config.awg_bulkload,
                                fileload=fl, dot_awg_path=fp)
        base = 1
        for i in range(1, 5):
            awg = self.instruments['AWG%d'%i]
            if awg:
                chanmap = {1:base, 2:base+1, 3:base+2, 4:base+3}
                logging.info('Adding AWG%d, channel map: %s', i, chanmap)
                l.add_awg(awg, chanmap)
                base += 4

        self._awgloader = l
        return l

    def load(self, seqs, run=False, ntries=1):
        '''
        Load sequences <seqs> to awgs.
        awgs are located from the instruments list and should be named
        AWG1, AWG2, ... (up to 4 currently).
        '''
        
        start = time.clock()
        l = self.get_awg_loader()
        for i in range(ntries):
            try:
                l.load(seqs)
                break
            except Exception, e:
                logging.warning('Loading failed (%s), retrying', str(e))
                time.sleep(1)

                
#        ''' JEFF wait till all awgs active '''
#        count = 1
#        while not l.is_awg_running() and count < 30:
#            print(count, 'tries to prime', l)
#            time.sleep(1)
#            count += 1
#            
#        ''' JEFF moved waveform load time from awgloader.py '''
#        dt = time.clock() - start
#        nloaded = len(l._loaded_wforms)
#        if nloaded > 0:
#            print 'Loaded %d waveforms in %.03f sec' % (nloaded, dt)
            
        if run:
            self.start_awgs()

    def stop_awgs(self):
        '''
        Stop AWGs
        '''
        logging.info('Stopping AWGs')
        l = self.get_awg_loader()
        for awg in l.get_awgs():
            awg.all_off()
            awg.stop()

    def start_awgs(self):
        l = self.get_awg_loader()
        print('measurement start_awgs', l)
        print('awgs:', l.get_awgs(), l.get_active_awgs())
        l.run()

    def stop_funcgen(self):
        if self._funcgen is None:
            return
        logging.info('Turning off function generator')
        if self.use_sync:
            self._funcgen.set_sync_on(False)
        else:
            self._funcgen.set_output_on(False)

    def start_funcgen(self):
        if self._funcgen is None:
            return
        logging.info('Turning on function generator')
        if self.use_sync:
            self._funcgen.set_sync_on(True)
        else:
            self._funcgen.set_output_on(True)

    def _capture_progress_cb(self, navg):
        if self.print_progress:
            print '%d averages done' % navg

    def update(self, avg_data):
        '''
        Override to update a plot
        '''
        pass

    def _data_changed_cb(self, key, _slice=None):
        if self.histogram:
            return
        avg_data = self.avg_data[:]
        try:
            self.update(avg_data)
        except Exception, e:
            print 'Error: %s' % (str(e),)

    def _ctrlc_cb(self, *args):
        self._interrupted = True

    def capture_ctrlc(self):
        self._interrupted = False
        self._old_signal = signal.signal(signal.SIGINT, self._ctrlc_cb)

    def release_ctrlc(self):
        signal.signal(signal.SIGINT, self._old_signal)

    def acquisition_loop(self, alz, fast=False):
        '''
        Acquisition loop, talk to alazar daemon.
        Also starts the measurement.
        '''

        # If we have a function generator, start AWGs before setting up alazar
        if self._funcgen and not fast:
            self.start_awgs()
            time.sleep(1)

        # Setup and arm alazar
        if self.histogram:
            alz.setup_hist(self.cyclelen * alz.get_naverages(), self.shot_data)
        else:
            alz.setup_experiment(self.cyclelen)

        alz.set_interrupt(False)
        # Estimate a capture timeout, mostly because the AWG is a bit slow...
        timeout = min(10000 + 4000 * self.cyclelen, 600000)
        alz.set_timeout(timeout)
        time.sleep(1)

        # Capture CTRL-C and connect callbacks
        self.capture_ctrlc()
        progress_hid = alz.connect('capture-progress', self._capture_progress_cb)
        dataupd_hid = self.data.connect('changed', self._data_changed_cb)

        # Start measurement, either by starting the AWG or the function generator
        if not fast:
            if self._funcgen:
                self.start_funcgen()
            else:
                self.start_awgs()

        try:
            if self.histogram:
                ret = alz.take_hist(async=True)
            else:
                ret = alz.take_experiment(avg_buf=self.avg_data, async=True, singleshotbin=self.singleshotbin,
                                          IQ_e=self.readout_info.IQe, e_radius=self.readout_info.IQe_radius)
            if self.print_progress:
                logging.info('Acquiring...')
            while not ret.is_valid() and not self._interrupted:
                objsh.helper.backend.main_loop(20)
                QtGui.QApplication.processEvents()
            if self._interrupted:
                alz.set_interrupt(True)
        except Exception, e:
            logging.info('CTRL-C Caught or error, stopping Alazar')
            alz.set_interrupt(True)
            logging.error(str(e))
        finally:
            alz.disconnect(progress_hid)
            self.data.disconnect(dataupd_hid)
            self.release_ctrlc()

        # Final processing of data
        self.post_process()
        
        return ret.get()

    def save_settings(self, fn=None):
        '''
        Save settings. If <fn> is not specified, generate a file associated
        with the measurement data (in sub directory settings).
        Also save settings to the file config.ins_store_fn.
        '''

        settings = mclient.instruments.get_all_parameters()
        if fn is None and self._timestamp_str != '':
            fn = os.path.join(config.datadir, 'settings/%s.set'%self._timestamp_str)
        fdir = os.path.split(fn)[0]
        if not os.path.isdir(fdir):
            os.makedirs(fdir)
        with open(fn, "w") as sfile:
            jsonext.dump(settings, sfile)

        mclient.save_instruments()

    def setup_measurement(self):
        '''
        - Stop AWGs / function generator
        - Generate sequence
        - Save settings
        - Arm alazar
        '''

        self.stop_funcgen()
        self.stop_awgs()
        alz = self.instruments['alazar']
        if alz is None:
            logging.error('Alazar instrument not found!')
            return

        # Generate and load sequence
        if self.do_generate:
            logging.info('Generating sequence...')
            seqs = self.generate()
            if self.plot_seqs:
                s = pulseseq.sequencer.Sequencer()
                s.plot_seqs(seqs)
            if self.print_seqs:
                s = pulseseq.sequencer.Sequencer()
                s.print_seqs(seqs)
            
            logging.info('Loading sequence...')
            self.load(seqs)
            if self.release_seqs:
                self.seqs = None
            
        #If not generating, we guess that all AWGs are used
        else:
            l = self.get_awg_loader()
            l.set_all_awgs_active()

        self.save_settings()
        
        alz.setup_clock()
        alz.setup_channels()
        alz.setup_trigger()
        alz.set_real_signals(self.real_signals)     # Doesn't do anything for histrograms

    def setup_measurement_data(self):
        '''
        Create datasets to store measured and post-processed data.
        '''
        alz = self.instruments['alazar']
        if self.histogram:
            self.shot_data = self.data.create_dataset('shots', shape=[self.cyclelen*alz.get_naverages()], dtype=np.complex)
            self.avg_data = None
            self.pp_data = None
        elif self.singleshotbin:
            self.shot_data = None
            self.avg_data = self.data.create_dataset('avg', [self.cyclelen,], dtype=np.float)
            self.pp_data = None
        else:
            self.shot_data = None
            # If saving complex data, save both raw signal and post-processed version
            if not self.real_signals:
                self.avg_data = self.data.create_dataset('avg', [self.cyclelen,], dtype=np.complex)
                self.pp_data = self.data.create_dataset('avg_pp', [self.cyclelen,], dtype=np.float)
            else:
                self.avg_data = self.data.create_dataset('avg', [self.cyclelen,], dtype=np.float)
                self.pp_data = None

    def measure(self):
        '''
        Perform a measurement.

        Requires existance of an instrument named 'alazar'.

        Sets up data sets, performs initialization and updates plots if the
        class has an 'update' function.
        '''

        self.setup_measurement()
        self.setup_measurement_data()

        alz = self.instruments['alazar']
        ret = self.acquisition_loop(alz) # calls update function
#        print('after aquisition loop')
        self.avg_data = ret

        if self.histogram:
            if self.cyclelen == 1:
                self.plot_histogram(self.shot_data[:])
        else:
            ret = self.analyze(self.get_ys(), fig=self.get_figure())

        if self.savefig:
            self.save_fig()

        txt = 'Done'
        if self.data:
            txt += '; in data group: %s' % self.data.get_fullname()
        logging.info(txt)

        if self._interrupted:
            raise Exception('Measurement interrupted')

        # Remove pulse data to keep memory usage reasonable
        pulseseq.sequencer.Pulse.clear_pulse_data()
 
        return ret

    def acquisition_loop_keysight(self, dig, fast=False):
        '''
        JEFF: all methods with _keysight used with keysight digitizer instead of alazar
        Acquisition loop, talk to keysight dig.
        Also starts the measurement.
        
        TODO: implement the interupt like alazar has
        '''

        # Setup and arm alazar
        dig.setup_experiment(self.cyclelen)
        dig.arm()

        # Start measurement, either by starting the AWG or the function generator
        self.start_awgs()
        ret = dig.take_experiment()

        # Final processing of data
        self.post_process()
        
        return ret


    def setup_measurement_keysight(self):
        '''
        - Stop AWGs / function generator
        - Generate sequence
        - Save settings
        - Arm digitizer
        '''

        self.stop_funcgen()
        self.stop_awgs()
        dig = self.instruments['dig']
        if dig is None:
            logging.error('Digitizer not found!')
            return

        # Generate and load sequence
        if self.do_generate:
            logging.info('Generating sequence...')
            seqs = self.generate()
            if self.plot_seqs:
                s = pulseseq.sequencer.Sequencer()
                s.plot_seqs(seqs)
            if self.print_seqs:
                s = pulseseq.sequencer.Sequencer()
                s.print_seqs(seqs)
            
            logging.info('Loading sequence...')
            self.load(seqs)
            if self.release_seqs:
                self.seqs = None
            
        #If not generating, we guess that all AWGs are used
        else:
            l = self.get_awg_loader()
            l.set_all_awgs_active()

        self.save_settings()
        
#        alz.setup_clock()
#        alz.setup_channels()
#        alz.setup_trigger()
#        alz.set_real_signals(self.real_signals)    

    def setup_measurement_data_keysight(self):
        '''
        Create datasets to store measured and post-processed data.
        '''
        dig = self.instruments['dig']
        if self.histogram:
            self.shot_data = self.data.create_dataset('shots', shape=[self.cyclelen*dig.do_get_naverages()], dtype=np.complex)
            self.avg_data = None
            self.pp_data = None
        elif self.singleshotbin:
            self.shot_data = None
            self.avg_data = self.data.create_dataset('avg', [self.cyclelen,], dtype=np.float)
            self.pp_data = None
        else:
            self.shot_data = None
            # If saving complex data, save both raw signal and post-processed version
            if not self.real_signals:
                self.avg_data = self.data.create_dataset('avg', [self.cyclelen,], dtype=np.complex)
                self.pp_data = self.data.create_dataset('avg_pp', [self.cyclelen,], dtype=np.float)
            else:
                self.avg_data = self.data.create_dataset('avg', [self.cyclelen,], dtype=np.float)
                self.pp_data = None

    def measure_keysight(self):
        '''
        Perform a measurement.

        Sets up data sets, performs initialization and updates plots if the
        class has an 'update' function.
        '''

        self.setup_measurement_keysight()
        self.setup_measurement_data_keysight()

        dig = self.instruments['dig']
        ret = self.acquisition_loop_keysight(dig) # calls update function
#        print('after aquisition loop')
        self.avg_data = ret

        if self.histogram:
            if self.cyclelen == 1:
                self.plot_histogram(self.shot_data[:])
        else:
            ret = self.analyze(self.get_ys(), fig=self.get_figure())

        if self.savefig:
            self.save_fig()

        txt = 'Done'
        if self.data:
            txt += '; in data group: %s' % self.data.get_fullname()
        logging.info(txt)

        if self._interrupted:
            raise Exception('Measurement interrupted')

        # Remove pulse data to keep memory usage reasonable
        pulseseq.sequencer.Pulse.clear_pulse_data()
 
        return ret

    def play_sequence(self, load=True):
        '''
        Generate and play the sequence for this measurement without setting
        up data acquistion.
        '''
        if load:
            self.load(self.generate())
        else:
            l = self.get_awg_loader()
            l.stop()

        self.start_awgs()
        self.start_funcgen()

    def create_figure(self):
        '''
        Create a figure associated with this measurement.
        If residuals is True it will have 2 axes objects, the first one
        for data, the second for fit residuals.
        If vert is True these are organized vertically and the residuals
        axes is smaller than the data axes.
        If vert is False they are of equal size and next to each other,
        useful for 2D measurements.
        '''
        self.fig = plt.figure()
        title = self.title
        if self.data:
            title += ' data in %s' % self.data.get_fullname()
        self.fig.suptitle(title)
        if not self.residuals:
            self.fig.add_subplot(111)
            return self.fig

        if self.res_vert:
            gs = gridspec.GridSpec(2, 1, height_ratios=[3,1])
        else:
            gs = gridspec.GridSpec(1, 2, width_ratios=[1,1])
        self.fig.add_subplot(gs[0])
        self.fig.add_subplot(gs[1])
        return self.fig

    def get_figure(self):
        if self.fig:
            print "There already exists the figure"
            return self.fig
        else:
            print "Here we create a figure"
        return self.create_figure()

    def complex_to_real(self, ys):
        '''
        Convert complex IQ values to real values.
        If IQg/e are specified project on the line through those two points
        Otherwise fit a line through data in IQ space and project on that line.
        '''

        if not is_complex(ys):
            return ys

        IQg = self.readout_info.IQg
        IQe = self.readout_info.IQe
        if IQg is None or IQe is None or IQg == 0 or IQe == 0:
            p = np.polyfit(np.real(ys), np.imag(ys), 1)
            vproj = 1 + 1j*p[0]
#            return np.real(ys * np.exp(-1j * np.angle(np.average(ys))))
        else:
            vproj = IQe - IQg

        vproj /= np.abs(vproj)
        ys = ys - IQg
        return (np.real(ys)**2+np.imag(ys)**2)**0.5
#        return np.real(ys) * vproj.real  + np.imag(ys) * vproj.imag

    def get_ys(self, data=None):
        '''
        Return measured data.
        Can be overloaded for example if a background measurement is included
        in the sequence.
        '''
        if data is None:
            ys = self.avg_data[:]
        else:
            ys = data
        ''' CHEN/DARIO/JEFF fix for old error shifting first point to last point '''
#        ys=np.concatenate((ys[1:], ys[:1]))
        return self.complex_to_real(ys)

    def post_process(self):
        '''
        Post-process acquired data, i.e. convert complex IQ values to real
        numbers.
        '''
        if not self.keep_data:
            self.drop_data()

        if self.pp_data is None:
            return
        self.pp_data[:] = self.complex_to_real(self.avg_data[:])

    def get_ys_fig(self, data=None, fig=None):
        '''
        Return a plottable Y data array and a figure object to plot in.
        '''
        if fig is None:
            fig = self.get_figure()
        return self.get_ys(), fig

    def analyze(self, data=None, fig=None):
        '''
        Should be implemented in derived class.
        Best is to use a function that is defined outside of your measurement
        class so that you can reload a module and use the updated analysis
        function from an old measurement instance.
        '''
        if not self.analysis_func:
            raise Exception('Either overload analyze() or specify an analysis_func')
        ret = self.analysis_func(self, data, fig)
        if self.saveas:
            self.fig.canvas.draw()
            self.fig.savefig(self.saveas)
        return ret

    def plot_dataset(self, xs, ys, *args, **kwargs):
        kwargs['ls'] = 'None'
        kwargs['marker'] = 's'
        kwargs['ms'] = 3
        ret = self.fig.axes[0].plot(xs, ys, *args, **kwargs)
        self._datacol = ret[0].get_c()

    def plot_fit(self, xs, ys, *args, **kwargs):
        kwargs['ls'] = '-'
        kwargs['dashes'] = (2,2)
        kwargs['ms'] = 3
        kwargs['color'] = self._datacol
        self.fig.axes[0].plot(xs, ys, *args, **kwargs)

    def save_fig(self, fn=None):
        '''
        Save the figure belonging to this measurement.
        '''
        if fn is None:
            fn = os.path.join(config.datadir, 'images/%s_%s.%s'%(self._timestamp_str, self.name, self.imagetype))
        fdir = os.path.split(fn)[0]
        if not os.path.isdir(fdir):
            os.makedirs(fdir)
        kwargs = dict()
        if self.imagetype == 'png':
            kwargs['dpi'] = 200
        if self.fig:
            self.fig.savefig(fn, **kwargs)

    def plot_histogram(self, data):
        fig = self.get_figure()
        avg = np.average(data)
        print 'avgerage I,Q is:', avg, '\n'
        if 0:
            fig.axes[0].scatter(np.real(data), np.imag(data), label='avg=%s'%(avg,))
        else:
            fig.axes[0].hexbin(np.real(data), np.imag(data), label='avg=%s'%(avg,), cmap=mpl.cm.hot)
        if self.residuals:
            n, bins, patches = fig.axes[1].hist(self.complex_to_real(data), bins=64)
            ax2 = fig.axes[1].twinx()
            ax2.set_zorder(fig.axes[1].zorder+1)
            ax2.patch.set_visible(False)
            ax2.plot((bins[:-1]+bins[1:])/2, np.cumsum(n), 'k')
            ax2.plot((bins[:-1]+bins[1:])/2, np.sum(n) - np.cumsum(n), 'r')

    #########################################################
    # Sequencer helper functions
    #########################################################

    def get_readout_pulse(self, pulse_len=None):
        if pulse_len is None:
            pulse_len = self.readout_info.pulse_len

        return sequencer.Combined([
            pulselib.Constant(pulse_len, 1, chan=self.readout_info.readout_chan),
            pulselib.Constant(pulse_len, 1, chan=self.readout_info.acq_chan),
        ])

class Measurement1D(Measurement):
    '''
    Base class for 1D measurements such as T1 or T2.
    '''

    def __init__(self, cyclelen, **kwargs):
        super(Measurement1D, self).__init__(cyclelen, **kwargs)

    def update(self, avg_data):
        ys = self.get_ys(avg_data)
        fig = self.get_figure()
        fig.axes[0].clear()
        if hasattr(self, 'xs'):
            fig.axes[0].plot(self.xs, ys)
        else:
            fig.axes[0].plot(ys)
        fig.canvas.draw()

    def analyze_parabola(self, data=None, fig=None, xlabel='', ylabel=''):
        '''
        Standard analysis function to fit a parabola and return the extremum.
        '''

        ys, fig = self.get_ys_fig(data, fig)
        xs = self.xs

        p = np.polyfit(xs, ys, 2)
        self.fit_params = p
        minmax = 'max' if (p[0] < 0) else 'min'
        minmaxpos = -p[1]/2/p[0]
        txt = 'Fit, %s at %.06f' % (minmax, minmaxpos,)
        fig.axes[0].plot(xs, ys, 'ks', ms=3)
        fig.axes[0].plot(xs, xs**2*p[0]+xs*p[1]+p[2], label=txt)
        fig.axes[0].set_ylabel(ylabel)
        fig.axes[0].set_xlabel(xlabel)
        fig.axes[0].legend(loc=0)
        plt.legend()

        fig.axes[1].plot(xs, ys - (xs**2*p[0] + xs*p[1] + p[2]), 'k', marker='s')
        fig.canvas.draw()

        return minmaxpos

class Measurement2D(Measurement):
    '''
    Base class for 2D measurements such as Q- or Wigner functions.
    '''

    def __init__(self, cyclelen, style=STYLE_IMAGE, **kwargs):
        self.style = style
        super(Measurement2D, self).__init__(cyclelen, **kwargs)

    def get_plotxsys(self):
        if self.style == STYLE_IMAGE:
            dx = (self.xs[1] - self.xs[0]) / 2.
            xs = np.linspace(np.min(self.xs)-dx, np.max(self.xs)+dx, len(self.xs)+1)
            dy = (self.ys[1] - self.ys[0]) / 2.
            ys = np.linspace(np.min(self.ys)-dy, np.max(self.ys)+dy, len(self.ys)+1)
            return xs, ys
        else:
            return self.xs, self.ys

    def update(self, avg_data):
        zs = self.get_ys(avg_data)
        fig = self.get_figure()
        fig.axes[0].clear()
        if hasattr(self, 'xs') and hasattr(self, 'ys'):
            zs = zs.reshape((len(self.xs), len(self.ys)))
            xs, ys = self.get_plotxsys()
            if self.style == STYLE_IMAGE:
                fig.axes[0].pcolormesh(xs, ys, zs)
                fig.axes[0].set_xlim(xs.min(), xs.max())
                fig.axes[0].set_ylim(ys.min(), ys.max())
                fig.canvas.draw()
            else:
                for i_y, y in enumerate(ys):
                    fig.axes[0].plot(xs, zs[:,i_y], label='%.03f'%y)
                fig.axes[0].legend(loc=0)
        else:
            logging.warning('Unable to plot 2D array without xs and ys')
