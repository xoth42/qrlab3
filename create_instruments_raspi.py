import time

if 1:
    import os
    os.system(r'C:\qrlab\start.bat')
    time.sleep(1)

from mclient import instruments

raspi = instruments.create('raspi', 'raspi_manager')
raspi.do_set_domain('172.30.52.81')
raspi.do_set_password('rafiki789')
raspi.connect_ssh()

LNA23 = instruments.create('LNA23', 'Agilent_B2901A', address='GPIB1::23::INSTR')
BBAC = instruments.create('BBAC', 'Agilent_B2901A', address='GPIB1::24::INSTR')
LNA1 = instruments.create('LNA1', 'Agilent_B2901A', address='GPIB1::25::INSTR')


IREF = instruments.create('IREF', 'Keithley2400', address='GPIB1::22::INSTR')


#DMM = instruments.create('DMM', 'Keithley2400', address='GPIB1::16::INSTR')
