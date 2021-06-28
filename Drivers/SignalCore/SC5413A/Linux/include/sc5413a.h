/*
 ***************************************************************************
 * USB functions for SignalCore Inc SC5413A products using "libusb"
 * functions and driver
 *
 * "libusb" license is covered by the LGPL 
 *	
 *	Copyright (c) 2013 SignalCore Inc.
 *	
 ****************************************************************************
 * SC5413A header file 
*/

#ifndef __SC5413A_H__
#define __SC5413A_H__

#include <libusb.h>

//  Define USB SignalCore ID

#define SCI_USB_VID					0x277C  // SignalCore USB Vendor ID 
#define	SCI_USB_PID					0x0017  // Product ID SC5413A
#define SCI_SN_LENGTH				0x08
#define SCI_PRODUCT_NAME			"SC5413A"

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

// Define labels
#  define CH_I							0x00
#  define CH_Q							0x01
#  define RF_ATTEN1						0x00	
#  define RF_ATTEN2						0x01
#  define RF_ATTEN3						0x02
#  define RF_ATTEN3						0x02



// EEPROM SIZE
#define CALEEPROMSIZE					32768  // bytes 
#define USEREEPROMSIZE					32768  // bytes


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
#  define INITIALIZE					0x01    // Initialize the devices
#  define SET_SYSTEM_ACTIVE				0x02    // Set the System Active light
// 
#  define RF_FREQUENCY					0x10	// Using Frequency to set up the the LO and RF filters automatically
#  define RF_GAIN						0x11	// Set Gain (Not Implemented)
#  define RF_AMPLIFIER					0x12	// Selects the RF amplifiers (2) to enable/disable
#  define RF_ATTENUATION				0x13	// Set the RF attenuation for the 3 DSA
#  define RF_PATH						0x14	// Select the main (0) or auxillary (1) rf input path
#  define RF_FILTER_SELECT				0x15    // Allows the user to manually select the RF filter in the RF filter bank
#  define LO_FILTER_SELECT				0x16	// Allows the user to manually select the LO filter
#  define LO_OUT_ENABLE					0x17	// Enable LO output)
#  define DC_OFFSET_DAC					0x1A	// Sets the DC offset on each of the differential I and Q channels (0 to 0xFFF)
#  define LINEARITY_DAC					0x1B	// Sets the Linearity DAC (0to0xFFF)  
#  define STORE_STARTUP_STATE			0x1D    // Store the current state as default
#  define USER_EEPROM_WRITE				0x1F    // calibration EEPROM write 

#  define GET_DEVICE_STATUS				0x20    // Get Device Status
#  define GET_TEMPERATURE				0x21    // Get Temperature
#  define USER_EEPROM_READ				0x23    // Read user EEPROM byte
#  define CAL_EEPROM_READ				0x24	// Read Cal EEPROM byte

#ifdef __cplusplus
extern "C"
{
#endif

#ifdef _LINUX 
	#define EXPORT_DLL 
#else
	#ifdef SC5413A_EXPORT  // Preprocessor
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
		libusb_device_handle	*handle;
		libusb_context *ctx;
} deviceHandle;
	
typedef struct 
{
	unsigned int productSerialNumber;
	unsigned int rfModuleSerialNumber;
	float firmwareRevision;
	float hardwareRevision;
	unsigned int calDate; // year,month,day,hour 
	unsigned int manDate; // year,month,day,hour
} 	deviceInfo_t;

typedef struct 
{
	bool rfAmpEnable;
	bool rfPath;
	bool loEnable;
	bool deviceAccess;
}	deviceStatus_t;


/* Export Function Prototypes */
/* sc5413a.c */

/* UsbTransfer is provided as a generic transfer function for transfer format register level
*  data. 
*/
EXPORT_DLL int UsbTransfer(deviceHandle *devHandle, int size,
							unsigned char *bufferOut, 
							unsigned char *bufferIn);

/* USB specific related functions */	

/*	Function to find the serial numbers of all SignalCore device with the same product ID
*	return:		The number of product devices found 
*	output:		2-D array (or pointers) to pass out the list serial numbers for devices found
*	Example, calling function could declare:
*		char **serialNumberList;
*		serialNumberList = (char**)malloc(sizeof(char*)*50); // 50 serial numbers
*		for (i=0;i<50; i++)
*			searchNumberList[i] = (char*)malloc(sizeof(char)*SCI_SN_LENGTH); 
*	and pass searchNumberList into the function.
*/
EXPORT_DLL int sc5413a_SearchDevices(char **serialNumberList);

/*	Function to handle LabView call to search devices
*/
EXPORT_DLL int sc5413a_SearchDevicesLV(char *serialNumberList);

/*	Function opens the target USB device.
	return:		pointer to usb_dev_handle type
	input: 		devSerialNum is the product serial number. Product number is available on
				the product label.
*/
EXPORT_DLL deviceHandle *sc5413a_OpenDevice(char *devSerialNum);

/*	Function to handle LabView call to open device
*/
EXPORT_DLL deviceHandle *sc5413a_OpenDeviceLV(char *devSerialNum);

/*	Function  closes USB device associated with the handle.
	return:		error code
	input: 		usb device handle
*/
EXPORT_DLL int sc5413a_CloseDevice(deviceHandle *devHandle);

/* 	Register level access function prototypes 
	=========================================================================================
*/

/* 	Writing the register with via the USB device handle allocated by sc5413a_OpenDevice
	return: error code
	input: commandByte contains the target register address, eg 0x10 is the frequency register
	input: 64 bit instructWord contains necessary data for the specified register address
*/
EXPORT_DLL int sc5413a_RegWrite(deviceHandle *devHandle, 
							unsigned char commandByte, 
							unsigned long long int instructWord); 

