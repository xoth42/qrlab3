import pyvisa
import time
import numpy as np
import matplotlib.pyplot as plt

'''
http://www.home.agilent.com/upload/cmc_upload/All/86100_Programming_Guide.pdf?&cc=US&lc=eng
'''

debug = False

NO_ERROR = '0,"No error"'




class FastScope:

    def __init__(self, address):
        self.ins = pyvisa.ResourceManager().open_resource(address)
        self.ins.timeout = 5000
        self.ins.read_termination = '\n'
        self.ins.write_termination = '\n'
        self.reset()
        self.set_oscilloscope_mode()
        self.set_num_pts_manual()
        self.set_num_pts(10000)
        self.set_trig_frontpanel(level=0.5)

        self.x = np.array([])
        self.y = np.array([])

    def wr(self, command):
        self.ins.write(command+'\n')
        if debug:
            return self.error_check()

    def ask(self,command,bypass=False):
        ret = self.ins.query(command+'?\n')
        if debug and not bypass:
            ''' The bypass command makes sure that error querying (an ask)
            doesn't lead to infinite recursion'''
            err = self.error_check()
            return ret
        else:
            return ret

    def reset(self):
        self.wr('*RST')

    def clear(self):
        '''Clears error queue, others'''
        self.wr('*CLS')

    def set_oscilloscope_mode(self):
        self.wr('SYST:MODE OSC')

    def set_trig_frontpanel(self,level=None):
        self.wr('TRIG:SOUR FPAN')
        self.wr('TRIG:BWL EDGE')
        if level:
            self.set_trig_level(level)

    def set_trig_freerun(self):
        self.wr('TRIG:SOUR FRUN')

    def set_trig_level(self,trig_lev):
        self.wr(f'TRIG:LEV {trig_lev:f}')

    def error_query(self):
        return self.ask('SYSTEM:ERROR',bypass=True)

    def report_error(self,error):
        if error != NO_ERROR:
            print(f'\tERROR: {error}')

    def error_check(self):
        ret = self.error_query()
        if ret != NO_ERROR:
            self.report_error(ret)
            self.print_error_queue()
            return False #Return if there is an error.
        else:
            return True #No error return

    def print_error_queue(self):
        ret = self.error_query()
        for _ in range(100):
            if ret == NO_ERROR:
                break
            self.report_error(ret)
            ret = self.error_query()
        else:
            raise IOError('Error queue did not clear after 100 entries')

    def set_num_pts_manual(self):
        self.wr('ACQ:RLEN:AUT MAN')
        time.sleep(0.01)

    def set_num_pts_auto(self):
        self.wr('ACQ:RLEN:AUT AUT')

    def set_num_pts(self,num_pts):
        '''Requires being in manual num pts mode'''
        self.wr(f'ACQ:RLEN {int(num_pts)}')

    def set_time_range(self,full_range_in_seconds):
        return self.wr(f':TIM:RANG {full_range_in_seconds:f}')

    def set_averaging(self, num_avg):
        if num_avg == 0:
            self.wr('ACQ:SMO NONE')
        else:
            self.wr('ACQ:SMO AVER')
            self.wr(f'ACQ:ECO {int(num_avg)}')

    def set_time_offset(self,offset_in_seconds):
        #minimum 24ns
        self.wr(f':TIM:POS {offset_in_seconds:f}')

    def take_trace(self):
        x = self.ask('WAV:XYF:ASC:XDAT')
        x = np.array(x.split(','))
        self.x = x.astype(np.float)

        y = self.ask('WAV:XYF:ASC:YDAT')
        y = np.array(y.split(','))
        self.y = y.astype(np.float)

    def plot_trace(self):
        plt.plot(self.x,self.y)

    def set_voltage_range(self,voltage):
        '''set voltage in volts'''
        cmd = f'CHAN1:YSC {voltage/8.0:f}' #8 for 8 divs
        self.wr(cmd)

    def set_voltage_offset(self,offs):
        cmd = f'CHAN1:YOFF {offs:f}'
        self.wr(cmd)


    def clear_and_wait_for_averages(self,num_avg):
        '''

        does not actually work.


        This command takes over until the FS has taken the specified number
        of averages'''
        self.wr('LTESt:ACQuire:STATe ON')
        self.wr(f'LTESt:ACQuire:CTYPe:WAVeforms {int(num_avg)}')
        self.wr('ACQuire:SMOothing AVERage')
        self.wr(f'ACQuire:ECOunt {int(num_avg)}')
        self.wr('ACQuire:CDISplay')
        self.wr(':ACQuire:RUN')

        for _ in range(max(60, num_avg * 10)):
            ret = self.ask('*OPC')
            print(ret)
            if ret == '1':
                break
            time.sleep(1)
        else:
            raise IOError('Timed out waiting for averages')

#r = FastScope('TCPIP0::172.28.141.133::inst0::INSTR')
#time.sleep(2)
#r.take_trace()
#r = FastScope('fastscope')
##data = r.single_shot()
#data = r.take_single_channel(1)
#plt.plot(data, 'r-')
