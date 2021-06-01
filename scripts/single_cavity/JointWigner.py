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
    if meas.plot_type is 'shell':
        ax.set_xlabel(r'$Angle \{\alpha \}$')
        ax.set_ylabel(r'$Angle \{\beta \}$')
    elif meas.plot_type is None:
        if meas.ax1 == 0: # choose correct label based on ax1 and ax2
            ax.set_xlabel(r'$Re \{\alpha \}$')
        elif meas.ax1 == 1:
            ax.set_xlabel(r'$Im \{\alpha \}$')
        elif meas.ax1 == 2:
            ax.set_xlabel(r'$Re \{\beta \}$')
        elif meas.ax1 == 3:
            ax.set_xlabel(r'$Im \{\beta \}$')
        if meas.ax2== 0:
            ax.set_ylabel(r'$Re \{\alpha \}$')
        elif meas.ax2 == 1:
            ax.set_ylabel(r'$Im \{\alpha \}$')
        elif meas.ax2 == 2:
            ax.set_ylabel(r'$Re \{\beta \}$')
        elif meas.ax2 == 3:
            ax.set_ylabel(r'$Im \{\beta \}$')
#    ax.xaxis.set_ticks_position('top')   # to move the x ticks to top (juliang)
#    ax.xaxis.set_label_position('top')# to move the x label to top (juliang)
    fig.canvas.draw()

def ax2disp(xs, ys, ax1, ax2): # converts slices to displacements
    disp = np.zeros((len(xs) * len(ys), 4), dtype=float)
    xs, ys = np.meshgrid(xs, ys)
    xs = xs.flatten()
    ys = ys.flatten()
    disp[:,ax1] += xs
    disp[:,ax2] += ys
    return disp


class JointWigner(Measurement2D):

    def __init__(self, qubit_info, ef_info, cav_info1, cav_info2, xs, ys, ax1, ax2, t_ge=0, t_gf=0,
                 disp_array=None, cav_switch=None, seq=None, delay=0, saveas=None, bgcor=False,
                 zmin=None, zmax=None, plot_type = None,
                 rotation=0, **kwargs):
        self.qubit_info = qubit_info
        self.ef_info = ef_info
        self.cav_info1 = cav_info1
        self.cav_info2 = cav_info2
        self.t_ge = t_ge
        self.t_gf = t_gf
        if seq is None:
            seq = [Trigger(250)]
        self.seq = seq
        self.delay = delay
        self.saveas = saveas
        self.bgcor = bgcor
        self.cav_switch = cav_switch
        self.zmin=zmin
        self.zmax=zmax
        self.plot_type = plot_type
        self.rotation=rotation
        
        self.xs = xs
        self.ys = ys
        self.ax1 = ax1 # can be 0 thru 3 corresponding to re(a), im(a), re(b), im(b)
        self.ax2 = ax2 # can be 0 thru 3 corresponding to re(a), im(a), re(b), im(b)
        
 
                    
                    
        if disp_array is None and self.ax1 is not None:
            self.displacements = ax2disp(xs, ys, ax1, ax2)
        elif disp_array is not None:
            self.displacements = disp_array


        npoints = int(self.displacements.shape[0])
        if bgcor:
            npoints *= 2
        super(JointWigner, self).__init__(npoints, infos=(qubit_info, cav_info1, cav_info2), 
              residuals=False, **kwargs)
        self.data.create_dataset('disp0', data=self.displacements[:,0], dtype=np.float)
        self.data.create_dataset('disp1', data=self.displacements[:,1], dtype=np.float)
        self.data.create_dataset('disp2', data=self.displacements[:,2], dtype=np.float)
        self.data.create_dataset('disp3', data=self.displacements[:,3], dtype=np.float)
#        self.data.create_dataset('xs', data=self.xs, dtype=np.float)
#        self.data.create_dataset('ys', data=self.ys, dtype=np.float)
#        self.data.create_dataset('ax1', data=self.ax1, dtype=np.int)
#        self.data.create_dataset('ax2', data=self.ax2, dtype=np.int)
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
        c1 = self.cav_info1.rotate
        c2 = self.cav_info2.rotate
        for i, disp in enumerate(self.displacements):
            for i_bg in range(2):
                    
                if i_bg == 1 and not self.bgcor:
                    continue
                
                temp_seq = self.seq[:]
                
                    
                alpha = disp[0] + 1j * disp[1]
                beta = disp[2] + 1j* disp[3]
                temp_seq += [Combined(c1(np.abs(alpha), np.angle(alpha) - self.rotation), 
                                      c2(np.abs(beta),  np.angle(beta)  - self.rotation))]

                if i_bg == 0:
                    temp_seq += [ge(np.pi/2, X_AXIS)]
                    if self.t_ge > 0:
                        temp_seq += [Delay(self.t_ge)]
                    if self.t_gf > 0:
                        temp_seq += [ef(np.pi, X_AXIS)]
                        temp_seq += [Delay(self.t_gf)]
                        temp_seq += [ef(np.pi, X_AXIS)]
                    temp_seq += [ge(np.pi/2, X_AXIS)]
                else:
#                    s.append(ge(np.pi/2, Y_AXIS))
                    temp_seq += [ge(np.pi/2, X_AXIS)]
                    if self.t_ge > 0:
                        temp_seq += [Delay(self.t_ge)]
                    if self.t_gf > 0:
                        temp_seq += [ef(np.pi, X_AXIS)]
                        temp_seq += [Delay(self.t_gf)]
                        temp_seq += [ef(np.pi, X_AXIS)]
                    temp_seq += [ge(-np.pi/2, X_AXIS)]

                if self.delay:
                    temp_seq += [Delay(self.delay)]
                
                
                temp_seq += [self.readout_driver.do_get_sequence(self.readout_qubit_info)]
                temp_seq += [Delay(2000)]
                s.append(Join(temp_seq))
#                temp_seq += [Combined([
#                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
#                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
#                ])]

                

        s = self.get_sequencer(s)
        seqs = s.render(debug=False)
        return seqs



    def get_ys(self, data=None):
        ys = super(JointWigner, self).get_ys(data)
        if self.bgcor:
#            return (ys[::2]-ys[1::2])*1.0/(1.0-ys[1::2])
            return ys[::2]-ys[1::2]
        return ys

    def analyze(self, data=None, fig=None):
        self.fit_params = analysis(self, data, fig)