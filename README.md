[![image](https://img.shields.io/badge/pypi-v1.7.0-blue.svg)](https://pypi.org/project/dcspy/)
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
* Logitech device with 160x43 px (4 lines) monochrome LCD - **G13**, **G15 (v1 and v2)** and **G510**
* Logitech device with 320x240 px (8 lines) full RGBA LCD - **G19**

See more information on [Wiki](https://github.com/emcek/dcspy/wiki) page.

## Sponsored by Jetbrains Open Source Support Program
[![logo](https://resources.jetbrains.com/storage/products/company/brand/logos/PyCharm.svg)](https://jb.gg/OpenSourceSupport)
[![logo](https://resources.jetbrains.com/storage/products/company/brand/logos/jb_beam.svg)](https://jb.gg/OpenSourceSupport)

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
* [Python 3.10](https://www.python.org/downloads/) but 3.7+ (with tcl/tk support, see installation) should be fine, please choose Windows x86-64 version, file should be python-3.10.5-amd64.exe.  
* [Logitech Gaming Software 9.04.49](https://support.logitech.com/software/lgs)
* [DCS-BIOS 0.7.45](https://github.com/DCSFlightpanels/dcs-bios/releases/latest) (or newer)

**Notes:**
* If you upgrade DCSpy from 1.5.1 or older you can safely remove Logitech LCD SDK from `C:\Program Files\Logitech Gaming Software\LCDSDK_8.57.148`. Since DCSpy version 1.6.0 use built-in SDK in LGS (Logitech Gaming Software).

## New ideas
I have lots of plans and new ideas how to improve it internally and form user's perspective, but don't hesitate to contact me. Maybe it will motivate me to implement some new stuff. Please open issue if you find bug or have any crazy idea.  
You are welcome [dcspy Discord](https://discord.gg/SP5Yjx3) server. 

## Contributing
You want contribute, perfect see: [contributing](./CONTRIBUTING.md) guide.
