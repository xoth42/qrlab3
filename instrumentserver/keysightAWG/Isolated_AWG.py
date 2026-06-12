# import logging setup
import logging

logger = logging.getLogger(__name__)

## For debug
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

try:
    import keysightSD1 as key
except ModuleNotFoundError:
    # Not in current dir? try full path
    import instrumentserver.keysightAWG.keysightSD1 as key


"""E2E AWG test script to show sign of life on an awg slot and chassis. 
Starts with Chassis 0, Slot 8, waveform Gaussian.csv.
"""
def AWG_test(product="M3202A", chassis=0, slot=8):
    m = key.SD_Module()
    rc = m.openWithSlot(product, chassis, slot)
    print(f"openWithSlot({product}, {chassis}, {slot}) ->", rc)
    if rc <= 0:
        print("openWithSlot error:", key.SD_Error.getErrorMessage(rc))
        return rc

    result = m.runSelfTest()
    print("runSelfTest ->", result)
    print(key.SD_Error.getErrorMessage(result))
    m.close()
    return result



"""
4. 2. 1 Example Program
"""
def Example_4_2_1(
    AWG_PRODUCT = "M3202A", # Product's model number
    CHASSIS = 0, # Chassis number holding product
    AWG_SLOT = 8, # Slot number of product in chassis
    # Specify values for variables related to the AWG waveform
    waveform_number = 1, # Numerical label of AWG waveform
    cycles = 1,  # Number of times to play a waveform from same channel
    start_delay = 0,    # Delay the start of the waveform playback
    prescalar = 0,    # How much to scale the outgoing waveform
    waveform_csv = r"C:\qrlab-3\instrumentserver\keysightAWG\waveforms\Gaussian.csv", # Path to your qrlab waveform file
):
    
    awg = key.SD_AOU()
    # Create an AWG object
    #----------
    # Open and connect to the specific AWG, using openWithSlot().
    # If any errors occur, they are negative numbers and saved into aouID.
    aouID = awg.openWithSlot(AWG_PRODUCT, CHASSIS, AWG_SLOT)
    # Check aouID for errors and close connection if an error is found
    if aouID < 0:
        # If aouID is a negative number, an error occurred so print it out
        print("ERROR")
        # Print error code so it can be looked up in the Keysight SD1 error list.
        print("aouID:", aouID)
        # Since there was an error, close the connection with the AWG.
        awg.close()
        # Print out a message that the connection is closed.
        print()
        print("AOU connection closed")
        return aouID
        
    # If NO errors occur, flush/remove remaining old waveforms from AWG memory
    awg.waveformFlush()
    #----------
    # Set all four channels (1 to 4) of the AWG output mode
    awg.channelWaveShape(1, key.SD_Waveshapes.AOU_AWG)
    awg.channelWaveShape(2, key.SD_Waveshapes.AOU_AWG)
    awg.channelWaveShape(3, key.SD_Waveshapes.AOU_AWG)
    awg.channelWaveShape(4, key.SD_Waveshapes.AOU_AWG)
    #----------
    # Create a new wave object
    wave = key.SD_Wave()
    #----------
    # Load a .csv file as the wave data
    r = wave.newFromFile(waveform_csv)
    if r < 0:
        print("ERROR")
        print("newFromFile failed with error code:", r)
        awg.close()
        print()
        print("AOU connection closed")
        return r
    #----------
    # Load the wave csv file into AWG memory,
    # assigning it the arbitrary number set earlier in this program.
    rc = awg.waveformLoad(wave, waveform_number)
    logger.debug("waveformLoad returned: %d", rc)
    #----------

    # Optional: make the queue cyclic (good habit if later you queue multiple wfs)
    for ch in (1, 2, 3, 4):
        rc = awg.AWGqueueConfig(ch, 1)  # 1 = cyclic queue
        logger.debug("AWGqueueConfig(%d, 1) returned: %d", ch, rc)


    # Queue everything that will be playing, with AWGqueueWaveform()
    # AWGqueueWaveform(CHANNEL, number assigned to wave you want,
    # trigger mode, delay before start (ns), number of times to play, prescaler)
    for ch in (1, 2, 3, 4):
        rc = awg.AWGqueueWaveform(ch, waveform_number, key.SD_TriggerModes.SWHVITRIG,
            start_delay, cycles, prescalar)
        logger.debug("AWGqueueWaveform(%d) returned: %d", ch, rc)
    #----------
    # Set the relative amplitudes for each channel.
    # CSV waveforms are normalized between-1 and 1 * amplitude.
    for ch in (1, 2, 3, 4):
        rc = awg.channelAmplitude(ch, 1.5)
        logger.debug("channelAmplitude(%d) returned: %d", ch, rc)
    #----------
    # Start each channel’s waveform- If trigger mode was set to AUTO, they would
    # start playing automatically but, since SD_TriggerModes.SWHVITRIG was
    # selected, a software trigger is required to play each channel’s waveform
    for ch in (1, 2, 3, 4):
        rc = awg.AWGstart(ch)
        logger.debug("AWGstart(%d) returned: %d", ch, rc)
    #----------
    # Trigger waveforms with software triggers to play the loaded waveforms
    for ch in (1, 2, 3, 4):
        rc = awg.AWGtrigger(ch)
        logger.debug("AWGtrigger(%d) returned: %d", ch, rc)

    # AWG never actually starts playing
    # Even if queued and started, it’s useful to check AWGisRunning(nAWG) and AWGnWFplaying(nAWG) to verify the hardware thinks it’s playing.
    for ch in (1, 2, 3, 4):
        is_running = awg.AWGisRunning(ch)
        wf_playing = awg.AWGnWFplaying(ch)
        logger.debug("AWGisRunning(%d) -> %s, AWGnWFplaying(%d) -> %s", ch, is_running, ch, wf_playing)
        if is_running:
            print(f"Channel {ch} is running and playing waveform {wf_playing}.")

    #----------
    # Close the connection with the AWG hardware.
    awg.close()


