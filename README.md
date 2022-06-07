[![image](https://img.shields.io/badge/pypi-v1.6.1-blue.svg)](https://pypi.org/project/dcspy/)
[![Python CI](https://github.com/emcek/dcspy/actions/workflows/python-ci.yml/badge.svg?branch=master)](https://github.com/emcek/dcspy/actions/workflows/python-ci.yml)
[![Coverage Status](https://coveralls.io/repos/github/emcek/dcspy/badge.svg?branch=master)](https://coveralls.io/github/emcek/dcspy?branch=master)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/5270a4fc2ba24261a3bfa7361150e8ff)](https://www.codacy.com/manual/mplichta/dcspy?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=emcek/dcspy&amp;utm_campaign=Badge_Grade)
[![License](https://img.shields.io/badge/Licence-MIT-blue.svg)](./LICENSE.md)
[![Downloads](https://img.shields.io/github/downloads/emcek/dcspy/total?label=Downloads)](https://github.com/emcek/dcspy/releases)
[![dcspy](https://snyk.io/advisor/python/dcspy/badge.svg)](https://snyk.io/advisor/python/dcspy)
[![Patreon](https://img.shields.io/badge/Patreon-donate-ff424d?logo=patreon)](https://www.patreon.com/mplichta)
[![Discord](https://img.shields.io/discord/672486999516774442?label=Discord&logo=discord&logoColor=lightblue)](https://discord.gg/SP5Yjx3)
[![image](https://img.shields.io/badge/python-3.7%20%7C%203.8%20%7C%203.9%20%7C%203.10-blue.svg)](https://github.com/emcek/dcspy)
[![BCH compliance](https://bettercodehub.com/edge/badge/emcek/dcspy?branch=master)](https://bettercodehub.com/)
[![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=emcek_dcspy&metric=sqale_rating)](https://sonarcloud.io/dashboard?id=emcek_dcspy)
[![CII Best Practices](https://bestpractices.coreinfrastructure.org/projects/6056/badge)](https://bestpractices.coreinfrastructure.org/projects/6056)
![dcspylogo](https://i.imgur.com/eqqrPB8.jpg)  
## DCSpy
DCSpy is able to pull information from DCS aircraft and display on Logitech G-series keyboards LCD.
It supports:
*  Logitech device with 160x43 px (4 lines) monochrome LCD - **G13**, **G15 (v1 and v2)** and **G510**
*  Logitech device with 320x240 px (8 lines) full RGBA LCD - **G19**

## Sponsored by Jetbrains Open Source Support Program
[![logo](https://resources.jetbrains.com/storage/products/company/brand/logos/PyCharm.svg)](https://jb.gg/OpenSourceSupport)
[![logo](https://resources.jetbrains.com/storage/products/company/brand/logos/jb_beam.svg)](https://jb.gg/OpenSourceSupport)

## Table of Contents
* [Aircraft and instruments](#aircraft-and-instruments)
* [Requirements](#requirements)
* [Credits](#credits)
* [Installation](#installation)
* [Upgrade](#upgrade)
* [Usage](#usage)
* [Configuration](#configuration)
* [Mono vs. Color](#mono-vs-color)
* [FAQ](#faq)
* [New ideas](#new-ideas)
* [Contributing](#contributing)

## Aircraft and instruments
* F/A-18C Hornet UFC - Up Front Controller
* F-16C Viper DED - Data Entry Display
* Ka-50 Black Shark PVI-800 and autopilot channels
* A-10C Warthog and A-10C II Tank Killer - Radio frequency information
* F-14B Tomcat - basic support for RIO CAP
* AV-8B Night Attack Harrier - Up Front Controller and Option Display Unit
* AH-64D Apache - Enhanced Up Front Display
* more to come....

## Requirements
* [Python 3.10](https://www.python.org/downloads/) but 3.7+ (with tcl/tk support, see installation) should be fine, please choose Windows x86-64 version, file should be python-3.10.1-amd64.exe.  
* [Logitech Gaming Software 9.02.65](https://support.logitech.com/software/lgs)
* [DCS-BIOS 0.7.45](https://github.com/DCSFlightpanels/dcs-bios/releases/latest) (or newer)

**Notes:**
* You do not need Logitech LCD SDK ver. 8.57.148 probably extract to `C:\Program Files\Logitech Gaming Software\LCDSDK_8.57.148`. Since DCSpy version 1.6.0 use built-in SDK in LGS (Logitech Gaming Software), you can safely remove from your system.

## Credits
This project has been heavily inspired by [specelUFC](https://github.com/specel/specelUFC), and I want to thank **specel**, the author of that project for his work and the inspiring ideas. This software uses:
* [DCS-BIOS](https://github.com/DCSFlightpanels/dcs-bios) fork by DCSFlightpanels for exporting data from DCS to local network
* [jboecker's parser](https://github.com/jboecker/python-dcs-bios-example) to read data stream from DCS-BIOS

## Installation
Install all requirements:
1. During Python installation please select  
   * Optional Features:
     * pip
     * tcl/tk and IDLE
     * py launcher  
   * Advanced Options:
     * Associate files with Python (requires the py launcher)
     * Add Python to environment variables
     * Customize install location: **C:\Python310** or **C:\Python**
2. Logitech Gaming Software installation is straightforward.
3. DCS-BIOS
   * You can skip for now and install DCS-BIOS directly from Dcspy (Config -> Check DCS-BIOS). Check **dcsbios** config flag before, see [Configuration](#configuration).  
     It checks if new version exists, download, and unpack DCS-BIOS to `Save Games` folder and check `Export.lua` file.
   * Or follow manual installation [DCS-BIOS wiki page](https://github.com/DCSFlightpanels/DCSFlightpanels/wiki/Installation)
4. Package is available on [PyPI](https://pypi.org/project/dcspy/), open Windows Command Prompt (cmd.exe) and type:
```shell script
pip install dcspy
```
or download manually wheel file from [releases](https://github.com/emcek/dcspy/releases/latest):
```shell script
pip install dcspy-1.6.1-py3-none-any.whl
```
**Note:** If you got `pip is not recognized as an internal or external command, operable program or batch file.` error, see [FAQ](#faq)
## Upgrade
To upgrade DCSpy to the latest version, open Command Prompt and type:
```shell script
pip install -U dcspy
```
**Note:** If you upgrade DCSpy from 1.5.1 or older you can remove Logitech LCD SDK from `C:\Program Files\Logitech Gaming Software\LCDSDK_8.57.148`

## Usage
1. Run Logitech Gaming Software (it allows updating LCD)
2. You can check with `pip uninstall dcspy` (**NOTE!** answer **No** to question) where dcspy was installed. Usually pip should install dcspy into your python directory: i.e.:
   * `c:\python310\dcspy_data\dcspy.ico`
   * `c:\python310\scripts\dcspy.exe`
3. You can drag and drop `dcspy.exe` to desktop and make shortcut (with custom icon, you can find icon in installation directory).
4. Double-click on dcspy icon or type `dcspy.exe` from Command Prompt
5. LCD should update with dcspy basic info, waiting to connect to DCS 
6. Run DCS and start any mission.

## Configuration
DCSpy can be configured via `config.yaml` file. It is located in Python's installation directory (e.g. `c:\python310\dcspy_data\config.yaml`). 
This is simple file, most users do not need to touch it at all. However, it can be easily edited directly from GUI. Configuring DCSpy enable some powerful features of DCSpy.  
Please check **Config** button in GUI. Right now there are available options:  
* **dcsbios** - location of DCS-BIOS folder inside user's `Saved Games\DCS.openbeta`.  
  Set this parameter to correct value allows user check and update DCS-BIOS to the latest release.  
  *example value*: `D:\Users\emcek\Saved Games\DCS.openbeta\Scripts\DCS-BIOS`
* **keyboard** - default Logitech keyboard value, last used value is saved automatically  
  *possible values*: `G19`, `G510`, `G15 v1/v2`, `G13`
* **show_gui** - it allows showing or hiding GUI during start of DCSpy.  
  *possible values*: `true` or `false`
* **font_name** - file name with TrueType font use in all devices
* **font_mono_s** - size of small font for mono devices
* **font_mono_l** - size of large font for mono devices
* **font_color_s** - size of small font for color devices
* **font_color_l** - size of large font for color devices

## Mono vs. Color
DCSpy do not use full potential of G19, which support full RGBA, 8-lines LCD with 7 programmable buttons. In contrast to 
mono devices (like G13, G15 and G510), which support mono, 4-lines LCD with only 4 buttons. Right now DCSpy use only top 
4 lines of LCD and 4 buttons. Way in which actions assign to button for G13 (4 buttons form left to right) are mapped to G19 looks:
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

### F-16C Viper
* IFF MASTER Knob - OFF/STBY/LOW/NORM/EMER
* IFF ENABLE Switch - M1/M3 /OFF/ M3/MS
* IFF M-4 CODE Switch - HOLD/ A/B /ZERO
* IFF MODE 4 REPLY Switch - OUT/A/B

### F-14B Tomcat
* RIO CAP Clear
* RIO CAP SW
* RIO CAP NE
* RIO CAP Enter

### AV-8B N/A Harrier
* UFC COMM1 channel select decrease
* UFC COMM1 channel select increase
* UFC COMM2 channel select decrease
* UFC COMM2 channel select increase

### AH-64D Apache
* IDM Radio Select Rocker Down
* IDM Radio Select Rocker Up
* Radio Transmit Select Rocker Down
* Radio Transmit Select Rocker Up

## FAQ
1. Why in [F-16C DED](https://i.imgur.com/Hr0kmFV.jpg) instead of triangle up and down arrow I see strange character.   
   I didn't find good alternative, so I use unicode character [2666](https://www.fileformat.info/info/unicode/char/2195/index.htm) (I consider [2195](https://www.fileformat.info/info/unicode/char/2195/index.htm) as well, which do not render very well).
2. I got error: `'pip' is not recognized as an internal or external command, operable program or batch file.`  
   Probably during installation of Python `pip` and/or `Add Python to environment variables` were not selected. Uninstall Python and install again with correct options, or consider add Python installation directory to PATH environment variable.
3. Python 3.6 not supported due to 3 known vulnerabilities in Pillow library (version 9.0.0 drop support for Python 3.6)

| Name   | Version | ID            | Fix Versions |
|--------| --------|---------------|--------------|
| pillow | 8.4.0   | PYSEC-2022-10 | 9.0.0        |
| pillow | 8.4.0   | PYSEC-2022-9  | 9.0.0        |
| pillow | 8.4.0   | PYSEC-2022-8  | 9.0.0        |

## New ideas
I have lots of plans and new ideas how to improve it internally and form user's perspective, but don't hesitate to contact me. Maybe it will motivate me to implement some new stuff. Please open issue if you find bug or have any crazy idea.  
You are welcome [dcspy Discord](https://discord.gg/SP5Yjx3) server. 

## Contributing
You want contribute, perfect see: [contributing](./CONTRIBUTING.md) guide.
