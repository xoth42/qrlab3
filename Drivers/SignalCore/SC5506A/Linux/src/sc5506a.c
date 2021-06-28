/*
 * USB functions for SignalCore Inc SC5506A products using "libusbx"
 * functions and driver
 *
 * "libusbx" license is covered by the LGPL 
 *	
 *	Copyright (c) 2013 - 2014  SignalCore Inc.
 *	
 *
 * Rev 1.1 Corrected for sc5506a_GetDeviceStatus function for deviceStatus->ch2AlcOpen
 *
*/
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include "sc5506a.h"

/* Local constants */
#	define TRANSFER_BYTES			0x08 // number of transfer bytes to registers
#	define	TIMEOUT					5000  // Define the time out for USB transfers


/* Local functions prototypes */

/*  LoopBackControl performs a write and then readback using Control endpoint 
	bufferOut is the array of characters written
	bufferIn is the array of characters received
*/
 int UsbTransferControl(deviceHandle *devHandle, int size,
							unsigned char *bufferOut, 
							unsigned char *bufferIn);
							
/*  UsbTransferInterrupt performs a write and then readback using Interrupt endpoint
	bufferOut is the array of characters written
	bufferIn is the array of characters received
*/							
 int UsbTransferInterrupt(deviceHandle *devHandle, int size,
							unsigned char *bufferOut, 
							unsigned char *bufferIn);

/*  UsbTransferBulk performs a write and then read-back using Bulk endpoint 
	bufferOut is the array of characters written
	bufferIn is the array of characters received
*/							
 int UsbTransferBulk(deviceHandle *devHandle, int size,
							unsigned char *bufferOut, 
							unsigned char *bufferIn);

/* 	Reads a float number stored at the starting memory Address of the calibration EEPROM
	return:		error code
	input: 		The starting memory address of the 4 bytes where the float is stored
	output:		value - the request float number
*/
float UsbReadCalF32 (deviceHandle *devHandle, 
					unsigned int startMemAdd);

/* 	Reads an unsigned 32bit number stored at the starting memory Address of the calibration EEPROM
	return:		The requested unsigned int number
	input: 		startMemAdd - The starting memory address of the 4 bytes where the unsigned number is stored
	output:		value - the request unsigned value
*/
unsigned int UsbReadCalU32(deviceHandle *devHandle, 
							unsigned int startMemAdd);

/* 	Reads a 1-D array of floats stored at the starting memory Address of the calibration EEPROM
	return:		error code
	input: 		startMemAdd - The starting memory address of the 4 bytes where the unsigned number is stored
	input:		len - length of the 1-D array
	output:		*array - 1D array to return the value. array must be allocated with sufficient space
*/
 int	UsbReadCalArrayF32(deviceHandle *devHandle, 
							unsigned int startMemAdd, 
							unsigned int len, 
							float *array);	
							
/* 	Reads a 2-D array of floats stored at the starting memory Address of the calibration EEPROM
	return:		error code
	input: 		startMemAdd - The starting memory address of the 4 bytes where the unsigned number is stored
	input:		len - length of the 1-D array
	output:		**array - 2D array to return the value. array must be allocated with sufficient space
*/						
 int	UsbReadCal2DArrayF32(deviceHandle *devHandle, 
							unsigned int startMemAdd,
							unsigned int rows, 
							unsigned int cols,  
							float **array);

/*	Local Math function prototypes */

// int spline( double *xArray, double *yArray, int  nPoints, double  firstBoundary , double  secondBoundary , double *yInterpolant);

// int splineInterp(double *xArray, double *yArray, double *yInterpolant, double nPoints, double x, double *interpolatedYValue);

double 	round(double number)
{
		return floor(number + .5);
}


//==============================================================================
// Local function implementations

