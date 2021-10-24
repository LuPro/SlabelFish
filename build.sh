#!/bin/sh
pyinstaller slabelfish.py --name slabelfish_linux --distpath "./bin/linux/" --exclude-module _bootlocale -F
