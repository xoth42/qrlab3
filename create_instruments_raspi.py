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

Agilent1 = instruments.create('Agilent1', 'Agilent_B2901A', address='GPIB1::23::INSTR')
Agilent2 = instruments.create('Agilent2', 'Agilent_B2901A', address='GPIB1::24::INSTR')
Agilent3 = instruments.create('Agilent3', 'Agilent_B2901A', address='GPIB1::25::INSTR')


Keithley = instruments.create('Keithley', 'Keithley2400', address='GPIB1::22::INSTR')



