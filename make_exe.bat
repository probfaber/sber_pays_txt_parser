@echo off

del /Q build
del /Q *.spec

pyinstaller --onefile -y sber_pays_txt_parser_gui.py

pause