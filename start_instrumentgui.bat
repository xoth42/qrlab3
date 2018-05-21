@echo off
set PYTHONPATH=%CD%;%CD%\objectsharer\;%PYTHONPATH%
cd instrumentserver
python instrument_gui.py
cd ..
