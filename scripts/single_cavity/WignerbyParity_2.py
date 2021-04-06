import numpy as np
import matplotlib.pyplot as plt
from measurement import Measurement2D
#from lib.math import fit
from pulseseq.sequencer import *
from pulseseq.pulselib import *

def analysis(meas, data=None, fig=None):
    zs, fig = meas.get_ys_fig(data, fig)
    zs = zs.reshape(len(meas.ys), len(meas.xs))
    xs, ys = meas.get_plotxsys()
    ax = fig.axes[0]
    plt.sca(ax)
    
    if meas.bgcor == True:
#        vmax = meas.zmax
        if meas.zmax is not None:
            vmax = meas.zmax
        else:
            vmax = max(np.absolute(zs.flatten())) # sorry this is not done yet.
        vmin = -vmax
    else:
        zavg=(meas.zmin+meas.zmax)/2.0
        diff = max(max(zs.flatten())-zavg, zavg-min(zs.flatten()))
        vmax = zavg+diff
        vmin = zavg-diff
    
    pc = ax.pcolormesh(xs, ys, zs, vmin=vmin, vmax=vmax, cmap=plt.get_cmap('RdBu'))
    fig.colorbar(pc)

    ax.set_xlim(xs.min(), xs.max())
    ax.set_ylim(ys.min(), ys.max())
#    if meas.zmin is not None and meas.zmax is not None:  (was trying to force set data range for color bar)
#        ax.set_zlim(meas.zmin, meas.zmax())
    ax.set_xlabel(r'$Re \{\alpha \}$')
    ax.set_ylabel(r'$Im \{\alpha \}$')
    ax.xaxis.set_ticks_position('top')   # to move the x ticks to top (juliang)
    ax.xaxis.set_label_position('top')# to move the x label to top (juliang)
    fig.canvas.draw()

class WignerFunction2(Measurement2D):

    def __init__(self, qubit_info, ef_info, cav_info, xs, ys, t_ge=0, t_gf=0, t_ef=0, 
                 #amax=None, N=None, amaxx=None, Nx=None, amaxy=None, Ny=None,
                 cav_switch=None, seq=None, delay=0, saveas=None, bgcor=False,
                 zmin=None, zmax=None, Qswitch_infoA=None, Qswitch_infoB=None, 
                 rotation=0, **kwargs):
        self.qubit_info = qubit_info
        self.ef_info = ef_info
        self.cav_info = cav_info
        self.t_ge = t_ge
        self.t_gf = t_gf
        self.t_ef = t_ef
        self.QswA = Qswitch_infoA
        self.QswB = Qswitch_infoB
        if seq is None:
            seq = [Trigger(250)]
        self.seq = seq
        self.delay = delay
        self.saveas = saveas
        self.bgcor = bgcor
        self.cav_switch = cav_switch
        self.zmin=zmin
        self.zmax=zmax
        self.rotation=rotation

#        if amaxx is not None:
#            xs = np.linspace(-amaxx, amaxx, Nx)
#            ys = np.linspace(-amaxy, amaxy, Ny)
#        else:
#            Nx, Ny = N, N
#            xs = np.linspace(-amax, amax, N)
#            ys = xs

        XS, YS = np.meshgrid(xs, ys)
        self.displacements = -(XS + 1j*YS)
        self.xs = xs
        self.ys = ys

        npoints = self.displacements.size
        if bgcor:
            npoints *= 2
        super(WignerFunction2, self).__init__(npoints, infos=(qubit_info, cav_info), residuals=False, **kwargs)
        self.data.create_dataset('displacements', data=self.displacements, dtype=np.complex)
        self.data.set_attrs(
            delay=delay,
            bgcor=bgcor
        )

    def generate(self):
        '''
        If bg = True generate background measurement, i.e. without qubit pi pulse
        '''

        s = Sequence()

        ge = self.qubit_info.rotate
        ef = self.ef_info.rotate
        c = self.cav_info.rotate
        for i, alpha in enumerate(self.displacements.flatten()):
            for i_bg in range(2):
                    
                if i_bg == 1 and not self.bgcor:
                    continue

                temp_seq = self.seq[:]

                temp_seq += [c(np.abs(alpha), np.angle(alpha) - self.rotation)]

                if i_bg == 0:
                    
                    if self.t_ge > 0:
                        temp_seq += [ge(np.pi/2, X_AXIS)]
                        temp_seq += [Delay(self.t_ge)]
                    if self.t_gf > 0:
                        temp_seq += [ge(np.pi/2, X_AXIS)]
                        temp_seq += [ef(np.pi, X_AXIS)]
                        temp_seq += [Delay(self.t_gf)]
                        temp_seq += [ef(np.pi, X_AXIS)]
                    if self.t_ef > 0:
                        temp_seq += [ef(np.pi/2, X_AXIS)]
                        temp_seq += [Delay(self.t_ef)]
                        temp_seq += [ge(np.pi, X_AXIS)]
                        temp_seq += [ef(np.pi, X_AXIS)]
                    temp_seq += [ge(np.pi/2, X_AXIS)]
                else:
