[![image](https://img.shields.io/badge/pypi-v3.6.3-blue.svg)](https://pypi.org/project/dcspy/)
[![Python CI](https://github.com/emcek/dcspy/actions/workflows/python-ci.yml/badge.svg?branch=master)](https://github.com/emcek/dcspy/actions/workflows/python-ci.yml)
[![Coverage Status](https://coveralls.io/repos/github/emcek/dcspy/badge.svg?branch=master)](https://coveralls.io/github/emcek/dcspy?branch=master)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/5270a4fc2ba24261a3bfa7361150e8ff)](https://app.codacy.com/gh/emcek/dcspy/dashboard?utm_source=gh&utm_medium=referral&utm_content=&utm_campaign=Badge_grade)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](./LICENSE.md)
[![Downloads](https://img.shields.io/github/downloads/emcek/dcspy/total?label=Downloads)](https://github.com/emcek/dcspy/releases)
[![dcspy](https://snyk.io/advisor/python/dcspy/badge.svg)](https://snyk.io/advisor/python/dcspy)
[![Patreon](https://img.shields.io/badge/Patreon-donate-ff424d?logo=patreon)](https://www.patreon.com/mplichta)
[![Discord](https://img.shields.io/discord/672486999516774442?label=Discord&logo=discord&logoColor=lightblue)](https://discord.gg/SP5Yjx3)
[![image](https://img.shields.io/badge/python-3.9%20%7C%203.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue.svg)](https://github.com/emcek/dcspy)
[![CodSpeed Badge](https://img.shields.io/endpoint?url=https://codspeed.io/badge.json)](https://codspeed.io/emcek/dcspy)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/emcek/dcspy/master.svg)](https://results.pre-commit.ci/latest/github/emcek/dcspy/master)
[![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=emcek_dcspy&metric=sqale_rating)](https://sonarcloud.io/dashboard?id=emcek_dcspy)
[![Downloads](https://static.pepy.tech/badge/dcspy)](https://pepy.tech/project/dcspy)

![dcspylogo](https://i.imgur.com/eqqrPB8.jpg)
## DCSpy
DCSpy is able to pull information from DCS aircraft and display on Logitech G-series keyboards LCD.

Features:
* Logitech device with 160x43 px four (4) lines monochrome LCD - **G13**, **G15 (v1 and v2)** and **G510**
* Logitech device with 320x240 px eight (8) lines full RGBA LCD - **G19**
* Support for other [Logitech devices](https://dcspy.readthedocs.io/en/latest/devices/):
  * Keyboards: **G910**, **G710**, **G110**, **G105**, **G103**, **G11**
  * Headphones: **G35**, **G633**, **G930**, **G933**
  * Mouses: **G600**, **G300**, **G400**, **G700**, **G9**, **MX518**, **G402**, **G502**, **G602**
* Setup G-Keys to any toggle, switch or knob in cockpit - [Setup of G-Keys](https://dcspy.readthedocs.io/en/latest/usage/#how-to-setup)
* Support for all aircraft (official and mods) with clickable cockpits - [DCS-BIOS aircraft](https://github.com/DCS-Skunkworks/dcs-bios?tab=readme-ov-file#modules)
* Modern looking GUI using Qt6/PySide6

See more information on [documentation](https://dcspy.readthedocs.io/en/latest/) page.

## Aircraft and instruments
There are to kinds of supported aircraft:
* **Basic** - allow assigning all G-Keys of Logitech keyboard to aircraft's instruments in the cockpit (all clickable cockpits supported by DCS-BIOS)
* **Advanced** - additionally can display some information on LCD (listed below)

Why a such way? Basically advanced support is for aircraft that I own and therefore can test it.

# Advanced
* F/A-18C Hornet UFC - Up Front Controller
* F-16C Viper DED - Data Entry Display
* Ka-50 Black Shark II / III - PVI-800 and autopilot channels
* Mi-8MTV2 Hip - autopilot channels and Radio information
* Mi-24P Hind - Autopilot channels and modes and Radio information
* A-10C Warthog / A-10C II Tank Killer - Radio frequency information
* F-14A / F-14B Tomcat - basic support for RIO CAP
* AV-8B Night Attack Harrier - Up Front Controller and Option Display Unit
* AH-64D Apache - Enhanced Up Front Display (EUFD)
* F-15E Eagle - Upfront Control Panel
* F-4 Phantom II - UHF (ARC 164) Radio
* more to come...

## Requirements
* [Logitech Gaming Software 9.04.49](https://support.logitech.com/software/lgs)
* DCS-Skunkworks DCS-BIOS:
  * [DCS-BIOS 0.8.3](https://github.com/DCS-Skunkworks/dcs-bios/releases/tag/v0.8.3) or newer (can be [installed](https://dcspy.readthedocs.io/en/latest/upgrade/#manual-procedure) directly from DCSpy)
  * However, it is recommended to use [Live DCS-BIOS](https://dcspy.readthedocs.io/en/latest/bios_live/) latest git version
  * [Git](https://git-scm.com/download/win) it is necessary to use the live version of DCS-BIOS
* DCS World: [2.9.12.5336.1](https://www.digitalcombatsimulator.com/en/news/changelog/stable/2.9.12.5336.1/), but any version from 2.9.* branch should be fine.
* optional:
  * [Python 3.13](https://www.python.org/downloads/) but 3.9+ should be fine (see [installation](https://dcspy.readthedocs.io/en/latest/install/))

## New ideas
I have lots of plans and new ideas how to improve it internally and form a user's perspective, but don't hesitate to contact me. Maybe it will motivate me to implement some new stuff. Please open issue if you find a bug or have any crazy idea.
You are welcome [dcspy discord](https://discord.gg/SP5Yjx3) server.

## Contributing
You want to contribute, perfect see: [contributing](./CONTRIBUTING.md) guide.

## Credits
More details [here](https://dcspy.readthedocs.io/en/latest/credits/).

## Sponsored by Jetbrains Open Source Support Program
[![logo](https://resources.jetbrains.com/storage/products/company/brand/logos/PyCharm.svg)](https://jb.gg/OpenSourceSupport)
[![logo](https://resources.jetbrains.com/storage/products/company/brand/logos/jb_beam.svg)](https://jb.gg/OpenSourceSupport)