/* 	Begin Implementation of local functions USB functions*/							
 int UsbTransferControl(deviceHandle *devHandle, int size,
							unsigned char *bufferOut, 
							unsigned char *bufferIn)
{
	if (0 >  libusb_control_transfer(
			devHandle->handle,
			USB_TYPE_VENDOR | USB_RECIP_INTERFACE , // bRequestType
			0, // bRequestm
			0, // wValue
			0, // wIndex
			bufferOut, // pointer to destination buffer
			size, // wLength
			(unsigned int)TIMEOUT // timeout ms
			)) 
		{
			return -2;
		}
	if (0 >  libusb_control_transfer(
			devHandle->handle,
			USB_TYPE_VENDOR | USB_RECIP_INTERFACE | USB_ENDPOINT_IN, // bRequestType
			0, // bRequest
			0, // wValue
			0, // wIndex
			bufferIn, // pointer to destination buffer
			size, // wLength
			(unsigned int) TIMEOUT // timeout ms
			)) 
		{
			return -2;
		}
	return SUCCESS;
}

 int UsbTransferInterrupt(deviceHandle *devHandle, int size, 
							unsigned char *bufferOut, 
							unsigned char *bufferIn)
{
	int transferred = 0;
	if (0> libusb_interrupt_transfer(devHandle->handle, SCI_ENDPOINT_OUT_INT, bufferOut, size, &transferred, TIMEOUT)) 
		{
			return -2;
		}
	if (0> libusb_interrupt_transfer(devHandle->handle, SCI_ENDPOINT_IN_INT, bufferIn, size, &transferred, TIMEOUT))
		{
			return -2;
		}
}


 int UsbTransferBulk(deviceHandle *devHandle, int size, 
							unsigned char *bufferOut, 
							unsigned char *bufferIn)
{
	int transferred = 0;
	if (0 > libusb_bulk_transfer(devHandle->handle, SCI_ENDPOINT_OUT_BULK, bufferOut, size, &transferred, TIMEOUT)) 
		{
			return -2;
		}
	if (0 > libusb_bulk_transfer(devHandle->handle, SCI_ENDPOINT_IN_BULK, bufferIn, size, &transferred, TIMEOUT))
		{
			return -2;
		}
	return SUCCESS;
}

/* Begin Implemenation of local functions */
/* *********************************************************************************** */

float	UsbReadCalF32 (deviceHandle *devHandle, unsigned int startAddress) //might have to change to remove eeprom 1 and 0
{

	unsigned int eeRead = 0;
	unsigned int tempValue = 0;
	int byteCounter = 0;
	int status; 
	
	while (byteCounter < 4){
		status = sc5506a_RegRead(devHandle,CAL_EEPROM_READ,(unsigned long long int)startAddress,&eeRead);
		if (status != SUCCESS)
		{
			return -1;
		}
		tempValue = tempValue | ((eeRead & 0xFF) << (byteCounter*8));
		byteCounter++;
		startAddress++;
	}
	
	return *((float *)&tempValue);
}

 unsigned int UsbReadCalU32 (deviceHandle *devHandle, unsigned int startAddress)  //might have to change to remove eeprom 1 and 0
{

	unsigned int eeRead = 0;
	unsigned int tempValue = 0;
	int byteCounter = 0;
	int status; 
	
	while (byteCounter < 4){
		status = sc5506a_RegRead(devHandle,CAL_EEPROM_READ,startAddress,&eeRead);
		if (status != SUCCESS)
		{
			return -1;
		}
		tempValue = tempValue | ((eeRead & 0xFF) << (byteCounter*8));
		byteCounter++;
		startAddress++;
	}
	
	return tempValue;
}

/* 	Begin Impementation of export functions 
	****************************************************************************************************************
	
	Begin USB device session related functions
	=================================================================================================================
*/
 
int UsbTransfer(deviceHandle *devHandle, int size,
							unsigned char *bufferOut, 
							unsigned char *bufferIn)
{
	int transferred = 0;
	if (0 > libusb_bulk_transfer(devHandle->handle, SCI_ENDPOINT_OUT_BULK, bufferOut, size, &transferred, TIMEOUT)) 
		{
			return -2;
		}
	if (0 > libusb_bulk_transfer(devHandle->handle, SCI_ENDPOINT_IN_BULK, bufferIn, size, &transferred, TIMEOUT))
		{
			return -2;
		}
	return SUCCESS;
}

