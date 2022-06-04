__config_version__ = 1

GLOBALS = {
    'serializer': "{{ MAJOR }}.{{ MINOR }}.{{ PATCH }}{{ '-{}'.format(PRERELEASE) if PRERELEASE }}"
}

FILES = ['setup.py',
         'dcspy/dcspy.py',
         'dcspy/starter.py',
         'dcspy/tk_gui.py']

VERSION = ['MAJOR',
           'MINOR',
           'PATCH',
           {'name': 'PRERELEASE',
            'type': 'value_list',
            'allowed_values': ['', 'alpha', 'beta']}]
