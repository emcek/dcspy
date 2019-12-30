[![Build Status](https://travis-ci.org/emcek/specelUFC.svg?branch=master)](https://travis-ci.org/emcek/specelUFC)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/028d23a12d5345b7bbeece49860a7992)](https://www.codacy.com/manual/mplichta/specelUFC?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=emcek/specelUFC&amp;utm_campaign=Badge_Grade)
[![BCH compliance](https://bettercodehub.com/edge/badge/emcek/specelUFC?branch=master)](https://bettercodehub.com/)

# specelUFC
This is a software designed to put information from DCS:FA18C Hornet's Up Front Controller (UFC) and F-16C DED display to Logitech G-series keyboards. Developed for **Logitech G13**, but should also work with any other Logitech device with 160x43 px monchrome display, like G15 and G510.

<p align="center">
  <img src="https://i.imgur.com/PK8qdG4.jpg" width="350" title="hover text">
</p>

## Requirements
  * Installed Python 3.x https://www.python.org/downloads/

  * Installed Logitech Gaming Software https://support.logitech.com/software/lgs

  * Installed Logitech LCD SDK_8.57.148 in `C:\Program Files\Logitech Gaming Software\LCDSDK_8.57.148` http://gaming.logitech.com/sdk/LCDSDK_8.57.148.zip

  * DCS-BIOS https://github.com/DCSFlightpanels/dcs-bios (version required 0.7.31)copied into `C:\Users\XXX\Saved Games\DCS.openbeta\Scripts`. You also need to add ```dofile(lfs.writedir()..[[Scripts\DCS-BIOS\BIOS.lua]])``` line to your `C:\Users\XXX\Saved Games\DCS.openbeta\Scripts\Export.lua` file

## Credits
This software uses:
  * https://github.com/DCSFlightpanels/dcs-bios DCS-BIOS fork by DCSFlightpanels for exporting data from DCS to local network (version required 0.7.31)
  * Matchstick's script for exportind DED over DCS-BIOS 
  * https://github.com/jboecker/python-dcs-bios-example jboecker's parser to read data stream from DCS-BIOS
  * https://github.com/50thomatoes50/GLCD_SDK.py A Python wrapper for Logitech's LCD SDK

## Changelog
### v1.12
  * Added - specelUFC will now export F-16C Data Entry Display (DED) on screen - for now it is required to copy custom .lua script into `Scripts\DCS-BIOS\lib`
  * Changed - specelUFC will by now based on **DCSFlightpanels/dcs-bios**

### v1.11
  * Added - Update checker will check is there a newer version od this software
### v1.1
  * Added - Aircraft detection. Software now detects active aircraft and will load specific handlers, not only FA-18C
  * Fixed - After disconnect from server or leaving current mission, software will reset itself and wait for new connection
### v1.0 
  * initial release

## Usage
You can use it straight away, by running `./dist/specelUFC.exe` (or, if you prefer, `specelUFC.py`), it's fully functional and can be run before DCS, as well as after. After succesful connect attemption, G13 display should show data as in picture. 

  * `specelUFC.py` is responsible for initialise parser, G13 handler, as well as running connection with DCS.
  * `specelG13Handler.py` is responsible for initialise aircraft specific file (only F/A18 for now) and handling G13 display and buttons
  * `specelFA18Handler` "subscribes" aircraft data by creating stringbuffers and reading their values, draws bitmap that will be passed to G13 handler and returns input data for buttons under G13 display

If you want to modify or write something by yourself, here's a quick walkthrough:

  * First, you need to "subscribe" data you want and pass it to G13Handler: 
```
ScratchpadNumberDisplay = StringBuffer(parser, 0x543e, 8, lambda s: g13.setData(3,s))
```
For required adress and data length, look up in `C:\Users\XXX\Saved Games\DCS.openbeta\Scripts\DCS-BIOS\doc\control-reference.html`

  * Then, receive byte and use parser 
```
c = s.recv(1)
parser.processByte(c)
```
which calls back function in G13Handler `setData(...)` with apropriate paramteres and update display content, by creating bitmap and passing it through LCD SDK to device display

  * You can also use 4 button below display, just checktheir state with `g13.checkButtons()` which one is pressed and send TCP packet with command you wish to use. Again, look it up in `control-reference.html`, for example `s.send(bytes("UFC_COMM1_CHANNEL_SELECT -3200\n","utf-8"))` to rotate COMM1 knob left
