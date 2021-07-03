/*
*	The example program shows how the user may want to program the device. This 
*	serves as only as an example. 
*	User may not want to use the calibration data or the method of application 
*	as outlined here. This device provide an extra user EEPROM for convenience, 
*	and may be used to store user calibration in applications where full system 
*	calibration is performed.
*	
*	This example shows how to initialize the device, read information stored
*	in the calibration EEPROM, reading device temperature, calculate the
* 	attenuator setting based on user inputs, set the attenuators and preamp,
*	calculate the conversion gain, read and write to the user EEPROM, and reading
*	the entire calibration EEPROM.
*/
#include <stdio.h>
#include <time.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <unistd.h>
#include <sc5413a.h>


 /* Some local functions to display results and perform memory allocation */
void displayDeviceStatus(deviceStatus_t *deviceStatus)
{
	printf("\n\n*********DEVICE STATUS READ FROM DEVICE***************\n");
	printf(" RF AMP #1 Status: %d \n",deviceStatus->rfAmpEnable);
	printf(" RF PATH: %d \n",deviceStatus->rfPath);
	printf(" LO ENABLE: %d \n",deviceStatus->loEnable);
	printf(" DEVICE ACCESSED: %d \n",deviceStatus->deviceAccess); 
	printf("\n");
}

void displayDeviceAttributes(deviceInfo_t *devInfo)
{
	printf("\n**********DEVICE ATTRIBUTES************* \n");
	printf(" The product serial number is 0x%08X \n",devInfo->productSerialNumber);
	printf(" The module serial number is 0x%08X \n",devInfo->rfModuleSerialNumber);
	printf(" The product firmware rev. is %f \n",devInfo->firmwareRevision);
	printf(" The product hardware rev. is %f \n",devInfo->hardwareRevision);
	printf(" The product manufactured date is: Year:%d Month:%d, Day:%d\n\n",
				(devInfo->manDate&0xFF000000)>>24,(devInfo->manDate&0xFF0000)>>16,(devInfo->manDate&0xFF00)>>8);	
}



