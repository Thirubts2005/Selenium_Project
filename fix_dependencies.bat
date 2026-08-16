@echo off
echo Uninstalling old versions...
pip uninstall pandas numpy -y
echo Installing compatible versions...
pip install numpy==1.24.3 pandas==2.0.3
echo Dependencies fixed!
pause