int sc5506a_SearchDevices(char **serialNumberList)
{
	libusb_device_handle *devHandle = NULL; 
	int deviceCount = 0;
	unsigned char string_usb[9];
	libusb_device *device = NULL;
	libusb_context *ctx = NULL;
	libusb_device **devList;
		struct libusb_device_descriptor desc;	
	int r, i;
	int status = 0;
	ssize_t count;

	r = libusb_init(&ctx);
	if (r < 0) return USBDEVICEERROR;

	count = libusb_get_device_list(ctx, &devList);
	if (count < 0) 
	{
		libusb_free_device_list(devList, 1);
		return USBDEVICEERROR;
	}
	for (i = 0; i < count; i++) 
	{
		device = devList[i];
		r = libusb_get_device_descriptor(device, &desc);
		if(desc.idVendor == SCI_USB_VID && desc.idProduct == SCI_USB_PID)
			{	
				status = libusb_open(device, &devHandle);
				if (status == 0)
				{	
					libusb_get_string_descriptor_ascii(devHandle, desc.iSerialNumber, string_usb, sizeof(string_usb));
					strncpy(serialNumberList[deviceCount], (const char*)string_usb, SCI_SN_LENGTH+1);
					libusb_close(devHandle);
					deviceCount++;
				}
			}
    }
	libusb_free_device_list(devList, 1);
	libusb_exit(ctx);
	return deviceCount;
}

	
int sc5506a_SearchDevicesLV(char *serialNumberList)
{
	libusb_device_handle *devHandle = NULL; 
	int deviceCount = 0;
	unsigned char string_usb[9];
	char *list;
	libusb_device **devList;
	libusb_context *ctx = NULL;
	struct libusb_device_descriptor desc;	
	int r, i;
	int status = 0;
	ssize_t count;

	list = (char*)malloc(160);
	if (list == NULL) return 0;
	list[0] = '\0';
	r = libusb_init(&ctx);
	if (r < 0) return USBDEVICEERROR;

	count = libusb_get_device_list(ctx, &devList);
	if (count < 0) 
		{
			libusb_free_device_list(devList, 1);
			return USBDEVICEERROR;
		}
	for (i = 0; i < count; i++) 
	{
		status = libusb_get_device_descriptor(devList[i], &desc);
		if(desc.idVendor == SCI_USB_VID && desc.idProduct == SCI_USB_PID)
			{	
				status = libusb_open(devList[i], &devHandle);
				if (status == 0)
				{	
					libusb_get_string_descriptor_ascii(devHandle, desc.iSerialNumber, string_usb, sizeof(string_usb));
					strncat(list, (char *)string_usb, SCI_SN_LENGTH+1);
					libusb_close(devHandle);
					deviceCount++;
				}
			}
    }
	strcpy(serialNumberList,list);
	libusb_free_device_list(devList, 1);
	libusb_exit(ctx);
	free(list);
	return deviceCount;
}

deviceHandle *sc5506a_OpenDeviceLV(char *devSerialNum)
{
	deviceHandle *devHandle;
	unsigned char string_usb[9];
	libusb_device *device;
	libusb_device **devList;
	struct libusb_device_descriptor desc;
	libusb_device_handle *tmpHandle;

	int i,r;
	ssize_t count;
	int status;

	devHandle = (deviceHandle*) malloc(sizeof(deviceHandle));

	r = 0;
	status = libusb_init(&(devHandle->ctx));
	count = libusb_get_device_list(devHandle->ctx, &devList);
	for (i = 0; i < count; i++) 
	{		
		status = libusb_get_device_descriptor(devList[i], &desc);
		if(desc.idVendor == SCI_USB_VID && desc.idProduct == SCI_USB_PID)
			{	
				status = libusb_open(devList[i], &tmpHandle);
				if (status == 0)
				{
					libusb_get_string_descriptor_ascii(tmpHandle, desc.iSerialNumber, string_usb, sizeof(string_usb));
					if (strncmp( string_usb, devSerialNum, SCI_SN_LENGTH) == 0)  
						{	
							device = devList[i];
							r = 1;
						}
					libusb_close(tmpHandle);
				}
			}
    }
	
	if (r)
	{
		if (libusb_open(device, &devHandle->handle) == 0)
			status = libusb_reset_device(devHandle->handle);
		libusb_set_configuration(devHandle->handle, 1);
		if (!libusb_claim_interface(devHandle->handle, 0)) libusb_set_interface_alt_setting(devHandle->handle, 0, 1);
		sc5506a_RegWrite(devHandle, SET_SYSTEM_ACTIVE, 0x01);
		libusb_free_device_list(devList, 1);
		return devHandle;
	}
	else
	{
		libusb_exit(devHandle->ctx);
		free(devHandle);
		return 0;
	}
}

