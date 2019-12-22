"""Various tools to emerge and to show status for conky."""
import io
from os.path import abspath, dirname, join

from setuptools import setup, find_packages

from pyerge import __version__

here = abspath(dirname(__file__))

with io.open(join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

with io.open(join(here, 'requirements.txt'), encoding='utf-8') as f:
    requires = f.read().splitlines()

setup(
    name='pyerge',  # Required
    version=__version__,  # Required
    description='Various tools to emerge and to show status for conky',  # Required
    long_description=long_description,  # Optional
    long_description_content_type='text/markdown',  # Optional (see note above)
    url='https://github.com/emcek/pyerge',  # Optional
    author='Michal Plichta',  # Optional
    license='GPLv2',
    scripts=['script/pye'],
    # entry_points={'console_scripts': ['exec = pyerge.cli:run_parser']},
    classifiers=[  # Optional
        'Development Status :: 4 - Beta',

        'Environment :: Console',
        'Environment :: X11 Applications',

        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',

        'Operating System :: POSIX',
        'Operating System :: Unix',

        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',

        'Topic :: Desktop Environment',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Monitoring',
        'Topic :: Utilities'
    ],

    keywords='gentoo portage emerge conky',  # Optional

    # You can just specify package directories manually here if your project is
    # simple. Or you can use find_packages().
    #
    # Alternatively, if you just want to distribute a single Python file, use
    # the `py_modules` argument instead as follows, which will expect a file
    # called `my_module.py` to exist:
    #
    #   py_modules=["my_module"],
    #
    packages=find_packages(exclude=['tests']),  # Required

    # This field lists other packages that your project depends on to run.
    # Any package you put here will be installed by pip when your project is
    # installed, so they must be valid existing projects.
    #
    # For an analysis of "install_requires" vs pip's requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires=requires,  # Optional

    extras_require={
        'testing': ['pytest']
    },

    project_urls={  # Optional
        'Bug Reports': 'https://github.com/emcek/pyerge/issues',
        'Source': 'https://github.com/emcek/pyerge',
    },
)