def Example_4_2_3(
    # Specify values for variables
    product = 'M3202A', # Product's model number
    chassis = 0,
    # Chassis number holding product
    slot = 8,
    channel = 2,
    amplitude = 0.1,
    # Slot number of product in chassis
    # Channel being used
    # (Unit: Vpp) Amplitude of AWG output signal (0.1 Vpp)
    waveshape = key.SD_Waveshapes.AOU_AWG, # Specify AWG output
    delay = 0,
    # (Unit: ns) Delay after trigger before generating output.
    cycles = 0, # Number of cycles. Zero specifies infinite cycles.
    # Otherwise, a new trigger is required to actuate each cycle
    prescaler = 0, # Integer division reduces high freq signals to lower frequency
    #----------
):
    """
    4.2.3 Example Program Using Python to Produce a Sawtooth Wave from an Array
    This example program shows Python using the Keysight SD1 Programming Libraries
    to produce a Sawtooth Wave out of Keysight M3202A PXIe AWG's channel 1.
    """
    #----------
    # Python- Sample Application to set up the AWG
    #
    # to output an array that was created with numpy.
    #----------
    # Import required system components
    #----------
    # Append the system path to include the
    # location of Keysight SD1 Programming Libraries then import the library
    # sys.path.append('C:\Program Files (x86)\Keysight\SD1\Libraries\Python')
    # import keysightSD1 # Import Python SD1 library and AWG/Digitizer commands.
    import numpy  # Import numpy which is used to make an array

    #----------
  
    # Select settings and use specified variables
    awg = key.SD_AOU()
    # Creates SD_AOU object called awg
    rc = awg.openWithSlot(product, chassis, slot) # Connects awg object to module
    logger.debug("openWithSlot(%s, %d, %d) returned: %d", product, chassis, slot, rc)
    if rc < 0:
        logger.debug("Failed to open AWG, error code: %d", rc)
        awg.close()
        return rc
    rc = awg.channelAmplitude(channel, amplitude) # Sets output amplitude for awg
    logger.debug("channelAmplitude(%d, %s) returned: %d", channel, amplitude, rc)
    rc = awg.channelWaveShape(channel, waveshape) # Sets output signal type for awg
    logger.debug("channelWaveShape(%d) returned: %d", channel, rc)
    rc = awg.waveformFlush() # Cleans the queue
    logger.debug("waveformFlush returned: %d", rc)
    rc = awg.AWGflush(channel) # Stops signal from outputing out of channel 1
    logger.debug("AWGflush(%d) returned: %d", channel, rc)
    # Create an array that represents a sawtooth signal using "numpy"
    array = numpy.zeros(1000) # Create array of zeros with 1000 elements
    array[0] =-0.5 # Initialize element 0 as-0.5
    for i in range(1, len(array)): # This for..loop will increment from-0.5
        array[i] = array[i-1] + .001 # Increment by .001 every iteration
    logger.debug("Sawtooth array built, length: %d, first: %s, last: %s", len(array), array[0], array[-1])
    wave = key.SD_Wave() # Create SD_Wave object and call it "wave"
    # (will place the array inside "wave")
    error = wave.newFromArrayDouble(key.SD_WaveformTypes.WAVE_ANALOG,
    array.tolist()) # Place the array into the "wave" object
    logger.debug("newFromArrayDouble returned: %d", error)
    waveID = 0 # This number is arbitrary and used to identify the waveform
    rc = awg.waveformLoad(wave, waveID) # Load the "wave" object and give it an ID
    logger.debug("waveformLoad(waveID=%d) returned: %d", waveID, rc)
    rc = awg.AWGqueueWaveform(channel, waveID, key.SD_TriggerModes.SWHVITRIG,
    delay, cycles, prescaler)
    logger.debug("AWGqueueWaveform(%d) returned: %d", channel, rc)
    # Queue waveform to prepare it to be output
    #----------
    rc = awg.AWGstart(channel) # Start the AWG
    logger.debug("AWGstart(%d) returned: %d", channel, rc)
    rc = awg.AWGtrigger(channel) # Trigger the AWG to begin
    logger.debug("AWGtrigger(%d) returned: %d", channel, rc)
    #----------
    is_running = awg.AWGisRunning(channel)
    wf_playing = awg.AWGnWFplaying(channel)
    logger.debug("AWGisRunning(%d) -> %s, AWGnWFplaying(%d) -> %s", channel, is_running, channel, wf_playing)
    if is_running:
        print(f"Channel {channel} is running and playing waveform {wf_playing}.")
    #----------
    # Close the connection between the AWG object and the physical AWG hardware.
    awg.close()
    logger.debug("AWG connection closed")