deviceHandle *sc5506a_OpenDevice(char *devSerialNum)
{
	deviceHandle *devHandle;
	unsigned char string_usb[9];
	libusb_device *device;
	libusb_device **devList;
	struct libusb_device_descriptor desc;
	libusb_device_handle *tmpHandle;

	int i,r;
	ssize_t count;
	int status;

	devHandle = (deviceHandle*) malloc(sizeof(deviceHandle));

	r = 0;
	status = libusb_init(&(devHandle->ctx));
	count = libusb_get_device_list(devHandle->ctx, &devList);
	for (i = 0; i < count; i++) 
	{		
		status = libusb_get_device_descriptor(devList[i], &desc);
		if(desc.idVendor == SCI_USB_VID && desc.idProduct == SCI_USB_PID)
			{	
				status = libusb_open(devList[i], &tmpHandle);
				if (status == 0)
				{
					libusb_get_string_descriptor_ascii(tmpHandle, desc.iSerialNumber, string_usb, sizeof(string_usb));
					if (strncmp( string_usb, devSerialNum, SCI_SN_LENGTH) == 0)  
						{	
							device = devList[i];
							r = 1;
						}
					libusb_close(tmpHandle);
				}
			}
    }
	
	if (r)
	{
		if (libusb_open(device, &devHandle->handle) == 0)
			status = libusb_reset_device(devHandle->handle);
		libusb_set_configuration(devHandle->handle, 1);
		if (!libusb_claim_interface(devHandle->handle, 0)) libusb_set_interface_alt_setting(devHandle->handle, 0, 1);
		sc5506a_RegWrite(devHandle, SET_SYSTEM_ACTIVE, 0x01);
		libusb_free_device_list(devList, 1);
	}
	else
	{
		libusb_exit(devHandle->ctx);
		devHandle->handle = NULL;
		devHandle->ctx = NULL;
	}
	return devHandle;
}

int  sc5506a_CloseDevice(deviceHandle *devHandle)
{
	libusb_device *dev = NULL;
	dev = libusb_get_device(devHandle->handle);
	if (dev == NULL) return -1;  //invalid handle
	sc5506a_RegWrite(devHandle, SET_SYSTEM_ACTIVE, 0x00); // Turn off the device system access light
	libusb_release_interface(devHandle->handle, 0);
	libusb_close(devHandle->handle);
	libusb_exit(devHandle->ctx);
	free(devHandle);
	return SUCCESS;
}

/*
	Begin product Export wrapper functions
	=================================================================================================================
*/
/* Implementation of Register access functions */

int  sc5506a_RegWrite(deviceHandle *devHandle, 
							unsigned char commandByte, 
							unsigned long long int instructWord)
 {
	unsigned char bufferOut[TRANSFER_BYTES];
	unsigned char bufferIn[TRANSFER_BYTES]; 
	int i;
	int instructBytes = 0;
	switch(commandByte)
	{
		case INITIALIZE: //Initialize Device
			instructBytes = 1;
			break;
		case SET_SYSTEM_ACTIVE: //Set System Active LED
			instructBytes = 1; 
			break;
		case DEVICE_STANDBY: //StandBy power
			instructBytes = 1;
			break;
		case RF_FREQUENCY: //RF Frequency
			instructBytes = 6;
			break;
		case RF_POWER: //RF power level
			instructBytes = 3;
			break;
		case RF_ALC_MODE:
			instructBytes = 1;
			break;
		case REFERENCE_MODE: //Reference Clock Setting
			instructBytes = 1; 
			break;
		case REFERENCE_DAC_SETTING: //Override the internal reference DAC value
			instructBytes = 2; 
			break;
		case RF_OUT_ENABLE: //Disable RF power 
			instructBytes = 1; 
			break;
		case STORE_STARTUP_STATE://program the start up state
			instructBytes = 1;
			break;
		case USER_EEPROM_WRITE: //Write byte to the user EEPROM
			instructBytes = 3;
			break;
		case SET_ALC_DAC_VALUE:
			instructBytes = 3;
			break;
		case AUTO_POWER_DISABLE:
			instructBytes = 1;
			break;
		default:
			instructBytes = -1; 
			break;
	}

	if(!(instructBytes < 0))
	{
		bufferOut[0] = commandByte;
		i = 0;
		while(i < instructBytes)
		{
			bufferOut[i+1] = (unsigned char)((instructWord >> (8*(instructBytes-i-1))) & 0xFF);
			i++;
		}	
		
		if (0 > UsbTransferBulk(devHandle, sizeof(bufferOut), bufferOut, bufferIn)) return -2;
		
	}
	else return INVALIDCOMMAND;
	return SUCCESS;
 }

