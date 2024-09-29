# Starting
## Single file download (new way)
1. Run Logitech Gaming Software (it allows accessing LCD)
2. Double click at downloaded file.
3. Click `Start`
4. LCD should update with dcspy basic info, waiting to connect to DCS
5. Run DCS and start any mission.

## via pip (old way)
1. Run Logitech Gaming Software (it allows accessing LCD)
2. You can check with `pip uninstall dcspy` (**NOTE!** answer **No** to question) where dcspy was installed. Usually pip should install dcspy into your python directory: i.e.:
   * `d:\projects\venvs\dcspy\lib\site-packages\dcspy-3.0.0.dist-info\*`
   * `d:\projects\venvs\dcspy\lib\site-packages\dcspy\*`
   * `d:\projects\venvs\dcspy\scripts\dcspy.exe`
   * `d:\projects\venvs\dcspy\scripts\dcspy_cli.exe`
3. You can drag and drop `dcspy.exe` or `dcspy_cli.exe` to desktop and make shortcut (with custom icon, you can find icon in installation directory i.e. `d:\projects\venvs\dcspy\lib\site-packages\dcspy\img\dcspy.ico`).
   * `dcspy.exe` - with open directly GUI window
   * `dcspy_cli.exe` - additionally start console window (with logs)
4. Double-click on dcspy icon or type `dcspy.exe`\`dcspy_cli.exe` from Command Prompt
5. Click `Start`
6. LCD should update with dcspy basic info, waiting to connect to DCS
7. Run DCS and start any mission.

**Note:** DCS can already running, before starting LGS and or DCSpy.

**Note:** If you upgrade DCSpy before version 1.7.0 `dcspy.ico` and `config.yaml` were in data directory like `c:\python312\dcspy_data\` but location is deperched in Python if you still have it, you can safely delete it

# Mono vs. Color
DCSpy do not use full potential of G19, which support full RGBA, 8-lines LCD.
In contrast to mono devices (like G13, G15 and G510), which support mono, 4-lines LCD.

## LCD buttons
G19 has 7  buttons.
In contrast to mono devices (like G13, G15 and G510) has only 4 buttons.
Way in which actions assign to button for G13 (4 buttons form left to right) are mapped to G19 looks:
* G13 1st button -> G19 left button
* G13 2nd button -> G19 right button
* G13 3rd button -> G19 down button
* G13 4th button -> G19 up button

Right now LCD buttons are hardcoded in DCSpy and its function depends on currently loaded aircraft. This will change in future.

## G13, G15, G510 - Mono
mono, 4-lines LCD with only 4 buttons
![image](https://user-images.githubusercontent.com/475312/174407168-7db23a3f-3493-4a35-b898-ebb3a3ff839f.png)
![image](https://user-images.githubusercontent.com/475312/174407442-ed9c7d85-057d-4572-8316-3578721e4dab.png)
![image](https://user-images.githubusercontent.com/475312/174407530-b010691c-0895-4786-ad4e-8f98deeebb02.png)
## G19 - Color
full RGBA, 8-lines LCD with 7 buttons
![image](https://user-images.githubusercontent.com/475312/174407299-d07e7ba5-d837-4af4-884a-7e20a48d676a.png)

## G-keys
From DCSpy 3.0 it is possible to use all keyboard's G-Keys:
* G19 - 12 keys
* G510 - 18 keys
* G15 v1 - 18 keys
* G15 v2 - 6 keys
* G13 - 29 keys

You can assign almost any input controller from cockpit for aircraft supported by DCS-BIOS. Note: DCS-BIOS has to provide input protocol.

### How to setup:
* Install Git: https://git-scm.com/download/win (any 64-Bit, default options should be fine)
* Set **DCS-BIOS** folder
  ie. (D:/Users/wags/Saved Games/DCS.openbeta/Scripts/DCS-BIOS)
* Set checked **Use live DCS-BIOS version** (can take 20+ sec)
* Click **Start** and then **Stop** (in rare cases is needed)
* Open LGS, new profile should be added (current dcspy file name: ie. dcspy_cli_3.0.0)
![image](https://github.com/emcek/dcspy/assets/475312/3145510c-ad8b-4fca-8fe6-596129d9a755)
* Set this profile default and optionally persistent. Close LGS.
![image](https://github.com/emcek/dcspy/assets/475312/c56f61fb-bafb-4fd2-a2a9-549b5b1be990)
* Go to **G-Keys** tab, additionally turn on **View** / **Show G-Keys** extra dialog
* Select plane from combo box up right corner
* assign any controllers to G-Key/Modes
* Use save icon to save plane configuration

# Configuration
All settings can be configured directly via GUI. However,  more advanced users can change configuration file `config.yaml` file. It is located in user's AppData directory (e.g. `C:\Users\<user_name>\AppData\Local\dcspy\config.yaml`).
This is simple file, most users do not need to touch it at all. Configuring DCSpy enable some powerful features of DCSpy.

## Keyboards
![image](https://github.com/emcek/dcspy/assets/475312/3be6a62f-029e-43a2-b6ab-b2d4e06e8e9b)

* **keyboard** - default Logitech keyboard value, last used value is saved automatically
  *possible values*: `G19`, `G510`, `G15 v1`, `G15 v2`, `G13`
* Select correct keyboard since all of then support different combination of: LCD, LCD buttons and G-Keys

## Settings
![image](https://github.com/emcek/dcspy/assets/475312/70b9101e-e09e-492f-8baa-92bf2be812a7)

### DCSpy
* **autostart** - when set to `true` DCSpy start automatically.
  *possible values*: `true` or `false`
* **show_gui** - it allows showing or hiding GUI during start of DCSpy. When set to `false` DCSpy start automatically.
  *possible values*: `true` or `false`
* **check_ver** - check for new version during start of DCSpy.
  *possible values*: `true` or `false`
* **dcs** - installation directory of DCS. By default it is set to `C:\Program Files\Eagle Dynamics\DCS World OpenBeta`

### DCS-BIOS
* **check_bios** - check for new version of DCS-BIOS during start of DCSpy.
  *possible values*: `true` or `false`
* **git_bios** - If set to `True` Git/Live version of DCS-BIOS with be used
  *possible values*: `true` or `false`
* **git_bios_ref** - Git valid reference i.e. branch name, tag, SHA of commit etc.
  *possible values*: any Git valid reference
* **dcsbios** - location of DCS-BIOS folder inside user's `Saved Games\DCS.openbeta`.
  Set this parameter to correct value allows user check and update DCS-BIOS to the latest release.
  *example value*: `D:\Users\wags\Saved Games\DCS.openbeta\Scripts\DCS-BIOS`

### Fonts
* **font_mono_xs** - size of extra small font for mono devices
* **font_mono_s** - size of small font for mono devices
* **font_mono_l** - size of large font for mono devices
* **font_color_xs** - size of extra small font for color devices
* **font_color_s** - size of small font for color devices
* **font_color_l** - size of large font for color devices
* **font_name** - file name with TrueType font use in all devices
* **f16_ded_font** - Special font for F-16's DED (G19 Color LCD only)

### Debug
* **save_lcd** - take every change of LCD as screenshot (for debugging)
  *possible values*: `true` or `false`
* **verbose** - Show more debug logs, be more verbose (for debugging)
  *possible values*: `true` or `false`
