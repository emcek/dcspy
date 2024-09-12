from re import match
from sys import argv

import git
from packaging import version


def latest_version(repo_path: str, as_tag: int = 1) -> str:
    """
    Get the latest version number form repository.

    :param repo_path: Path to repository
    :param as_tag: if True return full tag name
    :return: Version or tag name as string
    """
    repo = git.Repo(repo_path)
    tags_list = [str(tag) for tag in repo.tags]
    ver_tags = [version.parse(match_ver.group(1)) for tag in tags_list if (match_ver := match(r'v(\d+\.\d+\.\d+)$', tag))]
    ver = str(max(ver_tags))
    if bool(int(as_tag)):
        ver = f'v{ver}'
    return ver


if __name__ == '__main__':
    _repo_path, _as_tag = argv[1:]
    print(latest_version(_repo_path, int(_as_tag)))