int  sc5506a_RegRead(deviceHandle *devHandle, 
							unsigned char commandByte, 
							unsigned long long int instructWord,
							unsigned int *receivedWord)
 {
	unsigned char bufferOut[TRANSFER_BYTES];
	unsigned char bufferIn[TRANSFER_BYTES];
	int i;
	int instructBytes = 0;
	int inBytes = 0;
	unsigned int tmpWord = 0;

	switch (commandByte)
	{
		case GET_TEMPERATURE: //Serial Ready
			instructBytes = 1;
			inBytes = 2;
			break;
		case GET_DEVICE_STATUS: //Fetch device status
			instructBytes = 1;
			inBytes = 3;
			break;
		case CAL_EEPROM_READ: //Fetch Temperature
			instructBytes = 2;
			inBytes = 1;
			break;
		case USER_EEPROM_READ:
			instructBytes = 2;
			inBytes = 1;
			break;
		case GET_ALC_DAC_VALUE:
			instructBytes = 1;
			inBytes = 2;
			break;
		default:
			instructBytes = -1; 
			break;
	}
	
	if(!(instructBytes < 0))
	{
		bufferOut[0] = commandByte;
		i = 0;
		while(i < instructBytes)
		{
			bufferOut[i+1] = (unsigned char)((instructWord >> (8*(instructBytes-i-1))) & 0xFF);
			i++;
		}
		if (0 > UsbTransferBulk(devHandle, sizeof(bufferOut), bufferOut, bufferIn)) return -2;
		i = 0;
		while ( i < inBytes)
		{
			tmpWord = tmpWord | (((unsigned int)bufferIn[i]) << (inBytes -i -1)*8); //MSB
			i++;
		}
		*receivedWord = tmpWord;
	}
	else 
	{
		*receivedWord = 0x00;	
		return INVALIDCOMMAND;
	}
	return SUCCESS;
 }
 

 /* Implementation of configuration (or setting ) functions */
int	sc5506a_InitDevice(deviceHandle *devHandle, bool mode)
{
	int status;
	status = sc5506a_RegWrite(devHandle,INITIALIZE,(mode & 0x01));
	if(status != SUCCESS) return status;	
	//Sleep(100); 
	return SUCCESS;	
}

int sc5506a_SetDeviceStandby(deviceHandle *devHandle, unsigned char channel, bool standbyStatus)
{
	int status;
	status = sc5506a_RegWrite(devHandle, DEVICE_STANDBY, (channel << 1) | (standbyStatus&0x01)); 
	if (status != SUCCESS) return status;
	return SUCCESS;
}

int sc5506a_SetFrequency(deviceHandle *devHandle, unsigned char channel, unsigned long long int frequency)
{
	int status;
	if (frequency > 6100000000) frequency = 6100000000;	/*limit to 6100 MHz */
	status = sc5506a_RegWrite(devHandle, RF_FREQUENCY, frequency | ((unsigned long long int)channel << 40));
	if (status != SUCCESS) return status;
	if (frequency > 6000000000) return INPUTOUTOFRANGE;	
	return SUCCESS;
}	

int sc5506a_SetPowerLevel(deviceHandle *devHandle, unsigned char channel, float powerLevel)
{
	int status;
	unsigned long long int instructWord;
	
	if (powerLevel < 0)
			instructWord = (((unsigned long long int)round(powerLevel*(-100))) & 0x7FFF) | ( (unsigned long long int)1 << 15);
	else
			instructWord = ((unsigned long long int)round(powerLevel*100)) & 0x7FFF;
		 
	status = sc5506a_RegWrite(devHandle, RF_POWER, instructWord | ((unsigned long long int)channel << 16));
	if (status != SUCCESS) return status;
	return SUCCESS;
}

int sc5506a_SetRfOutput(deviceHandle *devHandle, unsigned char channel, bool mode)
{
	int status;
	status = sc5506a_RegWrite(devHandle, RF_OUT_ENABLE, (unsigned long long int)((channel << 1) | (mode & 0x01)));
	if (status != SUCCESS) return status;
	return SUCCESS;
}

