## 2.0.0
* Allow use/update DCS-BIOS directly from GitHub (master branch)
* Allow run DCSpy without console
* Internal:
  * improve type checking
  * verbose setting will impact both console and file logs

## 1.9.5
* Support for **Mi-8MTV2 Magnificent Eight**
  * Autopilot Channels (Heading, Pitch/Bank and Altitude)
  * Radios: R868, R828, YADRO1A information
* Support for **Mi-24P Hind**
  * Autopilot Channels (Yaw, Roll, Pitch and Altitude)
  * Autopilot Modes (Hover, Route and Altitude)
  * Radios: R868, R828, YADRO1I information
* Add About tab with basic information
* **F-16C Viper**:
  * Add spacial font for DED (G19 only)
  * Clean some extra characters from DED
* Internal:
  * force update customtkinter to at least 5.1.0

## 1.8.1
* Add support for **Ka-50 Black Shark III**
* Update footer when checking DCS-BIOS version
* Align with DCS 2.8.1.34667.2 and DCS-BIOS 0.7.47
* Internal:
  * add more unit tests
  * mark some test as DCS-BIOS tests

## 1.8.0
* Major GUI redesign using `customtkinter` package, which provides new, modern widgets:
  * Appearance system mode (`Light`, `Dark`)
  * Three colort theme (`Green`, `Blue` and `Dark Blue`)
  * All settings are configured from GUI vie widgets
  * One window for all configuration and buttons
  * Check version from GUI
  * Add configuration flag to check for new version during start

## 1.7.5
* report DCS stable version correctly in logs during start
* Internal:
  * rename starting script
  * remove usage of McCabe
  * add unit tests

## 1.7.4
* **AH-64D Apache**
  * add better support for G19 for PRE mode
  * update name from `AH64D` to `AH64DBLKII`
* Show DCS version in logs
* Fix name of plane for **F-14 Tomcat** depending on model A or B
* Toggle Start/Stop buttons
* Do not show warning when plane's name is empty
* Internal:
  * improve checking DCS-BIOS data
  * introduce enum values for parser state
  * improve CI process - add Python 3.11
  * force using Pillow 9.3.0

## 1.7.3
* Align **F-16C Viper** DED and **AH-64D Apache** EUFD with DCS-BIOS 0.7.46 changes
* Basic support for **F-14A Tomcat**

## 1.7.2
* **AH-64D Apache**
  * update name from `AH64DBLKII` to `AH64D`
  * fix display PRE mode for G19
  * fix handling buttons
* Internal:
  * update unit test for better coverage and more use-cases

## 1.7.1
* New config settings:
  * `auto_start` - run DCSpy atomically after start
  * `verbose` - show more logs in terminal/console window
* Fixing handling of `dcsbios` settings from `config.yaml`
* Start and stop buttons can be used several times without closing GUI
* **F-16C Viper**
  * replace `*` with inverse white circle character at DED
  * Fix unhandled buttons for G19 (menu, ok and cancel)
* G19 and **F/A-18C Hornet**
  * Push **Menu** and **Cancel** toggle cockpit button down, push it again toggles button up (Integrated Fuel/Engine Indicator - IFEI).
  * Add handling **Ok** as Attitude Selector Switch, INS/AUTO/STBY
* Internal:
  * use Pythonic way using temporary directory
  * speed-up tests - cache json files instead of downloading from internet
  * use Enum for LCD type
  * use Enum for LCD buttons, add to LcdInfo dataclass

## 1.7.0
* Support for **AH-64D Apache** with 3 modes:
  * `IDM` - Squeeze and shows radios frequencies (from Radio Area), IDM and RTS rocker are used to scroll down
  * `WCA` - Enter button display warnings, cautions, and advisories, WCA rocker is used to scroll down
  * `PRE` - Preset button displays the preset menu for the selected radio, WCA rocker is used to scroll down
* **F-16C Viper** DED clean-up extra characters

## 1.6.1
* Update **F-16C Viper** for latest DSC-BIOS (0.7.45)
* Fresh installation of DCS-BIOS is painless
* Drop support for Python 3.6

