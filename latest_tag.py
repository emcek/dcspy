from re import match
from sys import argv

from packaging import version
import git


def latest_version(repo_path: str, as_tag=1) -> str:
    """
    Get latest version number form repository.

    :param repo_path: path to repository
    :param as_tag: if True return full tag name
    :return: return version or tag name as string
    """
    repo = git.Repo(repo_path)
    tags_list = [str(tag) for tag in repo.tags]
    ver_tags = [version.parse(m.group(1)) for tag in tags_list if (m := match(r'v(\d+\.\d+\.\d+)$', tag))]
    ver = str(max(ver_tags))
    if bool(int(as_tag)):
        ver = f'v{ver}'
    return ver


if __name__ == '__main__':
    print(latest_version(*argv[1:]))
