/*
 ***************************************************************************
 * USB functions for SignalCore Inc SC5506A products using "libusb"
 * functions and driver
 *
 * "libusb" license is covered by the LGPL 
 *	
 *	Copyright (c) 2013 - 2014 SignalCore Inc.
 *	
 * rev 1.1
 *
 ****************************************************************************
 * SC5506A header file 
*/

#ifndef __SC5506A_H__
#define __SC5506A_H__

#include <libusb.h>

//  Define USB SignalCore ID

#define SCI_USB_VID					0x277C  // SignalCore Vendor ID 
#define	SCI_USB_PID					0x0016  // Product ID SC5506A
#define SCI_SN_LENGTH				0x08
#define SCI_PRODUCT_NAME			"SC5506A"

//  Define SignalCore USB endpoints
#define	SCI_ENDPOINT_IN_INT			0x81
#define	SCI_ENDPOINT_OUT_INT		0x02
#define	SCI_ENDPOINT_IN_BULK		0x83
#define	SCI_ENDPOINT_OUT_BULK		0x04

// 	Define for control endpoints
#define USB_ENDPOINT_IN				0x80
#define USB_ENDPOINT_OUT			0x00
#define USB_TYPE_VENDOR				(0x02 << 5)
#define USB_RECIP_INTERFACE			0x01

// Calibration EEPROM parameters dimensions		   

// channel index assignment
#define CH1								0   // channel #1 is 0 (zero)
#define CH2								1   // channel #2 is 1

// Attenuator assignments
#define CH1ATTEN0						0		
#define CH1ATTEN1						1
#define CH2ATTEN0						2
#define CH2ATTEN1						3

// EEPROM SIZE
#define CALEEPROMSIZE					65536  // bytes 
#define USEREEPROMSIZE					32768  // bytes

// The Fine tune frequency stepping modes
#define DISABLEDALC						1 // Disable ALC close loop, use open loop level control
#define DISABLEAUTOLEVEL				1 // Level correction is disabled when frequency is tuned, user set the new rf level
#define DDSFINEMODE						2 //1 Hz tuning steps, DDS & PLL implementation

// Define error codes used 
#define SUCCESS							0
#define USBDEVICEERROR					-1
#define USBTRANSFERERROR				-2
#define INPUTNULL						-3
#define COMMERROR						-4
#define INPUTNOTALLOC					-5
#define EEPROMOUTBOUNDS					-6
#define INVALIDARGUMENT					-7
#define INPUTOUTOFRANGE					-8
#define NOREFWHENLOCK					-9
#define NORESOURCEFOUND					-10
#define INVALIDCOMMAND 					-11

// Define device registers
#  define INITIALIZE						0x01    // Initialize the devices
#  define SET_SYSTEM_ACTIVE					0x02    // Set the System Active light
// 
#  define RF_FREQUENCY						0x10	// set the frequency
#  define RF_POWER							0x11	// Set Power 
#  define RF_OUT_ENABLE						0x12	// Enable RF output
#  define AUTO_POWER_DISABLE				0x13	// Disable the auto power correction on freq changes
#  define RF_ALC_MODE						0x14	// selects the close (0) or open (1) ALC modes
#  define DEVICE_STANDBY					0x15	// Places the channel in standby mode and powering down the analog circuits
#  define REFERENCE_MODE					0x16    // Reference Settings
#  define GET_TEMPERATURE					0x17    // load sensor temperature into the SPI output buffer
#  define GET_DEVICE_STATUS					0x18    // load the board status into the SPI output buffer
#  define USER_EEPROM_READ					0x1A    // transfer user EEPROM data to SPI output buffer
#  define USER_EEPROM_WRITE					0x1B    // calibration EEPROM write
#  define USER_EEPROM_READ64				0x1C	// transfer cal EEPROM data to USB in 64 byte chucks
#  define REFERENCE_DAC_SETTING				0x1D    // set reference DAC
#  define RF_PHASE_ADJUST					0x1F    // phase adjustment 
#  define CAL_EEPROM_READ					0x21	// reads a byte from the user EEPROM
#  define CAL_EEPROM_READ64					0x22	// reads 64 bytes from the user EEPROM
#  define STORE_STARTUP_STATE				0x23	// store the new default state
#  define SET_ALC_DAC_VALUE					0x24	// set the rf acl dac value
#  define GET_ALC_DAC_VALUE					0x39	// read back the rf alc dac value

