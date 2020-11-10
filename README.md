[![image](https://img.shields.io/badge/pypi-v1.2.0-blue.svg)](https://pypi.org/project/dcspy/)
[![Python](https://github.com/emcek/dcspy/workflows/Python/badge.svg)](https://github.com/emcek/dcspy/actions)
[![Build Status](https://travis-ci.org/emcek/dcspy.svg?branch=master)](https://travis-ci.org/emcek/dcspy)
[![Coverage Status](https://coveralls.io/repos/github/emcek/dcspy/badge.svg?branch=master)](https://coveralls.io/github/emcek/dcspy?branch=master)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/5270a4fc2ba24261a3bfa7361150e8ff)](https://www.codacy.com/manual/mplichta/dcspy?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=emcek/dcspy&amp;utm_campaign=Badge_Grade)
[![BCH compliance](https://bettercodehub.com/edge/badge/emcek/dcspy?branch=master)](https://bettercodehub.com/)
[![image](https://img.shields.io/badge/python-3.6%20%7C%203.7%20%7C%203.8-blue.svg)](https://github.com/emcek/dcspy)
[![License](https://img.shields.io/badge/Licence-MIT-blue.svg)](./LICENSE.md)  
![dcspylogo](https://i.imgur.com/eqqrPB8.jpg)  
# dcspy
DCSpy is able to pull information from DCS aircraft and display on Logitech G-series keyboards LCD.
It supports:
*  Logitech device with 160x43 px (4 lines) monochrome LCD display - **G13**, **G15 (v1 and v2)** and **G510**
*  Logitech device with 320x240 px (8 lines) full RGBA LCD display - **G19**

## Table of Contents
* [Aircrafts and instruments](#aircrafts-and-instruments)
* [Requirements](#requirements)
* [Credits](#credits)
* [Installation](#installation)
* [Usage](#usage)
* [Mono vs. Color](#mono-vs-color)
* [FAQ](#faq)
* [New ideas](#new-ideas)
* [Contributing](#contributing)

## Aircrafts and instruments
* F/A-18C Hornet UFC - Up Front Controller
* F-16C Viper DED - Data Entry Display
* Ka-50 Black Shark PVI-800 and autopilot channels
* F-14B Tomcat - basic support for RIO CAP
* more to come....

## Requirements
* [Python 3.8](https://www.python.org/downloads/) but 3.6+ (with tcl/tk support, see installation) should be fine, please choose Windows x86-64 version, file should be python-3.8.5-amd64.exe
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
     * tcl/tk and IDLE
     * py launcher  
   * Advanced Options:
     * Associate files with Python (requires the py launcher)
     * Add Python to environment variables
     * Customize install location: **C:\Python38** or **C:\Python**
3. Package is available on [PyPI](https://pypi.org/project/dcspy/), open Command Prompt and type:
```shell script
pip install dcspy
```
or download manually wheel file from [releases](https://github.com/emcek/dcspy/releases/latest):
```shell script
pip install dcspy-1.2.0-py3-none-any.whl
```

## Usage
1. Run Logitech Gaming Software (it allow to update LCD)
2. You can check with `pip uninstall dcspy` (**NOTE!** answer **No** to question) where dcspy was installed. Usually pip should install dcspy into you python directory: i.e.:
   * `c:\python38\dcspy_data\dcspy.ico`
   * `c:\python38\scripts\dcspy.exe`
3. You can drag and drop `dcspy.exe` to desktop and make shortcut (with custom icon, you can find icon in installation directory).
4. Double click on dcspy icon or type `dcspy.exe` from Command Prompt
5. LCD display should update with dcspy basic info, waiting to connect to DCS 
6. Run DCS and start any mission.

## Mono vs. Color
DCSpy do not uses full potential of G19, which support full RGBA, 8-lines LCD with 7 programmable buttons. In contrast to 
mono devices (like G13, G15 and G510), which support mono, 4-lines LCD with only 4 buttons. Right now DCSpy use only top 
4 lines of LCD and 4 buttons. Way in which actions assign to buttons for G13 (4 buttons form left to right) are mapped to G19 looks:
* G13 1st button -> G19 left button
* G13 2nd button -> G19 right button
* G13 3rd button -> G19 down button
* G13 4th button -> G19 up button

Maybe in future when settings via config file will be added, then it allowed usage all 7 buttons in G19. But right now 
actions for supported airplanes are hardcoded right now and look like:

### F/A-18C Hornet
* UFC COMM1 channel select decrease
* UFC COMM1 channel select increase
* UFC COMM2 channel select decrease
* UFC COMM2 channel select increase

### Ka-50 Black Shark
* PVI waypoints button
* PVI fix points button
* PVI airfield button
* PVI targets button

### F-14B Tomcat
* RIO CAP Clear
* RIO CAP SW
* RIO CAP NE
* RIO CAP Enter

## FAQ
1. Why in [F-16C DED](https://i.imgur.com/Hr0kmFV.jpg) instead of triangle up and down arrow I see strange character.   
   I didn't find good alternative so I use unicode character [2195](https://www.fileformat.info/info/unicode/char/2195/index.htm) which do not render very well
2. I got error: `'pip' is not recognized as an internal or external command, operable program or batch file.`  
   Probably during installation of Python `pip` and/or `Add Python to environment variables` were not selected. Uninstall Python and install again with correct options. 
3. Is DCSpy working with Python 3.9?  
   Python 3.9 is not supported, because current [Pillow 7.2](https://pillow.readthedocs.io/en/latest/installation.html#python-support) not working with Python 3.9, as it's developers said: 
   > Pillow 7.2.0 does not support Python 3.9 and does not provide prebuilt Windows binaries. We do not recommend building from source on Windows.  

## New ideas
I have lots of plans and new ideas how to improve it internally and form user's perspective, but don't hesitate to contact me. Maybe it will motivate me to implement some new stuff. Please open issue if you find bug or have any crazy idea.  
You are welcome [dcspy Discord](https://discord.gg/SP5Yjx3) server. 

## Contributing
You want contribute, perfect see: [contributing](./CONTRIBUTING.md) guide.
