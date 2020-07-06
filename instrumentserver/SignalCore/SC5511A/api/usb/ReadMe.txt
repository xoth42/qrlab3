Description of the \Win\API directories:

\C contains the DLL and header files for development in x86 and x64 architectures based on LibUSB (WinUSB).

\LabVIEW contains the LabVIEW wrappers of the x86 DLL. The \SignalCore sub-directory contains the standard LabVIEW palette functions for this product as well as the appropriate directory menu files needed for this product's sub-palette to be listed under the main SignalCore (SCI) palette group.

To properly create the SC5511A LabVIEW pallet directory, drag the \SignalCore folder located under \win\api\labview into the \instr.lib folder under the LabVIEW installation directory (typically C:\Program Files (x86)\National Instruments\LabVIEW XXXX, where XXXX is the installed version number(version 2010 or later is required). IF previous SignalCore products have been installed to this folder, select "copy and merge files" if a folder conflict window appears.

For 64-bit operating systems, make sure the sc5511a.dll and libusb-1.0.dll are in the C:\windows\sysWOW64\ directory. If they are not, copy these 2 files from the api\c\x86 directory into the \sysWOW64 directory. These two files are required for LabVIEW (32-bit) to function.


