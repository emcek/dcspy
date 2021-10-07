import io
from os.path import abspath, dirname, join

from setuptools import setup, find_packages

__version__ = '1.4.0'
here = abspath(dirname(__file__))

with io.open(join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

with io.open(join(here, 'requirements.txt'), encoding='utf-8') as f:
    requires = f.read().splitlines()

setup(name='dcspy',
      version=__version__,
      description='Integrating DCS (Digital Combat Simulator) planes with Logitech G13/G15/G510/G19 LCD',
      long_description=long_description,
      long_description_content_type='text/markdown',
      url='https://github.com/emcek/dcspy',
      author='Michal Plichta',
      license='MIT License',
      entry_points={'console_scripts': ['dcspy = dcspy.dcspy:run']},
      data_files=[('dcspy_data', ['resources/dcspy.ico', 'resources/config.yaml'])],
      classifiers=['Development Status :: 5 - Production/Stable',
                   'Environment :: Console',
                   'License :: OSI Approved :: MIT License',
                   'Programming Language :: Python :: 3.6',
                   'Programming Language :: Python :: 3.7',
                   'Programming Language :: Python :: 3.8',
                   'Programming Language :: Python :: 3.9',
                   'Operating System :: Microsoft :: Windows',
                   'Operating System :: Microsoft :: Windows :: Windows 10',
                   'Topic :: Games/Entertainment',
                   'Topic :: Games/Entertainment :: Simulation',
                   'Topic :: Software Development :: Libraries :: Python Modules',
                   'Topic :: System :: Hardware',
                   'Topic :: Utilities'],
      keywords='logitech logitech-sdk logitech-keyboards logitech-gaming logitech-gaming-keyboard dcs-world dcs g13 g15 g510 g19',
      packages=find_packages(exclude=['tests']),
      install_requires=requires,
      python_requires='>=3.6',
      platforms=['win32', 'nt', 'Windows'],
      extras_require={'testing': ['pytest']},
      project_urls={'Bug Reports': 'https://github.com/emcek/dcspy/issues',
                    'Source': 'https://github.com/emcek/dcspy'})
