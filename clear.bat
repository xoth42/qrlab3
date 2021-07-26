@echo off

TASKKILL /FI "WINDOWTITLE eq Instrument Server*" /T /F >nul 2>&1
TASKKILL /FI "WINDOWTITLE eq Select Instrument Server*" /T /F >nul 2>&1
TASKKILL /FI "WINDOWTITLE eq Data Server*"  /T  /F >nul 2>&1
TASKKILL /FI "WINDOWTITLE eq QRLab Server*"  /T  /F >nul 2>&1
TASKKILL /FI "WINDOWTITLE eq QRLab*"  /T  /F >nul 2>&1

exit