/// The main entry-point function.
int main (int argc, char *argv[])
{
	
	//define the device data parameters
	deviceStatus_t devStatus;
	deviceInfo_t devInfo;
	float deviceTemp;
	
	//init some device input values
	
	// parameter to work with the USB device(s)
	#define MAXDEVICES 50
	deviceHandle *devHandle; //device handle
	int input; // user input to select the device found
	int numOfDevices; // the number of device types found
	char **deviceList;  // 2D to hold serial numbers of the devices found 
	int status; // status reporting of functions

	// test read and write 
	int i;
	unsigned char byte;
	unsigned char userData[8] = {0xA1,0xA2,0xAE,0xA4,0x05,0x06,0x07,0xA9};
	unsigned int userMemAdd; 
	
	/* 	Begin by looking for devices attached to the host 
	*	=============================================================================================
	*/

	deviceList = (char**)malloc(sizeof(char*)*MAXDEVICES); // MAXDEVICES serial numbers to search
	for (i=0;i<MAXDEVICES; i++)
		deviceList[i] = (char*)malloc(sizeof(char)*SCI_SN_LENGTH); // SCI SN has 8 char

	numOfDevices = sc5413a_SearchDevices(deviceList); //searches for SCI for device type
	
	if (numOfDevices == 0) 
	{
		printf("No SignalCore SC5413A devices found\n");
		for(i = 0; i<MAXDEVICES;i++) free(deviceList[i]);
		free(deviceList);
		return 1;
	}

	printf("\n There are %d SignalCore %s USB devices found. \n \n", numOfDevices, SCI_PRODUCT_NAME);
	i = 0;
	while ( i < numOfDevices)
	{
		printf("	Device %d has Serial Number: %s \n", i+1, deviceList[i]);
		i++;
	}

	printf("\n Enter the number of the device you wish to select : ");
	
	scanf(" %d",&input);
	getchar();
	if ((input < 1) || (input > numOfDevices)) 
	{
		printf(" No such device !!! exiting... \n");
		return 1;
	}
//	Open the selected device through the use of its serial number

	devHandle = sc5413a_OpenDevice(deviceList[input-1]);

	if (devHandle->handle == NULL) //make sure the device was opened successfully
	{
		printf("Device with serial number: %s cannot be opened.\n",deviceList[input-1]);
		printf("Please ensure your device is powered on and connected\n");
		for(i = 0; i<MAXDEVICES;i++) free(deviceList[i]); 
		free(deviceList);
		free(devHandle);  //If NULL, need to free devHandle OpenDevice allocate memory to it.
		return 1;
	}
	printf("Opened Device %s\n", deviceList[input-1]);

	for(i = 0; i<MAXDEVICES;i++) free(deviceList[i]); 
	free(deviceList); // Done with the deviceList


	/*	Begin communication to the device	
	*/

	printf("\n Init the device ..........\n");	
	status = sc5413a_InitDevice(devHandle, 0);  // reset the device to power on state
	if (status != SUCCESS) return 1;

	printf("\nGetting device Info ..........\n");
	status = sc5413a_GetDeviceInfo(devHandle, &devInfo);  // obtain device info
	if (status != SUCCESS) return status;
	displayDeviceAttributes(&devInfo);

	printf("\n Setting the RF Attenuators ..........\n");	
	status = sc5413a_SetRfAttenuation(devHandle, RF_ATTEN1, 0);
	printf ("Status : %d", status);
	if (status != SUCCESS) return status;
	printf("\n RF Atten 1 set to 0 dB ..........\n");
	status = sc5413a_SetRfAttenuation(devHandle, RF_ATTEN2, 0);
	if (status != SUCCESS) return status;
	printf("\n RF Atten 2 set to 0 dB ..........\n");
	status = sc5413a_SetRfAttenuation(devHandle, RF_ATTEN3, 5);
	if (status != SUCCESS) return status;
	printf("\n RF Atten 3 set to 5 dB ..........\n\n");

	printf("\n Enabling LO Output ..........\n");	
	status = sc5413a_SetLoOut(devHandle, 1);
	if (status != SUCCESS) return 1;

	printf("\n Getting the device status..........\n");	
	status = sc5413a_GetDeviceStatus(devHandle, &devStatus); // Obtain the current status of the device
	if (status != SUCCESS) return 1;
	
	displayDeviceStatus(&devStatus); // display the device status 


	printf("\n********* Reading 16 bytes from Cal EEPROM ***********\n\n");
	for (i=0x04; i < 0x0B; i++)
	{
	status = sc5413a_ReadCalEeprom(devHandle, i, &byte);
	printf("%02X ", byte);
	}
	printf("\n\n");

	status = sc5413a_GetTemperature(devHandle, &deviceTemp); // obtain the temperature
	if (status != SUCCESS) return 1;
	printf("\n The temperature of the device is %f degC\n\n", deviceTemp);

	printf("\n********* Writing 8 bytes to User EEPROM ***********\n\n");

	userMemAdd = 0x10;
	for (i=0; i < 8; i++)
	{
	status = sc5413a_WriteUserEeprom(devHandle, userMemAdd + i, userData[i]);
	//Sleep(2); // require a short wait between EEPROM writes, adjust for user system, needs windows.h
	printf("%02X ", userData[i]);
	}	
	printf("\n\n********* Reading 8 bytes from User EEPROM ***********\n\n");	
	for (i=0x0; i < 0x8; i++)
	{
	status = sc5413a_ReadUserEeprom(devHandle,userMemAdd + i, &byte);
	printf("%02X ", byte);
	}	

	printf("\n\n********** EXAMPLE DONE **********\n");
	
	// Do not free devHandle if devHandl->handle != NULL
	//CloseDevice will needs it to close properly because a session is still opened.
	sc5413a_CloseDevice(devHandle);
	return 1;
}




