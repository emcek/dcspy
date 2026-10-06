# Live DCS-BIOS
The easiest way to use this feature is from DCSpy, but you need [Git](https://git-scm.com/download/win) installed. It is possible download live version manually from GitHub and place in Save Games folder, but you need do it every time you want update latest changes of DCS-BIOS.

When enable DCSpy will use live/git version of DCS-BIOS. It is like DCS OpenBeta vs. Stable.

When you switch to live version for first time be patient DCSpy will download repository (ca. 150 MB it can take a few seconds), freeze can be expected.

This is recommended way using DCS-BIOS by its developers.

DCSpy basically copy latest changes from DCS-BIOS repository into your `Save Games` folder, so every time you run DCSpy (when `Auto Update DCS-BIOS` is enable as well) latest commit from GitHub will be fetched.

Another option you can specify is `DCS-BIOS Git reference`, where `master` (recommended default value) means latest commit. But you can use any branch or commit ID.

You can even use own DCS-BIOS fork, just enter URL address of repository. It is requre to click **Repair** button to remove old repo and clone new one.

Example:

![image](https://github.com/emcek/dcspy/assets/475312/7d1da9db-a123-456f-bf7a-78d70344ba8c)

![image](https://github.com/user-attachments/assets/e2aca438-09b9-406d-88bf-5cf70b45b44b)
