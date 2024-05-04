## Development
DCSpy uses multicast UDP to receive/send data from/to the DCS-BIOS, as describe [here](https://github.com/DCS-Skunkworks/dcs-bios/blob/master/Scripts/DCS-BIOS/doc/developerguide.adoc)
Main modules of DCSpy:
* `run.py` main script: it starts GUI in Qt6/PySide6
* `starter.py` responsible to initialise DCS-BIOS parser, Logitech G13/G15/G510 Mono handler and G19 Color handler, as well as running connection to DCS
* `log.py` dumb simple logger configuration
* `logitech.py` handling Logitech keyboards with LCD and buttons, loading dynamically aircraft used in DCS
* `aircraft.py` define all supported aircraft with details how and what display from DCS, draws bitmap that will be passed to LCD keyboard handler and returns input data for buttons
* `dcsbios.py` BIOS protocol parser and two buffers to fetching integer and string values `IntegerBuffer` and `StringBuffer` respectively.
* `qt_gui.py` GUI with widgets, layouts and events. It allows configuring DCSpy as well
* `utils.py` various useful tools - load and save config, check an online version, download file, update DCS-BIOS using git, etc.
* `models.py` pydantic models of internal data structures, some additional enums and other types definition used across DCSpy
* `sdk` python interface for Logitech C/C++ libraries to access keyboard LCD, G-keys and LED backlight
