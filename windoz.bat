@echo off
echo.
echo Notes about how to run RBN analysis tool on Windoze 10
echo THIS WILL NOT WORK UNTIL WE GET CARTOPY WORKING ON WINBLOZ!!!!!!!
echo.
echo Already should have matplotlib, basemap installed from demos
echo Need a few more libs:
echo.
echo    pip install xlrd unidecode pyhamtools serial
echo.
echo To run (example):
echo.
echo    rbn_tool.py 20220728.csv -t1 3 -hours 1 -na
echo.
echo To compile (works under linux):
echo.
echo         pyinstaller --onefile rbn_tool.py
echo         dist\rbn_tool.exe 20220728.csv -t1 3 -hours 1 -na
echo.
echo Do not try standalone windoz exe until get demos/basemap1.exe or
echo demos/cart1/py working
echo.
