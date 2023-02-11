@echo off
goto BUILD
echo %DATE% %TIME%
echo.
echo Notes about how to compile and run RBN analysis tool on Windoze 10/11.
echo.
echo Already should have matplotlib, cartopy installed from demos
      pip install -r requirements.txt
echo.
echo To run the script directly under python (example):
echo.
      rbn_tool.py 20220728.csv -t1 3 -hours 1 -na
echo.
:BUILD       
echo.
echo To compile (works under both linux and windoz - takes a long time):
echo.
      pyinstaller --onefile rbn_tool.py
      copy 20220728.csv dist
      copy Release_Notes.txt dist
echo.
echo To test binary:
      dist\rbn_tool.exe 20220728.csv -t1 3 -hours 1 -na
echo.
echo Run Inno Setup Compiler and follow the prompts to create an installer
echo This installer works on Windoz 10 and Bottles!
echo Be sure to include a sample RBN file, e.g. 20220728.csv
echo.
echo %DATE% %TIME%
echo.