int sc5506a_SetAlcMode(deviceHandle *devHandle, unsigned char channel, bool mode)
{
	int status;
	status = sc5506a_RegWrite(devHandle, RF_ALC_MODE, (unsigned long long int)((channel << 1) | (mode&0x01)));
	if (status != SUCCESS) return status;
	return SUCCESS;
}

int sc5506a_DisableAutoLevel(deviceHandle *devHandle, unsigned char channel, bool mode)
{
	int status;
	status = sc5506a_RegWrite(devHandle, AUTO_POWER_DISABLE, (unsigned long long int)((channel << 1) | mode));
	if (status != SUCCESS) return status;
	return SUCCESS;
}

int sc5506a_SetClockReference(deviceHandle *devHandle, bool lockExtEnable, bool RefOutEnable)
{
	int status;
	status = sc5506a_RegWrite(devHandle, REFERENCE_MODE, (unsigned long long int)(( RefOutEnable << 1) | lockExtEnable));
	if (status != SUCCESS) return status;
	return SUCCESS;
}

int sc5506a_SetReferenceDac(deviceHandle *devHandle, unsigned int dacValue)
{
	int status;
	status = sc5506a_RegWrite(devHandle, REFERENCE_DAC_SETTING, (unsigned long long int)(dacValue) & 0x3FFF);
	if (status != SUCCESS) return status;
	return SUCCESS;
}

int sc5506a_StoreCurrentState(deviceHandle *devHandle, unsigned char channel)
{   
	int status;
	status = sc5506a_RegWrite(devHandle,STORE_STARTUP_STATE,channel&0x01);
	if(status != SUCCESS) return status;
	return SUCCESS;
}

int sc5506a_WriteUserEeprom(deviceHandle *devHandle, 
										unsigned int memAdd, 
										unsigned char byteData)
{
	int status; 
	unsigned long long int instructWord; 

	if (memAdd > 0x7FFF) 
		return EEPROMOUTBOUNDS;
		
	instructWord = ((memAdd & 0x7FFF) << 8) | (byteData);
	status = sc5506a_RegWrite(devHandle, USER_EEPROM_WRITE, instructWord);
	if (status != SUCCESS) return status;
	return SUCCESS;
}

int sc5506a_SetAlcDac(deviceHandle *devHandle, unsigned char channel, unsigned int dacValue)
{
	int status;
	status = sc5506a_RegWrite(devHandle,SET_ALC_DAC_VALUE, (unsigned long long int)(((channel&0x01)<<16)|(dacValue&0x3FFF)));
	if (status != SUCCESS) return status;
	return SUCCESS;
}

int sc5506a_SetSignalPhase(deviceHandle *devHandle, unsigned char channel, float phase)
{
	int status; 
	unsigned long long int phaseWord;
	phaseWord = ((unsigned long long int)abs(phase * 10)) & 0x3FFF;
	status = sc5506a_RegWrite(devHandle, RF_PHASE_ADJUST, phaseWord | ((unsigned long long int)channel << 16));
	if (status != SUCCESS) return status;
	return SUCCESS;
}


/* begin implemenation of export Read functions */

