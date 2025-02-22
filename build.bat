@echo off

pyside6-rcc resources.qrc -o resources_rc.py
python -m nuitka --onefile --windows-console-mode=disable --enable-plugin=pyside6 --windows-icon-from-ico=icon.ico main.py --output-filename=Telescan2coeGui
