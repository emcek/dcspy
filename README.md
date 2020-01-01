[![image](https://img.shields.io/badge/pypi-v0.9.0-blue.svg)](https://pypi.org/project/dcspy/)
[![Build Status](https://travis-ci.org/emcek/specelUFC.svg?branch=master)](https://travis-ci.org/emcek/specelUFC)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/4be48a777921491896a0ed8de9a73e05)](https://www.codacy.com/manual/mplichta/dcspy?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=emcek/dcspy&amp;utm_campaign=Badge_Grade)
[![BCH compliance](https://bettercodehub.com/edge/badge/emcek/dcspy?branch=master)](https://bettercodehub.com/)
[![image](https://img.shields.io/badge/python-3.6%20%7C%203.7%20%7C%203.8-blue.svg)](https://github.com/emcek/dcspy)
[![License](https://img.shields.io/badge/Licence-MIT-blue.svg)](./LICENSE)

# dcspy
This is a software designed to put information from DCS aircraft to Logitech G-series keyboards. Developed for **Logitech G13**, but should also work with any other Logitech device with 160x43 px monochrome display, like G15 and G510.
* F/A-18C Hornet's Up Front Controller (UFC)
* F-16C DED display - some parts are missing
* Ka-50 PVI-800 - under development

![dcspylogo](https://i.imgur.com/eqqrPB8.jpg)

## Requirements
* Installed Python 3.8 (but 3.6 should be fine) <https://www.python.org/downloads/>
* Installed Logitech Gaming Software 9.02.65 <https://support.logitech.com/software/lgs>
* Installed Logitech LCD SDK 8.57.148 in `C:\Program Files\Logitech Gaming Software\LCDSDK_8.57.148` <http://gaming.logitech.com/sdk/LCDSDK_8.57.148.zip>
* DCS-BIOS 0.7.31 (or newer) <https://github.com/DCSFlightpanels/dcs-bios>

## Credits
This project has been heavily inspired by [specelUFC](https://github.com/specel/specelUFC), and I want to thank **specel**, the author of that project for his work and the inspiring ideas. This software uses:
* <https://github.com/DCSFlightpanels/dcs-bios> DCS-BIOS fork by DCSFlightpanels for exporting data from DCS to local network
* <https://github.com/jboecker/python-dcs-bios-example> jboecker's parser to read data stream from DCS-BIOS
* <https://github.com/50thomatoes50/GLCD_SDK.py> A Python wrapper for Logitech's LCD SDK (with my minor modifications)

## Changelog
### 0.9.0
* based on version [specelUFC v1.12.1](https://github.com/specel/specelUFC/releases/tag/v1.12.1)
* added basic handling for Ka-50 PVI-800 data are received but not formatted properly
* F-16C DED should working but not 4 buttons under LCD  - I don't have it so it is hard to test
* G13 handler detect 32/64 bit of Python and load correct version of LCD Logitech C library
* adding basic logging for debugging - prints on console 
* all defined aircraft are detected and loaded on-the-fly during operation
* define new plane should be easy just use `AircraftHandle` as base class
* Python LCD SDK was clean-up
* other refactorings and code duplication removal 

## Usage
You can use it straight away, by running `dcs_g13.py`, it can be run before DCS, as well as after. After successful connect attempt, G13 display should update. 

* `dcs_g13.py` is responsible for initialise parser, G13 handler, as well as running connection with DCS.
* `logitech.py` is responsible for initialise aircraft specific file and handling G13 display and buttons
* `aircrafts.py` are define all supported aircrafts with details how to handle and display data from DCS, draws bitmap that will be passed to G13 handler and returns input data for buttons under G13 display

If you want to modify or write something by yourself, here's a quick walkthrough:

* First, you need to "subscribe" data you want and pass it to G13Handler:
```python
bufferScratchpadStr1 = StringBuffer(self.g13.parser, 0x744e, 2, lambda s: self.set_data('ScratchpadStr1', s))
```
For required address and data length, look up in `C:\Users\xxx\Saved Games\DCS.openbeta\Scripts\DCS-BIOS\doc\control-reference.html`

* Then, receive byte and use parser:
```python
c = s.recv(1)
parser.processByte(c)
```
which calls back function in G13Handler `set_data(...)` with appropriate parameters and update display content, by creating bitmap and passing it through LCD SDK to device display

* You can also use 4 button below display, just check their state with `g13.check_buttons()` which one is pressed and send packet with command you wish to use. Again, look it up in `control-reference.html`, for example, to rotate COMM1 knob right in F/A-18C:
```python
s.send(bytes('UFC_COMM1_CHANNEL_SELECT INC\n', 'utf-8'))
```

## New ideas
I have lots of plans and new ideas how to improve it internally and form user's perspective, but don't hesitate to contact me. Maybe it will motivate me to implement some new stuff. Please open issue if you find bug or have any crazy idea. 