"""
Testing the 'AWGFromFile' 

def AWGFromFile(self, nAWG, waveformFile, triggerMode, startDelay, cycles, prescaler, paddingMode = 0) :

Provides a one-step method to load, queue, and start a single waveform in one of the
module's AWGs. The waveform can be loaded from an array of points in memory or
from a file.
Step-by-Step Programming: This AWG function is equivalent to:
1. creating a waveform with new on page 140
2. calling waveformLoad on page 96
3. followed by AWGqueueWaveform on page 104
4. and then calling AWGstart on page 10
"""
def FromFile_Example(
    AWG_PRODUCT = "M3202A", # Product's model number
    CHASSIS = 0, # Chassis number holding product
    AWG_SLOT = 8, # Slot number of product in chassis
    CHANNEL = 2, # Channel being used
    waveform_csv = r"C:\qrlab-3\instrumentserver\keysightAWG\waveforms\Gaussian.csv", # Path to your qrlab waveform file
    triggermode = key.SD_TriggerModes.AUTOTRIG, # Trigger mode for the AWG. This example uses software trigger.
    # Specify values for variables related to the AWG waveform
    waveform_number = 1, # Numerical label of AWG waveform
    cycles = 0,  # Number of times to play a waveform from same channel
    start_delay = 0,    # Delay the start of the waveform playback
    prescaler = 0,    # How much to scale the outgoing waveform
  
):
    awg = key.SD_AOU()
    aouID = awg.openWithSlot(AWG_PRODUCT, CHASSIS, AWG_SLOT)
    print("openWithSlot ->", aouID)
    if aouID < 0:
        awg.close()
        print("ERROR")
        print("aouID:", aouID)
        return aouID

    # Use the AWGFromFile function to load, queue, and start the waveform in one step
    rc = awg.AWGFromFile(CHANNEL, waveform_csv,triggermode,
        start_delay, cycles, prescaler)
    print("AWGFromFile returned:", rc)

    is_running = awg.AWGisRunning(CHANNEL)
    wf_playing = awg.AWGnWFplaying(CHANNEL)
    print(f"Channel {CHANNEL} is running: {is_running}, playing waveform: {wf_playing}")
    return awg



