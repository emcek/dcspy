from collections.abc import Sequence
from os import environ
from sys import argv

from PyInstaller.utils.win32 import versioninfo


def generate_ver_info(major: int, minor: int, patch: int, build: int, git_sha: str) -> versioninfo.VSVersionInfo:
    """
    Generate a version information object.

    :param major: Version major part
    :param minor: Version minor part
    :param patch: Version patch part
    :param build: GitHub build number
    :param git_sha: Git SHA hash
    :return: VSVersionInfo object
    """
    ver_info = versioninfo.VSVersionInfo(
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
              versioninfo.StringStruct('LegalCopyright', '© 2023 Michał Plichta. All rights reserved.'),
              versioninfo.StringStruct('OriginalFilename', 'dcs_py.exe'),
              versioninfo.StringStruct('ProductName', 'DCSpy'),
              versioninfo.StringStruct('ProductVersion', f'{major}.{minor}.{patch} ({git_sha})')])]),
              versioninfo.VarFileInfo([versioninfo.VarStruct('Translation', [1033, 1200])])])
    return ver_info


def save_ver_file(ver=environ.get('GITHUB_REF_NAME', '3.5.1'), bld=environ.get('GITHUB_RUN_NUMBER', '1'),
                  sha=environ.get('GITHUB_SHA', 'deadbeef'), ver_f='file_version_info.txt') -> Sequence[str]:
    """
    Save generated version file based on the list of strings.

    Example of params: v1.9.5 40 6bbd8808 file_version_info.txt

    :param ver: Version name or tag name
    :param bld: GitHub build number
    :param sha: Git SHA hash
    :param ver_f: File name of version file
    :return: Input parameters
    """
    if all([ver, bld, sha, ver_f]):
        if ver.startswith('v'):
            ver = ver[1:]
        info_ver_data = generate_ver_info(*[int(i) for i in ver.split('.')], build=int(bld), git_sha=sha[:7])
        with open(ver_f, mode='w+', encoding='utf-8') as file_ver_info:
            file_ver_info.write(str(info_ver_data))
    else:
        print('Use: v1.9.5 40 a43c77649cad77204c075b431f38d03dbc75cbdd file_version_info.txt')
    return ver, bld, sha[:7], ver_f


if __name__ == '__main__':
    print(save_ver_file(*argv[1:]))
