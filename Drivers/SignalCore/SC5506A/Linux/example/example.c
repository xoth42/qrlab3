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
#include <stdlib.h>
#include <time.h>
#include <unistd.h>
#include <string.h>
#include <sc5506a.h>


 /* Some local functions to display results and perform memory allocation */
void displayDeviceStatus(deviceStatus_t *deviceStatus)
{
	printf("\n\n*********DEVICE STATUS READ FROM DEVICE***************\n");
	printf(" External reference detected: %d \n",deviceStatus->extRefDetected);
	printf(" External reference lock enabled: %d \n",deviceStatus->extRefLockEnable);
	printf(" Reference clk out enabled: %d \n",deviceStatus->refClkOutEnable);
	printf(" External reference lock status: %d \n",deviceStatus->tcxoPllStatus);
	printf(" VCXO 100MHz PLL lock status: %d \n",deviceStatus->vcxoPllStatus); 
	printf(" Ch1 PLLs lock status: %d \n",deviceStatus->ch1CrsPllStatus && deviceStatus->ch1FinePllStatus && deviceStatus->ch1SumPllStatus); 
	printf(" Ch2 PLLs lock status: %d \n",deviceStatus->ch2CrsPllStatus && deviceStatus->ch2FinePllStatus && deviceStatus->ch2SumPllStatus); 
	printf(" Ch1 RF enable: %d \n",deviceStatus->ch1RfOutEnable); 
	printf(" Ch2 RF enable: %d \n",deviceStatus->ch2RfOutEnable); 
	printf(" Ch1 Alc Disabled: %d \n",deviceStatus->ch1AlcOpen); 
	printf(" Ch2 Alc Disabled: %d \n",deviceStatus->ch2AlcOpen); 
	printf("\n");
	
	if(deviceStatus->extRefLockEnable)
	{
		if(deviceStatus->extRefDetected)
		{
			if(deviceStatus->tcxoPllStatus)
			{
				printf("External Reference Detected. Locked to external reference.\n");
			}
			else
			{
				printf("Error: External Reference Detected. Unable to lock to external reference.\n");
			}
		}
		else
		{
			printf("Error: No external reference detected.\n");
		}
	}

}

void displayDeviceAttributes(deviceInfo_t *devInfo)
{
	printf("\n**********DEVICE ATTRIBUTES************* \n");
	printf(" The product serial number is 0x%08X \n",devInfo->productSerialNumber);
	printf(" The module serial number is 0x%08X \n",devInfo->rfModuleSerialNumber);
	printf(" The product firmware rev. is %f \n",devInfo->firmwareRevision);
	printf(" The product hardware rev. is %f \n",devInfo->hardwareRevision);
	printf(" The product cal date is: %08X \n\n",
					devInfo->calDate);	
}



