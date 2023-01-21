@echo off
echo.
echo Notes about how to run RBN analysis tool on Windoze 10
echo.
echo Already should have matplotlib, cartopy installed from demos
echo Need a few more libs:
echo.
echo    pip install xlrd unidecode pyhamtools serial
echo.
echo To run (example):
echo.
echo    rbn_tool.py 20220728.csv -t1 3 -hours 1 -na
echo.
echo To compile (works under both linux and windoz):
echo.
echo         pyinstaller --onefile rbn_tool.py
echo         dist\rbn_tool.exe 20220728.csv -t1 3 -hours 1 -na
echo.

