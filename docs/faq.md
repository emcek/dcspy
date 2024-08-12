# FAQ
**Q:** Why in [F-16C DED](https://i.imgur.com/Hr0kmFV.jpg) instead of triangle up and down arrow I see strange character.
**A:** I didn't find good alternative, so I use unicode character [2666](https://www.fileformat.info/info/unicode/char/2195/index.htm) (I consider [2195](https://www.fileformat.info/info/unicode/char/2195/index.htm) as well, which do not render very well).

**Q:** I got error: `'pip' is not recognized as an internal or external command, operable program or batch file.`
**A:** Probably during installation of Python `pip` and/or `Add Python to environment variables` were not selected. Uninstall Python and install again with correct options, or consider add Python installation directory to PATH environment variable.

**Q:** No data from DCS-BIOS issue.
**A:** Check:
   * You have to be in cockpit to DCS-BIOS sent any data to DCSpy
   * some VPN block LAN traffic - turn off Stay invisible on LAN