## 1.6.0
* use fonts in dynamic way - you can customize fonts in `config.yaml` file (see [Configuration](https://github.com/emcek/dcspy#configuration))
* usage for LCD SDK built-in LGS - no need additional package for usage
* support for Python 3.10 (use `dataclasses` internally)
* ability to stop DCSpy from GUI
* supporters are printed in welcome screen - I'm thrilled with support and help of community!

## 1.5.1
* alignment for new DCS-BIOS [v0.7.43](https://github.com/DCSFlightpanels/dcs-bios/releases/tag/v0.7.43)

## 1.5.0
* Support for **AV-8B N/A Harrier** with:
  * **UFC** - Up Front Controller
  * **ODU** - Option Display Unit
  * **decrease UFC Comm 1 Channel** - G13 1st button or G19 left button
  * **increase UFC Comm 1 Channel** - G13 2nd button or G19 right button
  * **decrease UFC Comm 2 Channel** - G13 3rd button or G19 down button
  * **increase UFC Comm 2 Channel** - G13 4th button or G19 up button

## 1.4.0
* Configuration editor:
  * **dcsbios** - set default Logitech keyboard: "G19", "G510", "G15 v1/v2", "G13"
  * **show_gui** - showing or hiding GUI during start of DCSpy
  * **dcsbios** - location of DCS-BIOS folder inside user's Saved Games
* Check and update DCS-BIOS directly from DCSpy
  * **Check DCS-BIOS** button in **Config** editor
  * **dcsbios** needs to be set to correct value
* Basic A-10C Warthog and A-10C II Tank Killer support

## 1.3.0
* **F-16C Viper** use 4 buttons for IFF
  * **IFF MASTER Knob** - OFF/STBY/LOW/NORM/EMER
  * **IFF ENABLE Switch** - M1/M3 /OFF/ M3/MS
  * **IFF M-4 CODE Switch** - HOLD/ A/B /ZERO
  * **IFF MODE 4 REPLY Switch** - OUT/A/B
* Fix alignment of (DCS-BIOS [v0.7.41](https://github.com/DCSFlightpanels/dcs-bios/releases/tag/v0.7.41)) for **F-14B Tomcat**
* Internally all data fetch form DCS-BIOS is check against its specification. Sometimes due to changes DCS-BIOS protocol DCSpy couldn't fetch all data i.e. F-16 DED. It shouldn't happened anymore.

## 1.2.3
* Fix alignment of DED (DCS-BIOS [v0.7.41](https://github.com/DCSFlightpanels/dcs-bios/releases/tag/v0.7.43)) for **F-16C Viper**

## 1.2.2
* Fix alignment of DED for **F-16C Viper**
* Fix position of Integrated Fuel/Engine Indicator (IFEI) for **F/A-18C Hornet** (only G19)

## 1.2.1
* **F/A-18C Hornet** shows extra Total Internal Fuel (G19 only)
* Internal refactoring

## 1.2.0
* Simple Tkinter GUI - to select your Logitech keyboard
* Support for G19 - Big thanks for **BrotherBloat** who makes this release possible. He spent countless hours to share his G19 and let me troubleshoot remotely.
* **F/A-18C Hornet** shows Total Fuel instead of Total Internal Fuel

## 1.1.1
* Basic support for **F-14B Tomcat** RIO CAP (Computer Address Panel):
  * **CLEAR** - button 1
  * **S-W** - button 2
  * **N+E** - button 3
  * **ENTER** - button 4

## 1.1.0
* dcspy use now UDP multicast connection do DCS-BIOS, since each TCP connection slightly increases the amount of work that is performed inside of DCS (blocking the rest of the simulation).
* support for integer data to be fetch from DCS-BIOS - using IntegerBuffer()
* bios_data in Airplanes instances allow both StringBuffer() and IntegerBuffer()
* reformat waiting time before DCS connected
* fix Data Entry Display for F-16C Viper - DCS-BIOS [v0.7.34](https://github.com/DCSFlightpanels/dcs-bios/releases/tag/v0.7.34) is required
* **Ka-50 Black Shark** - Autopilot channels show up in LCD

## 1.0.0
* **Ka-50 Black Shark** data from PVI-800 shows (in similar boxes) on LCD
* ProtocolParser for DCS-BIOS has new optimized state machine
  * LCD SDK is re-written from scratch:
  * low and high level API
  * auto-loading C library during importing
  * all API is type annotated and well documented
  * move loading LCD C library from G13 handler
*internal:
  * refactoring and rename internals of G13 handler module
  * add unit tests

## 0.9.2
* LCD prints current waiting time to connect to DCS
* when DCS exit from plane/mission exception is catch and handle correctly
* lots of internal changes, preparing for new features, most important:
  * change structure of AircraftHandler, move subscription to DCS-BIOS changes out of planes
  * update and clear methods move from G13 handler to LCD SDK

## 0.9.1
* G13 handler have display property to send text to LCD
* rename starting script to dcspy.exe
* starting script now show waiting time for DCS connection
* minor code optimization and refactoring

## 0.9.0
* based on version [specelUFC v1.12.1](https://github.com/specel/specelUFC/releases/tag/v1.12.1)
* added basic handling for Ka-50 PVI-800 data are received but not formatted properly
* F-16C DED should working but not 4 buttons under LCD - I don't have it so it is hard to test
* G13 handler detect 32/64 bit of Python and load correct version of LCD Logitech C library
* adding basic logging for debugging - prints on console
* all defined aircraft are detected and loaded on-the-fly during operation
* define new plane should be easy just use AircraftHandler as base class
* Python LCD SDK was clean-up
* other refactorings and code duplication removal
