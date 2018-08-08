// Example using DAQbufferPoolConfig
//
#include <iostream>
#include <Windows.h>
#include <conio.h>
#include "SD_AIN.h"
#include "sd_constants.h"
#include "SD_Module.h"
#include "SD_AOU.h"
#include "SD_WAVE.h"
using namespace std;

void myCallback(SD_Object* SDobject, int eventNumber, void* buffer0, int buffer0Points,
   void* buffer1, int buffer1Points, void* userObject, int status);

int main()
{
   int chassis = 1;
   int digSlot = 5;
   int digChannel = 1;

   int status, i;
   int channels[] = { 1 };
   int numberOfChannels = 1;

   double fullScale = 2;
   int pointsPerCycle = 20;
   int cycles = 1000;
   int delay = 0;

   int AIN_IMPEDANCE_HZ = 0;
   int AIN_IMPEDANCE_50 = 1;
   int AIN_COUPLING_DC = 0;
   int AIN_COUPLING_AC = 1;

   int timeOut = 10000;

   int BUFFER_SIZE = pointsPerCycle * cycles / 2;

   short *buffer1 = new short[BUFFER_SIZE];
   short *buffer2 = new short[BUFFER_SIZE];


   cout << "Enter chassis number: " << endl;
   cin >> chassis;
   char a;
   if (cin.fail()) {
      cout << "Invalid chassis" << endl;     
      getch();
      return 0;
   }

   cout << "Enter digitizer slot number: " << endl;
   cin >> digSlot;
   if (cin.fail()) {
      cout << "failed" << endl;
      getch();
      return 0;
   }
   

   SD_AIN *dig = new SD_AIN();

   if ((status = dig->open("M3102A", chassis, digSlot)) < 0)
   {
      cout << "Could not open digitizer: " << status << endl;
      getch();
      return 0;
   }
   
   dig->DAQflush(digChannel);
   
   dig->channelInputConfig(digChannel, fullScale, AIN_IMPEDANCE_50, AIN_COUPLING_DC);
   dig->DAQconfig(digChannel, pointsPerCycle, cycles, delay, SWHVITRIG);
      

   //Callback setup - not available in Python
   callbackEventPtr cb = callbackEventPtr(&myCallback);
   dig->DAQbufferPoolConfig(digChannel, buffer1, BUFFER_SIZE, timeOut, cb, NULL);
   dig->DAQbufferAdd(digChannel, buffer2, BUFFER_SIZE);
   

   dig->DAQstart(digChannel);
   cout << "Setup done." << endl;
   
   //Trigger or wait for all cycles
   for (i = 0; i < cycles; i++) 
   {
      Sleep(10);
      dig->DAQtrigger(digChannel);
   }
   
   
   cin >> status;
   cout << "done" << endl;
   dig->close();
   delete(buffer1);
   delete(buffer2);

   return 0;

}


//This function gets called every time the provided buffer gets full
//Here, one can save data to file, plot etc.
void myCallback(SD_Object* SDobject, int eventNumber, void* buffer0, int buffer0Points,
   void* buffer1, int buffer1Points, void* userObject, int status) 
{
   //As an example, we simply print out the acquired data to the console
   int i; 
   for (i = 0; i < buffer0Points; i++) 
   {
      cout << ((short*)buffer0)[i] << " " << std::flush; 
   }
   
   cout << endl;  
}