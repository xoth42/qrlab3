@echo off
set PYTHONPATH=%CD%;%CD%\objectsharer\;%CD%\pulseseq;%PYTHONPATH%

start /min "Instrument Server" start_instrumentserver.bat
start /min "Data Server" start_dataserver.bat

REM The instrument GUI call was removed by Josh on 2/19/18
REM It doesn't work and it has a replacement anyway.