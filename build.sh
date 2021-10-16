#!/bin/sh
pyinstaller slabelfish.py --distpath "./bin/linux/" --exclude-module _bootlocale -F
