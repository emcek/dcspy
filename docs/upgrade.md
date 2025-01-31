# DCSpy
## Single file download (basic/recommended way)
Download latest file from [Releases](https://github.com/emcek/dcspy/releases/latest)

## via uv (advanced way)
To upgrade DCSpy to the latest version, open Command Prompt and type:
```shell script
uv tool update dcspy
```
**Note:** If you upgrade DCSpy from 1.5.1 or older you can remove Logitech LCD SDK from `C:\Program Files\Logitech Gaming Software\LCDSDK_8.57.148`

## Switch from advanced to basic
1. Remove dcspy, open Command Prompt and type:
```shell script
uv tool uninstall dcspy
```
2. Follow installation [procedure](install.md#single-file-download-new-way).

# DCS-BIOS
If you have enable `Auto check DCS-BIOS` you do not need any manual steps. Every time you start DCSpy, DCS-BIOS will be checked and updated for you.

## Manual procedure
1. Stop DCS World or at least exit mission.
2. Make sure setting **DCS-BIOS folder** is correct
3. Click **Check for updates** button in DCS-BIOS group, Note, new version in footer.
4. Click OK.
![image](https://github.com/emcek/dcspy/assets/475312/187f9d91-5464-4560-9308-405e37816562)
