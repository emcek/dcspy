# Installation
There are two ways of install DCSpy: single file download (basic / new way) or via Python package manager (advanced / old way). Both have advantages and  disadvantages. For new users it is recommended to use first one, current users can stick to old way or switch to new way. Both will be supported.

## Single file download (basic way)
* Advantage: Simple download and you are ready to go
* Disadvantage: Windows Defender can block download/execution

1. Install [Logitech Gaming Software 9.04.49](https://support.logitech.com/software/lgs)
2. Go to [Releases](https://github.com/emcek/dcspy/releases), from Assets section download one of:
   * `dcspy_*.exe` - simple one window application
3. Place file anywhere in your system, double click to start.
4. DCS-BIOS
   * Install DCS-BIOS directly from DCSpy (button **Check DCS-BIOS**, see [DCS-BIOS Upgrade](upgrade.md#manual-procedure)).
     It checks if new version exists, download, and unpack DCS-BIOS to `Save Games` folder and check `Export.lua` file.
   * Or follow manual installation [DCS-BIOS wiki page](https://github.com/DCS-Skunkworks/DCSFlightpanels/wiki/Installation)

Due to how Python application can be pack into executable file (using PyInstaller/Nuitka), sometimes Windows Defender can recognize it as a virus. See more details [here](defender.md)

## via uv (advanced way)
* Advantage: Better control, simple update process, no Defender hassle
* Disadvantage: Python interpreter and/or uv tool is needed, more steps, more complicated process

1. Install [Logitech Gaming Software 9.04.49](https://support.logitech.com/software/lgs)
2. Install [uv](https://github.com/astral-sh/uv)
3. DCS-BIOS
   * You can skip for now and install DCS-BIOS directly from DCSpy (button Check DCS-BIOS, see [Configuration](usage.md#configuration)).
     It checks if new version exists, download, and unpack DCS-BIOS to `Save Games` folder and check `Export.lua` file.
   * Or follow manual installation [DCS-BIOS wiki page](https://github.com/DCS-Skunkworks/DCSFlightpanels/wiki/Installation)
4. Package is available on [PyPI](https://pypi.org/project/dcspy/), open Windows Command Prompt (cmd.exe) and type:
```shell script
uv tool install -p 3.13 dcspy
```


**Note:** If you got `pip is not recognized as an internal or external command, operable program or batch file.` error, see [FAQ](faq.md)


**Next step:** [Usage](usage.md)
