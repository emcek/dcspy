[![image](https://img.shields.io/badge/pypi-v0.9.2-blue.svg)](https://pypi.org/project/dcspy/)
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
There is possibility to modify this package to use full RGBA LCD of Logitech G19 (size 320x240) - please open issue.  

## Currently supported devices and aircrafts
* F/A-18C Hornet UFC - Up Front Controller
* F-16C Viper DED - Data Entry Display (some parts are missing)
* Ka-50 Black Shark PVI-800 (under development)

## Table of Contents
* [Requirements](#requirements)
* [Credits](#credits)
* [Installation](#installation)
* [Usage](#usage)
* [New ideas](#new-ideas)
* [Development](#development)

## Requirements
* Installed Python 3.8 (but 3.6+ should be fine) <https://www.python.org/downloads/>
* Installed Logitech Gaming Software 9.02.65 <https://support.logitech.com/software/lgs>
* Installed Logitech LCD SDK 8.57.148 in `C:\Program Files\Logitech Gaming Software\LCDSDK_8.57.148` <http://gaming.logitech.com/sdk/LCDSDK_8.57.148.zip>
* DCS-BIOS 0.7.31 (or newer) <https://github.com/DCSFlightpanels/dcs-bios>

## Credits
This project has been heavily inspired by [specelUFC](https://github.com/specel/specelUFC), and I want to thank **specel**, the author of that project for his work and the inspiring ideas. This software uses:
* <https://github.com/DCSFlightpanels/dcs-bios> DCS-BIOS fork by DCSFlightpanels for exporting data from DCS to local network
* <https://github.com/jboecker/python-dcs-bios-example> jboecker's parser to read data stream from DCS-BIOS

## Installation
Package is available on [PyPI](https://pypi.org/project/dcspy/), open Command Prompt and type:
```shell script
pip install dcspy
```
or use attached wheel file:
```shell script
pip install dcspy-0.9.2-py3-none-any.whl
```

## Usage
pip should install into you python installation directory: i.e.:
* `d:\python38\dcspy_data\dcspy.ico`
* `d:\python38\scripts\dcspy.exe`

You can drag and drop `dcspy.exe` to desktop and make shortcut (with custom icon).
After successful connect attempt, G13 display should update. 

## New ideas
I have lots of plans and new ideas how to improve it internally and form user's perspective, but don't hesitate to contact me. Maybe it will motivate me to implement some new stuff. Please open issue if you find bug or have any crazy idea. 

## Development
* `dcspy.py` is responsible for initialise parser, G13 handler, as well as running connection with DCS.
* `logitech.py` is responsible for initialise aircraft specific file and handling G13 display and buttons
* `aircrafts.py` are define all supported aircrafts with details how to handle and display data from DCS, draws bitmap that will be passed to G13 handler and returns input data for buttons under G13 display

If you want to modify or write something by yourself, here's a quick walkthrough:
* Each plan has special dict:
```python
BIOS_VALUE = TypedDict('BIOS_VALUE', {'addr': int, 'len': int, 'val': str})
self.bios_data: Dict[str, BIOS_VALUE] = {
    'ScratchpadStr1': {'addr': 0x744e, 'len': 2, 'val': ''},
    'FuelTotal': {'addr': 0x748a, 'len': 6, 'val': ''}}
```
which describe data to be fetch from DCS-BIOS. For required address and data length, look up in `C:\Users\xxx\Saved Games\DCS.openbeta\Scripts\DCS-BIOS\doc\control-reference.html`
* Then after detecting current plane in DCS, G13 will load instance of aircraft as `plane`
```python
self.plane: Aircraft = getattr(import_module('dcspy.aircrafts'), self.plane_name)(self.g13_lcd.width, self.g13_lcd.height)
```
* and "subscribe" for changes with callback for all fields defined in `plane` instance
```python
for field_name, proto_data in self.plane.bios_data.items():
    StringBuffer(self.parser, proto_data['addr'], proto_data['len'], partial(self.plane.set_bios, field_name))
```
* when, receive byte, parser will process data:
```python
dcs_bios_resp = sock.recv(1)
parser.process_byte(dcs_bios_resp)
```
and calls callback function `set_bios()` of current `plane` with received value and update display content, by creating bitmap and passing it through LCD SDK to device display.

* You can also use 4 button below LCD display, just check their state with `g13.check_buttons()` which one is pressed and send request do DCS-BIOS.
```python
sock.send(bytes(self.plane.button_request(button), 'utf-8'))
```
* Correct action is define in aircraft instance `button_request()` method:
```python
action = {1: 'UFC_COMM1_CHANNEL_SELECT DEC',
          2: 'UFC_COMM1_CHANNEL_SELECT INC',
          3: 'UFC_COMM2_CHANNEL_SELECT DEC',
          4: 'UFC_COMM2_CHANNEL_SELECT INC'}
return f'{action[button]}\n'
```
Again, look it up in `control-reference.html`, in example above, COMM1 and COMM2 knobs of F/A-18C will rotate left and right.