# To help debug possible clock issues
def debug_clock(AWG_PRODUCT="M3202A", CHASSIS=0, AWG_SLOT=8):
    awg = key.SD_AOU()
    aouID = awg.openWithSlot(AWG_PRODUCT, CHASSIS, AWG_SLOT)
    print("openWithSlot ->", aouID)
    if aouID < 0:
        return

    f = awg.clockGetFrequency()
    print("clockGetFrequency ->", f)

    # Try forcing a sane internal clock; for M3202A internal is 1 GS/s when prescaler=0
    f_set = awg.clockSetFrequency(1e9, 1)  # mode=1 is the usual "internal" mode
    print("clockSetFrequency(1e9, 1) ->", f_set)

    f2 = awg.clockGetFrequency()
    print("clockGetFrequency (after set) ->", f2)

    awg.close()




"""
# ----------------------------------------------------------------------
# Helper: decode SD1 error codes
# ----------------------------------------------------------------------
def check_err(label, ret):
    if ret < 0:
        msg = key.SD_Error.getErrorMessage(ret)
        raise RuntimeError(f"{label} failed with {ret}: {msg}")

# ----------------------------------------------------------------------
# 0. Open AWG and print basic info
# ----------------------------------------------------------------------
awg = key.SD_AOU()
aouID = awg.openWithSlot(AWG_PRODUCT, CHASSIS, AWG_SLOT)
check_err("openWithSlot", aouID)

part = awg.getProductNameBySlot(CHASSIS, AWG_SLOT)
serial = awg.getSerialNumberBySlot(CHASSIS, AWG_SLOT)
count = awg.moduleCount()
status = awg.getStatus()
clk = awg.clockGetFrequency()

print("Opened AWG:")
print(f"  Product : {part}")
print(f"  Serial  : {serial}")
print(f"  Modules : {count}")
print(f"  Status  : {status}")
print(f"  Clock   : {clk} Hz")

# ----------------------------------------------------------------------
# 1. Simple, obvious sine wave for scope debugging
#    - 2 V amplitude, 1 kHz, continuous
# ----------------------------------------------------------------------
print("\n=== Step 1: function-generator sine (visible on scope) ===")

check_err("AWGstopMultiple", awg.AWGstopMultiple(0xF))  # stop all 4 channels
check_err("AWGflush", awg.AWGflush(CHANNEL))            # clear queue on this channel

# Set channel to function generator mode (sine)
check_err("channelWaveShape-sine",
          awg.channelWaveShape(CHANNEL, key.SD_Waveshapes.AOU_SINUSOIDAL))
check_err("channelAmplitude-sine",
          awg.channelAmplitude(CHANNEL, 2.0))           # 2 V amplitude
check_err("channelOffset-sine",
          awg.channelOffset(CHANNEL, 0.0))
freq_ret = awg.channelFrequency(CHANNEL, 1e3)           # 1 kHz
print(f"  Sine freq set to ~{freq_ret} Hz")

print("  -> Connect the scope to channel", CHANNEL,
      " (50 Ω if possible), 1 V/div, 5–20 ms/div. You should see a big 1 kHz sine.")

time.sleep(2.0)  # just give you time to look

# ----------------------------------------------------------------------
# 2. Load Gaussian.csv as AWG waveform and play once
# ----------------------------------------------------------------------
print("\n=== Step 2: load Gaussian.csv and play one-shot on AWG ===")

gauss = key.SD_Wave()
ret = gauss.newFromFile(GAUSSIAN_CSV)
check_err("SD_Wave.newFromFile(Gaussian)", ret)

print("  Gaussian SD_Wave handle:", ret)

check_err("waveformFlush", awg.waveformFlush())
check_err("waveformLoad(gauss, 0)", awg.waveformLoad(gauss, 0))

# Configure channel to AWG mode
check_err("AWGflush", awg.AWGflush(CHANNEL))
check_err("channelWaveShape-AWG",
          awg.channelWaveShape(CHANNEL, key.SD_Waveshapes.AOU_AWG))
check_err("channelAmplitude-AWG",
          awg.channelAmplitude(CHANNEL, 1.0))
check_err("channelOffset-AWG",
          awg.channelOffset(CHANNEL, 0.0))

# One-shot queue: play waveform #0 once on a software trigger
check_err("AWGqueueConfig(one-shot)", awg.AWGqueueConfig(CHANNEL, 0))  # 0=one-shot
check_err("AWGqueueWaveform(Gaussian)",
          awg.AWGqueueWaveform(
              CHANNEL,
              0,                               # waveform index
              key.SD_TriggerModes.SWHVITRIG,   # software/HVI trigger
              0,                               # start delay
              1,                               # cycles = 1
              0                                # prescaler
          ))

check_err("AWGstart(Gaussian)", awg.AWGstart(CHANNEL))
check_err("AWGtrigger(Gaussian)", awg.AWGtrigger(CHANNEL))

time.sleep(0.1)  # short pulse; you may need a high-bandwidth scope trigger to see it

is_running = awg.AWGisRunning(CHANNEL)
wf_playing = awg.AWGnWFplaying(CHANNEL)
print(f"  After Gaussian shot: AWGisRunning={is_running}, AWGnWFplaying={wf_playing}")

# ----------------------------------------------------------------------
# 3. Long DC AWG waveform with many cycles (more sustained output)
# ----------------------------------------------------------------------
print("\n=== Step 3: long AWG waveform, many cycles ===")

# Build a long DC waveform: 10M points of +1.0
long_data = np.ones(10_000_000, dtype=float)  # ~10 ms at 1 GS/s
wave_long = key.SD_Wave()
ret = wave_long.newFromArrayDouble(key.SD_WaveformTypes.WAVE_ANALOG, long_data)
check_err("SD_Wave.newFromArrayDouble(long)", ret)

check_err("waveformFlush(long)", awg.waveformFlush())
check_err("waveformLoad(long, 0)", awg.waveformLoad(wave_long, 0))

# Configure channel to AWG mode again
check_err("AWGflush(long)", awg.AWGflush(CHANNEL))
check_err("channelWaveShape-AWG-long",
          awg.channelWaveShape(CHANNEL, key.SD_Waveshapes.AOU_AWG))
check_err("channelAmplitude-AWG-long",
          awg.channelAmplitude(CHANNEL, 1.0))
check_err("channelOffset-AWG-long",
          awg.channelOffset(CHANNEL, 0.0))

# Cyclic queue, play the long waveform many times
check_err("AWGqueueConfig(cyclic)", awg.AWGqueueConfig(CHANNEL, 1))  # 1=cyclic
cycles = 1000
check_err("AWGqueueWaveform(long)",
          awg.AWGqueueWaveform(
              CHANNEL,
              0,
              key.SD_TriggerModes.SWHVITRIG,
              0,
              cycles,
              0
          ))

check_err("AWGstart(long)", awg.AWGstart(CHANNEL))
check_err("AWGtrigger(long)", awg.AWGtrigger(CHANNEL))

print("  Monitoring AWG status for a few seconds:")
for i in range(10):
    is_running = awg.AWGisRunning(CHANNEL)
    wf_playing = awg.AWGnWFplaying(CHANNEL)
    print(f"    t={i*0.5:.1f}s : AWGisRunning={is_running}, AWGnWFplaying={wf_playing}")
    time.sleep(0.5)

print("  -> On the scope, this should look like a relatively long, flat pulse at +1 V")
print("     repeating many times (depending on how you trigger).")

# ----------------------------------------------------------------------
# 4. Cleanup
# ----------------------------------------------------------------------
print("\n=== Cleanup ===")
check_err("AWGstop(long)", awg.AWGstop(CHANNEL))
check_err("AWGflush(end)", awg.AWGflush(CHANNEL))
awg.close()
print("AWG closed.")

"""