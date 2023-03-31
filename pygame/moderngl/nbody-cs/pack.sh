#!/bin/bash
rm -rf main build/ dist/
pyinstaller --onefile --hidden-import glcontext main.py 
mv dist/main .
