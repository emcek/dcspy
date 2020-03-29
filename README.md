[![image](https://img.shields.io/badge/pypi-v1.1.1-blue.svg)](https://pypi.org/project/dcspy/)
[![Build Status](https://travis-ci.org/emcek/dcspy.svg?branch=master)](https://travis-ci.org/emcek/dcspy)
[![Coverage Status](https://coveralls.io/repos/github/emcek/dcspy/badge.svg?branch=master)](https://coveralls.io/github/emcek/dcspy?branch=master)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/5270a4fc2ba24261a3bfa7361150e8ff)](https://www.codacy.com/manual/mplichta/dcspy?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=emcek/dcspy&amp;utm_campaign=Badge_Grade)
[![BCH compliance](https://bettercodehub.com/edge/badge/emcek/dcspy?branch=master)](https://bettercodehub.com/)
[![image](https://img.shields.io/badge/python-3.6%20%7C%203.7%20%7C%203.8-blue.svg)](https://github.com/emcek/dcspy)
[![License](https://img.shields.io/badge/Licence-MIT-blue.svg)](./LICENSE.md)  
![dcspylogo](https://i.imgur.com/eqqrPB8.jpg)  
# dcspy
DCSpy is able to pull information from DCS aircraft and display on Logitech G-series keyboards LCD. Developed for **Logitech G13**.
Should also work with any other Logitech device with 160x43 px monochrome display, like G15 (v1 and v2) and G510. 
There is possibility to modify this package to use full RGBA LCD of Logitech G19 (size 320x240) - please open issue, anyway I have plan to do it in future.  

## Table of Contents
* [Aircrafts and instruments](#aircrafts-and-instruments)
* [Requirements](#requirements)
* [Credits](#credits)
* [Installation](#installation)
* [Usage](#usage)
* [FAQ](#faq)
* [New ideas](#new-ideas)
* [Contributing](#contributing)

## Aircrafts and instruments
* F/A-18C Hornet UFC - Up Front Controller
* F-16C Viper DED - Data Entry Display
* Ka-50 Black Shark PVI-800 and autoplilot chanels
* F-14B Tomcat - basic support for RIO CAP
* more to come....

## Requirements
* [Python 3.8](https://www.python.org/downloads/) (but 3.6+ should be fine)
* [Logitech Gaming Software 9.02.65](https://support.logitech.com/software/lgs)
* [Logitech LCD SDK 8.57.148](http://gaming.logitech.com/sdk/LCDSDK_8.57.148.zip) extract to `C:\Program Files\Logitech Gaming Software\LCDSDK_8.57.148`
* [DCS-BIOS 0.7.34](https://github.com/DCSFlightpanels/dcs-bios/releases/latest) (or newer)

## Credits
This project has been heavily inspired by [specelUFC](https://github.com/specel/specelUFC), and I want to thank **specel**, the author of that project for his work and the inspiring ideas. This software uses:
* [DCS-BIOS](https://github.com/DCSFlightpanels/dcs-bios) fork by DCSFlightpanels for exporting data from DCS to local network
* [jboecker's parser](https://github.com/jboecker/python-dcs-bios-example) to read data stream from DCS-BIOS

## Installation
1. Install all requirements
2. During Python installation please select  
   * Optional Features:
     * pip
     * tcl/tk and IDLE (for future use)
     * py launcher  
   * Advanced Options:
     * Associate files with Python (requires the py lauchner)
     * Add Python to environment variables
     * Customize install location: C:\Python38 or C:\Python
3. Package is available on [PyPI](https://pypi.org/project/dcspy/), open Command Prompt and type:
```shell script
pip install dcspy
```
or use wheel file from [releases](https://github.com/emcek/dcspy/releases/latest):
```shell script
pip install dcspy-1.1.1-py3-none-any.whl
```

## Usage
1. Run Logitech Gaming Software (it allow to update LCD)
2. You can check with `pip uninstall dcspy` (**NOTE!** answer no to question) where dcspy was installed. Usually pip should install dcspy into you python directory: i.e.:
   * `c:\python38\dcspy_data\dcspy.ico`
   * `c:\python38\scripts\dcspy.exe`
3. You can drag and drop `dcspy.exe` to desktop and make shortcut (with custom icon).
4. Double click on dcspy icon or type `dcspy.exe` from Command Prompt
5. LCD display should update with basic info, waiting to connect to DCS 
6. Run DCS and start any mission.

## FAQ
1. Why in [F-16C DED](https://i.imgur.com/Hr0kmFV.jpg) instead of triangle up and down arrow I see strange character.   
   I didn't find good alternative so I use unicode character [2195](https://www.fileformat.info/info/unicode/char/2195/index.htm) which do not render very well
2. I got error: `'pip' is not recognized as an internal or external command, operable program or batch file.`  
   Probably during installation of Python `pip` and/or `Add Python to environment variables` were not selected. Uninstall Python and install again with correct options. 

## New ideas
I have lots of plans and new ideas how to improve it internally and form user's perspective, but don't hesitate to contact me. Maybe it will motivate me to implement some new stuff. Please open issue if you find bug or have any crazy idea.  
You are welcome [dcspy Discord](https://discord.gg/SP5Yjx3) server. 

## Contributing
You want contribute, perfect see: [contributing](./CONTRIBUTING.md) guide.
