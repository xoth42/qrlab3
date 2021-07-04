#Small script to test how the tk gui performs.
#Josh Carey 1/26/18
#joshuacarey@umass.edu
import objectsharer as objsh
import time
new_backend = objsh.ZMQBackend()
new_backend.start_server("127.0.0.1")
new_backend.connect_to("tcp://127.0.0.1:55555")
instr = objsh.helper.find_object('instruments')
instr['qubit1ge'].set('sideband_phase', 1.0)
while True:
    value = instr['qubit1ge'].get('sideband_phase')
    value = value + 0.1
    instr['qubit1ge'].set('sideband_phase', value)
    print(value)
    time.sleep(1)