#                    s.append(ge(np.pi/2, Y_AXIS
                    if self.t_ge > 0:
                        temp_seq += [ge(np.pi/2, X_AXIS)]
                        temp_seq += [Delay(self.t_ge)]
                    if self.t_gf > 0:
                        temp_seq += [ge(np.pi/2, X_AXIS)]
                        temp_seq += [ef(np.pi, X_AXIS)]
                        temp_seq += [Delay(self.t_gf)]
                        temp_seq += [ef(np.pi, X_AXIS)]
                    if self.t_ef > 0:
                        temp_seq += [ef(np.pi/2, X_AXIS)]
                        temp_seq += [Delay(self.t_ef)]
                        temp_seq += [ge(np.pi, X_AXIS)]
                        temp_seq += [ef(np.pi, X_AXIS)]
                    temp_seq += [ge(-np.pi/2, X_AXIS)]

                if self.delay:
                    temp_seq += [Delay(self.delay)]
                
                s.append(Join(temp_seq))
#                temp_seq += [Combined([
#                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
#                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
#                ])]
                s.append(self.readout_driver.do_get_sequence(self.readout_qubit_info))
                s.append(Delay(2000))
                

        s = self.get_sequencer(s)
        seqs = s.render(debug=False)
        return seqs


    def generate_old(self):
        '''
        If bg = True generate background measurement, i.e. without qubit pi pulse
        '''

        s = Sequence()

        ge = self.qubit_info.rotate
        ef = self.ef_info.rotate
        c = self.cav_info.rotate
        for i, alpha in enumerate(self.displacements.flatten()):
            for i_bg in range(2):

                if i_bg == 1 and not self.bgcor:
                    continue


                s.append(self.seq)
                if self.cav_switch is not None:
                    s.append(Constant(500, 1, chan=self.cav_switch))
                    s.append(Combined([c(np.abs(alpha), np.angle(alpha)),
                                       Constant(int(self.cav_info.w*4), 1, chan=self.cav_switch)]))
                else:
                    s.append(c(np.abs(alpha), np.angle(alpha)))

                if i_bg == 0:
                    s.append(ge(np.pi/2, X_AXIS))
                    if self.t_ge > 0:
                        s.append(Delay(self.t_ge))
                    if self.t_gf > 0:
                        s.append(ef(np.pi, X_AXIS))
                        s.append(Delay(self.t_gf))
                        s.append(ef(np.pi, X_AXIS))
                    s.append(ge(np.pi/2, X_AXIS))
                else:
#                    s.append(ge(np.pi/2, Y_AXIS))
                    s.append(ge(np.pi/2, X_AXIS))
                    if self.t_ge > 0:
                        s.append(Delay(self.t_ge))
                    if self.t_gf > 0:
                        s.append(ef(np.pi, X_AXIS))
                        s.append(Delay(self.t_gf))
                        s.append(ef(np.pi, X_AXIS))
                    s.append(ge(-np.pi/2, X_AXIS))

                if self.delay:
                    s.append(Delay(self.delay))

                s.append(Combined([
                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
                ]))
                s.append(Delay(800))

            if self.QswA is not None or self.QswB is not None:
                s.append(Repeat(Delay(1000), 20))   # wait for alazar acquisition to finish
                s.append(Combined([
                    Repeat(Constant(5000, 0.4, chan=self.QswA.sideband_channels[0]), 120),
                    Repeat(Constant(5000, 0.4, chan=self.QswA.sideband_channels[1]), 120),
                    Repeat(Constant(5000, 0.6, chan=self.QswB.sideband_channels[0]), 120),
                    Repeat(Constant(5000, 0.6, chan=self.QswB.sideband_channels[1]), 120),
                    Repeat(Constant(5000, 1, chan='1m1'), 120),     # Readout pump tone switch
                    Repeat(Constant(5000, 0.0001, chan=5), 120),         # Qubit/Readout master switch
                ]))

        s = self.get_sequencer(s)
        seqs = s.render(debug=False)
        return seqs

    def get_ys(self, data=None):
        ys = super(WignerFunction2, self).get_ys(data)
        if self.bgcor:
#            return (ys[::2]-ys[1::2])*1.0/(1.0-ys[1::2])
            return ys[::2]-ys[1::2]
        return ys

    def analyze(self, data=None, fig=None):
        self.fit_params = analysis(self, data, fig)