@echo off
set PYTHONPATH=%CD%;%CD%\objectsharer\;%CD%\pulseseq;%PYTHONPATH%

start /min "Instrument Server" start_instrumentserver.bat
start /min "Data Server" start_dataserver.bat
