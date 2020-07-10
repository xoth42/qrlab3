SC5511A
100 MHz to 20 GHz Signal Source

©2015 SignalCore, Inc.

Document is for Windows OS Only, for Linux instructions see the Readme.txt file in the Linux Directory

Installation Steps

*** FOR PROPER INSTALLATION, DO NOT ATTACH THE DEVICE TO YOUR COMPUTER AT THIS TIME.

*** Please note that the LabVIEW API function palette must be installed separately. To install the LabVIEW API palette, refer to step 26, below.

1. Run "SC5511A Installer.exe" To install the control software and LabVIEW runtime engine (if necessary)

2. If LabVIEW 2010 or the LabVIEW 2010 Run-Time Engine are already installed on your machine, skip to step 5.

3. If LabVIEW 2010 or the LabVIEW 2010 Run-Time Engine are not installed on your computer, select "Install LabVIEW Run-Time Engine" on the installation menu. This file is required for the Soft Front Panel application to run properly.

4. After the LabVIEW installer finishes, exit the LabVIEW installation window to return to the main SC5511A installation menu.

NOTE: The LabVIEW Run-Time installer may require you to reboot your computer to complete its installation. If so, once the computer has booted and returned to the desktop, navigate back to the SC5511A installation folder on the USB flash drive and proceed to step 5.

5. On the main installation menu, select either "Install SC5511A Software for 32-bit Windows" or "Install SC5511A Software for 64-bit Windows" depending on which type of operating system is installed on the host computer. Follow the instructions in the installer application. Exit the main SC5511A installation menu when finished.

********************************************************************************
The Soft Front Panel has only been tested to run on Windows XP, Vista, and Windows 7 operating systems. All drivers are found under the SC5511A\Win\ directory on the USB installation flash drive. Follow the instructions below to install the driver for your operating system. The instructions below assume that the USB flash drive has been assigned to drive letter "D:". Substitute the appropriate drive letter if your USB flash drive letter is different.
********************************************************************************

For all Windows operating systems (menu wording may vary slightly from OS to OS):

6. Apply power to the SC5511A.

7. Connect a mini-USB to Type-A USB cable between the SC5511A and an available USB port on the host computer.

8. The "Found New Hardware Wizard" dialog will open. The operating system will try to detect and load the driver but will fail to do so. Exit the "Found New Hardware" wizard.

9. Click on Start button and then select "Run".

10. Type devmgmt.msc into the text box and hit the "ENTER" key or click the "OK" button. The device manager dialog box will open.

11. Under the SC5511A should be listed under "Other Devices". Right click on the SC5511A entry and select "Update Driver Software". The Update Driver Software wizard will appear.

12. Select "Browse my computer for driver software."

13. Select "Let me pick from a list of device drivers on my computer", then click [Next] to continue.

14. Select “Show All Devices” and click [Next] to continue.

15. On the next two screens, click [Have Disk…].

16. On the next screen browse to or type in the directory location where the sc5511a.inf file resides. If you used the default install location for the Setup32 or Setup64 executable, the INF file will be located under C:\Program Files\SignalCore\SC5511A. Select the appropriate directory and click [OK]. Alternatively the file is also at USB_DRIVE:\SC5511A\Win directory

17. The host PC will pick up the information provided by the sc5511a.inf file and should show that it has found a driver for the device. If the wrong directory is chosen for the location of the sc5511a.inf file, the device will not show up in the list. In that case, you will need to click [Have Disk…] again and select the correct directory. If the device driver shows up correctly in the list, click [Next] to continue.

18. There will be a warning that the driver is not digitally signed and Windows cannot verify the publisher of the driver. The SC5511A device drivers are not digitally signed. However, SignalCore takes proper precautions and all device drivers are thoroughly tested. Select "Install this software driver anyway" to start the installation.

19. The installation should proceed to completion at this point.

20. On completion of the driver installation, the "Completing the Found New Hardware Wizard" dialog box will display. Click on the "Finish" button to end the installation.

21. To verify that the device is successfully installed, check device manager to see if the computer has properly recognized it. To bring up the device manager again, perform the following actions: 

22. Click on Start button and then select "Run".

23. Type devmgmt.msc into the text box and hit the "ENTER" key or click the "OK" button. The device manager dialog box will open.

24. The SC5511A device should show under the "SignalCore USB Devices" group as the SC5511A Signal Source". Please contact SignalCore if the device does not show up in the list.
 
25. You can launch installed applications and the operating and programming manual by navigating to the "Signalcore" directory under "Program Files" (or the custom location designated by you during installation) or navigating to the "SignalCore" (or custom) folder in the Programs listing under the Start menu.

26. To install the API for LabVIEW, copy the "SignalCore" folder in the Win\API\LabVIEW directory into the instr.lib directory of the LabVIEW version installed on the host computer. For example, for LabVIEW 2010 installations the full directory path would be C:\Program Files\National Instruments\LabView 2010\instr.lib. If SignalCore products have previously been installed on the host computer, Copy and merge the contents of the \SignalCore folder with the existing \SignalCore folder.

26.1 Launch LabVIEW. The SignalCore sub-palette should appear under the Instrument I/0 -> Instrument Drivers function palette.

26.2 The SC5511A function palette will be located under the SignalCore sub-palette.
