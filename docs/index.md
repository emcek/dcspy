## DCSpy
DCSpy is able to pull information from DCS aircraft and display on Logitech G-series keyboards LCD.

Features:

* Logitech device with 160x43 px (4 lines) monochrome LCD - **G13**, **G15 (v1 and v2)** and **G510**
* Logitech device with 320x240 px (8 lines) full RGBA LCD - **G19**
* Support for other [Logitech devices](https://github.com/emcek/dcspy/wiki/Supported-devices):
    * Keyboards: **G910**, **G710**, **G110**, **G105**, **G103**, **G11**
    * Headphones: **G35**, **G633**, **G930**, **G933**
    * Mouses: **G600**, **G300**, **G400**, **G700**, **G9**, **MX518**, **G402**, **G502**, **G602**
* Setup G-Keys to any toggle, switch or knob in cockpit - [Setup of G-Keys](https://github.com/emcek/dcspy/wiki/Usage#how-to-setup)
* Support for all aircraft (official and mods) with clickable cockpits - [DCS-BIOS aircraft](https://github.com/DCS-Skunkworks/dcs-bios#is-my-aircraft-supported)
* Modern looking GUI using Qt6/PySide6

## Aircraft and instruments
There are to kinds of supported aircraft:
* **Basic** - allow assigning all G-Keys of Logitech devices to aircraft's instruments in the cockpit (all clickable cockpits supported by DCS-BIOS)
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

See more information on [Wiki](https://github.com/emcek/dcspy/wiki) page.
