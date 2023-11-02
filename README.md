[![image](https://img.shields.io/badge/pypi-v3.0.0-blue.svg)](https://pypi.org/project/dcspy/)
[![Python CI](https://github.com/emcek/dcspy/actions/workflows/python-ci.yml/badge.svg?branch=master)](https://github.com/emcek/dcspy/actions/workflows/python-ci.yml)
[![Coverage Status](https://coveralls.io/repos/github/emcek/dcspy/badge.svg?branch=master)](https://coveralls.io/github/emcek/dcspy?branch=master)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/5270a4fc2ba24261a3bfa7361150e8ff)](https://app.codacy.com/gh/emcek/dcspy/dashboard?utm_source=gh&utm_medium=referral&utm_content=&utm_campaign=Badge_grade)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](./LICENSE.md)
[![Downloads](https://img.shields.io/github/downloads/emcek/dcspy/total?label=Downloads)](https://github.com/emcek/dcspy/releases)
[![dcspy](https://snyk.io/advisor/python/dcspy/badge.svg)](https://snyk.io/advisor/python/dcspy)
[![Patreon](https://img.shields.io/badge/Patreon-donate-ff424d?logo=patreon)](https://www.patreon.com/mplichta)
[![Discord](https://img.shields.io/discord/672486999516774442?label=Discord&logo=discord&logoColor=lightblue)](https://discord.gg/SP5Yjx3)
[![image](https://img.shields.io/badge/python-3.8%20%7C%203.9%20%7C%203.10%20%7C%203.11%20%7C%203.12-blue.svg)](https://github.com/emcek/dcspy)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/emcek/dcspy/master.svg)](https://results.pre-commit.ci/latest/github/emcek/dcspy/master)
[![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=emcek_dcspy&metric=sqale_rating)](https://sonarcloud.io/dashboard?id=emcek_dcspy)
[![CII Best Practices](https://bestpractices.coreinfrastructure.org/projects/6056/badge)](https://bestpractices.coreinfrastructure.org/projects/6056)
[![Downloads](https://static.pepy.tech/badge/dcspy)](https://pepy.tech/project/dcspy)
[![Rate this package](https://badges.openbase.com/python/rating/dcspy.svg?token=AZCVj1Hdbl6cC3I/gkVpgsigp22LtCOR0sB8lcODY9Y=)](https://openbase.com/python/dcspy?utm_source=embedded&amp;utm_medium=badge&amp;utm_campaign=rate-badge)

![dcspylogo](https://i.imgur.com/eqqrPB8.jpg)
## DCSpy
DCSpy is able to pull information from DCS aircraft and display on Logitech G-series keyboards LCD.
Features:
* Logitech device with 160x43 px (4 lines) monochrome LCD - **G13**, **G15 (v1 and v2)** and **G510**
* Logitech device with 320x240 px (8 lines) full RGBA LCD - **G19**
* Setup G-Keys to any toggle, switch or knob in cockpit
* Support for all aircraft (official and mods) with clickable cockpits - [DCS-BIOS aircraft](https://github.com/DCS-Skunkworks/dcs-bios#is-my-aircraft-supported)
* Modern looking GUI using Qt6/PySide6

See more information on [Wiki](https://github.com/emcek/dcspy/wiki) page.

## Aircraft and instruments
There are to kinds of supported aircraft:
* **Basic** - allow to assign all G-Keys of Logitech keyboard to aircraft's instruments in cockpit (all clickable cockpits supported by DCS-BIOS)
* **Advanced** - additionally can display some information on LCD (listed below)

Why such way? Basically advanced support is for aircraft which I own and therefore can test it.

# Advanced
* F/A-18C Hornet UFC - Up Front Controller
* F-16C Viper DED - Data Entry Display
* Ka-50 Black Shark II and III - PVI-800 and autopilot channels
* Mi-8MTV2 Hip - autopilot channels and Radios information
* Mi-24P Hind - Autopilot channels and modes and Radios information
* A-10C Warthog and A-10C II Tank Killer - Radio frequency information
* F-14A and F-14B Tomcat - basic support for RIO CAP
* AV-8B Night Attack Harrier - Up Front Controller and Option Display Unit
* AH-64D Apache - Enhanced Up Front Display
* F-15E Eagle - Upfront Control Panel
* more to come....

## Requirements
* [Logitech Gaming Software 9.04.49](https://support.logitech.com/software/lgs)
* [Git](https://git-scm.com/download/win) it is necessary for using live version of DCS-BIOS, see [Live DCS-BIOS](https://github.com/emcek/dcspy/wiki/Information#live-dcs-bios))
* [DCS-BIOS 0.7.50](https://github.com/DCS-Skunkworks/dcs-bios/releases/latest) or newer (can be installed directly from DCSpy)
* DCS World: [2.9.0.46801](https://www.digitalcombatsimulator.com/en/news/changelog/openbeta/2.9.0.46801/) Open Beta
* (optional) [Python 3.12](https://www.python.org/downloads/) but 3.8+ should be fine (see [installation](https://github.com/emcek/dcspy/wiki/installation))

**Notes:**
* If you upgrade DCSpy from 1.5.1 or older you can safely remove Logitech LCD SDK from `C:\Program Files\Logitech Gaming Software\LCDSDK_8.57.148`. Since DCSpy version 1.6.0 use built-in SDK in LGS (Logitech Gaming Software).

## New ideas
I have lots of plans and new ideas how to improve it internally and form user's perspective, but don't hesitate to contact me. Maybe it will motivate me to implement some new stuff. Please open issue if you find bug or have any crazy idea.
You are welcome [dcspy Discord](https://discord.gg/SP5Yjx3) server.

## Contributing
You want contribute, perfect see: [contributing](./CONTRIBUTING.md) guide.

## Credits
More details [here](https://github.com/emcek/dcspy/wiki/Information#credits).

## Sponsored by Jetbrains Open Source Support Program
[![logo](https://resources.jetbrains.com/storage/products/company/brand/logos/PyCharm.svg)](https://jb.gg/OpenSourceSupport)
[![logo](https://resources.jetbrains.com/storage/products/company/brand/logos/jb_beam.svg)](https://jb.gg/OpenSourceSupport)
