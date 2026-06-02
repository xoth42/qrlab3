import mclient
import config
import time
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib import gridspec
import logging
import signal
import objectsharer as objsh
from lib import jsonext
import os
import awgloader

from PyQt5 import QtWidgets
from pulseseq import sequencer
from pulseseq import pulselib

logging.getLogger().setLevel(logging.INFO)

STYLE_IMAGE = "IMAGE"
STYLE_LINES = "LINES"
MAX_ACQUISITION_POLLS = 1_000_000_000


def is_complex(ar):
    return ar.dtype in (complex, np.complex64, np.complex128)


def _ensure_list(value):
    """Normalize a value into a list without copying lists unnecessarily."""
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    return [value]


class Measurement(object):
    """
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
    """

    def __init__(
        self,
        cyclelen,
        readout="readout",
        keep_shots=False,
        name=None,
        histogram=False,
        singleshotbin=False,
        generate=True,
        fig=None,
        title="",
        residuals=True,
        res_vert=True,
        release_seqs=True,
        plot_seqs=False,
        print_seqs=False,
        keep_data=True,
        infos=None,
        extra_info=None,
        comment="",
        use_sync=True,
        real_signals=False,
        analysis_func=None,
        savefig=True,
        imagetype="png",
        print_progress=True,
        proj_func="amplitude",
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
        self.proj_func = proj_func
        self.readout = readout

        # `infos` is used as a sequence of pulse metadata objects. Normalize
        # scalars and tuples into a plain list so the rest of the code can
        # iterate without special cases.
        self.infos = _ensure_list(infos)
        if extra_info is not None:
            self.infos.extend(_ensure_list(extra_info))

        self.analysis_func = analysis_func

        self.setup_data(name)

        self.instruments = mclient.instruments
        self.readout_info = mclient.get_readout_info(readout)
        self.readout_driver = mclient.instruments.get(readout)

        self._funcgen = mclient.instruments.get("funcgen")
        self.use_sync = use_sync

        # Cache which digitizer backend is available so later branches can stay
        # short and readable.
        alz = mclient.instruments.get("alazar")
        if alz is not None:
            self.dig_type = "alz"
        else:
            self.dig_type = "key"
        self._dig = mclient.instruments.get("dig")  # Fallback trigger source.

    def setup_data(self, name):
        if self.keep_data:
            self.datafile = mclient.datafile
        else:
            self.datafile = mclient.get_temp_file()

        ts = time.localtime()
        tstr = time.strftime("%Y%m%d/%H%M%S", ts)
        self._timestamp_str = tstr
        self._groupname = f"{tstr}_{name}"
        self.data = self.datafile.create_group(self._groupname)
        self.data.set_attrs(title=self.title, comment=self.comment)

    def _create_awg_loader(self, fileload=False, dot_awg_path=None):
        """Create and cache the AWG loader with the standard 4-AWG mapping."""
        if self._awgloader:
            return self._awgloader

        loader = awgloader.AWGLoader(
            bulkload=config.awg_bulkload,
            fileload=fileload,
            dot_awg_path=dot_awg_path,
        )

        # Each physical AWG contributes four logical channels in sequence.
        base_channel = 1
        for awg_index in range(1, 5):
            awg = self.instruments[f"AWG{int(awg_index)}"]
            if awg:
                chanmap = {
                    1: base_channel,
                    2: base_channel + 1,
                    3: base_channel + 2,
                    4: base_channel + 3,
                }
                logging.info(f"Adding AWG{int(awg_index)}, channel map: {chanmap}", )
                loader.add_awg(awg, chanmap)
                base_channel += 4

        self._awgloader = loader
        return loader

    def drop_data(self):
        """
        Remove data from hdf5 file but keep arrays in memory.
        Remove temporary file.
        """
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
            if self.ste_data:
                stedata = np.array(self.ste_data[:])
            else:
                stedata = None

            logging.info(f"Dropping data group {self._groupname}")
            del self.datafile[self._groupname]
            mclient.remove_temp_file()
            self.data = None

            self.avg_data = avgdata
            self.pp_data = ppdata
            self.shot_data = shotdata
            self.ste_data = stedata

        except Exception as e:
            logging.warning(f"Unable to remove data: {str(e)}")

    def set_parameters(self, **kwargs):
        self.data.set_attrs(kwargs)

    def get_sequencer(self, seqs=None):
        s = sequencer.Sequencer(seqs)

        for i in self.infos:
            if hasattr(i, "ssb_list"):
                for ssb in i.ssb_list:
                    s.add_ssb(ssb)
            else:
                if i.ssb:
                    s.add_ssb(i.ssb)
            if i.marker and i.marker["channel"] != "":
                s.add_marker(
                    i.marker["channel"],
                    i.channels[0],
                    ofs=i.marker["ofs"],
                    bufwidth=i.marker["bufwidth"],
                )
                s.add_marker(
                    i.marker["channel"],
                    i.channels[1],
                    ofs=i.marker["ofs"],
                    bufwidth=i.marker["bufwidth"],
                )

        if hasattr(config, "required_markers"):
            for marker_dict in config.required_markers:
                s.add_marker(
                    marker_dict["out_chan"],
                    marker_dict["in_chan"],
                    ofs=marker_dict["ofs"],
                    bufwidth=marker_dict["bufwidth"],
                )

        for ch in config.required_channels:
            s.add_required_channel(ch)

        # Add master/slave settings to sequencer
        if hasattr(config, "slave_triggers"):
            slave_chan = int(config.slave_triggers[0][0].split("m")[0])
            master_awg = ((slave_chan - 1) / 4) + 1
            logging.info(f"AWG {int(master_awg)} seems to be the master")
            for i in range(4):
                ch = 4 * (master_awg - 1) + i + 1
                s.add_master_channel(ch)
                s.add_master_channel(f"{int(ch)}m1")
                s.add_master_channel(f"{int(ch)}m2")

            for chan, delay in config.slave_triggers:
                s.add_slave_trigger(chan, delay)

        # Add channel delays settings to sequencer
        if hasattr(config, "channel_delays"):
            for ch, delay in config.channel_delays:
                s.add_channel_delay(ch, delay)

        if hasattr(config, "flatten_waveforms"):
            s.set_flatten(config.flatten_waveforms)

        if hasattr(config, "channel_convolutions"):
            s.set_flatten(True)
            for ch, path in config.channel_convolutions:
                kernel = np.loadtxt(path)
                s.add_convolution(ch, kernel)
                logging.info(f"adding convolution channel: {int(ch)}")

        return s

    def generate(self):
        """
        This function should generate the pulse sequence and return it.
        """
        return None

    def get_awg_loader_old(self):
        """
        Detect all AWGs and map channels:
        AWG1 gets channel 1-4, AWG2 5-8, etc.
        """
        return self._create_awg_loader()

    def get_awg_loader(self):
        """
        Detect all AWGs and map channels:
        AWG1 gets channel 1-4, AWG2 5-8, etc.
        """
        fileload = getattr(config, "awg_fileload", False)
        dot_awg_path = getattr(config, "dot_awg_path", None)
        return self._create_awg_loader(fileload=fileload, dot_awg_path=dot_awg_path)

    def load(self, seqs, run=False, ntries=1):
        """
        Load sequences <seqs> to awgs.
        awgs are located from the instruments list and should be named
        AWG1, AWG2, ... (up to 4 currently).
        """
        loader = self.get_awg_loader()
        for _ in range(ntries):
            try:
                loader.load(seqs)
                break
            except Exception as exc:
                logging.warning(f"Loading failed ({exc}), retrying", )
                time.sleep(1)
        if run:
            self.start_awgs()

    def stop_awgs(self):
        """
        Stop AWGs
        """
        logging.info("Stopping AWGs")
        loader = self.get_awg_loader()
        for awg in loader.get_awgs():
            awg.all_off()
            awg.stop()

    def start_awgs(self):
        loader = self.get_awg_loader()
        logging.info(
            f"Starting AWGs: {loader.get_awgs()} (active: {loader.get_active_awgs()})",
            )
        loader.run()

    def stop_funcgen(self):
        if self._funcgen is None:
            return
        logging.info("Turning off function generator")
        if self.use_sync:
            self._funcgen.set_sync_on(False)
        else:
            self._funcgen.set_output_on(False)

    def start_funcgen(self):
        if self._funcgen is None:
            return
        logging.info("Turning on function generator")
        if self.use_sync:
            self._funcgen.set_sync_on(True)
        else:
            self._funcgen.set_output_on(True)

    def _capture_progress_cb(self, navg):
        if self.print_progress:
            logging.info(f"{int(navg)} averages done", )

    def update(self, avg_data):
        """
        Override to update a plot
        """
        pass

    def _data_changed_cb(self, key, _slice=None):
        if self.histogram:
            return
        avg_data = self.avg_data[:]
        try:
            self.update(avg_data)
        except Exception as exc:
            logging.exception(f"Plot update failed: {exc}", )

    def _ctrlc_cb(self, *args):
        self._interrupted = True

    def capture_ctrlc(self):
        self._interrupted = False
        self._old_signal = signal.signal(signal.SIGINT, self._ctrlc_cb)

    def release_ctrlc(self):
        signal.signal(signal.SIGINT, self._old_signal)

    def acquisition_loop(self, alz, fast=False):
        """
        Acquisition loop, talk to alazar daemon.
        Also starts the measurement.
        """
        # The function-generator path starts AWGs first because the generator
        # often provides the final timing edge that arms the digitizer.
        if self._funcgen and not fast:
            logging.debug(
                "Function generator present, starting AWGs before Alazar setup"
            )
            self.start_awgs()
            time.sleep(1)

        # Configure the digitizer for histogram or averaged acquisition.
        if self.histogram:
            alz.setup_hist(self.cyclelen * alz.get_naverages(), self.shot_data)
        else:
            alz.setup_experiment(self.cyclelen)

        alz.set_interrupt(False)
        # Estimate a generous timeout so slow AWG transfers do not abort early.
        timeout = min(10000 + 4000 * self.cyclelen, 600000)
        alz.set_timeout(timeout)
        time.sleep(1)

        # Hook progress and data updates before the run starts.
        self.capture_ctrlc()
        progress_hid = alz.connect("capture-progress", self._capture_progress_cb)
        dataupd_hid = self.data.connect("changed", self._data_changed_cb)

        # Start whichever hardware source is responsible for beginning the run.
        if not fast:
            if self._funcgen:
                self.start_funcgen()
            elif self._dig:
                dig = self.instruments["dig"]
                dig.stop_hvi()
                self.start_awgs()
                dig.start_hvi()
            else:
                self.start_awgs()

        try:
            take_ref = self.readout != "readout_IQ"
            if self.histogram:
                # Histogram acquisition currently always keeps the reference
                # decision simple because the backend API is limited here.
                ret = alz.take_hist(async_=True, take_ref=take_ref)
            else:
                ret = alz.take_experiment(
                    avg_buf=self.avg_data,
                    async_=True,
                    singleshotbin=self.singleshotbin,
                    cov_buf=self.cov_data,
                    shot_buf=self.shot_data,
                    IQ_e=self.readout_info.IQe,
                    e_radius=self.readout_info.IQe_radius,
                    proj_func=self.proj_func,
                    take_ref=take_ref,
                )

            if self.print_progress:
                logging.info("Acquiring...")
            for _ in range(MAX_ACQUISITION_POLLS):
                if ret.is_valid() or self._interrupted:
                    break
                objsh.helper.backend.main_loop(20, origin=0)
                QtWidgets.QApplication.processEvents()
            else:
                raise TimeoutError(f"Acquisition timed out after {MAX_ACQUISITION_POLLS} loop steps")
            if self._interrupted:
                alz.set_interrupt(True)
        except Exception as exc:
            logging.info("CTRL-C Caught or error, stopping Alazar")
            alz.set_interrupt(True)
            logging.exception(f"Acquisition failed: {exc}", )
        finally:
            alz.disconnect(progress_hid)
            self.data.disconnect(dataupd_hid)
            self.release_ctrlc()
        # Final processing of data
        self.post_process()

        return ret.get()

    def save_settings(self, fn=None):
        """
        Save settings. If <fn> is not specified, generate a file associated
        with the measurement data (in sub directory settings).
        Also save settings to the file config.ins_store_fn.
        """

        settings = mclient.instruments.get_all_parameters()
        if fn is None and self._timestamp_str != "":
            fn = os.path.join(config.datadir, f"settings/{self._timestamp_str}.set")
        fdir = os.path.split(fn)[0]
        if not os.path.isdir(fdir):
            os.makedirs(fdir)
        with open(fn, "w") as sfile:
            jsonext.dump(settings, sfile)

        mclient.save_instruments()

    def setup_measurement(self):
        """
        - Stop AWGs / function generator
        - Generate sequence
        - Save settings
        - Arm alazar
        """

        self.stop_funcgen()
        self.stop_awgs()
        alz = self.instruments["alazar"]
        if alz is None:
            logging.error("Alazar instrument not found!")
            return

        # Generate and load sequence
        if self.do_generate:
            logging.info("Generating sequence...")
            seqs = self.generate()
            if self.plot_seqs:
                s = sequencer.Sequencer()
                s.plot_seqs(seqs)
            if self.print_seqs:
                s = sequencer.Sequencer()
                s.print_seqs(seqs)

            logging.info("Loading sequence...")
            self.load(seqs)
            if self.release_seqs:
                self.seqs = None

        # If not generating, we guess that all AWGs are used
        else:
            loader = self.get_awg_loader()
            loader.set_all_awgs_active()

        self.save_settings()
        alz.setup_channels()
        alz.setup_trigger()
        alz.set_real_signals(self.real_signals)

    def setup_measurement_data(self):
        """
        Create datasets to store measured and post-processed data.
        """
        alz = self.instruments["alazar"]
        if self.histogram:
            self.shot_data = self.data.create_dataset(
                "shots",
                shape=[self.cyclelen * alz.get_naverages()],
                dtype=np.complex128,
            )
            self.avg_data = None
            self.pp_data = None
            self.std_i_data = None
            self.std_q_data = None
        elif self.singleshotbin:
            self.shot_data = None
            self.avg_data = self.data.create_dataset(
                "avg",
                [
                    self.cyclelen,
                ],
                dtype=np.float64,
            )
            self.pp_data = None
            self.ste_data = None
            # Keep the raw single-shot bin data alongside the averaged result.
        elif self.keep_shots:
            self.shot_data = self.data.create_dataset(
                "shots",
                shape=[self.cyclelen * alz.get_naverages()],
                dtype=np.complex128,
            )
            if not self.real_signals:
                self.avg_data = self.data.create_dataset(
                    "avg",
                    [
                        self.cyclelen,
                    ],
                    dtype=np.complex128,
                )
                self.pp_data = self.data.create_dataset(
                    "avg_pp",
                    [
                        self.cyclelen,
                    ],
                    dtype=np.float64,
                )
            else:
                self.avg_data = self.data.create_dataset(
                    "avg",
                    [
                        self.cyclelen,
                    ],
                    dtype=np.float64,
                )
                self.pp_data = None
        else:
            self.shot_data = None
            # If saving complex data, save both raw signal and post-processed version
            if not self.real_signals:
                self.avg_data = self.data.create_dataset(
                    "avg",
                    [
                        self.cyclelen,
                    ],
                    dtype=np.complex128,
                )
                self.pp_data = self.data.create_dataset(
                    "avg_pp",
                    [
                        self.cyclelen,
                    ],
                    dtype=np.float64,
                )
            else:
                self.avg_data = self.data.create_dataset(
                    "avg",
                    [
                        self.cyclelen,
                    ],
                    dtype=np.float64,
                )
                self.pp_data = None
            self.cov_data = self.data.create_dataset(
                "cov", [self.cyclelen, 3], dtype=np.float64
            )

    def measure(self):
        """
        Perform a measurement.

        Requires existance of an instrument named 'alazar'.

        Sets up data sets, performs initialization and updates plots if the
        class has an 'update' function.
        """
        if self.dig_type == "key":
            return self.measure_keysight()

        self.setup_measurement()
        self.setup_measurement_data()

        alz = self.instruments["alazar"]
        if self.histogram:
            #            if self.cyclelen == 1:
            ret = self.acquisition_loop(alz)
            self.plot_histogram(self.shot_data[:])

        else:
            avgs, cov = self.acquisition_loop(alz)  # calls update function
            self.avg_data = avgs
            self.cov_data = cov
            ret = self.analyze(self.get_ys(), fig=self.get_figure())

        if self.savefig:
            self.save_fig()

        txt = "Done"
        if self.data:
            txt += f"; in data group: {self.data.get_fullname()}"
        logging.info(txt)

        if self._interrupted:
            raise Exception("Measurement interrupted")

        # Remove pulse data to keep memory usage reasonable
        sequencer.Pulse.clear_pulse_data()

        return ret

    def acquisition_loop_keysight(self, dig, fast=False):
        """
        JEFF: all methods with _keysight used with keysight digitizer instead of alazar
        Acquisition loop, talk to keysight dig.
        Also starts the measurement.

        TODO: implement the interrupt like alazar has
        """

        self.capture_ctrlc()
        progress_hid = dig.connect("capture-progress", self._capture_progress_cb)
        dataupd_hid = self.data.connect("changed", self._data_changed_cb)

        logging.info(f"Cycle length is {self.cyclelen}", )

        dig.stop_hvi()
        if self.histogram:
            dig.setup_hist(self.cyclelen * dig.get_naverages(), hist_buf=self.shot_data)
        else:
            dig.setup_experiment(self.cyclelen, ntransfers=None)

        dig.arm()

        dig.set_interrupt(False)

        # Start measurement, either by starting the AWG or the function generator
        self.start_awgs()
        dig.start_hvi()

        #        ret = dig.take_experiment(avg_buf=self.avg_data, ste_buf=self.ste_data,
        #                                  async_=True, IQ_e=self.readout_info.IQe,
        #                                  e_radius=self.readout_info.IQe_radius)

        take_ref = self.readout != "readout_IQ"
        if self.histogram:
            ret = dig.take_hist(async_=True, take_ref=take_ref)
        else:
            ret = dig.take_experiment(
                avg_buf=self.avg_data,
                cov_buf=self.cov_data,
                async_=True,
                IQ_e=self.readout_info.IQe,
                e_radius=self.readout_info.IQe_radius,
                take_ref=take_ref,
            )  # , proj_func=self.proj_func)

        try:
            for _ in range(MAX_ACQUISITION_POLLS):
                if ret.is_valid() or self._interrupted:
                    break
                objsh.helper.backend.main_loop(20)
                QtWidgets.QApplication.processEvents()
            else:
                raise TimeoutError(f"Acquisition timed out after {MAX_ACQUISITION_POLLS} loop steps")
            if self._interrupted:
                dig.set_interrupt(True)
        except Exception as exc:
            logging.info("CTRL-C Caught or error, stopping Alazar")
            dig.set_interrupt(True)
            logging.exception(f"Acquisition failed: {exc}", )
        finally:
            dig.disconnect(progress_hid)
            self.data.disconnect(dataupd_hid)
            self.release_ctrlc()

        # Final processing of data
        self.post_process()

        dig.release_buf()

        return ret.get()

    def setup_measurement_keysight(self):
        """
        - Stop AWGs / function generator
        - Generate sequence
        - Save settings
        - Arm digitizer
        """

        self.stop_funcgen()
        self.stop_awgs()
        dig = self.instruments["dig"]
        if dig is None:
            logging.error("Digitizer not found!")
            return

        # Generate and load sequence
        if self.do_generate:
            logging.info("Generating sequence...")
            seqs = self.generate()
            if self.plot_seqs:
                s = sequencer.Sequencer()
                s.plot_seqs(seqs)
            if self.print_seqs:
                s = sequencer.Sequencer()
                s.print_seqs(seqs)

            logging.info("Loading sequence...")
            self.load(seqs)
            if self.release_seqs:
                self.seqs = None

        # If not generating, we guess that all AWGs are used
        else:
            loader = self.get_awg_loader()
            loader.set_all_awgs_active()

        self.save_settings()

    def setup_measurement_data_keysight(self):
        """
        Create datasets to store measured and post-processed data.
        """
        dig = self.instruments["dig"]
        if self.histogram:
            self.shot_data = self.data.create_dataset(
                "shots",
                shape=[self.cyclelen * dig.do_get_naverages()],
                dtype=np.complex128,
            )
            self.avg_data = None
            self.pp_data = None
            self.std_i_data = None
            self.std_q_data = None
        elif self.singleshotbin:
            self.shot_data = None
            self.avg_data = self.data.create_dataset(
                "avg",
                [
                    self.cyclelen,
                ],
                dtype=np.float64,
            )
            self.pp_data = None
            self.ste_data = None
        else:
            self.shot_data = None
            # If saving complex data, save both raw signal and post-processed version
            if not self.real_signals:
                self.avg_data = self.data.create_dataset(
                    "avg",
                    [
                        self.cyclelen,
                    ],
                    dtype=np.complex128,
                )
                self.pp_data = self.data.create_dataset(
                    "avg_pp",
                    [
                        self.cyclelen,
                    ],
                    dtype=np.float64,
                )
            else:
                self.avg_data = self.data.create_dataset(
                    "avg",
                    [
                        self.cyclelen,
                    ],
                    dtype=np.float64,
                )
                self.pp_data = None
            self.cov_data = self.data.create_dataset(
                "cov", [self.cyclelen, 3], dtype=np.float64
            )

    def measure_keysight(self):
        """
        Perform a measurement.

        Sets up data sets, performs initialization and updates plots if the
        class has an 'update' function.
        """

        self.setup_measurement_keysight()
        self.setup_measurement_data_keysight()

        dig = self._dig

        if self.histogram:
            ret = self.acquisition_loop_keysight(dig)
            if self.cyclelen == 1:
                self.plot_histogram(ret)
        else:
            avgs, cov = self.acquisition_loop_keysight(dig)  # calls update function
            self.avg_data = avgs
            self.cov_data = cov
            ret = self.analyze(self.get_ys(), fig=self.get_figure())

        if self.savefig:
            self.save_fig()

        txt = "Done"
        if self.data:
            txt += f"; in data group: {self.data.get_fullname()}"
        logging.info(txt)

        if self._interrupted:
            raise Exception("Measurement interrupted")

        # Remove pulse data to keep memory usage reasonable
        sequencer.Pulse.clear_pulse_data()

        return ret

    def play_sequence(self, load=True):
        """
        Generate and play the sequence for this measurement without setting
        up data acquistion.
        """
        if load:
            self.load(self.generate())
        else:
            loader = self.get_awg_loader()
            loader.stop()

        self.start_awgs()
        self.start_funcgen()

    def create_figure(self):
        """
        Create a figure associated with this measurement.
        If residuals is True it will have 2 axes objects, the first one
        for data, the second for fit residuals.
        If vert is True these are organized vertically and the residuals
        axes is smaller than the data axes.
        If vert is False they are of equal size and next to each other,
        useful for 2D measurements.
        """
        self.fig = plt.figure()
        title = self.title
        if self.data:
            title += f" data in {self.data.get_fullname()}"
        self.fig.suptitle(title)
        if not self.residuals:
            self.fig.add_subplot(111)
            return self.fig

        if self.res_vert:
            gs = gridspec.GridSpec(2, 1, height_ratios=[3, 1])
        else:
            gs = gridspec.GridSpec(1, 2, width_ratios=[1, 1])
        self.fig.add_subplot(gs[0])
        self.fig.add_subplot(gs[1])
        return self.fig

    def get_figure(self):
        if self.fig:
            return self.fig
        logging.info(f"Creating a new figure for {self.name}", )
        return self.create_figure()

    def complex_to_real(self, ys):
        """
        Convert complex IQ values to real values.
        If IQg/e are specified project on the line through those two points
        Otherwise fit a line through data in IQ space and project on that line.
        """

        if not is_complex(ys):
            return ys

        IQg = self.readout_info.IQg
        IQe = self.readout_info.IQe
        if IQg is None or IQe is None or IQg == 0 or IQe == 0:
            p = np.polyfit(np.real(ys), np.imag(ys), 1)
            vproj = 1 + 1j * p[0]
        #            return np.real(ys * np.exp(-1j * np.angle(np.average(ys))))
        else:
            vproj = IQe - IQg

        vproj /= np.abs(vproj)

        if self.proj_func == "phase":
            return np.angle(ys, deg=True)
        elif self.proj_func == "projection":
            ys = ys - IQg
            return np.real(ys) * vproj.real + np.imag(ys) * vproj.imag
        else:
            return np.hypot(np.real(ys), np.imag(ys))

    def get_ys(self, data=None):
        """
        Return measured data.
        Can be overloaded for example if a background measurement is included
        in the sequence.
        """
        if data is None:
            ys = self.avg_data[:]
        else:
            ys = data
        return self.complex_to_real(ys)

    def get_errorbars(self, data=None):
        """
        Return measured standard errors
        """
        if data is None:
            naverages = self.get_naverages()
            values = self.avg_data[:]

            # calculate amp based on projection type
            if self.proj_func == "amplitude":
                theta = -np.angle(values)
            elif self.proj_func == "phase":
                theta = -np.angle(values) + np.pi / 2
            elif self.proj_func == "projection":
                IQg = self.readout_info.IQg
                IQe = self.readout_info.IQe
                vproj = IQe - IQg
                theta = -np.angle(vproj) * np.ones_like(values)

            eb = np.zeros_like(values)
            for i in range(len(values)):
                m = np.array(
                    [
                        [self.cov_data[i, 0], self.cov_data[i, 2]],
                        [self.cov_data[i, 2], self.cov_data[i, 1]],
                    ]
                )
                r = np.array(
                    [
                        [np.cos(theta[i]), -np.sin(theta[i])],
                        [np.sin(theta[i]), np.cos(theta[i])],
                    ]
                )
                m = np.matmul(r, m)
                eb[i] = np.sqrt(np.abs(m[0, 0])) / np.sqrt(naverages - 1)
                if self.proj_func == "phase":
                    eb[i] = np.arcsin(eb[i] / np.abs(self.avg_data[i])) * 180 / np.pi
        else:
            eb = data
        logging.debug(f"Computed error bars: {eb}", )
        return eb

    def get_naverages(self):
        if self.dig_type == "alz":
            return self.instruments["alazar"].get_naverages()
        else:
            return self._dig.get_naverages()

    def post_process(self):
        """
        Post-process acquired data, i.e. convert complex IQ values to real
        numbers.
        """
        if not self.keep_data:
            self.drop_data()

        if self.pp_data is None:
            return
        self.pp_data[:] = self.complex_to_real(self.avg_data[:])

    def get_ys_fig(self, data=None, fig=None):
        """
        Return a plottable Y data array and a figure object to plot in.
        """
        if fig is None:
            fig = self.get_figure()
        if data is None:
            return self.get_ys(), fig
        else:
            return data, fig

    def analyze(self, data=None, fig=None):
        """
        Should be implemented in derived class.
        Best is to use a function that is defined outside of your measurement
        class so that you can reload a module and use the updated analysis
        function from an old measurement instance.
        """
        if not self.analysis_func:
            raise Exception("Either overload analyze() or specify an analysis_func")
        ret = self.analysis_func(self, data, fig)
        if hasattr(self, "saveas") and self.saveas:
            self.fig.canvas.draw()
            self.fig.savefig(self.saveas)
        return ret

    def plot_dataset(self, xs, ys, *args, **kwargs):
        kwargs["ls"] = "None"
        kwargs["marker"] = "s"
        kwargs["ms"] = 3
        ret = self.fig.axes[0].plot(xs, ys, *args, **kwargs)
        self._datacol = ret[0].get_c()

    def plot_fit(self, xs, ys, *args, **kwargs):
        kwargs["ls"] = "-"
        kwargs["dashes"] = (2, 2)
        kwargs["ms"] = 3
        kwargs["color"] = self._datacol
        self.fig.axes[0].plot(xs, ys, *args, **kwargs)

    def save_fig(self, fn=None):
        """
        Save the figure belonging to this measurement.
        """
        if fn is None:
            fn = os.path.join(
                config.datadir,
                f"images/{self._timestamp_str}_{self.name}.{self.imagetype}",
            )
        fdir = os.path.split(fn)[0]
        if not os.path.isdir(fdir):
            os.makedirs(fdir)
        kwargs = dict()
        if self.imagetype == "png":
            kwargs["dpi"] = 200
        if self.fig:
            self.fig.savefig(fn, **kwargs)

    def plot_histogram(self, data):
        fig = self.get_figure()
        avg = np.average(data)
        logging.info(f"Histogram data shape: {np.shape(data)}", )
        datasets = [data]
        if self.cyclelen == 2:
            data1 = data[::2]
            data2 = data[1::2]
            datasets = [data1, data2]
        elif self.cyclelen == 3:
            data1 = data[::3]
            data2 = data[1::3]
            data3 = data[2::3]
            datasets = [data1, data2, data3]
        logging.info(f"Average I,Q is: {avg}", )

        if self.cyclelen == 3:
            cmap_names = ["Blues", "Reds", "Greens"]
            for dataset, cmap_name in zip(datasets, cmap_names):
                fig.axes[0].hexbin(
                    np.real(dataset), np.imag(dataset), alpha=0.4, cmap=cmap_name
                )
        else:
            fig.axes[0].hexbin(
                np.real(data), np.imag(data), label=f"avg={avg}", cmap=mpl.cm.hot
            )

        if self.residuals:
            colors = [None, "r", None]
            for idx, dataset in enumerate(datasets):
                color = colors[idx] if idx < len(colors) else None
                fig.axes[1].hist(self.complex_to_real(dataset), bins=64, color=color)

    #            ax2 = fig.axes[1].twinx()
    #            ax2.set_zorder(fig.axes[1].zorder+1)
    #            ax2.patch.set_visible(False)
    #            ax2.plot((bins[:-1]+bins[1:])/2, np.cumsum(n), 'k')
    #            ax2.plot((bins[:-1]+bins[1:])/2, np.sum(n) - np.cumsum(n), 'r')

    #########################################################
    # Sequencer helper functions
    #########################################################

    def get_readout_pulse(self, pulse_len=None):
        if pulse_len is None:
            pulse_len = self.readout_info.pulse_len

        return sequencer.Combined(
            [
                pulselib.Constant(pulse_len, 1, 
                                  chan=self.readout_info.readout_chan),
                pulselib.Constant(pulse_len, 1, 
                                  chan=self.readout_info.acq_chan),
            ]
        )


class Measurement1D(Measurement):
    """
    Base class for 1D measurements such as T1 or T2.
    """

    def __init__(self, cyclelen, **kwargs):
        super().__init__(cyclelen, **kwargs)

    def update(self, avg_data):
        ys = self.get_ys(avg_data)
        fig = self.get_figure()
        fig.axes[0].clear()
        if hasattr(self, "xs"):
            fig.axes[0].plot(self.xs, ys)
        else:
            fig.axes[0].plot(ys)
        fig.canvas.draw()

    def analyze_parabola(self, data=None, fig=None, xlabel="", ylabel=""):
        """
        Standard analysis function to fit a parabola and return the extremum.
        """

        ys, fig = self.get_ys_fig(data, fig)
        xs = self.xs

        p = np.polyfit(xs, ys, 2)
        self.fit_params = p
        minmax = "max" if (p[0] < 0) else "min"
        minmaxpos = -p[1] / 2 / p[0]
        txt = f"Fit, {minmax} at {minmaxpos:.6f}"
        fig.axes[0].plot(xs, ys, "ks", ms=3)
        fig.axes[0].plot(xs, xs**2 * p[0] + xs * p[1] + p[2], label=txt)
        fig.axes[0].set_ylabel(ylabel)
        fig.axes[0].set_xlabel(xlabel)
        fig.axes[0].legend(loc=0)
        plt.legend()

        fig.axes[1].plot(xs, ys - (xs**2 * p[0] + xs * p[1] + p[2]), "k", marker="s")
        fig.canvas.draw()

        return minmaxpos


class Measurement2D(Measurement):
    """
    Base class for 2D measurements such as Q- or Wigner functions.
    """

    def __init__(self, cyclelen, style=STYLE_IMAGE, **kwargs):
        self.style = style
        super().__init__(cyclelen, **kwargs)

    def get_plotxsys(self):
        if self.style == STYLE_IMAGE:
            dx = (self.xs[1] - self.xs[0]) / 2.0
            xs = np.linspace(
                np.min(self.xs) - dx, np.max(self.xs) + dx, len(self.xs) + 1
            )
            dy = (self.ys[1] - self.ys[0]) / 2.0
            ys = np.linspace(
                np.min(self.ys) - dy, np.max(self.ys) + dy, len(self.ys) + 1
            )
            return xs, ys
        else:
            return self.xs, self.ys

    def update(self, avg_data):
        zs = self.get_ys(avg_data)
        fig = self.get_figure()
        fig.axes[0].clear()
        if hasattr(self, "xs") and hasattr(self, "ys"):
            zs = zs.reshape((len(self.ys), len(self.xs)))
            xs, ys = self.get_plotxsys()
            if self.style == STYLE_IMAGE:
                fig.axes[0].pcolormesh(xs, ys, zs, cmap=plt.get_cmap("RdBu"))
                fig.axes[0].set_xlim(xs.min(), xs.max())
                fig.axes[0].set_ylim(ys.min(), ys.max())
                fig.canvas.draw()
            else:
                for i_y, y in enumerate(ys):
                    fig.axes[0].plot(xs, zs[:, i_y], label=f"{y:.3f}")
                fig.axes[0].legend(loc=0)
        else:
            logging.warning("Unable to plot 2D array without xs and ys")
