import io
from os.path import abspath, dirname, join

from setuptools import setup, find_packages

from dcspy import __version__

here = abspath(dirname(__file__))

with io.open(join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

with io.open(join(here, 'requirements.txt'), encoding='utf-8') as f:
    requires = f.read().splitlines()

setup(name='dcspy',  # Required
      version=__version__,  # Required
      description='Software for integrating DCS: F/A-18C, F-16C and Ka-50 with Logitech G13',  # Required
      long_description=long_description,  # Optional
      long_description_content_type='text/markdown',  # Optional (see note above)
      url='https://github.com/emcek/dcspy',  # Optional
      author='Michal Plichta',  # Optional
      license='MIT License',
      entry_points={'console_scripts': ['dcspy = dcspy.dcspy:run']},
      data_files=[('dcspy_data', ['images/dcspy.ico'])],
      classifiers=['Development Status :: 4 - Beta',
                   'Environment :: Console',
                   'License :: OSI Approved :: MIT License',
                   'Programming Language :: Python :: 3.6',
                   'Programming Language :: Python :: 3.7',
                   'Programming Language :: Python :: 3.8',
                   'Operating System :: Microsoft :: Windows',
                   'Operating System :: Microsoft :: Windows :: Windows 10',
                   'Topic :: Games/Entertainment',
                   'Topic :: Games/Entertainment :: Simulation',
                   'Topic :: Software Development :: Libraries :: Python Modules',
                   'Topic :: System :: Hardware',
                   'Topic :: Utilities'],
      keywords='logitech logitech-sdk logitech-keyboards logitech-gaming logitech-gaming-keyboard dcs-world dcs g13',
      # packages=find_packages(exclude=['tests']),  # Required
      packages=find_packages(),  # Required
      install_requires=requires,  # Optional
      platforms=['win32', 'nt', 'Windows'],
      # extras_require={'testing': ['pytest']},
      project_urls={'Bug Reports': 'https://github.com/emcek/dcspy/issues',
                    'Source': 'https://github.com/emcek/dcspy'})