/// The main entry-point function.
int main (int argc, char *argv[])
{
	
	//define the device data parameters
	deviceStatus_t devStatus;
	deviceInfo_t devInfo;
	float deviceTemp;
	
	//init some device input values
	unsigned long long int ch1RfFreq = (unsigned long long int)(2000000000); // chan #1 freq = 2.0 GHz
	unsigned long long int ch2RfFreq = (unsigned long long int)(1800000000); // chan #2 freq = 1.8 GHz
	float ch1Level = 0.0; // channel #1 rf level;
	float ch2Level = 0.0; // channel #2 rf level;
	
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
	unsigned char userData[8] = {0xA1,0xA2,0xA3,0xA4,0x05,0x06,0x07,0xA8};
	unsigned int userMemAdd; 

	// generic counter
	
	
	/* 	Begin by looking for devices attached to the host 
	*	=============================================================================================
	*/
	
	deviceList = (char**)malloc(sizeof(char*)*MAXDEVICES); // MAXDEVICES serial numbers to search
	for (i=0;i<MAXDEVICES; i++)
		deviceList[i] = (char*)malloc(sizeof(char)*SCI_SN_LENGTH); // SCI SN has 8 char
		
	numOfDevices = sc5506a_SearchDevices(deviceList); //searches for SCI for device type
	
	if (numOfDevices == 0) 
	{
		printf("No signal core devices found or cannot not obtain serial numbers\n");
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
	/* 	*/
	printf("\n Enter the number of the device you wish to select : ");
	
	scanf(" %d",&input);
	getchar();
	if ((input < 1) || (input > numOfDevices)) 
	{
		printf(" No such device !!! exiting... \n");
		return 1;
	}
	/*	Open the selected device through the use of its serial number
	*/
	devHandle = sc5506a_OpenDevice(deviceList[input - 1]);
	
	if (devHandle->handle == NULL) 
	{
		printf("Device with serial number: %s cannot be opened.\n", deviceList[input - 1]);
		printf("Please ensure your device is powered on and connected\n");
		for(i = 0; i<MAXDEVICES;i++) free(deviceList[i]); 
		free(deviceList);
		free(devHandle); //devHandle is allocated memory on OpenDevice(); 
		return 1;
	}

	for(i = 0; i<MAXDEVICES;i++) free(deviceList[i]); 
	free(deviceList); // Done with the deviceList


	/*	Begin communication to the device	
	*/

	printf("\n Init the device ..........\n");	
	status = sc5506a_InitDevice(devHandle, 0);  // reset the device to power on state
	if (status != SUCCESS) return 1;
	
	status = sc5506a_SetRfOutput(devHandle, CH1, 0x01);
	if (status != SUCCESS) return 1;
	printf("\n Enable Rf CH1 ..........\n");	
	status = sc5506a_SetAlcMode(devHandle, CH1, 0x01);
	if (status != SUCCESS) return 1;
	printf("\n ALC Mode set to Close Loop on CH1 ..........\n");	

	printf("\n Getting the device status..........\n");	
	status = sc5506a_GetDeviceStatus(devHandle, &devStatus); // Obtain the current status of the device
	if (status != SUCCESS) return 1;
	
	displayDeviceStatus(&devStatus); // display the device status 
	
	printf("\nGetting device Info ..........\n");
	status = sc5506a_GetDeviceInfo(devHandle, &devInfo);  // obtain calData
	printf("\nSet Done ..........\n");	
	if (status != SUCCESS) return 1;
	displayDeviceAttributes(&devInfo);

	status = sc5506a_SetFrequency(devHandle, CH1, ch1RfFreq); // Set channel #1 freq
	if (status != SUCCESS) return 1;
	printf("\n Set freq on CH1..........\n");
	status = sc5506a_SetPowerLevel(devHandle, CH1, ch1Level); // Set channel #1 rf power level
	if (status != SUCCESS) return 1;
	printf("\n Set power level of CH1 ..........\n");
	status = sc5506a_SetFrequency(devHandle, CH2, ch2RfFreq); // Set channel #2 freq
	if (status != SUCCESS) return 1;
	printf("\n Set freq on Ch2..........\n");
	status = sc5506a_SetPowerLevel(devHandle, CH2, ch2Level); // Set channel #2 rf power level
	if (status != SUCCESS) return 1;
	printf("\n Set pow on CH2..........\n");
	printf(" The channel #1 frequency is set to %f Hz \n\n", (double)ch1RfFreq);
	printf(" The channel #2 frequency is set to %f Hz \n\n", (double)ch2RfFreq);

	printf("\n********* Reading 16 bytes from Cal EEPROM ***********\n\n");
	for (i=0x04; i < 0x14; i++)
	{
	status = sc5506a_ReadCalEeprom(devHandle, i, &byte);
	printf("%02X ", byte);
	}
	printf("\n\n");

	status = sc5506a_GetTemperature(devHandle, &deviceTemp); // obtain the temperature
	if (status != SUCCESS) return 1;
	printf("\n The temperature of the device is %f degC\n\n", deviceTemp);

	printf("\n********* Writing 8 bytes to User EEPROM ***********\n\n");

	userMemAdd = 0x10;
	for (i=0; i < 8; i++)
	{
	status = sc5506a_WriteUserEeprom(devHandle, userMemAdd + i, userData[i]);
	printf("%02X ", userData[i]);
	}	
	printf("\n\n********* Reading 8 bytes from User EEPROM ***********\n\n");	
	for (i=0x0; i < 0x8; i++)
	{
	status = sc5506a_ReadUserEeprom(devHandle,userMemAdd + i, &byte);
	printf("%02X ", byte);
	}	

	printf("\n\n********** EXAMPLE DONE **********\n");

	sc5506a_CloseDevice(devHandle); //function closes the device and frees the device Handle
	return 1;
}




