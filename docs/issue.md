## Troubleshooting
![image](https://github.com/emcek/dcspy/assets/475312/5ce0038a-e227-412b-a8fc-5f09a7dbf879)

If you encounter any problem during DCSpy usage, follow these steps:

* enable **Save LCD screenshot**
* enable **Show more logs**
* restart DCSpy
* try reproduce problem
* Immediately click **Stop** button
* click **Collect data** button
* It will ask you for location where to save zip archive with all data.

You can examine content yourself, here is list of collected data:

* Dcspy configuration: `C:\Users\<user>\AppData\Local\dcspy\config.yaml`
* Dcspy planes configurations i.e. `C:\Users\<user>\AppData\Local\dcspy\A-10C.yaml`
* Dcspy LCD screenshots: i.e. `C:\Users\<user>\AppData\Local\Temp\AH64DBLKII_xx.png`
* Dcspy log file `C:\Users\<user>\AppData\Local\Temp\dcspy.log`
* DCS log file `C:\Users\<user>\Saved Games\DCS.openbeta\Logs\dcs.log`
* system data `system_data.txt` created dynamically:
    * Windows version
    * Python location and version
    * Git version
    * DCS-BIOS SHA and version
    * structure of LGS installation
    * dump of current Dcspy configuration