int sc5506a_GetDeviceStatus(deviceHandle *devHandle, deviceStatus_t *deviceStatus)
{
	int status;
	unsigned int receivedWord = 0;
	
	if(deviceStatus == NULL) return INPUTNOTALLOC; // if type is not allocated
	
	status = sc5506a_RegRead(devHandle, GET_DEVICE_STATUS, 0, &receivedWord);
	if (status != SUCCESS) return status;
	
	deviceStatus->ch1AlcOpen = 					(bool)((receivedWord & 0x200000) >> 21);
	deviceStatus->ch2AlcOpen = 					(bool)((receivedWord & 0x100000) >> 20);
	deviceStatus->ch1RfOutEnable = 				(bool)((receivedWord & 0x80000) >> 19);
	deviceStatus->ch2RfOutEnable = 				(bool)((receivedWord & 0x40000) >> 18);
	deviceStatus->ch1StandbyEnable = 			(bool)((receivedWord & 0x20000) >> 17);
	deviceStatus->ch2StandbyEnable = 			(bool)((receivedWord & 0x10000) >> 16);
	deviceStatus->ch1CrsPllStatus = 			(bool)((receivedWord & 0x8000) >> 15);
	deviceStatus->ch1FinePllStatus = 			(bool)((receivedWord & 0x4000) >> 14);
	deviceStatus->ch1SumPllStatus = 			(bool)((receivedWord & 0x2000) >> 13);
	deviceStatus->ch2CrsPllStatus = 			(bool)((receivedWord & 0x800) >> 11);
	deviceStatus->ch2FinePllStatus = 			(bool)((receivedWord & 0x400) >> 10);
	deviceStatus->ch2SumPllStatus = 			(bool)((receivedWord & 0x200) >> 9);
	deviceStatus->vcxoPllStatus =				(bool)((receivedWord & 0x80) >> 7);	
	deviceStatus->tcxoPllStatus =				(bool)((receivedWord & 0x40) >> 6);	
	deviceStatus->extRefDetected = 				(bool)((receivedWord & 0x20) >> 5); 
	deviceStatus->extRefLockEnable = 			(bool)((receivedWord & 0x10) >> 4);
	deviceStatus->refClkOutEnable = 			(bool)((receivedWord & 0x08) >> 3);
	deviceStatus->deviceAccess = 				(bool)((receivedWord & 0x04) >> 2);
	return SUCCESS;
}

int	sc5506a_GetTemperature (deviceHandle *devHandle, float *temperature)
{
	int status;
	int signBit = 1;
	unsigned int receivedWord = 0;

	if(temperature == NULL) return INPUTNOTALLOC;
	
	status = sc5506a_RegRead(devHandle, GET_TEMPERATURE, 0, &receivedWord);
	if(status != SUCCESS) return status;

	if (receivedWord & 0x2000) signBit = -1;
	
	*temperature = (float)(((double)(receivedWord&0x1FFF))/8191 * signBit * 256);

	return SUCCESS;	
}

int	sc5506a_GetAlcDac(deviceHandle *devHandle, unsigned char channel, unsigned int *dacValue)
{
	int status;
	unsigned int receivedWord = 0;

	status = sc5506a_RegRead(devHandle,GET_ALC_DAC_VALUE,(unsigned long long int)channel,&receivedWord);
	if(status != SUCCESS) return status;
	
	*dacValue = receivedWord & 0x3FFF;
	return SUCCESS;	
}

int	sc5506a_ReadCalEeprom(deviceHandle *devHandle, 
								unsigned int memAdd, 
								unsigned char *byteData)
{
	int status;
	unsigned int receivedWord = 0;
	
	status = sc5506a_RegRead(devHandle, CAL_EEPROM_READ, (memAdd & 0xFFFF), &receivedWord);
	if(status != SUCCESS) return status;
	
	*byteData = (unsigned char)(receivedWord & 0xFF);

	return SUCCESS;	
}


int	sc5506a_ReadUserEeprom(deviceHandle *devHandle, 
								unsigned int memAdd, 
								unsigned char *byteData)
{
	int status;
	unsigned int receivedWord = 0;
	
	status = sc5506a_RegRead(devHandle, USER_EEPROM_READ, (memAdd & 0xFFFF), &receivedWord);
	if(status != SUCCESS) return status;
	
	*byteData = (unsigned char)(receivedWord & 0xFF);

	return SUCCESS;	
}

int sc5506a_GetDeviceInfo(deviceHandle *devHandle,
											deviceInfo_t *deviceInfo)
{		
	if(deviceInfo == NULL) return INPUTNOTALLOC; // if type is not allocated

	//Product Serial Number 
	deviceInfo->productSerialNumber = UsbReadCalU32(devHandle, 0x04);
	//Brick Serial Number 
	deviceInfo->rfModuleSerialNumber = UsbReadCalU32(devHandle, 0x08);
	//manDate 
	deviceInfo->calDate = UsbReadCalU32(devHandle, 0x0C);
	//CalDate 
	deviceInfo->manDate = UsbReadCalU32(devHandle, 0x10);	
	//Firmware Revision Converstion
	deviceInfo->firmwareRevision = UsbReadCalF32 (devHandle, 0x24);	
	//LO Hardware Revision Converstion
	deviceInfo->hardwareRevision = UsbReadCalF32 (devHandle, 0x28);
	
	return SUCCESS;
}