/* 	Reading the register with via the USB device handle allocated by sc5413a_OpenDevice
	input: commandByte contains the target register address, eg 0x10 is the frequency register
	input: 64 bit instructWord contains necessary data for the specified register address
	output: 32 bit receivedWord is the return data request through the commandByte and instructWord
*/							
EXPORT_DLL int sc5413a_RegRead(deviceHandle *devHandle, 
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
EXPORT_DLL int sc5413a_InitDevice(deviceHandle *devHandle, bool Mode);

/*	Sets the device frequency
	return: error code
	input:	frequency in Hz up to 3,900,000,000 Hz
*/
EXPORT_DLL int sc5413a_SetFrequency(deviceHandle *devHandle, unsigned long long int frequency);

/*	Sets the device gain
	return: error code
	input:	gain	in dB
*/
EXPORT_DLL int sc5413a_SetRfGain(deviceHandle *devHandle, float rfGain);

/*	Enable Amplifier.
	return: error code
	input:	mode		Enables/disable the Amplifier
*/
EXPORT_DLL int sc5413a_SetRfAmplifier(deviceHandle *devHandle, bool mode);

/*	Set the input RF path
	return: error code
	input:	path	0 Selects the main path, 1 selects the auxillary path. The auxillary path
			is ususally select as a calibration path without breaking the DUT which is usually
			attached to the main path.
*/
EXPORT_DLL int sc5413a_SetRfPath(deviceHandle *devHandle, bool path);

/*	Enables/disables the LO output
	return:	error code
	input:	mode.	0 disables the LO output, 1 Enables it for common LO drive in phase coherent
					application where more than one demodulator/modulator is used.
*/
EXPORT_DLL int sc5413a_SetLoOut(deviceHandle *devHandle, bool mode);

/*	Sets the Attenuation
	return: error code
	input:	attenuator			1,2,3,4 
	input:	atten				the level of attenuation (0-30, 1 dB step)
*/
EXPORT_DLL int sc5413a_SetRfAttenuation(deviceHandle *devHandle, unsigned char attenuator, unsigned char atten);

/*	Select the RF filter from the RF filter bank
	return: error code
	input:	filter			0-8, 9 filters in all
*/
EXPORT_DLL int sc5413a_SetRfFilter(deviceHandle *devHandle, unsigned char filter);

/*	Select the LO filter from the LO filter bank
	return: error code
	input:	filter			0-8, 9 filters in all
*/
EXPORT_DLL int sc5413a_SetLoFilter(deviceHandle *devHandle, unsigned char filter);

/*	Set the DC offset of the differential output  
	return:		error code
	input:		channel		I or Q
	input:		dacValue	Varies the output voltage from -0.24V to +0.24V (0-4095), the limits depend
							on the value of Vcom Out.
*/
EXPORT_DLL int sc5413a_SetDcOffsetDac(deviceHandle *devHandle, unsigned char channel, unsigned short dacValue);

/*	Set the linearity of the IQ demodulator.
	return:		error code
	input:		channel		I or Q
	input:		dacValue.		This DAC controls the linearity of the device. This Voltage is typically set 
				to 0.6V. V_linearity = (dacValue/4095)*5V.
*/
EXPORT_DLL int sc5413a_SetLinearityDac(deviceHandle *devHandle, unsigned char channel, unsigned short dacValue);


/*	Write User EEPROM
	return: error code
	input: 	memAdd		the address of the EEPROM memory to write to
	input:	byteData	the byte data to write to the specified memory address 
*/
EXPORT_DLL int sc5413a_WriteUserEeprom(deviceHandle *devHandle, 
										unsigned int memAdd, 
										unsigned char byteData);

/*	Store the current state of the signal source into EEPROM as the default startup state
	return: error code
	input: 	channel
*/										
EXPORT_DLL int sc5413a_StoreCurrentState(deviceHandle *devHandle);

/* Product Export Query (Read) function prototypes */
/*----------------------------------------------------------------------------------------------- */

/*	Function retrives the device attributes such as product serial, calibration dates, firmware revisions
	return: error code
	output: device attributes
*/
EXPORT_DLL int	sc5413a_GetDeviceInfo(deviceHandle *devHandle, deviceInfo_t *devInfo);

/*	Function retrives the device status - PLL locks status, ref clk config, etc see deviceStatus_t type
	return:	error code
	output:	device status
*/
EXPORT_DLL int sc5413a_GetDeviceStatus(deviceHandle *devHandle, deviceStatus_t *deviceStatus);

/*	Function retrives the device temperature in degrees Celsius
	return:	error code
	output:	device temperature
*/
EXPORT_DLL int sc5413a_GetTemperature (deviceHandle *devHandle, float *temperature);

/*	Function retrives a single byte from Cal-EEPROM address
	return:	error code
	input:	input memAdd	memory address
	output:	byteData		1 byte data
*/
EXPORT_DLL int sc5413a_ReadCalEeprom(deviceHandle *devHandle, 
									unsigned int memAdd, 
									unsigned char *byteData);

/*	Function retrives a single byte from User-EEPROM address
	return:	error code
	input:	input memAdd	memory address
	output:	byteData		1 byte data
*/
EXPORT_DLL int sc5413a_ReadUserEeprom(deviceHandle *devHandle, 
								unsigned int memAdd, 
								unsigned char *byteData);						
											
# 	ifdef __cplusplus
}
#	endif

#	endif  /* __SC5413A__H__ */	