#ifdef __cplusplus
extern "C"
{
#endif

#ifdef _LINUX 
	#define EXPORT_DLL 
#else
	#ifdef SC5506A_EXPORT  // Preprocessor
		#define EXPORT_DLL	__declspec(dllexport)
	#else
		#define EXPORT_DLL	__declspec(dllimport)
	#endif
#endif

#ifndef bool
	#define bool unsigned char
#endif

// Define types used


typedef	struct
{
	libusb_device_handle *handle;
	libusb_context *ctx;  //need to carry the session context for libusb_exit
} deviceHandle;
	
typedef struct deviceInfo_t
{
	unsigned int productSerialNumber;
	unsigned int rfModuleSerialNumber;
	float firmwareRevision;
	float hardwareRevision;
	unsigned int calDate; // year,month,day,hour 
	unsigned int manDate; // year,month,day,hour
} 	deviceInfo_t;

typedef struct deviceStatus_t
{
	bool ch1AlcOpen;
	bool ch2AlcOpen;
	bool ch1RfOutEnable;
	bool ch2RfOutEnable;
	bool ch1StandbyEnable;					
	bool ch2StandbyEnable;
	bool ch1SumPllStatus;
	bool ch1CrsPllStatus;
	bool ch1FinePllStatus;
	bool ch2SumPllStatus;
	bool ch2CrsPllStatus;
	bool ch2FinePllStatus;
	bool vcxoPllStatus;
	bool tcxoPllStatus;
	bool extRefDetected;
	bool extRefLockEnable;
	bool refClkOutEnable;
	bool deviceAccess;
}	deviceStatus_t;


/* Export Function Prototypes */
/* sc5506a.c */

/* USB specific related functions */	

/*	Raw transferFunction not made public in documentation but useful to 
*	access factory only registers
*/
EXPORT_DLL int UsbTransfer(deviceHandle *devHandle, int size,
							unsigned char *bufferOut, 
							unsigned char *bufferIn);

/*	Function to find the serial numbers of all SignalCore device with the same product ID
	return:		The number of product devices found 
	output:		2-D array (or pointers) to pass out the list serial numbers for devices found
	Example, calling function could declare:
		char **serialNumberList;
		serialNumberList = (char**)malloc(sizeof(char*)*50); // 50 serial numbers
		for (i=0;i<50; i++)
			searchNumberList[i] = (char*)malloc(sizeof(char)*SCI_SN_LENGTH); 
	and pass searchNumberList into the function.
*/
EXPORT_DLL int sc5506a_SearchDevices(char **serialNumberList);

/* Function aimed to handle LabVIEW calls. As labView is not able to handle **pointers
*	*pointer to maximum of 20 devices are passed back
*/
EXPORT_DLL int sc5506a_SearchDevicesLV(char *serialNumberList);

/*	Function opens the target USB device.
	return:		pointer to usb_dev_handle type
	input: 		devSerialNum is the product serial number. Product number is available on
				the product label.
*/
EXPORT_DLL deviceHandle *sc5506a_OpenDevice(char *devSerialNum);

/*	Function opens the target USB device aimed to handle LabVIEW calls.
	return:		pointer to usb_dev_handle type
	input: 		devSerialNum is the product serial number. Product number is available on
				the product label.
*/
EXPORT_DLL deviceHandle *sc5506a_OpenDeviceLV(char *devSerialNum);

/*	Function  closes USB device associated with the handle.
	return:		error code
	input: 		usb device handle
*/
EXPORT_DLL int sc5506a_CloseDevice(deviceHandle *devHandle);
	

/* 	Register level access function prototypes 
	=========================================================================================
*/

/* 	Writing the register with via the USB device handle allocated by sc5506a_OpenDevice
	return: error code
	input: commandByte contains the target register address, eg 0x10 is the frequency register
	input: 64 bit instructWord contains necessary data for the specified register address
*/
EXPORT_DLL int sc5506a_RegWrite(deviceHandle *devHandle, 
							unsigned char commandByte, 
							unsigned long long int instructWord); 

/* 	Reading the register with via the USB device handle allocated by sc5506a_OpenDevice
	input: commandByte contains the target register address, eg 0x10 is the frequency register
	input: 64 bit instructWord contains necessary data for the specified register address
	output: 32 bit receivedWord is the return data request through the commandByte and instructWord
*/							
EXPORT_DLL int sc5506a_RegRead(deviceHandle *devHandle, 
							unsigned char commandByte, 
							unsigned long long int instructWord,
							unsigned int *receivedWord);
							
/* 	Product configuration wrapper function prototypes 
	=========================================================================================
*/
/*	Initializes the device
	return: error code
	input: 		Mode	0: 	The device initializes to the power up state
						1:	The device reprograms all internal components to the current device 
							state
*/							
EXPORT_DLL int sc5506a_InitDevice(deviceHandle *devHandle, bool mode);

/*	Puts the device in power standby mode.
	return: error code
	input: standbyStatus	0:	Take device out off power standby. If the device was in standby,
								the device will be reprogrammed to the previous state. The device
								channel needs about a second to stabilize.
							1:	The device channel is taken into standby. All power to the channel 
								components are turned off. Conserves power consumption when not in use
*/
EXPORT_DLL int sc5506a_SetDeviceStandby(deviceHandle *devHandle, unsigned char channel, bool standbyStatus);

/*	Sets the device frequency
	return: error code
	input:	frequency in Hz up to 3,900,000,000 Hz
*/
EXPORT_DLL int sc5506a_SetFrequency(deviceHandle *devHandle, unsigned char channel, unsigned long long int frequency);

/*	Sets the device power level
	return: error code
	input:	channel			1, 2 
	input:	power			in dB
*/
EXPORT_DLL int sc5506a_SetPowerLevel(deviceHandle *devHandle, unsigned char channel, float powerLevel);

/*	Enable Power output.
	return: error code
	input:	channel			1, 2 
	input:	mode		Enables/disable the RF output. All attenuators are set to max attenuation
							and power is dialed down to a minimum level.
*/
EXPORT_DLL int sc5506a_SetRfOutput(deviceHandle *devHandle, unsigned char channel, bool mode);

/*	Enables/disable the output rf 
	return: error code
	input:	channel			1, 2 
	input:	enableRf		high disables Alc for the channel, and power level is performed open loop. 
							The amplitude accuracy may suffer slightly however disabling it could reduce
							amplitude settle times, and may improve sideband AM noise due to the loop.
*/
EXPORT_DLL int sc5506a_SetAlcMode(deviceHandle *devHandle, unsigned char channel, bool mode);

/*	Disables auto power level adjustment
	return: error code
	input:	channel			1, 2 
	input:	mode			mode = 1 disables auto adjustment of the power level when frequency 
							is 	changed. This may be an option for the user to set the frequency and power as 
								a pair in some applications. 
*/
EXPORT_DLL int sc5506a_DisableAutoLevel(deviceHandle *devHandle, unsigned char channel, bool mode);

/*	Set the reference clock configurations
	return:	error code
	input:	lockExtEnable	enables the device to lock to an external source. If the source
							not available error code returns. The device will not attempt
							to lock and waits for source.
	input:	RefOutEnable	enable the device to send out its reference clock
*/
EXPORT_DLL int sc5506a_SetClockReference(deviceHandle *devHandle, 
								bool lockExtEnable, 
								bool RefOutEnable);

/*	Sets the value of the Clock reference DAC and hence adjusts reference clock frequency
	return: error code
	input: 	dacValue	a 14 bit word
*/
EXPORT_DLL int sc5506a_SetReferenceDac(deviceHandle *devHandle, unsigned int dacValue);

/*	Inverts the IF spectrum polarity with respect to the input
	return: error code
	input: 	memAdd		the address of the EEPROM memory to write to
	input:	byteData	the byte data to write to the specified memory address 
*/
EXPORT_DLL int sc5506a_WriteUserEeprom(deviceHandle *devHandle, 
										unsigned int memAdd, 
										unsigned char byteData);

/*	Store the current state of the signal source into EEPROM as the default startup state
	return: error code
	input: 	channel
*/										
EXPORT_DLL int sc5506a_StoreCurrentState(deviceHandle *devHandle, unsigned char channel);

/*  Set the ALC DAC value of the channel
	return: error code
	input: dacValue (14 bits)
*/
EXPORT_DLL int sc5506a_SetAlcDac(deviceHandle *devHandle, unsigned char channel, unsigned int dacValue);

/*	Set the phase of the rf signal
	return: error code
	input: 	phase  	in degrees rotates the phase of the signal in degrees 
*/										
EXPORT_DLL int sc5506a_SetSignalPhase(deviceHandle *devHandle, unsigned char channel, float phase);	

/* Product Export Query (Read) function prototypes */
/*----------------------------------------------------------------------------------------------- */

/*	Function retrives the device status - PLL locks status, ref clk config, etc see deviceStatus_t type
	return:	error code
	output:	device status
*/
EXPORT_DLL int sc5506a_GetDeviceStatus(deviceHandle *devHandle, deviceStatus_t *deviceStatus);

/*	Function retrives the device temperature in degrees Celsius
	return:	error code
	output:	device temperature
*/
EXPORT_DLL int sc5506a_GetTemperature (deviceHandle *devHandle, float *temperature);

/*	Function retrives the current ALC DAC value of the channel
	return:	error code
	output:	ACL DAC Value
*/
EXPORT_DLL int	sc5506a_GetAlcDac(deviceHandle *devHandle, unsigned char channel, unsigned int *dacValue);

/*	Function retrives a single byte from Cal-EEPROM address
	return:	error code
	input:	input memAdd	memory address
	output:	byteData		1 byte data
*/
EXPORT_DLL int sc5506a_ReadCalEeprom(deviceHandle *devHandle, 
									unsigned int memAdd, 
									unsigned char *byteData);

/*	Function retrives a single byte from User-EEPROM address
	return:	error code
	input:	input memAdd	memory address
	output:	byteData		1 byte data
*/
EXPORT_DLL int sc5506a_ReadUserEeprom(deviceHandle *devHandle, 
								unsigned int memAdd, 
								unsigned char *byteData);						

/*	Function retrives a bulk of 64 bytes from Cal EEPROM start address
	return:	error code
	input:	input memAdd	start memory address
	output:	byteDataArray		64 byte data array
*/
EXPORT_DLL int sc5506a_ReadCalEepromBulk(deviceHandle *devHandle,
								unsigned int startMemAdd,
								unsigned char *byteDataArray);

/*	Function retrives a bulk of 64 bytes from user EEPROM start address
	return:	error code
	input:	input memAdd	start memory address
	output:	byteDataArray		64 byte data array
*/
EXPORT_DLL int sc5506a_ReadUserEepromBulk(deviceHandle *devHandle,
								unsigned int startMemAdd,
								unsigned char *byteDataArray);

/*	Function fetches the device Info
	return:	error code
	output:	deviceInfo		device information structure
*/
EXPORT_DLL int sc5506a_GetDeviceInfo(deviceHandle *devHandle,
											deviceInfo_t *deviceInfo);		
											
# 	ifdef __cplusplus
}
#	endif

#	endif  /* __SC5506A__H__ */	