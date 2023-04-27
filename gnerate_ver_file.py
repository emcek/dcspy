from sys import argv

from PyInstaller.utils.win32 import versioninfo


def _generate(major: int, minor: int, patch: int, build: int, git_sha: str) -> versioninfo.VSVersionInfo:
    version = versioninfo.VSVersionInfo(
        ffi=versioninfo.FixedFileInfo(
            filevers=(major, minor, patch, build),
            prodvers=(major, minor, patch, build),
            mask=0x3f,
            flags=0x0,
            OS=0x40004,
            fileType=0x1,
            subtype=0x0,
            date=(0, 0)),
        kids=[versioninfo.StringFileInfo([versioninfo.StringTable('040904B0', [
                versioninfo.StringStruct('CompanyName', 'Michał Plichta'),
                versioninfo.StringStruct('FileDescription', 'Integrating DCS Planes with Logitech keyboards with LCD'),
                versioninfo.StringStruct('FileVersion', f'{major}.{minor}.{patch}'),
                versioninfo.StringStruct('InternalName', 'dcs_py'),
                versioninfo.StringStruct('LegalCopyright', '© Michał Plichta. All rights reserved.'),
                versioninfo.StringStruct('OriginalFilename', 'dcs_py.exe'),
                versioninfo.StringStruct('ProductName', 'DCSpy'),
                versioninfo.StringStruct('ProductVersion', f'{major}.{minor}.{patch} ({git_sha})')])]),
              versioninfo.VarFileInfo([versioninfo.VarStruct('Translation', [1033, 1200])])])
    return version


if __name__ == '__main__':
    ma, mi, pat, bld, sha, ver_f = argv[1:]
    ver = _generate(int(ma), int(mi), int(pat), int(bld), sha)

    with open(ver_f, 'w+', encoding='utf-8') as f:
        f.write(str(ver))
